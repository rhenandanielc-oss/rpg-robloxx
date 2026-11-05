"""E4: UV por regioes (cartas grandes) em vez do Smart UV (que picota a malha reduzida em milhares de ilhas).
Crescimento de regiao pela adjacencia: entra na carta a face cuja normal desvia < LIM graus da normal media da carta e
enquanto a carta tem < MAXF faces; bordas das cartas viram costura; desdobra por angulo (ABF) e empacota.
Funcao usada pelo e4_04 (importar) ou sozinho para teste: blender -b <x.blend> -P e4_uv_regioes.py -- <LIM> <MAXF>"""
import bpy, bmesh, math, sys
from mathutils import Vector
def uv_regioes(obj, LIM=55.0, MAXF=700, MINF=10):
    me = obj.data; bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.normal_update()
    lim = math.cos(math.radians(LIM)); carta = [-1] * len(bm.faces); k = 0
    ordem = sorted(range(len(bm.faces)), key=lambda i: -bm.faces[i].calc_area())
    for s in ordem:
        if carta[s] >= 0: continue
        n = bm.faces[s].normal.copy(); soma = n.copy(); fila = [s]; carta[s] = k; cnt = 1; mat = bm.faces[s].material_index
        while fila and cnt < MAXF:
            f = bm.faces[fila.pop(0)]
            for e in f.edges:
                for g in e.link_faces:
                    if carta[g.index] >= 0 or g.material_index != mat: continue
                    if g.normal.dot(soma.normalized()) < (lim if mat == 0 else -0.2): continue
                    carta[g.index] = k; soma += g.normal; fila.append(g.index); cnt += 1
        k += 1
    for _ in range(3):                                       # cartas minusculas entram na vizinha com mais arestas em comum
        tam = {}
        for c in carta: tam[c] = tam.get(c, 0) + 1
        for f in bm.faces:
            c = carta[f.index]
            if tam[c] >= MINF: continue
            viz = {}
            for e in f.edges:
                for g in e.link_faces:
                    cg = carta[g.index]
                    if cg != c and g.material_index == f.material_index: viz[cg] = viz.get(cg, 0) + 1
            if viz:
                alvo = max(viz, key=lambda x: (tam[x], viz[x]))
                for h in bm.faces:
                    if carta[h.index] == c: carta[h.index] = alvo
                tam[alvo] += tam[c]; tam[c] = 0
    k = len(set(carta))
    for e in bm.edges:
        lf = e.link_faces
        e.seam = len(lf) != 2 or carta[lf[0].index] != carta[lf[1].index] or not e.smooth
    bm.to_mesh(me); bm.free()
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=0.002)
    bpy.ops.uv.average_islands_scale()                      # mesma densidade de textura em todas as cartas
    bpy.ops.object.mode_set(mode="OBJECT")
    return k
def estat(obj):
    me = obj.data; uv = me.uv_layers.active.data
    uniq = {(l.vertex_index, round(uv[l.index].uv[0], 5), round(uv[l.index].uv[1], 5)) for l in me.loops}
    # distorcao: razao area UV / area 3D por face, normalizada
    import numpy as np
    r = []
    for p in me.polygons:
        a3 = p.area
        if a3 < 1e-9: continue
        us = [Vector(uv[i].uv) for i in p.loop_indices]
        a2 = 0.0
        for i in range(1, len(us) - 1): a2 += abs((us[i] - us[0]).cross(us[i + 1] - us[0])) / 2
        r.append(a2 / a3)
    r = np.array(r); r = r / np.median(r)
    return len(uniq), float(np.percentile(r, 5)), float(np.percentile(r, 95))
if __name__ == "__main__" and "--" in sys.argv:
    A = sys.argv[sys.argv.index("--") + 1:]
    o = bpy.data.objects["Leao_Solar_E4"]
    k = uv_regioes(o, float(A[0]), int(A[1]), int(A[2]))
    print("UVREG cartas", k, "verts", len(o.data.vertices), "verts_uv/dist p5,p95", estat(o))
