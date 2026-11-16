"""v16: a CAUSA do 'pelo da cauda grudado na perna E' (print do usuario, 06/11): o corte da v10 ficou no lugar errado. Do lado
'pata' (classe_cauda = +1) ficou um LOBO inteiro da cauda (faixa comprida com pelo de cauda, entre a tampa da pata e o vinco
da coxa), pesado em Coxa_E/Tibia_E: no Andar ele anda com a perna.
Correcao (so pesos de osso e o atributo classe_cauda; geometria, UV, rig e clipes iguais; sobre anim_v14):
1. Lobo = vertices do lado +1 (sem tampas) mais perto, por distancia GEODESICA, da tampa da pata (lado_tampa +1) do que da
   fronteira com o corpo (faces 0): dA < dB. Calculado por LOD.
2. Peso do lobo e da tampa da pata = peso do vertice mais proximo da face interna da cauda (classe -1, sem tampa).
   Transicao no vinco: t = dA / (dA + dB); s = suave((t - T0) / (0,5 - T0)); peso = (1 - s) * cauda + s * original.
3. Faces do lobo passam a classe_cauda = -1 (lado da cauda) para os scripts seguintes (pelo_fresta_v15.py).
4. Pelagem: cartao cuja raiz (vertice mais perto do corpo) fica sobre o lobo recebe, rigido, o peso do vertice do corpo
   mais proximo da raiz (ja corrigido).
Uso: blender -b anim_v14/CR_LoboArtico_Anim.blend -P lobo_cauda_v16.py -- anim_v16a   (depois pelo_fresta_v15.py -- anim_v16)"""
import bpy, bmesh, sys, os, json, shutil, heapq
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath); T0 = 0.3
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
REL = {"parametros": {"T0": T0}}
def suave(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def gravar(o, i, w):
    for g in list(o.data.vertices[i].groups): o.vertex_groups[g.group].remove([i])
    w = dict(sorted(((k, x) for k, x in w.items() if x > 1e-4), key=lambda t: -t[1])[:4]); s = sum(w.values())
    for k, x in w.items(): (o.vertex_groups.get(k) or o.vertex_groups.new(name=k)).add([i], x / s, "REPLACE")
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
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
                if u not in vp: continue
                nd = dd + e.calc_length()
                if nd < d.get(u, 1e9): d[u] = nd; heapq.heappush(h, (nd, u.index))
        return d
    dA, dB = dij(A), dij(B)
    lobo = {v for v in vp if dA.get(v, 1e9) < dB.get(v, 1e9)} | (tp - vp)
    cau = [v for v in bm.verts if v not in tp and all(f[cl] == -1 and not f[la] for f in v.link_faces)]
    kd = KDTree(len(cau))
    for k, v in enumerate(cau): kd.insert(v.co, k)
    kd.balance()
    W = {v.index: {gn[g.group]: g.weight for g in me.vertices[v.index].groups} for v in bm.verts}
    novo = {}
    for v in lobo:
        wc = W[cau[kd.find(v.co)[1]].index]
        t = dA.get(v, 0.0) / max(1e-9, dA.get(v, 0.0) + dB.get(v, 1e9)) if v in vp else 0.0; s = suave((t - T0) / (0.5 - T0))
        w = {}
        for k, x in wc.items(): w[k] = w.get(k, 0) + (1 - s) * x
        for k, x in W[v.index].items(): w[k] = w.get(k, 0) + s * x
        novo[v.index] = w
    for f in bm.faces:
        if f[cl] == 1 and not f[la] and sum(v in lobo for v in f.verts) * 2 >= len(f.verts): f[cl] = -1
    nf = sum(1 for f in bm.faces if f[cl] == -1)
    bm.to_mesh(me); me.update()
    for i, w in novo.items(): gravar(o, i, w)                       # pesos DEPOIS do to_mesh
    R = {"vertices_lobo": len(lobo), "transicao_no_vinco": sum(1 for v in lobo if v in vp and 0 < suave((dA.get(v, 0) / max(1e-9, dA.get(v, 0) + dB.get(v, 1e9)) - T0) / (0.5 - T0)) < 1)}
    # pelagem
    po = bpy.data.objects.get(L + "_Pelagem")
    if po:
        fs = list(bm.faces); bvh = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in fs])
        gn = {g.index: g.name for g in o.vertex_groups}; Wn = {i: {gn[g.group]: g.weight for g in me.vertices[i].groups} for i in range(len(me.vertices))}
        loboi = {v.index for v in lobo}; pm = po.data; pb_ = bmesh.new(); pb_.from_mesh(pm); pb_.verts.ensure_lookup_table(); vis = set(); n = 0
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
            if vc.index not in loboi: continue
            for i in cc: gravar(po, i, Wn[vc.index])
            n += 1
        pb_.free(); R["cartoes_do_lobo"] = n
    bm.free(); REL[L] = R; print("V16 lobo", L, json.dumps(R), flush=True)
json.dump(REL, open(os.path.join(OUT, "lobo_cauda_v16.json"), "w"), indent=1)
ARM.animation_data.action = AC; bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("LOBO_V16_OK", flush=True)
