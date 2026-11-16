"""v9: RIG PILOTO proprio do Lobo Artico sobre a v8 (low_v8/ preservada). Nao usa rigs/clipes dos prototipos V2/V5.
Esqueleto quadrupede digitigrado (37 ossos, nomes finais do jogo; o Roblox liga malha a osso PELO NOME):
  Raiz (chao, sem peso) > Quadril > Coluna1 > Coluna2 > Coluna3 > Pescoco1 > Pescoco2 > Cabeca > Mandibula,
  Palpebra_{Sup,Inf}_{E,D}, Orelha_{E,D}; Coluna3 > Escapula_X > Umero_X > Antebraco_X > Metacarpo_X > Dedos_X;
  Quadril > Coxa_X > Tibia_X > Metatarso_X > DedosPe_X; Quadril > Cauda1..4.  (E = +x = lado esquerdo do lobo)
Eixos: X local de todo osso = X global (flexao = giro em X local), exceto palpebras (X local = eixo de fechamento
da v5/v8, em rig_pivos.json). Repouso = malha v8 sem nenhuma mudanca de posicao.
Pesos:
- base: heat (Blender) num PROXY fechado (voxel) da pele unida cabeca+corpo, transferido por interpolacao da face mais
  proxima a cada malha de pele dos 3 LODs (vertices coincidentes da costura recebem o mesmo peso); lados separados
  (osso _E nao pesa em x < -0,25 e vice-versa); rosto puxado para Cabeca longe do plano da costura; no proxy:
  alcance dos ossos das patas limitado (nada de escapula na garganta), troca E/D suave no meio e 4 passadas de alisamento;
- rosto: os grupos aprovados da v8 viram ossos SEM perder o comportamento: peso final = (1 - m - p) * base +
  m * Mandibula + p * Palpebra (m, p = pesos v8), ou seja, abrir a boca so com o rig mexe exatamente os mesmos vertices
  com os mesmos pesos (o teste v8 girava cada vertice por angulo * peso; o rig mistura linearmente: diferenca medida);
  originais guardados como v8_<grupo>;
- orelhas: peso pela posicao ao longo do eixo base -> ponta (medido na malha);
- pecas soltas da cabeca (globos, dentes, lingua): Cabeca 100% + Mandibula da v8 (dentes de baixo/lingua);
- pelagem: cada cartao inteiro com o peso da pele no ponto da raiz (nao estica, nao descola);
- marca: cada vertice com o peso da pele no ponto mais proximo (acompanha a pele);
- cristais: cada cristal inteiro com o peso da pele na base (forma mantida; medido em auditar_rig_v9.py);
- no maximo 4 influencias por vertice, normalizadas.
Uso: blender -b low_v8/CR_LoboArtico_LOW.blend -P rig_v9.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, math, shutil
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.interpolate import poly_3d_calc
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
for im in bpy.data.images:                                              # texturas: copias proprias da v9
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()
LODS = {"LOW": ("LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem"), "LOD1": ("LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem"), "LOD2": ("LOD2_Cabeca", "LOD2_Corpo", None)}
CP, CN = V(PIV["costura"]["ponto"]), V(PIV["costura"]["normal"])
FACIAIS = ("Mandibula", "Palpebra_Sup_E", "Palpebra_Inf_E", "Palpebra_Sup_D", "Palpebra_Inf_D")

# ------------------------------------------------------------------ marcos medidos na malha do corpo (LOD0)
corpo = bpy.data.objects["LOW_Corpo"]; n = len(corpo.data.vertices); co = np.empty(n * 3); corpo.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co.T
def coluna_pata(px, py):
    """centroide da pata em fatias de altura, seguindo o membro de baixo para cima (so ate z 2,1: acima o tronco mistura)"""
    cx, cy, c = px, py, {}
    for zz in np.arange(0.05, 2.15, 0.25):
        s = (np.abs(z - zz) < 0.12) & (np.hypot(x - cx, y - cy) < 0.75) & (x * np.sign(px) > 0.15)
        if s.sum() >= 5: m = co[s].mean(0); cx, cy = m[0], m[1]
        c[round(float(zz), 2)] = V((cx, cy, zz))
    return c
def em(c, zz):
    ks = sorted(c); k = min(ks, key=lambda q: abs(q - zz)); return c[k].copy()
def centro(yy, prof=0.85):                                              # eixo da coluna: 0,85 abaixo do dorso na fatia
    s = (np.abs(y - yy) < 0.2) & (np.abs(x) < 0.6); return V((0, yy, z[s].max() - prof))
PES = {"E": V(PIV["pose_neutra"]["patas_xy_depois"][0] + [0]), "D": V(PIV["pose_neutra"]["patas_xy_depois"][1] + [0]),
       "TE": V(PIV["pose_neutra"]["patas_xy_depois"][2] + [0]), "TD": V(PIV["pose_neutra"]["patas_xy_depois"][3] + [0])}
J = {}
for lado in ("E", "D"):
    p = PES[lado]; s = 1 if lado == "E" else -1; c = coluna_pata(p.x, p.y)
    pata = co[(z < 0.35) & (np.hypot(x - p.x, y - p.y) < 0.8)]
    ponta = V((float(pata[:, 0].mean()), float(pata[:, 1].min()) + 0.12, 0.12))
    mcp = em(c, 0.30); mcp.z = 0.30
    carpo = em(c, 0.80); carpo.z = 0.85
    antebr = em(c, 1.80)
    cotov = V((antebr.x, antebr.y + 0.22, 2.45))
    ombro = V((antebr.x + 0.10 * s, antebr.y - 0.50, 3.65))
    escap = V((0.42 * s, ombro.y + 1.05, 5.25))
    J[lado] = dict(Escapula=(escap, ombro), Umero=(ombro, cotov), Antebraco=(cotov, carpo), Metacarpo=(carpo, mcp), Dedos=(mcp, ponta))
    p = PES["T" + lado]; c = coluna_pata(p.x, p.y)
    pata = co[(z < 0.35) & (np.hypot(x - p.x, y - p.y) < 0.8)]
    ponta = V((float(pata[:, 0].mean()), float(pata[:, 1].min()) + 0.12, 0.12))
    mtp = em(c, 0.30); mtp.z = 0.30
    jarr = em(c, 1.05); jarr = V((jarr.x, jarr.y + 0.22, 1.15))
    tib = em(c, 2.05)
    joelho = V((tib.x, tib.y - 0.45, 2.70))
    quad = V((0.72 * s, tib.y + 0.30, 4.20))
    J["T" + lado] = dict(Coxa=(quad, joelho), Tibia=(joelho, jarr), Metatarso=(jarr, mtp), DedosPe=(mtp, ponta))
cab = bpy.data.objects["LOW_Cabeca"]; kc = np.array([v.co[:] for v in cab.data.vertices])
ORE = {}
for lado, s in (("E", 1), ("D", -1)):                                    # orelha: ponta = vertice mais alto do lado; base 0,5 abaixo
    m = (kc[:, 0] * s > 0.2) & (kc[:, 1] < -4.4) & (kc[:, 1] > -5.8)
    i = int(np.argmax(np.where(m, kc[:, 2], -9))); tip = V(kc[i])
    b = (np.abs(kc[:, 2] - (tip.z - 0.50)) < 0.06) & (np.hypot(kc[:, 0] - tip.x, kc[:, 1] - tip.y) < 0.45) & (kc[:, 0] * s > 0.15)
    base = V(kc[b].mean(0)) if b.sum() > 5 else tip - V((0, 0, 0.5))
    ORE[lado] = (base, tip)
PV = V(PIV["mandibula"]["pivo_sugerido"]); BA, BB = PIV["mandibula"]["linha_boca"]
NUCA = V((0, -4.72, 6.05))
COL = [centro(2.55), centro(1.45), centro(0.15), centro(-1.20, 1.25), centro(-2.35, 1.30)]   # torax e cernelha: juba alta, mais fundo
# cauda: eixo pela linha de fundo do volume (vista lateral). Teste com o eixo pelo miolo medido nos cortes (y ~3,7) e
# separacao de pesos cauda/pata por distancia: PIOROU (a cauda do Meshy esta fundida a coxa esquerda; ver ficha 8.11)
CAUDA = [V((0, 2.95, 4.55)), V((0, 3.55, 3.75)), V((0, 4.02, 2.85)), V((0, 4.35, 1.90)), V((0, 4.58, 0.75))]
print("MARCOS", {k: {b: [tuple(round(c, 2) for c in p) for p in v] for b, v in d.items()} for k, d in J.items()}, "ORE", ORE, "COL", COL, flush=True)

# ------------------------------------------------------------------ esqueleto
arm_d = bpy.data.armatures.new("LoboArtico_Rig"); arm = bpy.data.objects.new("LoboArtico_Rig", arm_d); sc.collection.objects.link(arm)
arm_d.display_type = "OCTAHEDRAL"; arm.show_in_front = True
ativar(arm); bpy.ops.object.mode_set(mode="EDIT"); E = arm_d.edit_bones
def osso(nome, a, b, pai=None, eixo_x=V((1, 0, 0))):
    eb = E.new(nome); eb.head = a; eb.tail = b
    yv = (V(b) - V(a)).normalized(); xv = (eixo_x - yv * eixo_x.dot(yv)).normalized(); zv = xv.cross(yv)
    M = Matrix((xv, yv, zv)).transposed().to_4x4(); M.translation = V(a); eb.matrix = M
    if pai:
        eb.parent = E[pai]; eb.use_connect = (E[pai].tail - V(a)).length < 1e-4
    return eb
ymeio = (PES["E"].y + PES["TE"].y) / 2
osso("Raiz", V((0, ymeio, 0)), V((0, ymeio - 1.0, 0)))
osso("Quadril", COL[0], COL[1], "Raiz")
osso("Coluna1", COL[1], COL[2], "Quadril"); osso("Coluna2", COL[2], COL[3], "Coluna1"); osso("Coluna3", COL[3], COL[4], "Coluna2")
pm = (COL[4] + NUCA) / 2 + V((0, 0, 0.15))
osso("Pescoco1", COL[4], pm, "Coluna3"); osso("Pescoco2", pm, NUCA, "Pescoco1")
osso("Cabeca", NUCA, V((0, -6.25, 5.72)), "Pescoco2")
yq = -6.30; osso("Mandibula", PV, V((0, yq, BA + BB * yq - 0.12)), "Cabeca")
for lado, ol in PIV["olhos"].items():
    S, ax = V(ol["centro_globo"]), V(ol["eixo"]).normalized()
    fr = V((0, -1, 0)); fr = (fr - ax * fr.dot(ax)).normalized()
    for k in ("Sup", "Inf"):
        osso("Palpebra_%s_%s" % (k, lado), S, S + fr * 0.15 + V((0, 0, 0.04 if k == "Sup" else -0.04)), "Cabeca", eixo_x=ax)
for lado, (b, t) in ORE.items(): osso("Orelha_" + lado, b, t, "Cabeca")
for lado in ("E", "D"):
    pai = "Coluna3"
    for nm in ("Escapula", "Umero", "Antebraco", "Metacarpo", "Dedos"):
        a, b = J[lado][nm]; osso(nm + "_" + lado, a, b, pai); pai = nm + "_" + lado
    pai = "Quadril"
    for nm in ("Coxa", "Tibia", "Metatarso", "DedosPe"):
        a, b = J["T" + lado][nm]; osso(nm + "_" + lado, a, b, pai); pai = nm + "_" + lado
pai = "Quadril"
for i in range(4): osso("Cauda%d" % (i + 1), CAUDA[i], CAUDA[i + 1], pai); pai = "Cauda%d" % (i + 1)
bpy.ops.object.mode_set(mode="OBJECT")
OSSOS = [b.name for b in arm_d.bones]; print("OSSOS", len(OSSOS), OSSOS, flush=True)
SEM_HEAT = {"Raiz", "Orelha_E", "Orelha_D"} | set(FACIAIS)
arm_d.bones["Raiz"].use_deform = False

# ------------------------------------------------------------------ proxy fechado + heat
def componente_pele(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    sem = [v for v in bm.verts if v.is_boundary and abs((v.co - CP).dot(CN)) < 0.03]; comp = set(v.index for v in sem); pilha = list(sem)
    while pilha:
        v = pilha.pop()
        for e in v.link_edges:
            u = e.other_vert(v)
            if u.index not in comp: comp.add(u.index); pilha.append(u)
    bm.free(); return comp
def copia(o, nome):
    c = o.copy(); c.data = o.data.copy(); c.name = nome; sc.collection.objects.link(c)
    for g in list(c.vertex_groups): c.vertex_groups.remove(g)
    return c
pc = copia(cab, "tmp_proxy_cab"); pele = componente_pele(cab)
bm = bmesh.new(); bm.from_mesh(pc.data); bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in pele], context="VERTS"); bm.to_mesh(pc.data); bm.free()
pb_ = copia(corpo, "tmp_proxy_corpo"); ativar(pc); pb_.select_set(True); bpy.ops.object.join(); prox = bpy.context.object; prox.name = "tmp_Proxy"
rm = prox.modifiers.new("R", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.07; bpy.ops.object.modifier_apply(modifier=rm.name)
sm = prox.modifiers.new("S", "SMOOTH"); sm.factor = 0.5; sm.iterations = 2; bpy.ops.object.modifier_apply(modifier=sm.name)
for nm in SEM_HEAT: arm_d.bones[nm].use_deform = False
ativar(prox); arm.select_set(True); bpy.context.view_layer.objects.active = arm
try: bpy.ops.object.parent_set(type="ARMATURE_AUTO")
except Exception as e: print("HEAT erro:", e)
for nm in SEM_HEAT - {"Raiz"}: arm_d.bones[nm].use_deform = True
sem_p = sum(1 for v in prox.data.vertices if not v.groups); print("HEAT proxy verts", len(prox.data.vertices), "sem peso", sem_p, flush=True)
HEAT_OK = sem_p <= len(prox.data.vertices) * 0.02
SEG = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in arm_d.bones if b.name not in SEM_HEAT]
def dseg(p, a_, b_):
    ab = b_ - a_; t_ = max(0.0, min(1.0, (p - a_).dot(ab) / max(ab.length_squared, 1e-9))); return (p - (a_ + ab * t_)).length
pnome = {g.index: g.name for g in prox.vertex_groups}
PW = []
for v in prox.data.vertices:
    d = {pnome[e.group]: e.weight for e in v.groups if e.weight > 1e-4 and pnome[e.group] not in SEM_HEAT}
    if not d or not HEAT_OK:
        ds = sorted((dseg(v.co, a_, b_), nm) for nm, a_, b_ in SEG)[:3]; ws = [1 / max(q, 0.05) ** 4 for q, _ in ds]
        d = {nm: w / sum(ws) for (_, nm), w in zip(ds, ws)}
    PW.append(d)
# correcoes do heat no proxy (valem igual para todas as malhas e LODs, e a costura continua coerente):
# - alcance dos membros: os ossos da pata dianteira nao pesam na garganta/peito a frente do ombro (somem de y -3,9 a -4,6)
#   e os da traseira nao pesam na barriga a frente da coxa (somem de y 1,0 a 0,2) - o heat espalhava a escapula ate a garganta;
# - troca de lado suave na linha do meio (osso _E vai de 1 em x 0,3 a 0 em x -0,3; _D espelhado): sem salto E/D entre vizinhos;
# - 4 passadas de alisamento (metade do proprio peso + metade da media dos vizinhos) contra os saltos do corte em 4 influencias.
DIANT = ("Escapula", "Umero", "Antebraco", "Metacarpo", "Dedos_"); TRAS = ("Coxa", "Tibia", "Metatarso", "DedosPe")
def corrige(d, p):
    out = {}
    for k, w in d.items():
        if k.startswith(DIANT): w *= suave((p.y + 4.6) / 0.7)
        if k.startswith(TRAS): w *= suave((p.y - 0.2) / 0.8)
        if k.endswith("_E"): w *= suave((p.x + 0.3) / 0.6)
        if k.endswith("_D"): w *= suave((0.3 - p.x) / 0.6)
        if w > 1e-5: out[k] = w
    if not out: out = {"Pescoco2": 1.0} if p.y < -3.0 else {"Coluna2": 1.0}
    t = sum(out.values()); return {k: w / t for k, w in out.items()}
PW = [corrige(d, v.co) for d, v in zip(PW, prox.data.vertices)]
VIZ = [[] for _ in prox.data.vertices]
for e in prox.data.edges: VIZ[e.vertices[0]].append(e.vertices[1]); VIZ[e.vertices[1]].append(e.vertices[0])
for _ in range(4):
    novo = []
    for i, d in enumerate(PW):
        m = {}
        for j in VIZ[i]:
            for k, w in PW[j].items(): m[k] = m.get(k, 0.0) + w / len(VIZ[i])
        s = {k: 0.5 * d.get(k, 0.0) + 0.5 * m.get(k, 0.0) for k in set(d) | set(m)}; novo.append(s)
    PW = novo
ppos = [v.co.copy() for v in prox.data.vertices]; pfac = [list(p.vertices) for p in prox.data.polygons]
BVH_P = BVHTree.FromPolygons(ppos, pfac)
def peso_em(p, bvh, pos, fac, W):
    loc, nr, fi, d = bvh.find_nearest(p)
    vs = fac[fi]; bc = poly_3d_calc([pos[i] for i in vs], loc); out = {}
    for i, b in zip(vs, bc):
        for k, w in W[i].items(): out[k] = out.get(k, 0.0) + w * b
    return out
def lado_ok(nome, px):
    if nome.endswith("_E") and px < -0.25: return False
    if nome.endswith("_D") and px > 0.25: return False
    return True
def normal(d, maxi=4):
    d = {k: w for k, w in d.items() if w > 1e-4}
    it = sorted(d.items(), key=lambda kv: -kv[1])[:maxi]; t = sum(w for _, w in it)
    return {k: w / t for k, w in it}

# ------------------------------------------------------------------ pesos por malha de pele
ESTAT = {}
def pesar_pele(o, e_cab):
    me = o.data; gi = {g.name: g for g in o.vertex_groups}
    orig = {}
    for nm in FACIAIS:                                                  # guarda os grupos aprovados da v8
        g = gi.get(nm)
        if g is not None: g.name = "v8_" + nm; orig[nm] = g.index
    for nm in ("Boca_Superior", "Boca_Inferior", "Protecao_LOD"):
        if nm in gi: gi[nm].name = "v8_" + nm
    pele_ids = componente_pele(o) if e_cab else set(range(len(me.vertices)))
    W = []; trunc = 0
    for v in me.vertices:
        if v.index in pele_ids:
            b = {k: w for k, w in peso_em(v.co, BVH_P, ppos, pfac, PW).items() if lado_ok(k, v.co.x)}
            if e_cab:                                                    # rosto (longe da costura, que e inclinada): Cabeca
                f = suave(((v.co - CP).dot(CN) - 0.35) / 0.50); b = {k: w * (1 - f) for k, w in b.items()}; b["Cabeca"] = b.get("Cabeca", 0) + f
        else:
            b = {"Cabeca": 1.0}                                         # pecas soltas: globos, dentes, lingua
        t = sum(b.values()); b = {k: w / t for k, w in b.items()}
        if e_cab:
            fac = {nm: next((e.weight for e in v.groups if e.group == gi_), 0.0) for nm, gi_ in orig.items()}
            for lado, (bs, tp) in ORE.items():                          # orelha: ao longo do eixo base -> ponta
                ax = tp - bs; tt = (v.co - bs).dot(ax) / ax.length_squared; r = (v.co - (bs + ax * max(0, min(1, tt)))).length
                if tt > -0.25 and r < 0.40 and v.co.x * (1 if lado == "E" else -1) > 0.1:
                    fac["Orelha_" + lado] = suave((tt + 0.25) / 0.45) * suave((0.40 - r) / 0.12)
            soma = min(1.0, sum(fac.values()))
            b = {k: w * (1 - soma) for k, w in b.items()}
            for k, w in fac.items():
                if w > 0: b[k] = b.get(k, 0) + w
        nb = normal(b); trunc += sum(b.values()) - sum(w for k, w in sorted(b.items(), key=lambda kv: -kv[1])[:4]) > 0.02
        W.append(nb)
    ESTAT[o.name] = {"truncados_>0.02": trunc}
    return W
def gravar(o, W):
    gs = {}
    for nm in OSSOS:
        gs[nm] = o.vertex_groups.get(nm) or o.vertex_groups.new(name=nm)
    for i, d in enumerate(W):
        for k, w in d.items(): gs[k].add([i], w, "REPLACE")
    for nm in OSSOS:                                                    # grupos de osso vazios ficam fora
        if not any(k == nm for d in W for k in d): o.vertex_groups.remove(gs[nm])
    md = o.modifiers.new("Armature", "ARMATURE"); md.object = arm; o.parent = arm
def costura_igual(h, c, Wh, Wc):
    """vertices coincidentes cabeca/corpo: o mesmo peso (media); conta as diferencas antes"""
    kd = KDTree(len(c.data.vertices))
    for v in c.data.vertices: kd.insert(v.co, v.index)
    kd.balance(); dif = 0; pares = 0
    for v in h.data.vertices:
        if abs((v.co - CP).dot(CN)) > 0.2: continue
        p, j, d = kd.find(v.co)
        if d > 1e-4: continue
        pares += 1; a, b = Wh[v.index], Wc[j]
        dif = max(dif, max(abs(a.get(k, 0) - b.get(k, 0)) for k in set(a) | set(b)))
        m = normal({k: (a.get(k, 0) + b.get(k, 0)) / 2 for k in set(a) | set(b)}); Wh[v.index] = m; Wc[j] = dict(m)
    return pares, round(dif, 4)
PELES = {}
for L, (nh, nc, nf) in LODS.items():
    h, c = bpy.data.objects[nh], bpy.data.objects[nc]
    Wh, Wc = pesar_pele(h, True), pesar_pele(c, False)
    pares, dif = costura_igual(h, c, Wh, Wc); ESTAT[L + "_costura"] = {"pares_coincidentes": pares, "dif_max_antes_da_media": dif}
    gravar(h, Wh); gravar(c, Wc); PELES[L] = (h, c, Wh, Wc)
    print("PELE", L, ESTAT[nh], ESTAT[nc], ESTAT[L + "_costura"], flush=True)
bpy.data.objects.remove(prox, do_unlink=True)

# ------------------------------------------------------------------ pelagem, marca e cristais
def bvh_pele(L):
    h, c, Wh, Wc = PELES[L]; pos, fac, W = [], [], []
    for o, Wo in ((h, Wh), (c, Wc)):
        ids = componente_pele(o) if o is h else None; base = len(pos)
        pos += [v.co.copy() for v in o.data.vertices]; W += Wo
        fac += [[base + i for i in p.vertices] for p in o.data.polygons if ids is None or all(i in ids for i in p.vertices)]
    return BVHTree.FromPolygons(pos, fac), pos, fac, W
def ilhas(me):
    pai = list(range(len(me.vertices)))
    def r(i):
        while pai[i] != i: pai[i] = pai[pai[i]]; i = pai[i]
        return i
    for e in me.edges:
        a, b = r(e.vertices[0]), r(e.vertices[1])
        if a != b: pai[a] = b
    g = {}
    for i in range(len(me.vertices)): g.setdefault(r(i), []).append(i)
    return list(g.values())
def pesar_solto(o, L, modo):
    bvh, pos, fac, W = bvh_pele(L); me = o.data; Wo = [None] * len(me.vertices); dist = []
    for g in list(o.vertex_groups): o.vertex_groups.remove(g)
    if modo == "vertice":
        for v in me.vertices: Wo[v.index] = normal(peso_em(v.co, bvh, pos, fac, W)); dist.append(bvh.find_nearest(v.co)[3])
    else:
        for il in ilhas(me):
            raiz = min(il, key=lambda i: bvh.find_nearest(me.vertices[i].co)[3]); dist.append(bvh.find_nearest(me.vertices[raiz].co)[3])
            w = normal(peso_em(me.vertices[raiz].co, bvh, pos, fac, W))
            for i in il: Wo[i] = w
    gravar(o, Wo)
    ESTAT[o.name] = {"modo": modo, "dist_raiz_pele_max": round(max(dist), 4), "dist_raiz_pele_media": round(sum(dist) / len(dist), 4)}
    print("SOLTO", o.name, ESTAT[o.name], flush=True)
pesar_solto(bpy.data.objects["LOW_Pelagem"], "LOW", "ilha"); pesar_solto(bpy.data.objects["LOD1_Pelagem"], "LOD1", "ilha")
pesar_solto(bpy.data.objects["LOW_Marca"], "LOW", "vertice"); pesar_solto(bpy.data.objects["LOW_Cristais"], "LOW", "ilha")

# ------------------------------------------------------------------ registro
for o in sc.objects:
    if o.type == "MESH":
        sem = sum(1 for v in o.data.vertices if not any(o.vertex_groups[e.group].name in OSSOS and e.weight > 0 for e in v.groups))
        inf = max(sum(1 for e in v.groups if o.vertex_groups[e.group].name in OSSOS and e.weight > 0) for v in o.data.vertices)
        ESTAT.setdefault(o.name, {}).update({"sem_influencia": sem, "max_influencias": inf})
R = {"ossos": [{"nome": b.name, "pai": b.parent.name if b.parent else None, "cabeca": [round(c, 4) for c in b.head_local], "cauda": [round(c, 4) for c in b.tail_local],
                "eixo_x": [round(c, 4) for c in b.matrix_local.col[0][:3]], "deforma": b.use_deform} for b in arm_d.bones],
     "heat_ok": HEAT_OK, "estatisticas": ESTAT, "pes": {k: [round(c, 3) for c in v] for k, v in PES.items()}}
PIV["rig_v9"] = {"ossos": len(OSSOS), "raiz": [round(c, 4) for c in arm_d.bones["Raiz"].head_local], "nota": "rig piloto; ver rig_v9.json"}
json.dump(PIV, open(os.path.join(OUT, "rig_pivos.json"), "w"), indent=1); json.dump(R, open(os.path.join(OUT, "rig_v9.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Rig.blend")); print("RIG_V9_OK", flush=True)
