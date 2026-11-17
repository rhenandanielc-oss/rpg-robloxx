"""Poses extremas de TESTE no rig do Cerbero (deformacao real pelo esqueleto; NAO sao clipes). Adaptado de
Urso_Silvestre_Ref/v2/rig/poses_teste.py. Mede por pose: altura minima, esticamento das arestas (p99, maximo e onde) e
renderiza. Tambem gera a vista dos ossos (raio-x) em repouso. Nada e salvo no .blend.
Uso: blender -b -t 4 CR_Cerbero_Rig.blend -P poses_cerbero.py -- <saida_dir>"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Cerbero_Rig"]
sc.render.threads_mode = "FIXED"; sc.render.threads = 4
PELES = [bpy.data.objects[n] for n in ("Cerbero_Cabecas", "Cerbero_Corpo")]; BOCA = bpy.data.objects["Cerbero_Bocas"]
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.42, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
for nome, en, rot in (("K", 3.2, (0.84, 0, -0.61)), ("R", 2.0, (2.1, 0, 2.8)), ("F", 1.2, (1.13, 0, 1.92))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=200); ch = bpy.context.object; mc = bpy.data.materials.new("Chao"); mc.use_nodes = True
mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1); ch.data.materials.append(mc)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
def render(nome, pos, alvo, lente=50, res=(1000, 720)):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
# referencial das cabecas = ossos Cabeca{K} (frente horizontal)
CABS = {}
for k in "CED":
    b = A.data.bones["Cabeca" + k]; f = (b.tail_local - b.head_local); f.z = 0; f.normalize()
    CABS[k] = (b.tail_local.copy(), f, f.cross(V((0, 0, 1))).normalized())

# ------------------------------------------------------------------ vista dos ossos (raio-x, Workbench)
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "OBJECT"
sh.show_xray = True; sh.xray_alpha = 0.35
cil = []
mo = bpy.data.materials.new("Osso")
for b in A.data.bones:
    h, t = b.head_local, b.tail_local; d = t - h
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18 if b.name != "Raiz" else 0.3, depth=d.length, vertices=8, location=(h + t) / 2)
    o = bpy.context.object; o.rotation_euler = d.to_track_quat("Z", "Y").to_euler(); o.color = (1.0, 0.35, 0.05, 1) if "Mandibula" in b.name else (0.1, 0.8, 1.0, 1)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, segments=10, ring_count=6, location=h); s_ = bpy.context.object; s_.color = (1, 1, 0.2, 1)
    cil += [o, s_]
for o in PELES + [BOCA]: o.color = (0.5, 0.5, 0.5, 1)
ch.hide_render = True
render("ossos_lado", (-40, 0, 10), (0, 0, 9), 50); render("ossos_frente", (0, -42, 12), (0, 0, 9), 50); render("ossos_cima", (0, 0.01, 50), (0, 0, 0), 45)
for o in cil: bpy.data.objects.remove(o, do_unlink=True)
sh.show_xray = False; ch.hide_render = False
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 24; sc.view_settings.view_transform = "AgX"

REST = {}
for o in PELES:
    e = np.empty(len(o.data.edges) * 2, dtype=np.int64); o.data.edges.foreach_get("vertices", e); e = e.reshape(-1, 2)
    c = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", c); c = c.reshape(-1, 3)
    REST[o.name] = (e, np.linalg.norm(c[e[:, 0]] - c[e[:, 1]], axis=1), c)
def medir():
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); zmin = 99.0; rs = []; pior = None; ruins = []
    for o in PELES + [BOCA]:
        ev = o.evaluated_get(dg); m = ev.to_mesh()
        c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); c = c.reshape(-1, 3); zmin = min(zmin, float(c[:, 2].min()))
        if o.name in REST:
            e, l0, c0 = REST[o.name]; r = np.linalg.norm(c[e[:, 0]] - c[e[:, 1]], axis=1) / np.maximum(l0, 1e-6); rs.append(r)
            i = int(np.argmax(r)); rr = e[r > 3][:, 0]
            if len(rr): ruins.append((o.name, int(len(rr)), tuple(np.round(c0[rr].mean(axis=0), 1))))
            if pior is None or r[i] > pior[0]: pior = (round(float(r[i]), 2), o.name, tuple(np.round(c0[e[i, 0]], 1)))
        ev.to_mesh_clear()
    r = np.concatenate(rs)
    return zmin, float(np.percentile(r, 99)), pior, ruins
def zera():
    for pb in A.pose.bones: pb.matrix_basis.identity()
    bpy.context.view_layer.update()
def girar(nome, eixo, graus):
    bpy.context.view_layer.update(); pb = A.pose.bones[nome]; M = pb.matrix.copy(); h = M.translation.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ M
    bpy.context.view_layer.update()
def mover(nome, d):
    bpy.context.view_layer.update(); pb = A.pose.bones[nome]; pb.matrix = Matrix.Translation(V(d)) @ pb.matrix.copy(); bpy.context.view_layer.update()
X, Z = V((1, 0, 0)), V((0, 0, 1))
S = {k: CABS[k][2] for k in "CED"}                          # eixo lateral de cada cabeca (mandibula/cabeca para baixo = negativo)
POSES = {
    "repouso": [],
    "bocas_abertas": [("MandibulaC", S["C"], -32), ("MandibulaE", S["E"], -32), ("MandibulaD", S["D"], -32)],
    "cabecas_alvos_diferentes": [("PescocoE1", Z, 22), ("PescocoE2", Z, 12), ("CabecaE", S["E"], 12),          # E olha para fora e para cima
                                 ("PescocoD1", S["D"], -18), ("PescocoD2", S["D"], -14), ("CabecaD", S["D"], -10),  # D abaixa
                                 ("PescocoC1", Z, -16), ("PescocoC2", Z, -12), ("MandibulaC", S["C"], -24)],   # C vira e morde
    "cabecas_juntas_frente": [("PescocoE1", Z, -18), ("PescocoE2", Z, -14), ("PescocoD1", Z, 18), ("PescocoD2", Z, 14),
                              ("PescocoC1", S["C"], -12), ("CabecaC", S["C"], -10)],
    "passada_longa": [("BracoE", X, 30), ("AntebracoE", X, -22), ("MaoE", X, -15), ("BracoD", X, -26), ("AntebracoD", X, 16),
                      ("MaoD", X, 22), ("CoxaE", X, -26), ("CanelaE", X, 28), ("PeE", X, -10), ("CoxaD", X, 28),
                      ("CanelaD", X, -14), ("PeD", X, -10), ("Coluna2", Z, 5), ("Cauda1", X, -15)],
    "agachar_ataque": [("Coluna3", X, -8), ("BracoE", X, 24), ("BracoD", X, 24), ("AntebracoE", X, -44), ("AntebracoD", X, -44),
                       ("MaoE", X, 22), ("MaoD", X, 22), ("PescocoC1", S["C"], -10), ("PescocoE1", S["E"], -10), ("PescocoD1", S["D"], -10),
                       ("Cauda1", X, 20)],
    "torcao_tronco": [("Coluna1", Z, 12), ("Coluna2", Z, 12), ("Coluna3", Z, 8), ("Cauda1", Z, -25), ("Cauda2", Z, -15), ("Coluna2", V((0, 1, 0)), 6)],
}
linhas = ["pose;z_min;esticamento_p99;pior_aresta;arestas>3x(malha,qtd,centro_repouso)"]
for nome, ops in POSES.items():
    zera()
    for o_, ax, g in ops: girar(o_, ax, g)
    if nome != "repouso":
        zmin, *_ = medir(); mover("Raiz", (0, 0, -zmin))
    zmin, p99, pior, ruins = medir()
    linhas.append("%s;%.3f;%.3f;%s;%s" % (nome, zmin, p99, pior, ruins)); print("POSE", linhas[-1], flush=True)
    if nome.startswith(("bocas", "cabecas")):
        render(nome + "_34", (-16, -30, 22), (0, -8, 15), 55)
        if nome == "bocas_abertas":
            for k in "CED":
                T, f, s_ = CABS[k]; render(nome + "_" + k, tuple(T + f * 9 + s_ * 6 + V((0, 0, 1.5))), tuple(T - f * 1.0), 55, (800, 640))
    else:
        render(nome + "_lado", (-40, 0, 10), (0, 0, 8.5), 50); render(nome + "_34", (-30, -32, 20), (0, 0, 8), 50)
zera()
open(os.path.join(OUT, "poses_medidas.txt"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
print("POSES_OK", flush=True)
