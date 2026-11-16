"""v11: pesos da garganta / babador da juba / peito sobre a v10 (rig_v10/ preservado). So PESOS (sem topologia nova):
o diagnostico (diag_garganta_v11.py) mostrou que as dobras sao da PELE principal (108 de 112 faces viradas), onde o heat
misturava Pescoco2 + Escapula + Umero no peito e na garganta (1.233 vertices a frente do ombro com > 10% de membro).
Por LOD (pele da cabeca e do corpo; mesmos ossos, repouso e acao):
1. pesos AXIAIS da regiao (Coluna3, Pescoco1, Pescoco2, Cabeca) refeitos como transicao suave ao longo da cadeia:
   parametro = posicao ao longo do corpo (y) entre as juntas reais do rig, com faixa de transicao de 45% do osso em cada
   junta; a pele VENTRAL abaixo do eixo do pescoco recua o parametro para tras (peito ancorado na coluna/base do pescoco,
   garganta desliza sobre ele) em proporcao a profundidade (RECUO_VENTRAL por stud abaixo de PROF0);
2. ossos do MEMBRO dianteiro (Escapula/Umero) so na ponta do ombro: somem de y -3,3 a -3,9 e, perto da linha do meio
   (|x| < 0,45), mesmo antes; o lado de fora do ombro (|x| > 0,85) continua ate y -4,2;
3. mistura suave com os pesos da v10 (mascara da regiao: some acima do pescoco/juba alta, atras de y -2,0 e no rosto,
   onde a v10 ja tem Cabeca ~1); facial (Mandibula/Palpebras/Orelhas) intocado;
4. 2 passadas de alisamento so na regiao; pares coincidentes da costura cabeca/corpo voltam a ter o MESMO peso;
   <= 4 influencias, normalizadas;
5. cartoes de pelo da regiao (raiz em y < -2,0, z < 6,4): de novo o peso da pele na raiz; marca (por vertice) e cristais
   (pela base) de novo pela pele nova.
Uso: blender -b rig_v10/CR_LoboArtico_Rig.blend -P garganta_v11.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, math, shutil
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.interpolate import poly_3d_calc
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); sc = bpy.context.scene
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()
for f in ("rig_pivos.json", "acao_v10.json"): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
ARM = bpy.data.objects["LoboArtico_Rig"]; B = ARM.data.bones; OSS = {b.name for b in B}
RECUO_VENTRAL, PROF0, FAIXA = float(os.environ.get("RECUO_VENTRAL", 0.9)), float(os.environ.get("PROF0", 0.4)), 0.45   # varredura: ficha 8.13
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
CADEIA = ["Coluna3", "Pescoco1", "Pescoco2", "Cabeca"]
JY = [B[n].head_local.y for n in CADEIA] + [B["Cabeca"].tail_local.y]          # juntas (y decresce para a frente)
JZ = [B[n].head_local.z for n in CADEIA] + [B["Cabeca"].tail_local.z]
AXIAIS = set(CADEIA) | {"Coluna2"}
FACIAIS = ("Mandibula", "Palpebra", "Orelha")
MEMBRO = ("Escapula", "Umero")
def z_eixo(y):
    for k in range(len(JY) - 1):
        if JY[k + 1] <= y <= JY[k]: t = (JY[k] - y) / (JY[k] - JY[k + 1]); return JZ[k] + (JZ[k + 1] - JZ[k]) * t
    return JZ[0] if y > JY[0] else JZ[-1]
def axial(p):
    """pesos ao longo da cadeia pelo y efetivo (ventral recua para tras = +y)"""
    prof = z_eixo(p.y) - p.z; ye = p.y + RECUO_VENTRAL * max(0.0, prof - PROF0)
    w = {}
    for k in range(len(CADEIA)):
        y0, y1 = JY[k], JY[k + 1]; L = y0 - y1; h = FAIXA * L * 0.5
        ent = 1.0 if k == 0 else suave((y0 + h - ye) / (2 * h))          # entra na junta de tras
        sai = 1.0 if k == len(CADEIA) - 1 else suave((ye - (y1 - h)) / (2 * h))   # sai na junta da frente
        x = ent * sai
        if x > 1e-4: w[CADEIA[k]] = x
    t = sum(w.values()); return {k: x / t for k, x in w.items()}
def membro_fica(p):
    f = suave((p.y + 3.9) / 0.6); lat = suave((abs(p.x) - 0.85) / 0.3) * suave((p.y + 4.2) / 0.3); meio = suave((abs(p.x) - 0.2) / 0.25)
    return max(f * meio, lat)
def mascara(p, w):
    if any(k.startswith(FACIAIS) and x > 0.01 for k, x in w.items()): return 0.0
    if w.get("Cabeca", 0) > 0.97: return 0.0                             # rosto/cranio da v10
    return suave((-2.0 - p.y) / 0.5) * suave((6.3 - p.z) / 0.5) * suave((1.75 - abs(p.x)) / 0.3)
def pesos_novos(p, w):
    m = mascara(p, w)
    if m <= 0: return w, 0.0
    lim = {k: x * membro_fica(p) for k, x in w.items() if k.startswith(MEMBRO)}
    outros = {k: x for k, x in w.items() if not k.startswith(MEMBRO) and k not in AXIAIS}
    resto = max(0.0, 1.0 - sum(lim.values()) - sum(outros.values()))
    n = dict(outros); n.update(lim)
    for k, x in axial(p).items(): n[k] = n.get(k, 0) + x * resto
    ks = set(w) | set(n); out = {k: (1 - m) * w.get(k, 0) + m * n.get(k, 0) for k in ks}
    t = sum(out.values()); return {k: x / t for k, x in out.items() if x / t > 1e-4}, m
REL = {"parametros": {"RECUO_VENTRAL": RECUO_VENTRAL, "PROF0": PROF0, "FAIXA": FAIXA, "juntas_y": [round(y, 3) for y in JY]}}
def ler(o):
    gn = {g.index: g.name for g in o.vertex_groups}
    return [{gn[e.group]: e.weight for e in v.groups if gn[e.group] in OSS and e.weight > 0} for v in o.data.vertices]
def gravar(o, W, ids):
    gi = {g.name: g for g in o.vertex_groups}
    for i in ids:
        for g in o.vertex_groups:
            if g.name in OSS: g.remove([i])
        it = sorted(W[i].items(), key=lambda kv: -kv[1])[:4]; t = sum(x for _, x in it)
        for k, x in it:
            g = gi.get(k) or o.vertex_groups.new(name=k); gi[k] = g; g.add([i], x / t, "REPLACE")
for L in ("LOW", "LOD1", "LOD2"):
    H, C = bpy.data.objects[L + "_Cabeca"], bpy.data.objects[L + "_Corpo"]; r = REL[L] = {}
    WS = {}; MUD = {}
    for o in (H, C):
        W = ler(o); me = o.data; novo = list(W); ms = []
        for i, v in enumerate(me.vertices):
            nw, m = pesos_novos(v.co, W[i]); novo[i] = nw; ms.append(m)
        viz = [[] for _ in me.vertices]
        for e in me.edges: viz[e.vertices[0]].append(e.vertices[1]); viz[e.vertices[1]].append(e.vertices[0])
        for _ in range(2):                                              # alisamento so onde a mascara age
            nx = list(novo)
            for i in range(len(novo)):
                if ms[i] <= 0.05 or not viz[i]: continue
                acc = {}
                for j in viz[i]:
                    for k, x in novo[j].items(): acc[k] = acc.get(k, 0) + x / len(viz[i])
                if any(k.startswith(FACIAIS) for k in acc) or any(k.startswith(FACIAIS) for k in novo[i]): continue
                b = 0.5 * ms[i]; nx[i] = {k: (1 - b) * novo[i].get(k, 0) + b * acc.get(k, 0) for k in set(novo[i]) | set(acc)}
            novo = nx
        WS[o.name] = novo; MUD[o.name] = [i for i, m in enumerate(ms) if m > 0.001]
        r[o.name] = {"vertices_alterados": len(MUD[o.name]),
                     "membro_>0.1_a_frente_do_ombro_antes_depois": [sum(1 for i, v in enumerate(me.vertices) if v.co.y < -3.6 and v.co.z < 5.6 and sum(x for k, x in W[i].items() if k.startswith(MEMBRO)) > 0.1),
                                                                     sum(1 for i, v in enumerate(me.vertices) if v.co.y < -3.6 and v.co.z < 5.6 and sum(x for k, x in novo[i].items() if k.startswith(MEMBRO)) > 0.1)]}
    kd = KDTree(len(C.data.vertices))                                   # costura: pares coincidentes com o mesmo peso
    for v in C.data.vertices: kd.insert(v.co, v.index)
    kd.balance(); pares = 0; dif = 0.0
    for v in H.data.vertices:
        p, j, d = kd.find(v.co)
        if d > 1e-5: continue
        a_, b_ = WS[H.name][v.index], WS[C.name][j]; ks = set(a_) | set(b_)
        dif = max(dif, max(abs(a_.get(k, 0) - b_.get(k, 0)) for k in ks)); m = {k: (a_.get(k, 0) + b_.get(k, 0)) / 2 for k in ks}
        WS[H.name][v.index] = m; WS[C.name][j] = dict(m); pares += 1
        if v.index not in MUD[H.name]: MUD[H.name].append(v.index)
        if j not in MUD[C.name]: MUD[C.name].append(j)
    r["costura"] = {"pares": pares, "dif_max_antes_da_media": round(dif, 4)}
    for o in (H, C): gravar(o, WS[o.name], MUD[o.name])
    print("V11", L, json.dumps(r), flush=True)
def ilhas(me):
    pai = list(range(len(me.vertices)))
    def rr(i):
        while pai[i] != i: pai[i] = pai[pai[i]]; i = pai[i]
        return i
    for e in me.edges:
        x_, y_ = rr(e.vertices[0]), rr(e.vertices[1])
        if x_ != y_: pai[x_] = y_
    g = {}
    for i in range(len(me.vertices)): g.setdefault(rr(i), []).append(i)
    return list(g.values())
for L in ("LOW", "LOD1"):
    H, C = bpy.data.objects[L + "_Cabeca"], bpy.data.objects[L + "_Corpo"]; F = bpy.data.objects[L + "_Pelagem"]
    pos, fac, WW = [], [], []
    for o in (H, C):
        b = len(pos); pos += [v.co.copy() for v in o.data.vertices]; WW += ler(o); uvl = o.data.uv_layers.active.data
        fac += [[b + i for i in p.vertices] for p in o.data.polygons if not (o is H and uvl[p.loop_start].uv.x >= 0.9)]
    bvh = BVHTree.FromPolygons(pos, fac); fm = F.data; n = 0; dmax = 0.0
    for il in ilhas(fm):
        raiz = min(il, key=lambda i: bvh.find_nearest(fm.vertices[i].co)[3]); p = fm.vertices[raiz].co
        if not (p.y < -2.0 and p.z < 6.4): continue
        loc, nr, fi, d = bvh.find_nearest(p); dmax = max(dmax, d); bc = poly_3d_calc([pos[i] for i in fac[fi]], loc); w = {}
        for i, bb in zip(fac[fi], bc):
            for k, x in WW[i].items(): w[k] = w.get(k, 0) + x * bb
        it = sorted(w.items(), key=lambda kv: -kv[1])[:4]; t = sum(x for _, x in it)
        for g in F.vertex_groups: g.remove(il)
        for k, x in it:
            g = F.vertex_groups.get(k) or F.vertex_groups.new(name=k); g.add(il, x / t, "REPLACE")
        n += 1
    REL[L + "_pelagem"] = {"cartoes_repesados": n, "dist_raiz_pele_max": round(dmax, 4)}; print("V11 pelagem", L, REL[L + "_pelagem"], flush=True)
# marca (vertice a vertice) e cristais (cada um pelo ponto da base) seguem a pele NOVA do LOD0 (sem isto a marca descolava
# ate 0,039 com a cabeca virada: a pele sob ela mudou de peso)
H, C = bpy.data.objects["LOW_Cabeca"], bpy.data.objects["LOW_Corpo"]; pos, fac, WW = [], [], []
for o in (H, C):
    b = len(pos); pos += [v.co.copy() for v in o.data.vertices]; WW += ler(o); uvl = o.data.uv_layers.active.data
    fac += [[b + i for i in p.vertices] for p in o.data.polygons if not (o is H and uvl[p.loop_start].uv.x >= 0.9)]
bvh = BVHTree.FromPolygons(pos, fac)
def peso_pele(p):
    loc, nr, fi, d = bvh.find_nearest(p); bc = poly_3d_calc([pos[i] for i in fac[fi]], loc); w = {}
    for i, bb in zip(fac[fi], bc):
        for k, x in WW[i].items(): w[k] = w.get(k, 0) + x * bb
    it = sorted(w.items(), key=lambda kv: -kv[1])[:4]; t = sum(x for _, x in it); return {k: x / t for k, x in it}
for nome, modo in (("LOW_Marca", "vertice"), ("LOW_Cristais", "ilha")):
    o = bpy.data.objects[nome]; me = o.data; Wn = [None] * len(me.vertices)
    if modo == "vertice":
        for v in me.vertices: Wn[v.index] = peso_pele(v.co)
    else:
        for il in ilhas(me):
            raiz = min(il, key=lambda i: bvh.find_nearest(me.vertices[i].co)[3]); w = peso_pele(me.vertices[raiz].co)
            for i in il: Wn[i] = w
    gravar(o, Wn, range(len(me.vertices))); REL[nome] = {"repesado": modo, "vertices": len(me.vertices)}
RJ = json.load(open(os.path.join(SRC, "rig_v10.json"))); RJ["v11_garganta"] = REL
json.dump(RJ, open(os.path.join(OUT, "rig_v11.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Rig.blend")); print("V11_OK", flush=True)
