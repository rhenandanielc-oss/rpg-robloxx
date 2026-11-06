# E4 - corrige SO a transicao cauda-bulbo-gancho (mesmos vertices, UV, material, ossos; sem subdivisao).
# Causas medidas no M0 (04a_diagnostico_ferrao.py):
#  1) 02_ferrao.py normalizava cada fatia de 0,25 pela largura da propria fatia, mas a ponta do Ashwing
#     nao tem aneis: varias fatias tem 1-3 vertices -> vertices jogados para direcoes erradas (espiculas);
#  2) raio do bulbo so C0 no pico (afinamento comeca com derivada != 0) + mistura de so 0,22 stud;
#  3) espicula fina original do Ashwing em y~22,7 (diedros ~175 graus), que agora parece calombo do bulbo;
#  4) normais personalizadas (glTF) nao recalculadas -> sombreado quebrado; 5) peso tail_09->tail_10 com
#     salto 0->1 em cima do bulbo -> pincamento ao dobrar.
# Correcao: cada vertice ganha angulo em torno da linha central ORIGINAL (E1) e e recolocado num tubo
# analitico liso (raio C1, mesma curva/comprimento do E2); zona de entrada com raio limitado ao envelope;
# pesos suavizados so na juncao; normais recalculadas so na regiao.
# Uso: blender -b Wyvern_E3.blend -P 04_transicao_ferrao.py -- <Wyvern_E1.blend> <saida.blend> [opcoes]
#   E4 = sem opcoes. E5 (04/11 - fechamento local, partindo do E4) = opcoes "juncao_tubo fenda":
#   juncao_tubo: a zona de entrada (22,3-23,36) tambem vai para o tubo liso (mistura desde YA em 0,5 stud) ->
#     some a aba dobrada da emenda original cauda/ponta do Ashwing em y~22,7 (verso visivel; penetrava no fly 4-10);
#   fenda: os vertices de BORDA ABERTA da ponta (labios da "lamina" aberta do losango original) recebem o mesmo
#     angulo e raio -> os dois labios caem na mesma linha e a fenda fecha, sem vertice novo nem solda.
import bpy, sys, math, json
import numpy as np
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
E1, OUT = argv[0], argv[1]
OPC = set(argv[2:])
obj = bpy.data.objects["Wyvern"]; me = obj.data
NV = len(me.vertices)
with bpy.data.libraries.load(E1) as (src, dst): dst.meshes = list(src.meshes)
m1 = [m for m in dst.meshes if m and len(m.vertices) == NV][0]
P1 = np.array([v.co[:] for v in m1.vertices])           # posicoes originais (antes do E2)
Y0, COMP, CURVA = 23.91, 5.5, 110.0                      # mesmos parametros do E2
y_max1 = P1[:, 1].max(); L0 = y_max1 - Y0
YA = 22.3                                                # inicio da zona de entrada (inclui a espicula de 22,7)
# linha central original: reta ajustada (minimos quadrados) na cauda antes da ponta
sel = (P1[:, 1] > 19.0) & (P1[:, 1] < Y0)
ax_, bx_ = np.polyfit(P1[sel, 1], P1[sel, 0], 1); az_, bz_ = np.polyfit(P1[sel, 1], P1[sel, 2], 1)
def c1(y): return np.array([ax_ * y + bx_, y, az_ * y + bz_])
# raios da cauda (meias-larguras robustas) antes da ponta
d = P1[sel] - np.array([c1(y) for y in P1[sel, 1]])
HW0 = np.percentile(np.abs(d[:, 0]), 90); HH0 = np.percentile(np.abs(d[:, 2]), 90); R0 = (HW0 + HH0) / 2
A0 = -math.atan(az_)                                     # inclinacao inicial da cauda (descendo em z)
# linha central nova: reta ate Y0 e arco do E2 depois (integrado), tangente continua
N = 400; C = [Vector(c1(Y0))]; ANG = [A0]
for i in range(1, N + 1):
    a = A0 + math.radians(CURVA) * (i / N) ** 1.6
    C.append(C[-1] + Vector((0, math.cos(a), -math.sin(a))) * (COMP / N)); ANG.append(a)
def centro(t):
    if t <= 0: return Vector(c1(Y0 + t * L0)), A0
    i = min(N - 1, int(t * N)); f = t * N - i
    return C[i].lerp(C[i + 1], f), ANG[i] + (ANG[i + 1] - ANG[i]) * f
def sstep(x):   # smootherstep (C2)
    x = min(1.0, max(0.0, x)); return x * x * x * (x * (6 * x - 15) + 10)
TP, BULBO = 0.24, 2.0                                    # pico do bulbo (t) e fator do raio (E2: 0,22 e 2,1)
def raio(t):
    if t <= TP: return R0 * (1 + (BULBO - 1) * sstep((t + 0.10) / (TP + 0.10)))
    u = (t - TP) / (1 - TP)
    return R0 * BULBO * math.cos(math.pi / 2 * min(u, 1)) ** 1.25 + 0.022   # ponta com raio minimo (E2: 0,02)
# envelope radial original (janela deslizante +-0,6) para preservar leve variacao e limitar espiculas
reg = np.where(P1[:, 1] >= YA)[0]
PR = P1[reg]
# centro/semieixos LOCAIS da ponta original (janela +-0,5): a ponta do Ashwing nao segue a reta da cauda
# (fica ~0,23 acima dela) - com a reta, todos os vertices da ponta caiam do mesmo lado e colapsavam
def secao(y):
    m = np.abs(PR[:, 1] - y) < 0.5
    if m.sum() < 6: m = np.argsort(np.abs(PR[:, 1] - y))[:6]
    q = PR[m]; lo, hi = np.percentile(q, 10, axis=0), np.percentile(q, 90, axis=0)
    return (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, max((hi[0] - lo[0]) / 2, 0.02), max((hi[2] - lo[2]) / 2, 0.02)
rel = {}
for i in reg:
    p = P1[i]; c = c1(p[1])
    xl, zl, hwl, hhl = secao(p[1]); b = sstep((p[1] - (Y0 - 0.3)) / 0.6)   # reta da cauda -> centro local
    xc = c[0] + (xl - c[0]) * b; zc = c[2] + (zl - c[2]) * b
    hw = HW0 + (hwl - HW0) * b; hh = HH0 + (hhl - HH0) * b
    dx, dz = (p[0] - xc) / hw, (p[2] - zc) / hh
    rel[i] = (math.atan2(dz, dx), math.hypot(dx, dz))
ZB = Y0 - 0.55                                           # zona de entrada (YA..ZB) / tubo (ZB..ponta)
def colocar(i, th):
    p = P1[i]; y = p[1]; rho = rel[i][1]
    g = math.tanh(1.3 * rho)          # raio normalizado na secao local; monotonico: vertices distintos nao colapsam
    t = (y - Y0) / L0
    if y < ZB and "juncao_tubo" not in OPC:
        # zona de entrada: mantem o original, so limita o raio ao envelope liso
        c = c1(y); dx, dz = p[0] - c[0], p[2] - c[2]
        rr = math.hypot(dx / HW0, dz / HH0) * R0; lim = 1.08 * R0
        k = 1.0 if rr <= lim else lim / rr
        k = 1 + (k - 1) * sstep((y - YA) / 0.5)          # entra suave a partir de YA
        return Vector((c[0] + dx * k, y, c[2] + dz * k))
    c, a = centro(t); r = raio(t) * (0.80 + 0.22 * g)
    nz = Vector((0, math.sin(a), math.cos(a)))
    alvo = c + Vector((math.cos(th) * r * HW0 / R0, 0, 0)) + nz * (math.sin(th) * r * HH0 / R0)
    if "juncao_tubo" in OPC: return Vector(p).lerp(alvo, sstep((y - YA) / 0.5))
    return Vector(p).lerp(alvo, sstep((y - ZB) / 0.75))  # mistura original->tubo em 0,75 stud (E2: 0,22)
TH = {int(i): rel[i][0] for i in reg}
novo = {int(i): colocar(i, TH[int(i)]) for i in reg}
# vizinhanca soldada por posicao (costuras de UV duplicam vertices) e triangulos da regiao
regs = set(novo)
ch1 = {i: tuple(np.round(P1[i], 4)) for i in regs}
grupo = {}
for i in regs: grupo.setdefault(ch1[i], []).append(i)
viz = {k: set() for k in grupo}
for e in me.edges:
    a, b = e.vertices
    if a in regs and b in regs and ch1[a] != ch1[b]: viz[ch1[a]].add(ch1[b]); viz[ch1[b]].add(ch1[a])
me.calc_loop_triangles()
TRI = [t.vertices[:] for t in me.loop_triangles if all(v in regs for v in t.vertices)]
LABIOS = set()
if "fenda" in OPC:
    from collections import Counter
    cont = Counter()
    for t in TRI:
        for u, v in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): cont[frozenset((ch1[u], ch1[v]))] += 1
    LABIOS = {k for e, n in cont.items() if n == 1 for k in e if grupo[k] and P1[grupo[k][0], 1] > Y0 + 0.5 * L0}
    sinal = 1 if sum(math.sin(rel[grupo[k][0]][0]) for k in LABIOS) >= 0 else -1
    for k in LABIOS:
        for v in grupo[k]: rel[v] = (sinal * math.pi / 2, 1.5)      # angulo e raio comuns aos dois labios
    for k in LABIOS:
        for v in grupo[k]: TH[v] = rel[v][0]; novo[v] = colocar(v, TH[v])
def dobradas():
    ac = {}
    ns = []
    for t in TRI:
        a, b, c = (novo[v] for v in t); n = (b - a).cross(c - a); ns.append(n)
        for v in t: ac[ch1[v]] = ac.get(ch1[v], Vector()) + n
    out = []
    for t, n in zip(TRI, ns):
        m = sum((ac[ch1[v]] for v in t), Vector())
        if n.length > 1e-9 and m.length > 1e-9 and n.normalized().dot(m.normalized()) < 0: out.append(t)
    return out
# (a) a espicula fina original em y~22,7 (faces ja dobradas no Ashwing) NAO e mexida alem do limite de raio:
#     levar o apice a media dos vizinhos foi testado e criou autointersecao em 22,7.
# (b) faces dobradas no tubo: relaxa SO o angulo (t fixo -> gradiente de veneno/UV nao desliza ao longo).
#     Guloso: cada iteracao so fica se reduzir as dobradas sem criar triangulo degenerado.
def degenerados():
    return sum(1 for t in TRI if ((novo[t[1]] - novo[t[0]]).cross(novo[t[2]] - novo[t[0]])).length / 2 < 1e-4)
n_dobradas = [len(dobradas())]
for it in range(40):
    fd = dobradas()
    if not fd: break
    salvo_th, salvo_p = dict(TH), dict(novo); d0 = degenerados()
    alvo = {ch1[v] for t in fd for v in t if P1[v, 1] >= ZB}
    alvo |= {j for k in list(alvo) for j in viz[k] if P1[grupo[j][0], 1] >= ZB}
    alvo -= LABIOS
    for k in alvo:
        i = grupo[k][0]; th = salvo_th[i]
        if not viz[k]: continue
        s = sum(math.sin(salvo_th[grupo[j][0]] - th) for j in viz[k]) / len(viz[k])
        th += 0.5 * s
        for v in grupo[k]: TH[v] = th; novo[v] = colocar(v, th)
    n = len(dobradas())
    if n >= n_dobradas[-1] or degenerados() > d0:
        TH, novo = salvo_th, salvo_p; break
    n_dobradas.append(n)
# aplica na base e nas shape keys (deslocamento das correctives e zero na regiao; preserva mesmo assim)
if me.shape_keys:
    base = me.shape_keys.reference_key
    for kb in me.shape_keys.key_blocks:
        if kb == base: continue
        for i, c in novo.items(): kb.data[i].co = c + (kb.data[i].co - base.data[i].co)
    for i, c in novo.items(): base.data[i].co = c
for i, c in novo.items(): me.vertices[i].co = c
# pesos: so a juncao tail_09/tail_10 (E1 original: 25,3->25,9; E2 forcou 100% tail_10 a partir de 25,56)
g09 = obj.vertex_groups["tail_09"]; g10 = obj.vertex_groups["tail_10"]
JA, JB = 24.7, 26.3
for i in reg:
    y = P1[i, 1]
    if y < JA: continue
    w10 = sstep((y - JA) / (JB - JA))
    for gr in me.vertices[i].groups:
        if gr.group not in (g09.index, g10.index): gr.weight = 0.0
    g09.add([int(i)], 1 - w10, "REPLACE"); g10.add([int(i)], w10, "REPLACE")
me.update()
# normais personalizadas: recalcula so os cantos da regiao (resto do corpo fica identico)
cn_antigo = [Vector(c.vector) for c in me.corner_normals]
# normal lisa por POSICAO soldada (costuras de UV duplicam vertices; a ponta original tinha sharp_edge/
# sharp_face, que deixavam facetas claras), ponderada por area; entra suave a partir de YA (sem costura de luz)
regs = set(int(i) for i in reg)
chave = {i: tuple(round(c, 4) for c in me.vertices[i].co) for i in regs}
acum = {}
for p in me.polygons:
    if any(v in regs for v in p.vertices):
        for v in p.vertices:
            if v in regs: acum[chave[v]] = acum.get(chave[v], Vector()) + p.normal * p.area
cn = []
for l in me.loops:
    v = l.vertex_index; n0 = cn_antigo[l.index]
    if v in regs and acum.get(chave[v], Vector()).length > 1e-9:
        n = n0.lerp(acum[chave[v]].normalized(), sstep((P1[v, 1] - YA) / 0.6)); cn.append(n.normalized())
    else: cn.append(n0)
me.normals_split_custom_set([v[:] for v in cn])
me.update()
for m in list(dst.meshes):
    if m: bpy.data.meshes.remove(m)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("RJSON" + json.dumps({"R0": round(R0, 3), "HW0": round(float(HW0), 3), "HH0": round(float(HH0), 3), "A0_graus": round(math.degrees(A0), 2),
      "vertices_regiao": len(novo), "YA": YA, "faces_dobradas_por_iteracao": n_dobradas, "opcoes": sorted(OPC), "labios_fenda": len(LABIOS)}) + "RFIM")
