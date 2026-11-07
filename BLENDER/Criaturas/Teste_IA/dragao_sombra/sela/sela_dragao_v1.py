"""Sela + arreio dos Dragoes (05/11, usuario: "Aprovar e modelar"; proposta DOCS/equipamentos/sela-dragoes.md).
Base comum sobre o esqueleto do Silverwing (Sombrio v10 / Glacial usam a mesma malha-base; o Silverwing de Fogo tem corpo
proprio e vai precisar de ajuste). Tudo por script, moldado ao corpo por raios contra a ILHA PRINCIPAL do corpo (espinhos e
chifres sao ilhas separadas e ficam de fora).
Pecas: assento com aba lateral (moldado ao dorso), arcao (santantonio na frente + patilha atras), peitoral em V ate o peito,
barrigueira (volta inteira), loros + estribos, 2 alcas de apoio no santantonio, adorno regional na frente.
Posicao: o cavaleiro do jogo fica sobre o osso spine_1 (Coluna2) + 1,8 stud (ConfigMontaria/atributo AssentoAcima);
1 unidade aqui ~ 17,5 studs.
Pesos: media dos 8 vertices do corpo mais proximos (a sela deforma junto com o dorso). Materiais por slot (couro, metal,
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
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
BVH = BVHTree.FromBMesh(bm)
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
def fita(nome, pts_n, larg, esp, mat):          # tira sobre a pele: pts_n = [(ponto, normal)], largura ao longo da tangente lateral
    for _ in range(4):                            # (r3) cinta esticada: suaviza o caminho e nao deixa entrar na pele
        pts_n = [pts_n[0]] + [(acima_pele((pts_n[i - 1][0] + pts_n[i][0] * 2 + pts_n[i + 1][0]) / 4, 0.004), pts_n[i][1]) for i in range(1, len(pts_n) - 1)] + [pts_n[-1]]
    vs, fs = [], []
    for i, (p, n) in enumerate(pts_n):
        t = (pts_n[min(i + 1, len(pts_n) - 1)][0] - pts_n[max(i - 1, 0)][0]).normalized()
        lado = t.cross(n).normalized()
        vs += [p + lado * larg / 2, p - lado * larg / 2]
    for i in range(len(pts_n) - 1): fs.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    o = malha(nome, vs, fs, mat); solidificar(o, esp, 1.0); return o
pecas = []
# ---- 1) assento + aba: grade (angulo x comprimento), moldada a pele ----
L = 0.095; TH_S, TH_A = math.radians(34), math.radians(64)       # meia largura do assento / da aba (angulo)
NU, NV = 25, 19
grade = []
for j in range(NV):
    v = -1 + 2 * j / (NV - 1); y = Y0 + v * L                     # v = -1 frente (cabeca em -y), +1 tras
    for i in range(NU):
        u = -1 + 2 * i / (NU - 1); th = u * TH_A
        cen = max(0.0, 1 - (abs(th) / TH_S) ** 2)                   # 1 no meio do assento, 0 fora dele
        acolch = 0.010 * cen ** 0.6 * (1 - 0.35 * v * v)            # acolchoado do assento
        arco = 0.0
        if v < -0.55: arco += 0.030 * ((-v - 0.55) / 0.45) ** 1.6 * cen   # santantonio (frente) sobe
        if v > 0.45: arco += 0.042 * ((v - 0.45) / 0.55) ** 1.5 * cen     # patilha (tras) sobe mais
        recorte = 1 - 0.18 * (abs(u) ** 3) * (abs(v) ** 2)          # cantos da aba arredondados
        p, n = sup(th * recorte, y, 0.003 + acolch + arco)
        grade.append(p)
for _ in range(8):                           # (r3) suaviza os calombos das escamas: couro esticado, nao colado em cada escama
    nova = list(grade)
    for j in range(1, NV - 1):
        for i in range(1, NU - 1):
            k = j * NU + i
            nova[k] = grade[k] * 0.4 + (grade[k - 1] + grade[k + 1] + grade[k - NU] + grade[k + NU]) * 0.15
    grade = [acima_pele(p, 0.0035) for p in nova]
fs = [(j * NU + i, j * NU + i + 1, (j + 1) * NU + i + 1, (j + 1) * NU + i) for j in range(NV - 1) for i in range(NU - 1)]
assento = malha("Sela_Assento", grade, fs, "couro"); solidificar(assento, 0.004, -1.0)   # espessura para dentro (nao afasta)
pecas.append(assento)
# ---- 2) arcao: santantonio e patilha como tubos que contornam a borda ----
def borda(v, raio_extra):
    pts = []
    for k in range(13):
        th = (-1 + 2 * k / 12) * TH_S * 1.05; y = Y0 + v * L
        cen = max(0.0, 1 - (abs(th) / TH_S) ** 2)
        arco = 0.030 * cen if v < 0 else 0.042 * cen
        p, n = sup(th, y, 0.003 + 0.010 * cen ** 0.6 * 0.65 + arco + raio_extra)
        pts.append(p)
    return pts
pecas.append(tubo("Sela_Santantonio", borda(-1.0, 0.006), 0.0065, "madeira", 10))
pecas.append(tubo("Sela_Patilha", borda(1.0, 0.006), 0.0075, "madeira", 10))
# ---- 3) alcas de apoio no santantonio (pegadores, no lugar de redeas) ----
for s in (1, -1):
    base = sup(s * 0.32, Y0 - L, 0.0)[0]; p0 = sup(s * 0.32, Y0 - L, 0.040)[0]
    pts = [base + (p0 - base) * 0.2 + V((s * 0.012 * math.sin(math.pi * k / 10), -0.016 * math.sin(math.pi * k / 10), 0.020 * math.sin(math.pi * k / 10))) + V((0, -0.004 * k / 10, 0.025)) for k in range(11)]
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
cp = sup(math.pi, YP, 0.008)[0]                                     # argola onde as duas tiras se encontram
pecas.append(tubo("Sela_ArgolaPeito", [cp + V((0.012 * math.cos(2 * math.pi * k / 16), 0, 0.012 * math.sin(2 * math.pi * k / 16))) for k in range(16)], 0.0028, "metal", 6, True))
# ---- 6) loros + estribos (dos dois lados) ----
for s in (1, -1):
    topo = sup(s * TH_A * 0.75, Y0 + 0.01, 0.006); ptsn = [sup(s * (TH_A * 0.75 + math.radians(18) * k / 6), Y0 + 0.01, 0.006) for k in range(7)]
    pecas.append(fita("Sela_Loro_" + ("E" if s > 0 else "D"), ptsn, 0.010, 0.0025, "couro"))
    pe, ne = ptsn[-1]; fora = (ne + V((0, 0, -0.6))).normalized()
    c = pe + fora * 0.028
    ax = V((0, 1, 0)); u_ = (pe - c).normalized(); w_ = ax.cross(u_)
    anel = [c + (u_ * math.cos(2 * math.pi * k / 18) * 0.020 + w_ * math.sin(2 * math.pi * k / 18) * 0.014) for k in range(18)]
    pecas.append(tubo("Sela_Estribo_" + ("E" if s > 0 else "D"), anel, 0.0030, "metal", 6, True))
# ---- 7) fivelas de metal onde as cintas encontram a aba ----
for s in (1, -1):
    for y_, th_ in ((YB, s * TH_A * 0.95), (Y0 - L * 0.95, s * TH_A * 0.85)):
        p, n = sup(th_, y_, 0.006); t_ = V((0, 1, 0)); u_ = t_.cross(n).normalized()
        q = [p + u_ * 0.010 * math.cos(2 * math.pi * k / 4 + math.pi / 4) * 1.41 + t_ * 0.010 * math.sin(2 * math.pi * k / 4 + math.pi / 4) * 1.41 for k in range(4)]
        pecas.append(tubo("Sela_Fivela", q, 0.0022, "metal", 5, True))
# ---- 8) adorno regional na frente do santantonio (losango/cristal) ----
fr = sup(0.0, Y0 - L * 1.02, 0.040)[0] + V((0, -0.006, 0.004))
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
for g in list(sela.vertex_groups): sela.vertex_groups.remove(g)
grupos = {}
for v in sela.data.vertices:
    acc = {}; tot = 0
    for co, idx, dist in kd.find_n(sela.matrix_world @ v.co, 8):
        w = 1 / (dist + 1e-4); tot += w
        for gn, gw in pesoV[idx].items(): acc[gn] = acc.get(gn, 0) + gw * w
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
