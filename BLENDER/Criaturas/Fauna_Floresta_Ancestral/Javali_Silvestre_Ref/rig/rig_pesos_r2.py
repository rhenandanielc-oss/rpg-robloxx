"""Rig r2 do Javali Silvestre (13/11/2026): SO PESOS. Ossos, nomes, hierarquia e malhas nao mudam; o rig piloto aprovado fica
preservado em rig/CR_Javali_Rig.blend. Causa medida no lote A: o heat deixou degraus de peso na pele da barriga/axila por dentro
das pernas (x ~0,05, z ~0,27) e na base das orelhas; quando a pata balanca, arestas de ~1 cm esticavam ate 4,7x.
Correcao GUIADA PELA MEDICAO (uma tentativa anterior por regioes fixas so mudou o degrau de lugar, 7,5x):
  1) avalia a pele em quadros dos clipes do lote A (acoes trazidas do .blend de clipes; acoes so mexem nos ossos);
  2) acha as arestas com estiramento > LIMITE (ou compressao forte) e marca seus vertices + 1 anel de vizinhos;
  3) suaviza SO esses pesos (media com os vizinhos, fator 0,5), mantendo cascos, focinho/presas (cabeca rigida) e orelhas-ponta;
  4) repete ate passar no limite ou acabar as rodadas. Maximo 4 influencias; costura cabeca/corpo igualada no fim.
Uso: blender -b rig/CR_Javali_Rig.blend -P rig/rig_pesos_r2.py -- <clipes.blend> <saida.blend> [limite=1.6] [rodadas=12]
r3 (13/11, lote B): mesmo script com o .blend de clipes A+B (as marchas rapidas entram na medicao) -> rig/CR_Javali_Rig_r3.blend
r4 (13/11, lote C): idem com o .blend A+B+C (cabeca baixa entra na medicao) -> rig/CR_Javali_Rig_r4.blend"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils.kdtree import KDTree
A = sys.argv[sys.argv.index("--") + 1:]; CLIPES_BLEND = os.path.abspath(A[0]); SAIDA = os.path.abspath(A[1])
LIM = float(A[2]) if len(A) > 2 else 1.6; RODADAS = int(A[3]) if len(A) > 3 else 12
sc = bpy.context.scene; arm = bpy.data.objects["Javali_Rig"]
MALHAS = [bpy.data.objects["Javali_Corpo"], bpy.data.objects["Javali_Cabeca"]]
with bpy.data.libraries.load(CLIPES_BLEND, link=False) as (src, dst):
    dst.actions = [a for a in src.actions if a.startswith("Javali_")]
ACOES = {a.name: a for a in dst.actions}
AMOSTRA = [("Javali_Andar", 2), ("Javali_VirarE", 2), ("Javali_VirarD", 2), ("Javali_ParadoParaAndar", 2),
           ("Javali_AndarParaParado", 2), ("Javali_Repouso", 4),
           # r3 (lote B): marchas rapidas entram na medicao quando o .blend de clipes as tiver
           ("Javali_Trote", 1), ("Javali_Corrida", 1), ("Javali_Arrancada", 1), ("Javali_Frenagem", 1), ("Javali_AndarParaTrote", 2),
           ("Javali_TroteParaAndar", 2), ("Javali_TroteParaCorrida", 1), ("Javali_CorridaParaTrote", 1),
           # r4 (lote C): cabeca baixa (farejar/fucar) e alerta
           ("Javali_Farejar", 2), ("Javali_Fucar", 2), ("Javali_Alerta", 2), ("Javali_AlertaParaRepouso", 3)]
AMOSTRA = [(n, p_) for n, p_ in AMOSTRA if n in ACOES]
arm.animation_data_create()
for pb in arm.pose.bones: pb.rotation_mode = "QUATERNION"      # as acoes gravam quaternions (o rig piloto estava em XYZ)
NY = min(v.co.y for o in MALHAS for v in o.data.vertices)
def coords(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); return c.reshape(-1, 3)
ED = [np.array([tuple(e.vertices) for e in o.data.edges]) for o in MALHAS]
REST = [np.array([v.co[:] for v in o.data.vertices]) for o in MALHAS]
L0 = [np.linalg.norm(c[e[:, 0]] - c[e[:, 1]], axis=1) for c, e in zip(REST, ED)]
VIZ = []
for o in MALHAS:
    bm_ = bmesh.new(); bm_.from_mesh(o.data); bm_.verts.ensure_lookup_table()
    VIZ.append([[e.other_vert(v).index for e in v.link_edges] for v in bm_.verts]); bm_.free()
def _borda(o):
    bm_ = bmesh.new(); bm_.from_mesh(o.data); r_ = {v.index for v in bm_.verts if v.is_boundary}; bm_.free(); return r_
BORDA = [_borda(o) for o in MALHAS]                  # costura cabeca/corpo: fica como esta (os dois lados ja tem os mesmos pesos)
def fixo(p):                                         # pesos que NAO podem ser suavizados
    return p[2] < 0.015 or p[1] < NY + 0.20          # sola dos cascos e focinho/presas rigidos
def medir():
    pior = [np.ones(len(l)) for l in L0]
    for nome, passo in AMOSTRA:
        act = ACOES[nome]; arm.animation_data.action = act
        if getattr(act, "slots", None) and len(act.slots) and arm.animation_data.action_slot is None:
            arm.animation_data.action_slot = act.slots[0]               # acao trazida de outro .blend: liga o slot (Blender 5)
        for f in range(int(act.frame_range[0]), int(act.frame_range[1]) + 1, passo):
            sc.frame_set(f)
            for i, (o, e, l0) in enumerate(zip(MALHAS, ED, L0)):
                c = coords(o); r = np.linalg.norm(c[e[:, 0]] - c[e[:, 1]], axis=1) / np.maximum(l0, 1e-6)
                r[l0 < 0.003] = 1.0                                     # micro-arestas da decimacao (< 3 mm) sao ruido
                pior[i] = np.maximum(pior[i], r)                         # so estiramento (compressao de aresta minuscula e ruido)
    arm.animation_data.action = None
    return pior
def pesos(o, v): return {o.vertex_groups[g.group].name: g.weight for g in v.groups}
def grava(o, v, novos):
    for g in list(v.groups): o.vertex_groups[g.group].remove([v.index])
    tot = sum(novos.values()) or 1.0
    for nm, w in sorted(novos.items(), key=lambda e: -e[1])[:4]:
        if w / tot > 1e-4: (o.vertex_groups.get(nm) or o.vertex_groups.new(name=nm)).add([v.index], w / tot, "REPLACE")
# ---- 0) limpeza por distancia: peso de osso de PERNA so vale perto do proprio osso (o heat vazou pela barriga fina:
#         vertice no meio da barriga com 22% de CoxaD, a 30 cm da coxa). O excedente vai para o osso da coluna local.
BD = arm.data.bones
RMAX = {"Escapula": 0.13, "Braco": 0.12, "Antebraco": 0.085, "Canela": 0.07, "Quartela": 0.07,
        "Coxa": 0.17, "Perna": 0.11, "CanelaTras": 0.07, "QuartelaTras": 0.07}
def rmax(nm):
    for base in sorted(RMAX, key=len, reverse=True):
        if nm[:-1] == base: return RMAX[base]
    return None
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9))); return (p - (a + ab * t)).length
def coluna_em(y):
    if y < -0.13: return "Coluna3"
    if y < 0.03: return "Coluna2"
    if y < 0.23: return "Coluna1"
    return "Pelve"
from mathutils import Vector as Vv
n_limpos = 0
PERNAS_DEF = [b.name for b in BD if b.use_deform and rmax(b.name) is not None]
for o in MALHAS:
    for v in o.data.vertices:
        pw = pesos(o, v); tira = 0.0; novos = {}
        for nm, w in pw.items():
            rm = rmax(nm)
            if rm is None: novos[nm] = w; continue
            d = dist_seg(v.co, BD[nm].head_local, BD[nm].tail_local)
            k = 1 - max(0.0, min(1.0, (d - rm) / 0.03))          # some aos poucos entre rm e rm + 3 cm
            novos[nm] = w * k; tira += w * (1 - k)
        if tira > 1e-3:
            # r3: abaixo de 0,12 (pata) o excedente vai para o osso de perna mais proximo dentro do raio; acima (barriga) vai para a coluna.
            # (mandar tudo para a perna mais proxima foi testado e piorou a barriga: 4,5x) (antes: tudo ia para a coluna -> esporao com 17% de Coluna3 afundava)
            melhor = None
            for nm in (PERNAS_DEF if v.co.z < 0.12 else []):             # so na pata (casco/boleto/esporao); barriga -> coluna
                d = dist_seg(v.co, BD[nm].head_local, BD[nm].tail_local)
                if d <= rmax(nm) and (melhor is None or d < melhor[0]): melhor = (d, nm)
            dest = melhor[1] if melhor else coluna_em(v.co.y)
            novos[dest] = novos.get(dest, 0.0) + tira; grava(o, v, novos); n_limpos += 1
# 0b) pata sem peso de tronco: abaixo de 0,12 nenhum peso de coluna/pelve (o esporao atras do casco dianteiro tinha ~19% de
#     Coluna3 vindo do heat e afundava 6 mm no apoio do galope); vai para o osso de perna mais proximo
TRONCO = {"Pelve", "Coluna1", "Coluna2", "Coluna3", "Pescoco", "Pescoco2", "Cabeca", "Cauda1", "Cauda2"}
n_pata = 0
for o in MALHAS:
    for v in o.data.vertices:
        if v.co.z >= 0.12: continue
        pw = pesos(o, v); tr = sum(w for nm, w in pw.items() if nm in TRONCO)
        if tr < 1e-3: continue
        perto = min(PERNAS_DEF, key=lambda nm: dist_seg(v.co, BD[nm].head_local, BD[nm].tail_local))
        novos = {nm: w for nm, w in pw.items() if nm not in TRONCO}; novos[perto] = novos.get(perto, 0.0) + tr
        grava(o, v, novos); n_pata += 1
print("LIMPEZA por distancia: vertices", n_limpos, "| pata sem tronco:", n_pata, flush=True)
HIST = []
for rodada in range(RODADAS + 1):
    pior = medir(); resumo = [(round(float(p.max()), 2), int((p > LIM).sum())) for p in pior]; HIST.append(resumo)
    print("RODADA", rodada, "pior (fator, arestas > %.1f)" % LIM, resumo, flush=True)
    if all(n == 0 for _, n in resumo) or rodada == RODADAS: break
    for i, o in enumerate(MALHAS):
        ruins = ED[i][pior[i] > LIM]; alvo = set(ruins.ravel().tolist())
        for vi in list(alvo): alvo.update(VIZ[i][vi])
        me = o.data; antigos = {vi: pesos(o, me.vertices[vi]) for vi in range(len(me.vertices))}
        for vi in alvo:
            if fixo(REST[i][vi]) or not VIZ[i][vi] or vi in BORDA[i]: continue
            soma = {}
            for vj in VIZ[i][vi]:
                for nm, w in antigos[vj].items(): soma[nm] = soma.get(nm, 0.0) + w / len(VIZ[i][vi])
            novos = {nm: 0.5 * antigos[vi].get(nm, 0.0) + 0.5 * soma.get(nm, 0.0) for nm in set(soma) | set(antigos[vi])}
            grava(o, me.vertices[vi], novos)
# costura cabeca/corpo: mesmos pesos nos vertices coincidentes
def bordas(o):
    bm_ = bmesh.new(); bm_.from_mesh(o.data); idx = [v.index for v in bm_.verts if v.is_boundary]; bm_.free(); return idx
CORPO, CAB = MALHAS; bc = bordas(CORPO); kd = KDTree(len(bc))
for i in bc: kd.insert(CORPO.data.vertices[i].co, i)
kd.balance(); cop = 0
for i in bordas(CAB):
    vc = CAB.data.vertices[i]; _, j, d = kd.find(vc.co)
    if d is not None and d < 1e-4: grava(CAB, vc, pesos(CORPO, CORPO.data.vertices[j])); cop += 1
pior = medir()
for i, o in enumerate(MALHAS):
    ix = np.argsort(-pior[i])[:12]
    print("PIORES", o.name, [(round(float(pior[i][j]), 2), tuple(np.round(REST[i][ED[i][j, 0]], 3)), round(float(L0[i][j]) * 100, 2)) for j in ix])
final = [(round(float(p.max()), 2), int((p > LIM).sum())) for p in pior]
mx = max(len([g for g in v.groups if g.weight > 1e-4]) for o in MALHAS for v in o.data.vertices)
sem = sum(1 for o in MALHAS for v in o.data.vertices if not v.groups)
print("PESOS_R2 final", final, "costura", cop, "max_infl", mx, "sem_peso", sem)
for a in list(ACOES.values()): bpy.data.actions.remove(a)
bpy.ops.wm.save_as_mainfile(filepath=SAIDA); print("RIG_R2_OK", SAIDA)
