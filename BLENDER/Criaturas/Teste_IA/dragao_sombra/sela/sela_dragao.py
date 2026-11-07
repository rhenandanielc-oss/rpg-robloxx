"""Sela + arreio dos Dragoes (05/11, usuario: "Aprovar e modelar"; proposta DOCS/equipamentos/sela-dragoes.md).
Base comum sobre o esqueleto do Silverwing (Sombrio v10 / Glacial usam a mesma malha-base; o Silverwing de Fogo tem corpo
proprio e vai precisar de ajuste). Tudo por script, moldado ao corpo por raios contra a ILHA PRINCIPAL do corpo (espinhos e
chifres sao ilhas separadas e ficam de fora).
Pecas: assento com aba lateral (moldado ao dorso), arcao (santantonio na frente + patilha atras), peitoral em V ate o peito,
barrigueira (volta inteira), loros + estribos, 2 alcas de apoio no santantonio, adorno regional na frente.
Posicao: o cavaleiro do jogo fica sobre o osso spine_1 (Coluna2) + 1,8 stud (ConfigMontaria/atributo AssentoAcima);
1 unidade aqui ~ 17,5 studs.
Pesos (v2): os do ponto exato da pele embaixo de cada vertice (baricentrico no triangulo mais proximo), para a sela seguir
a pele em todas as poses.
v2 (05/11, usuario: "ajuste melhor no corpo do dragao"; QA da v1 achou 8-20% do couro e 20-44% do metal dentro do corpo):
face INTERNA de assento e cintas a 1 mm da pele (grupo _interno) e espessura so para fora; argolas, fivelas e estribos
deitados no plano da pele; arcao sobre a borda externa real do assento. v1 guardada em sela_dragao_v1.py. Materiais por slot (couro, metal,
madeira, adorno); as cores do tema vem de TEMA (Sombra/Fogo/Gelo) so para a revisao.
Uso: blender -b rig/SB_Dragao_M2M_v10_boca.blend -P sela/sela_dragao.py -- [saida.blend]"""
import bpy, bmesh, math, sys, os
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAIDA = os.path.abspath(a[0]) if a else os.path.join(AQUI, "rig", "SB_Dragao_M2M_v11_sela.blend")
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for b_ in A.pose.bones: b_.matrix_basis.identity()
if A.animation_data: A.animation_data.action = None
bpy.context.view_layer.update()
# ---- (r2) espinhos do dorso que atravessariam a sela: removidos so na area dela ----
S1_ = A.matrix_world @ A.data.bones["spine_1"].head_local
bmS = bmesh.new(); bmS.from_mesh(M.data); bmS.verts.ensure_lookup_table(); mw = M.matrix_world
visS, ilhasS = set(), []
for v in bmS.verts:
    if v.index in visS: continue
    pilha, ilha = [v], []
    while pilha:
        x = pilha.pop()
        if x.index in visS: continue
        visS.add(x.index); ilha.append(x)
        for e in x.link_edges: pilha.append(e.other_vert(x))
    ilhasS.append(ilha)
maiorS = max(ilhasS, key=len); tira = []
for il in ilhasS:
    if il is maiorS or len(il) > 400: continue
    c = sum(((mw @ v.co) for v in il), V()) / len(il)
    if abs(c.x) < 0.07 and abs(c.y - S1_.y) < 0.125 and c.z > S1_.z: tira += il
bmesh.ops.delete(bmS, geom=tira, context="VERTS"); bmS.to_mesh(M.data); bmS.free(); M.data.update()
print("SELA espinhos do dorso removidos (verts)", len(tira))
# ---- ilha principal do corpo (sem espinhos/chifres/dentes) ----
bm = bmesh.new(); bm.from_mesh(M.data); bm.verts.ensure_lookup_table(); bm.transform(M.matrix_world)
vis = set(); maior = []
for v in bm.verts:
    if v.index in vis: continue
    pilha, ilha = [v], []
    while pilha:
        x = pilha.pop()
        if x.index in vis: continue
        vis.add(x.index); ilha.append(x.index)
        for e in x.link_edges: pilha.append(e.other_vert(x))
    if len(ilha) > len(maior): maior = ilha
manter = set(maior)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in manter], context="VERTS")
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.verts.index_update(); bm.faces.index_update()               # indices locais (o delete deixa os antigos)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
BVH = BVHTree.FromBMesh(bm); TRI = [[v.index for v in f.verts] for f in bm.faces]
corpoCo = [v.co.copy() for v in bm.verts]; idxOrig = sorted(manter)
bm.free()
print("SELA corpo principal", len(corpoCo), "verts")
pb = lambda n: A.matrix_world @ A.data.bones[n].head_local
S1 = pb("spine_1")
ESTUD = 17.5
Y0 = S1.y                                    # centro do assento (o cavaleiro fica aqui)
HRP = V((0, Y0, S1.z + 1.8 / ESTUD))
def eixoZ(y):                                # centro da secao do corpo na altura y (meio entre dorso e ventre)
    cima = BVH.ray_cast(V((0, y, 2)), V((0, 0, -1)))[0]
    baixo = BVH.ray_cast(V((0, y, -1)), V((0, 0, 1)))[0]
    return (cima.z + baixo.z) / 2 if cima and baixo else S1.z - 0.02
def sup(th, y, off=0.0):                     # ponto da pele no angulo th (0 = topo, + = esquerda/x+) na altura y, + afastamento
    zc = eixoZ(y); d = V((math.sin(th), 0, math.cos(th)))
    o = V((0, y, zc)) + d * 1.5
    h, n, _, _ = BVH.ray_cast(o, -d)
    if h and (h - V((0, y, zc))).length > RMAX:               # bateu numa pata/asa: tenta de dentro para fora
        h2, n2, _, _ = BVH.ray_cast(V((0, y, zc)) + d * 0.02, d)
        if h2: h, n = h2, n2
    if not h: return V((0, y, zc)) + d * 0.1, d
    return h + n * off, n
RMAX = 0.26
def malha(nome, verts, faces, mat):
    me = bpy.data.meshes.new(nome); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    o = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(o)
    o["mat"] = mat; return o
def solidificar(o, esp, desloc=1.0):
    m = o.modifiers.new("s", "SOLIDIFY"); m.thickness = esp; m.offset = desloc; m.use_even_offset = True
    bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.modifier_apply(modifier="s"); o.select_set(False)
def tubo(nome, pts, r, mat, segs=8, fechado=False):
    vs, fs = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        t = (pts[(i + 1) % n] if fechado else pts[min(i + 1, n - 1)]) - (pts[(i - 1) % n] if fechado else pts[max(i - 1, 0)])
        t.normalize(); u = t.orthogonal().normalized(); w = t.cross(u)
        for k in range(segs):
            ang = 2 * math.pi * k / segs; vs.append(p + (u * math.cos(ang) + w * math.sin(ang)) * r)
    for i in range(n if fechado else n - 1):
        j = (i + 1) % n
        for k in range(segs):
            fs.append((i * segs + k, i * segs + (k + 1) % segs, j * segs + (k + 1) % segs, j * segs + k))
    if not fechado:
        fs.append(tuple(range(segs))[::-1]); fs.append(tuple(range((n - 1) * segs, n * segs)))
    return malha(nome, vs, fs, mat)
def acima_pele(p, folga):                    # empurra para fora da pele se o suavizado afundou
    q = BVH.find_nearest(p)
    if q[0] is None: return p
    d = p - q[0]
    if d.dot(q[1]) < folga: return q[0] + q[1] * folga
    return p
def normal_pele(p):
    q = BVH.find_nearest(p); return q[1] if q[0] is not None else V((0, 0, 1))
FOLGA = 0.0018                                    # face interna a 1,8 mm da pele (~0,03 stud; com K_ASA 0,5 nao entra nas poses)
def casca(nome, dentro, fora, nu, nv, mat):
    """Solido entre a grade interna e a externa (nu x nv), com paredes nas bordas; grupo _interno = face de baixo."""
    vs = list(dentro) + list(fora); N = len(dentro); fs = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            a_, b_ = j * nu + i, j * nu + i + 1; c_, d_ = (j + 1) * nu + i + 1, (j + 1) * nu + i
            fs.append((N + a_, N + b_, N + c_, N + d_)); fs.append((d_, c_, b_, a_))
    for i in range(nu - 1):
        for j in (0, nv - 1):
            a_, b_ = j * nu + i, j * nu + i + 1
            fs.append((a_, b_, N + b_, N + a_))
    for j in range(nv - 1):
        for i in (0, nu - 1):
            a_, d_ = j * nu + i, (j + 1) * nu + i
            fs.append((d_, a_, N + a_, N + d_))
    o = malha(nome, vs, fs, mat)
    g = o.vertex_groups.new(name="_interno"); g.add(list(range(N)), 1.0, "REPLACE")
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT"); o.select_set(False)
    return o
def fita(nome, pts_n, larg, esp, mat):           # cinta: face interna a 1 mm da pele, espessura para fora
    pts = [p for p, n in pts_n]
    for _ in range(4):                            # cinta esticada: suaviza o caminho (sem afundar)
        pts = [pts[0]] + [acima_pele((pts[i - 1] + pts[i] * 2 + pts[i + 1]) / 4, FOLGA) for i in range(1, len(pts) - 1)] + [pts[-1]]
    pts = [acima_pele(p, FOLGA) for p in pts]
    dentro, fora = [], []
    for i, p in enumerate(pts):
        n = normal_pele(p); t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        lado = t.cross(n).normalized()
        for s_ in (0.5, -0.5):
            q = acima_pele(p + lado * larg * s_, FOLGA); dentro.append(q); fora.append(q + normal_pele(q) * esp)
    return casca(nome, dentro, fora, 2, len(pts), mat)
def plano_pele(p):                                # base do plano tangente da pele (n, t ao longo do corpo, u lateral)
    n = normal_pele(p); t = V((0, 1, 0)); t = (t - n * t.dot(n)).normalized(); return n, t, n.cross(t)
pecas = []
# ---- 1) assento + aba: grade (angulo x comprimento), moldada a pele ----
L = 0.095; TH_S, TH_A = math.radians(34), math.radians(64)       # meia largura do assento / da aba (angulo)
NU, NV = 25, 19
V_PICO, ALT_SANT, ALT_PAT = 0.78, 0.024, 0.032                  # (v3) pico do arcao e alturas (antes 0,030/0,042 na borda)
grade, alt = [], []
for j in range(NV):
    v = -1 + 2 * j / (NV - 1); y = Y0 + v * L                     # v = -1 frente (cabeca em -y), +1 tras
    for i in range(NU):
        u = -1 + 2 * i / (NU - 1); th = u * TH_A
        cen = max(0.0, 1 - (abs(th) / TH_S) ** 2)                   # 1 no meio do assento, 0 fora dele
        acolch = 0.010 * cen ** 0.6 * (1 - 0.35 * v * v)            # acolchoado do assento
        # (v3, usuario: "a sela nao esta assentada no corpo") santantonio e patilha sobem em curva ATE O PICO (|v| = V_PICO)
        # e descem arredondados de volta a pele na borda: sem as paredes retas de 3-4 cm que davam ar de caixa por cima
        arco = 0.0
        if abs(v) > 0.45:
            t = (abs(v) - 0.45) / 0.55; tp = (V_PICO - 0.45) / 0.55
            g = math.sin(math.pi / 2 * t / tp) if t < tp else math.cos(math.pi / 2 * (t - tp) / (1 - tp)) ** 0.8
            arco = (ALT_SANT if v < 0 else ALT_PAT) * g * cen
        borda_ = min(1.0, (1 - abs(v)) / 0.10 + 0.25, (1 - abs(u)) / 0.10 + 0.25)   # couro afina nas bordas
        recorte = 1 - 0.18 * (abs(u) ** 3) * (abs(v) ** 2)          # cantos da aba arredondados
        p, n = sup(th * recorte, y, 0.0)
        grade.append(p); alt.append(0.0022 + (0.0018 + acolch) * borda_ + arco)
for _ in range(6):                           # suaviza os calombos das escamas (couro esticado), sem afundar na pele
    nova = list(grade)
    for j in range(1, NV - 1):
        for i in range(1, NU - 1):
            k = j * NU + i
            nova[k] = grade[k] * 0.4 + (grade[k - 1] + grade[k + 1] + grade[k - NU] + grade[k + NU]) * 0.15
    grade = [acima_pele(p, FOLGA) for p in nova]
grade = [acima_pele(p, FOLGA) for p in grade]
nrm = [normal_pele(p) for p in grade]
for _ in range(3):                           # normais suaves para a espessura nao ondular
    nn = list(nrm)
    for j in range(1, NV - 1):
        for i in range(1, NU - 1):
            k = j * NU + i; nn[k] = (nrm[k] * 2 + nrm[k - 1] + nrm[k + 1] + nrm[k - NU] + nrm[k + NU]).normalized()
    nrm = nn
fora = [grade[k] + nrm[k] * alt[k] for k in range(len(grade))]
assento = casca("Sela_Assento", grade, fora, NU, NV, "couro")
pecas.append(assento)
# ---- 2) arcao: santantonio e patilha como tubos que contornam a borda ----
def borda(j, r):                              # tubo do arcao assentado na borda EXTERNA real do assento (linha j da grade)
    pts = []
    for i in range(NU):
        th = (-1 + 2 * i / (NU - 1)) * TH_A
        if abs(th) <= TH_S * 1.08:
            k = j * NU + i; pts.append(fora[k] + nrm[k] * r * 0.55)
    return pts
JP = round((1 - V_PICO) / 2 * (NV - 1))                        # (v3) arcao sobre a linha do pico, nao na borda
SANT = borda(JP, 0.0065); PAT = borda(NV - 1 - JP, 0.0075)
pecas.append(tubo("Sela_Santantonio", SANT, 0.0065, "madeira", 10))
pecas.append(tubo("Sela_Patilha", PAT, 0.0075, "madeira", 10))
# ---- 3) alcas de apoio no santantonio (pegadores, no lugar de redeas) ----
for s in (1, -1):
    m_ = len(SANT) // 2; a0 = SANT[m_ + s * max(1, m_ // 3)]; a1 = SANT[m_ + s * max(2, m_ - 1)]   # pontas presas no santantonio
    pts = [a0.lerp(a1, k / 10) + V((0, -0.014 * math.sin(math.pi * k / 10), 0.018 * math.sin(math.pi * k / 10))) for k in range(11)]
    pecas.append(tubo("Sela_Alca_" + ("E" if s > 0 else "D"), pts, 0.0035, "couro", 8))
# ---- 4) barrigueira: volta inteira atras das patas dianteiras ----
YB = Y0 + L * 0.35
volta = [sup(2 * math.pi * k / 48 - math.pi, YB, 0.004) for k in range(49)]
pecas.append(fita("Sela_Barrigueira", volta, 0.024, 0.003, "couro"))
# ---- 5) peitoral em V: da frente da aba ate o meio do peito, na frente das patas ----
YP = pb("spine_3").y + 0.005                                       # (r2) base do pescoco, a frente das patas e garras
for s in (1, -1):
    ptsn = []
    for k in range(17):
        t = k / 16
        th = s * (TH_A * 0.85 + (math.radians(176) - TH_A * 0.85) * t ** 0.8)   # desce pela lateral ate a frente do peito
        y = (Y0 - L) + (YP - (Y0 - L)) * math.sin(t * math.pi / 2)
        ptsn.append(sup(th, y, 0.004))
    pecas.append(fita("Sela_Peitoral_" + ("E" if s > 0 else "D"), ptsn, 0.018, 0.003, "couro"))
cp0 = sup(math.pi, YP, 0.0)[0]; n_, t_, u_ = plano_pele(cp0)           # argola onde as tiras se encontram, deitada na pele
cp = cp0 + n_ * (FOLGA + 0.003 + 0.0028 + 0.0005)
pecas.append(tubo("Sela_ArgolaPeito", [cp + (t_ * math.cos(2 * math.pi * k / 16) + u_ * math.sin(2 * math.pi * k / 16)) * 0.012 for k in range(16)], 0.0028, "metal", 6, True))
# ---- 6) loros + estribos (dos dois lados) ----
for s in (1, -1):
    topo = sup(s * TH_A * 0.75, Y0 + 0.01, 0.006); ptsn = [sup(s * (TH_A * 0.75 + math.radians(18) * k / 6), Y0 + 0.01, 0.006) for k in range(7)]
    pecas.append(fita("Sela_Loro_" + ("E" if s > 0 else "D"), ptsn, 0.010, 0.0025, "couro"))
    pe = ptsn[-1][0]; n_, t_, u_ = plano_pele(pe)
    baixo = V((0, 0, -1)); baixo = (baixo - n_ * baixo.dot(n_)).normalized()        # descendo pela lateral, rente a pele
    c = pe + baixo * 0.022 + n_ * (FOLGA + 0.0025 + 0.003 + 0.004)
    anel = [c + baixo * math.cos(2 * math.pi * k / 18) * 0.020 + t_ * math.sin(2 * math.pi * k / 18) * 0.014 for k in range(18)]
    pecas.append(tubo("Sela_Estribo_" + ("E" if s > 0 else "D"), anel, 0.0030, "metal", 6, True))
# ---- 7) fivelas de metal onde as cintas encontram a aba ----
for s in (1, -1):
    for y_, th_ in ((YB, s * TH_A * 0.95), (Y0 - L * 0.95, s * TH_A * 0.85)):
        p0 = sup(th_, y_, 0.0)[0]; n_, t_, u_ = plano_pele(p0); p = p0 + n_ * (FOLGA + 0.003 + 0.0022 + 0.0006)
        q = [p + u_ * 0.010 * math.cos(2 * math.pi * k / 4 + math.pi / 4) * 1.41 + t_ * 0.010 * math.sin(2 * math.pi * k / 4 + math.pi / 4) * 1.41 for k in range(4)]
        pecas.append(tubo("Sela_Fivela", q, 0.0022, "metal", 5, True))
# ---- 8) adorno regional na frente do santantonio (losango/cristal) ----
fr = SANT[len(SANT) // 2] + V((0, -0.010, 0.006))
r_, h_ = 0.010, 0.016
vs = [fr + V((0, 0, h_)), fr + V((0, 0, -h_ * 0.7)), fr + V((r_, 0, 0)), fr + V((-r_, 0, 0)), fr + V((0, -r_ * 0.7, 0)), fr + V((0, r_ * 0.7, 0))]
fs = [(0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2), (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5)]
pecas.append(malha("Sela_Adorno", vs, fs, "adorno"))
# ---- juntar, materiais por slot, pesos copiados do corpo ----
MATS = ["couro", "metal", "madeira", "adorno"]
for nome in MATS:
    if nome not in bpy.data.materials:
        mt = bpy.data.materials.new("M_Sela_" + nome); mt.use_nodes = True
for o in pecas:
    o.data.materials.append(bpy.data.materials["M_Sela_" + o["mat"]])
bpy.ops.object.select_all(action="DESELECT")
for o in pecas: o.select_set(True)
bpy.context.view_layer.objects.active = pecas[0]; bpy.ops.object.join()
sela = bpy.context.view_layer.objects.active; sela.name = "Silverwing_Sela"; sela.data.name = "Silverwing_Sela"
for p_ in sela.data.polygons: p_.use_smooth = True
bpy.ops.object.shade_auto_smooth(angle=math.radians(50))
print("SELA materiais", [m.name for m in sela.data.materials])   # o join junta os slots iguais e remapeia os indices
# ---- pesos ----
kd = KDTree(len(corpoCo))
for i, co in enumerate(corpoCo): kd.insert(co, i)
kd.balance()
mvg = {g.index: g.name for g in M.vertex_groups}
pesoV = {}
for i_loc, i_orig in enumerate(idxOrig):
    pesoV[i_loc] = {mvg[g.group]: g.weight for g in M.data.vertices[i_orig].groups if g.weight > 0.001}
for g in list(sela.vertex_groups):
    if g.name != "_interno": sela.vertex_groups.remove(g)
grupos = {}
from mathutils.geometry import area_tri
K_ASA = float(os.environ.get("K_ASA", "0.5"))   # 1 = segue a pele (asa puxa a aba), 0 = so tronco (pele se afasta)
for v in sela.data.vertices:
    acc = {}
    q, n_, fi, _ = BVH.find_nearest(sela.matrix_world @ v.co)
    t3 = TRI[fi]; a3, b3, c3 = (corpoCo[t3[0]], corpoCo[t3[1]], corpoCo[t3[2]])
    tot = area_tri(a3, b3, c3) or 1e-12
    bc = (area_tri(q, b3, c3) / tot, area_tri(a3, q, c3) / tot, area_tri(a3, b3, q) / tot)
    for idx, wb in zip(t3, bc):
        for gn, gw in pesoV[idx].items():
            if gn.startswith(('wing_', 'shoulder_', 'front_leg', 'collar_')): gw *= K_ASA   # (v2) sela segue a asa so em parte
            acc[gn] = acc.get(gn, 0) + gw * wb
    s_ = sum(acc.values()) or 1
    for gn, gw in acc.items():
        if gw / s_ < 0.02: continue
        g = grupos.get(gn) or sela.vertex_groups.new(name=gn); grupos[gn] = g
        g.add([v.index], gw / s_, "REPLACE")
sela.parent = A; sela.matrix_parent_inverse = A.matrix_world.inverted()
mod = sela.modifiers.new("Armature", "ARMATURE"); mod.object = A
n = sum(len(p.vertices) - 2 for p in sela.data.polygons)
print("SELA tris", n, "verts", len(sela.data.vertices), "grupos", len(grupos), "HRP", tuple(round(c, 3) for c in HRP))
sela["HRP"] = list(HRP)
bpy.ops.wm.save_as_mainfile(filepath=SAIDA)
print("SELA_OK", SAIDA)
