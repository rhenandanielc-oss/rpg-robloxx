"""E5 Fase B: labios superiores (Labio_D/E, filhos da Cabeca) para rosnado/intimidacao: a pele do labio superior sobre os
caninos sobe (translacao) e mostra os dentes aos poucos. Dentes e interior (cascas soltas) nao recebem peso.
Uso: blender -b Leao_Solar_Ref_E5_rig.blend -P e5_13_labios.py -- <saida.blend> <relatorio.json>"""
import bpy, bmesh, sys, json
import numpy as np
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; OUT, REL = A
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]; me = ob.data
n = len(me.vertices); co = np.array([v.co for v in me.vertices])
def s(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
# casca principal (pele); dentes/lingua sao cascas soltas
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); casca = -np.ones(n, int); k = 0
for v in bm.verts:
    if casca[v.index] >= 0: continue
    pil = [v]; casca[v.index] = k
    while pil:
        x = pil.pop()
        for e in x.link_edges:
            y = e.other_vert(x)
            if casca[y.index] < 0: casca[y.index] = k; pil.append(y)
    k += 1
bm.free(); pele = casca == np.argmax(np.bincount(casca))
G = {g.name: g.index for g in ob.vertex_groups}
W = np.zeros((n, len(ob.vertex_groups))); nomes = [g.name for g in ob.vertex_groups]
for v in me.vertices:
    for g in v.groups: W[v.index, g.group] = g.weight
mand = W[:, G["Mandibula"]]
CENTRO = {"D": (0.52, -14.80, 12.62), "E": (-0.98, -14.80, 12.62)}
bpy.context.view_layer.objects.active = arm; arm.select_set(True); bpy.ops.object.mode_set(mode="EDIT")
for k_, c in CENTRO.items():
    e = arm.data.edit_bones.new("Labio_" + k_); e.head = Vector(c) + Vector((0, 0.35, 0)); e.tail = Vector(c) + Vector((0, -0.15, 0)); e.parent = arm.data.edit_bones["Cabeca"]
bpy.ops.object.mode_set(mode="OBJECT")
for k_, c in CENTRO.items():
    c = np.array(c); d = np.linalg.norm((co - c) * np.array([1.0, 0.8, 1.3]), axis=1)
    m = (1 - s((d - 0.28) / 0.38)) * s((co[:, 2] - 12.30) / 0.10) * pele * (mand < 0.05) * (co[:, 1] < -14.0)
    m *= 0.95; sel = m > 0.01
    W[sel] *= (1 - m[sel])[:, None]; W = np.c_[W, np.where(sel, m, 0)]; nomes.append("Labio_" + k_); print("LABIO", k_, int(sel.sum()), "vertices")
W[W < 0.01] = 0; o_ = np.argsort(-W, 1); cut = np.zeros_like(W, bool); np.put_along_axis(cut, o_[:, :4], True, 1); W *= cut
W[W < 0.01] = 0; W /= np.maximum(W.sum(1, keepdims=True), 1e-9)
ob.vertex_groups.clear()
for j, nm in enumerate(nomes):
    if not W[:, j].any(): continue
    g = ob.vertex_groups.new(name=nm)
    for i in np.nonzero(W[:, j])[0]: g.add([int(i)], float(W[i, j]), "REPLACE")
for b in arm.data.bones: b.use_deform = b.name != "Raiz"
infl = (W > 0).sum(1)
rel = {"vertices": n, "sem_peso": int((infl == 0).sum()), "influencias_max": int(infl.max()), "ossos": len(arm.data.bones),
       "hierarquia": {b.name: (b.parent.name if b.parent else None) for b in arm.data.bones}, "pivos": {b.name: [round(x, 3) for x in b.head_local] for b in arm.data.bones}}
json.dump(rel, open(REL, "w"), indent=1); print("RIG", {k_: v for k_, v in rel.items() if k_ not in ("hierarquia", "pivos")})
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("RIG_OK")
