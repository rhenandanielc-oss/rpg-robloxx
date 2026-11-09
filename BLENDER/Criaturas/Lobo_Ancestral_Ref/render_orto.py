"""Vistas ORTOGRAFICAS (cima, frente, lado) com grade de 1 stud, para medir pivos. So leitura (nao salva).
Uso: blender -b <arquivo.blend> -P render_orto.py -- <saida_dir>"""
import bpy, sys, os, math, bmesh
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
for o in list(sc.objects):
    if o.name.startswith("Plane"): o.hide_render = True
# grade: linhas finas a cada stud no plano z=0 e x=0 e y=0
def grade(nome, eixo):
    m = bpy.data.meshes.new(nome); b = bmesh.new()
    for i in range(-8, 9):
        for a, c in ((V((i, -8, 0)), V((i, 8, 0))), (V((-8, i, 0)), V((8, i, 0)))):
            if eixo == "x": a, c = V((0, a.x, a.y + 8)) * 1, V((0, c.x, c.y + 8))
            if eixo == "y": a, c = V((a.x, 0, a.y + 8)), V((c.x, 0, c.y + 8))
            v1, v2 = b.verts.new(a), b.verts.new(c); b.edges.new((v1, v2))
    b.to_mesh(m); b.free(); o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    mod = o.modifiers.new("W", "WIREFRAME"); mod.thickness = 0.02
    mat = bpy.data.materials.new(nome)
    if mat.node_tree is None: mat.use_nodes = True
    bs = mat.node_tree.nodes["Principled BSDF"]; bs.inputs["Base Color"].default_value = (1, 0.1, 0.1, 1)
    bs.inputs["Emission Color"].default_value = (1, 0.1, 0.1, 1); bs.inputs["Emission Strength"].default_value = 3
    o.data.materials.append(mat); return o
camd = bpy.data.cameras.new("Orto"); camd.type = "ORTHO"; camd.ortho_scale = 15
cam = bpy.data.objects.new("Orto", camd); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x = sc.render.resolution_y = 1200
for nome, pos, rot, g in (("cima", V((0, 0, 30)), (0, 0, 0), "z"), ("frente_orto", V((0, -30, 4.2)), (math.radians(90), 0, 0), "y"),
                          ("lado_orto", V((30, 0, 4.2)), (math.radians(90), 0, math.radians(90)), "x")):
    gr = grade("Grade_" + nome, g)
    if g == "y": gr.location.y = 4
    if g == "x": gr.location.x = -4
    cam.location = pos; cam.rotation_euler = rot
    sc.render.filepath = os.path.join(OUT, "orto_%s.png" % nome); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(gr)
