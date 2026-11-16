"""v13, passo 2: as manchas escuras da face interna da cauda E no Andar sao GEOMETRIA (lascas pontudas/amassadas do Meshy
na faixa que encostava na pata, sombreadas na fresta; continuam sem pelo e com descarte de faces de costas, e a repintura de
textura do passo 1 quase nao mudou nada). Correcao local por LOD no corpo (roda sobre anim_v13/, depois de
textura_borda_v13.py):
- vertices do lado da CAUDA (faces 'classe_cauda' = -1, sem as tampas) a menos de R_BORDA da borda do corte e a menos de
  D_OCULTO da superficie da pata no repouso (faixa escondida no repouso: nao muda a silhueta);
- PASSADAS de alisamento laplaciano (vizinhos do mesmo lado), borda do corte FIXA (continuidade com a tampa), deslocamento
  maximo MAX_D por vertice. Pesos, UV, clipes e rig iguais.
Uso: blender -b anim_v13/CR_LoboArtico_Anim.blend -P lascas_v13.py"""
import bpy, bmesh, os, json
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R_BORDA, D_OCULTO, MAX_D, PASSADAS = 0.6, 0.25, 0.2, 12
SRC = os.path.dirname(bpy.data.filepath); REL = {"parametros": {"R_BORDA": R_BORDA, "D_OCULTO": D_OCULTO, "MAX_D": MAX_D, "PASSADAS": PASSADAS}}
ARM = bpy.data.objects["LoboArtico_Rig"]; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    cls = bm.faces.layers.int.get("classe_cauda"); lad = bm.faces.layers.int.get("lado_tampa")
    tampa = [f for f in bm.faces if f[lad] != 0]; ts = set(tampa)
    borda = {v for f in tampa for v in f.verts if any(g not in ts for g in v.link_faces)}
    kd = KDTree(len(borda))
    for i, v in enumerate(borda): kd.insert(v.co, i)
    kd.balance()
    pata = [f for f in bm.faces if (f[cls] == 1 or f[lad] == 1)]
    bvp = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in pata])
    lado = {}
    for f in bm.faces:
        c_ = f[lad] or f[cls]
        if c_:
            for v in f.verts: lado.setdefault(v, set()).add(c_)
    alvo = [v for v, ls in lado.items() if ls == {-1} and v not in borda and kd.find(v.co)[2] < R_BORDA and bvp.find_nearest(v.co)[3] < D_OCULTO]
    sa = set(alvo); p0 = {v: v.co.copy() for v in alvo}
    for _ in range(PASSADAS):
        nov = {}
        for v in alvo:
            vz = [e.other_vert(v) for e in v.link_edges if lado.get(e.other_vert(v)) in ({-1},) or e.other_vert(v) in borda]
            if vz: nov[v] = sum((u.co for u in vz), V()) / len(vz)
        for v, p in nov.items():
            v.co = v.co * 0.4 + p * 0.6; d = v.co - p0[v]
            if d.length > MAX_D: v.co = p0[v] + d.normalized() * MAX_D
    mx = max(((v.co - p0[v]).length for v in alvo), default=0.0)
    vis = 0                                                              # quantos ficaram fora da faixa escondida (> D_OCULTO da pata)
    for v in alvo:
        if bvp.find_nearest(v.co)[3] > D_OCULTO + 0.05: vis += 1
    bm.to_mesh(o.data); bm.free(); o.data.update()
    REL[L] = {"vertices_alisados": len(alvo), "maior_deslocamento": round(mx, 4), "medio": round(sum((v.co - p0[v]).length for v in alvo) / max(1, len(alvo)), 4) if False else None,
              "sairam_da_faixa_escondida": vis}
    print("V13 lascas", L, REL[L], flush=True)
json.dump(REL, open(os.path.join(SRC, "lascas_v13.json"), "w"), indent=1)
ARM.animation_data.action = bpy.data.actions["Andar"]
bpy.ops.wm.save_mainfile(); print("LASCAS_V13_OK", flush=True)
