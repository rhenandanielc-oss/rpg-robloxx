"""v17, passo 0: posicoes do LOBO da cauda que o corte da v10 deixou do lado da pata (mesmo criterio de lobo_cauda_v16.py:
vertices do lado +1, sem tampas, mais perto por distancia geodesica da tampa da pata do que da fronteira com o corpo), por
LOD, no repouso. Servem de referencia para o corte novo (separar_cauda_v17.py) sobre a malha da v9.
Uso: blender -b anim_v14/CR_LoboArtico_Anim.blend -P exportar_lobo_v17.py -- corte_v17/lobo_pontos.json"""
import bpy, bmesh, sys, json, heapq
OUT = sys.argv[sys.argv.index("--") + 1:][0]
ARM = bpy.data.objects["LoboArtico_Rig"]; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update(); R = {}
for L in ("LOW", "LOD1", "LOD2"):
    bm = bmesh.new(); bm.from_mesh(bpy.data.objects[L + "_Corpo"].data); bm.verts.ensure_lookup_table()
    cl = bm.faces.layers.int.get("classe_cauda"); la = bm.faces.layers.int.get("lado_tampa")
    vp = {v for f in bm.faces if f[cl] == 1 and not f[la] for v in f.verts}; tp = {v for f in bm.faces if f[la] == 1 for v in f.verts}
    A = tp & vp; B = {v for v in vp if any(f[cl] == 0 and not f[la] for f in v.link_faces)}
    def dij(src):
        d = {v: 0.0 for v in src}; h = [(0.0, v.index) for v in src]
        while h:
            dd, i = heapq.heappop(h); v = bm.verts[i]
            if dd > d.get(v, 1e9): continue
            for e in v.link_edges:
                u = e.other_vert(v)
                if u in vp and dd + e.calc_length() < d.get(u, 1e9): d[u] = dd + e.calc_length(); heapq.heappush(h, (d[u], u.index))
        return d
    dA, dB = dij(A), dij(B)
    R[L] = [[round(c, 5) for c in v.co] for v in vp if dA.get(v, 1e9) < dB.get(v, 1e9)]
    print("LOBO", L, len(R[L]), flush=True); bm.free()
json.dump(R, open(OUT, "w")); print("EXPORT_LOBO_OK", flush=True)
