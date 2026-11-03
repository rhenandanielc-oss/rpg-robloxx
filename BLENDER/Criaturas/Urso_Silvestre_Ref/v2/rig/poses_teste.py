"""Poses extremas de TESTE no rig do Urso v2 (deformacao real pelo esqueleto, nao sao clipes de animacao):
repouso, erguer-se nas patas traseiras, passada longa, comer (cabeca baixa e de lado), torcao do tronco, boca aberta.
Mede por pose: altura minima da malha (garras/patas abaixo do chao), esticamento das arestas da pele (p99 e maximo,
razao posado/repouso) e onde ocorre. Renderiza perfil e 3/4 com luz neutra. Nada e salvo no .blend.
Uso: blender -b CR_Urso_v2_Rig.blend -P poses_teste.py -- <saida_dir>"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Urso_Rig"]
PELES = [bpy.data.objects[n] for n in ("Urso_Cabeca", "Urso_Corpo_Frente", "Urso_Corpo_Tras")]; BOCA = bpy.data.objects["Urso_Boca"]
# cena neutra
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.42, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
for nome, en, rot in (("K", 3.0, (0.84, 0, -0.61)), ("R", 2.0, (2.1, 0, 2.8)), ("F", 1.0, (1.13, 0, 1.92))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=80); ch = bpy.context.object; mc = bpy.data.materials.new("Chao"); mc.use_nodes = True
mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1); ch.data.materials.append(mc)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 24; sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
def render(nome, pos, alvo, lente=50):
    sc.render.resolution_x, sc.render.resolution_y = 1100, 750
    cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)

# arestas de repouso
REST = {}
for o in PELES:
    e = np.empty(len(o.data.edges) * 2, dtype=np.int64); o.data.edges.foreach_get("vertices", e); e = e.reshape(-1, 2)
    c = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", c); c = c.reshape(-1, 3)
    REST[o.name] = (e, np.linalg.norm(c[e[:, 0]] - c[e[:, 1]], axis=1))
def medir():
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); zmin = 9.0; rs = []; pior = None
    for o in PELES + [BOCA]:
        ev = o.evaluated_get(dg); m = ev.to_mesh()
        c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); c = c.reshape(-1, 3)
        c = (np.array(o.matrix_world)[:3, :3] @ c.T).T + np.array(o.matrix_world.translation)
        zmin = min(zmin, float(c[:, 2].min()))
        if o.name in REST:
            e, l0 = REST[o.name]; l1 = np.linalg.norm(c[e[:, 0]] - c[e[:, 1]], axis=1); r = l1 / np.maximum(l0, 1e-6); rs.append(r)
            i = int(np.argmax(r))
            c0 = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", c0); c0 = c0.reshape(-1, 3)
            ruins = np.unique(e[r > 3][:, 0])
            if len(ruins): print("   RUINS", o.name, len(ruins), "repouso y/z medios", np.round(c0[ruins].mean(axis=0), 2), "faixa y", np.round(c0[ruins][:, 1].min(), 2), np.round(c0[ruins][:, 1].max(), 2))
            if pior is None or r[i] > pior[0]: pior = (round(float(r[i]), 2), o.name, "repouso", tuple(float(v) for v in np.round(c0[e[i, 0]], 2)), "arestas>3x:", int((r > 3).sum()))
        ev.to_mesh_clear()
    r = np.concatenate(rs)
    return zmin, float(np.percentile(r, 99)), float(np.percentile(r, 1)), pior
def zera():
    for pb in A.pose.bones: pb.matrix_basis.identity()
    bpy.context.view_layer.update()
def girar(nome, eixo, graus):
    """gira o osso em torno de um eixo do MUNDO passando pela cabeca do osso (os filhos acompanham)"""
    bpy.context.view_layer.update(); pb = A.pose.bones[nome]; M = pb.matrix.copy(); h = M.translation.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ M
    bpy.context.view_layer.update()
def mover(nome, d):
    bpy.context.view_layer.update(); pb = A.pose.bones[nome]; M = pb.matrix.copy(); pb.matrix = Matrix.Translation(V(d)) @ M
    bpy.context.view_layer.update()
POSES = {
    "repouso": [],
    "erguer_patas_traseiras": [("Pelve", "X", -52), ("CoxaE", "X", 52), ("CoxaD", "X", 52), ("CanelaE", "X", -8), ("CanelaD", "X", -8),
                               ("PeE", "X", 8), ("PeD", "X", 8), ("BracoE", "X", 35), ("BracoD", "X", 28), ("AntebracoE", "X", -55),
                               ("AntebracoD", "X", -48), ("MaoE", "X", -25), ("MaoD", "X", -25), ("Pescoco", "X", 22), ("Cabeca", "X", 12),
                               ("Mandibula", "X", 30), ("Raiz", "MOVE", (0, 0, 0.0))],
    "passada_longa": [("BracoE", "X", 32), ("AntebracoE", "X", -20), ("MaoE", "X", -12), ("BracoD", "X", -28), ("AntebracoD", "X", 18),
                      ("MaoD", "X", 22), ("CoxaE", "X", -26), ("CanelaE", "X", 24), ("PeE", "X", 6), ("CoxaD", "X", 30),
                      ("CanelaD", "X", -12), ("PeD", "X", -14), ("Coluna2", "Z", 6), ("Pescoco", "Z", -6)],
    "comer_cabeca_baixa": [("Coluna3", "X", 10), ("Pescoco", "X", 30), ("Pescoco2", "X", 18), ("Pescoco", "Z", 25), ("Pescoco2", "Z", 15),
                           ("Cabeca", "X", 10), ("Mandibula", "X", 18), ("OrelhaE", "X", -25), ("OrelhaD", "X", -25)],
    "torcao_tronco": [("Coluna1", "Z", 14), ("Coluna2", "Z", 14), ("Coluna3", "Z", 10), ("Pescoco", "Z", 20), ("Cauda1", "Z", -25),
                      ("Coluna2", "Y", 8)],
    "boca_aberta": [("Mandibula", "X", 38), ("Pescoco", "X", -18), ("Cabeca", "X", -12)],
}
EIXO = {"X": V((1, 0, 0)), "Y": V((0, 1, 0)), "Z": V((0, 0, 1))}
linhas = ["pose;z_min;esticamento_p99;compressao_p1;pior_aresta"]
for nome, ops in POSES.items():
    zera()
    for o_, ax, g in ops:
        if ax == "MOVE": mover(o_, g)
        else: girar(o_, EIXO[ax], g)
    if nome != "repouso":                                      # apoio: o corpo inteiro sobe/desce ate a parte mais baixa tocar o chao
        zmin, *_ = medir(); mover("Raiz", (0, 0, -zmin))
    zmin, p99, p1, pior = medir()
    linhas.append("%s;%.3f;%.3f;%.3f;%s" % (nome, zmin, p99, p1, pior)); print("POSE", linhas[-1])
    if nome == "erguer_patas_traseiras":
        render(nome + "_lado", (-30, -1.0, 7.5), (0, 1.0, 7.0), 45); render(nome + "_34", (-20, -20, 9), (0, 0.5, 6.5), 45)
    elif nome in ("boca_aberta",):
        render(nome + "_cab", (-4.6, -9.8, 7.6), (0, -5.0, 7.0), 60)
    else:
        render(nome + "_lado", (-30, 0, 5.5), (0, 0, 4.6), 45); render(nome + "_34", (-20, -20, 9), (0, -0.5, 4.4), 45)
zera()
open(os.path.join(OUT, "poses_medidas.txt"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
print("POSES_OK")
