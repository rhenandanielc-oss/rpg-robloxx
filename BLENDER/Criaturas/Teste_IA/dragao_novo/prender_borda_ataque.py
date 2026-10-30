"""Prende a BORDA DE ATAQUE da membrana (faixa a frente do braco, entre ombro e punho) aos ossos do braco.
Com as asas armadas no chao (punho e dedos dobrados em relacao ao antebraco), essa faixa tinha peso misturado com
wing_3 / dedos 1 e 2 e se soltava do braco, aparecendo como uma fita solta na frente da asa. Agora cada vertice a
frente da linha ombro-cotovelo-punho segue so o umero (wing_1) ou o antebraco (wing_2), com mistura curta no cotovelo,
e a faixa (que ficava ~4 cm a frente do tubo do braco, com vao) e puxada para junto do braco (some dentro do tubo).
Uso: blender -b CR_Dragao_M2M.blend -P prender_borda_ataque.py   (salva no proprio arquivo; rodar uma vez)"""
import bpy, bmesh
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]; B = A.data.bones
assert not M.get("borda_ataque_presa"), "ja aplicado"
nomes = {g.index: g.name for g in M.vertex_groups}
bm = bmesh.new(); bm.from_mesh(M.data); bm.verts.ensure_lookup_table()
vis, memb = set(), []
for v in bm.verts:                                   # membranas: pecas soltas largas em X (criterio da exportacao)
    if v.index in vis: continue
    pilha, ilha = [v], []
    while pilha:
        x = pilha.pop()
        if x.index in vis: continue
        vis.add(x.index); ilha.append(x.index)
        for e in x.link_edges: pilha.append(e.other_vert(x))
    xs = [abs(bm.verts[i].co.x) for i in ilha]
    if max(xs) - min(xs) > 0.25 and len(ilha) < 3000: memb += ilha
bm.free()
mud = 0
for i in memb:
    v = M.data.vertices[i]; co = v.co; s = "l" if co.x > 0 else "r"; ax = abs(co.x)
    om, co_, pu = (B[n + s].head_local for n in ("wing_1_", "wing_2_", "wing_3_"))
    if not (abs(om.x) <= ax <= abs(pu.x)): continue
    a, b = (om, co_) if ax <= abs(co_.x) else (co_, pu)
    t = (ax - abs(a.x)) / (abs(b.x) - abs(a.x)); y_braco = a.y + (b.y - a.y) * t
    if co.y > y_braco - 0.004: continue              # atras da linha do braco: membrana normal
    k = (ax - abs(co_.x)) / 0.03                     # mistura no cotovelo (+-0,03)
    w2 = max(0.0, min(1.0, 0.5 + 0.5 * k))
    v.co.y = y_braco - 0.006                       # encosta no braco (dentro do tubo): sem fita solta
    for g in list(v.groups): M.vertex_groups[nomes[g.group]].remove([i])
    if w2 < 1: M.vertex_groups["wing_1_" + s].add([i], 1 - w2, "REPLACE")
    if w2 > 0: M.vertex_groups["wing_2_" + s].add([i], w2, "REPLACE")
    mud += 1
M["borda_ataque_presa"] = 1
print("BORDA_PRESA", mud, "vertices")
bpy.ops.wm.save_mainfile()
