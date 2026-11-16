"""v13, passo 3: CAUSA REAL das manchas escuras da face interna da cauda E no Andar = SOMBREAMENTO da tampa da v10.
Diagnostico (passos 1-2 quase nao mudaram a imagem): sem pelo e com descarte de faces de costas a mancha continua; no
Workbench a tampa e lisa, no EEVEE escura e facetada; as normais de canto da tampa estao invertidas/desalinhadas
(LOW 54 ruins / 27 invertidas de 846 cantos) porque parte das faces da tampa tem ENROLAMENTO oposto ao das vizinhas
(arestas com o mesmo sentido nas duas faces) e ha dobras (faces vizinhas com normais opostas) depois da reprojecao.
Correcao local por LOD no corpo (so faces 'lado_tampa' != 0 e seus vertices internos; borda do corte fixa):
1. ENROLAMENTO: busca em largura a partir das faces que NAO sao tampa (confiaveis); cada face da tampa recebe o sentido da
   maioria das vizinhas ja orientadas (bmesh.ops.reverse_faces preserva UV/atributos de canto);
2. DOBRAS: PASSADAS de alisamento laplaciano so nos vertices INTERNOS da tampa que tocam face dobrada (anel 1), mantendo a
   borda; deslocamento maximo MAX_D. Pesos de osso, UV, clipes e rig iguais.
Uso: blender -b anim_v13/CR_LoboArtico_Anim.blend -P normais_tampa_v13.py [-- medir]"""
import bpy, bmesh, os, sys, json
from collections import deque
from mathutils import Vector as V
MAX_D, PASSADAS, DOBRA = 0.08, 10, -0.3
MEDIR = "medir" in sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else False
SRC = os.path.dirname(bpy.data.filepath); REL = {"parametros": {"MAX_D": MAX_D, "PASSADAS": PASSADAS, "DOBRA": DOBRA}}
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
def contar(bm, lad):
    inv = dob = 0
    for e in bm.edges:
        if len(e.link_faces) != 2: continue
        f, g = e.link_faces
        if not (f[lad] or g[lad]): continue
        lf = next(l for l in f.loops if l.edge is e); lg = next(l for l in g.loops if l.edge is e)
        inv += lf.vert is lg.vert; dob += f.normal.dot(g.normal) < DOBRA
    return inv, dob
def cantos_ruins(o):
    me = o.data; la = me.attributes["lado_tampa"]; cn = me.corner_normals; r = i = t = 0
    for p in me.polygons:
        if la.data[p.index].value == 0: continue
        for li in p.loop_indices:
            d = cn[li].vector.dot(p.normal); t += 1; r += d < 0.3; i += d < 0
    return {"cantos_tampa": t, "ruins_lt_0_3": r, "invertidos": i}
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; R = {"antes": cantos_ruins(o)}
    bm = bmesh.new(); bm.from_mesh(o.data); lad = bm.faces.layers.int.get("lado_tampa"); bm.faces.ensure_lookup_table()
    R["antes"]["arestas_enrolamento_oposto"], R["antes"]["arestas_dobradas"] = contar(bm, lad)
    if not MEDIR:
        # 1. enrolamento consistente
        ok = {f.index for f in bm.faces if not f[lad]}; tampa = [f.index for f in bm.faces if f[lad]]; inverter = set()
        def sentido(f, g, e):                                   # +1 se f e g percorrem a aresta em sentidos opostos (consistentes)
            lf = next(l for l in f.loops if l.edge is e); lg = next(l for l in g.loops if l.edge is e)
            return -1 if lf.vert is lg.vert else 1
        pend = set(tampa); mudou = True
        while pend and mudou:
            mudou = False
            for i in sorted(pend):
                f = bm.faces[i]; votos = 0
                for e in f.edges:
                    if len(e.link_faces) != 2: continue
                    g = next(x for x in e.link_faces if x is not f)
                    if g.index in ok: votos += sentido(f, g, e) * (-1 if g.index in inverter else 1)
                if votos:
                    if votos < 0: inverter.add(i)
                    ok.add(i); pend.discard(i); mudou = True
        bmesh.ops.reverse_faces(bm, faces=[bm.faces[i] for i in inverter]); bm.normal_update()
        R["faces_tampa_invertidas"] = len(inverter); R["faces_tampa_sem_vizinha_orientada"] = len(pend)
        # 2. dobras: alisa vertices internos da tampa em volta das faces dobradas
        borda = {v for i in tampa for v in bm.faces[i].verts if any(not g[lad] for g in v.link_faces)}
        dobr = set()
        for e in bm.edges:
            if len(e.link_faces) == 2 and any(f[lad] for f in e.link_faces) and e.link_faces[0].normal.dot(e.link_faces[1].normal) < DOBRA:
                dobr |= {v for f in e.link_faces for v in f.verts}
        alvo = [v for v in dobr if v not in borda and all(g[lad] for g in v.link_faces)]
        p0 = {v: v.co.copy() for v in alvo}
        for _ in range(PASSADAS):
            nov = {v: sum((e.other_vert(v).co for e in v.link_edges), V()) / len(v.link_edges) for v in alvo}
            for v, p in nov.items():
                v.co = v.co * 0.5 + p * 0.5; d = v.co - p0[v]
                if d.length > MAX_D: v.co = p0[v] + d.normalized() * MAX_D
        bm.normal_update(); R["vertices_internos_alisados"] = len(alvo)
        R["maior_deslocamento"] = round(max(((v.co - p0[v]).length for v in alvo), default=0.0), 4)
        R["depois"] = {}; R["depois"]["arestas_enrolamento_oposto"], R["depois"]["arestas_dobradas"] = contar(bm, lad)
        bm.to_mesh(o.data); o.data.update(); R["depois"].update(cantos_ruins(o))
    bm.free(); REL[L] = R; print("V13 normais", L, json.dumps(R), flush=True)
if not MEDIR:
    json.dump(REL, open(os.path.join(SRC, "normais_tampa_v13.json"), "w"), indent=1)
    ARM.animation_data.action = AC; bpy.ops.wm.save_mainfile(); print("NORMAIS_V13_OK", flush=True)
