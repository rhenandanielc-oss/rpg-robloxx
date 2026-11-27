"""Montaria M2 r2 (27/11/2026): busca da POSE SENTADA do manequim de teste na sela do Cerbero (repouso), sem tocar na sela.
Na r1 as coxas entravam ~0,22 na sela e o quadril ficava 0,40 acima do assento. Varre: altura e posicao (frente/tras) do quadril,
abertura e altura dos pes nos apoios. Nota: menor folga com sinal (corpo + sela) e distancia do quadril (LowerTorso) ao assento.
Escolhe a melhor pose sem penetracao (ou a de menor penetracao) com o quadril o mais perto possivel do assento. So leitura.
Uso: blender -b -t 1 montaria/CB_M1_sela.blend -P montaria/m2_sentado_busca.py -- <saida.json>"""
import bpy, sys, os, json, math, itertools
from mathutils import Vector as V, Matrix as M, Quaternion as Q
from mathutils.bvhtree import BVHTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import m1_sela_cerbero as sl
A = sys.argv[sys.argv.index("--") + 1:]
arm = bpy.data.objects["Cerbero_Rig"]; sela = bpy.data.objects[sl.NOME]
CORPO = [bpy.data.objects["Cerbero_Corpo"], bpy.data.objects["Cerbero_Cabecas"]]
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for c in pb.constraints: c.mute = True
if arm.animation_data: arm.animation_data.action = None
bpy.context.view_layer.update()
def bvh_obj(os_):
    dg = bpy.context.evaluated_depsgraph_get(); vs, fs = [], []
    for o_ in os_:
        ev = o_.evaluated_get(dg); m = ev.to_mesh(); W = o_.matrix_world; k = len(vs)
        vs += [W @ v.co for v in m.vertices]; fs += [tuple(i + k for i in p.vertices) for p in m.polygons]; ev.to_mesh_clear()
    return BVHTree.FromPolygons(vs, fs)
BC, BS = bvh_obj(CORPO), bvh_obj([sela])
SENT0 = {tuple(k.split("|")): tuple(v) for k, v in json.loads(sela["sentado"]).items()}
hit = BS.ray_cast(V((sl.XC, sl.ASSENTO_Y, 25)), V((0, 0, -1))); Z_SEAT = hit[0].z
ra, ob, alvos = mq.criar()
for pb in ra.pose.bones:
    for c in pb.constraints: c.mute = False
amo = mq.amostras_partes(0.25)
def avaliar(dz, dy, ax, az, inclina=8.0):
    mq.SENTADO = dict(SENT0)
    for lado, s in (("LeftFoot", 1), ("RightFoot", -1)):
        x, y, z = SENT0[("IK", lado)]; mq.SENTADO[("IK", lado)] = (x + s * ax, y, z + az - dz)
    Mq = M.Translation(V((sl.XC, sl.ASSENTO_Y + dy, Z_SEAT + sl.DZ_QUADRIL + dz)))
    mq.aplicar(ra, alvos, mq.estado_sentado(Mq, inclina))
    for lado_ in ("Left", "Right"): ra.pose.bones[lado_ + "LowerLeg"].rotation_quaternion = Q(V((1, 0, 0)), math.radians(15))
    bpy.context.view_layer.update()
    fc = mq.folgas(ra, amo, BC, raio=3.0); fs = mq.folgas(ra, amo, BS, raio=3.0)
    pior = min(min(fc.values()), min(fs.values()))
    return pior, fs["LowerTorso"], fc, fs
res = []
for dz, dy, ax, az in itertools.product([-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3], [-0.3, -0.15, 0.0, 0.15, 0.3], [0.0, 0.15, 0.3, 0.45], [0.0, 0.15]):
    pior, gap, fc, fs = avaliar(dz, dy, ax, az)
    res.append({"dz": dz, "dy": dy, "ax": ax, "az": az, "pior": round(pior, 3), "gap_quadril": round(gap, 3)})
ok = [r for r in res if r["pior"] >= -0.03]
melhor = min(ok, key=lambda r: (r["gap_quadril"], -r["pior"])) if ok else max(res, key=lambda r: r["pior"])
pior, gap, fc, fs = avaliar(melhor["dz"], melhor["dy"], melhor["ax"], melhor["az"])
print("MELHOR", json.dumps(melhor), "corpo", fc, "sela", fs, flush=True)
r1 = avaliar(0.05, 0.0, 0.0, 0.0)
print("R1_EQUIV pior %.3f gap %.3f" % (r1[0], r1[1]), flush=True)
json.dump({"melhor": melhor, "z_assento": Z_SEAT, "folgas_corpo": fc, "folgas_sela": fs, "todas": res}, open(A[0], "w"), indent=1)
print("BUSCA_OK")
