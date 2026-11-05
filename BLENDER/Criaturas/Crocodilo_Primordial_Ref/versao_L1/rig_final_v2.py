"""Rig FINAL v2 (Lote 1, 03/11) do Crocodilo Primordial: separacao das arcadas pela TOPOLOGIA (rasgo das arestas entre
cranio e mandibula a frente do canto anatomico + fechamento dos furinhos); flexivel so no canto. Base: rig_final.py.
 (LOW do Meshy, 32 studs). Marcos tirados da propria malha; cada pata com as
articulacoes medidas na sua propria malha (as traseiras do Meshy estao desencontradas ~2 studs, pose de passo da
referencia: NAO reposicionar a malha, as lascas do Silverwing vieram de repose). Pesos heat + mandibula por disputa
geodesica cranio x queixo + suavizacao no canto da boca. IK de 2 ossos por pata (alvos = Empties, so para animar;
os clipes sao assados em FK antes de exportar). Nomes dos ossos ja sao os do jogo (o Roblox liga malha a osso pelo nome).
Uso: blender -b CR_Crocodilo_LOW.blend -P rig_final.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; lo = bpy.data.objects["CR_Croc_LOW"]; me = lo.data
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co[:, 0], co[:, 1], co[:, 2]
Y0, Y1 = y.min(), y.max()

# ------------------------------------------------------------------ marcos
pes = {}
for lado, sx in (("E", 1), ("D", -1)):
    for par, cond in (("dian", y < -4.0), ("tras", y >= -4.0)):
        sel = (z < 0.35) & (x * sx > 1.5) & cond
        pes[(lado, par)] = V(co[sel].mean(axis=0)) if sel.any() else None
print("PES", {k: tuple(round(c, 2) for c in v) for k, v in pes.items() if v})
y_ombro = (pes[("E", "dian")].y + pes[("D", "dian")].y) / 2 + 0.6
y_quad = (pes[("E", "tras")].y + pes[("D", "tras")].y) / 2 + 0.3
def centro(yy, faixa=0.3):
    s = np.abs(y - yy) < faixa
    s2 = s & (np.abs(x) < 1.0)
    return V((0, yy, (z[s2].min() + z[s2].max()) / 2)) if s2.any() else V((0, yy, 3))
# boca: raios verticais no eixo. A malha e casca: cranio (entra), palato (sai), lingua/assoalho (entra), queixo (sai).
# O ar da boca fica entre o 2o e o 3o impacto. Sem boca (atras do canto) so ha 2 impactos.
bpy.context.view_layer.update()
def impactos(xx, yy):
    zs = []; zz = 12.0
    while True:
        ok, h, nrm, _ = lo.ray_cast(V((xx, yy, zz)), V((0, 0, -1)), distance=zz + 1)
        if not ok: break
        zs.append(h.z); zz = h.z - 0.002
        if len(zs) > 12: break
    return zs
fenda = []                                              # (y, z_meio, altura do vao, z_palato, z_assoalho)
for yy in np.arange(Y0 + 0.25, Y0 + 9.0, 0.15):
    vaos = []
    for xx in (0.0, 0.35, -0.35):
        h = impactos(xx, yy)
        if len(h) >= 4: vaos.append((h[1], h[2]))
    if vaos:
        pal = float(np.median([a for a, b in vaos])); ass = float(np.median([b for a, b in vaos]))
        if pal - ass > 0.04: fenda.append((float(yy), (pal + ass) / 2, pal - ass, pal, ass))
# a fenda continua so ate o primeiro buraco grande (a garganta fechada atras do canto encerra a sequencia)
cont = [fenda[0]]
for f in fenda[1:]:
    if f[0] - cont[-1][0] > 0.5: break
    cont.append(f)
fenda = cont
y_canto = fenda[-1][0]
y_dob, z_dob = y_canto + 0.55, fenda[-1][1]                # articulacao: atras e na linha do canto da boca
ab = fenda[0]
print("BOCA fenda de y %.2f a %.2f (canto); vao na ponta %.2f (palato %.2f, assoalho %.2f); dobradica y %.2f z %.2f" % (
    fenda[0][0], y_canto, ab[2], ab[3], ab[4], y_dob, z_dob))
def z_palato(yy):
    if yy <= fenda[0][0]: return fenda[0][3]
    for a, b in zip(fenda, fenda[1:]):
        if a[0] <= yy <= b[0]: t = (yy - a[0]) / (b[0] - a[0]); return a[3] + (b[3] - a[3]) * t
    return fenda[-1][3]
def z_fenda(yy):
    if yy <= fenda[0][0]: return fenda[0][1]
    for a, b in zip(fenda, fenda[1:]):
        if a[0] <= yy <= b[0]: t = (yy - a[0]) / (b[0] - a[0]); return a[1] + (b[1] - a[1]) * t
    return fenda[-1][1]

# ------------------------------------------------------------------ articulacoes das patas pela secao da malha
def centroide(sx, ypes, z0, faixa=0.15, raio_y=2.0, xmin=1.8):
    s = (np.abs(z - z0) < faixa) & (x * sx > xmin) & (np.abs(y - ypes) < raio_y)
    return V(co[s].mean(axis=0)) if s.sum() > 5 else None
PATA = {}
for lado, sx in (("E", 1), ("D", -1)):
    for par in ("dian", "tras"):
        p = pes[(lado, par)]
        punho = centroide(sx, p.y, 0.80)
        meio = [centroide(sx, p.y, zz) for zz in (1.4, 1.7, 2.0, 2.3)]
        meio = [m for m in meio if m]
        topo = centroide(sx, p.y, 3.0) or centroide(sx, p.y, 2.7)
        omb = V((1.55 * sx, topo.y, topo.z - 0.10))                  # junta dentro do corpo
        # cotovelo/joelho na altura media entre ombro e punho (braco e antebraco de tamanhos parecidos = alcance),
        # na lateral da secao da pata
        zm = (omb.z + punho.z) / 2; cm = centroide(sx, p.y, zm) or max(meio, key=lambda m: abs(m.x))
        lat = max(abs(m.x) for m in meio)
        cot = V((lat * sx, cm.y, zm))
        ponta = V((p.x + 0.15 * sx, p.y - (1.25 if par == "dian" else 1.45), 0.18))
        PATA[(lado, par)] = (omb, cot, V((punho.x, punho.y, max(0.70, punho.z))), ponta)
        print("PATA", lado, par, [tuple(round(c, 2) for c in q) for q in PATA[(lado, par)]])
y_ombro = (PATA[("E", "dian")][0].y + PATA[("D", "dian")][0].y) / 2
y_quad = (PATA[("E", "tras")][0].y + PATA[("D", "tras")][0].y) / 2

# ------------------------------------------------------------------ armadura
arm_d = bpy.data.armatures.new("CR_Croc_Rig"); arm = bpy.data.objects.new("CR_Croc_Rig", arm_d); sc.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT")
E = arm_d.edit_bones
def osso(nome, a, b, pai=None, conecta=True):
    o = E.new(nome); o.head = a; o.tail = b
    if pai: o.parent = E[pai]; o.use_connect = conecta and (E[pai].tail - a).length < 1e-4
    return o
y_meio = (y_quad + y_ombro) / 2
osso("Raiz", V((0, y_meio, 0)), V((0, y_meio - 1.0, 0)))                          # no chao, aponta para a frente
osso("Pelve", centro(y_quad), centro(y_meio), "Raiz", False)
osso("Coluna1", E["Pelve"].tail, centro((y_meio + y_ombro) / 2), "Pelve")
osso("Coluna2", E["Coluna1"].tail, centro(y_ombro), "Coluna1")
y_pesc = (y_ombro + y_dob) / 2
osso("Pescoco", E["Coluna2"].tail, centro(y_pesc), "Coluna2")
cab0 = V((0, y_dob, z_dob + 0.35))
osso("Pescoco2", E["Pescoco"].tail, cab0, "Pescoco")
osso("Cabeca", cab0, V((0, Y0 + 0.6, z_fenda(Y0 + 0.6) + 0.5)), "Pescoco2")
osso("Mandibula", V((0, y_dob, z_dob)), V((0, Y0 + 0.6, z_fenda(Y0 + 0.6) - 0.35)), "Pescoco2", False)
ys_c = np.linspace(y_quad, Y1 - 0.2, 9)
for i in range(8):
    osso("Cauda%d" % (i + 1), centro(ys_c[i]), centro(ys_c[i + 1]), "Cauda%d" % i if i else "Pelve", i > 0)
for lado in ("E", "D"):
    for par, pai, nomes in (("dian", "Coluna2", ("Braco", "Antebraco", "Mao")), ("tras", "Pelve", ("Coxa", "Canela", "Pe"))):
        omb, cot, punho, ponta = PATA[(lado, par)]
        osso(nomes[0] + lado, omb, cot, pai, False); osso(nomes[1] + lado, cot, punho, nomes[0] + lado)
        osso(nomes[2] + lado, punho, ponta, nomes[1] + lado)
for b in E: b.roll = 0.0
bpy.ops.object.mode_set(mode="OBJECT")

# ------------------------------------------------------------------ pesos
for o in sc.objects: o.select_set(False)
lo.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
ok_heat = True
try: bpy.ops.object.parent_set(type="ARMATURE_AUTO")
except Exception as e: ok_heat = False; print("HEAT falhou:", e)
sem_peso = sum(1 for v in me.vertices if not v.groups)
print("PESOS heat ok:", ok_heat, "verts sem peso:", sem_peso)
if sem_peso > n * 0.01:                                  # reserva: pesos por envelope (distancia)
    for vg in list(lo.vertex_groups): lo.vertex_groups.remove(vg)
    lo.parent = None; lo.modifiers.clear()
    lo.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_ENVELOPE"); print("PESOS reserva envelope")
# mandibula x cranio: disputa geodesica (Dijkstra pelas arestas) entre sementes inequivocas - cranio acima do palato e
# queixo abaixo do assoalho. Dentes/gengivas/labios ficam com quem chega primeiro (um contato dente-dente nao vaza).
import heapq
def z_assoalho(yy):
    if yy <= fenda[0][0]: return fenda[0][4]
    for a, b in zip(fenda, fenda[1:]):
        if a[0] <= yy <= b[0]: t = (yy - a[0]) / (b[0] - a[0]); return a[4] + (b[4] - a[4]) * t
    return fenda[-1][4]
# linha do labio pelos lados: raios horizontais de fora para dentro; o entalhe (raio mais fundo) separa os labios
def entalhe(yy):
    zs = []
    for sx in (1, -1):
        melhor = None
        for k in range(int(1.2 / 0.04)):
            zz = z_fenda(yy) - 0.6 + k * 0.04
            ok, h, nrm, _ = lo.ray_cast(V((5 * sx, yy, zz)), V((-sx, 0, 0)), distance=6)
            prof = abs(h.x) if ok else 0.0
            if melhor is None or prof < melhor[0]: melhor = (prof, zz)
        zs.append(melhor[1])
    return sum(zs) / 2
ENT = [(yy, entalhe(yy)) for yy in np.arange(fenda[0][0], y_canto, 0.25)]
ENT = [(a, (ENT[max(i - 1, 0)][1] + b + ENT[min(i + 1, len(ENT) - 1)][1]) / 3) for i, (a, b) in enumerate(ENT)]
def z_corte(yy):
    if yy <= ENT[0][0]: return ENT[0][1]
    for a, b in zip(ENT, ENT[1:]):
        if a[0] <= yy <= b[0]: t = (yy - a[0]) / (b[0] - a[0]); return a[1] + (b[1] - a[1]) * t
    return ENT[-1][1]
print("LABIO entalhe lateral", [(round(a, 1), round(b, 2)) for a, b in ENT[::4]])
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
dono = {}; dist = {}; fila = []; SEMENTE = set()
for v in bm.verts:
    if v.co.y > y_canto - 0.10: continue
    if v.co.z > z_palato(v.co.y) + 0.35: dono[v.index] = 0
    elif v.co.z < z_assoalho(v.co.y) - 0.35: dono[v.index] = 1
    else: continue
    dist[v.index] = 0.0; heapq.heappush(fila, (0.0, v.index, dono[v.index])); SEMENTE.add(v.index)
while fila:
    d, i, k = heapq.heappop(fila)
    if d > dist.get(i, 1e9): continue
    a = bm.verts[i]
    for e in a.link_edges:
        b = e.other_vert(a)
        if b.co.y > y_canto - 0.10: continue
        zf = z_corte(b.co.y)
        cruza = (k == 1 and b.co.z > zf) or (k == 0 and b.co.z < zf)   # atravessar a linha da boca custa mais
        nd = d + e.calc_length() * (4.0 if cruza else 1.0)
        if nd < dist.get(b.index, 1e9): dist[b.index] = nd; dono[b.index] = k; heapq.heappush(fila, (nd, b.index, k))
# voto de maioria (2 aneis de vizinhos): ponta de dente que encostava na outra arcada volta para o proprio dente
viz2 = {}
for v in bm.verts:
    if v.index not in dono: continue
    r1 = {e.other_vert(v).index for e in v.link_edges}
    r2 = set(r1)
    for j in r1:
        r2 |= {e.other_vert(bm.verts[j]).index for e in bm.verts[j].link_edges}
    r2.discard(v.index); viz2[v.index] = [j for j in r2 if j in dono]
trocas = 0
for _ in range(4):
    novo = {}
    for i, vz in viz2.items():
        if not vz: continue
        m = sum(dono[j] for j in vz) / len(vz)
        if dono[i] == 1 and m < 0.3: novo[i] = 0
        elif dono[i] == 0 and m > 0.7: novo[i] = 1
    for i, k in novo.items(): dono[i] = k
    trocas += len(novo)
print("VOTO trocas", trocas)
# contatos dente-arcada: dentro da boca nenhuma aresta liga cranio e queixo. Em cada aresta mista, o lado com o
# grupinho menor (mesmo dono, ate 0,6 de distancia pelas arestas) e a ponta intrusa: troca de dono.
def grupo(i0, raio=0.6):
    k = dono[i0]; vist = {i0: 0.0}; fila_ = [(0.0, i0)]
    while fila_:
        d, i = heapq.heappop(fila_)
        a_ = bm.verts[i]
        for e in a_.link_edges:
            j = e.other_vert(a_).index
            if dono.get(j) != k: continue
            nd = d + e.calc_length()
            if nd <= raio and nd < vist.get(j, 9e9): vist[j] = nd; heapq.heappush(fila_, (nd, j))
    return set(vist)
contatos = 0; trocado = set()
CONTATOS = False      # testado 03/11: na ponta do focinho os labios se tocam de verdade e o passo joga o focinho na mandibula
for _ in range(1 if CONTATOS else 0):
    mudou = False
    for e in bm.edges:
        i, j = e.verts[0].index, e.verts[1].index
        if i not in dono or j not in dono or dono[i] == dono[j]: continue
        if max(e.verts[0].co.y, e.verts[1].co.y) > y_canto - 0.3: continue
        gi, gj = grupo(i), grupo(j)
        menor = gi if len(gi) < len(gj) else gj
        if len(menor) < 30 and not (menor & SEMENTE) and not (menor & trocado):
            novo_k = 1 - dono[next(iter(menor))]
            for q in menor: dono[q] = novo_k
            trocado |= menor
            contatos += 1; mudou = True
    if not mudou: break
mistas = sum(1 for e in bm.edges if e.verts[0].index in dono and e.verts[1].index in dono and dono[e.verts[0].index] != dono[e.verts[1].index]
             and max(e.verts[0].co.y, e.verts[1].co.y) <= y_canto - 0.3)
print("CONTATOS corrigidos", contatos, "arestas mistas restantes na boca", mistas)
# correcao dirigida (03/11, pedido do usuario): so arestas mistas que ESTICAM > 2x quando a mandibula gira +-10 graus
# na dobradica (pontas de dente presas na arcada oposta). Troca o grupinho menor, sem sementes; repete ate sumir.
from mathutils import Matrix as _M
def esticadas():
    out = []
    for ang in (math.radians(10), math.radians(-11)):
        R_ = _M.Translation(V((0, y_dob, z_dob))) @ _M.Rotation(ang, 4, "X") @ _M.Translation(V((0, -y_dob, -z_dob)))
        for e in bm.edges:
            i, j = e.verts[0].index, e.verts[1].index
            if i not in dono or j not in dono or dono[i] == dono[j]: continue
            a_, b_ = e.verts[0].co, e.verts[1].co
            pa = R_ @ a_ if dono[i] == 1 else a_; pb_ = R_ @ b_ if dono[j] == 1 else b_
            if (pa - pb_).length > 2.0 * max((a_ - b_).length, 1e-4) and (pa - pb_).length > 0.06: out.append(e)
    return out
fixos = 0
DIRIGIDA = False      # testado 03/11: a fronteira so muda de lugar (a parede interna da boca liga as arcadas) -> membrana suave abaixo
for rodada in range(6 if DIRIGIDA else 0):
    lista = esticadas()
    if not lista: break
    for e in lista:
        i, j = e.verts[0].index, e.verts[1].index
        if dono[i] == dono[j]: continue
        gi, gj = grupo(i, 0.45), grupo(j, 0.45)
        menor = gi if len(gi) <= len(gj) else gj
        if len(menor) < 40 and not (menor & SEMENTE):
            k_ = 1 - dono[next(iter(menor))]
            for q in menor: dono[q] = k_
            fixos += len(menor)
    print("DENTES rodada", rodada, "arestas esticadas", len(lista), "verts trocados ate aqui", fixos)
print("DENTES arestas mistas que esticam > 2x:", len(esticadas()))

# ------------------------------------------------------------------ v2: separacao das arcadas pela topologia
# Cortes transversais (review/cortes_L0.png): a frente do canto as arcadas ja sao cascas separadas e so se tocam nas pontas
# dos dentes; do canto anatomico (juncao lateral dos labios) para tras elas se unem pelos lados (pele que estica).
# Rasga as arestas entre faces de donos diferentes A FRENTE da juncao e fecha os furinhos: cada dente rigido na sua arcada.
bm.faces.ensure_lookup_table(); bm.edges.ensure_lookup_table()
Y_JUNCAO_PRE = y_canto - 1.6                     # faixa da frente (a juncao exata e medida abaixo)
def dono_face(f):
    ks = [dono.get(v.index) for v in f.verts]
    if None in ks: return None
    return 1 if sum(ks) * 2 > len(ks) else 0
DF = {f.index: dono_face(f) for f in bm.faces}
# voto por FACE (3 aneis): ponta de dente que ficou com a arcada oposta segue o corpo do proprio dente, para o rasgo cair
# no contato com a gengiva e nao no meio do dente
def aneis(f, n_=3):
    vist = {f.index}; borda_ = [f]
    for _ in range(n_):
        prox = []
        for g_ in borda_:
            for e in g_.edges:
                for h in e.link_faces:
                    if h.index not in vist: vist.add(h.index); prox.append(h)
        borda_ = prox
    vist.discard(f.index); return vist
trocas_f = 0
for _ in range(3):
    mud = {}
    for f in bm.faces:
        if DF.get(f.index) is None or f.calc_center_median().y > Y_JUNCAO_PRE: continue
        viz = [DF[i] for i in aneis(f) if DF.get(i) is not None]
        if len(viz) < 6: continue
        m = sum(viz) / len(viz)
        if DF[f.index] == 1 and m < 0.3: mud[f.index] = 0
        elif DF[f.index] == 0 and m > 0.7: mud[f.index] = 1
    DF.update(mud); trocas_f += len(mud)
    if not mud: break
print("VOTO_FACES trocas", trocas_f)
mistas_e = [e for e in bm.edges if len(e.link_faces) == 2 and None not in (DF[e.link_faces[0].index], DF[e.link_faces[1].index])
            and DF[e.link_faces[0].index] != DF[e.link_faces[1].index]]
# juncao lateral: faixa CONTINUA de arestas mistas (em todas as fatias de 0,25) ate o canto
bins_ = {}
for e in mistas_e:
    yb = int(math.floor(((e.verts[0].co.y + e.verts[1].co.y) / 2) / 0.25)); bins_[yb] = bins_.get(yb, 0) + 1
# juncao REAL dos labios = onde o entalhe lateral (raio horizontal entrando na boca) some; a faixa continua de arestas
# mistas pegava os dentes de tras encaixados (testado: deixava fios entre -12,75 e -11,3)
def entra_boca(yy):
    zz = z_corte(yy); fundo = []
    for sx in (1, -1):
        ok, h, nrm, _ = lo.ray_cast(V((5 * sx, yy, zz)), V((-sx, 0, 0)), distance=6)
        fundo.append(abs(h.x) if ok else 0.0)
    xl = x_lab_lado(yy)
    return min(fundo) < xl - 0.35
def x_lab_lado(yy):
    ok, h, nrm, _ = lo.ray_cast(V((5, yy, z_corte(yy) + 0.35)), V((-1, 0, 0)), distance=6)
    return abs(h.x) if ok else 1.0
# testado: usar o canto da fenda (-10,8) rasga a pele do canto e deixa abas (cortina). Fica a faixa continua.
yb = int(math.floor(y_canto / 0.25))
while bins_.get(yb - 1, 0) > 0: yb -= 1
Y_JUNCAO = yb * 0.25
# colunas de tecido do Meshy no fundo da boca (ligam as arcadas por DENTRO da pele lateral, entre a juncao e o canto):
# viram fios ao abrir. Ajuste local: apaga so essas faces e tampa as bases. A pele de fora da bochecha fica ligada.
XLC = {}
def xl(yy):
    k = round(yy, 1)
    if k not in XLC: XLC[k] = x_lab_lado(yy)
    return XLC[k]
# testado: apagar as faces das colunas deixa buracos visiveis. Em vez disso: rasga as colunas no meio (arestas mistas por
# DENTRO da pele lateral, entre a juncao e o canto) e tampa as duas pontas; a bochecha de fora continua ligada.
def dentro(e):
    c = (e.verts[0].co + e.verts[1].co) / 2
    return Y_JUNCAO - 0.1 < c.y < y_canto and abs(c.x) < xl(c.y) - 0.05
rasgar = [e for e in mistas_e if max(e.verts[0].co.y, e.verts[1].co.y) < Y_JUNCAO - 0.05 or dentro(e)]
print("PILARES arestas de coluna rasgadas", sum(1 for e in rasgar if dentro(e)))
print("RASGO juncao lateral dos labios em y %.2f (canto da fenda %.2f); arestas mistas %d, rasgadas %d" % (Y_JUNCAO, y_canto, len(mistas_e), len(rasgar)))
nv0 = len(bm.verts)
bmesh.ops.split_edges(bm, edges=rasgar)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
# dono dos vertices novos (e dos antigos que ficaram so de um lado) = dono das faces ligadas
for v in bm.verts:
    ks = {DF.get(f.index) for f in v.link_faces} - {None}
    if len(ks) == 1 and (v.index >= nv0 or v.index in dono): dono[v.index] = ks.pop()
# furinhos abertos pelo rasgo (pontas de dente e gengiva): fecha laços pequenos e copia a UV do vizinho
borda = [e for e in bm.edges if e.is_boundary and e.verts[0].co.y < y_canto + 0.2]
antes_f = len(bm.faces)
res = bmesh.ops.holes_fill(bm, edges=borda, sides=24)
if res["faces"]: bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))   # tampas com normal para fora
uvl = bm.loops.layers.uv.active
for f in res["faces"]:
    for l in f.loops:
        viz = [l2 for l2 in l.vert.link_loops if l2.face is not f]
        if viz and uvl: l[uvl].uv = viz[0][uvl].uv.copy()
    ks = {dono.get(v.index) for v in f.verts} - {None}
print("RASGO verts novos %d; furos fechados %d faces; bordas abertas restantes na frente %d" % (
    len(bm.verts) - nv0, len(res["faces"]), sum(1 for e in bm.edges if e.is_boundary)))
bm.verts.index_update(); bm.to_mesh(me); me.update()
inf = {i for i, k in dono.items() if k == 1}
bm.free()
gc, gm = lo.vertex_groups.get("Cabeca") or lo.vertex_groups.new(name="Cabeca"), lo.vertex_groups.get("Mandibula") or lo.vertex_groups.new(name="Mandibula")
cab_set = 0
for v in me.vertices:
    if v.co.y > y_dob + 0.8: continue
    if v.index in inf and v.co.y < y_canto - 0.10:
        gm.add([v.index], 1.0, "REPLACE"); gc.add([v.index], 0.0, "REPLACE")
    elif v.co.y < y_canto - 0.10:
        gc.add([v.index], 1.0, "REPLACE"); gm.add([v.index], 0.0, "REPLACE"); cab_set += 1
    else:                                                # canto -> dobradica: abaixo da linha vai com a mandibula
        t = min(1.0, max(0.0, (y_dob + 0.8 - v.co.y) / (y_dob + 0.8 - y_canto)))
        baixo = min(1.0, max(0.0, (z_dob + 0.15 - v.co.z) / 0.4))
        wm = t * baixo; gm.add([v.index], wm, "REPLACE"); gc.add([v.index], t * (1 - baixo), "REPLACE")
print("MANDIBULA verts", len(inf), "cabeca", cab_set)
# na cabeca o heat espalha pesos para o pescoco; zera grupos que nao sejam Cabeca/Mandibula a frente do canto
for v in me.vertices:
    if v.co.y < y_canto - 0.10:
        for g in list(v.groups):
            nome = lo.vertex_groups[g.group].name
            if nome not in ("Cabeca", "Mandibula"): lo.vertex_groups[g.group].remove([v.index])

# ------------------------------------------------------------------ canto da boca: suaviza Cabeca x Mandibula (evita faixa esticada)
adj = {i: set() for i in range(len(me.vertices))}
for e in me.edges: a, b = e.vertices; adj[a].add(b); adj[b].add(a)
def peso(g, i):
    try: return g.weight(i)
    except RuntimeError: return 0.0
zona = [v.index for v in me.vertices if Y_JUNCAO - 0.10 < v.co.y < y_dob + 0.9]   # v2: canto anatomico (juncao lateral) ate a dobradica
for _ in range(6):
    novo = {}
    for i in zona:
        viz = adj[i]
        if not viz: continue
        m = (peso(gm, i) + sum(peso(gm, j) for j in viz)) / (len(viz) + 1)
        novo[i] = m
    for i, m in novo.items():
        c = peso(gc, i); tot = c + peso(gm, i)
        gm.add([i], m, "REPLACE")
        if tot > 0: gc.add([i], max(0.0, tot - m), "REPLACE")
print("CANTO suavizado verts", len(zona))
# v2: lamina do canto (juncao -> canto da fenda): faixa entre as arcadas fica livre, cranio/queixo fixos; muitas
# iteracoes espalham o esticao pela pele inteira em vez de concentrar em fios entre dentes
def z_ref(yy): return z_corte(yy) if yy <= y_canto else z_dob
livres = [v.index for v in me.vertices if Y_JUNCAO - 0.1 < v.co.y < y_canto + 0.3 and abs(v.co.z - z_ref(v.co.y)) < 0.6]
for _ in range(40):
    novo = {i: (peso(gm, i) + sum(peso(gm, j) for j in adj[i])) / (len(adj[i]) + 1) for i in livres if adj[i]}
    for i, m in novo.items(): gm.add([i], m, "REPLACE"); gc.add([i], 1.0 - m, "REPLACE")
print("LAMINA do canto verts", len(livres))
def x_labio(yy):
    ok, h, nrm, _ = lo.ray_cast(V((5, yy, z_corte(yy) + 0.2)), V((-1, 0, 0)), distance=6)
    return abs(h.x) if ok else 1.0
XL = {round(yy, 1): x_labio(yy) for yy in np.arange(fenda[0][0], y_canto + 0.1, 0.1)}
def x_dentro(yy): return XL.get(round(yy, 1), 1.0) - 0.15
REMENDOS_V1 = False   # v2: membrana/bolas/canino encurtado nao sao mais necessarios (arcadas separadas pela topologia)
memb = [] if not REMENDOS_V1 else [v.index for v in me.vertices if v.co.y < y_canto - 0.10 and abs(v.co.x) < x_dentro(v.co.y)
        and abs(v.co.z - z_corte(v.co.y)) < 0.55]
mset = set(memb)
for _ in range(40):
    novo = {}
    for i in memb:
        viz = adj[i]
        if viz: novo[i] = (peso(gm, i) + sum(peso(gm, j) for j in viz)) / (len(viz) + 1)
    for i, m in novo.items():
        gm.add([i], m, "REPLACE"); gc.add([i], 1.0 - m, "REPLACE")
print("MEMBRANA interna suavizada verts", len(memb))
# bolas locais: onde uma aresta ainda estica > 2x (+-10 graus na dobradica), o peso vira degrade num raio de 0,3
from mathutils import Matrix as _M2
cos_ = [v.co.copy() for v in me.vertices]
def pos_def(i, ang):
    R_ = _M2.Translation(V((0, y_dob, z_dob))) @ _M2.Rotation(ang, 4, "X") @ _M2.Translation(V((0, -y_dob, -z_dob)))
    w = peso(gm, i); return cos_[i] * (1 - w) + (R_ @ cos_[i]) * w
for rodada in range(4 if REMENDOS_V1 else 0):
    quentes = []
    for e in me.edges:
        i, j = e.vertices
        if max(cos_[i].y, cos_[j].y) > y_canto - 0.1: continue
        if abs(peso(gm, i) - peso(gm, j)) < 0.3: continue
        L0_ = (cos_[i] - cos_[j]).length
        for ang in (math.radians(10), math.radians(-11)):
            if (pos_def(i, ang) - pos_def(j, ang)).length > 2.0 * max(L0_, 1e-4) + 0.03: quentes.append((cos_[i] + cos_[j]) / 2); break
    if not quentes: break
    bola = {v.index for v in me.vertices if v.co.y < y_canto - 0.1 and any((v.co - c).length < 0.30 for c in quentes)}
    for _ in range(25):
        novo = {i: (peso(gm, i) + sum(peso(gm, j) for j in adj[i])) / (len(adj[i]) + 1) for i in bola if adj[i]}
        for i, m in novo.items(): gm.add([i], m, "REPLACE"); gc.add([i], 1.0 - m, "REPLACE")
    print("BOLAS rodada", rodada, "pontos quentes", len(quentes), "verts suavizados", len(bola))
    if rodada == 3:       # o que sobrou e o canino de baixo preso ao focinho: a bola inteira vai com a mandibula
        for i in bola: gm.add([i], 1.0, "REPLACE"); gc.add([i], 0.0, "REPLACE")
        print("BOLAS teimosas -> mandibula", len(bola), "centros", [tuple(round(c_, 2) for c_ in q) for q in quentes])
# testado 03/11: mandar mais bolas inteiras para um lado so (caninos de cima) cria bordas novas e piora (ate 7,7x);
# o canino de cima fica com a ponta presa na gengiva de baixo -> os clipes nao abrem alem da boca do Meshy (ABRE_MAX = 0)
# canino de baixo esquerdo (4o dente): no Meshy a ponta encosta na ponta do canino de cima e, ao fechar, fura o
# focinho. Encurtado para 55% da altura a partir da base: a ponta para dentro do canino de cima.
# So os vertices da mandibula num cilindro em volta do dente.
EIXO_CANINO, Z_CONTATO = (0.98, -13.86), 3.56        # contato ponta-a-ponta com o canino de cima (medido no repouso)
can, cima = [], []
for v in (me.vertices if REMENDOS_V1 else []):
    if math.hypot(v.co.x - EIXO_CANINO[0], v.co.y - EIXO_CANINO[1]) >= 0.30 or not (2.85 < v.co.z < 3.85): continue
    if v.co.z > Z_CONTATO: cima.append(v)                 # ponta do canino de cima: volta para o cranio, sem mover
    elif peso(gm, v.index) >= 0.5: can.append(v)
for v in cima: gm.add([v.index], 0.0, "REPLACE"); gc.add([v.index], 1.0, "REPLACE")
if can:
    zb = min(v.co.z for v in can)
    for v in can: v.co.z = zb + (v.co.z - zb) * 0.55     # inclinar para fora (testado) fica enterrado na lateral do focinho
    me.update()
print("CANINO encurtado verts", len(can), "ponta do canino de cima -> cabeca", len(cima))
# normaliza (no maximo 4 influencias, como o Roblox)
bpy.ops.object.select_all(action="DESELECT"); lo.select_set(True); bpy.context.view_layer.objects.active = lo
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)

# ------------------------------------------------------------------ IK por pata (alvos Empties; polo para fora)
def angulo_polo(base, ik, polo):
    """formula classica: angulo de polo que preserva a pose de repouso"""
    normal = (ik.tail - base.head).cross(polo - base.head)
    eixo = normal.cross(base.tail - base.head)
    a = base.x_axis.angle(eixo)
    if base.x_axis.cross(eixo).dot(base.tail - base.head) < 0: a = -a
    return a
ALVOS = {}
for lado, sx in (("E", 1), ("D", -1)):
    for par, nomes in (("dian", ("Braco", "Antebraco", "Mao")), ("tras", ("Coxa", "Canela", "Pe"))):
        b0, b1, b2 = (arm.data.bones[n_ + lado] for n_ in nomes)
        alvo = bpy.data.objects.new("IK_" + nomes[2] + lado, None); sc.collection.objects.link(alvo)
        alvo.location = b2.head_local.copy(); alvo.empty_display_size = 0.5
        polo = bpy.data.objects.new("Polo_" + nomes[1] + lado, None); sc.collection.objects.link(polo)
        polo.location = b1.head_local + V((2.5 * sx, 1.2 if par == "dian" else -1.2, 0.3))
        pb = arm.pose.bones[nomes[1] + lado]; c = pb.constraints.new("IK")
        c.target = alvo; c.pole_target = polo; c.chain_count = 2; c.use_tail = True
        c.pole_angle = angulo_polo(b0, b1, polo.location)
        # use_tail: a ponta do antebraco/canela (= punho/tornozelo) persegue o alvo
        pm = arm.pose.bones[nomes[2] + lado]; cr = pm.constraints.new("COPY_ROTATION"); cr.target = alvo   # mao/pe segue o alvo
        cr.mix_mode = "REPLACE"; cr.target_space = "WORLD"; cr.owner_space = "WORLD"
        alvo.rotation_mode = "QUATERNION"; alvo.rotation_quaternion = (arm.matrix_world @ b2.matrix_local).to_quaternion()
        ALVOS[nomes[2] + lado] = (alvo, polo)
bpy.context.view_layer.update()
# angulo de polo por busca: o que deixa o cotovelo/joelho exatamente no lugar de repouso
for lado in ("E", "D"):
    for nomes in (("Braco", "Antebraco"), ("Coxa", "Canela")):
        c = arm.pose.bones[nomes[1] + lado].constraints["IK"]; b0 = arm.data.bones[nomes[0] + lado]
        def erro(a_):
            c.pole_angle = a_; bpy.context.view_layer.update()
            return (arm.pose.bones[b0.name].tail - b0.tail_local).length
        melhor = min((erro(math.radians(g)), math.radians(g)) for g in range(-180, 180, 3))
        a_ = melhor[1]
        for passo in (1.0, 0.25, 0.05):
            cand = [a_ + math.radians(passo * k) for k in range(-4, 5)]
            a_ = min(cand, key=erro)
        c.pole_angle = a_; print("POLO", nomes[1] + lado, round(math.degrees(a_), 2), "erro", round(erro(a_), 4))
bpy.context.view_layer.update()
# conferencia: com os alvos no lugar de repouso, a pose nao pode mudar
desvio = max((arm.pose.bones[b.name].matrix.translation - b.matrix_local.translation).length +
             (arm.pose.bones[b.name].tail - b.tail_local).length for b in arm.data.bones)
print("IK desvio_repouso_max %.4f" % desvio)
for b in arm.data.bones:
    d_ = (arm.pose.bones[b.name].tail - b.tail_local).length
    if d_ > 0.01: print("IK desvio", b.name, round(d_, 3))
arm["y_juncao"] = Y_JUNCAO
arm["y_canto"], arm["y_dob"], arm["z_dob"], arm["ang_boca"] = y_canto, y_dob, z_dob, math.degrees(math.atan2(fenda[0][2], (y_dob - fenda[0][0])))
print("ANGULO boca aberta no repouso %.1f graus" % arm["ang_boca"])
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath), "CR_Crocodilo_Rig.blend"))
print("RIG_FINAL_OK ossos", len(arm_d.bones), [b.name for b in arm_d.bones])
