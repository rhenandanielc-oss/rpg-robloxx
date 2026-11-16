"""v22: correcao LOCAL de pesos da transicao ventre - flanco - coxa DIREITA (autorizada 09/11; so pesos e cartoes da regiao).
Diagnostico (diag_flanco_v22.py + diag_vistas_v22.py sobre anim_v21): a pele e continua (sem fusao anomala nem furo); a prega
do flanco (faixa de triangulos longos do Meshy entre o joelho D e a barriga, ja presente no repouso) fica numa fronteira de
peso ABRUPTA (1-2 aneis): Coluna1/Coluna2 de um lado, Coxa_D + Tibia_D do outro. Perna atras (Trote q6) -> a prega estica
(membrana); perna a frente (Corrida q8-q12, Andar q14) -> a borda da coxa entra na barriga (faces viradas, avesso escuro).
Correcao (anim_v21 so lido; saida anim_v22; geometria, UV, rig, acoes iguais):
1. Regiao: pele do corpo do lado D e linha media (x < X_MAX), -0,8 < y < Y_MAX, 0,8 < z < 4,2, fora das faces do corte da
   cauda/pata E (classe_cauda/lado_tampa != 0) e longe da pata E (Coxa_E+Tibia_E < 0,1). Lado PERNA: Coxa_D+Tibia_D+Metatarso_D
   > 0,5. Fronteira = vertices das arestas em que o peso da perna D (Coxa_D+Tibia_D+Metatarso_D) CRUZA 0,5 (ha vertices
   mistos na prega: a 1a versao, que pedia vizinhos 'puro corpo' x 'pura perna', achava so 6 vertices).
2. Distancia GEODESICA d a fronteira (pela pele da regiao); faixa = d < W de cada lado.
3. No lado perna da faixa com d < W_TIB: o peso de Tibia_D vai para Coxa_D (a pele da prega junto a barriga acompanha a
   coxa, nao o joelho); Tibia_D NAO se espalha para o corpo no passo 4.
4. PASSADAS de difusao (media com os vizinhos) so nos vertices da faixa; fora dela os pesos ficam fixos (ancoras): transicao
   gradual sem puxar a barriga inteira. <= 4 influencias, soma 1.
5. Cartoes de pelo com raiz na faixa: peso da pele interpolado no ponto da raiz (como no passo 6 da v10).
Uso: blender -b anim_v21/CR_LoboArtico_Anim.blend -P pesos_flanco_v22.py -- anim_v22"""
import bpy, bmesh, sys, os, json, shutil, heapq
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc
A_ = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A_[0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
W_FAIXA = float(os.environ.get("W_FAIXA", 0.45)); W_TIB = float(os.environ.get("W_TIB", 0.3)); PASSADAS = int(os.environ.get("PASSADAS", 25))
X_MAX, Y_MAX = 0.35, 2.4
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; SL = ARM.animation_data.action_slot; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update(); OSS = {b.name for b in ARM.data.bones}
PERNA = ("Coxa_D", "Tibia_D", "Metatarso_D"); CORPO = ("Coluna1", "Coluna2", "Coluna3", "Quadril"); PATA_E = ("Coxa_E", "Tibia_E")
REL = {"parametros": {"W_FAIXA": W_FAIXA, "W_TIB": W_TIB, "PASSADAS": PASSADAS, "X_MAX": X_MAX, "Y_MAX": Y_MAX}}
def gravar(o, i, w):
    for g in list(o.data.vertices[i].groups): o.vertex_groups[g.group].remove([i])
    w = dict(sorted(((k, x) for k, x in w.items() if x > 1e-4), key=lambda t: -t[1])[:4]); s = sum(w.values())
    for k, x in w.items(): (o.vertex_groups.get(k) or o.vertex_groups.new(name=k)).add([i], x / s, "REPLACE")
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); cl = bm.faces.layers.int.get("classe_cauda"); la = bm.faces.layers.int.get("lado_tampa")
    W = {v.index: {gn[g.group]: g.weight for g in me.vertices[v.index].groups if gn[g.group] in OSS and g.weight > 1e-5} for v in bm.verts}
    def soma(i, ks): return sum(W[i].get(k, 0.0) for k in ks)
    reg = {v for v in bm.verts if v.co.x < X_MAX and -0.8 < v.co.y < Y_MAX and 0.8 < v.co.z < 4.2 and v.link_faces
           and all(f[cl] == 0 and f[la] == 0 for f in v.link_faces) and soma(v.index, PATA_E) < 0.1}
    perna = {v for v in reg if soma(v.index, PERNA) > 0.5}; corpo = {v for v in reg if soma(v.index, CORPO) > 0.5 and soma(v.index, PERNA) < 0.1}
    front = {v for v in reg for e in v.link_edges if e.other_vert(v) in reg and (soma(v.index, PERNA) - 0.5) * (soma(e.other_vert(v).index, PERNA) - 0.5) < 0}
    d = {v: 0.0 for v in front}; h = [(0.0, v.index) for v in front]
    while h:
        dd, i = heapq.heappop(h); v = bm.verts[i]
        if dd > d.get(v, 1e9): continue
        for e in v.link_edges:
            u = e.other_vert(v); nd = dd + e.calc_length()
            if u in reg and nd < W_FAIXA and nd < d.get(u, 1e9): d[u] = nd; heapq.heappush(h, (nd, u.index))
    faixa = set(d); lado_perna = {v for v in faixa if soma(v.index, PERNA) >= soma(v.index, CORPO)}
    tinha_tib = {v.index for v in faixa if W[v.index].get("Tibia_D", 0) > 1e-4}
    n_tib = 0
    for v in lado_perna:                                              # 3. Tibia_D -> Coxa_D na prega junto a barriga
        if d[v] < W_TIB and W[v.index].get("Tibia_D", 0) > 0:
            w = W[v.index]; w["Coxa_D"] = w.get("Coxa_D", 0) + w.pop("Tibia_D"); n_tib += 1
    for _ in range(PASSADAS):                                         # 4. difusao so na faixa; fora = ancoras
        nov = {}
        for v in faixa:
            vz = [e.other_vert(v) for e in v.link_edges]; acc = {}
            for u in vz:
                for k, x in W[u.index].items(): acc[k] = acc.get(k, 0) + x / len(vz)
            w = {k: 0.5 * W[v.index].get(k, 0) + 0.5 * acc.get(k, 0) for k in set(W[v.index]) | set(acc)}
            if v.index not in tinha_tib or (v in lado_perna and d[v] < W_TIB): w.pop("Tibia_D", None)
            t = sum(w.values()); nov[v.index] = {k: x / t for k, x in w.items() if x > 1e-5}
        W.update(nov)
    for v in faixa: gravar(o, v.index, W[v.index])
    gn = {g.index: g.name for g in o.vertex_groups}
    barriga = [v for v in faixa if abs(v.co.x) < 0.3 and v.co.z < 2.9]
    R = {"vertices_regiao": len(reg), "fronteira": len(front), "faixa": len(faixa), "faixa_lado_perna": len(lado_perna), "tibia_para_coxa": n_tib,
         "coxaD_max_na_linha_media_da_barriga": round(max((sum(g.weight for g in me.vertices[v.index].groups if gn[g.group] in ("Coxa_D", "Tibia_D")) for v in barriga), default=0.0), 3)}
    po = bpy.data.objects.get(L + "_Pelagem")
    if po:
        pos = [v.co.copy() for v in me.vertices]; fac = [list(p.vertices) for p in me.polygons]; bvh = BVHTree.FromPolygons(pos, fac)
        WC = [{gn[g.group]: g.weight for g in v.groups if gn[g.group] in OSS} for v in me.vertices]; fx = {v.index for v in faixa}
        pb_ = bmesh.new(); pb_.from_mesh(po.data); pb_.verts.ensure_lookup_table(); vis = set(); n_c = 0; pend = []
        for v0 in pb_.verts:
            if v0.index in vis: continue
            st, cc = [v0], []; vis.add(v0.index)
            while st:
                x = st.pop(); cc.append(x.index)
                for e in x.link_edges:
                    u = e.other_vert(x)
                    if u.index not in vis: vis.add(u.index); st.append(u)
            raiz = min(cc, key=lambda i: bvh.find_nearest(pb_.verts[i].co)[3]); loc, _, fi, _ = bvh.find_nearest(pb_.verts[raiz].co)
            if not any(i in fx for i in fac[fi]): continue
            bc = poly_3d_calc([pos[i] for i in fac[fi]], loc); w = {}
            for i, b in zip(fac[fi], bc):
                for k, x in WC[i].items(): w[k] = w.get(k, 0) + x * b
            pend.append((cc, w)); n_c += 1
        pb_.free()
        for cc, w in pend:
            for i in cc: gravar(po, i, w)
        R["cartoes_repesados"] = n_c
    bm.free(); REL[L] = R; print("V22 flanco", L, json.dumps(R), flush=True)
json.dump(REL, open(os.path.join(OUT, "pesos_flanco_v22.json"), "w"), indent=1)
ARM.animation_data.action = AC
if SL: ARM.animation_data.action_slot = SL
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("FLANCO_V22_OK", flush=True)
