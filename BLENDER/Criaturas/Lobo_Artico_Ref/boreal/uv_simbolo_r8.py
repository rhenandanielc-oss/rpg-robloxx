"""r8l: mede, na LOW_Corpo em REPOUSO, o mapeamento local (y, z) do perfil -> UV no ponto do simbolo da perna (cada lado),
para desenhar a espiral DIRETO na mascara (redonda e nitida; o bake deformava na perna estreita e curva).
r8l: o ponto foi escolhido por varredura sem costura de UV (anel de raio 0,42 sem salto > 4 px) em y -3,06, z 2,62.
Saida: boreal/export/uv_simbolo_r8.json {lado: {uv0, J, erro_anel, espiral_uv: [[u, v], ...]}}
Uso: blender -b boreal/CR_LoboArtico_Boreal_r8.blend -P boreal/uv_simbolo_r8.py -- <cy> <cz> <raio>"""
import bpy, bmesh, os, json, sys
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
a = sys.argv[sys.argv.index("--") + 1:]; CY, CZ, R = (float(x) for x in a[:3])
AQUI = os.path.dirname(os.path.abspath(__file__))
rig = bpy.data.objects["LoboArtico_Rig"]; rig.animation_data.action = None
for pb in rig.pose.bones: pb.matrix_basis.identity()
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
o = bpy.data.objects["LOW_Corpo"]; dg = bpy.context.evaluated_depsgraph_get(); me = o.evaluated_get(dg).to_mesh()
bm = bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.faces.ensure_lookup_table(); uvl = bm.loops.layers.uv.active
T = BVHTree.FromBMesh(bm)
def uv_em(y, z, lado):
    hit, nrm, idx, d = T.ray_cast(V((lado * 4.0, y, z)), V((-lado, 0, 0)), 8.0)
    if hit is None: return None, None
    f = bm.faces[idx]; vs = [l.vert.co for l in f.loops]; us = [l[uvl].uv.to_3d() for l in f.loops]
    u = barycentric_transform(hit, vs[0], vs[1], vs[2], us[0], us[1], us[2]); return (u.x, u.y), hit
res = {}
for lado, nome in ((1, "E"), (-1, "D")):
    (u0, p0) = uv_em(CY, CZ, lado); h = 0.08
    uy1, _ = uv_em(CY + h, CZ, lado); uy0, _ = uv_em(CY - h, CZ, lado); uz1, _ = uv_em(CY, CZ + h, lado); uz0, _ = uv_em(CY, CZ - h, lado)
    J = [[(uy1[0] - uy0[0]) / (2 * h), (uz1[0] - uz0[0]) / (2 * h)], [(uy1[1] - uy0[1]) / (2 * h), (uz1[1] - uz0[1]) / (2 * h)]]
    err = 0.0
    import math
    for k in range(12):
        ang = 2 * math.pi * k / 12; dy, dz = R * math.cos(ang), R * math.sin(ang); ur, _ = uv_em(CY + dy, CZ + dz, lado)
        if ur is None: err = max(err, 9.0); continue
        pu = (u0[0] + J[0][0] * dy + J[0][1] * dz, u0[1] + J[1][0] * dy + J[1][1] * dz)
        err = max(err, math.hypot(ur[0] - pu[0], ur[1] - pu[1]) * 1024)
    esp = []
    VOLTAS, R1 = 1.5, 0.07; n = 260
    for k in range(n + 1):
        t = k / n; ang = VOLTAS * 2 * math.pi * t; r = R + (R1 - R) * t
        ur, _ = uv_em(CY + r * math.cos(ang), CZ + r * math.sin(ang), lado)
        if ur is not None: esp.append([round(ur[0], 6), round(ur[1], 6)])
    res[nome] = {"uv0": u0, "J": J, "erro_anel_px": round(err, 2), "ponto": list(p0), "lado": lado, "espiral_uv": esp}
    print("UVSIM", nome, res[nome]["erro_anel_px"], len(res[nome]["espiral_uv"]))
json.dump({"centro_yz": [CY, CZ], "raio": R, "lados": res}, open(os.path.join(AQUI, "export", "uv_simbolo_r8.json"), "w"), indent=1)
