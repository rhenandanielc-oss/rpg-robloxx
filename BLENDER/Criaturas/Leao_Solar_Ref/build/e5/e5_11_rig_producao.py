"""E5: rig de producao a partir da E4b r2 (mesmos pesos do corpo, testados como os melhores entre 7 variantes).
Acrescenta Orelha_D/E (filhas da Cabeca) e Palpebra_D/E (palpebra superior, filhas da Cabeca, giram para baixo para piscar
e semicerrar), remove o atributo de QA e grava a hierarquia. As restricoes do rig de teste (auxiliares de volume a meia
rotacao, tufo copiando a cauda, juba por mola) NAO ficam como restricao: o gerador de clipes grava tudo em chaves.
Uso: blender -b Leao_Solar_Ref_E4b_r2.blend -P e5_11_rig_producao.py -- <saida.blend> <relatorio.json> [com_qa=0]"""
import bpy, sys, json, math
import numpy as np
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; OUT, REL = A[0], A[1]; COM_QA = len(A) > 2 and A[2] == "1"
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]; me = ob.data
ad = arm.data; n = len(me.vertices); co = np.array([v.co for v in me.vertices])
def s(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
ORELHA = {"D": (1.72, -13.3, 15.5), "E": (-2.08, -13.3, 15.5)}
OLHO = {"D": (0.65, -14.25, 14.38), "E": (-1.11, -14.25, 14.38)}
bpy.context.view_layer.objects.active = arm; arm.select_set(True); bpy.ops.object.mode_set(mode="EDIT")
for k, c in ORELHA.items():
    c = Vector(c); base = c + Vector((-0.25 if k == "D" else 0.25, 0.15, -0.45)); e = ad.edit_bones.new("Orelha_" + k); e.head = base; e.tail = c + Vector((0.12 if k == "D" else -0.12, -0.05, 0.45))
    e.parent = ad.edit_bones["Cabeca"]
for k, c in OLHO.items():
    c = Vector(c); e = ad.edit_bones.new("Palpebra_" + k); e.head = c + Vector((0, 0.35, 0)); e.tail = c + Vector((0, -0.25, 0.0))   # pivo atras do olho, aponta para a frente
    e.parent = ad.edit_bones["Cabeca"]
bpy.ops.object.mode_set(mode="OBJECT")
G = {g.name: g for g in ob.vertex_groups}
W = np.zeros((n, len(ob.vertex_groups))); nomes = [g.name for g in ob.vertex_groups]
for v in me.vertices:
    for g in v.groups: W[v.index, g.group] = g.weight
novos = {}
for k, c in ORELHA.items():
    d = np.linalg.norm(co - np.array(c), axis=1); m = (1 - s((d - 0.38) / 0.32)) * (co[:, 2] > 14.85) * (np.abs(co[:, 0] + 0.2) > 1.15)
    novos["Orelha_" + k] = m
for k, c in OLHO.items():
    c = np.array(c); dx = np.abs(co[:, 0] - c[0]); dz = co[:, 2] - c[2]
    m = (1 - s((dx - 0.30) / 0.15)) * s((dz - 0.03) / 0.07) * (1 - s((dz - 0.30) / 0.15)) * (co[:, 1] < -13.75) * (co[:, 1] > -14.8)
    novos["Palpebra_" + k] = m * 0.95
for nome, m in novos.items():
    sel = m > 0.01; W[sel] *= (1 - m[sel])[:, None]; W = np.c_[W, np.where(sel, m, 0)]; nomes.append(nome)
    print("GRUPO", nome, int(sel.sum()), "vertices")
# limite 4 + normalizacao
W[W < 0.01] = 0; o_ = np.argsort(-W, 1); cut = np.zeros_like(W, bool); np.put_along_axis(cut, o_[:, :4], True, 1); W *= cut
W[W < 0.01] = 0; W /= np.maximum(W.sum(1, keepdims=True), 1e-9)
ob.vertex_groups.clear()
for j, nm in enumerate(nomes):
    if not W[:, j].any(): continue
    g = ob.vertex_groups.new(name=nm)
    for i in np.nonzero(W[:, j])[0]: g.add([int(i)], float(W[i, j]), "REPLACE")
for b in ad.bones: b.use_deform = b.name != "Raiz"
if not COM_QA and "qa_juba" in me.attributes: me.attributes.remove(me.attributes["qa_juba"])
for o in list(bpy.data.objects):
    if o.name.startswith("Leao_Rig_Teste_Boca"): bpy.data.objects.remove(o, do_unlink=True)
arm.name = ad.name = "Leao_Solar_Rig"
infl = (W > 0).sum(1)
# ossos com peso (os sem peso somem na importacao do Roblox)
com_peso = {nomes[j] for j in range(len(nomes)) if W[:, j].any()}
rel = {"vertices": n, "sem_peso": int((infl == 0).sum()), "influencias_max": int(infl.max()), "mal_normalizados": int((np.abs(W.sum(1) - 1) > 1e-3).sum()),
       "ossos": len(ad.bones), "ossos_deformam": sum(b.use_deform for b in ad.bones), "ossos_deform_sem_peso": sorted(b.name for b in ad.bones if b.use_deform and b.name not in com_peso),
       "atributos": [a.name for a in me.attributes if not a.name.startswith((".", "position", "sharp", "UV", "material"))],
       "hierarquia": {b.name: (b.parent.name if b.parent else None) for b in ad.bones},
       "pivos": {b.name: [round(x, 3) for x in b.head_local] for b in ad.bones}}
json.dump(rel, open(REL, "w"), indent=1); print("PRODUCAO", json.dumps({k: v for k, v in rel.items() if k not in ("hierarquia", "pivos")}))
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("RIG_OK")
