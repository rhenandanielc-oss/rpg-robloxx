"""S2: cavaleiro de TESTE sentado (preso ao osso Coluna1 no ponto do assento) nos clipes reaproveitados do leao: folga minima
do manequim contra o leao e contra a sela, por clipe. So leitura. Uso: blender -b Leao_Solar_Ref_S2_montaria.blend -P s2_04_montado.py -- <saida.json>"""
import bpy, sys, os, json
from mathutils import Vector as V, Matrix as M
from mathutils.bvhtree import BVHTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(RAIZ, "..", "s1"))
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import s1_01_sela_leao as sl
A = sys.argv[sys.argv.index("--") + 1:]; sc = bpy.context.scene
arm = bpy.data.objects["Leao_Solar_Rig"]; lo = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; sela = bpy.data.objects[sl.NOME]
ra = bpy.data.objects["TESTE_Manequim_R15aprox_Rig"]; ra.animation_data.action = bpy.data.actions["DEMO_Cav_Sentado"]
DZ = 0.10; arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
def bvh_obj(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); m = ev.to_mesh(); W = o.matrix_world
    vs = [W @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]; ev.to_mesh_clear(); return BVHTree.FromPolygons(vs, fs)
# pose sentada assada (DEMO_Cav_Sentado, quadro 1) relativa ao osso: guarda o quadril no espaco de Coluna1 e reposiciona o rig inteiro
sc.frame_set(1); bpy.context.view_layer.update()
BL = arm.data.bones["Coluna1"].matrix_local
def osso(): return arm.matrix_world @ arm.pose.bones["Coluna1"].matrix @ BL.inverted()
REL = osso().inverted() @ ra.matrix_world
amo = mq.amostras_partes(0.2); res = {}
for nome in ("Repouso_Vigilante", "Andar", "Trote", "Corrida", "Virar_E", "Frenagem"):
    act = bpy.data.actions["Leao_" + nome]; arm.animation_data.action = act; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    pl, ps = {}, {}
    for f in range(f0, f1 + 1, 2):
        sc.frame_set(f); bpy.context.view_layer.update(); ra.matrix_world = osso() @ REL; bpy.context.view_layer.update()
        fo = mq.folgas(ra, amo, bvh_obj(lo), passo=2); fs = mq.folgas(ra, amo, bvh_obj(sela), raio=3.0, passo=2)
        for k, v in fo.items():
            if v < pl.get(k, (9, 0))[0]: pl[k] = (v, f)
        for k, v in fs.items():
            if v < ps.get(k, (9, 0))[0]: ps[k] = (v, f)
    res[nome] = {"leao_min": min(pl.values()), "leao_parte": min(pl, key=lambda k: pl[k][0]), "sela_min": min(ps.values()), "sela_parte": min(ps, key=lambda k: ps[k][0])}
    print("MONTADO", nome, json.dumps(res[nome]), flush=True)
json.dump(res, open(A[0], "w"), indent=1); print("MONTADO_OK")
