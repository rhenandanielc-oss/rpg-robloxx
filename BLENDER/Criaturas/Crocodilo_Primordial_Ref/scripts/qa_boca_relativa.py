"""QA da mordida durante o movimento: a Mandibula e filha do Pescoco2 (nao da Cabeca). Se a Cabeca gira e a mandibula nao
acompanha, os dentes deslizam (lateral) ou cruzam (fecham alem do fechado). Mede, por clipe, a mandibula EM RELACAO A
CABECA a partir dos JSON: 'fecha_alem' = graus alem da boca fechada (negativo = dentes de cima passam dos de baixo),
'lateral' = desvio fora da dobradica (dentes raspando de lado), 'desloca' = deslocamento da ponta do queixo em relacao a
cabeca que nao vem da abertura (studs). Uso: blender -b CR_Crocodilo_Rig.blend -P qa_boca_relativa.py -- <clipes_dir> [saida.json]"""
import bpy, sys, os, json, glob, math
from mathutils import Quaternion as Q, Vector as V, Matrix as M
A = sys.argv[sys.argv.index("--") + 1:]; DIR = A[0]
arm = bpy.data.objects["CR_Croc_Rig"]; BD = arm.data.bones
FECHADA = -1.0 * math.radians(arm["ang_boca"])
def mat(o, s, q):
    x, y, z, w, tx, ty, tz = s[q * 7:q * 7 + 7]; return M.Translation(V((tx, ty, tz))) @ Q((w, x, y, z)).to_matrix().to_4x4()
Rh, Rj = BD["Cabeca"].matrix_local, BD["Mandibula"].matrix_local
ponta = BD["Mandibula"].tail_local.copy()
res = {}
for f in sorted(glob.glob(os.path.join(DIR, "Crocodilo_*.json"))):
    d = json.load(open(f)); nome = d["nome"].replace("Crocodilo_", ""); o = d["ossos"]
    pior = {"fecha_alem": 0.0, "lateral": 0.0, "desloca": 0.0}
    for q in range(d["quadros"]):
        # mesmo pai: pose no espaco do pai = rest_rel @ basis; delta em espaco de armadura (pai em descanso)
        Gh = Rh @ mat("Cabeca", o["Cabeca"], q) @ Rh.inverted(); Gj = Rj @ mat("Mandibula", o["Mandibula"], q) @ Rj.inverted()
        rel = (Gh.inverted() @ Gj)                       # mandibula vista da cabeca (descanso = identidade)
        qr = rel.to_quaternion()
        # torcao em X (dobradica) e balanco (resto)
        tw = Q((qr.w, qr.x, 0, 0)).normalized(); sw = qr @ tw.inverted()
        ang_x = 2 * math.atan2(tw.x, tw.w)
        lateral = math.degrees(2 * math.acos(min(1.0, abs(sw.w))))
        fecha = math.degrees(ang_x - FECHADA)            # >0 = aberta alem do fechado; <0 = fecha alem (cruza)
        # deslocamento da ponta do queixo que nao vem da abertura pura em X
        pura = (Gh @ M.Translation(Rj.translation) @ M.Rotation(ang_x, 4, "X") @ M.Translation(-Rj.translation))
        desl = ((Gj @ ponta) - (pura @ ponta)).length
        pior["fecha_alem"] = min(pior["fecha_alem"], fecha); pior["lateral"] = max(pior["lateral"], lateral); pior["desloca"] = max(pior["desloca"], desl)
    res[nome] = {k: round(v, 3) for k, v in pior.items()}
    print("BOCA %-24s fecha_alem %7.2f graus | lateral %5.2f graus | desloca %.3f studs" % (nome, pior["fecha_alem"], pior["lateral"], pior["desloca"]), flush=True)
if len(A) > 1: json.dump(res, open(A[1], "w"), indent=1)
