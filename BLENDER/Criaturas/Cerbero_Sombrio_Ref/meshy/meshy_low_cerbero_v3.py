"""Cerbero Sombrio (Meshy m1) -- malha de JOGO v3: low_v2 + BOCAS das tres cabecas + ponta da cauda arredondada.
Base: meshy_low_cerbero.py (low_v2). Boca: mesmo metodo do Urso v2 (Urso_Silvestre_Ref/v2/meshy/meshy_low.py), num referencial
LOCAL por cabeca (ponta do focinho T, frente f horizontal, lado s = f x z, altura z):
  1) linha dos labios: leitura inicial nos renders laterais (17/11) refinada na malha: em cada ponto, o sulco = menor largura lateral;
  2) fenda fina ate a comissura + 2 cavidades elipsoides (recortadas na malha densa do voxel, ANTES da reducao);
  3) pecas da boca numa malha propria "Cerbero_Bocas": gengivas, dentes (caninos fortes) escondidos com a boca fechada, lingua;
     atributos "mand" (1 = mandibula) e "cabeca" (0=C, 1=E, 2=D) para o rig;
  4) bake da bruta (cor, normal, rugosidade); interior da boca pintado a parte;
  5) renders: geral, boca fechada e ABERTA (giro procedural so para revisao, nao e rig).
Uso: blender -b -t 4 modelo/CR_Cerbero_meshy_bruto.blend -P meshy_low_cerbero_v3.py -- <saida_dir> [alvo=18000] [voxel=0.005] [res=1024]"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
def arg(n, d): return type(d)(next((a.split("=")[1] for a in ARGS if a.startswith(n + "=")), d))
ALVO, VOX, R = arg("alvo", 18000), arg("voxel", 0.005), arg("res", 1024)
sc = bpy.context.scene
sc.render.threads_mode = "FIXED"; sc.render.threads = 4          # PC compartilhado com o usuario
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
def mod(o, tipo, **kw):
    ativar(o); m = o.modifiers.new(tipo, tipo)
    for k, v in kw.items(): setattr(m, k, v)
    bpy.ops.object.modifier_apply(modifier=m.name)
for o in [o for o in sc.objects if o.type in ("CAMERA", "LIGHT")]: bpy.data.objects.remove(o)
HIGH = bpy.data.objects["Mesh_0"]; HIGH.name = "CR_Cerbero_Meshy"
HIGH.data.transform(Matrix.Translation((0, 0, -min(v.co.z for v in HIGH.data.vertices))))   # patas no chao (z=0)
Y_CAB, Z_CAB, Z_PATA = -0.42, 0.95, 0.14
def regiao(p):
    if p.y < Y_CAB and p.z > Z_CAB: return "cabecas"
    if p.z < Z_PATA: return "patas"
    return "corpo"

# ------------------------------------------------------------------ referencial das cabecas (sondado em 17/11, sonda_cab.py)
CABS = {"C": ((-0.0102, -0.951, 1.3438), (0.1569, -0.9876)), "E": ((-0.5132, -0.8128, 1.1428), (-0.7816, -0.6238)),
        "D": ((0.5129, -0.7218, 1.1808), (0.9029, -0.4299))}
# linha dos labios lida nos renders laterais: (a = frente a partir da ponta, h = altura a partir da ponta); da comissura para a frente
LAB0 = {"C": [(-0.145, -0.0525), (-0.10, -0.060), (-0.05, -0.0675), (-0.025, -0.070), (0.0, -0.070)],
        "E": [(-0.1025, -0.0175), (-0.07, -0.0225), (-0.04, -0.030), (-0.005, -0.035), (0.01, -0.035)],
        "D": [(-0.1275, -0.0525), (-0.10, -0.055), (-0.06, -0.0625), (-0.03, -0.0625), (-0.015, -0.060)]}
ORDEM = ["C", "E", "D"]
class Cab:
    def __init__(s_, k):
        t, f = CABS[k]; s_.k = k; s_.T = V(t); s_.f = V((f[0], f[1], 0)).normalized(); s_.s = s_.f.cross(V((0, 0, 1))).normalized()
        s_.z = V((0, 0, 1)); s_.M = Matrix((s_.s, s_.f, s_.z)).transposed()          # colunas: lado, frente, altura
    def P(s_, a, l, h): return s_.T + s_.f * a + s_.s * l + s_.z * h
    def loc(s_, p): r = V(p) - s_.T; return r.dot(s_.f), r.dot(s_.s), r.dot(s_.z)
    def lip(s_, a):
        L = s_.LAB
        if a <= L[0][0]: return L[0][1]
        for (a0, h0), (a1, h1) in zip(L, L[1:]):
            if a0 <= a <= a1: return lerp(h0, h1, (a - a0) / (a1 - a0))
        return L[-1][1]
CB = {k: Cab(k) for k in ORDEM}
BVH_H = BVHTree.FromObject(HIGH, bpy.context.evaluated_depsgraph_get())
def largura(c, a, h, bvh):
    """meia-largura lateral do focinho no ponto (a,h): media dos dois lados (raio de fora para dentro)."""
    ls = []
    for sg in (1, -1):
        o_ = c.P(a, sg * 0.25, h); hit = bvh.ray_cast(o_, -c.s * sg, 0.25)
        if hit[0] is not None: ls.append(abs(c.loc(hit[0])[1]))
    return sum(ls) / len(ls) if len(ls) == 2 else None
def centralizar(c):
    """v3b: a ponta sondada nem sempre fica no meio do focinho (cabeca E). Mede o meio entre os dois lados em 3 pontos,
    recentra T e gira f pela inclinacao da linha dos meios."""
    for _ in range(2):
        pts = []
        for a in (-0.025, -0.055, -0.085):
            h = np.interp(a, [p[0] for p in LAB0[c.k]], [p[1] for p in LAB0[c.k]]) + 0.018
            ls = []
            for sg in (1, -1):
                hit = BVH_H.ray_cast(c.P(a, sg * 0.25, h), -c.s * sg, 0.25)
                if hit[0] is not None: ls.append(c.loc(hit[0])[1])
            if len(ls) == 2: pts.append((a, (ls[0] + ls[1]) / 2))
        if len(pts) < 2: return
        A = np.array(pts); inc, l0 = np.polyfit(A[:, 0], A[:, 1], 1)
        c.T = c.T + c.s * l0
        c.f = (c.f + c.s * inc).normalized(); c.s = c.f.cross(c.z).normalized(); c.M = Matrix((c.s, c.f, c.z)).transposed()
    print("CENTRO", c.k, "T", tuple(round(x, 4) for x in c.T), "f", tuple(round(x, 4) for x in c.f), flush=True)
for c in CB.values():
    centralizar(c)
    lab = []
    for a, h0 in [(lerp(LAB0[c.k][0][0], LAB0[c.k][-1][0], i / 12), None) for i in range(13)]:
        h0 = np.interp(a, [p[0] for p in LAB0[c.k]], [p[1] for p in LAB0[c.k]])
        cand = [(largura(c, a, h0 + dh, BVH_H), h0 + dh) for dh in np.arange(-0.012, 0.0121, 0.0008)]
        cand = [x for x in cand if x[0] is not None]
        lab.append((a, min(cand)[1] if cand else h0))
    hs = [h for _, h in lab]; hs = [np.mean(hs[max(0, i - 1):i + 2]) for i in range(len(hs))]        # suaviza
    c.LAB = [(a, float(h)) for (a, _), h in zip(lab, hs)]
    c.CANTO, c.FRENTE = c.LAB[0][0], c.LAB[-1][0]; c.L = c.FRENTE - c.CANTO
    c.HW = largura(c, c.CANTO + 0.55 * c.L, c.lip(c.CANTO + 0.55 * c.L), BVH_H) or 0.05
    print("LABIO", c.k, "L=%.3f HW=%.3f" % (c.L, c.HW), [(round(a, 3), round(h, 4)) for a, h in c.LAB], flush=True)

# ------------------------------------------------------------------ 1) voxel, ponta da cauda arredondada
low = HIGH.copy(); low.data = HIGH.data.copy(); low.name = low.data.name = "Cerbero_Corpo"; sc.collection.objects.link(low)
low.data.materials.clear()
mod(low, "REMESH", mode="VOXEL", voxel_size=VOX, use_smooth_shade=True)
print("LOW voxel", tris(low), flush=True)
bm = bmesh.new(); bm.from_mesh(low.data); vist = set(); ilhas = []
for v0 in bm.verts:
    if v0.index in vist: continue
    il = []; pilha = [v0]
    while pilha:
        x = pilha.pop()
        if x.index in vist: continue
        vist.add(x.index); il.append(x); pilha.extend(e.other_vert(x) for e in x.link_edges)
    ilhas.append(il)
ilhas.sort(key=len, reverse=True)
bmesh.ops.delete(bm, geom=[v for il in ilhas[1:] if len(il) < 0.01 * len(bm.verts) for v in il], context="VERTS")
TIP, RT = V((-0.04, 0.947, 0.822)), arg("rcauda", 0.12)        # ponta em cone da cauda (render lateral 17/11)
Q = TIP - V((0, 0.48, 0.88)) * 0.09                               # ponto dentro da cauda, atras do cone
bm.verts.ensure_lookup_table()
zona = [(v, suave(1 - (v.co - TIP).length / RT)) for v in bm.verts if (v.co - TIP).length < RT]
for v, w in zona: v.co = v.co + (Q - v.co) * (0.55 * w * w)     # v3b: encurta o cone em direcao ao interior
for _ in range(arg("itcauda", 30)):
    novos = [(v, v.co + w * 0.5 * (sum((e.other_vert(v).co for e in v.link_edges), V()) / max(1, len(v.link_edges)) - v.co)) for v, w in zona]
    for v, p in novos: v.co = p
print("CAUDA verts suavizados", len(zona), flush=True)
bm.to_mesh(low.data); bm.free()

# ------------------------------------------------------------------ 2) bocas: fenda + cavidades (malha densa, antes da reducao)
M_PELE = bpy.data.materials.new("M_tmp_Pele"); low.data.materials.append(M_PELE)
M_BOCA = bpy.data.materials.new("M_tmp_Boca")
def fenda(c):
    m = bpy.data.meshes.new("Fenda_" + c.k); b = bmesh.new(); N = 20; secs = []
    for i in range(N + 1):
        t = i / N; a = lerp(c.FRENTE + 0.04, c.CANTO, t); h = c.lip(a)
        meia = 0.0007 * (1 - suave((t - 0.86) / 0.14)) + 0.0003     # v3b: mais fina (a frente mostrava os incisivos)
        hw = 0.11                                                    # atravessa o focinho dos dois lados
        secs.append([b.verts.new(c.P(a, ll, h + hh)) for ll, hh in ((-hw, -meia), (hw, -meia), (hw, meia), (-hw, meia))])
    for p_, q_ in zip(secs, secs[1:]):
        for k in range(4): b.faces.new((p_[k], p_[(k + 1) % 4], q_[(k + 1) % 4], q_[k]))
    b.faces.new(secs[0][::-1]); b.faces.new(secs[-1]); bmesh.ops.recalc_face_normals(b, faces=b.faces)
    b.to_mesh(m); b.free(); o = bpy.data.objects.new("Fenda_" + c.k, m); sc.collection.objects.link(o); return o
def elipsoide(nome, c, a, h, raios, seg=20):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=seg, ring_count=seg // 2)
    o = bpy.context.object; o.name = nome
    o.matrix_world = Matrix.Translation(c.P(a, 0, h)) @ c.M.to_4x4() @ Matrix.Diagonal((*raios, 1))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); return o
cortes = bpy.data.collections.new("Cortes"); sc.collection.children.link(cortes)
for c in CB.values():
    a1, a2 = c.CANTO + 0.55 * c.L, c.CANTO + 0.30 * c.L
    for o in (fenda(c),
              elipsoide("Cav1_" + c.k, c, a1, c.lip(a1) + 0.0005, (0.50 * c.HW, 0.33 * c.L, 0.085 * c.L)),   # nao alcanca a parede da frente
              elipsoide("Cav2_" + c.k, c, a2, c.lip(a2), (0.42 * c.HW, 0.22 * c.L, 0.10 * c.L))):             # estreita: nao rompe o lado
        o.data.materials.append(M_BOCA)
        for col in o.users_collection: col.objects.unlink(o)
        cortes.objects.link(o)
ativar(low); bo = low.modifiers.new("Bocas", "BOOLEAN"); bo.operation = "DIFFERENCE"; bo.solver = "EXACT"
bo.operand_type = "COLLECTION"; bo.collection = cortes; bo.material_mode = "TRANSFER"; bpy.ops.object.modifier_apply(modifier=bo.name)
for o in list(cortes.objects): bpy.data.objects.remove(o)
mod(low, "TRIANGULATE")
print("BOCA faces internas (densa)", sum(1 for p in low.data.polygons if p.material_index == 1), flush=True)
def zona_boca(p):
    for c in CB.values():
        a, l, h = c.loc(p)
        if c.CANTO - 0.03 < a < c.FRENTE + 0.02 and abs(l) < c.HW + 0.03 and abs(h - c.lip(a)) < 0.03: return c
    return None

# ------------------------------------------------------------------ 3) reducao (labios e interior mais densos)
vg = low.vertex_groups.new(name="densidade")
W_CAB, W_PATA, W_BOCA = arg("wc", 0.85), arg("wp", 0.92), arg("wb", 0.35)
for v in low.data.vertices:
    r = regiao(v.co)
    w = W_CAB if r == "cabecas" else W_PATA if r == "patas" else 1.0
    if r == "cabecas" and zona_boca(v.co): w = W_BOCA
    vg.add([v.index], w, "REPLACE")
ativar(low); dm = low.modifiers.new("Dec", "DECIMATE"); dm.ratio = ALVO / tris(low); dm.use_collapse_triangulate = True
dm.vertex_group = "densidade"; dm.vertex_group_factor = arg("fator", 1.0); bpy.ops.object.modifier_apply(modifier=dm.name)
mod(low, "TRIANGULATE"); low.vertex_groups.clear()
for p in low.data.polygons: p.use_smooth = True
REG = {"cabecas": 0, "patas": 0, "corpo": 0}
for f in low.data.polygons: REG[regiao(f.center)] += len(f.vertices) - 2
print("LOW reduzido", tris(low), "REGIOES", REG, "boca faces", sum(1 for p in low.data.polygons if p.material_index == 1), flush=True)
BVH = BVHTree.FromObject(low, bpy.context.evaluated_depsgraph_get())

# ------------------------------------------------------------------ 4) pecas da boca (malha propria)
def tubo(pts, raios, nome, achat=0.85, sub=1):
    m = bpy.data.meshes.new(nome); o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = pts[0]; b = bmesh.new(); vs = [b.verts.new(p - pts[0]) for p in pts]
    for a, c_ in zip(vs, vs[1:]): b.edges.new((a, c_))
    b.to_mesh(m); b.free()
    k = o.modifiers.new("Pele", "SKIN"); k.use_smooth_shade = True
    for i, d in enumerate(m.skin_vertices[0].data): d.radius = (raios[i], raios[i] * achat); d.use_root = i == 0
    if sub:
        s2 = o.modifiers.new("Sub", "SUBSURF"); s2.levels = s2.render_levels = sub
    ativar(o)
    for mm in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mm.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o
def arcada(c, a, h, sg, recuo):
    """ultima parede atravessada de dentro para fora (lado sg) no ponto (a,h), recuada para dentro."""
    ult = None; o_ = c.P(a, 0, h)
    for _ in range(6):
        hit = BVH.ray_cast(o_, c.s * sg, 0.3)
        if hit[0] is None: break
        ult = hit[0]; o_ = hit[0] + c.s * sg * 0.0008
    if ult is None: return None
    a_, l_, _ = c.loc(ult); return c.P(a, math.copysign(max(0.004, abs(l_) - recuo), sg), h)
def visivel(q):
    """ponta visivel com a boca fechada: algum raio escapa sem bater na pele"""
    return any(BVH.ray_cast(q, d.normalized(), 0.6)[0] is None for d in
               (V((1, 0, 0)), V((-1, 0, 0)), V((0, 1, 0)), V((0, -1, 0)), V((0.7, -0.7, 0)), V((-0.7, -0.7, 0)), V((0.7, 0.7, 0)),
                V((-0.7, 0.7, 0)), V((0, 0, 1)), V((0, 0, -1)), V((0.6, 0, -0.8)), V((-0.6, 0, -0.8)), V((0, 0.6, -0.8)), V((0, -0.6, -0.8))))
PECAS = []                                       # (objeto, papel, mand, cabeca)
AJUSTE = []
for ci, c in enumerate(CB[k] for k in ORDEM):
    L, rec = c.L, 0.17 * c.HW + 0.004
    def fa(fr): return c.FRENTE - fr * L                             # fracao do comprimento a partir da frente
    ARCO_INF = {sg: [(fa(fr), arcada(c, fa(fr), c.lip(fa(fr)) - 0.003, sg, 0.0)) for fr in np.linspace(0.06, 0.9, 13)] for sg in (1, -1)}
    def lim_inf(a, sg):
        p = min(ARCO_INF[sg], key=lambda x: abs(x[0] - a))[1]
        return abs(c.loc(p)[1]) if p is not None else 9.0
    for sup in (True, False):
        dz = -1 if sup else 1
        def zg(a, sup=sup): return c.lip(a) + (0.003 if sup else -0.003)
        for sg in (1, -1):
            arco = []
            for fr in np.linspace(0.28, 0.85, 11):                  # v3c: gengiva comeca atras da frente dos labios
                a = fa(fr); p = arcada(c, a, zg(a), sg, rec)
                if p is None: continue
                _, l_, _ = c.loc(p)
                if sup: l_ = math.copysign(min(abs(l_), lim_inf(a, sg) - 0.6 * rec), sg)
                arco.append((a, c.P(a, l_, zg(a))))
            if len(arco) < 4: print("ARCADA_FALHOU", c.k, sup, sg, flush=True); continue
            gpts = [p - c.z * dz * 0.0018 for _, p in arco[::2]]
            gpts = [p for p in gpts if not visivel(p)]                 # v3d: ponto da gengiva visivel de boca fechada fica fora (so a gengiva)
            if len(gpts) >= 2: PECAS.append((tubo(gpts, [0.0065] * len(gpts), "Gengiva", 0.75, 0), "gengiva", not sup, ci))
            def em(a): return min(arco, key=lambda x: abs(x[0] - a))[1].copy()
            # fracao da frente, comprimento e raio em fracoes de L (canino forte); pontas DENTRO da carne com a boca fechada
            TAB = [(0.30, 0.085, 0.024), (0.34, 0.09, 0.026), (0.40, 0.24 if sup else 0.20, 0.060),   # v3c: tudo mais para tras
                   (0.54, 0.07, 0.030), (0.65, 0.08, 0.034), (0.78, 0.09, 0.050)]
            for kk, (fr, comp_r, r_r) in enumerate(TAB):
                a = fa(fr); p = em(a); p = p + c.z * (zg(a) - c.loc(p)[2]) - c.z * dz * 0.0045      # raiz enterrada na gengiva
                comp = comp0 = comp_r * L; r = r_r * L
                curva = c.s * (-math.copysign(1, c.loc(p)[1]) * 0.12 * comp) if kk == 2 else V()   # caninos curvam para dentro
                for _ in range(10):
                    ponta = p + c.z * dz * comp + curva; meio = p + c.z * dz * comp * 0.55 + curva * 0.5
                    if not (visivel(ponta) or visivel(meio)): break
                    if comp > comp0 * 0.6: comp *= 0.9
                    else: p = p - c.f * 0.002; p = p - c.s * math.copysign(0.0015, c.loc(p)[1])
                AJUSTE.append((c.k, "sup" if sup else "inf", sg, kk, round(comp0, 4), round(comp, 4)))
                pts = [p, p + c.z * dz * comp * 0.55 + curva * 0.5, p + c.z * dz * comp + curva]
                PECAS.append((tubo(pts, [r, r * (0.72 if kk == 2 else 0.85), 0.0008 if kk <= 2 else r * 0.6], "Dente",
                                   0.8 if kk == 2 else 0.6, 0), "dente", not sup, ci))   # v3b: sem subdivisao (custo)
    al = c.CANTO + 0.45 * L
    PECAS.append((elipsoide("Lingua_" + c.k, c, al, c.lip(al) - 0.134 * L, (0.36 * c.HW, 0.29 * L, 0.044 * L), 12), "lingua", True, ci))
print("BOCA pecas", len(PECAS), "dentes encurtados", [x for x in AJUSTE if x[4] != x[5]], flush=True)

# ------------------------------------------------------------------ 5) separa cabecas, UV + bake
def separar(o, cond, nome):
    c_ = o.copy(); c_.data = o.data.copy(); c_.name = c_.data.name = nome; sc.collection.objects.link(c_)
    for o_, manter in ((c_, True), (o, False)):
        bm_ = bmesh.new(); bm_.from_mesh(o_.data)
        bmesh.ops.delete(bm_, geom=[f for f in bm_.faces if cond(f.calc_center_median()) != manter], context="FACES")
        bm_.to_mesh(o_.data); bm_.free()
    return c_
CAB = separar(low, lambda p: regiao(p) == "cabecas", "Cerbero_Cabecas")
def uv_proj(o, margem=0.003):
    ativar(o); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margem, area_weight=0.0)
    bpy.ops.uv.pack_islands(margin=margem); bpy.ops.object.mode_set(mode="OBJECT")
sc.render.engine = "CYCLES"; sc.cycles.samples = 4; sc.cycles.device = "CPU"
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.008; bk.max_ray_distance = 0.03; bk.margin = 8
def preencher_falhas(img):
    px = np.array(img.pixels[:], dtype=np.float32).reshape(R, R, 4)
    for _ in range(12):
        falha = (px[..., 0] + px[..., 1] + px[..., 2]) < 1e-4
        if not falha.any(): break
        viz = np.zeros_like(px[..., :3]); cont = np.zeros((R, R, 1), np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.roll(px, (dy, dx), axis=(0, 1)); ok = ((sh[..., 0] + sh[..., 1] + sh[..., 2]) >= 1e-4)[..., None]
            viz += sh[..., :3] * ok; cont += ok
        preenche = falha & (cont[..., 0] > 0)
        px[preenche, :3] = (viz / np.maximum(cont, 1))[preenche]
    img.pixels[:] = px.ravel()
def assar(o, prefixo):
    uv_proj(o)
    imgs = {k: bpy.data.images.new(f"{prefixo}_{k}", R, R) for k in ("Cor", "Normal", "Rugosidade")}
    imgs["Normal"].colorspace_settings.name = "Non-Color"; imgs["Rugosidade"].colorspace_settings.name = "Non-Color"
    idx_boca = [p.index for p in o.data.polygons if p.material_index == 1]
    mat = bpy.data.materials.new("M_" + prefixo[2:]); mat.use_nodes = True; nt = mat.node_tree
    for img in imgs.values():
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img; tx.name = img.name
    o.data.materials.clear(); o.data.materials.append(mat)
    for o_ in sc.objects: o_.select_set(False)
    HIGH.select_set(True); o.select_set(True); bpy.context.view_layer.objects.active = o
    nt.nodes.active = nt.nodes[imgs["Cor"].name]; bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"})
    nt.nodes.active = nt.nodes[imgs["Normal"].name]; bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")
    nt.nodes.active = nt.nodes[imgs["Rugosidade"].name]; bpy.ops.object.bake(type="ROUGHNESS")
    preencher_falhas(imgs["Cor"])
    if idx_boca:                                  # interior da boca: escuro perto dos labios, vermelho escuro no fundo; normal plana
        pc, pn, pr = (np.array(imgs[k].pixels[:], dtype=np.float32).reshape(R, R, 4) for k in ("Cor", "Normal", "Rugosidade"))
        uvl = o.data.uv_layers.active.data
        for i in idx_boca:
            poly = o.data.polygons[i]; us = [uvl[li].uv for li in poly.loop_indices]
            xs = [u.x * R for u in us]; ys = [u.y * R for u in us]
            x0, x1, y0, y1 = max(0, int(min(xs)) - 2), min(R, int(max(xs)) + 3), max(0, int(min(ys)) - 2), min(R, int(max(ys)) + 3)
            c = min(CB.values(), key=lambda c_: (poly.center - c_.T).length)
            a, _, _ = c.loc(poly.center); prof = suave((c.FRENTE - a - 0.10 * c.L) / (0.35 * c.L))
            pc[y0:y1, x0:x1] = (lerp(0.03, 0.30, prof), lerp(0.012, 0.05, prof), lerp(0.014, 0.055, prof), 1.0)
            pn[y0:y1, x0:x1] = (0.5, 0.5, 1.0, 1.0); pr[y0:y1, x0:x1] = (0.45, 0.45, 0.45, 1.0)
        for k, px in (("Cor", pc), ("Normal", pn), ("Rugosidade", pr)): imgs[k].pixels[:] = px.ravel()
    for img in imgs.values():
        img.filepath_raw = os.path.join(OUT, img.name + ".png"); img.file_format = "PNG"; img.save()
    b_ = nt.nodes["Principled BSDF"]; nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(nt.nodes[imgs["Cor"].name].outputs["Color"], b_.inputs["Base Color"])
    nt.links.new(nt.nodes[imgs["Normal"].name].outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs[0], b_.inputs["Normal"])
    nt.links.new(nt.nodes[imgs["Rugosidade"].name].outputs["Color"], b_.inputs["Roughness"])
    return len(idx_boca)
nb = assar(CAB, "T_Cerbero_Cabecas"); assar(low, "T_Cerbero_Corpo")
print("BAKE_OK cabecas", tris(CAB), "corpo", tris(low), "faces de boca pintadas", nb, flush=True)
# bocas: junta pecas, UV, textura pequena pintada por papel
CORES = {"dente": (0.78, 0.70, 0.56), "gengiva": (0.30, 0.06, 0.07), "lingua": (0.36, 0.08, 0.09)}
for o, papel, mand, ci in PECAS:
    a_ = o.data.attributes.new("papel", "FLOAT_COLOR", "POINT"); am = o.data.attributes.new("mand", "FLOAT", "POINT")
    ac = o.data.attributes.new("cabeca", "INT", "POINT")
    for i in range(len(o.data.vertices)): a_.data[i].color = (*CORES[papel], 1.0); am.data[i].value = 1.0 if mand else 0.0; ac.data[i].value = ci
ativar(PECAS[0][0])
for o, _, _, _ in PECAS: o.select_set(True)
bpy.ops.object.join(); BOCA = bpy.context.object; BOCA.name = BOCA.data.name = "Cerbero_Bocas"
mod(BOCA, "TRIANGULATE"); uv_proj(BOCA, 0.01)
img_b = bpy.data.images.new("T_Cerbero_Bocas_Cor", 256, 256)
mb = bpy.data.materials.new("M_Cerbero_Bocas"); mb.use_nodes = True; ntb = mb.node_tree; bb = ntb.nodes["Principled BSDF"]
atn = ntb.nodes.new("ShaderNodeAttribute"); atn.attribute_name = "papel"; ntb.links.new(atn.outputs["Color"], bb.inputs["Base Color"])
tb = ntb.nodes.new("ShaderNodeTexImage"); tb.image = img_b; ntb.nodes.active = tb; BOCA.data.materials.append(mb)
bk.use_selected_to_active = False; ativar(BOCA); bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"})
img_b.filepath_raw = os.path.join(OUT, "T_Cerbero_Bocas_Cor.png"); img_b.file_format = "PNG"; img_b.save()
ntb.links.new(tb.outputs["Color"], bb.inputs["Base Color"]); bb.inputs["Roughness"].default_value = 0.35

# ------------------------------------------------------------------ 6) exporta + relatorio
JOGO = [CAB, low, BOCA]
HIGH.hide_render = True
for o in sc.objects: o.select_set(o in JOGO)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "CR_Cerbero_Sombrio_LOW.glb"), use_selection=True, export_format="GLB",
                          export_yup=True, export_apply=True, export_image_format="AUTO", export_materials="EXPORT", export_attributes=True)
pts = np.array([(o.matrix_world @ v.co)[:] for o in JOGO[:2] for v in o.data.vertices])
rel = {"regioes": REG, "pesos": [W_CAB, W_PATA, W_BOCA], "alvo": ALVO, "voxel": VOX, "textura": R,
       "malhas": {o.name: {"tris": tris(o), "material": o.data.materials[0].name} for o in JOGO},
       "tris_total": sum(tris(o) for o in JOGO), "bruto_tris": tris(HIGH),
       "labios": {c.k: {"L": round(c.L, 4), "meia_largura": round(c.HW, 4), "linha": [(round(a, 4), round(h, 4)) for a, h in c.LAB]} for c in CB.values()},
       "dentes_encurtados": [x for x in AJUSTE if x[4] != x[5]],
       "medidas": {"comprimento": float(np.ptp(pts[:, 1])), "largura": float(np.ptp(pts[:, 0])), "altura": float(pts[:, 2].max()),
                   "pata_min_z": float(pts[:, 2].min())}}
json.dump(rel, open(os.path.join(OUT, "relatorio_low.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("REL", json.dumps({k: rel[k] for k in ("malhas", "tris_total")}), flush=True)

# ------------------------------------------------------------------ 7) renders: geral, bocas fechadas e ABERTAS (giro procedural de revisao)
def lin(hx):
    c_ = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c_)
def camera(nome, loc, alvo, lente):
    c_ = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c_); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); c_.lens = lente; return o
CAMS = {"tres_quartos": (camera("Cam_34", (-2.6, -3.0, 1.9), (0, 0, 0.72), 58), (1000, 760)),
        "perfil": (camera("Cam_Perfil", (4.4, 0, 0.9), (0, 0, 0.75), 58), (1000, 700)),
        "cauda": (camera("Cam_Cauda", (1.4, 1.6, 1.1), (0, 0.85, 0.75), 70), (800, 700))}
for c in CB.values():                                  # cada boca vista de frente-lado, a 3/4
    alvo = c.P(c.CANTO + 0.4 * c.L, 0, c.lip(c.CANTO + 0.4 * c.L))
    CAMS["boca_" + c.k] = (camera("Cam_Boca_" + c.k, alvo + c.f * 0.42 + c.s * 0.26 + c.z * 0.03, alvo, 60), (800, 700))
mundo = bpy.data.worlds.new("Fundo"); sc.world = mundo; mundo.use_nodes = True
bg = mundo.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (*lin("8a8580"), 1); bg.inputs["Strength"].default_value = 1.1
sd = bpy.data.lights.new("Sol", "SUN"); sd.energy = 3.0; sd.angle = math.radians(12)
so = bpy.data.objects.new("Sol", sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
sc.view_settings.view_transform = "Standard"; sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
sc.render.film_transparent = False; sc.render.resolution_percentage = 100
def render(cam, res, arq):
    sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = res; sc.render.filepath = os.path.join(OUT, arq)
    bpy.ops.render.render(write_still=True)
sc.render.engine = "BLENDER_EEVEE"
try: sc.eevee.taa_render_samples = 32
except Exception: pass
for n in ("tres_quartos", "perfil", "cauda", "boca_C", "boca_E", "boca_D"): render(*CAMS[n], f"v3_{n}.png")
HIGH.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_Sombrio_LOW.blend"))   # salvo com as bocas FECHADAS
print("CERBERO_V3_OK", flush=True)
# boca aberta 26 graus: so para revisao (sem rig); mandibula = abaixo da linha dos labios, a frente da comissura
ANG = math.radians(arg("abre", 26))
def abrir(o, pecas=False):
    am = o.data.attributes.get("mand") if pecas else None; acb = o.data.attributes.get("cabeca") if pecas else None
    for v in o.data.vertices:
        if pecas:
            if am.data[v.index].value < 0.5: continue
            c = CB[ORDEM[acb.data[v.index].value]]; w = 1.0
        else:
            c = min(CB.values(), key=lambda c_: (v.co - c_.T).length); a, l, h = c.loc(v.co)
            if abs(l) > c.HW + 0.035 or not (c.lip(a) - 0.065 < h < c.lip(a) + 0.0005): continue
            w = suave((a - (c.CANTO - 0.035)) / 0.035) * suave((h - (c.lip(a) - 0.065)) / 0.02)
            if w <= 0: continue
        piv = c.P(c.CANTO - 0.012, 0, c.lip(c.CANTO) + 0.004)
        v.co = piv + Matrix.Rotation(-ANG * w, 3, c.s) @ (v.co - piv)
for o in (CAB, low): abrir(o)
abrir(BOCA, True)
for k in ORDEM: render(*CAMS["boca_" + k], f"v3_boca_{k}_aberta.png")
print("CERBERO_V3_RENDER_OK", flush=True)                 # a pose aberta NAO e salva
