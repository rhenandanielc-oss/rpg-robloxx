"""Encurta a franja escura de pelo da barriga/peito que pende entre as patas dianteiras (vista frontal: parecia "um osso
fora do lugar"). Vertices fora das patas, perto da linha central, abaixo de Z_TOPO e entre o peito e a barriga sobem em
direcao a Z_TOPO (fator FATOR), com transicao macia. So posicao de vertice. Simetria mantida (campo so depende de |x|).
Uso: blender -b rig7/Lobo_Ancestral_Rig.blend -P encurtar_franja.py -- <saida_dir>"""
import bpy, sys, os, json
import numpy as np
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
Z_TOPO, FATOR = 3.55, 0.35
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
gi = {g.index: g.name for g in LO.vertex_groups}
perna = np.array([sum(g.weight for g in v.groups if gi[g.group].startswith(("Braco", "Antebraco", "Mao", "Dedos", "Coxa", "Canela", "Metatarso", "Pe"))) for v in me.vertices])
w = (1 - np.clip(perna * 1.5, 0, 1)) * suave((0.95 - np.abs(co[:, 0])) / 0.3) * suave((co[:, 1] + 4.9) / 0.5) * suave((-0.3 - co[:, 1]) / 0.6)
baixo = co[:, 2] < Z_TOPO
dz = np.where(baixo, (Z_TOPO - co[:, 2]) * (1 - FATOR), 0.0) * w
co[:, 2] += dz
me.vertices.foreach_set("co", co.ravel()); me.update()
rel = {"Z_TOPO": Z_TOPO, "FATOR": FATOR, "movidos": int((dz > 0.005).sum()), "dz_max": round(float(dz.max()), 3)}
print("FRANJA", rel)
json.dump(rel, open(os.path.join(OUT, "encurtar_franja.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("ENCURTAR_FRANJA_OK")
