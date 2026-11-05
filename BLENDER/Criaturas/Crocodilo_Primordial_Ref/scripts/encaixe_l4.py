"""Lote 4, etapa 1: estudo de ENCAIXE do cavaleiro de teste no adulto atual (pose do quadro 0 do Repouso). Marca cristas
(vermelho), sela PROPOSTA (laranja), manequim R15 aproximado (azul) e pontos de apoio das maos/pes (verde). Mede a folga
de cada parte do manequim ate a pele (negativa = atravessa). Renderiza frente/lado/topo/3-4 e closes das cristas, com e
sem cavaleiro. Nao salva o .blend.
Uso: blender -b CR_Crocodilo_Anim.blend -P encaixe_l4.py -- <saida_dir> [z_quadril_sobre_sela] [sem_sela]"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V, Matrix as M
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manequim_r15 as mq
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
DZ = float(A[1]) if len(A) > 1 else 0.35; SEM_SELA = len(A) > 2 and A[2] == "sem_sela"
sc = bpy.context.scene; croc = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]; cam = sc.camera; cd = cam.data
for pb in croc.pose.bones:
    for c in pb.constraints: c.mute = True
for o in sc.objects:
    if o.type in ("EMPTY", "ARMATURE"): o.hide_render = True
croc.animation_data.action = bpy.data.actions["Croc_Repouso"]; croc.animation_data.action_slot = bpy.data.actions["Croc_Repouso"].slots[0]
sc.frame_set(1); bpy.context.view_layer.update()
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0)); chao = bpy.context.object
m = bpy.data.materials.new("M_Chao"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 200; ck.inputs["Color1"].default_value = (0.55, 0.55, 0.56, 1)
ck.inputs["Color2"].default_value = (0.36, 0.36, 0.38, 1); nt.links.new(ck.outputs["Color"], b.inputs["Base Color"]); chao.data.materials.append(m)
# ------------------------------------------------------------------ cristas: vertices do dorso acima da vizinhanca
dg = bpy.context.evaluated_depsgraph_get(); ev = lo.evaluated_get(dg); mm = ev.to_mesh()
co = np.array([lo.matrix_world @ v.co for v in mm.vertices]); ev.to_mesh_clear()
dor = co[(np.abs(co[:, 0]) < 2.2) & (co[:, 1] > -10.5) & (co[:, 1] < 1.0) & (co[:, 2] > 4.3)]
cristas = []
for p in dor:
    viz = dor[np.linalg.norm(dor[:, :2] - p[:2], axis=1) < 0.7]
    if p[2] - np.median(viz[:, 2]) > 0.16 and p[2] >= viz[:, 2].max() - 1e-4: cristas.append(p)
cristas = np.array(cristas)
mc = bpy.data.materials.new("TESTE_M_Crista"); mc.use_nodes = True; mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.05, 0.05, 1)
mc.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (0.9, 0.05, 0.05, 1); mc.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.6
for p in cristas:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=tuple(p), segments=10, ring_count=6); bpy.context.object.data.materials.append(mc)
print("CRISTAS", len(cristas), "y", round(float(cristas[:, 1].min()), 2), "..", round(float(cristas[:, 1].max()), 2), "z max", round(float(cristas[:, 2].max()), 2))
# ------------------------------------------------------------------ sela PROPOSTA + manequim sentado
sela, z_topo_c, z_topo_max, z_fundo_max = mq.criar_sela(croc, lo)
mq.segue_osso(sela, croc)
if SEM_SELA: sela.hide_render = True
ra, ob, alvos = mq.criar()
z_base = (z_topo_c if not SEM_SELA else float(cristas[np.abs(cristas[:, 1] - mq.ASSENTO_Y) < 1.3][:, 2].max())) + DZ
Mq = mq.assento_mundo(croc, z_base - croc.pose.bones[mq.OSSO_ASSENTO].head.z * 0 - 0.0)
# assento_mundo recebe z no espaco do osso em descanso: o quadro 0 do Repouso esta praticamente na pose de descanso
mq.sentado(ra, alvos, Mq); bpy.context.view_layer.update()
mv = bpy.data.materials.new("TESTE_M_Apoio"); mv.use_nodes = True; mv.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.85, 0.2, 1)
for (tipo, ponta), e in alvos.items():
    if tipo == "IK":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=e.matrix_world.translation, segments=10, ring_count=6); bpy.context.object.data.materials.append(mv)
bvh = mq.bvh_croc(lo); amo = mq.amostras_partes(0.2)
fol = mq.folgas(ra, amo, bvh)
# folga da sela: vertices do fundo contra a pele
dg = bpy.context.evaluated_depsgraph_get(); fs_ = []
for v in sela.data.vertices:
    w = sela.matrix_world @ v.co; loc, nor, _, d = bvh.find_nearest(w, 5.0)
    if loc is not None: fs_.append(d if nor.dot(w - loc) >= 0 else -d)
res = {"z_quadril": round(Mq.translation.z, 3), "sela_topo_centro": round(z_topo_c, 3), "sela_topo_max": round(z_topo_max, 3),
       "sela_fundo_max": round(z_fundo_max, 3), "sela_folga_min": round(min(fs_), 3), "folgas_manequim": fol,
       "cristas": {"n": len(cristas), "y_min": round(float(cristas[:, 1].min()), 2), "y_max": round(float(cristas[:, 1].max()), 2),
                   "z_max": round(float(cristas[:, 2].max()), 2), "x_abs_max": round(float(np.abs(cristas[:, 0]).max()), 2)},
       "pes_mundo": {k[1]: [round(c, 2) for c in e.matrix_world.translation] for k, e in alvos.items() if k[0] == "IK"},
       "cabeca_topo_z": round((ra.matrix_world @ ra.pose.bones["Head"].tail).z, 2), "sem_sela": SEM_SELA}
json.dump(res, open(os.path.join(OUT, "encaixe%s.json" % ("_sem_sela" if SEM_SELA else "")), "w"), indent=1)
print("ENCAIXE", json.dumps(res))
# ------------------------------------------------------------------ renders
Y0 = mq.ASSENTO_Y
CAMS = {"frente": (V((0, -30, 12)), V((0, Y0, 5.5)), 40, None), "lado": (V((26, Y0, 7)), V((0, Y0, 5.0)), 40, None),
        "topo": (V((0, Y0, 40)), V((0, Y0 + 0.01, 0)), 0, 13), "34": (V((15, -17, 12)), V((0, Y0, 5.0)), 34, None),
        "tras": (V((-6, 22, 11)), V((0, Y0, 5.5)), 40, None),
        "close_lado": (V((11, -6.5, 7.5)), V((0, -6.0, 5.6)), 40, None), "close_topo": (V((0, -5.5, 30)), V((0, -5.49, 0)), 0, 8)}
sc.render.resolution_x, sc.render.resolution_y = 960, 540; sc.eevee.taa_render_samples = 32
tag = "_sem_sela" if SEM_SELA else ""
for vis in ("com", "sem"):
    for o_ in (ob,): o_.hide_render = (vis == "sem")
    for cn, (p, a, lente, orto) in CAMS.items():
        cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler()
        if cn.endswith("topo"): cam.rotation_euler = (0, 0, math.pi / 2)
        if orto: cd.type = "ORTHO"; cd.ortho_scale = orto
        else: cd.type = "PERSP"; cd.lens = lente
        sc.render.filepath = os.path.join(OUT, "encaixe%s_%s_%s.png" % (tag, vis, cn)); bpy.ops.render.render(write_still=True)
print("ENCAIXE_OK")
