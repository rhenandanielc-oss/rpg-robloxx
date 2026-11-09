"""S1 r3: afasta as argolas da cilha (ferro + ambar perto de y da cilha, nos dois lados, no alto da manta) 0,05 na direcao
radial da cilha (residuo de 0,01 numa argola em Observar_Farejar q33). So a malha da sela.
Uso: blender -b <sela.blend> -P s1_05_argolas.py -- <saida.blend>"""
import bpy, sys, os
import numpy as np
from mathutils import Vector as V
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s1_01_sela_leao as sl
A = sys.argv[sys.argv.index("--") + 1:]
sela = bpy.data.objects[sl.NOME]; me = sela.data; PL = list(sela["pecas"]); vp = [PL[d.value] for d in me.attributes["peca"].data]
c0 = V((sl.XC, sl.CILHA["y"], 8.0)); n = 0
for v, p in zip(me.vertices, vp):
    if p in ("ferro", "ambar") and abs(v.co.y - sl.CILHA["y"]) < 0.45 and v.co.z > 10.0:
        d = v.co - c0; d.y = 0; v.co += d.normalized() * 0.05; n += 1
me.update(); print("ARGOLAS vertices movidos", n)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[0]))
