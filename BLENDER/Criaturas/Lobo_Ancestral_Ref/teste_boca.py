"""Teste visual da boca: abre a mandibula provisoriamente (rotacao em X na dobradica atras do canto, por regiao) e
renderiza closes. NAO salva. Uso: blender -b low/l03/Lobo_Ancestral_LOW_rig.blend -P teste_boca.py -- <saida> <graus>"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); ANG = math.radians(float(A[1]))
M = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "marcos_rig.json")))
ob = bpy.data.objects["Lobo_Ancestral_LOW"]; me = ob.data
import numpy as np
YC = M["y_canto"]
def zb(y): return float(np.interp(y, M["curva_y"], M["curva_z"]))
DOB = V((0, YC + 0.45, zb(YC) + 0.05))
R = Matrix.Translation(DOB) @ Matrix.Rotation(ANG, 4, "X") @ Matrix.Translation(-DOB)
def suave(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
MAND = set()
if "mandibula" in me.attributes:
    ma = me.attributes["mandibula"].data
    for p_ in me.polygons:
        if ma[p_.index].value: MAND.update(p_.vertices)
for v in me.vertices:
    p = v.co
    if v.index in MAND: w = 1.0
    elif p.y > YC - 0.05 and p.y < YC + 0.9 and abs(p.x) < 1.3 and zb(YC) - 1.2 < p.z < zb(YC) + 0.02: w = 1 - suave((p.y - YC) / 0.9)
    else: continue
    v.co = p.lerp(R @ p, w)
me.update()
os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene; cam = sc.camera; camd = cam.data
sc.render.resolution_x, sc.render.resolution_y = 900, 700
nar = V(M["nariz"]); alvo = nar + V((0, 0.8, -0.2))
for nome, pos in (("lado", alvo + V((5, 0, 0.2))), ("frente34", alvo + V((2.6, -3.6, 0.4))), ("frente", alvo + V((0, -4.5, 0.5)))):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = 70
    sc.render.filepath = os.path.join(OUT, "boca_%s.png" % nome); bpy.ops.render.render(write_still=True)
