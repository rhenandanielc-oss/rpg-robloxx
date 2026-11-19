# Arvore seca de vigia (freixo morto) para o poleiro de vista da Coruja-da-Floresta - Lagoa_5 (18/11/2026)
# Blender 5.2 headless:  blender -b --factory-startup --python gerar_arvore_seca.py
# Saidas (nesta pasta): Arvore_Seca_Vigia.blend, Arvore_Seca_Vigia.glb, casca_seca.png, render_*.png, poleiro.json
# Unidades: 1 unidade Blender = 1 stud (a escala final e conferida no Studio). Z para cima, frente do galho = +X.
import bpy, bmesh, math, random, json, os
import numpy as np
from mathutils import Vector, Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
random.seed(7); np.random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)

# ------------------------------------------------------------------ textura (tileavel em U e V)
W, H = 512, 1024
u = np.linspace(0, 2 * np.pi, W, endpoint=False)[None, :]
v = np.linspace(0, 2 * np.pi, H, endpoint=False)[:, None]
def onda(fu, fv, fase):
    return np.sin(fu * u + fv * v + fase)
sulcos = np.zeros((H, W))
for k in range(9):
    fu = random.choice([10, 12, 14, 16, 18, 22]); fv = random.choice([1, 2, 3])
    sulcos += onda(fu, fv, random.uniform(0, 6.28)) * (1.0 / (k + 1) ** 0.5)
sulcos = (sulcos - sulcos.min()) / (sulcos.max() - sulcos.min())
fino = np.zeros((H, W))
for k in range(6):
    fino += onda(random.choice([30, 34, 40, 46]), random.choice([4, 6, 8]), random.uniform(0, 6.28))
fino = (fino - fino.min()) / (fino.max() - fino.min())
musgo = np.zeros((H, W))
for k in range(5):
    musgo += onda(random.choice([4, 6, 8]), random.choice([2, 3, 4]), random.uniform(0, 6.28))
musgo = (musgo - musgo.min()) / (musgo.max() - musgo.min())
musgo = np.clip((musgo - 0.62) * 4.0, 0, 1) * np.clip((sulcos - 0.25) * 3, 0, 1)
# casca seca: cinza-acastanhada (arvore morta, sem a casca verde-viva das vivas), sulcos escuros, musgo nos sulcos
base = np.array([0.36, 0.29, 0.23]); claro = np.array([0.50, 0.42, 0.34]); escuro = np.array([0.13, 0.10, 0.08])
verde = np.array([0.24, 0.33, 0.13])
t = (sulcos * 0.7 + fino * 0.3)[..., None]
cor = escuro * (1 - t) + (base * 0.6 + claro * 0.4) * t
cor = cor * (1 - np.clip((0.22 - sulcos) * 4, 0, 1))[..., None] * 1.0
cor = cor * (1 - musgo[..., None] * 0.85) + verde * musgo[..., None] * 0.85
# faixa de madeira exposta (topo quebrado / ponta do galho): ultimos 64 px de cima da imagem, sem tileamento
mad = np.array([0.66, 0.53, 0.38]); anel = np.array([0.48, 0.36, 0.24])
yy, xx = np.mgrid[0:64, 0:W]
r = np.sqrt(((xx % 64) - 32) ** 2 + (yy - 32) ** 2)
aneis = (np.sin(r * 0.9) * 0.5 + 0.5)[..., None]
cor[H - 64:, :, :] = mad * (1 - aneis * 0.5) + anel * aneis * 0.5
img = bpy.data.images.new("casca_seca", W, H, alpha=False)
rgba = np.concatenate([np.clip(cor, 0, 1), np.ones((H, W, 1))], axis=2).astype(np.float32)
img.pixels.foreach_set(rgba.ravel())
img.filepath_raw = os.path.join(AQUI, "casca_seca.png"); img.file_format = 'PNG'; img.save()
V_MAD = (H - 64 + 2) / H   # inicio da faixa de madeira (v da textura)

# ------------------------------------------------------------------ geometria
bm = bmesh.new()
uvl = bm.loops.layers.uv.new("UVMap")
LADOS = 14

def tubo(caminho, raios, lados=LADOS, lobos=None, topo_quebrado=None, tampa=True, fundo=False, rot0=0.0):
    """anel por ponto do caminho; raios por ponto; lobos(i,ang)->fator; topo_quebrado: alturas extras no ultimo anel."""
    aneis = []
    comp = 0.0
    tang_ant = None
    for i, p in enumerate(caminho):
        if i < len(caminho) - 1: tg = (caminho[i + 1] - p).normalized()
        else: tg = (p - caminho[i - 1]).normalized()
        if tang_ant is None:
            ref = Vector((0, 0, 1)) if abs(tg.z) < 0.9 else Vector((1, 0, 0))
            n1 = tg.cross(ref).normalized()
        else:
            n1 = (n1 - tg * n1.dot(tg)).normalized()
        n2 = tg.cross(n1).normalized()
        tang_ant = tg
        if i > 0: comp += (p - caminho[i - 1]).length
        anel = []
        for k in range(lados):
            a = rot0 + 2 * math.pi * k / lados
            rr = raios[i] * (lobos(i, a) if lobos else 1.0) * (1 + random.uniform(-0.05, 0.05))
            q = p + (n1 * math.cos(a) + n2 * math.sin(a)) * rr
            if topo_quebrado is not None and i == len(caminho) - 1:
                q = q + tg * topo_quebrado[k]
            anel.append((bm.verts.new(q), comp))
        aneis.append(anel)
    circ = 2 * math.pi * max(raios)
    for i in range(len(aneis) - 1):
        for k in range(lados):
            a0, a1 = aneis[i][k], aneis[i][(k + 1) % lados]
            b0, b1 = aneis[i + 1][k], aneis[i + 1][(k + 1) % lados]
            f = bm.faces.new((a0[0], a1[0], b1[0], b0[0]))
            u0, u1 = k / lados, (k + 1) / lados
            for lp, (uu, vv) in zip(f.loops, ((u0, a0[1]), (u1, a1[1]), (u1, b1[1]), (u0, b0[1]))):
                lp[uvl].uv = (uu, (vv / circ) % 1.0 * V_MAD * 0.98)
    def tampar(anel, inverter):
        c = sum((x[0].co for x in anel), Vector()) / len(anel)
        cv = bm.verts.new(c)
        for k in range(lados):
            a, b = anel[k][0], anel[(k + 1) % lados][0]
            f = bm.faces.new((cv, b, a) if not inverter else (cv, a, b))
            for lp in f.loops:
                d = lp.vert.co - c
                ang = math.atan2(d.y, d.x)
                lp[uvl].uv = ((0.0625 + 0.05 * math.cos(ang) * (0 if lp.vert is cv else 1)) , V_MAD + 0.03 + 0.025 * math.sin(ang) * (0 if lp.vert is cv else 1))
    if tampa: tampar(aneis[-1], False)
    if fundo: tampar(aneis[0], True)
    return aneis

def caminho_curvo(p0, direcao, comp, n, curva=Vector((0, 0, 0)), ruido=0.15):
    pts = []
    d = direcao.normalized()
    for i in range(n):
        s = i / (n - 1)
        p = p0 + d * comp * s + curva * (s * s)
        if 0 < i < n - 1: p = p + Vector((random.uniform(-1, 1), random.uniform(-1, 1), 0)) * ruido
        pts.append(p)
    return pts

ALT = 21.0
# tronco: leve inclinacao, raizes em 5 lobos na base, topo quebrado em lascas
cam_tronco = []
for i in range(16):
    s = i / 15
    cam_tronco.append(Vector((0.35 * math.sin(s * 2.2) - 0.2 * s, 0.25 * math.sin(s * 3.1), -1.0 + (ALT + 1.0) * s)))
raios_tronco = []
for i in range(16):
    s = i / 15
    r0 = 1.25 - 0.62 * s
    if i <= 2: r0 *= (1.9 - 0.35 * i)          # alargamento das raizes
    raios_tronco.append(r0)
def lobos_raiz(i, a):
    if i > 2: return 1.0 + 0.06 * math.sin(3 * a + i)
    return 1.0 + (0.45 - 0.15 * i) * max(0.0, math.cos(5 * a)) ** 2
lascas = [random.choice([0.0, 0.4, 1.1, 1.8, 0.2, 2.3, 0.6]) for _ in range(LADOS)]
tronco = tubo(cam_tronco, raios_tronco, lobos=lobos_raiz, topo_quebrado=lascas, tampa=True, fundo=True)

def no_tronco(z):
    # ponto do eixo do tronco na altura z
    for i in range(len(cam_tronco) - 1):
        a, b = cam_tronco[i], cam_tronco[i + 1]
        if a.z <= z <= b.z:
            t2 = (z - a.z) / (b.z - a.z); return a.lerp(b, t2), raios_tronco[i] * (1 - t2) + raios_tronco[i + 1] * t2
    return cam_tronco[-1], raios_tronco[-1]

# GALHO DE VIGIA: horizontal para +X (lado da lagoa), na altura 13,5, ponta quebrada; topo quase plano para as garras
Z_G = 13.5
eixo, rt = no_tronco(Z_G)
ini = eixo + Vector((rt * 0.2, 0, -0.35))
cam_g = caminho_curvo(ini, Vector((1, 0.08, 0.05)), 5.6, 9, curva=Vector((0, 0.15, 0.35)), ruido=0.04)
raios_g = [0.46 - 0.21 * (i / 8) for i in range(9)]
galho = tubo(cam_g, raios_g, lados=10, topo_quebrado=[random.choice([0.0, 0.25, 0.45]) for _ in range(10)], tampa=True)
# tocos curtos (galhos antigos quebrados)
for zt, dirt, cmp_ in ((9.0, Vector((-0.8, 0.6, 0.35)), 1.6), (16.8, Vector((-0.3, -1, 0.45)), 2.2), (18.6, Vector((0.7, 0.7, 0.6)), 1.2)):
    e, r2 = no_tronco(zt)
    cam_t = caminho_curvo(e, dirt, r2 + cmp_, 4, ruido=0.02)
    tubo(cam_t, [0.34, 0.3, 0.24, 0.2], lados=8, topo_quebrado=[random.choice([0, 0.12, 0.25]) for _ in range(8)], tampa=True)

me = bpy.data.meshes.new("Arvore_Seca_Vigia")
bm.normal_update()
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("Arvore_Seca_Vigia", me)
bpy.context.scene.collection.objects.link(ob)
for p in me.polygons: p.use_smooth = True
mat = bpy.data.materials.new("Casca_Seca")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
tex = mat.node_tree.nodes.new("ShaderNodeTexImage"); tex.image = img
mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.9
me.materials.append(mat)

# ------------------------------------------------------------------ poleiro: topo do galho a 3,2 studs do tronco (medido por raycast)
bpy.context.view_layer.update()
from mathutils.bvhtree import BVHTree
dg = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(ob, dg)
pol = []
for dx in (2.6, 3.2, 3.8, 4.4):
    q = cam_g[0].lerp(cam_g[-1], dx / 5.6)
    hit = bvh.ray_cast(Vector((q.x, q.y, q.z + 3)), Vector((0, 0, -1)))
    if hit[0] is not None: pol.append({"x": round(hit[0].x, 3), "y": round(hit[0].y, 3), "z": round(hit[0].z, 3), "nz": round(hit[1].z, 3)})
info = {"altura_total": ALT, "galho_z": Z_G, "galho_dir": [1, 0.08, 0.05], "poleiro_pontos": pol,
        "tris": sum(len(p.vertices) - 2 for p in me.polygons), "verts": len(me.vertices)}
# QA basico
bm2 = bmesh.new(); bm2.from_mesh(me)
info["arestas_nao_manifold"] = sum(1 for e in bm2.edges if not e.is_manifold)
info["faces_degeneradas"] = sum(1 for f in bm2.faces if f.calc_area() < 1e-6)
bm2.free()
json.dump(info, open(os.path.join(AQUI, "poleiro.json"), "w"), indent=1)
print("INFO", json.dumps(info))

# ------------------------------------------------------------------ render de revisao (EEVEE, 2 vistas + coruja de escala: esfera 1,2)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 900, 1100
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.68, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
sol = bpy.data.lights.new("sol", 'SUN'); sol.energy = 3.5
so = bpy.data.objects.new("sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
chao = bpy.context.object; mc = bpy.data.materials.new("chao"); mc.use_nodes = True
mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.18, 0.3, 0.12, 1); chao.data.materials.append(mc)
if pol:
    p = pol[1] if len(pol) > 1 else pol[0]
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(p["x"], p["y"], p["z"] + 0.6))
    co = bpy.context.object; mo = bpy.data.materials.new("coruja"); mo.use_nodes = True
    mo.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.45, 0.3, 0.15, 1); co.data.materials.append(mo)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
for nome, pos in (("lado", (4, -30, 9)), ("tres4", (-18, -22, 6))):
    cam.location = pos
    d = Vector((1.5, 0, 11)) - Vector(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(AQUI, f"render_{nome}.png")
    bpy.ops.render.render(write_still=True)
# remove objetos de revisao antes de salvar/exportar
for o in list(sc.objects):
    if o.name != "Arvore_Seca_Vigia": bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "Arvore_Seca_Vigia.blend"))
bpy.ops.export_scene.gltf(filepath=os.path.join(AQUI, "Arvore_Seca_Vigia.glb"), export_format='GLB', use_selection=False, export_yup=True)
print("OK")
