"""Diagnostico SO LEITURA dos cantos da boca (comissuras) no .blend com grupos (teste geometrico sem rig).
Canto K de cada lado = media dos vertices de PELE com peso de Mandibula entre 0,2 e 0,8 junto a linha da boca.
Medidas (zona r < 0,35 de K, arestas de pele/labio/mucosa; mandibula girada 32 graus como em teste_lod_v7.py):
comprimento em repouso e aberto (absoluto), razao, salto de peso por aresta, distribuicao dos pesos da pele, faces que
crescem >3x com area aberta visivel (>2e-4) ou viram (normal oposta a do repouso; separadas as viradas
visiveis, area aberta >2e-4: lascas quase degeneradas viram por ruido mesmo com pesos ~iguais).
Renders por canto (E = +x, D = -x), vistas lateral, 3/4 e baixo, fases repouso/meio/maximo, modos:
  pesos  = Mandibula (azul 0 -> verde 0,5 -> vermelho 1) + arame;
  classe = pele externa (cinza), labio (vinho), mucosa (rosa: gengiva/palato/assoalho/bochecha), garganta/saco fundo (roxo),
           dentes/lingua (amarelo) + arame;
  textura = material normal + arame.
Uso: blender -b <arquivo.blend> -P diag_canto_v8.py -- <dir_saida> [OBJ=LOW_Cabeca] [render]"""
import bpy, bmesh, sys, os, json, math
from mathutils import Vector as V, Matrix
from collections import Counter
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
NOME = next((x[4:] for x in a if x.startswith("OBJ=")), "LOW_Cabeca"); RENDER = "render" in a
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
BA, BB = PIV["mandibula"]["linha_boca"]; CANTO = PIV["mandibula"]["canto_y"]; PV = V(PIV["mandibula"]["pivo_sugerido"])
h = bpy.data.objects[NOME]; me = h.data; gi = {g.name: g.index for g in h.vertex_groups}; GM = gi["Mandibula"]
BAND = ["labio", "gengiva", "palato", "assoalho", "lingua", "dente", "garganta", "bochecha"]
bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.active; dl = bm.verts.layers.deform.active
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
def tipo(f):
    u = f.loops[0][uv].uv
    if 0.955 < u.x < 0.965 and u.y < 0.5: return BAND[min(7, int((u.y - 0.02) / 0.06))]
    if u.x > 0.90: return "anel"
    return "pele"
def classe(t): return {"pele": "pele", "labio": "labio", "gengiva": "mucosa", "palato": "mucosa", "assoalho": "mucosa", "bochecha": "mucosa",
                       "garganta": "garganta", "lingua": "dente_lingua", "dente": "dente_lingua", "anel": "anel"}[t]
W = [v[dl].get(GM, 0.0) for v in bm.verts]
P0 = [v.co.copy() for v in bm.verts]
def aberto(ang): return [PV + Matrix.Rotation(math.radians(ang) * w, 3, V((1, 0, 0))) @ (p - PV) for p, w in zip(P0, W)]
P1 = aberto(32.0)
R = {"objeto": NOME}
CANTOS = {}
for lado, s in (("E", 1), ("D", -1)):
    vs = [v for v in bm.verts if v.co.x * s > 0.1 and v.co.y < CANTO + 0.3 and abs(v.co.z - (BA + BB * v.co.y)) < 0.15
          and 0.2 < W[v.index] < 0.8 and v.link_faces and all(tipo(f) == "pele" for f in v.link_faces)]
    K = sum((v.co for v in vs), V()) / max(1, len(vs)) if vs else None
    if K is None: continue
    CANTOS[lado] = K
    zona = [v for v in bm.verts if (v.co - K).length < 0.35]; zs = {v.index for v in zona}
    es = [e for e in bm.edges if e.verts[0].index in zs and e.verts[1].index in zs and e.link_faces
          and all(classe(tipo(f)) in ("pele", "labio", "mucosa") for f in e.link_faces)]
    L = []
    for e in es:
        i, j = e.verts[0].index, e.verts[1].index; l0 = (P0[i] - P0[j]).length; l1 = (P1[i] - P1[j]).length
        L.append({"l0": l0, "l1": l1, "razao": l1 / max(l0, 1e-6), "dw": abs(W[i] - W[j]), "meio": (P0[i] + P0[j]) / 2,
                  "classe": "/".join(sorted({classe(tipo(f)) for f in e.link_faces}))})
    vis = [x for x in L if x["l1"] > 0.06]
    pele_w = [W[v.index] for v in zona if v.link_faces and all(tipo(f) == "pele" for f in v.link_faces)]
    def area(f, P): return sum(((P[f.verts[0].index] - P[f.verts[k].index]).cross(P[f.verts[k + 1].index] - P[f.verts[0].index])).length / 2 for k in range(1, len(f.verts) - 1))
    def normal(f, P): return (P[f.verts[1].index] - P[f.verts[0].index]).cross(P[f.verts[2].index] - P[f.verts[0].index])
    ruins = []
    for f in bm.faces:
        if not all(v.index in zs for v in f.verts) or classe(tipo(f)) not in ("pele", "labio", "mucosa"): continue
        a0, a1 = area(f, P0), area(f, P1); vira = normal(f, P0).dot(normal(f, P1)) < 0
        if (a1 > 3 * max(a0, 1e-9) and a1 > 2e-4) or vira: ruins.append((a1, a0, vira, classe(tipo(f))))
    R[lado] = {"canto_K": [round(x, 4) for x in K], "vertices_zona": len(zona),
               "arestas": len(L), "aresta_minima_repouso": round(min(x["l0"] for x in L), 5),
               "arestas_salto_peso_>0.3_com_l0<0.02": sum(1 for x in L if x["dw"] > 0.3 and x["l0"] < 0.02),
               "maior_aresta_aberta": round(max(x["l1"] for x in L), 4),
               "maior_alongamento_absoluto": round(max(x["l1"] - x["l0"] for x in L), 4),
               "visiveis(l1>0.06)": len(vis), "visiveis_razao>2": sum(1 for x in vis if x["razao"] > 2), "visiveis_razao>3": sum(1 for x in vis if x["razao"] > 3),
               "razao_p95_visiveis": round(sorted(x["razao"] for x in vis)[int(len(vis) * 0.95)], 3) if vis else 0,
               "piores": [{"l0": round(x["l0"], 4), "l1": round(x["l1"], 4), "razao": round(x["razao"], 2), "dw": round(x["dw"], 2), "classe": x["classe"],
                           "em": [round(c, 3) for c in x["meio"]]} for x in sorted(vis, key=lambda x: -x["razao"])[:8]],
               "pesos_pele_hist_0.1": dict(sorted(Counter(round(w, 1) for w in pele_w).items())),
               "faces_problema": {"n": len(ruins), "area_aberta_total": round(sum(r[0] for r in ruins), 5), "viradas": sum(1 for r in ruins if r[2]),
                                  "viradas_visiveis(area_aberta>2e-4)": sum(1 for r in ruins if r[2] and r[0] > 2e-4),
                                  "area_viradas_visiveis": round(sum(r[0] for r in ruins if r[2] and r[0] > 2e-4), 5),
                                  "classes": dict(Counter(r[3] for r in ruins))}}
    print("CANTO", lado, json.dumps({k: v for k, v in R[lado].items() if k != "piores"}), flush=True)
json.dump(R, open(os.path.join(OUT, "diag_canto_%s.json" % NOME), "w"), indent=1)
if RENDER and CANTOS:
    sc = bpy.context.scene
    for o in sc.objects:
        if o.type == "MESH": o.hide_render = o is not h
    for o in list(sc.objects):
        if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
    w_ = bpy.data.worlds.new("E"); sc.world = w_
    if w_.node_tree is None: w_.use_nodes = True
    w_.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.43, 0.45, 1)
    for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 2.0, (120, 0, 205)), ("F", 1.2, (65, 0, -120)), ("B", 0.8, (150, 0, 0))):
        l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo)
        lo.rotation_euler = [math.radians(x) for x in rot]
    CORC = {"pele": (0.75, 0.75, 0.75), "labio": (0.35, 0.05, 0.08), "mucosa": (0.95, 0.45, 0.55), "garganta": (0.45, 0.15, 0.6),
            "dente_lingua": (0.95, 0.85, 0.2), "anel": (0.3, 0.6, 0.9)}
    at_w = me.color_attributes.new("PesoM", "FLOAT_COLOR", "POINT"); at_c = me.color_attributes.new("Classe", "FLOAT_COLOR", "CORNER")
    for i, w in enumerate(W):
        at_w.data[i].color = (max(0, 2 * w - 1), 1 - abs(2 * w - 1), max(0, 1 - 2 * w), 1)
    for f in bm.faces:
        c = CORC[classe(tipo(f))]
        for l in f.loops: at_c.data[l.index].color = c + (1,)
    mats0 = list(me.materials)
    def mat_attr(nome, attr):
        m = bpy.data.materials.new(nome)
        if m.node_tree is None: m.use_nodes = True
        nt = m.node_tree; ca = nt.nodes.new("ShaderNodeVertexColor"); ca.layer_name = attr
        nt.links.new(ca.outputs[0], nt.nodes["Principled BSDF"].inputs["Base Color"]); nt.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
        return m
    MODOS = {"pesos": mat_attr("MPeso", "PesoM"), "classe": mat_attr("MClasse", "Classe"), "textura": None}
    wf = h.copy(); wf.data = h.data; wf.name = "Arame"; sc.collection.objects.link(wf); wf.hide_render = False
    md = wf.modifiers.new("W", "WIREFRAME"); md.thickness = 0.0012; md.use_replace = True; md.use_even_offset = False
    mw = bpy.data.materials.new("Arame")
    if mw.node_tree is None: mw.use_nodes = True
    mw.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
    sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.render.resolution_x, sc.render.resolution_y = 800, 600
    sc.view_settings.view_transform = "Standard"
    cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 55
    for fase, ang in (("repouso", 0), ("meio", 15), ("maximo", 32)):
        P = aberto(ang)
        for v, p in zip(me.vertices, P): v.co = p
        me.update()
        for modo, mt in MODOS.items():
            me.materials.clear()
            for m in mats0: me.materials.append(m)
            if mt is not None:
                for k in range(len(mats0)): me.materials[k] = mt
            me.materials.append(mw); md.material_offset = len(mats0)
            for lado, K in CANTOS.items():
                s = 1 if lado == "E" else -1
                for vnome, off in (("lateral", V((1.05 * s, -0.10, 0.05))), ("34", V((0.75 * s, -0.75, 0.12))), ("baixo", V((0.45 * s, -0.45, -0.85)))):
                    cam.location = K + off; alvo = K + V((0, 0.03, -0.06 if fase != "repouso" else 0)); cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
                    sc.render.filepath = os.path.join(OUT, "c_%s_%s_%s_%s.png" % (lado, modo, vnome, fase)); bpy.ops.render.render(write_still=True)
    for v, p in zip(me.vertices, P0): v.co = p
    me.materials.clear()
    for m in mats0: me.materials.append(m)
print("DIAG_CANTO_OK")
