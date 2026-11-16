"""v14: o PELO DA CAUDA ainda acompanha a perna traseira E no Andar (relato do usuario, 06/11). Diagnostico em anim_v13:
- pelagem: 12 cartoes (LOW) / 11 (LOD1) com peso MISTO cauda (Cauda1-4) + perna E (Coxa_E/Tibia_E/Metatarso_E): a parte
  da perna puxa o cartao junto com a coxa;
- corpo: vertices do lado da cauda (faces 'classe_cauda' = -1) e da base da cauda na linha media com Coxa_E ate 0,26.
Correcao (so pesos de osso, sobre uma copia de anim_v13 em anim_v14/; geometria, UV, textura, rig e clipes iguais):
1. CORPO: lado da cauda (alguma face vizinha -1, nenhuma +1) -> zera perna E; lado da pata (alguma +1, nenhuma -1) -> zera Cauda*; vizinho de -1 e +1 = meio; base da cauda na
   linha media (faces 0, |x| < X_MEIO, com Cauda > 0,05) -> zera Coxa_E/Coxa_D/Tibia/Metatarso. O peso retirado vai para
   os ossos que sobram (normaliza); se nada sobra, vai para Quadril. PASSADAS de alisamento so nesses vertices, sem
   reintroduzir os ossos retirados.
2. PELAGEM: cada cartao (ilha) com cauda > 0,05 e QUALQUER peso de perna E recebe dono = classe da face do corpo mais proxima do centro do cartao
   (no repouso); remove os ossos do outro lado pela mesma regra e normaliza. Cartao todo rigido no lado do dono.
3. <= 4 influencias, soma 1.
Uso: blender -b anim_v13/CR_LoboArtico_Anim.blend -P pesos_cauda_v14.py -- anim_v14"""
import bpy, bmesh, sys, os, json, shutil
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); X_MEIO, PASSADAS = 0.35, 2
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
PERNA_E = {"Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"}; COXAS = PERNA_E | {"Coxa_D", "Tibia_D", "Metatarso_D", "DedosPe_D"}
def e_cauda(n): return n.startswith("Cauda")
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
REL = {"parametros": {"X_MEIO": X_MEIO, "PASSADAS": PASSADAS}}
def pesos(o, v, gn): return {gn[g.group]: g.weight for g in v.groups if g.weight > 1e-6}
def gravar(o, v, w, gn_inv):
    for g in list(v.groups): o.vertex_groups[g.group].remove([v.index])
    w = dict(sorted(((k, x) for k, x in w.items() if x > 1e-4), key=lambda t: -t[1])[:4]); s = sum(w.values())
    if s <= 0: w, s = {"Quadril": 1.0}, 1.0
    for k, x in w.items():
        if k not in gn_inv: gn_inv[k] = o.vertex_groups.new(name=k).index
        o.vertex_groups[gn_inv[k]].add([v.index], x / s, "REPLACE")
def regra(w, lado):
    if lado == "cauda": return {k: x for k, x in w.items() if k not in PERNA_E}
    if lado == "pata": return {k: x for k, x in w.items() if not e_cauda(k)}
    if lado == "meio": return {k: x for k, x in w.items() if k not in COXAS}
    return w
def misto(w, lado):
    c = sum(x for k, x in w.items() if e_cauda(k))
    if lado == "cauda": return any(k in PERNA_E for k in w)
    if lado == "pata": return c > 0
    if lado == "meio": return c > 0.05 and any(k in COXAS for k in w)
    return False
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}; gi = {v: k for k, v in gn.items()}
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); cl = bm.faces.layers.int.get("classe_cauda")
    def lado_v(i, co):
        cs = {f[cl] for f in bm.verts[i].link_faces}
        if -1 in cs and 1 in cs: return "meio"
        if -1 in cs: return "cauda"                              # inclui a fronteira cauda/quadril
        if 1 in cs: return "pata"
        if abs(co.x) < X_MEIO: return "meio"
        return None
    alvo = {}
    for v in me.vertices:
        lado = lado_v(v.index, v.co); w = pesos(o, v, gn)
        if lado and misto(w, lado): alvo[v.index] = lado; gravar(o, v, regra(w, lado), gi)
    gn = {g.index: g.name for g in o.vertex_groups}
    for _ in range(PASSADAS):                                   # alisamento sem reintroduzir ossos retirados
        nov = {}
        for i, lado in alvo.items():
            viz = [e.other_vert(bm.verts[i]).index for e in bm.verts[i].link_edges]; acc = dict(pesos(o, me.vertices[i], gn))
            for j in viz:
                for k, x in pesos(o, me.vertices[j], gn).items(): acc[k] = acc.get(k, 0) + x / len(viz)
            nov[i] = regra(acc, lado)
        for i, w in nov.items(): gravar(o, me.vertices[i], w, gi)
        gn = {g.index: g.name for g in o.vertex_groups}
    R = {"corpo_vertices_corrigidos": {s: sum(1 for x in alvo.values() if x == s) for s in ("cauda", "pata", "meio")}}
    # pelagem
    faces = list(bm.faces); bvh = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in faces])
    po = bpy.data.objects[L + "_Pelagem"] if (L + "_Pelagem") in bpy.data.objects else None
    if po:
        pm = po.data; pgn = {g.index: g.name for g in po.vertex_groups}; pgi = {v: k for k, v in pgn.items()}
        pb = bmesh.new(); pb.from_mesh(pm); pb.verts.ensure_lookup_table(); vis = set(); n_c = {"cauda": 0, "pata": 0, "meio": 0}
        for v0 in pb.verts:
            if v0.index in vis: continue
            st, comp = [v0], []; vis.add(v0.index)
            while st:
                x = st.pop(); comp.append(x.index)
                for e in x.link_edges:
                    u = e.other_vert(x)
                    if u.index not in vis: vis.add(u.index); st.append(u)
            ws = {i: pesos(po, pm.vertices[i], pgn) for i in comp}
            c = sum(x for w in ws.values() for k, x in w.items() if e_cauda(k)); p = sum(x for w in ws.values() for k, x in w.items() if k in PERNA_E)
            if not (c > 0.05 and p > 0): continue                 # qualquer peso de perna E num cartao com cauda
            cen = sum((pm.vertices[i].co for i in comp), pm.vertices[comp[0]].co * 0) / len(comp)
            f = faces[bvh.find_nearest(cen)[2]]; lado = {-1: "cauda", 1: "pata"}.get(f[cl], "meio" if abs(cen.x) < X_MEIO else ("cauda" if c >= p else "pata"))
            for i, w in ws.items(): gravar(po, pm.vertices[i], regra(w, lado), pgi)
            n_c[lado] += 1
        pb.free(); R["pelagem_cartoes_corrigidos"] = n_c
    bm.free(); REL[L] = R; print("V14 pesos", L, json.dumps(R), flush=True)
json.dump(REL, open(os.path.join(OUT, "pesos_cauda_v14.json"), "w"), indent=1)
ARM.animation_data.action = AC; bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("PESOS_V14_OK", flush=True)
