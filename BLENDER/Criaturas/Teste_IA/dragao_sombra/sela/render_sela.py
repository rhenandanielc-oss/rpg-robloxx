"""Renders de revisao da sela: tema por cores (TEMA=Sombra|Fogo|Gelo), boneco de cavaleiro em escala (R15 ~5 studs) no ponto
do jogo, vistas e poses. Uso: blender -b rig/SB_Dragao_M2M_v11_sela.blend -P sela/render_sela.py -- <saida_dir> <prefixo>
Env: TEMA, VISTAS (lado,34,frente,cima,tras), POSES (Parado:0.3,Andar:0.5,Voo:0.4,...), SEM_CAVALEIRO=1"""
import bpy, os, sys, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT, PRE = os.path.abspath(a[0]), a[1]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; S = bpy.data.objects["Silverwing_Sela"]
for o in sc.objects:
    if o.name.startswith("chao_revisao"): o.hide_render = True
TEMAS = {   # couro, metal, madeira, adorno (sRGB aproximado), rugosidade/metal
    "Sombra": [(0.24, 0.15, 0.22), (0.42, 0.40, 0.46), (0.26, 0.17, 0.16), (0.55, 0.28, 0.90)],   # (r2) mais claro que o corpo
    "Fogo": [(0.36, 0.17, 0.08), (0.18, 0.15, 0.14), (0.30, 0.18, 0.09), (1.0, 0.42, 0.10)],
    "Gelo": [(0.86, 0.87, 0.88), (0.70, 0.74, 0.80), (0.42, 0.33, 0.26), (0.55, 0.85, 1.0)],
}
tema = os.environ.get("TEMA", "Sombra"); cores = TEMAS[tema]
def lin(c): return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)
for i, nome in enumerate(["couro", "metal", "madeira", "adorno"]):
    mt = bpy.data.materials["M_Sela_" + nome]; bs = mt.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*lin(cores[i]), 1)
    bs.inputs["Roughness"].default_value = {"couro": 0.62, "metal": 0.35, "madeira": 0.55, "adorno": 0.2}[nome]
    bs.inputs["Metallic"].default_value = 1.0 if nome == "metal" else 0.0
    if nome == "adorno":
        bs.inputs["Emission Color"].default_value = (*lin(cores[i]), 1); bs.inputs["Emission Strength"].default_value = 0.6
# boneco de cavaleiro (blocos) em escala: 1 unidade ~ 17,5 studs; R15 sentado
ESC = 1 / 17.5
def bloco(nome, c, t, cor):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.name = nome; o.scale = t
    mt = bpy.data.materials.get("M_cav") or bpy.data.materials.new("M_cav"); mt.use_nodes = True
    mt.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*lin(cor), 1)
    o.data.materials.append(mt); o.parent = A; o.parent_type = "BONE"; o.parent_bone = "spine_1"
    o.matrix_world = __import__("mathutils").Matrix.Translation(c) @ __import__("mathutils").Matrix.Diagonal((*t, 1)); return o
if not os.environ.get("SEM_CAVALEIRO"):
    hrp = V(S["HRP"])
    def q(x, y, z): return hrp + V((x, y, z)) * ESC
    bloco("Cav_Tronco", q(0, 0, 0.9), (2 * ESC, 1 * ESC, 2 * ESC), (0.55, 0.55, 0.6))
    bloco("Cav_Cabeca", q(0, 0, 2.5), (1.1 * ESC, 1.1 * ESC, 1.1 * ESC), (0.85, 0.7, 0.55))
    for s in (1, -1):
        bloco("Cav_Coxa", q(s * 0.55, -0.9, -0.15), (0.8 * ESC, 1.8 * ESC, 0.8 * ESC), (0.35, 0.3, 0.28))
        bloco("Cav_Canela", q(s * 0.9, -1.7, -1.1), (0.7 * ESC, 0.7 * ESC, 1.8 * ESC), (0.35, 0.3, 0.28))
        bloco("Cav_Braco", q(s * 1.35, -0.6, 0.9), (0.6 * ESC, 1.6 * ESC, 0.6 * ESC), (0.55, 0.55, 0.6))
if os.environ.get("ESCONDER_ASAS"):                                  # so para a revisao: mascara os vertices das asas
    C = bpy.data.objects["Silverwing"]; asa = C.vertex_groups.get("_asas_revisao") or C.vertex_groups.new(name="_asas_revisao")
    nomes = {g.index for g in C.vertex_groups if g.name.startswith("wing_") and (os.environ.get("ESCONDER_ASAS") == "2" or not g.name.startswith("wing_1"))}
    ids = [v.index for v in C.data.vertices if sum(g.weight for g in v.groups if g.group in nomes) > 0.3]
    asa.add(ids, 1.0, "REPLACE"); mk = C.modifiers.new("mask_asas", "MASK"); mk.vertex_group = asa.name; mk.invert_vertex_group = True
POSES = [p.split(":") for p in os.environ.get("POSES", "Rest_Pose:0").split(",")]
VISTAS = os.environ.get("VISTAS", "lado,34,frente,cima").split(",")
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 800, 600
cam = bpy.data.objects.get("CamSela") or bpy.data.objects.new("CamSela", bpy.data.cameras.new("CamSela"))
if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
sc.camera = cam; cam.data.lens = 50; cam.data.clip_start = 0.001
if not [o for o in sc.objects if o.type == "LIGHT"]:
    l = bpy.data.objects.new("SolS", bpy.data.lights.new("SolS", "SUN")); l.data.energy = 3.2; sc.collection.objects.link(l); l.rotation_euler = (0.7, 0.2, 0.8)
f = bpy.data.objects.get("FillS") or bpy.data.objects.new("FillS", bpy.data.lights.new("FillS", "SUN"))
if f.name not in sc.collection.objects: sc.collection.objects.link(f)
f.data.energy = 1.3; f.rotation_euler = (1.2, 0, -2.4)
if not A.animation_data: A.animation_data_create()
for pose, fr in POSES:
    act = bpy.data.actions.get("Silverwing_" + pose)
    if act:
        A.animation_data.action = act
        if hasattr(A.animation_data, "action_slot") and act.slots: A.animation_data.action_slot = act.slots[0]
        f0, f1 = act.frame_range; sc.frame_set(int(f0 + (f1 - f0) * float(fr)))
    else:
        A.animation_data.action = None
        for b in A.pose.bones: b.matrix_basis.identity()
        sc.frame_set(1)
    bpy.context.view_layer.update()
    alvo = A.matrix_world @ A.pose.bones["spine_1"].head + V((0, 0, 0.05))
    K = float(os.environ.get("DIST", "1.0"))
    D = {"lado": V((1.0, 0.0, 0.18)), "34": V((0.72, -0.62, 0.45)), "frente": V((0.25, -1.0, 0.32)), "cima": V((0.10, 0.35, 1.0)),
         "tras": V((0.55, 0.75, 0.55)), "longe": V((2.6, -1.6, 1.4)), "perto": V((0.55, -0.30, 0.30)), "perto2": V((-0.42, 0.38, 0.40)), "perto_cima": V((0.10, 0.18, 0.62)), "perto_frente": V((0.18, -0.62, 0.24))}
    for vn in VISTAS:
        d = D[vn]; cam.location = alvo + d * (K if not vn.startswith("perto") else 1.0)
        cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_%s_%s.png" % (PRE, pose, vn)); bpy.ops.render.render(write_still=True)
print("RENDER_SELA_OK")
