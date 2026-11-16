"""Mede, no Andar, quanto os cartoes de pelo que tinham peso misto cauda + perna E (lista do anim_v13) se afastam do osso da
cauda dominante: vertice no espaco do osso (pose) - no repouso; maximo no ciclo. Cartao preso na cauda = perto de 0.
Uso: blender -b <anim.blend> -P medir_pelo_cauda_v14.py -- <saida_json>"""
import bpy, bmesh, sys, json
OUT = sys.argv[sys.argv.index("--") + 1:][0]; sc = bpy.context.scene
ARM = bpy.data.objects["LoboArtico_Rig"]; ac = bpy.data.actions["Andar"]; ARM.animation_data.action = ac
if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
PERNA_E = {"Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"}; R = {}
for L in ("LOW", "LOD1"):
    o = bpy.data.objects[L + "_Pelagem"]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); vis = set(); cards = []
    for v0 in bm.verts:
        if v0.index in vis: continue
        st, c = [v0], []; vis.add(v0.index)
        while st:
            x = st.pop(); c.append(x.index)
            for e in x.link_edges:
                u = e.other_vert(x)
                if u.index not in vis: vis.add(u.index); st.append(u)
        cards.append(c)
    bm.free()
    # cartoes da regiao cauda/pata E com algum peso de cauda (no arquivo atual)
    sel = []
    for c in cards:
        cw = {}
        for i in c:
            for g in me.vertices[i].groups: cw[gn[g.group]] = cw.get(gn[g.group], 0) + g.weight
        cau = {k: x for k, x in cw.items() if k.startswith("Cauda")}
        if sum(cau.values()) > 0.5 and (any(k in PERNA_E for k in cw) or True):
            co = sum((me.vertices[i].co for i in c), me.vertices[c[0]].co * 0) / len(c)
            if co.y > 2.2 and co.z < 4.6: sel.append((c, max(cau, key=cau.get), any(k in PERNA_E for k in cw)))
    sc.frame_set(0); dg = bpy.context.evaluated_depsgraph_get()
    def pos(c):
        ev = o.evaluated_get(dg).data; return [o.matrix_world @ ev.vertices[i].co for i in c]
    rest = {}
    ARM.animation_data.action = None
    for pb in ARM.pose.bones: pb.matrix_basis.identity()
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    for k, (c, b, _) in enumerate(sel):
        M = (ARM.matrix_world @ ARM.pose.bones[b].matrix).inverted(); rest[k] = [M @ p for p in pos(c)]
    ARM.animation_data.action = ac; ARM.animation_data.action_slot = ac.slots[0]
    mx = [0.0] * len(sel)
    for q in range(0, 37):
        sc.frame_set(q); dg = bpy.context.evaluated_depsgraph_get()
        for k, (c, b, _) in enumerate(sel):
            M = (ARM.matrix_world @ ARM.pose.bones[b].matrix).inverted()
            d = max((M @ p - r).length for p, r in zip(pos(c), rest[k])); mx[k] = max(mx[k], d)
    srt = sorted(mx, reverse=True)
    R[L] = {"cartoes_da_cauda_medidos": len(sel), "com_peso_de_perna_E": sum(1 for s in sel if s[2]),
            "afastamento_max_do_osso_da_cauda": round(srt[0], 4) if srt else 0, "top5": [round(x, 4) for x in srt[:5]],
            "acima_de_0_05": sum(1 for x in mx if x > 0.05)}
    print("PELO", L, json.dumps(R[L]), flush=True)
json.dump(R, open(OUT, "w"), indent=1)
