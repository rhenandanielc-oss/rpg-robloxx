"""S1 r3: folga medida da sela. Em todos os quadros (passo 2) dos clipes oficiais mede, para cada vertice da sela, quanto ele
fica DENTRO da pele do leao (sem os fios da juba) e afasta a sela so onde entra, com margem e suavizado:
 - pecas do dorso (manta, aba, assento, debrum, costura, apoios, alca, adorno, argolas): sobem em Z por um campo de alturas
   (x, y) = maior entrada por celula, dilatado e suavizado (as camadas sobem juntas, a espessura nao muda);
 - cilha: afasta-se na direcao radial do seu centro, por faixa de angulo (deixa de apertar a barriga).
Repete medir -> afastar ate 'iter' vezes. Altera so a malha da sela (posicao de repouso); pesos e o leao nao mudam.
Uso: blender -b Leao_Solar_Ref_S1_sela.blend -P s1_04_folga.py -- <saida.blend> <saida.json> [iter=3] [margem=0.04]"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import s1_01_sela_leao as sl
A = sys.argv[sys.argv.index("--") + 1:]; ITER = int(A[2]) if len(A) > 2 else 3; MARGEM = float(A[3]) if len(A) > 3 else 0.04
sc = bpy.context.scene; arm = bpy.data.objects["Leao_Solar_Rig"]; lo = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]
sela = bpy.data.objects[sl.NOME]; me = sela.data
PL = list(sela["pecas"]); vpeca = [PL[d.value] for d in me.attributes["peca"].data]
_co0 = np.array([v.co for v in me.vertices])
cilha = np.array([p == "cilha" or (p in ("ferro", "ambar") and abs(c[1] - sl.CILHA["y"]) < 0.4 and c[2] < 10.0) for p, c in zip(vpeca, _co0)])   # argolas da cilha: radial
GI = {g.index: g.name for g in lo.vertex_groups}
juba = np.array([any(GI[g.group].startswith("Juba") and g.weight > 0.5 for g in v.groups) for v in lo.data.vertices])
OFICIAIS = sorted((a for a in bpy.data.actions if a.name.startswith("Leao_") and not a.name.endswith(("_v1", "_r2", "_r3"))), key=lambda a: a.name)
def medir(passo=2):
    """maior entrada (positiva = dentro da pele) de cada vertice da sela em todos os quadros; e onde ocorreu"""
    ent = np.zeros(len(me.vertices)); onde = {}
    for act in OFICIAIS:
        arm.animation_data.action = act; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
        for f in range(f0, f1 + 1, passo):
            sc.frame_set(f); bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
            el = lo.evaluated_get(dg); ml = el.to_mesh(); Wl = lo.matrix_world; P = [Wl @ v.co for v in ml.vertices]
            fs = [tuple(p.vertices) for p in ml.polygons if not any(juba[i] for i in p.vertices)]; el.to_mesh_clear()
            bvh = BVHTree.FromPolygons(P, fs)
            es = sela.evaluated_get(dg); ms = es.to_mesh(); Ws = sela.matrix_world; S = [Ws @ v.co for v in ms.vertices]; es.to_mesh_clear()
            for i, w in enumerate(S):
                loc, _, _, d = bvh.find_nearest(w, 0.5)
                if loc is None or d > 0.45: continue
                if mq.dentro(bvh, w) and d > ent[i]: ent[i] = d; onde[i] = (act.name[5:], f - f0 + 1)
    return ent, onde
def aplicar(ent):
    co = np.array([v.co for v in me.vertices]); alvo = np.where(ent > 0, ent + MARGEM, 0.0)
    # dorso: campo de alturas (x, y)
    X0, Y0, PS = co[:, 0].min() - 0.5, co[:, 1].min() - 0.5, 0.08
    nx = int((co[:, 0].max() + 0.5 - X0) / PS) + 2; ny = int((co[:, 1].max() + 0.5 - Y0) / PS) + 2; G = np.zeros((ny, nx))
    ij = np.stack([((co[:, 1] - Y0) / PS).round().astype(int), ((co[:, 0] - X0) / PS).round().astype(int)], 1)
    for k in np.nonzero((alvo > 0) & ~cilha)[0]: G[ij[k, 0], ij[k, 1]] = max(G[ij[k, 0], ij[k, 1]], alvo[k])
    r = 3; Gd = G.copy(); p = np.pad(G, r)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r: Gd = np.maximum(Gd, p[r + dy:r + dy + ny, r + dx:r + dx + nx])
    Gs = Gd.copy()
    for _ in range(3):
        p = np.pad(Gs, 2, mode="edge"); Gs = sum(p[2 + dy:2 + dy + ny, 2 + dx:2 + dx + nx] for dy in range(-2, 3) for dx in range(-2, 3)) / 25.0
    Gf = np.maximum(Gs, G)                                   # o suavizado nunca fica abaixo do medido
    dz = Gf[ij[:, 0], ij[:, 1]] * ~cilha
    # cilha: radial por faixa de angulo em volta do centro do corte
    c0 = np.array([sl.XC, sl.CILHA["y"], 8.0]); rel = co - c0; phi = np.arctan2(rel[:, 2], rel[:, 0])
    nb = 72; bins = ((phi + math.pi) / (2 * math.pi) * nb).astype(int) % nb; Rb = np.zeros(nb)
    for k in np.nonzero((alvo > 0) & cilha)[0]: Rb[bins[k]] = max(Rb[bins[k]], alvo[k])
    Rb = np.maximum(Rb, np.maximum(np.roll(Rb, 1), np.roll(Rb, -1)))
    Rb = np.maximum(Rb, (np.roll(Rb, 1) + Rb + np.roll(Rb, -1)) / 3); Rb = (np.roll(Rb, 1) + 2 * Rb + np.roll(Rb, -1)) / 4
    rad = np.zeros(len(co)); rad[cilha] = Rb[bins[cilha]]
    dirr = rel / np.maximum(np.linalg.norm(rel[:, [0, 2]], axis=1, keepdims=True), 1e-6); dirr[:, 1] = 0
    novo = co + np.stack([np.zeros(len(co)), np.zeros(len(co)), dz], 1) + dirr * rad[:, None]
    for v, c in zip(me.vertices, novo): v.co = V(c)
    me.update(); return float(dz.max()), float(rad.max())
hist = []
for it in range(ITER):
    ent, onde = medir(); n_in = int((ent > 0.005).sum())
    pior = int(np.argmax(ent)); hist.append(dict(iter=it, vertices_dentro=n_in, pior=round(float(ent.max()), 3), onde=onde.get(pior), peca=vpeca[pior],
                                                 por_peca={p: round(float(ent[np.array(vpeca) == p].max()), 3) for p in sorted(set(vpeca))}))
    print("FOLGA", json.dumps(hist[-1]), flush=True)
    if n_in == 0: break
    dzm, drm = aplicar(ent); print("APLICADO dz_max %.3f radial_max %.3f" % (dzm, drm), flush=True)
else:
    ent, onde = medir(); pior = int(np.argmax(ent))
    hist.append(dict(iter=ITER, vertices_dentro=int((ent > 0.005).sum()), pior=round(float(ent.max()), 3), onde=onde.get(pior), peca=vpeca[pior],
                     por_peca={p: round(float(ent[np.array(vpeca) == p].max()), 3) for p in sorted(set(vpeca))}))
    print("FOLGA", json.dumps(hist[-1]), flush=True)
sela["etapa"] = "S1 r3 sela felina com folga medida nos 28 clipes (proposta)"; sela["folga_historico"] = json.dumps(hist)
json.dump(hist, open(A[1], "w"), indent=1)
arm.animation_data.action = None
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[0])); print("FOLGA_OK")
