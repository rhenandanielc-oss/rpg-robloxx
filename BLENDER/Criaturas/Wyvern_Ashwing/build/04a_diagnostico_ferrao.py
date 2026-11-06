# M0 (somente leitura) - diagnostico da transicao cauda-bulbo-ferrao.
# Uso: blender -b Wyvern_E3.blend -P 04a_diagnostico_ferrao.py -- <saida.json>
# Mede por anel de vertices (y) o perfil, as normais/diedros, pesos, shape keys e estiramento de UV
# na regiao da ponta da cauda, e as metricas gerais (triangulos, ossos, materiais, dimensoes).
import bpy, sys, json, math, bmesh
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
mesh = bpy.data.objects["Wyvern"]; arm = bpy.data.objects["Wyvern_Rig"]; me = mesh.data
y_max = max(v.co.y for v in me.vertices)
Y0 = 23.91   # inicio da remodelagem do 02_ferrao.py (registrado no LEIA-ME)
REG = Y0 - 3.0
gn = {g.index: g.name for g in mesh.vertex_groups}
res = {"y_max": y_max, "Y0": Y0}
# metricas gerais
me.calc_loop_triangles()
res["tris"] = len(me.loop_triangles); res["verts"] = len(me.vertices)
res["ossos"] = len(arm.data.bones); res["materiais"] = [m.name for m in me.materials]
res["shape_keys"] = [k.name for k in me.shape_keys.key_blocks] if me.shape_keys else []
ws = [mesh.matrix_world @ v.co for v in me.vertices]
res["dim"] = [round(max(w[i] for w in ws) - min(w[i] for w in ws), 3) for i in range(3)]
# vertices da regiao ordenados por y
ids = [v.index for v in me.vertices if v.co.y >= REG]
res["n_regiao"] = len(ids)
# aneis: agrupa por y arredondado (malha original tem loops ~ perpendiculares a y)
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
# diedros fortes (arestas vivas) na regiao
viv = []
for e in bm.edges:
    if len(e.link_faces) == 2 and all(v.co.y >= REG for v in e.verts):
        a = math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal, 0))
        if a > 35: viv.append((round((e.verts[0].co.y + e.verts[1].co.y) / 2, 2), round(a, 1)))
viv.sort()
res["arestas_vivas_>35"] = viv
# perfil por fatia de 0,25 (como o 02_ferrao.py usava) + contagem de vertices por fatia
fat = {}
for i in ids:
    v = me.vertices[i]; k = round((v.co.y - Y0) // 0.25 * 0.25 + Y0, 2)
    f = fat.setdefault(k, {"n": 0, "x": [1e9, -1e9], "z": [1e9, -1e9]})
    f["n"] += 1; f["x"] = [min(f["x"][0], v.co.x), max(f["x"][1], v.co.x)]; f["z"] = [min(f["z"][0], v.co.z), max(f["z"][1], v.co.z)]
res["fatias"] = {str(k): {"n": f["n"], "larg": round(f["x"][1] - f["x"][0], 3), "alt": round(f["z"][1] - f["z"][0], 3), "zc": round((f["z"][0] + f["z"][1]) / 2, 3)} for k, f in sorted(fat.items())}
# faces nao planas / pequenas / normais invertidas (normal apontando para o eixo central)
inv = 0; degen = 0
for f in bm.faces:
    if all(v.co.y >= REG for v in f.verts):
        if f.calc_area() < 1e-5: degen += 1
c_eixo = {}
res["faces_degeneradas"] = degen
# pesos: por vertice dominante e numero de influencias, perto da juncao
pes = []
for i in ids:
    v = me.vertices[i]
    gs = sorted(((gn[g.group], round(g.weight, 3)) for g in v.groups if g.weight > 0.001), key=lambda t: -t[1])
    pes.append((round(v.co.y, 2), gs[:3]))
pes.sort()
res["pesos_amostra"] = pes[::6]
# troca abrupta de peso: vizinhos (aresta) com grande diferenca de peso em tail_10
g10 = mesh.vertex_groups["tail_10"].index
def w10(v):
    for g in me.vertices[v].groups:
        if g.group == g10: return g.weight
    return 0.0
salto = []
for e in bm.edges:
    a, b = e.verts
    if a.co.y >= REG and b.co.y >= REG:
        d = abs(w10(a.index) - w10(b.index))
        if d > 0.3: salto.append((round((a.co.y + b.co.y) / 2, 2), round(d, 2)))
salto.sort(); res["saltos_peso_tail10_>0.3"] = salto
# ossos da cauda: cabeca/cauda em repouso
res["ossos_cauda"] = {b.name: [round(b.head_local.y, 2), round(b.tail_local.y, 2)] for b in arm.data.bones if b.name.startswith("tail")}
# shape keys: deslocamento maximo na regiao
if me.shape_keys:
    base = me.shape_keys.reference_key
    res["sk_desloc_regiao"] = {k.name: round(max((k.data[i].co - base.data[i].co).length for i in ids), 4) for k in me.shape_keys.key_blocks}
# estiramento UV: razao area3D/areaUV por face da regiao (normalizada pela mediana do corpo da cauda)
uvl = me.uv_layers.active.data
def razao(t):
    p = [me.vertices[v].co for v in t.vertices]; q = [Vector((*uvl[l].uv, 0)) for l in t.loops]
    a3 = (p[1] - p[0]).cross(p[2] - p[0]).length; au = (q[1] - q[0]).cross(q[2] - q[0]).length
    return a3 / max(au, 1e-12)
rz = []
for t in me.loop_triangles:
    ym = sum(me.vertices[v].co.y for v in t.vertices) / 3
    if ym >= REG: rz.append((round(ym, 2), razao(t)))
ref = sorted(r for y, r in rz if y < Y0)[len([1 for y, r in rz if y < Y0]) // 2]
res["uv_estiramento_por_fatia"] = {}
for y, r in rz:
    k = str(round((y - Y0) // 0.5 * 0.5 + Y0, 1))
    res["uv_estiramento_por_fatia"].setdefault(k, []).append(r / ref)
res["uv_estiramento_por_fatia"] = {k: [round(min(v), 2), round(sorted(v)[len(v) // 2], 2), round(max(v), 2)] for k, v in sorted(res["uv_estiramento_por_fatia"].items(), key=lambda kv: float(kv[0]))}
json.dump(res, open(OUT, "w"), indent=1)
print("OK", OUT)
