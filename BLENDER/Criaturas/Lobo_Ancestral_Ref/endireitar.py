"""Pose neutra do lobo do Meshy (normalizado): cabeca/pescoco girados de volta para -Y (rotacao rigida em torno de um
eixo vertical na base do pescoco, com transicao suave) e cauda desenrolada pela linha central (preserva o comprimento,
mantem a altura). As patas ficam como estao (passada da pintura) - registrar como diferenca.
v2 (03/11): pivo da cabeca e eixo da cauda na LINHA MEDIA DO TRONCO (a v1 centrava a cauda em x = 0 com o tronco em
x ~ -0,65 -> cauda deslocada +0,65 para o lado); linha da cauda pelo meio do contorno da faixa central (o leque assimetrico
puxava a media); transicao do giro da cabeca opcional so no pescoco ("pescoco") para nao arrastar a frente da juba.
Uso: blender -b <normalizado.blend> -P endireitar.py -- <saida.blend> [ang_cabeca_graus|auto] [juba|largo|pescoco]"""
import bpy, sys, os, math
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; SAIDA = os.path.abspath(A[0])
ob = bpy.data.objects["Lobo_Meshy"]; me = ob.data; n = len(me.vertices)
co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co[:, 0].copy(), co[:, 1].copy(), co[:, 2].copy()
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

# ---------------- linha media do tronco (meio do contorno das fatias acima das patas, sem cabeca e sem cauda)
meios = [(x[m].min() + x[m].max()) / 2 for a in np.arange(-4.4, 2.4, 0.4) for m in [(y >= a) & (y < a + 0.4) & (z > 4.2)] if m.sum() > 200]
XC = float(np.median(meios)); print("LINHA_MEDIA_TRONCO x", round(XC, 3), "fatias", len(meios))
MODO = A[2] if len(A) > 2 else "juba"
# ---------------- cabeca
P = np.array([XC, -2.9])                                     # base do pescoco, sobre a linha media
cab = (z > 6.4) & (z < 7.6) & (y < -4.0)
d = np.hypot(x - P[0], y - P[1]); d[~cab] = -1; i = int(np.argmax(d))
nariz = co[i]; ang_atual = math.degrees(math.atan2(nariz[0] - P[0], -(nariz[1] - P[1])))   # 0 = olhando para -Y
ANG = ang_atual if (len(A) < 2 or A[1] == "auto") else float(A[1])
print("NARIZ", nariz.round(2), "desvio_cabeca_graus", round(ang_atual, 1), "corrigindo", round(ANG, 1))
if MODO == "juba": w = suave((-2.2 - y) / 1.9) * suave((z - 4.5) / 1.7)
elif MODO == "largo": w = suave((-1.2 - y) / 3.2) * suave((z - 3.6) / 2.8)     # transicao longa: dilui o arrasto do peito
else: w = suave((-2.6 - y) / 1.4) * suave((z - 5.7) / 1.1)
th = -np.radians(ANG) * w                                    # gira de volta (sentido oposto ao desvio)
c, s = np.cos(th), np.sin(th); dx, dy = x - P[0], y - P[1]
x1 = P[0] + dx * c - dy * s; y1 = P[1] + dx * s + dy * c
# conferencia: o nariz deve ir para x ~ P.x
print("NARIZ_DEPOIS", round(float(x1[i]), 2), round(float(y1[i]), 2))
x, y = x1, y1

# ---------------- cauda: linha central por fatias de y (so vertices da cauda), desenrolada em linha reta
Y0 = 2.6; passo = 0.25; ys = np.arange(Y0, y.max() + passo, passo)
cx, cz, ok = [], [], []
for a in ys:
    m = (y >= a - passo) & (y < a + passo) & (z > (2.6 if a < 3.4 else 0.6))
    if m.sum() > 30:                                          # faixa central em z (o leque lateral nao puxa o eixo)
        zc = np.median(z[m]); m = m & (np.abs(z - zc) < 0.35)
    ok.append(m.sum() > 30); cx.append((x[m].min() + x[m].max()) / 2 if m.sum() else np.nan); cz.append(z[m].mean() if m.sum() else np.nan)
cx = np.array(cx); ys_ok = ys[np.array(ok)]; cx = cx[np.array(ok)]
cx = np.convolve(np.pad(cx, 2, mode="edge"), np.ones(5) / 5, mode="valid")           # suaviza a linha central
print("CAUDA_CENTRO", [(round(float(a), 2), round(float(b), 2)) for a, b in zip(ys_ok[::4], cx[::4])])
seg = np.hypot(np.diff(cx), np.diff(ys_ok)); s_arc = np.concatenate([[0], np.cumsum(seg)])
tx = np.gradient(cx, ys_ok); tl = np.hypot(tx, 1.0); Tx, Ty = tx / tl, 1.0 / tl          # tangente no plano XY
Bx, By = cx[0], ys_ok[0]
mc = y > Y0
yy = np.clip(y[mc], ys_ok[0], ys_ok[-1])
Cx = np.interp(yy, ys_ok, cx); S = np.interp(yy, ys_ok, s_arc); TX = np.interp(yy, ys_ok, Tx); TY = np.interp(yy, ys_ok, Ty)
ox, oy = x[mc] - Cx, y[mc] - yy
o_t = ox * TX + oy * TY; o_n = ox * TY - oy * TX            # componentes ao longo e na normal (direita da tangente)
xn = XC + o_n; yn = By + S + o_t                             # cauda reta sobre a linha media do tronco
wt = suave((y[mc] - Y0) / 0.9) * np.where(y[mc] < 3.4, suave((z[mc] - 1.6) / 0.6), 1.0)
x[mc] = x[mc] + (xn - x[mc]) * wt; y[mc] = y[mc] + (yn - y[mc]) * wt
print("CAUDA_COMPRIMENTO_ARCO", round(float(s_arc[-1]), 2), "ponta_x_antes", round(float(cx[-1]), 2))
co[:, 0], co[:, 1] = x, y
me.vertices.foreach_set("co", co.ravel()); me.update()
vs = co
print("MEDIDAS altura", round(float(z.max()), 2), "comprimento", round(float(y.max() - y.min()), 2), "largura", round(float(x.max() - x.min()), 2))
bpy.ops.wm.save_as_mainfile(filepath=SAIDA)
print("ENDIREITAR_OK")
