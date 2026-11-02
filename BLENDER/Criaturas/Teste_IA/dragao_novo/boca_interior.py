"""Interior da boca do CR_Dragao (Dragao das Montanhas, 02/11): LINGUA e GARGANTA com profundidade + suavizacao dos
pesos dos CANTOS da boca. Idempotente (refaz o objeto Silverwing_Boca a cada execucao; os pesos do canto so sao
suavizados uma vez, marcados na propriedade 'boca_cantos_v1' da malha).
- Silverwing_Boca: malha propria com textura propria (256x256, gerada aqui): lingua (assenta no assoalho medido por
  raios, afina para a ponta, sulco central, ponta levemente erguida; 100% na mandibula) e garganta (tubo que comeca
  na secao real da cavidade atras da articulacao e se fecha para dentro do pescoco, escurecendo ate quase preto;
  metade de cima no maxilar, metade de baixo na mandibula, fundo na cabeca), para a boca aberta nao ser um bloco claro.
- Cantos: vertices do corpo perto da linha da articulacao, nas laterais, com mistura de pesos suavizada
  (mandibula x maxilar/cabeca) para o estiramento se espalhar em vez de rasgar a textura em faixas.
Uso: blender -b CR_Dragao_M2M.blend -P boca_interior.py [-- nosave]"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
SALVAR = "nosave" not in sys.argv
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
A.animation_data.action = None
for b in A.pose.bones: b.matrix_basis.identity()
bpy.context.view_layer.update()
mw = A.matrix_world
def osso(n, tail=False): b = A.data.bones[n]; return mw @ (b.tail_local if tail else b.head_local)
DOBRA = osso("mouth_lower")                                   # articulacao (0,-0.873,0.531)

# ---- medidas reais da cavidade (repouso, boca fechada) por raios a partir do eixo da boca
# revisao 02/11: o interior VISIVEL e a bolsa de Silverwing_Detalhes (mais estreita que a cavidade do corpo)
DET = bpy.data.objects["Silverwing_Detalhes"]
dg = bpy.context.evaluated_depsgraph_get(); ev = DET.evaluated_get(dg); me = ev.to_mesh()
bvh = BVHTree.FromPolygons([DET.matrix_world @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
ev.to_mesh_clear()
def raio(o, d, maxd=0.2):
    h = bvh.ray_cast(o, d, maxd); return h[0]
def secao(y, zc=0.53):
    c = V((0, y, zc))
    chao = raio(c, V((0, 0, -1))); teto = raio(c, V((0, 0, 1)))
    lat = raio(V((0, y, (chao.z + teto.z) / 2 if chao and teto else zc)), V((1, 0, 0)))
    return (chao.z if chao else None), (teto.z if teto else None), (lat.x if lat else None)
for y in (-0.935, -0.95, -1.00, -1.04):
    print("SECAO y=%.3f chao=%s teto=%s lado=%s" % ((y,) + tuple(None if x is None else round(x, 4) for x in secao(y))))

# ---- textura propria: metade esquerda = lingua (rosa-vermelho umido com granulacao), direita = garganta (degrade)
D = os.path.dirname(os.path.abspath(bpy.data.filepath)); TEXP = os.path.join(D, "..", "tex", "boca_interior.png")
os.makedirs(os.path.dirname(TEXP), exist_ok=True)
N = 256; rng = np.random.default_rng(5)
img = np.zeros((N, N, 4)); yy, xx = np.mgrid[0:N, 0:N] / (N - 1)
gran = rng.random((N, N)) * 0.08
lin = np.dstack([0.62 + gran - 0.10 * yy, 0.10 + gran * 0.4, 0.12 + gran * 0.4])        # lingua vermelha (v = base->ponta)
fundo = np.clip(yy, 0, 1)                                                                # garganta: v 0 boca -> 1 fundo
gar = np.dstack([0.30 * (1 - fundo) ** 1.6 + 0.02, 0.06 * (1 - fundo) ** 1.6 + 0.005, 0.06 * (1 - fundo) ** 1.6 + 0.005])
img[..., :3] = np.where((xx < 0.5)[..., None], lin, gar); img[..., 3] = 1
im = bpy.data.images.get("boca_interior.png") or bpy.data.images.new("boca_interior.png", N, N, alpha=True)
if im.size[0] != N: im.scale(N, N)
im.pixels.foreach_set(img.astype(np.float32).ravel())          # Blender: linha 0 = base da imagem (v = 0)
im.filepath_raw = TEXP; im.file_format = "PNG"; im.save()

# ---- malha
velho = bpy.data.objects.get("Silverwing_Boca")
if velho: bpy.data.objects.remove(velho, do_unlink=True)
bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
grupos = {}                                                  # indice do vertice -> {osso: peso}
def vert(p, pesos): v = bm.verts.new(p); grupos[v] = pesos; return v

# LINGUA: aneis elipticos ao longo do assoalho
NL, NR = 12, 12
y0, y1 = -0.931, -1.045                                    # da boca da garganta ate atras dos dentes da frente
aneis = []
for i in range(NL + 1):
    t = i / NL; y = y0 + (y1 - y0) * t
    chao = secao(y)[0] or 0.526
    w = 0.026 * (1 - t) ** 0.7 + 0.006                       # larga atras, afina para a ponta (cabe na bolsa)
    h = 0.0075 * (1 - 0.5 * t)
    zc = chao + h * 0.9 + 0.0008 + 0.0018 * t * t            # assenta no assoalho; ponta levemente erguida
    anel = []
    for j in range(NR):
        a = 2 * math.pi * j / NR
        cx, sz = math.cos(a), math.sin(a)
        z = zc + h * (sz if sz > 0 else sz * 0.6)
        if sz > 0: z -= 0.0018 * math.exp(-(cx / 0.25) ** 2) * (1 - t)      # sulco central
        anel.append(vert(V((w * cx, y, z)), {"mouth_lower": 1.0}))
    aneis.append(anel)
ponta = vert(V((0, y1 - 0.006, sum(v.co.z for v in aneis[-1]) / NR)), {"mouth_lower": 1.0})
def quad(vs, uvs):
    f = bm.faces.new(vs)
    for l, (u, v) in zip(f.loops, uvs): l[uv].uv = (u, v)
    return f
for i in range(NL):
    for j in range(NR):
        a, b, c, d = aneis[i][j], aneis[i][(j + 1) % NR], aneis[i + 1][(j + 1) % NR], aneis[i + 1][j]
        u0, u1 = 0.05 + 0.4 * j / NR, 0.05 + 0.4 * (j + 1) / NR; v0, v1 = i / NL, (i + 1) / NL
        quad([a, b, c, d], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
for j in range(NR):
    f = bm.faces.new([aneis[-1][j], aneis[-1][(j + 1) % NR], ponta])
    for l in f.loops: l[uv].uv = (0.25, 0.98)

# GARGANTA: tubo da secao real da cavidade (atras da articulacao) fechando para dentro do pescoco
NG, NT = 7, 16
YF = -0.926                                                   # parede do fundo da bolsa (aberta abaixo)
ys = [YF - 0.002 + 0.009 * k for k in range(NG, -1, -1)]      # fundo (dentro da cabeca) -> boca da garganta
tubo = []
chao0, teto0, hx = 0.5135, 0.5505, 0.031                     # secao da boca da bolsa junto a parede (medida)
zm = (chao0 + teto0) / 2; hz = (teto0 - chao0) / 2
for k, y in enumerate(ys):
    s = k / NG                                                # 0 fundo .. 1 boca
    esc = 0.35 + 0.65 * s ** 0.8
    anel = []
    for j in range(NT):
        a = 2 * math.pi * j / NT
        z = zm + hz * esc * math.sin(a); x = hx * esc * math.cos(a)
        if s > 0.45:                                          # perto da boca: cima no maxilar, baixo na mandibula
            p = {"mouth_upper": 1.0} if math.sin(a) > 0.15 else {"mouth_lower": 1.0} if math.sin(a) < -0.15 else {"mouth_upper": 0.5, "mouth_lower": 0.5}
        else: p = {"head": 1.0}
        anel.append(vert(V((x, y, z)), p))
    tubo.append(anel)
fundoV = vert(V((0, ys[0] - 0.006, zm)), {"head": 1.0})
for k in range(NG):
    for j in range(NT):
        a, b, c, d = tubo[k][j], tubo[k][(j + 1) % NT], tubo[k + 1][(j + 1) % NT], tubo[k + 1][j]
        v0, v1 = 1 - k / NG, 1 - (k + 1) / NG                 # v: 0 boca -> 1 fundo (escuro)
        quad([d, c, b, a], [(0.55 + 0.4 * j / NT, v1), (0.55 + 0.4 * (j + 1) / NT, v1), (0.55 + 0.4 * (j + 1) / NT, v0), (0.55 + 0.4 * j / NT, v0)])
for j in range(NT):
    f = bm.faces.new([tubo[0][(j + 1) % NT], tubo[0][j], fundoV])
    for l in f.loops: l[uv].uv = (0.75, 0.99)
bm.normal_update()
mesh = bpy.data.meshes.new("Silverwing_Boca"); bm.to_mesh(mesh)
ob = bpy.data.objects.new("Silverwing_Boca", mesh); bpy.context.scene.collection.objects.link(ob)
for v in bm.verts:
    for n, w in grupos[v].items():
        (ob.vertex_groups.get(n) or ob.vertex_groups.new(name=n)).add([v.index], w, "REPLACE")
bm.free()
ob.parent = A; mod = ob.modifiers.new("Armature", "ARMATURE"); mod.object = A
for p in mesh.polygons: p.use_smooth = True
mat = bpy.data.materials.get("M_CR_Boca") or bpy.data.materials.new("M_CR_Boca"); mat.use_nodes = True
nt = mat.node_tree; bs = nt.nodes.get("Principled BSDF")
tx = nt.nodes.get("TexBoca") or nt.nodes.new("ShaderNodeTexImage"); tx.name = "TexBoca"
tx.image = im
nt.links.new(tx.outputs["Color"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.4
mesh.materials.append(mat)
print("BOCA tris", sum(len(p.vertices) - 2 for p in mesh.polygons), "verts", len(mesh.vertices))

# ---- abre a parede clara do fundo da bolsa (faces voltadas para a frente junto de YF): a garganta escura aparece
if not DET.data.get("bolsa_fundo_aberto"):
    bmd = bmesh.new(); bmd.from_mesh(DET.data)
    mwd = DET.matrix_world; R3 = mwd.to_3x3()
    tirar = [f for f in bmd.faces if abs((R3 @ f.normal).normalized().y) > 0.8 and abs((mwd @ f.calc_center_median()).y - YF) < 0.006
             and abs((mwd @ f.calc_center_median()).x) < 0.036 and 0.508 < (mwd @ f.calc_center_median()).z < 0.556]
    bmesh.ops.delete(bmd, geom=tirar, context="FACES")
    bmd.to_mesh(DET.data); bmd.free(); DET.data.update()
    DET.data["bolsa_fundo_aberto"] = len(tirar); print("FUNDO_ABERTO faces", len(tirar))

# ---- cantos da boca: suavizar a mistura de pesos perto da articulacao, nas laterais (uma vez so)
if not M.data.get("boca_cantos_v1"):
    gi = {g.index: g.name for g in M.vertex_groups}
    alvo = []
    for v in M.data.vertices:
        p = M.matrix_world @ v.co
        d = math.hypot(p.y - DOBRA.y, p.z - (DOBRA.z + 0.012))
        nomes = {gi[g.group] for g in v.groups if g.weight > 0.02}
        if d < 0.045 and abs(p.x) > 0.035 and ("mouth_lower" in nomes or "mouth_upper" in nomes): alvo.append(v.index)
    bpy.ops.object.select_all(action="DESELECT"); M.select_set(True); bpy.context.view_layer.objects.active = M
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="DESELECT"); bpy.ops.object.mode_set(mode="OBJECT")
    for i in alvo: M.data.vertices[i].select = True
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=0.5, repeat=6, expand=0.15)
    bpy.ops.object.mode_set(mode="OBJECT")
    # normaliza e limita a 4 influencias SO nos vertices do canto (o resto do corpo fica intacto)
    for i in alvo:
        v = M.data.vertices[i]
        gs = sorted(((g.group, g.weight) for g in v.groups), key=lambda x: -x[1])
        manter = [x for x in gs[:4] if x[1] > 0.001]; tot = sum(w for _, w in manter) or 1
        for g, _ in gs: M.vertex_groups[g].remove([i])
        for g, w in manter: M.vertex_groups[g].add([i], w / tot, "REPLACE")
    M.data["boca_cantos_v1"] = len(alvo)
    print("CANTOS suavizados", len(alvo))
if SALVAR: bpy.ops.wm.save_mainfile(); print("SALVO")
print("BOCA_OK")
