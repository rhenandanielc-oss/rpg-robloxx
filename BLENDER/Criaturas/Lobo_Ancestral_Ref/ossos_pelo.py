"""Ossos de PELO do Lobo Ancestral (para o pelo balancar com o vento, nao so a malha inteira): cadeias curtas na nuca,
lados da juba, bochechas, franja do peito, costas, barriga, cotovelos e coxas, filhas dos ossos do corpo. Pesos SO nas
pontas do pelo: dentro da capsula de cada osso de pelo, o peso cresce com a distancia ao eixo do osso do corpo
(camada rente ao corpo presa, camada externa solta). Peso = camada x regiao (capsula macia)
x FORCA; os pesos antigos do vertice sao reduzidos na mesma proporcao; maximo 4 influencias. Simetrico (E/D espelhados).
Malha, UV, textura e ossos existentes intactos. Uso: blender -b rig8/Lobo_Ancestral_Rig.blend -P ossos_pelo.py -- <saida_dir>"""
import bpy, sys, os, json
import numpy as np
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
# nome: (pai, cabeca, cauda, raio da regiao, forca). Lado E (+X); o D e gerado espelhado.
PELO = {
    "PeloNuca1":   ("Pescoco1", (0.0, -4.30, 7.55), (0.0, -3.55, 7.30), 1.20, 0.90),
    "PeloNuca2":   ("PeloNuca1", (0.0, -3.55, 7.30), (0.0, -2.80, 6.95), 1.10, 0.90),
    "PeloJubaE1":  ("Pescoco1", (0.95, -4.55, 7.05), (1.35, -4.15, 6.30), 0.95, 0.90),
    "PeloJubaE2":  ("PeloJubaE1", (1.35, -4.15, 6.30), (1.55, -3.75, 5.50), 0.85, 0.90),
    "PeloBochechaE": ("Cabeca", (0.80, -5.65, 7.05), (1.30, -5.35, 6.50), 0.60, 0.75),
    "PeloPeito1":  ("Peito", (0.0, -5.20, 5.40), (0.0, -5.25, 4.55), 0.95, 0.85),
    "PeloPeito2":  ("PeloPeito1", (0.0, -5.25, 4.55), (0.0, -5.05, 3.70), 0.85, 0.90),
    "PeloDorso1":  ("Peito", (0.0, -3.00, 6.75), (0.0, -2.10, 6.55), 0.95, 0.80),
    "PeloDorso2":  ("Coluna2", (0.0, -1.40, 6.25), (0.0, -0.30, 6.00), 0.95, 0.75),
    "PeloBarriga": ("Coluna2", (0.0, -2.30, 3.95), (0.0, -2.40, 3.15), 0.90, 0.80),
    "PeloCotoveloE": ("AntebracoE", (0.95, -3.05, 3.15), (0.95, -2.75, 2.40), 0.55, 0.80),
    "PeloCoxaE":   ("CoxaE", (0.95, 1.80, 4.10), (0.95, 2.25, 3.30), 0.75, 0.75),
}
def lado_d(nm):                                                        # PeloJubaE1 -> PeloJubaD1, AntebracoE -> AntebracoD
    if nm.startswith("PeloJubaE"): return "PeloJubaD" + nm[9:]
    return nm[:-1] + "D" if nm.endswith("E") else nm
OSSOS = {}
for nm, (pai, h, t, r, f) in PELO.items():
    OSSOS[nm] = (pai, V(h), V(t), r, f)
    if h[0] != 0.0:                                                    # lateral: gera o lado D espelhado
        OSSOS[lado_d(nm)] = (lado_d(pai), V((-h[0], h[1], h[2])), V((-t[0], t[1], t[2])), r, f)
# ------------------------------------------------------------------ ossos (edit mode)
bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); EB = arm.data.edit_bones
for nm in sorted(OSSOS, key=lambda s: ("2" in s, s)):                # pais antes das filhas
    pai, h, t, r, f = OSSOS[nm]
    eb = EB.get(nm) or EB.new(nm); eb.head = h; eb.tail = t; eb.roll = 0.0; eb.parent = EB[pai]; eb.use_connect = False; eb.use_deform = True
bpy.ops.object.mode_set(mode="OBJECT")
for nm in OSSOS:
    pb = arm.pose.bones[nm]; pb.rotation_mode = "QUATERNION"
# ------------------------------------------------------------------ peso: camada EXTERNA de cada regiao
# v1/v2 ("pelagem" = afastamento de uma malha suavizada) quase nao pegava a juba: ela e um volume grosso, nao so pontas.
# Agora, dentro da capsula de cada osso de pelo, o peso cresce com a distancia ao EIXO do osso do corpo (pescoco, coluna,
# pata...): a camada rente ao corpo (abaixo do percentil P0) fica presa e a camada de fora (ate o P1) solta ao vento.
n = len(me.vertices); co = np.array([v.co[:] for v in me.vertices])
viz = [[] for _ in range(n)]
for e in me.edges: a_, b_ = e.vertices; viz[a_].append(b_); viz[b_].append(a_)
VZ = [np.array(v, int) for v in viz]
BD = arm.data.bones
EIXO = {"PeloNuca": ("Pescoco1", "Cabeca"), "PeloJuba": ("Pescoco1", "Cabeca"), "PeloBochecha": ("Cabeca", "Cabeca"),
        "PeloPeito": ("Peito", "Pescoco1"), "PeloDorso": ("Coluna2", "Peito"), "PeloBarriga": ("Coluna2", "Coluna2"),
        "PeloCotovelo": ("Antebraco", "Antebraco"), "PeloCoxa": ("Coxa", "Coxa")}
P0, P1 = 35, 97
def dist_seg(p, a, b):
    ab = b - a; t = np.clip(((p - a) @ ab) / max(ab @ ab, 1e-9), 0, 1); return np.linalg.norm(p - (a + t[:, None] * ab), axis=1)
W = {}
for nm, (pai, h, t, r, f) in OSSOS.items():
    chave = next(k for k in EIXO if nm.startswith(k)); b1, b2 = EIXO[chave]
    lado = nm[-1] if nm[-1] in "ED" else (nm[-2] if nm[-2] in "ED" and nm.startswith("PeloJuba") else "")
    if b1 in ("Antebraco", "Coxa"): b1 = b2 = b1 + lado
    a = np.array(BD[b1].head_local); bb = np.array(BD[b2].tail_local if b1 == b2 else BD[b2].head_local)
    reg = 1 - suave((dist_seg(co, np.array(h), np.array(t)) - 0.55 * r) / (0.45 * r))
    dent = reg > 0.3
    d = dist_seg(co, a, bb)
    if dent.sum() < 10: W[nm] = np.zeros(n); continue
    r0, r1 = np.percentile(d[dent], P0), np.percentile(d[dent], P1)
    W[nm] = reg * suave((d - r0) / max(r1 - r0, 1e-3)) * f
    if nm.startswith("PeloJuba") or nm.startswith("PeloBochecha"):   # lado certo (nao puxa o outro lado da juba)
        W[nm] *= suave((co[:, 0] * (1 if "E" in nm[-2:] else -1) - 0.1) / 0.4)
for k in W:
    for _ in range(2): W[k] = 0.5 * W[k] + 0.5 * np.array([W[k][VZ[i]].mean() if len(VZ[i]) else W[k][i] for i in range(n)])
tot = np.sum([w for w in W.values()], axis=0)
escala = np.where(tot > 0.9, 0.9 / np.maximum(tot, 1e-9), 1.0)       # o corpo fica com >= 10%
gi = {g.index: g.name for g in LO.vertex_groups}
for nm in OSSOS:
    if nm not in LO.vertex_groups: LO.vertex_groups.new(name=nm)
VG = {g.name: g for g in LO.vertex_groups}
rel = {"ossos": {}, "vertices_com_pelo": 0}
for i, v in enumerate(me.vertices):
    novos = {nm: float(W[nm][i] * escala[i]) for nm in OSSOS if W[nm][i] * escala[i] > 0.02}
    if not novos: continue
    s_novo = sum(novos.values())
    antigos = {gi[g.group]: g.weight for g in v.groups}
    sa = sum(antigos.values()) or 1.0
    todos = {k: w / sa * (1 - s_novo) for k, w in antigos.items()}
    for k, w in novos.items(): todos[k] = todos.get(k, 0) + w
    top = sorted(todos.items(), key=lambda kv: -kv[1])[:4]; st = sum(w for _, w in top)
    for g in list(v.groups): LO.vertex_groups[g.group].remove([i])
    for k, w in top: VG[k].add([i], w / st, "REPLACE")
    rel["vertices_com_pelo"] += 1
for nm in OSSOS:
    w = np.array([next((g.weight for g in v.groups if g.group == VG[nm].index), 0.0) for v in me.vertices])
    rel["ossos"][nm] = {"vertices": int((w > 0.02).sum()), "peso_max": round(float(w.max()), 3), "pai": OSSOS[nm][0]}
    print("PELO %-15s pai %-11s verts %4d peso_max %.2f" % (nm, OSSOS[nm][0], rel["ossos"][nm]["vertices"], rel["ossos"][nm]["peso_max"]))
rel["total_ossos"] = len(arm.data.bones); print("TOTAL ossos", rel["total_ossos"], "vertices com pelo", rel["vertices_com_pelo"])
json.dump(rel, open(os.path.join(OUT, "ossos_pelo.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("OSSOS_PELO_OK")
