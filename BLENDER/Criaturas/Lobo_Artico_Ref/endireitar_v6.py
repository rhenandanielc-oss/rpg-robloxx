"""v6: endireita a cabeca da v5 (low_v5a, preservada) sem mexer no corpo nem na costura.
Diagnostico (review/v5_final/simetria): o cranio do Meshy esta girado ~3,3 graus (plano de simetria medido por espelho +
KDTree) e, alem disso, o focinho/nariz sai ~0,1 para o lado E desse plano.
1) GIRO no pescoco: cada vertice gira em torno do eixo vertical num ponto do plano na altura da costura, com peso
   suave(s/L) pela distancia s a frente do plano da costura (s<=0: corpo e costura intactos). Depois do giro o plano
   de simetria vira x=0.
2) FOCINHO: desloca lateralmente so a frente dos olhos (y < Y0, total em Y1) ate o nariz ficar em x=0. Os aneis dos
   olhos ficam atras de Y0 (giram rigidos com o globo).
O campo de deformacao e uma funcao da POSICAO, aplicado igual a todas as malhas: vertices coincidentes (corte dos
labios, costura, cartoes de pelagem) continuam coincidentes. UV/texturas nao mudam. Pivos do rig_pivos.json
transformados pelo mesmo campo.
Uso: blender -b low_v5a/CR_LoboArtico_LOW.blend -P endireitar_v6.py -- <saida_dir>   (depois: ajuste_r3.py)"""
import bpy, sys, os, json, math, shutil
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.kdtree import KDTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); AQUI = os.path.dirname(SRC)
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); NARIZ = V(json.load(open(os.path.join(AQUI, "meshy", "rosto.json")))["nariz"])
CP, CN = V(PIV["costura"]["ponto"]), V(PIV["costura"]["normal"])
L_PESCOCO, Y0, Y1 = 0.7, -5.85, -6.35
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
for im in bpy.data.images:                                              # texturas: copias proprias da v6
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()
cab = bpy.data.objects["LOW_Cabeca"]
# ---- plano de simetria do cranio (n = (cos phi, sin phi, 0), n.p = d), regiao rigida s > 1.0
P = np.array([v.co[:] for v in cab.data.vertices]); s_ = (P - np.array(CP[:])) @ np.array(CN[:]); Q = P[s_ > 1.0]
kd = KDTree(len(Q))
for i, p in enumerate(Q): kd.insert(p, i)
kd.balance()
def custo(phi, d):
    n = np.array([math.cos(phi), math.sin(phi), 0.0]); M = Q - 2 * (Q @ n - d)[:, None] * n[None]
    return float(np.mean([kd.find(m)[2] for m in M[::3]]))
best = min(((custo(math.radians(a), d), math.radians(a), d) for a in np.arange(-14, 14.1, 1.0) for d in np.arange(-0.8, 0.81, 0.04)))
for st in (0.5, 0.2, 0.05):
    for _ in range(4):
        c0, phi, d = best
        for dp, dd in ((st, 0), (-st, 0), (0, st * 0.04), (0, -st * 0.04)):
            c = custo(phi + math.radians(dp), d + dd)
            if c < best[0]: best = (c, phi + math.radians(dp), d + dd)
c_fim, PHI, D = best; c_ini = custo(0.0, 0.0)
PIVO = V(((D - CP.y * math.sin(PHI)) / math.cos(PHI), CP.y, CP.z))   # ponto do plano na altura da costura
print("V6 plano: giro %.2f graus, d %.3f, pivo x %.3f, custo espelho %.4f -> %.4f" % (math.degrees(PHI), D, PIVO.x, c_ini, c_fim), flush=True)
def giro(p):
    w = suave((p - CP).dot(CN) / L_PESCOCO)
    if w <= 0: return p.copy()
    q = PIVO + Matrix.Rotation(-PHI * w, 3, "Z") @ (p - PIVO); q.x -= PIVO.x * w; return q
DX = -giro(NARIZ).x                                                     # deslocamento do focinho para o nariz ir a x=0
def campo(p):
    q = giro(p)
    q.x += DX * suave((Y0 - q.y) / (Y0 - Y1)) * suave((p - CP).dot(CN) / L_PESCOCO)
    return q
print("V6 nariz x %.3f -> giro %.3f -> focinho %.3f" % (NARIZ.x, giro(NARIZ).x, campo(NARIZ).x), flush=True)
for o in bpy.data.objects:
    if o.type != "MESH": continue
    n = 0
    for v in o.data.vertices:
        q = campo(v.co)
        if (q - v.co).length > 1e-7: v.co = q; n += 1
    o.data.update(); print("V6 movidos", o.name, n, flush=True)
# ---- pivos
for lado, ol in PIV["olhos"].items():
    c = V(ol["centro_globo"]); w = suave((c - CP).dot(CN) / L_PESCOCO)
    ol["centro_globo"] = list(campo(c)); ol["eixo"] = list(Matrix.Rotation(-PHI * w, 3, "Z") @ V(ol["eixo"]))
m = PIV["mandibula"]; pv = campo(V(m["pivo_sugerido"])); pv.x = 0.0; m["pivo_sugerido"] = list(pv)
PIV["endireitar_v6"] = {"giro_pescoco_graus": -math.degrees(PHI), "pivo": list(PIVO), "faixa_pescoco_s": L_PESCOCO,
                        "focinho_dx": DX, "focinho_y": [Y0, Y1], "nariz_depois": list(campo(NARIZ)),
                        "custo_espelho_antes_depois": [c_ini, c_fim],
                        "nota": "campo de deformacao por posicao (corpo/costura intactos); UV/texturas inalteradas"}
json.dump(PIV, open(os.path.join(OUT, "rig_pivos.json"), "w"), indent=1)
oE, oD = V(PIV["olhos"]["E"]["centro_globo"]), V(PIV["olhos"]["D"]["centro_globo"])
print("V6 olhos depois: E %s D %s  meio_x %.3f  dif_y %.3f dif_z %.3f" % (tuple(round(x, 3) for x in oE), tuple(round(x, 3) for x in oD),
      (oE.x + oD.x) / 2, oE.y - oD.y, oE.z - oD.z), flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend")); print("V6_OK", flush=True)
