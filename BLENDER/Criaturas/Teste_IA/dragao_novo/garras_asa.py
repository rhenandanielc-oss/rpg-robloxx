"""Garras e detalhes das ASAS do CR_Dragao (usuario 31/10: "garras nas pontas da asa", mais detalhe na asa):
- polegar curvo no punho (garra maior e fina, aponta para frente e curva para baixo);
- as garras das pontas nascem na ponta REAL do dedo na malha (o osso passa da membrana);
- garra na ponta do dedo de ataque (wing_tip) e garras menores nas pontas dos dedos 5/4/3 (borda da membrana);
- 3 espinhos vermelhos escuros no antebraco (borda de ataque).
Pecas rigidas na malha "Silverwing_Detalhes" (mesmo atlas: marfim dos dentes, vermelho escuro das palpebras), cada
uma 100% no osso onde nasce -> nao estica com as animacoes. Coordenadas no repouso do rig (asas abertas).
Uso: blender -b CR_Dragao_M2M.blend -P garras_asa.py   (salva no proprio arquivo; rodar uma vez)"""
import bpy, bmesh, math
from mathutils import Vector as V, Matrix
A = bpy.data.objects["Silverwing_Rig"]; det = bpy.data.objects["Silverwing_Detalhes"]
assert not det.get("garras_asa"), "garras ja adicionadas"
for pb in A.pose.bones: pb.matrix_basis = Matrix.Identity(4)
if A.animation_data: A.animation_data.action = None
B = A.data.bones
UV_MARFIM = (0.52, 0.02, 0.73, 0.48)        # u0, v0 (raiz escura), u1, v1 (ponta clara)
UV_ESPINHO = (0.77, 0.05, 0.98, 0.40)       # vermelho escuro (regiao da palpebra)
bm = bmesh.new(); bm.from_mesh(det.data); uvl = bm.loops.layers.uv.verify()
dl = bm.verts.layers.deform.verify()
gi = {}
def grupo(n):
    if n not in gi: gi[n] = (det.vertex_groups.get(n) or det.vertex_groups.new(name=n)).index
    return gi[n]
n_tris = 0
def garra(base, eixo, curva, L, r, osso, uvbox=UV_MARFIM, aneis=6, seg=8):
    """cone curvo: eixo = direcao inicial, curva = para onde a ponta dobra (gancho)"""
    global n_tris
    eixo = eixo.normalized(); curva = (curva - eixo * curva.dot(eixo)).normalized()
    g = grupo(osso); u0, v0, u1, v1 = uvbox
    def P(t): return base + eixo * (L * t) + curva * (L * 0.38 * t * t)
    aneis_v = []
    for i in range(aneis):
        t = i / aneis; c = P(t); d = (P(min(1, t + 0.02)) - P(max(0, t - 0.02))).normalized()
        a = d.orthogonal().normalized(); b = d.cross(a); ri = r * (1 - t) ** 0.75
        anel = []
        for k in range(seg):
            ang = 2 * math.pi * k / seg; v = bm.verts.new(c + (a * math.cos(ang) + b * math.sin(ang)) * ri)
            v[dl][g] = 1.0; anel.append(v)
        aneis_v.append(anel)
    ponta = bm.verts.new(P(1.0)); ponta[dl][g] = 1.0
    def uv(k, i): return (u0 + (u1 - u0) * k / seg, v0 + (v1 - v0) * i / aneis)
    for i in range(aneis - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            f = bm.faces.new((aneis_v[i][k], aneis_v[i][k2], aneis_v[i + 1][k2], aneis_v[i + 1][k]))
            for lp, (kk, ii) in zip(f.loops, ((k, i), (k + 1, i), (k + 1, i + 1), (k, i + 1))): lp[uvl].uv = uv(kk, ii)
            f.smooth = True; n_tris += 2
    for k in range(seg):
        k2 = (k + 1) % seg
        f = bm.faces.new((aneis_v[-1][k], aneis_v[-1][k2], ponta))
        for lp, x in zip(f.loops, (uv(k, aneis - 1), uv(k + 1, aneis - 1), ((u0 + u1) / 2, v1))): lp[uvl].uv = x
        f.smooth = True; n_tris += 1
    f = bm.faces.new(list(reversed(aneis_v[0])))                     # tampa da raiz (fica dentro da asa)
    for lp in f.loops: lp[uvl].uv = (u0, v0)
    n_tris += seg - 2
def H(n): return B[n].head_local.copy()
def T(n): return B[n].tail_local.copy()
def D(n): return (T(n) - H(n)).normalized()
CORPO = bpy.data.objects["Silverwing"]; NG = {g.index: g.name for g in CORPO.vertex_groups}
def ponta_malha(n):
    """ponta REAL do dedo na malha (o osso passa da membrana): vertice com mais peso no osso mais longe ao longo dele"""
    d = D(n); h = H(n); best = None
    for v in CORPO.data.vertices:
        if any(NG[g.group] == n and g.weight > 0.4 for g in v.groups):
            x = (v.co - h).dot(d)
            if best is None or x > best[0]: best = (x, v.co.copy())
    return best[1] if best else T(n)
for s, sx in (("l", 1), ("r", -1)):
    fr, cima, fora = V((0, -1, 0)), V((0, 0, 1)), V((sx, 0, 0))
    # polegar no punho: para frente/cima/fora, gancho para baixo
    pu = H("wing_3_" + s)
    garra(pu + fr * 0.010 + cima * 0.004, fr * 1.0 + cima * 0.5 + fora * 0.2, -cima + fr * 0.3, 0.095, 0.008, "wing_3_" + s)
    # ponta do dedo de ataque: continua o osso e curva para tras/baixo
    d = D("wing_tip_" + s); pt = ponta_malha("wing_tip_" + s)
    garra(pt - d * 0.010, d, V((0, 1, 0)) - cima * 0.5, 0.065, 0.007, "wing_tip_" + s)
    # pontas dos dedos da membrana (garras menores)
    for k, L in (("5", 0.045), ("4", 0.04), ("3", 0.035)):
        n = "wing_feather_%s_tip_%s" % (k, s); d = D(n)
        garra(ponta_malha(n) - d * 0.006, d, -cima + V((0, 1, 0)) * 0.3, L, 0.005, n)
    # espinhos no antebraco (borda de ataque), vermelho escuro
    for t, L in ((0.3, 0.030), (0.55, 0.036), (0.8, 0.030)):
        p = H("wing_2_" + s).lerp(T("wing_2_" + s), t)
        garra(p + fr * 0.010 + cima * 0.006, cima * 1.0 + fr * 0.6, V((0, 1, 0)), L, 0.008, "wing_2_" + s, UV_ESPINHO, aneis=4, seg=6)
bm.normal_update(); bm.to_mesh(det.data); bm.free()
det["garras_asa"] = 1
print("GARRAS tris novos", n_tris, "DETALHES tris", sum(len(p.vertices) - 2 for p in det.data.polygons))
bpy.ops.wm.save_mainfile()
print("GARRAS_OK")
