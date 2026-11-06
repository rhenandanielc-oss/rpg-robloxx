# Inspecao (somente leitura) da ponta da cauda e da ocupacao da UV, para planejar o ferrao.
import bpy, json, bmesh
from mathutils import Vector
arm = bpy.data.objects["Wyvern_Rig"]; mesh = bpy.data.objects["Wyvern"]
arm.animation_data.action = None
for pb in arm.pose.bones: pb.matrix_basis.identity()
b = arm.data.bones
r = {"tail_09": [list(map(lambda x: round(x, 2), b["tail_09"].head_local)), list(map(lambda x: round(x, 2), b["tail_09"].tail_local))],
     "tail_10": [list(map(lambda x: round(x, 2), b["tail_10"].head_local)), list(map(lambda x: round(x, 2), b["tail_10"].tail_local))]}
me = mesh.data
y_max = max(v.co.y for v in me.vertices)
# perfil da cauda: largura/altura por fatia de y nos ultimos 8 studs
fat = {}
for v in me.vertices:
    if v.co.y > y_max - 8:
        k = round(v.co.y - (y_max - 8), 0)
        f = fat.setdefault(k, [1e9, -1e9, 1e9, -1e9, 0])
        f[0] = min(f[0], v.co.x); f[1] = max(f[1], v.co.x); f[2] = min(f[2], v.co.z); f[3] = max(f[3], v.co.z); f[4] += 1
r["y_max"] = round(y_max, 2)
r["fatias"] = {k: [round(f[1] - f[0], 2), round(f[3] - f[2], 2), round((f[2] + f[3]) / 2, 2), f[4]] for k, f in sorted(fat.items())}
# ocupacao da UV numa grade 32x32
bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.active
G = 32; occ = [[0] * G for _ in range(G)]
for f in bm.faces:
    for l in f.loops:
        u, v = l[uv].uv
        i = min(G - 1, max(0, int(u * G))); j = min(G - 1, max(0, int(v * G)))
        occ[j][i] = 1
r["uv_grade"] = ["".join("#" if c else "." for c in row) for row in reversed(occ)]
# UV da ponta (vertices alem de y_max-2.5)
us = []
for f in bm.faces:
    for l in f.loops:
        if l.vert.co.y > y_max - 2.5: us.append(tuple(l[uv].uv))
if us: r["uv_ponta"] = [round(min(u for u, v in us), 3), round(max(u for u, v in us), 3), round(min(v for u, v in us), 3), round(max(v for u, v in us), 3)]
r["materiais"] = [m.name for m in me.materials]
print("RJSON" + json.dumps(r) + "RFIM")
