"""E3 passo 3: mandibula articulavel e interior da boca na copia de trabalho (a E2 v11 nao e alterada).
- Abre os labios: corta a pele no plano da linha da boca (comissura -> frente, medido na v11) so entre as comissuras e
  separa as arestas do corte (fenda: labio superior e inferior).
- Mandibula: grupo de vertices "Mandibula" (1 abaixo da fenda, com transicao suave atras das comissuras e na garganta/
  barba) + "Cabeca"; armature de teste com 2 ossos (Cabeca, Mandibula com pivo na articulacao temporo-mandibular).
- Interior FECHADO e ligado aos labios (mesma malha, material M_Leao_Boca): palato a partir do labio superior,
  assoalho a partir do inferior, paredes laterais que esticam atras das comissuras, garganta compartilhada (peso 0,5).
- Lingua e dentes (incisivos, caninos, pre-molares) em objetos proprios, presos a Cabeca/Mandibula.
Uso: blender -b <e3_t2.blend> -P e3_05_boca.py -- <saida.blend>"""
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix
A = sys.argv[sys.argv.index("--") + 1:]
V = Vector
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]; me = ob.data
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
# ------------------------------------------------------------------ medidas da boca (na v11, em studs)
COMIS = V((0, -13.96, 12.23)); FRENTE = V((0, -15.33, 12.43))
d = (FRENTE - COMIS); NUP = V((0, -d.z, d.y)).normalized()
if NUP.z < 0: NUP = -NUP                                   # normal do plano da boca, para cima
def sd(p): return (p - FRENTE).dot(NUP)                    # distancia ao plano (+ = acima)
Y_COMIS = COMIS.y
def z_plano(y): return FRENTE.z + (y - FRENTE.y) * (d.z / d.y)
H = V((0, -12.75, z_plano(-12.75) + 0.30))                 # articulacao temporo-mandibular (pivo)
QUEIXO = V((0, -15.15, 11.95))
print("PLANO normal", tuple(round(c, 3) for c in NUP), "pivo", tuple(round(c, 3) for c in H))
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
# ------------------------------------------------------------------ 1. corte da fenda
def na_boca(c): return c.y < Y_COMIS + 0.02 and abs(c.x) < 1.9 and abs(sd(c)) < 0.35 and c.z > 11.4
reg = [f for f in bm.faces if na_boca(f.calc_center_median())]
geom = list({v for f in reg for v in f.verts}) + list({e for f in reg for e in f.edges}) + reg
cut = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=FRENTE, plane_no=NUP, dist=1e-5)["geom_cut"]
cut_e = [e for e in cut if isinstance(e, bmesh.types.BMEdge)]
# so as arestas na superficie externa do focinho, entre as comissuras
cut_e = [e for e in cut_e if all(v.co.y < Y_COMIS + 0.02 for v in e.verts)]
bmesh.ops.split_edges(bm, edges=cut_e)
bm.edges.ensure_lookup_table(); bm.verts.ensure_lookup_table()
fenda = [e for e in bm.edges if e.is_boundary and all(v.co.y < Y_COMIS + 0.05 and abs(sd(v.co)) < 0.02 for v in e.verts)]
print("FENDA arestas", len(fenda))
# separar em labio superior / inferior pelo lado das faces
def lado(e): return 1 if sd(e.link_faces[0].calc_center_median()) > 0 else -1
def cadeia(edges):
    """ordena um conjunto de arestas em caminho (do extremo esquerdo X- ao direito X+)"""
    adj = {}
    for e in edges:
        a, b = e.verts; adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    pontas = [v for v, l in adj.items() if len(l) == 1]
    if len(pontas) < 2: pontas = sorted(adj, key=lambda v: v.co.x)[:1] + sorted(adj, key=lambda v: -v.co.x)[:1]
    ini = min(pontas, key=lambda v: v.co.x); cam = [ini]; vis = {ini}
    while True:
        prox = [w for w in adj[cam[-1]] if w not in vis]
        if not prox: break
        cam.append(prox[0]); vis.add(prox[0])
    return cam
U = cadeia([e for e in fenda if lado(e) > 0]); D = cadeia([e for e in fenda if lado(e) < 0])
print("LABIOS sup", len(U), "inf", len(D), "extremos", tuple(round(c, 2) for c in U[0].co), tuple(round(c, 2) for c in U[-1].co))
# ------------------------------------------------------------------ 2. interior fechado (palato / assoalho / garganta)
def reamostrar(cam, M):
    pts = [v.co.copy() for v in cam]; L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (b - a).length)
    out = []
    for k in range(M):
        alvo = L[-1] * k / (M - 1)
        for i in range(len(pts) - 1):
            if L[i + 1] >= alvo: t = (alvo - L[i]) / max(L[i + 1] - L[i], 1e-9); out.append(lerp(pts[i], pts[i + 1], t)); break
    return out
M, KP = 23, 10
Yg = -12.95; G = [V((lerp(-0.55, 0.55, j / (M - 1)), Yg, z_plano(Yg))) for j in range(M)]
nrm = {}
bm.normal_update()
mat_boca = len(me.materials)
cor = {}                                                   # vertice -> cor da boca
peso_fixo = {}                                             # vertice -> peso Mandibula
gv = [bm.verts.new(p) for p in G]
for v in gv: peso_fixo[v] = 0.5; cor[v] = (52, 16, 20)
def superficie(cam, sinal, alt):
    """linhas do palato (sinal +1) ou assoalho (-1): da borda do labio ate a garganta"""
    base = reamostrar(cam, M)
    # "para dentro" = inverso da normal da pele no labio, projetada no plano da boca (lateral nos lados, para tras na frente)
    nb = []
    for p in base:
        v = min(cam, key=lambda x: (x.co - p).length_squared)
        n = sum((f.normal for f in v.link_faces), V()); n = n - NUP * n.dot(NUP)
        nb.append(-n.normalized() if n.length > 1e-6 else V((0, 1, 0)))
    linhas = []
    for r in range(1, KP):
        t = r / KP; lin = []
        for j in range(M):
            s = j / (M - 1)
            fundo = (0.24 if sinal > 0 else 0.36) if r == 1 else 0.10 * (1 - t)   # 1a fileira bem atras do labio (o inferior e recolhido)
            dentro = base[j] + nb[j] * fundo
            p = lerp(dentro, G[j], t ** 0.9) if r > 1 else dentro
            abob = (0.02 if sinal > 0 else 0.07) if r == 1 else alt * math.sin(math.pi * t) ** 0.7 * math.sin(math.pi * s) ** 0.5 + 0.03
            if j in (0, M - 1): abob = 0.02
            p = p + NUP * (sinal * abob)
            v = bm.verts.new(p); lin.append(v)
            peso_fixo[v] = 0.0 if sinal > 0 else 1.0
            cor[v] = (58, 34, 31) if r == 1 else (168, 74, 80) if r == 2 else tuple(int(lerp(c0, c1, t)) for c0, c1 in zip((118, 38, 44), (55, 17, 21)))   # 1a fileira = margem escura do labio; 2a = gengiva
            if r <= 2 and j in (0, 1, M - 2, M - 1): cor[v] = (58, 34, 31)       # junto as comissuras: cor da linha da boca
        linhas.append(lin)
    return linhas
def zipper(a, b, inverter):
    """faces entre duas polilinhas de contagens diferentes (mesmos extremos parametricos)"""
    i = j = 0; fs = []
    while i < len(a) - 1 or j < len(b) - 1:
        ta = (i + 1) / (len(a) - 1) if i < len(a) - 1 else 9; tb = (j + 1) / (len(b) - 1) if j < len(b) - 1 else 9
        if ta <= tb: tri = (a[i], a[i + 1], b[j]); i += 1
        else: tri = (a[i], b[j + 1], b[j]); j += 1
        if len(set(tri)) == 3:
            try: f = bm.faces.new(tri[::-1] if inverter else tri); f.material_index = mat_boca; fs.append(f)
            except ValueError: pass
    return fs
def grade(l1, l2, inverter):
    for j in range(M - 1):
        q = (l1[j], l1[j + 1], l2[j + 1], l2[j])
        try: f = bm.faces.new(q[::-1] if inverter else q); f.material_index = mat_boca
        except ValueError: pass
pal = superficie(U, +1, 0.36); ass = superficie(D, -1, 0.28)
for linhas, cam, inv in ((pal, U, False), (ass, D, True)):
    zipper(cam, linhas[0], inv)
    for a, b in zip(linhas, linhas[1:]): grade(a, b, inv)
    grade(linhas[-1], gv, inv)
# paredes laterais (bochechas internas) entre palato e assoalho, dos dois lados
for j in (0, M - 1):
    colp = [U[0] if j == 0 else U[-1]] + [l[j] for l in pal] + [gv[j]]
    cola = [D[0] if j == 0 else D[-1]] + [l[j] for l in ass] + [gv[j]]
    for k in range(len(colp) - 1):
        q = [colp[k], colp[k + 1], cola[k + 1], cola[k]]
        q = [x for i_, x in enumerate(q) if x not in q[:i_]]
        if len(q) >= 3:
            try: f = bm.faces.new(q if j == 0 else q[::-1]); f.material_index = mat_boca
            except ValueError: pass
bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f.material_index == mat_boca])
for f in bm.faces:
    if f.material_index == mat_boca: f.smooth = True          # interior com sombreamento suave
for e in bm.edges:                                        # pele x interior: aresta dura (a normal do labio nao se inclina)
    if len({f.material_index for f in e.link_faces}) > 1: e.smooth = False
# ------------------------------------------------------------------ 3. pesos da mandibula
bm.verts.ensure_lookup_table()
w = {}
for v in bm.verts:
    if v in peso_fixo: w[v] = peso_fixo[v]; continue
    p = v.co
    if not (p.y < -11.8 and p.z > 9.6 and abs(p.x) < 2.4): w[v] = 0.0; continue
    s = sum(sd(f.calc_center_median()) for f in v.link_faces) / max(len(v.link_faces), 1)
    if p.y < Y_COMIS:                                        # na frente das comissuras: lado da fenda decide
        base = 1.0 if s < 0 else 0.0
    else:                                                   # atras: bochecha que estica
        base = suave(-s / 0.45) * suave((-12.5 - p.y) / (-12.5 - Y_COMIS))
    meia = lerp(1.05, 0.70, suave((Y_COMIS - p.y) / 1.3))  # meia-largura anatomica da mandibula (estreita na frente)
    base *= suave((meia + 0.55 - abs(p.x)) / 0.55)          # bochechas e juba lateral: so acompanham parcialmente
    base *= 0.35 + 0.65 * suave((p.z - 11.2) / 0.7)         # barba sob o queixo: acompanha 35-100%
    base *= suave((p.z - 9.9) / 0.9)
    w[v] = base
# suaviza so nas zonas de transicao (atras da comissura e garganta), sem cruzar a fenda (topologia separada)
livre = [v for v in bm.verts if v not in peso_fixo and (v.co.y > Y_COMIS - 0.25 or v.co.z < 11.2) and v.co.y < -11.8]
for _ in range(6):
    nw = {}
    for v in livre:
        viz = [e.other_vert(v) for e in v.link_edges]
        nw[v] = 0.5 * w[v] + 0.5 * sum(w[x] for x in viz) / max(len(viz), 1)
    w.update(nw)
# margem escura dos labios (como na referencia) e pele das comissuras que estica: atributo por face para a textura
lab = bm.faces.layers.float.new("labio"); S = set(U) | set(D)
anel1 = {f for v in S for f in v.link_faces if f.material_index != mat_boca}
anel2 = {g for f in anel1 for v in f.verts for g in v.link_faces if g.material_index != mat_boca} - anel1
for f in anel1: f[lab] = 1.0
for f in anel2: f[lab] = 0.30
for f in bm.faces:
    if f.material_index == mat_boca or f in anel1: continue
    c = f.calc_center_median(); ws = [w.get(v, 0) for v in f.verts]
    if Y_COMIS - 0.1 < c.y < Y_COMIS + 0.30 and abs(sd(c)) < 0.15 and 0.10 < sum(ws) / len(ws) < 0.90: f[lab] = max(f[lab], 0.6)
bm.to_mesh(me); me.update()
mats = bpy.data.materials.new("M_Leao_Boca"); mats.use_nodes = True
nt = mats.node_tree; bs = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "CorBoca"; nt.links.new(vc.outputs["Color"], bs.inputs["Base Color"])
bs.inputs["Roughness"].default_value = 0.45; bs.inputs["Specular IOR Level"].default_value = 0.4
me.materials.append(mats)
at = me.color_attributes.new("CorBoca", "BYTE_COLOR", "POINT")
idx_cor = {v.index: c for v, c in cor.items()}
for i in range(len(me.vertices)):
    c = idx_cor.get(i, (45, 30, 28)); at.data[i].color_srgb = (c[0] / 255, c[1] / 255, c[2] / 255, 1)   # vertices do labio: margem escura
ga = ob.vertex_groups.new(name="Mandibula"); gc = ob.vertex_groups.new(name="Cabeca")
wi = {v.index: x for v, x in w.items()}
for i in range(len(me.vertices)):
    x = wi.get(i, 0.0)
    if x > 1e-4: ga.add([i], x, "REPLACE")
    if x < 1 - 1e-4: gc.add([i], 1 - x, "REPLACE")
print("PESOS mandibula>0.5:", sum(1 for x in wi.values() if x > 0.5), "transicao:", sum(1 for x in wi.values() if 0.05 < x < 0.95))
# ------------------------------------------------------------------ 4. lingua e dentes
def objeto(nome, verts, faces, cor_, grupo):
    m = bpy.data.meshes.new(nome); m.from_pydata(verts, [], faces); o = bpy.data.objects.new(nome, m)
    for c in ob.users_collection: c.objects.link(o)
    for p in m.polygons: p.use_smooth = True
    a = m.color_attributes.new("CorBoca", "BYTE_COLOR", "POINT")
    for i in range(len(m.vertices)): a.data[i].color_srgb = (cor_[0] / 255, cor_[1] / 255, cor_[2] / 255, 1)
    m.materials.append(mats); g = o.vertex_groups.new(name=grupo); g.add(list(range(len(m.vertices))), 1.0, "REPLACE")
    return o
def elipsoide(c, ex, ey, ez, nu=20, nv=10):
    vs, fs = [], []
    for i in range(nv + 1):
        th = math.pi * i / nv
        for j in range(nu):
            ph = 2 * math.pi * j / nu
            vs.append(tuple(c + ex * (math.sin(th) * math.cos(ph)) + ey * (math.sin(th) * math.sin(ph)) + ez * math.cos(th)))
    for i in range(nv):
        for j in range(nu):
            a = i * nu + j; b = i * nu + (j + 1) % nu; fs.append((a, b, b + nu, a + nu))
    return vs, fs
eixo_y = (V((0, FRENTE.y, FRENTE.z)) - V((0, Yg, z_plano(Yg)))).normalized()
centro_l = lerp(reamostrar(D, M)[M // 2], G[M // 2], 0.55) - NUP * 0.02
vs, fs = elipsoide(centro_l, V((0.40, 0, 0)), eixo_y * 0.85, NUP * 0.10)
objeto("Leao_Lingua", vs, fs, (196, 98, 104), "Mandibula")
def dentes(cam, sinal, nome, grupo):
    base = reamostrar(cam, 41); vs, fs = [], []
    # (posicao ao longo do arco, comprimento, raio na base)
    tipos = [(0.17, 0.20, 0.075), (0.23, 0.22, 0.08), (0.31, 0.42 if sinal > 0 else 0.36, 0.10)] + \
            [(0.40 + 0.04 * k, 0.17, 0.045) for k in range(6)]
    tipos += [(1 - s_, L_, r_) for s_, L_, r_ in tipos[:3]]
    for s_, L_, r_ in tipos:
        p = base[int(round(s_ * 40))]
        p = p - (p - V((0, p.y, p.z))).normalized() * 0.30 + V((0, 0.30, 0))         # bem para dentro do labio
        raiz = p + NUP * (sinal * (L_ + 0.03)); ponta = raiz - NUP * (sinal * L_) + V((0, 0.02, 0))   # fechada: ponta 0,03 antes do plano
        n0 = len(vs); SEG = 10
        for k in range(SEG):
            a = 2 * math.pi * k / SEG
            vs.append(tuple(raiz + V((math.cos(a) * r_, math.sin(a) * r_ * 0.8, 0))))
        for k in range(SEG):
            a = 2 * math.pi * k / SEG
            vs.append(tuple(lerp(raiz, ponta, 0.6) + V((math.cos(a) * r_ * 0.7, math.sin(a) * r_ * 0.56, 0))))
        vs.append(tuple(ponta)); vs.append(tuple(raiz + NUP * (sinal * 0.04)))
        for k in range(SEG):
            k2 = (k + 1) % SEG
            fs.append((n0 + k, n0 + k2, n0 + SEG + k2, n0 + SEG + k))
            fs.append((n0 + SEG + k, n0 + SEG + k2, n0 + 2 * SEG))
            fs.append((n0 + k2, n0 + k, n0 + 2 * SEG + 1))
    o = objeto(nome, vs, fs, (236, 226, 202), grupo)
    if sinal < 0: o.data.flip_normals()
    return o
dentes(U, +1, "Leao_Dentes_Sup", "Cabeca"); dentes(D, -1, "Leao_Dentes_Inf", "Mandibula")
# ------------------------------------------------------------------ 5. armature de teste
arm_d = bpy.data.armatures.new("Leao_Rig_Teste_Boca"); arm = bpy.data.objects.new("Leao_Rig_Teste_Boca", arm_d)
for c in ob.users_collection: c.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT")
bc = arm_d.edit_bones.new("Cabeca"); bc.head = (0, -11.0, 13.4); bc.tail = (0, -13.4, 14.6)
bmd = arm_d.edit_bones.new("Mandibula"); bmd.head = H; bmd.tail = QUEIXO; bmd.roll = 0; bmd.parent = bc
bpy.ops.object.mode_set(mode="OBJECT")
for o in [ob] + [x for x in bpy.data.objects if x.name.startswith(("Leao_Lingua", "Leao_Dentes"))]:
    mo = o.modifiers.new("Armature", "ARMATURE"); mo.object = arm
print("BOCA_OK")
bpy.ops.wm.save_as_mainfile(filepath=A[0])
