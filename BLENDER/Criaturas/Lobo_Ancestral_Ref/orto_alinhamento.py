"""Vistas ORTOGRAFICAS de alinhamento (frente, cima, lado) com a linha central marcada (vermelho, x = 0) e as marcas dos
4 apoios (amarelo, centro das patas a z<0,3). So leitura (nao salva). Pose: repouso do rig ou um quadro de acao.
Uso: blender -b <blend> -P orto_alinhamento.py -- <saida_dir> <prefixo> [acao] [quadro]"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); PRE = A[1]; os.makedirs(OUT, exist_ok=True)
ACAO = A[2] if len(A) > 2 else None; Q = int(A[3]) if len(A) > 3 else 0
sc = bpy.context.scene
LO = bpy.data.objects.get("Lobo_Ancestral_LOW") or bpy.data.objects.get("Lobo_Meshy")
arm = next((o for o in sc.objects if o.type == "ARMATURE"), None)
for o in sc.objects:
    if (o.type == "MESH" and o is not LO) or o.type == "EMPTY": o.hide_render = True
if arm:
    for pb in arm.pose.bones:
        for c in pb.constraints: c.mute = True
        pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    if ACAO:
        act = bpy.data.actions[ACAO]; arm.animation_data.action = act
        try: arm.animation_data.action_slot = act.slots[0]
        except Exception: pass
        sc.frame_set(int(act.frame_range[0]) + Q)
bpy.context.view_layer.update()
def mat(nome, cor):
    m = bpy.data.materials.new(nome)
    if m.node_tree is None: m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Emission Color"].default_value = (*cor, 1); b.inputs["Emission Strength"].default_value = 4.0; return m
def caixa(nome, c, d, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.name = nome; o.scale = d; o.data.materials.append(m); return o
VERM, AMAR = mat("Linha", (1, 0.05, 0.05)), mat("Apoio", (1, 0.85, 0.05))
caixa("LinhaFrente", (0, -12, 4.5), (0.035, 0.01, 9.5), VERM)
caixa("LinhaCima", (0, 0, 9.6), (0.035, 16, 0.01), VERM)
caixa("LinhaChao", (0, 0, 0.003), (0.035, 16, 0.006), VERM)
dg = bpy.context.evaluated_depsgraph_get(); ev = LO.evaluated_get(dg).data
co = np.array([LO.matrix_world @ v.co for v in ev.vertices]); x, y, z = co.T
pe = z < 0.30; ym = (y[pe].min() + y[pe].max()) / 2
for lado, sx in (("E", 1), ("D", -1)):
    for par, cnd in (("dian", y < ym), ("tras", y >= ym)):
        q = pe & (x * sx > 0.1) & cnd
        if q.any():
            c = co[q].mean(axis=0); caixa("Apoio" + lado + par, (c[0], c[1], 9.7), (0.18, 0.18, 0.01), AMAR)
            caixa("ApoioF" + lado + par, (c[0], -12.1, 0.05), (0.18, 0.01, 0.1), AMAR)
for o in sc.objects:
    if o.name.startswith("Plane"): o.hide_render = False
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12; sc.render.resolution_x = sc.render.resolution_y = 1000
cam = sc.camera; camd = cam.data; camd.type = "ORTHO"
for nome, pos, rot, esc in (("frente", V((0, -30, 4.3)), (math.radians(90), 0, 0), 9.5), ("cima", V((0, -0.5, 30)), (0, 0, 0), 15.0),
                            ("lado", V((30, -0.5, 4.3)), (math.radians(90), 0, math.radians(90)), 15.0)):
    camd.ortho_scale = esc; cam.location = pos; cam.rotation_euler = rot
    sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (PRE, nome)); bpy.ops.render.render(write_still=True)
print("ORTO_OK", PRE)
