"""v20: a 'mecha fina grudada na perna' que sobrou na v18 e a BORDA DE TRAS DA COXA E separada do resto da coxa por um SULCO
fundo do modelo do Meshy (render em cores: a tira e azul = perna; anda com a perna porque e perna, mas parece mecha solta).
v19 (parede do vinco por peso) foi descartada: arrastava a tampa da perna (faces esticadas no q33).
Correcao (so geometria do corpo; pesos, UV, rig e clipes iguais; copia de anim_v18 em anim_v20/): RASA o sulco.
- vertices do lado da pata (faces classe_cauda +1 ou tampa da pata) a menos de D_SULCO (geodesica pela pele do lado da
  pata) da borda do corte: PASSADAS de alisamento laplaciano (vizinhos do mesmo lado), deslocamento maximo MAX_D. A borda do
  corte entra no alisamento (a tira encosta na coxa) e a tampa da pata acompanha (relaxada junto). Repouso: faixa atras da cauda.
Uso: blender -b anim_v18/CR_LoboArtico_Anim.blend -P sulco_coxa_v20.py -- anim_v20"""
import bpy, bmesh, sys, os, json, shutil, heapq
from mathutils import Vector as V
A_ = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A_[0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
D_SULCO = float(os.environ.get("D_SULCO", 0.6)); MAX_D = float(os.environ.get("MAX_D", 0.3)); PASSADAS = int(os.environ.get("PASSADAS", 24))
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
REL = {"parametros": {"D_SULCO": D_SULCO, "MAX_D": MAX_D, "PASSADAS": PASSADAS}}
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    cl = bm.faces.layers.int.get("classe_cauda"); la = bm.faces.layers.int.get("lado_tampa")
    def pata(f): return f[cl] == 1 or f[la] == 1
    so_p = {v for v in bm.verts if v.link_faces and all(pata(f) for f in v.link_faces)}
    borda = {v for v in so_p if any(f[la] == 1 for f in v.link_faces) and any(f[cl] == 1 and not f[la] for f in v.link_faces)}
    d = {v: 0.0 for v in borda}; h = [(0.0, v.index) for v in borda]
    while h:
        dd, i = heapq.heappop(h); v = bm.verts[i]
        if dd > d.get(v, 1e9): continue
        for e in v.link_edges:
            u = e.other_vert(v); nd = dd + e.calc_length()
            if u in so_p and nd < D_SULCO and nd < d.get(u, 1e9): d[u] = nd; heapq.heappush(h, (nd, u.index))
    alvo = list(d); p0 = {v: v.co.copy() for v in alvo}
    for _ in range(PASSADAS):
        nov = {}
        for v in alvo:
            vz = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in so_p]
            if vz: nov[v] = sum((u.co for u in vz), V()) / len(vz)
        for v, p in nov.items():
            v.co = v.co * 0.5 + p * 0.5; dv = v.co - p0[v]
            if dv.length > MAX_D: v.co = p0[v] + dv.normalized() * MAX_D
    mx = max(((v.co - p0[v]).length for v in alvo), default=0.0)
    from mathutils.kdtree import KDTree
    desl = [(p0[v], v.co - p0[v]) for v in alvo]; n_c = 0
    bm.normal_update(); bm.to_mesh(o.data); o.data.update(); bm.free()
    po = bpy.data.objects.get(L + "_Pelagem")                           # cartoes com raiz na faixa: transladados junto com a pele
    if po and desl:
        kd = KDTree(len(desl))
        for k, (p_, _) in enumerate(desl): kd.insert(p_, k)
        kd.balance(); pb_ = bmesh.new(); pb_.from_mesh(po.data); pb_.verts.ensure_lookup_table(); vis = set()
        for v0 in pb_.verts:
            if v0.index in vis: continue
            st, cc = [v0], []; vis.add(v0.index)
            while st:
                x = st.pop(); cc.append(x)
                for e in x.link_edges:
                    u = e.other_vert(x)
                    if u.index not in vis: vis.add(u.index); st.append(u)
            raiz = min(cc, key=lambda x: kd.find(x.co)[2]); _, k, dk = kd.find(raiz.co)
            if dk > 0.12: continue
            for x in cc: x.co = x.co + desl[k][1]
            n_c += 1
        pb_.to_mesh(po.data); po.data.update(); pb_.free()
    REL[L] = {"vertices_alisados": len(alvo), "borda_do_corte": len(borda), "maior_deslocamento": round(mx, 4), "cartoes_transladados": n_c}
    print("V20 sulco", L, json.dumps(REL[L]), flush=True)
json.dump(REL, open(os.path.join(OUT, "sulco_coxa_v20.json"), "w"), indent=1)
ARM.animation_data.action = AC; bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("SULCO_V20_OK", flush=True)
