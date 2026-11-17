"""Montaria M3b: a sela de jogo sobre o lobo nos clipes de locomocao/acao (so leitura; nada salvo). Anexa a sela de <sela.blend>
ao lobo de <Anim.blend> (modificador de armadura no rig do lobo), mede por quadro a penetracao do corpo do lobo na sela (distancia
com sinal dos vertices de baixo da sela ate a pele/pelo do lobo; negativo = o lobo atravessa a sela) e renderiza 3 vistas.
Uso: blender -b <Anim.blend> -P m3b_sela_marcha.py -- <sela.blend> <saida_dir> <rotulo> [clipes] [passo=2]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]; SELA_BLEND = os.path.abspath(A[0]); OUT = os.path.abspath(A[1]); ROT = A[2]
CLIPES = (A[3] if len(A) > 3 else "Andar,Trote,Corrida,Partida,Freada,Salto,Impacto").split(","); PASSO = int(A[4]) if len(A) > 4 else 2
os.makedirs(OUT, exist_ok=True); R = math.radians; sc = bpy.context.scene
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
with bpy.data.libraries.load(SELA_BLEND) as (src, dst): dst.objects = ["Lobo_Ancestral_Sela"]
sela = dst.objects[0]; sc.collection.objects.link(sela); sela.parent = arm
for m in list(sela.modifiers): sela.modifiers.remove(m)
md = sela.modifiers.new("Armature", "ARMATURE"); md.object = arm
for o in sc.objects:
    if o.type == "MESH" and o.name not in ("Lobo_Ancestral_LOW", "Lobo_Ancestral_Sela"): o.hide_render = True
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0)); ch = bpy.context.active_object
mc = bpy.data.materials.new("_chao"); mc.use_nodes = True; nt = mc.node_tree; bs = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 200; ck.inputs["Color1"].default_value = (0.55, 0.52, 0.45, 1); ck.inputs["Color2"].default_value = (0.36, 0.34, 0.29, 1)
tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["UV"], ck.inputs["Vector"]); nt.links.new(ck.outputs["Color"], bs.inputs["Base Color"]); ch.data.materials.append(mc)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.64, 0.66, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.8; so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (R(48), 0, R(30))
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
sc.render.resolution_x, sc.render.resolution_y = 480, 360; sc.render.image_settings.file_format = "PNG"
VISTAS = {"lado": (-90, 6, 24, (0, -1.0, 4.2)), "34": (-40, 14, 24, (0, -1.0, 4.2)), "tras": (180, 10, 22, (0, -0.5, 4.4))}
def cam_(az, el, dist, alvo):
    al = V(alvo); cam.location = al + V((math.sin(R(az)) * math.cos(R(el)), -math.cos(R(az)) * math.cos(R(el)), math.sin(R(el)))) * dist
    cam.rotation_euler = (al - cam.location).to_track_quat("-Z", "Y").to_euler()
baixo = [v.index for v in sela.data.vertices if v.normal.z < -0.3]          # face de baixo da sela (contato com o lobo)
res = {}
for clipe in CLIPES:
    act = bpy.data.actions.get("Lobo_" + clipe)
    if not act: print("FALTA", clipe); continue
    arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); pen = []; pasta = os.path.join(OUT, clipe); os.makedirs(pasta, exist_ok=True)
    for f in range(f0, f1 + 1):
        sc.frame_set(f); bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
        el = LO.evaluated_get(dg); ml = el.to_mesh(); bl = BVHTree.FromPolygons([LO.matrix_world @ v.co for v in ml.vertices], [tuple(p.vertices) for p in ml.polygons]); el.to_mesh_clear()
        es = sela.evaluated_get(dg); ms = es.to_mesh(); W = sela.matrix_world
        d = []
        for i in baixo:
            p = W @ ms.vertices[i].co; loc, nor, _, dist = bl.find_nearest(p)
            if loc is None: continue
            d.append((p - loc).dot(nor))
        es.to_mesh_clear(); d = np.array(d)
        pen.append({"f": f, "min": round(float(d.min()), 3), "frac_dentro_005": round(float((d < -0.05).mean()), 4)})
        if (f - f0) % PASSO == 0:
            for vista, v in VISTAS.items():
                cam_(*v); sc.render.filepath = os.path.join(pasta, "%s_%03d.png" % (vista, f)); bpy.ops.render.render(write_still=True)
    res[clipe] = {"quadros": f1 - f0 + 1, "penetracao_min": min(x["min"] for x in pen), "frac_max_dentro_005": max(x["frac_dentro_005"] for x in pen), "por_quadro": pen}
    print("SELA_CLIPE", ROT, clipe, res[clipe]["penetracao_min"], res[clipe]["frac_max_dentro_005"], flush=True)
json.dump(res, open(os.path.join(OUT, "sela_marcha_%s.json" % ROT), "w"), indent=0); print("SELA_MARCHA_OK")
