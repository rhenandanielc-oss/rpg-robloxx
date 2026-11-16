"""v15: depois da v14 (pesos), os renders em cores (vistas_pelo_cauda_v14.py cores) mostraram o resto do defeito: cartoes de
pelo da PERNA traseira E (raiz na coxa, peso 100% perna) que se estendem POR CIMA da cauda (LOW: 16, 8 com metade ou mais
sobre a cauda). No Andar eles deslizam sobre a cauda junto com a perna = 'pelo da cauda indo com a perna'.
Correcao (so geometria da pelagem, nos LODs com pelagem; corpo, pesos, UV, rig e clipes iguais; copia de anim_v14):
- para cada cartao de um lado (perna E: peso de perna >= 0,3; cauda: peso de cauda >= 0,3) com vertice cuja face do corpo
  mais proxima e do OUTRO lado (atributo 'classe_cauda' da v10), encolhe o cartao em direcao a raiz (os 2 vertices mais
  perto do corpo) ate nenhum vertice ficar sobre o outro lado (passo 0,05; minimo S_MIN);
- se mesmo em S_MIN continua sobre o outro lado (cartao que nasce na fresta) e a maioria dos vertices esta la: volta ao
  tamanho original e PASSA DE LADO, com o peso do vertice do corpo do outro lado mais perto da raiz (rigido no cartao).
Uso: blender -b anim_v14/CR_LoboArtico_Anim.blend -P pelo_fresta_v15.py -- anim_v15"""
import bpy, bmesh, sys, os, json, shutil
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath); S_MIN = 0.35
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
PE = {"Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"}; REL = {"parametros": {"S_MIN": S_MIN}}
for L in ("LOW", "LOD1"):
    c = bpy.data.objects[L + "_Corpo"]; bm = bmesh.new(); bm.from_mesh(c.data); cl = bm.faces.layers.int.get("classe_cauda"); fs = list(bm.faces)
    bvh = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in fs])
    def classe(p): return fs[bvh.find_nearest(p)[2]][cl]
    o = bpy.data.objects[L + "_Pelagem"]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}
    pb_ = bmesh.new(); pb_.from_mesh(me); pb_.verts.ensure_lookup_table(); vis = set(); R = {"perna_sobre_cauda": [], "cauda_sobre_perna": []}; PEND = []
    for v0 in pb_.verts:
        if v0.index in vis: continue
        st, cc = [v0], []; vis.add(v0.index)
        while st:
            x = st.pop(); cc.append(x.index)
            for e in x.link_edges:
                u = e.other_vert(x)
                if u.index not in vis: vis.add(u.index); st.append(u)
        pe = sum(g.weight for i in cc for g in me.vertices[i].groups if gn[g.group] in PE) / len(cc)
        ca = sum(g.weight for i in cc for g in me.vertices[i].groups if gn[g.group].startswith("Cauda")) / len(cc)
        if pe >= 0.3: outro, chave = -1, "perna_sobre_cauda"
        elif ca >= 0.3: outro, chave = 1, "cauda_sobre_perna"
        else: continue
        if not any(classe(pb_.verts[i].co) == outro for i in cc): continue
        dist = sorted(cc, key=lambda i: bvh.find_nearest(pb_.verts[i].co)[3]); raiz = (pb_.verts[dist[0]].co + pb_.verts[dist[1]].co) / 2
        p0 = {i: pb_.verts[i].co.copy() for i in cc}; s = 1.0
        while s > S_MIN:
            s = round(s - 0.05, 2)
            for i in cc: pb_.verts[i].co = raiz + (p0[i] - raiz) * s
            if not any(classe(pb_.verts[i].co) == outro for i in cc): break
        if any(classe(pb_.verts[i].co) == outro for i in cc):          # nasce na fresta: volta ao tamanho e passa para o OUTRO lado
            for i in cc: pb_.verts[i].co = p0[i]
            if sum(1 for i in cc if classe(p0[i]) == outro) * 2 >= len(cc):
                lado_f = [f for f in fs if f[cl] == outro]; bl = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in lado_f])
                f = lado_f[bl.find_nearest(raiz)[2]]; vc = min(f.verts, key=lambda v: (v.co - raiz).length)
                w = {c.vertex_groups[g.group].name: g.weight for g in c.data.vertices[vc.index].groups if g.weight > 1e-4}
                PEND.append((list(cc), w)); R.setdefault(chave + "_passou_de_lado", 0); R[chave + "_passou_de_lado"] += 1; continue
        R[chave].append(s)
    pb_.to_mesh(me); me.update(); pb_.free(); bm.free()
    for cc, w in PEND:                                              # pesos DEPOIS do to_mesh (o bmesh sobrescreveria os grupos)
        for i in cc:
            for g in list(me.vertices[i].groups): o.vertex_groups[g.group].remove([i])
            for k, x in w.items():
                vg = o.vertex_groups.get(k) or o.vertex_groups.new(name=k); vg.add([i], x / sum(w.values()), "REPLACE")
    PASS = {k: v for k, v in R.items() if not isinstance(v, list)}; R = {k: v for k, v in R.items() if isinstance(v, list)}
    REL[L] = {k: {"cartoes": len(v), "escala_min": min(v) if v else None, "escala_media": round(sum(v) / len(v), 3) if v else None, "no_minimo": sum(1 for x in v if x <= S_MIN + 1e-6)} for k, v in R.items()}; REL[L].update(PASS)
    print("V15 pelo", L, json.dumps(REL[L]), flush=True)
json.dump(REL, open(os.path.join(OUT, "pelo_fresta_v15.json"), "w"), indent=1)
ARM.animation_data.action = AC; bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("PELO_V15_OK", flush=True)
