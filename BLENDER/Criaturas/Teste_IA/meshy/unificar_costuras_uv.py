"""Vertices duplicados nas costuras de UV (o glTF separa o vertice onde a UV corta) nao sao vizinhos pela malha: as etapas
de pesos (regioes geodesicas, costura, suavizacao) davam pesos diferentes a cada copia e a costura ABRIA em rachaduras
quando a pata/asa se movia. Aqui cada grupo de vertices na mesma posicao recebe a MEDIA dos pesos (limite 4, normaliza).
Uso: blender -b Silverwing_M2M.blend -P unificar_costuras_uv.py"""
import bpy
from mathutils.kdtree import KDTree
M = bpy.data.objects["Silverwing"]; V = M.data.vertices
kd = KDTree(len(V))
for v in V: kd.insert(v.co, v.index)
kd.balance()
visto = set(); grupos = []
for v in V:
    if v.index in visto: continue
    g = [i for _, i, _ in kd.find_range(v.co, 1e-6)]
    visto.update(g)
    if len(g) > 1: grupos.append(g)
dif = 0
vgs = M.vertex_groups
for g in grupos:
    W = [{x.group: x.weight for x in V[i].groups} for i in g]
    if any(abs(W[0].get(k, 0) - w.get(k, 0)) > 1e-3 for w in W[1:] for k in set(W[0]) | set(w)): dif += 1
    m = {}
    for w in W:
        for k, x in w.items(): m[k] = m.get(k, 0.0) + x / len(W)
    top = sorted(m.items(), key=lambda t: -t[1])[:4]; s = sum(x for _, x in top) or 1.0
    for i in g:
        for x in list(V[i].groups): vgs[x.group].remove([i])
        for k, x in top:
            if x / s > 0.005: vgs[k].add([i], x / s, "REPLACE")
print("COSTURAS_UV grupos", len(grupos), "vertices", sum(len(g) for g in grupos), "com_pesos_diferentes", dif)
bpy.ops.wm.save_mainfile()
print("UNIFICAR_OK")
