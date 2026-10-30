"""Renderiza o dragao original do Mesh2Motion (malha 'Dragon' do dragon-animations.glb) e o Silverwing no mesmo quadro
de cada acao, cada um enquadrado pela propria caixa, vistas topo/frente/3-4, para comparar como as asas dobram.
Uso: blender -b Silverwing_M2M.blend -P comparar_molde.py -- dragon-animations.glb saida_dir acao:quadro ..."""
import bpy, sys, os
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]; anim, out = args[0], args[1]; pedidos = [a.split(":") for a in args[2:]]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=anim)
novos = [o for o in bpy.data.objects if o not in antes]
T = [o for o in novos if o.type == "ARMATURE"][0]; D = [o for o in novos if o.type == "MESH" and o.name.startswith("Dragon")][0]
for o in novos:
    if o.name.startswith("Icosphere"): o.hide_render = True
for t in T.animation_data.nla_tracks: t.mute = True
chao = bpy.data.objects.get("chao_revisao")
cam = bpy.data.objects["cam_rev"]; sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 560, 420
def caixa(o):
    dg = bpy.context.evaluated_depsgraph_get(); me = o.evaluated_get(dg).to_mesh()
    ps = [o.matrix_world @ v.co for v in me.vertices]; o.evaluated_get(dg).to_mesh_clear()
    mn = Vector([min(p[i] for p in ps) for i in range(3)]); mx = Vector([max(p[i] for p in ps) for i in range(3)])
    return (mn + mx) / 2, (mx - mn).length
for acao, q in pedidos:
    act_s = bpy.data.actions["Silverwing_" + acao]; act_t = bpy.data.actions[acao.replace("_", " ")]
    A.animation_data.action = act_s; A.animation_data.action_slot = act_s.slots[0]
    T.animation_data.action = act_t; T.animation_data.action_slot = act_t.slots[0]
    sc.frame_set(int(q))
    for quem, obj, outro in (("silver", M, D), ("molde", D, M)):
        obj.hide_render = False; outro.hide_render = True
        if chao: chao.hide_render = quem == "molde"
        c, r = caixa(obj)
        for vista, d in (("topo", (0, -0.01, 1)), ("frente", (0, -1, 0.15)), ("34", (0.8, -1, 0.6))):
            cam.location = c + Vector(d).normalized() * r * 1.2
            cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = os.path.join(out, "cmp_%s_%s_%s_%s.png" % (acao, q, vista, quem)); bpy.ops.render.render(write_still=True)
    M.hide_render = False
print("COMPARAR_OK")
