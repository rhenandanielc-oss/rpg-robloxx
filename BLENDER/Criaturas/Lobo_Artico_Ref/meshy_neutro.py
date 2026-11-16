"""Pose NEUTRA do Lobo Artico do Meshy: a referencia tem a cabeca virada para a camera e o Meshy copiou isso.
Gira cabeca+pescoco em torno de um pivo na base do pescoco (eixo vertical), com peso suave ao longo do pescoco,
para o focinho apontar para -Y. O resto do corpo nao se move. Depois recentra X e confere a cernelha.
Uso: blender -b meshy/CR_LoboArtico_meshy_norm.blend -P meshy_neutro.py -- <saida_dir> [frac_pivo=0.28]"""
import bpy, sys, os, math
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); FP = float(a[1]) if len(a) > 1 else 0.28
ob = bpy.data.objects["CR_LoboArtico_Meshy"]; me = ob.data
n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
lo, hi = co.min(0), co.max(0); L = hi[1] - lo[1]
# 0) eixo do tronco = do meio das patas dianteiras ao meio das traseiras (pes no chao), alinhado a +Y
pes = co[co[:, 2] < 0.30][:, :2]; corte = np.median(pes[:, 1])
fr, tr_ = pes[pes[:, 1] < corte].mean(0), pes[pes[:, 1] >= corte].mean(0)
cen = (fr + tr_) / 2; eixo = (tr_ - fr) / np.linalg.norm(tr_ - fr)
yaw = math.atan2(eixo[0], eixo[1])                                # desvio do tronco em relacao a +Y
c0, s0 = math.cos(yaw), math.sin(yaw)
rx, ry = co[:, 0] - cen[0], co[:, 1] - cen[1]
co[:, 0] = cen[0] + rx * c0 - ry * s0; co[:, 1] = cen[1] + rx * s0 + ry * c0
print("NEUTRO tronco_girado_graus", round(math.degrees(yaw), 1))
lo, hi = co.min(0), co.max(0); L = hi[1] - lo[1]
nariz = co[np.argmin(co[:, 1])]
def fatia(y0, y1): return co[(co[:, 1] >= y0) & (co[:, 1] <= y1)]
corpo = fatia(lo[1] + 0.45 * L, lo[1] + 0.55 * L); cx = (corpo[:, 0].min() + corpo[:, 0].max()) / 2
yp = lo[1] + FP * L; sp = fatia(yp - 0.1, yp + 0.1)
piv = np.array([cx, yp, (sp[:, 2].min() + sp[:, 2].max()) / 2], np.float32)
ang = math.atan2(nariz[0] - piv[0], piv[1] - nariz[1])           # desvio do focinho em relacao a -Y (radianos)
print("NEUTRO nariz", np.round(nariz, 2), "pivo", np.round(piv, 2), "desvio_graus", round(math.degrees(ang), 1))
d = nariz[:2] - piv[:2]; Ld = np.linalg.norm(d); d = d / Ld
t = ((co[:, :2] - piv[:2]) @ d) / Ld                              # 0 no pivo, 1 no focinho
def suave(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
w = suave(t / 0.55) * suave((co[:, 2] - (piv[2] - 1.8)) / 1.2)
th = -ang * w; c, s = np.cos(th), np.sin(th)
rx, ry = co[:, 0] - piv[0], co[:, 1] - piv[1]
co[:, 0] = piv[0] + rx * c - ry * s; co[:, 1] = piv[1] + rx * s + ry * c
co[:, 0] -= cx
# 2) cauda centralizada: desloca em X a partir da raiz (peso suave), sem mexer na garupa
lo, hi = co.min(0), co.max(0); L = hi[1] - lo[1]
yr = lo[1] + 0.80 * L; desvio = co[co[:, 1] > lo[1] + 0.90 * L][:, 0].mean()
wc = suave((co[:, 1] - yr) / (0.12 * L)) * suave((4.8 - co[:, 2]) / 0.8)
co[:, 0] -= desvio * wc
print("NEUTRO cauda_desvio_x", round(float(desvio), 2))
me.vertices.foreach_set("co", co.ravel()); me.update()
lo, hi = co.min(0), co.max(0)
nz = co[np.argmin(co[:, 1])]
print("NEUTRO depois nariz", np.round(nz, 2), "bbox", np.round(lo, 2), np.round(hi, 2), "vertices_movidos", int((w > 0.01).sum()), "de", n)
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_meshy_neutro.blend"))
print("NEUTRO_OK")
