"""Solda as costuras da malha do Silverwing. Causa: a malha do Meshy vem partida por ilhas de UV; a decimacao (1M -> 20k)
moveu cada lado da costura de forma independente -> 771 ilhas, ~17 mil vertices de borda a 1-6 mm da ilha vizinha, com
pesos diferentes -> as costuras ABREM na animacao (rachaduras/lascas na cauda, asas e corpo).
Metodo: pares borda-borda de ilhas diferentes, do mais perto ao mais longe (<= LIM); agrupa sem nunca juntar dois
vertices da mesma ilha (nenhuma face colapsa) e com diametro <= LIM; cada grupo vai para a posicao media com pesos
medios; remove duplicados. A UV e por canto de face (textura preservada).
Uso: blender -b arq.blend -P soldar_costuras.py -- [medir] [LIM=0.007]"""
import bpy, sys, bmesh
from mathutils import kdtree, Vector
from collections import deque
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
so_medir = "medir" in args
LIM = float([a for a in args if a.replace(".", "").isdigit()][0]) if any(a.replace(".", "").isdigit() for a in args) else 0.007
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]; me = M.data

def ilhas_borda():
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    il = [-1] * len(bm.verts); k = 0
    for v in bm.verts:
        if il[v.index] >= 0: continue
        q = deque([v]); il[v.index] = k
        while q:
            x = q.popleft()
            for e in x.link_edges:
                y = e.other_vert(x)
                if il[y.index] < 0: il[y.index] = k; q.append(y)
        k += 1
    borda = [v.index for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
    nb = sum(1 for e in bm.edges if e.is_boundary); bm.free()
    return il, borda, k, nb

def grupos_solda(il, borda):
    kd = kdtree.KDTree(len(borda))
    for j, i in enumerate(borda): kd.insert(me.vertices[i].co, j)
    kd.balance()
    pares = []
    for j, i in enumerate(borda):
        for (co, j2, d) in kd.find_range(me.vertices[i].co, LIM):
            i2 = borda[j2]
            if i2 > i and il[i2] != il[i]: pares.append((d, i, i2))
    pares.sort()
    pai = {}; membros = {}
    def raiz(x):
        while pai.get(x, x) != x: x = pai[x]
        return x
    for d, a, b in pares:
        ra, rb = raiz(a), raiz(b)
        if ra == rb: continue
        ma, mb = membros.get(ra, [ra]), membros.get(rb, [rb])
        if {il[x] for x in ma} & {il[x] for x in mb}: continue                    # nunca dois da mesma ilha
        tudo = ma + mb
        if max((me.vertices[x].co - me.vertices[y].co).length for x in tudo for y in tudo) > LIM: continue
        pai[rb] = ra; membros[ra] = tudo; membros.pop(rb, None)
    return [g for g in membros.values() if len(g) > 1]

def abertura(grupos, nomes):
    pior = {}
    for nome in nomes:
        act = bpy.data.actions[nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
        f0, f1 = map(int, act.frame_range)
        for f in (f0, (f0 + f1) // 2):
            sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); m2 = M.evaluated_get(dg).to_mesh()
            P = [v.co.copy() for v in m2.vertices]; M.evaluated_get(dg).to_mesh_clear()
            R = [v.co for v in me.vertices]
            mx = max(((P[i] - P[g[0]]).length - (R[i] - R[g[0]]).length) for g in grupos for i in g[1:])
            pior[nome] = max(pior.get(nome, 0), mx)
    A.animation_data.action = None
    return {k.replace("Silverwing_", ""): round(v * 17.5, 3) for k, v in pior.items()}

CLIPES = ["Silverwing_Parado", "Silverwing_Andar", "Silverwing_Voo", "Silverwing_Pairar", "Silverwing_Curva_E"]
il, borda, nil, nb = ilhas_borda()
G = grupos_solda(il, borda)
print("ANTES ilhas", nil, "bordas_abertas", nb, "| grupos de solda", len(G), "vertices", sum(len(g) for g in G), "LIM", LIM)
print("ABERTURA_EXTRA_ANTES_studs (afastamento a mais que no repouso)", abertura(G, CLIPES))
if so_medir: raise SystemExit
gi = {g.index: g.name for g in M.vertex_groups}
for g in G:
    c = sum((me.vertices[i].co for i in g), Vector()) / len(g)
    acc = {}
    for i in g:
        for x in me.vertices[i].groups: acc[gi[x.group]] = acc.get(gi[x.group], 0) + x.weight / len(g)
    top = sorted(acc.items(), key=lambda t: -t[1])[:4]; s = sum(w for _, w in top) or 1
    for i in g:
        me.vertices[i].co = c
        for x in list(me.vertices[i].groups): M.vertex_groups[x.group].remove([i])
        for nm, w in top: M.vertex_groups[nm].add([i], w / s, "REPLACE")
n0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-7)
bm.to_mesh(me); bm.free(); me.update()
il, borda, nil, nb = ilhas_borda()
print("DEPOIS vertices", n0, "->", len(me.vertices), "ilhas", nil, "bordas_abertas", nb, "uv", [u.name for u in me.uv_layers])
bpy.ops.wm.save_mainfile()
print("SOLDAR_OK")
