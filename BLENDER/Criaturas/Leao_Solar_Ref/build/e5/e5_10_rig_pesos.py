"""E5 (rig de producao, pesos). Mudancas sobre r2_03 (build/e4b_r2):
- mascara da juba pela COR AVERMELHADA (vermelho/verde > 1,66 e saturacao > 0,74): a saturacao sozinha pegava o pelo dourado
  do alto do cotovelo (na E4b r2 isso foi diagnosticado errado como "mecha fundida"; os cortes da E3b e da E4b mostram
  que a pata e uma coluna limpa ligada ao peito, sem mecha sobre o antebraco);
- pata dianteira por PERTENCIMENTO geometrico: abaixo do cotovelo, dentro do raio da pata = so ossos da pata; em volta do
  umero (dentro do corpo) a fracao da pata cai suave com a distancia ate o umero (1,5 -> 3,3, inclui o cotovelo por tras); juba sobre o ombro segue a
  pata em 35% (rola com a escapula); o resto e do tronco. Reaplicado depois da suavizacao.
E4b r2 (correcao de cotovelo, punho e juba do peito; mesma malha da E4b). Mudancas sobre e4b_03:
- ossos auxiliares de volume Cotovelo_Aux/Punho_Aux (filhos de Umero/Antebraco, mesma orientacao de repouso do filho,
  giram METADE do filho): a faixa de mistura vira pai -> aux -> filho (o afinamento cai de cos(a/2) para cos(a/4));
- pata dianteira abaixo do meio do umero: peso do tronco (Peito/Coluna/Juba) volta para os ossos da pata;
- fora da pata dianteira: o peso da pata cai suave com a distancia ate o eixo da pata (faixa larga) em vez da mascara da juba.
E4b passo 3: rig de TESTE completo (mesma hierarquia pensada para o rig final) e pesos limpos.
Ossos: Raiz (chao, sem deformar) > Quadril > Coluna1 > Coluna2 > Peito > Pescoco1 > Pescoco2 > Cabeca > Mandibula >
Lingua1 > Lingua2; Escapula/Umero/Antebraco/Mao/Dedos (dianteiras, filhas do Peito); Coxa/Canela/Metatarso/Dedos
(traseiras, filhas do Quadril); Cauda1..6 (filhas do Quadril); Tufo1..2 (secundarios do tufo, filhos da Cauda4);
Juba_<setor>_1..2 (8 setores em volta do pescoco, secundarios, filhos do Pescoco1).
Pesos:
- corpo, patas, cauda: calor (pesos automaticos) com os ossos secundarios/boca desligados;
- boca: a fracao da mandibula vem do gerador da boca (c02): a influencia da cabeca+pescoco2 e repartida em Cabeca e
  Mandibula; interior/dentes/lingua por peca (dentes sup. = Cabeca, inf. = Mandibula, lingua = Mandibula/Lingua1/Lingua2);
- juba: mascara por cor (laranja saturado do albedo assado) e posicao; peso secundario cresce para fora do pescoco,
  repartido entre os 2 setores mais proximos e os 2 ossos da cadeia;
- tufo: pelos do tufo (fora do miolo da cauda) para Tufo1/Tufo2;
- limite de 4 influencias, limpeza (<0,01), normalizacao; relatorio.
Uso: blender -b <e4b_semrig.blend> -P e4b_03_rig_pesos.py -- <juntas.json> <saida.blend> <relatorio.json>"""
import bpy, bmesh, sys, json, math, os
U0 = float(os.environ.get('R2_U0', '1.2')); FORA = os.environ.get('R2_FORA', 'orig'); BANDA = float(os.environ.get('R2_BANDA', '1.8'))
print('VARIANTE U0', U0, 'FORA', FORA, 'BANDA', BANDA)
import numpy as np
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; J = json.load(open(A[0])); OUT, REL = A[1], A[2]; SUAV = int(A[3]) if len(A) > 3 else 12
sc = bpy.context.scene
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; me = ob.data
rig_boca = bpy.data.objects.get("Leao_Rig_Teste_Boca")
lin_h = rig_boca.data.bones["Lingua"].head_local.copy() if rig_boca else None; lin_t = rig_boca.data.bones["Lingua"].tail_local.copy() if rig_boca else None
n = len(me.vertices); co = np.array([v.co for v in me.vertices])
def grupo_arr(nome):
    a = np.zeros(n)
    if nome not in ob.vertex_groups: return a
    gi = ob.vertex_groups[nome].index
    for v in me.vertices:
        for g in v.groups:
            if g.group == gi: a[v.index] = g.weight
    return a
M_C02 = grupo_arr("Mandibula"); L_C02 = grupo_arr("Lingua"); PROF = grupo_arr("Boca_Profundo")
# cascas: 0 = corpo; pecas = dentes/lingua
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); casca = -np.ones(n, int); k = 0
for v in bm.verts:
    if casca[v.index] >= 0: continue
    pilha = [v]; casca[v.index] = k
    while pilha:
        x = pilha.pop()
        for e in x.link_edges:
            y = e.other_vert(x)
            if casca[y.index] < 0: casca[y.index] = k; pilha.append(y)
    k += 1
tam = np.bincount(casca); corpo_id = int(np.argmax(tam)); bm.free()
eh_peca = casca != corpo_id
eh_lingua = eh_peca & (L_C02 > 0) | eh_peca & np.isin(casca, [c for c in np.unique(casca[eh_peca]) if (L_C02[casca == c] > 0).any()])
eh_dente_inf = eh_peca & ~eh_lingua & (M_C02 > 0.5); eh_dente_sup = eh_peca & ~eh_lingua & ~eh_dente_inf
print("PECAS lingua", int(eh_lingua.sum()), "dentes sup", int(eh_dente_sup.sum()), "dentes inf", int(eh_dente_inf.sum()))
for o in list(bpy.data.objects):
    if o.type == "ARMATURE": bpy.data.objects.remove(o, do_unlink=True)
for m in list(ob.modifiers): ob.modifiers.remove(m)
ob.vertex_groups.clear()
# ---------------------------------------------------------------- esqueleto
ad = bpy.data.armatures.new("Leao_Solar_Rig_Teste"); arm = bpy.data.objects.new("Leao_Solar_Rig_Teste", ad); sc.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT")
def Vv(p): return Vector(p)
def osso(nome, a, b, pai=None, deform=True, conectar=False):
    e = ad.edit_bones.new(nome); e.head = Vv(a); e.tail = Vv(b); e.use_deform = deform
    if pai: e.parent = ad.edit_bones[pai]; e.use_connect = conectar and (ad.edit_bones[pai].tail - e.head).length < 1e-4
    return nome
C = J["coluna"]; P = J["pescoco"]
osso("Raiz", (0, 0, 0), (0, 0, 1.5), deform=False)
osso("Quadril", C[0], C[1], "Raiz"); osso("Coluna1", C[1], C[2], "Quadril", conectar=True); osso("Coluna2", C[2], C[3], "Coluna1", conectar=True)
osso("Peito", C[3], C[4], "Coluna2", conectar=True); osso("Pescoco1", P[0], P[1], "Peito", conectar=True); osso("Pescoco2", P[1], P[2], "Pescoco1", conectar=True)
osso("Cabeca", P[2], J["cabeca_fim"], "Pescoco2", conectar=True)
osso("Mandibula", J["mandibula"]["pivo"], J["mandibula"]["queixo"], "Cabeca")
if lin_h is not None:
    meio_l = (lin_h + lin_t) / 2; osso("Lingua1", lin_h, meio_l, "Mandibula"); osso("Lingua2", meio_l, lin_t, "Lingua1", conectar=True)
for perna in ("DD", "DE"):
    d = J[perna]; s = 1 if perna.endswith("D") else -1; esc_top = (s * 0.9, d["ombro"][1] + 2.3, 11.0)
    osso("Escapula_" + perna, esc_top, d["ombro"], "Peito"); osso("Umero_" + perna, d["ombro"], d["cotovelo"], "Escapula_" + perna, conectar=True)
    osso("Antebraco_" + perna, d["cotovelo"], d["punho"], "Umero_" + perna, conectar=True); osso("Mao_" + perna, d["punho"], d["pata"], "Antebraco_" + perna, conectar=True)
    osso("Dedos_" + perna, d["pata"], d["dedos"], "Mao_" + perna, conectar=True)
    c_, p_, a_ = (np.array(d[k], float) for k in ("cotovelo", "punho", "pata"))
    osso("Cotovelo_Aux_" + perna, c_, c_ + (p_ - c_) * 0.35, "Umero_" + perna); osso("Punho_Aux_" + perna, p_, p_ + (a_ - p_) * 0.6, "Antebraco_" + perna)
for perna in ("TD", "TE"):
    d = J[perna]
    osso("Coxa_" + perna, d["quadril"], d["joelho"], "Quadril"); osso("Canela_" + perna, d["joelho"], d["jarrete"], "Coxa_" + perna, conectar=True)
    osso("Metatarso_" + perna, d["jarrete"], d["pata"], "Canela_" + perna, conectar=True); osso("Dedos_" + perna, d["pata"], d["dedos"], "Metatarso_" + perna, conectar=True)
T = J["cauda"]; pai = "Quadril"
for i in range(len(T) - 1): pai = osso("Cauda%d" % (i + 1), T[i], T[i + 1], pai, conectar=(i > 0))
osso("Tufo1", T[4], T[5], "Cauda4", deform=False); osso("Tufo2", T[5], T[6], "Tufo1", deform=False, conectar=True)
# juba: eixo do pescoco e 8 setores
eixo_a = np.array(P[0], float); eixo_b = np.array(P[2], float); ax = (eixo_b - eixo_a) / np.linalg.norm(eixo_b - eixo_a)
up = np.array([0, 0, 1.0]) - ax * ax[2]; up /= np.linalg.norm(up); lado = np.cross(ax, up)
cent = eixo_a + (eixo_b - eixo_a) * 0.45
SET = ["Topo", "TopoD", "Dir", "BaixoD", "Peito", "BaixoE", "Esq", "TopoE"]
ANG = [i * math.pi / 4 for i in range(8)]                    # 0 = topo, sentido para X+ (lado)
def dir_setor(a): return up * math.cos(a) + lado * math.sin(a)
for nome, a in zip(SET, ANG):
    d = dir_setor(a); r0 = cent + d * 1.6; r1 = cent + d * 3.0 + ax * -0.4; r2 = cent + d * 4.3 + ax * -0.9
    osso("Juba_%s_1" % nome, r0, r1, "Pescoco1", deform=False); osso("Juba_%s_2" % nome, r1, r2, "Juba_%s_1" % nome, deform=False, conectar=True)
bpy.ops.object.mode_set(mode="OBJECT")
NAO_CALOR = {"Mandibula", "Lingua1", "Lingua2", "Cotovelo_Aux_DD", "Cotovelo_Aux_DE", "Punho_Aux_DD", "Punho_Aux_DE"}
for b in ad.bones:
    if b.name in NAO_CALOR: b.use_deform = False
# ---------------------------------------------------------------- calor (corpo)
for o in sc.objects: o.select_set(False)
ob.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
for b in ad.bones: b.use_deform = b.name != "Raiz"
W = {g.name: grupo_arr(g.name) for g in ob.vertex_groups}
for b in ad.bones:
    if b.use_deform and b.name not in W: W[b.name] = np.zeros(n)
sem_calor = np.array([sum(W[k][i] for k in W) < 1e-3 for i in range(n)])
print("CALOR vertices sem peso:", int(sem_calor.sum()), "(dentes/lingua sao cascas soltas)", int((sem_calor & ~eh_peca).sum()), "no corpo")
# corpo sem peso (se houver): herda do vizinho mais proximo com peso
if (sem_calor & ~eh_peca).any():
    com = np.nonzero(~sem_calor & ~eh_peca)[0]
    for i in np.nonzero(sem_calor & ~eh_peca)[0]:
        j = com[np.argmin(np.linalg.norm(co[com] - co[i], axis=1))]
        for k_ in W: W[k_][i] = W[k_][j]
def zera(i):
    for k_ in W: W[k_][i] = 0.0
# ---------------------------------------------------------------- boca
cab_pesc = W["Cabeca"] + W["Pescoco2"]
na_cabeca = (co[:, 1] < -11.4) & ~eh_peca
for i in np.nonzero(na_cabeca & (M_C02 > 1e-4))[0]:
    m = M_C02[i]; h = W["Cabeca"][i]; p2 = W["Pescoco2"][i]
    W["Mandibula"][i] = m * (h + p2); W["Cabeca"][i] = h * (1 - m); W["Pescoco2"][i] = p2 * (1 - m)
interior = (PROF > 0.5) & ~eh_peca
for i in np.nonzero(interior)[0]:                             # interior profundo: so cabeca/mandibula (calor dentro da cabeca e ruido)
    m = M_C02[i]; zera(i); W["Cabeca"][i] = 1 - m; W["Mandibula"][i] = m
for i in np.nonzero(eh_dente_sup)[0]: zera(i); W["Cabeca"][i] = 1.0
for i in np.nonzero(eh_dente_inf)[0]: zera(i); W["Mandibula"][i] = 1.0
if lin_h is not None:
    lh, lt = np.array(lin_h), np.array(lin_t); L = np.linalg.norm(lt - lh)
    for i in np.nonzero(eh_lingua)[0]:
        t = np.clip((co[i] - lh) @ (lt - lh) / L ** 2, 0, 1); wl = max(L_C02[i], 0.25 * t)
        zera(i); W["Mandibula"][i] = 1 - wl; W["Lingua2"][i] = wl * t; W["Lingua1"][i] = wl * (1 - t)
# ---------------------------------------------------------------- juba (cor + posicao)
uvd = me.uv_layers.active.data; img = None
for m_ in me.materials:
    for nd in m_.node_tree.nodes:
        if nd.type == "TEX_IMAGE" and nd.image and nd.image.colorspace_settings.name == "sRGB": img = nd.image
R = img.size[0]; px = np.array(img.pixels[:], np.float32).reshape(R, R, -1)[..., :3]
uvv = np.zeros((n, 2)); cnt = np.zeros(n)
for l in me.loops: uvv[l.vertex_index] += uvd[l.index].uv; cnt[l.vertex_index] += 1
uvv /= np.maximum(cnt, 1)[:, None]
cor = px[np.clip((uvv[:, 1] * R).astype(int), 0, R - 1), np.clip((uvv[:, 0] * R).astype(int), 0, R - 1)]
mx, mn = cor.max(1), cor.min(1); sat = (mx - mn) / np.maximum(mx, 1e-4)
rel_ = co - cent; along = rel_ @ ax; radial = rel_ - along[:, None] * ax; dist = np.linalg.norm(radial, axis=1)
def s(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
rosto = (co[:, 1] < -12.6) & (co[:, 2] > 10.6) & (np.abs(co[:, 0] + 0.23) < 1.9)
rg = cor[:, 0] / np.maximum(cor[:, 1], 1e-3)
juba = (rg > 1.66) & (sat > 0.74) & (mx > 0.35) & (co[:, 1] > -14.8) & (co[:, 1] < -2.5) & (co[:, 2] > 3.0) & ~rosto & ~eh_peca & (PROF < 0.5)
# mechas da juba nao seguem os ossos das patas (caem sobre ombro e antebraco): o peso das patas vai para Peito/Pescoco1,
# com transicao suave para fora da mascara (2 aneis de vizinhos)
def s_(x): return s(x)
def seg_dist(P, a, b):
    ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1); return np.linalg.norm(P - (a + t[:, None] * ab), axis=1), t
viz = [[] for _ in range(n)]
for e in me.edges: a_, b_ = e.vertices; viz[a_].append(b_); viz[b_].append(a_)
# mechas longas que pendem do peito ate a altura do antebraco: o voxel/decimacao as deixou como triangulos compridos
# (aresta > 0,8) e a cor nem sempre passa no limiar da mascara. Testado: soltar essas mechas da pata so leva o esticamento
# para a pele do antebraco (a ponta esta fundida nela); ficam com a pata e o esticamento fica na propria mecha (pelo).
# A mascara de cor vai para o atributo de QA "qa_juba" (so para as medicoes; remover antes de exportar).
Lmax = np.zeros(n); EE = np.array([e.vertices[:] for e in me.edges]); LL = np.linalg.norm(co[EE[:, 0]] - co[EE[:, 1]], axis=1)
np.maximum.at(Lmax, EE[:, 0], LL); np.maximum.at(Lmax, EE[:, 1], LL)
mecha = (Lmax > 0.8) & (co[:, 1] > -11.5) & (co[:, 1] < -4.0) & (co[:, 2] > 1.5) & (co[:, 2] < 8.0) & ~rosto & ~eh_peca & (PROF < 0.5)
print("MECHAS longas (fora da mascara de cor):", int((mecha & ~juba).sum()), "vertices")
fm = mecha.astype(float)
for _ in range(2): fm = np.maximum(fm, np.array([0.5 * max((fm[j] for j in viz[i]), default=0) for i in range(n)]))
fj = juba.astype(float)
for _ in range(2): fj = np.maximum(fj, np.array([0.5 * max((fj[j] for j in viz[i]), default=0) for i in range(n)]))
PERNA = {}
TRONCO_OK = ("Peito", "Pescoco1")
for perna in ("DD", "DE"):
    d = J[perna]; pts = [np.array(d[k], float) for k in ("ombro", "cotovelo", "punho", "pata", "dedos")]
    Dp = np.full(n, 1e9); Up = np.zeros(n)
    for k in range(4):
        dk, tk = seg_dist(co, pts[k], pts[k + 1]); m = dk < Dp; Dp[m] = dk[m]; Up[m] = k + tk[m]
    ossos = [b + "_" + perna for b in ("Escapula", "Umero", "Antebraco", "Mao", "Dedos")]
    wl = sum(W[b] for b in ossos)
    # raio real da pata: medido onde a pata e um cilindro isolado (antebraco/pata, abaixo do peito); acima do cotovelo
    # a pata encosta no peito, entao o raio cresce so um pouco (25%) ate o ombro em vez de ser medido (o peito contamina)
    sx = 1 if perna == "DD" else -1; lado_ok = (co[:, 0] * sx > 0.45) & ~eh_peca
    cen = np.arange(1.25, 4.0, 0.5); R = []
    for c in cen:
        sel = lado_ok & (np.abs(Up - c) < 0.25) & (Dp < 1.6) & (co[:, 2] < 4.3) & (fj == 0)   # sem as mechas que pendem junto da pata
        R.append(np.percentile(Dp[sel], 95) if sel.sum() > 15 else np.nan)
    R = np.array(R); ok = ~np.isnan(R); R = np.interp(cen, cen[ok], R[ok])
    cen = np.concatenate([[0.0, 0.6], cen]); R = np.concatenate([[R[0] * 1.25, R[0] * 1.15], R]); Rv = np.interp(Up, cen, R)
    PERNA[perna] = (Dp, Up, Rv, ossos)
    print("PERNA", perna, "raio por faixa u:", np.round(R, 2).tolist())
TORSO_SEC = None
def pertence(perna, Rv, sx):
    """fracao da pata dianteira por vertice (0..1): max(em volta do umero/cotovelo, dentro do antebraco/pata)"""
    d = J[perna]; pts = [np.array(d[k], float) for k in ("ombro", "cotovelo", "punho", "pata", "dedos")]
    Dh, _ = seg_dist(co, pts[0], pts[1])                                       # umero (inclui o ponto do cotovelo)
    Db = np.min([seg_dist(co, pts[k], pts[k + 1])[0] for k in (1, 2, 3)], axis=0)
    alto = (1 - s_((Dh - 1.5) / 1.8)) * s_((co[:, 0] * sx - 0.15) / 0.35)    # massa do braco/cotovelo: cai devagar ate o tronco
    baixo = 1 - s_((Db - (Rv + 0.2)) / 0.6)                                    # antebraco/pata: cilindro (inclui o lado de dentro)
    m = np.maximum(alto, baixo) * ~na_cabeca * ~eh_peca * (PROF < 0.5)
    m = np.where(juba & (baixo < 0.5), 0.35 * m, m)                            # juba sobre o ombro: rola com a escapula, sem ser arrastada
    return m
def aplica(Wd, ossos, m, perto):
    pat = sum(Wd[k_] for k_ in ossos); outros = [k_ for k_ in Wd if k_ not in ossos]; tor = sum(Wd[k_] for k_ in outros)
    sel = np.nonzero((m > 1e-4) | (pat > 1e-4))[0]
    for i in sel:
        if pat[i] > 1e-6:
            for k_ in ossos: Wd[k_][i] = m[i] * Wd[k_][i] / pat[i]
        else:
            for k_ in ossos: Wd[k_][i] = m[i] * (k_ == perto[i])
        if tor[i] > 1e-6:
            for k_ in outros: Wd[k_][i] = (1 - m[i]) * Wd[k_][i] / tor[i]
        else:
            Wd["Pescoco1" if (co[i, 1] < -8.5 and co[i, 2] > 10.0) else "Peito"][i] = 1 - m[i]
MEMB = {}
for perna, (Dp, Up, Rv, ossos) in PERNA.items():
    sx = 1 if perna == "DD" else -1; m = pertence(perna, Rv, sx); perto = np.array([ossos[min(4, 1 + int(u))] for u in Up])
    MEMB[perna] = (m, perto); aplica(W, ossos, m, perto)
    print("PERTENCE", perna, "vertices com pata>0.5:", int((m > 0.5).sum()), "juba sobre o ombro:", int((juba & (m > 0.01)).sum()))
wsec = juba * s((dist - 1.7) / 2.4) * s((along + 6.0) / 2.0) * s((4.5 - along) / 1.5) * 0.85
ang = np.arctan2(radial @ lado, radial @ up)
for i in np.nonzero(wsec > 0.01)[0]:
    a = ang[i] % (2 * math.pi); k0 = int(a // (math.pi / 4)) % 8; k1 = (k0 + 1) % 8; f = (a - k0 * math.pi / 4) / (math.pi / 4)
    t = s((dist[i] - 2.4) / 1.8)                              # perto da raiz: osso 1; pontas: osso 2
    base = 1 - wsec[i]
    for k_ in W: W[k_][i] *= base
    for kk, fk in ((k0, 1 - f), (k1, f)):
        W["Juba_%s_1" % SET[kk]][i] += wsec[i] * fk * (1 - t); W["Juba_%s_2" % SET[kk]][i] += wsec[i] * fk * t
print("JUBA vertices com peso secundario:", int((wsec > 0.01).sum()), "de", int(juba.sum()), "na mascara")
# ---------------------------------------------------------------- tufo (pelos fora do miolo da cauda)
t4, t6 = np.array(T[4], float), np.array(T[6], float); dt = (t6 - t4) / np.linalg.norm(t6 - t4)
rt = co - t4; at = rt @ dt; dl = np.linalg.norm(rt - at[:, None] * dt, axis=1)
tufo = (at > -0.6) & (co[:, 1] > 13.0) & ~eh_peca
wt = tufo * s((dl - 0.28) / 0.45) * 0.8
for i in np.nonzero(wt > 0.01)[0]:
    q = np.clip(at[i] / np.linalg.norm(t6 - t4), 0, 1); base = 1 - wt[i]
    for k_ in W: W[k_][i] *= base
    W["Tufo1"][i] += wt[i] * (1 - q); W["Tufo2"][i] += wt[i] * q
print("TUFO vertices com peso secundario:", int((wt > 0.01).sum()))
# ---------------------------------------------------------------- limite 4, limpeza, normalizacao
nomes = list(W.keys()); Wm = np.stack([W[k_] for k_ in nomes], 1)
# suavizacao dos pesos fora da cabeca (as transferencias juba/pata e a juba fundida a pele pelo voxel deixam degraus)
E0 = np.array([e.vertices[0] for e in me.edges]); E1 = np.array([e.vertices[1] for e in me.edges])
liv = ~((co[:, 1] < -12.3) & (co[:, 2] > 10.3) & (np.abs(co[:, 0] + 0.23) < 2.0)) & ~eh_peca & (PROF < 0.5); deg = np.bincount(E0, minlength=n) + np.bincount(E1, minlength=n)
for _ in range(SUAV):
    S = np.zeros_like(Wm); np.add.at(S, E0, Wm[E1]); np.add.at(S, E1, Wm[E0])
    Wn = 0.5 * Wm + 0.5 * S / np.maximum(deg, 1)[:, None]; Wm[liv] = Wn[liv]
print("SUAVIZACAO dos pesos:", SUAV, "passos em", int(liv.sum()), "vertices")
Wd = {k_: Wm[:, j] for j, k_ in enumerate(nomes)}
for perna, (Dp, Up, Rv, ossos) in PERNA.items():
    m, perto = MEMB[perna]; aplica(Wd, ossos + [b for b in Wd if b.startswith(("Cotovelo_Aux", "Punho_Aux")) and b.endswith(perna)], m, perto)   # reaplica depois da suavizacao
    for pai_, fil_, aux_ in (("Umero", "Antebraco", "Cotovelo_Aux"), ("Antebraco", "Mao", "Punho_Aux")):
        a_, b_, x_ = Wd[pai_ + "_" + perna], Wd[fil_ + "_" + perna], Wd[aux_ + "_" + perna]
        S_ = a_ + b_; sel = (a_ > 0.005) & (b_ > 0.005)
        t_ = np.where(sel, b_ / np.maximum(S_, 1e-9), 0); h_ = np.where(sel, S_ * (1 - np.abs(2 * t_ - 1)), 0)
        x_ += h_; a_[sel] = (S_ * (1 - t_) - h_ / 2)[sel]; b_[sel] = (S_ * t_ - h_ / 2)[sel]
        print("AUX", aux_ + "_" + perna, int((h_ > 0.01).sum()), "vertices")
Wm[Wm < 0.01] = 0
ordem = np.argsort(-Wm, axis=1); corte = np.zeros_like(Wm, bool)
np.put_along_axis(corte, ordem[:, :4], True, axis=1); Wm = Wm * corte
Wm[Wm < 0.01] = 0; soma = Wm.sum(1, keepdims=True); Wm = Wm / np.maximum(soma, 1e-9)
ob.vertex_groups.clear()
for j, k_ in enumerate(nomes):
    if not Wm[:, j].any(): continue
    g = ob.vertex_groups.new(name=k_)
    for i in np.nonzero(Wm[:, j])[0]: g.add([int(i)], float(Wm[i, j]), "REPLACE")
for b in ad.bones: b.use_deform = b.name != "Raiz"
mo = ob.modifiers.get("Armature") or ob.modifiers.new("Armature", "ARMATURE"); mo.object = arm; mo.use_deform_preserve_volume = False
infl = (Wm > 0).sum(1); soma = Wm.sum(1)
rel = {"vertices": n, "sem_peso": int((infl == 0).sum()), "influencias_max": int(infl.max()), "hist_influencias": {str(k_): int((infl == k_).sum()) for k_ in range(0, 5)},
       "mal_normalizados_|soma-1|>1e-3": int((np.abs(soma - 1) > 1e-3).sum()), "ossos": len(ad.bones), "ossos_deformam": sum(1 for b in ad.bones if b.use_deform),
       "grupos_com_peso": len(ob.vertex_groups), "juba_vertices_secundarios": int((wsec > 0.01).sum()), "tufo_vertices_secundarios": int((wt > 0.01).sum()),
       "hierarquia": {b.name: (b.parent.name if b.parent else None) for b in ad.bones}}
json.dump(rel, open(REL, "w"), indent=1); print("PESOS", json.dumps({k_: v for k_, v in rel.items() if k_ != "hierarquia"}))

qa = me.attributes.get("qa_juba") or me.attributes.new("qa_juba", "FLOAT", "POINT"); qa.data.foreach_set("value", juba.astype(np.float32))   # so a mascara de cor (as arestas longas dos aneis da pata tambem passam de 0,8)
ob.parent = arm
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("RIG_OK")
