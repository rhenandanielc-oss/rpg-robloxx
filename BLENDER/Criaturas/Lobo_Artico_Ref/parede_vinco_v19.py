"""v19: a 'mecha fina grudada na perna' que sobrou na v17/v18 (print do usuario, 06/11) e a PAREDE do vinco da coxa do lado
da cauda: uma faixa estreita de pele do lado 'pata' (classe_cauda +1) entre a borda do corte e o fundo do vinco. O vinco nao
e aresta viva na malha (mais aneis de corte nao chegam ao fundo: v18 com 1 e 2 aneis), entao a faixa e tratada por PESO:
- vertices do lado +1 (sem tampa) e da tampa da pata (lado_tampa +1) a menos de D_PAREDE (geodesica, pela pele do lado +1)
  da borda do corte recebem peso = mistura do peso da cauda (vertice mais proximo da face interna da cauda) com o proprio:
  s = suave(d / D_PAREDE); peso = (1 - s) * cauda + s * proprio. A borda do corte acompanha a cauda; o fundo do vinco, a perna.
- cartoes de pelo cuja raiz fica nessa faixa recebem, rigido, o peso do vertice do corpo mais proximo da raiz.
So pesos (geometria, UV, rig e clipes iguais; LOW e LOD1; LOD2 sem corte fino). Copia de anim_v18 em anim_v19/.
Uso: blender -b anim_v18/CR_LoboArtico_Anim.blend -P parede_vinco_v19.py -- anim_v19"""
import bpy, bmesh, sys, os, json, shutil, heapq
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
A_ = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A_[0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
D_PAREDE = float(os.environ.get("D_PAREDE", 0.25))
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
REL = {"parametros": {"D_PAREDE": D_PAREDE}}
def suave(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def gravar(o, i, w):
    for g in list(o.data.vertices[i].groups): o.vertex_groups[g.group].remove([i])
    w = dict(sorted(((k, x) for k, x in w.items() if x > 1e-4), key=lambda t: -t[1])[:4]); s = sum(w.values())
    for k, x in w.items(): (o.vertex_groups.get(k) or o.vertex_groups.new(name=k)).add([i], x / s, "REPLACE")
for L in ("LOW", "LOD1"):
    o = bpy.data.objects[L + "_Corpo"]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); cl = bm.faces.layers.int.get("classe_cauda"); la = bm.faces.layers.int.get("lado_tampa")
    lado_p = {v for f in bm.faces if (f[cl] == 1 or f[la] == 1) for v in f.verts}
    so_p = {v for v in lado_p if all((f[cl] == 1 or f[la] == 1) for f in v.link_faces)}
    borda = {v for v in lado_p if v.is_boundary is False and any(f[la] == 1 for f in v.link_faces) and any(f[cl] == 1 and not f[la] for f in v.link_faces)}
    d = {v: 0.0 for v in borda}; h = [(0.0, v.index) for v in borda]
    while h:
        dd, i = heapq.heappop(h); v = bm.verts[i]
        if dd > d.get(v, 1e9): continue
        for e in v.link_edges:
            u = e.other_vert(v)
            if u in so_p and dd + e.calc_length() < d.get(u, 1e9) and dd + e.calc_length() < D_PAREDE: d[u] = dd + e.calc_length(); heapq.heappush(h, (d[u], u.index))
    cau = [v for v in bm.verts if all(f[cl] == -1 and not f[la] for f in v.link_faces) and v.link_faces]
    kd = KDTree(len(cau))
    for k, v in enumerate(cau): kd.insert(v.co, k)
    kd.balance()
    W = {v.index: {gn[g.group]: g.weight for g in me.vertices[v.index].groups} for v in bm.verts}
    novo = {}
    for v, dv in d.items():
        s = suave(dv / D_PAREDE); wc = W[cau[kd.find(v.co)[1]].index]; w = {}
        for k, x in wc.items(): w[k] = w.get(k, 0) + (1 - s) * x
        for k, x in W[v.index].items(): w[k] = w.get(k, 0) + s * x
        novo[v.index] = w
    for i, w in novo.items(): gravar(o, i, w)
    R = {"vertices_parede": len(novo), "borda_do_corte": len(borda)}
    po = bpy.data.objects.get(L + "_Pelagem")
    if po:
        fs = list(bm.faces); bvh = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in fs])
        gn = {g.index: g.name for g in o.vertex_groups}; Wn = {i: {gn[g.group]: g.weight for g in me.vertices[i].groups} for i in novo}
        pm = po.data; pb_ = bmesh.new(); pb_.from_mesh(pm); pb_.verts.ensure_lookup_table(); vis = set(); n = 0
        for v0 in pb_.verts:
            if v0.index in vis: continue
            st, cc = [v0], []; vis.add(v0.index)
            while st:
                x = st.pop(); cc.append(x.index)
                for e in x.link_edges:
                    u = e.other_vert(x)
                    if u.index not in vis: vis.add(u.index); st.append(u)
            raiz = min(cc, key=lambda i: bvh.find_nearest(pb_.verts[i].co)[3]); loc, _, fi, _ = bvh.find_nearest(pb_.verts[raiz].co)
            vc = min(fs[fi].verts, key=lambda v: (v.co - loc).length)
            if vc.index not in novo: continue
            for i in cc: gravar(po, i, Wn[vc.index])
            n += 1
        pb_.free(); R["cartoes_da_parede"] = n
    bm.free(); REL[L] = R; print("V19 parede", L, json.dumps(R), flush=True)
json.dump(REL, open(os.path.join(OUT, "parede_vinco_v19.json"), "w"), indent=1)
ARM.animation_data.action = AC; bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("PAREDE_V19_OK", flush=True)
