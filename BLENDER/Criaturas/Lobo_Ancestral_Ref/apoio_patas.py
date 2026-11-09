"""Apoio VISIVEL das 4 patas num quadro (so leitura): malha deformada; por pata (vertices dos dedos/pe): z minimo, % da
sola (vertices ate 0,25 acima do ponto mais baixo) encostada (z < 0,06), inclinacao da sola (plano ajustado, graus do
horizontal) e altura da ponta dos dedos x calcanhar da almofada. Mais closes rentes ao chao (lateral e frontal) das patas.
Uso: blender -b <Anim.blend> -P apoio_patas.py -- <saida_dir> <prefixo> Clipe:quadro[,Clipe:quadro]"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); PRE = A[1]; LISTA = A[2].split(","); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
gi = {g.index: g.name for g in LO.vertex_groups}
dono = np.array([gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in LO.data.vertices])
PATAS = {"dianE": ("MaoE", "DedosE"), "dianD": ("MaoD", "DedosD"), "trasE": ("MetatarsoE", "PeE"), "trasD": ("MetatarsoD", "PeD")}
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.render.resolution_x, sc.render.resolution_y = 1000, 500
cam = sc.camera; cam.data.type = "PERSP"; cam.data.lens = 70
res = {}
for item in LISTA:
    nome, q = item.split(":"); act = bpy.data.actions["Lobo_" + nome]
    arm.animation_data_create(); arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    sc.frame_set(int(q)); bpy.context.view_layer.update()
    ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh(); co = np.array([v.co[:] for v in m.vertices]); ev.to_mesh_clear()
    r = {}
    for k, gs in PATAS.items():
        s = np.isin(dono, gs) & (co[:, 2] < 1.2)
        p = co[s]; zmin = float(p[:, 2].min()); sola = p[p[:, 2] < zmin + 0.25]
        enc = float((sola[:, 2] < 0.06).mean()) if len(sola) else 0.0
        A_ = np.c_[sola[:, 0], sola[:, 1], np.ones(len(sola))]; cf = np.linalg.lstsq(A_, sola[:, 2], rcond=None)[0]
        incl = math.degrees(math.atan(math.hypot(cf[0], cf[1])))
        frente = p[p[:, 1] < np.percentile(p[:, 1], 15)]; tras = p[p[:, 1] > np.percentile(p[:, 1], 85)]
        r[k] = {"z_min": round(zmin, 3), "sola_encostada_pct": round(100 * enc, 1), "inclinacao_sola_graus": round(incl, 1),
                "ponta_z_min": round(float(frente[:, 2].min()), 3), "fundo_z_min": round(float(tras[:, 2].min()), 3),
                "centro_xy": [round(float(p[:, 0].mean()), 3), round(float(p[:, 1].mean()), 3)]}
    res[item] = r; print("APOIO", item, json.dumps(r))
    alvo = V((0, -4.6, 0.5))
    for vn, pos in (("lado_chao", V((9, -4.6, 0.45))), ("frente_chao", V((0, -13, 0.6)))):
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_%s_%s_%s.png" % (PRE, nome, q, vn)); bpy.ops.render.render(write_still=True)
json.dump(res, open(os.path.join(OUT, PRE + "_apoio_patas.json"), "w"), indent=1)
