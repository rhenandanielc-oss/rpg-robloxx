"""Montaria M2: cavaleiro de TESTE sentado (preso ao osso Coluna2 no ponto do assento) nos clipes de locomocao/vida do urso
ja aprovados: folga minima do manequim contra o urso e contra a sela, por clipe. Adaptado do s2_04_montado.py do Leao Solar.
So leitura. Uso: blender -b CR_Urso_v2_M2_montaria.blend -P m2_montado.py -- <saida.json>"""
import bpy, sys, os, json
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import m1_sela_urso as sl
A = sys.argv[sys.argv.index("--") + 1:]; sc = bpy.context.scene
arm = bpy.data.objects["Urso_Rig"]; sela = bpy.data.objects[sl.NOME]
lo = [bpy.data.objects[n] for n in ("Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Cabeca")]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
ra = bpy.data.objects["TESTE_Manequim_R15aprox_Rig"]; ra.animation_data.action = bpy.data.actions["DEMO_Cav_Sentado"]
arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
def bvh_obj(o):
    dg = bpy.context.evaluated_depsgraph_get(); vs, fs = [], []
    for o_ in (o if isinstance(o, (list, tuple)) else [o]):
        ev = o_.evaluated_get(dg); m = ev.to_mesh(); W = o_.matrix_world; k = len(vs)
        vs += [W @ v.co for v in m.vertices]; fs += [tuple(i + k for i in p.vertices) for p in m.polygons]; ev.to_mesh_clear()
    return BVHTree.FromPolygons(vs, fs)
sc.frame_set(1); bpy.context.view_layer.update()
BL = arm.data.bones["Coluna2"].matrix_local
def osso(): return arm.matrix_world @ arm.pose.bones["Coluna2"].matrix @ BL.inverted()
REL = osso().inverted() @ ra.matrix_world
amo = mq.amostras_partes(0.2); res = {}
for nome in ("Repouso", "Observar", "Andar", "Corrida", "Arrancada", "Frenagem", "VirarE", "VirarD", "Rugir"):
    act = bpy.data.actions.get("Urso_" + nome)
    if not act: continue
    arm.animation_data.action = act; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    pl, ps = {}, {}
    for f in range(f0, f1 + 1, 2):
        sc.frame_set(f); bpy.context.view_layer.update(); ra.matrix_world = osso() @ REL; bpy.context.view_layer.update()
        fo = mq.folgas(ra, amo, bvh_obj(lo), passo=2); fs = mq.folgas(ra, amo, bvh_obj(sela), raio=3.0, passo=2)
        for k, v in fo.items():
            if v < pl.get(k, (9, 0))[0]: pl[k] = (v, f)
        for k, v in fs.items():
            if v < ps.get(k, (9, 0))[0]: ps[k] = (v, f)
    res[nome] = {"urso_min": min(pl.values()), "urso_parte": min(pl, key=lambda k: pl[k][0]), "sela_min": min(ps.values()), "sela_parte": min(ps, key=lambda k: ps[k][0])}
    print("MONTADO", nome, json.dumps(res[nome]), flush=True)
json.dump(res, open(A[0], "w"), indent=1); print("MONTADO_OK")
