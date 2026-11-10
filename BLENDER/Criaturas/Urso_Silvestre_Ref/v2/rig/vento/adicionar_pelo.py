"""Pelo ao vento, opcao A (04/11/2026, autorizada so no Blender: "Sim, opcao A no Blender").
Cria uma VARIANTE do rig com ossos curtos Pelo* para as mechas expostas, sem tocar no CR_Urso_v2_Rig.blend original:
  - os 31 ossos atuais ficam com os mesmos nomes, posicoes e hierarquia;
  - cada Pelo* e filho do osso do corpo da sua regiao e so recebe peso nas PONTAS das mechas (relevo alto da malha);
  - rosto, boca, orelhas, patas (antebraco/mao/dedos, canela/pe/dedos) ficam com peso 0 nos Pelo*;
  - areas lisas e largas (placas, base do pelo) quase nao recebem peso -> ficam firmes;
  - ate 4 influencias por vertice; o peso do Pelo* sai SO do osso pai dele. Sem vaga (4 influencias), o Pelo* assume
    todo o peso do pai, so nas pontas (relevo suavizado >= LIMIAR_TROCA, padrao 0,25). Medido 04/11: liberar vaga movendo a menor influencia mudava
    a malha ate 0,58 stud no Deitar/Comer -> descartado.
  - (antes: (no maximo o peso que o pai tem no vertice).
    Com o Pelo* parado (pose de descanso) o vertice segue o pai exatamente como antes -> os 18 clipes deformam igual.
    Vertices que ja tem 4 influencias (sem vaga) ficam de fora. Medido 04/11: tirar peso de todos os ossos mudava o
    Sentar/Deitar (vertices passavam a seguir outro osso).
Relevo = deslocamento do vertice em relacao a malha suavizada (Taubin, sem encolher), na direcao da normal.
Uso: blender -b ../CR_Urso_v2_Rig.blend -P adicionar_pelo.py -- <saida.blend> [peso_max]"""
import bpy, bmesh, sys, os, json
from mathutils import Vector as V
A_ = sys.argv[sys.argv.index("--") + 1:]; SAIDA = os.path.abspath(A_[0]); PMAX = float(A_[1]) if len(A_) > 1 else 0.55
arm = bpy.data.objects["Urso_Rig"]
EXCL = {"Cabeca", "Mandibula", "OrelhaE", "OrelhaD", "AntebracoE", "MaoE", "DedosE", "AntebracoD", "MaoD", "DedosD",
        "CanelaE", "PeE", "DedosPeE", "CanelaD", "PeD", "DedosPeD", "Raiz"}
# regioes: (osso novo, osso pai, centro y) -- o urso olha para -y; cadeias interpoladas por y
DORSO = [("PeloGarupa", "Pelve", 4.6), ("PeloDorso1", "Coluna1", 2.4), ("PeloDorso2", "Coluna2", -0.2),
         ("PeloDorso3", "Coluna3", -2.0), ("PeloJuba", "Pescoco", -3.4)]
BARRIGA = [("PeloBarrigaT", "Coluna1", 2.5), ("PeloBarrigaF", "Coluna2", -0.5)]
OMBRO = {1: ("PeloOmbroE", "EscapulaE"), -1: ("PeloOmbroD", "EscapulaD")}
PAI = {n: p for n, p, _ in DORSO + BARRIGA}; PAI.update({n: p for n, p in OMBRO.values()})
def interp(cadeia, y):
    ys = [c[2] for c in cadeia]
    if y >= ys[0]: return [(cadeia[0][0], 1.0)]
    if y <= ys[-1]: return [(cadeia[-1][0], 1.0)]
    for i in range(len(ys) - 1):
        if ys[i] >= y >= ys[i + 1]:
            f = (ys[i] - y) / (ys[i] - ys[i + 1]); return [(cadeia[i][0], 1 - f), (cadeia[i + 1][0], f)]
def relevo(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    P = [v.co.copy() for v in bm.verts]; S = [p.copy() for p in P]; viz = [[e.other_vert(v).index for e in v.link_edges] for v in bm.verts]
    def passo(S, f):
        M = [(sum((S[j] for j in viz[i]), V()) / len(viz[i])) if viz[i] else S[i] for i in range(len(S))]
        return [S[i] + (M[i] - S[i]) * f for i in range(len(S))]
    for _ in range(12): S = passo(passo(S, 0.6), -0.63)
    N = [v.normal.copy() for v in bm.verts]; bm.free()
    return [(P[i] - S[i]).dot(N[i]) for i in range(len(P))], N, viz
BS = []
pesos = {}       # (obj, vi) -> {osso_pelo: peso}
regiao_pts = {}  # osso -> [(pos, normal, peso)]
for o in [bpy.data.objects[n] for n in ("Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Cabeca")]:
    gn = {g.index: g.name for g in o.vertex_groups}; sal, N, viz = relevo(o); mw = o.matrix_world; m3 = mw.to_3x3()
    bruto = [0.0] * len(sal); dest = [None] * len(sal)
    for v in o.data.vertices:
        if not v.groups: continue
        dom = gn[max(v.groups, key=lambda g: g.weight).group]
        if dom in EXCL: continue
        s = max(0.0, min(1.0, (sal[v.index] - 0.02) / 0.12))
        if s <= 0: continue
        p = mw @ v.co; n = (m3 @ N[v.index]).normalized()
        if n.z > 0.25 and p.z > 5.5 and p.y > -4.3:
            reg = "Dorso"; fall = 1.0 if p.y > -3.9 else max(0.0, (p.y + 4.3) / 0.4)      # some antes da cabeca
        elif abs(n.x) > 0.55 and p.z > 4.8 and p.y < 0.5 and dom in ("EscapulaE", "EscapulaD", "Coluna3", "Coluna2", "Pescoco", "BracoE", "BracoD"):
            reg = "Ombro"; fall = 1.0
        elif n.z < -0.25 and p.z < 4.8 and dom in ("Pelve", "Coluna1", "Coluna2", "Coluna3"):
            reg = "Barriga"; fall = 1.0
        else: continue
        alvo = [("Pelo" + reg + dom, 1.0)]; PAI["Pelo" + reg + dom] = dom
        bruto[v.index] = s * fall; dest[v.index] = alvo
    # suaviza o peso bruto entre vizinhos (evita salpicado) - 2 passadas
    for _ in range(2):
        bruto = [0.5 * bruto[i] + 0.5 * (sum(bruto[j] for j in viz[i]) / len(viz[i]) if viz[i] else 0) if dest[i] else 0.0 for i in range(len(bruto))]
    for i, b in enumerate(bruto):
        if b < 0.03 or not dest[i]: continue
        w = b * PMAX; pesos[(o.name, i)] = {n_: w * f for n_, f in dest[i]}; BS.append(b)
        for n_, f in dest[i]: regiao_pts.setdefault(n_, []).append((mw @ o.data.vertices[i].co, (m3 @ N[i]).normalized(), w * f))
BS.sort(); print("B p25/p50/p75/p90 %.2f %.2f %.2f %.2f" % tuple(BS[int(len(BS) * f)] for f in (0.25, 0.5, 0.75, 0.9)))
MINV = 40
for nome in [n for n, pts in regiao_pts.items() if len(pts) < MINV]:
    del regiao_pts[nome]
pesos = {k: {n: w for n, w in d.items() if n in regiao_pts} for k, d in pesos.items()}
pesos = {k: d for k, d in pesos.items() if d}
# ossos: cabeca levemente para dentro da superficie, cauda para fora (normal media)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT"); eb = arm.data.edit_bones
info = {}
for nome, pts in regiao_pts.items():
    tw = sum(w for _, _, w in pts); c = sum((p * w for p, _, w in pts), V()) / tw; n = sum((nn * w for _, nn, w in pts), V()).normalized()
    b = eb.new(nome); b.head = c - n * 0.4; b.tail = c + n * 0.6; b.parent = eb[PAI[nome]]; b.use_connect = False; b.use_deform = True
    info[nome] = {"pai": PAI[nome], "cabeca": [round(x, 3) for x in b.head], "normal": [round(x, 3) for x in n], "vertices": len(pts)}
bpy.ops.object.mode_set(mode="OBJECT")
# pesos: o Pelo* pega parte do peso do PROPRIO pai (nada muda com o Pelo* em repouso); sem vaga (4 infl.) -> fica de fora
semvaga = 0; aplicados = 0; LIBERADAS = []; TROCAS = []; LIMIAR_TROCA = float(os.environ.get("LIMIAR_TROCA", "0.25"))
for o in [bpy.data.objects[n] for n in ("Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Cabeca")]:
    for nome in regiao_pts:
        if not o.vertex_groups.get(nome): o.vertex_groups.new(name=nome)
    gn = {g.index: g.name for g in o.vertex_groups}; gi = {g.name: g for g in o.vertex_groups}
    for v in o.data.vertices:
        novo = pesos.get((o.name, v.index))
        if not novo: continue
        atuais = {gn[g.group]: g.weight for g in v.groups if g.weight > 0}
        mix = dict(atuais); vagas = 4 - len(atuais); usou = False
        if vagas <= 0:
            # sem vaga: o Pelo* ASSUME todo o peso do pai (troca de grupo, mesma quantidade de influencias). Com o Pelo*
            # parado, a matriz dele = a do pai -> deformacao identica. So nas pontas (b alto), para a base ficar presa.
            pelo = max(novo, key=novo.get); pai = PAI[pelo]
            if pai in mix and novo[pelo] / PMAX >= LIMIAR_TROCA:
                mix[pelo] = mix.pop(pai); usou = True; TROCAS.append(mix[pelo])
            novo = {}
        for pelo, w in sorted(novo.items(), key=lambda kv: -kv[1]):
            pai = PAI[pelo]
            if pai not in mix or vagas <= 0: continue
            dw = min(w, mix[pai] * 0.9)
            if dw < 0.01: continue
            mix[pai] -= dw; mix[pelo] = dw; vagas -= 1; usou = True
        if not usou: semvaga += 1; continue
        aplicados += 1
        for g in list(v.groups): gi[gn[g.group]].remove([v.index])
        for k, w in mix.items():
            if w > 0: gi[k].add([v.index], w, "REPLACE")
LIBERADAS.sort(); print("PESOS aplicados", aplicados, "trocas_de_grupo", len(TROCAS), "sem_vaga_ou_sem_pai", semvaga, "vagas_liberadas", len(LIBERADAS), "peso_movido p50/p90/max %.3f/%.3f/%.3f" % (LIBERADAS[len(LIBERADAS)//2], LIBERADAS[int(len(LIBERADAS)*0.9)], LIBERADAS[-1]) if LIBERADAS else "")
maxinf = max(sum(1 for g in v.groups if g.weight > 0) for o in [bpy.data.objects[n] for n in ("Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Cabeca")] for v in o.data.vertices)
bpy.ops.wm.save_as_mainfile(filepath=SAIDA)
json.dump({"peso_max": PMAX, "ossos": info, "max_influencias": maxinf}, open(os.path.splitext(SAIDA)[0] + "_pelo.json", "w"), indent=1)
print("PELO_OK", {k: v["vertices"] for k, v in info.items()}, "total_vertices", len(pesos), "max_influencias", maxinf, "ossos", len(arm.data.bones))
