"""Auditoria SO LEITURA das malhas de jogo do Lobo Artico (nao salva nada). Grava <saida>/auditoria.json.
Por malha: tris, faces degeneradas, vertices duplicados (<1e-5), soltos, arestas nao-manifold, bordas abertas por
regiao (boca, olhos, costura, outras), arestas com enrolamento invertido, o que o validate() do Blender corrigiria.
Costura cabeca-corpo: distancia entre os vertices das duas bordas. Medidas: topo do pelo na cernelha, topo dos
cristais, orelhas, apoio e posicao das 4 patas.
Uso: blender -b <arquivo.blend> -P auditar_lobo.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, math, io, contextlib
from mathutils import Vector as V
from mathutils.kdtree import KDTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
BA, BB = PIV["mandibula"]["linha_boca"]; CANTO = PIV["mandibula"]["canto_y"]
OLHOS = [V(o["centro_globo"]) for o in PIV["olhos"].values()]
COST_P, COST_N = V(PIV.get("costura", {}).get("ponto", (0, -4.55, 4.90))), V(PIV.get("costura", {}).get("normal", (0, -0.7433, 0.6690)))
def regiao(p):
    if abs((p - COST_P).dot(COST_N)) < 0.03: return "costura"
    if p.y < CANTO + 0.05 and abs(p.z - (BA + BB * p.y)) < 0.15: return "boca"
    if any((p - s).length < 0.35 for s in OLHOS): return "olhos"
    return "outras"
rel = {"malhas": {}}
for o in bpy.data.objects:
    if o.type != "MESH" or not o.name.startswith(("LOW_", "LOD1_", "LOD2_")): continue
    me = o.data; bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    kd = KDTree(len(bm.verts))
    for v in bm.verts: kd.insert(v.co, v.index)
    kd.balance()
    dup = sum(1 for v in bm.verts for (c, i, d) in kd.find_range(v.co, 1e-5) if i > v.index)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    soltos = sum(1 for v in bm.verts if not v.link_faces)
    nm = [e for e in bm.edges if not e.is_manifold and not e.is_boundary]
    bordas = {}
    for e in bm.edges:
        if e.is_boundary:
            r = regiao((e.verts[0].co + e.verts[1].co) / 2); bordas[r] = bordas.get(r, 0) + 1
    inv = sum(1 for e in bm.edges if len(e.link_faces) == 2 and not e.is_contiguous)
    buf = io.StringIO()
    tmp = me.copy()
    with contextlib.redirect_stdout(buf): mudou = tmp.validate(verbose=True)
    bpy.data.meshes.remove(tmp)
    rel["malhas"][o.name] = {"tris": sum(len(f.verts) - 2 for f in bm.faces), "faces_degeneradas": deg, "vertices_duplicados": dup,
                             "vertices_soltos": soltos, "arestas_nao_manifold": len(nm), "bordas_abertas": bordas,
                             "arestas_enrolamento_invertido": inv, "validate_corrigiria": bool(mudou),
                             "materiais": [m.name for m in me.materials if m], "uv": len(me.uv_layers)}
    bm.free()
# costura cabeca-corpo
def borda_costura(nome):
    o = bpy.data.objects.get(nome)
    if not o: return []
    bm = bmesh.new(); bm.from_mesh(o.data)
    pts = [v.co.copy() for v in bm.verts if v.is_boundary and abs((v.co - COST_P).dot(COST_N)) < 0.03]; bm.free(); return pts
ca, co_ = borda_costura("LOW_Cabeca"), borda_costura("LOW_Corpo")
if ca and co_:
    kd = KDTree(len(co_))
    for i, p in enumerate(co_): kd.insert(p, i)
    kd.balance(); ds = [kd.find(p)[2] for p in ca]
    rel["costura"] = {"vertices_cabeca": len(ca), "vertices_corpo": len(co_), "dist_max": max(ds), "dist_media": sum(ds) / len(ds)}
# medidas
corpo = bpy.data.objects["LOW_Corpo"]; cab = bpy.data.objects["LOW_Cabeca"]; cr = bpy.data.objects.get("LOW_Cristais")
vc = [v.co for v in corpo.data.vertices]; vh = [v.co for v in cab.data.vertices]
ys = [p.y for p in vc]; L = max(ys) - min(ys)
cern = max((p.z for p in vc if -3.3 < p.y < -2.3 and abs(p.x - 0.12) < 0.35), default=None)
ombro = max((p.z for p in vc if -3.6 < p.y < -3.0 and abs(p.x - 0.12) > 0.5), default=None)
pes = [p for p in vc if p.z < 0.35]
cx_ = sum(p.x for p in pes) / len(pes); cy_ = sorted(p.y for p in pes)[len(pes) // 2]
patas = {}
for nome, f in (("dianteira_esq", lambda p: p.x > cx_ and p.y < cy_), ("dianteira_dir", lambda p: p.x <= cx_ and p.y < cy_),
                ("traseira_esq", lambda p: p.x > cx_ and p.y >= cy_), ("traseira_dir", lambda p: p.x <= cx_ and p.y >= cy_)):
    q = [p for p in pes if f(p)]
    if q: patas[nome] = {"apoio_z_min": round(min(p.z for p in q), 3), "centro_y": round(sum(p.y for p in q) / len(q), 3), "centro_x": round(sum(p.x for p in q) / len(q), 3)}
rel["medidas"] = {"topo_do_pelo_na_cernelha": cern, "topo_do_pelo_no_ombro_lateral": ombro,
                  "topo_cristais": max((v.co.z for v in cr.data.vertices), default=None) if cr else None,
                  "topo_orelhas": max(p.z for p in vh), "comprimento_corpo_mais_cauda": L, "patas": patas,
                  "pata_dianteira_adiantada_y": (patas["dianteira_esq"]["centro_y"] - patas["dianteira_dir"]["centro_y"]) if len(patas) == 4 else None}
json.dump(rel, open(os.path.join(OUT, "auditoria.json"), "w"), indent=1, default=float)
print("AUDIT", json.dumps(rel, default=float))
