"""Contatos com o chao (so leitura): para cada Clipe:quadro mede, na malha deformada, o ponto mais baixo de cada regiao -
pelve, esterno, cotovelo E/D, pata dianteira E/D, pata traseira E/D, jarrete E/D, queixo e cauda - e marca no chao um
disco (verde = apoiado, z < 0,12; laranja = perto, < 0,4; sem disco = no ar). Render lateral, 3/4 e de cima + JSON.
Uso: blender -b <Anim.blend> -P contatos_chao.py -- <saida_dir> <prefixo> Clipe:quadro[,...]"""
import bpy, sys, os, json
import numpy as np
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); PRE = A[1]; LISTA = A[2].split(","); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
gi = {g.index: g.name for g in LO.vertex_groups}
def dono(v): return gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else ""
pelo = np.array([sum(g.weight for g in v.groups if gi[g.group].startswith("Pelo")) for v in LO.data.vertices])
D = np.array([dono(v) for v in LO.data.vertices])
def grupo(nomes, sem_pelo=True): return np.nonzero(np.isin(D, nomes) & ((pelo < 0.05) if sem_pelo else True))[0]
REG = {"pelve": grupo(["Pelve", "Coluna1"]), "esterno": grupo(["Peito", "Coluna2"]),
       "cotovelo_E": grupo(["BracoE"]), "cotovelo_D": grupo(["BracoD"]),
       "pata_dian_E": grupo(["MaoE", "DedosE"]), "pata_dian_D": grupo(["MaoD", "DedosD"]),
       "jarrete_E": grupo(["MetatarsoE"]), "jarrete_D": grupo(["MetatarsoD"]),
       "pata_tras_E": grupo(["PeE"]), "pata_tras_D": grupo(["PeD"]),
       "queixo": grupo(["Cabeca", "Mandibula"], False), "cauda": grupo(["Cauda%d" % i for i in range(1, 8)], False)}
COR = {"apoio": (0.1, 0.95, 0.2, 1), "perto": (1.0, 0.55, 0.05, 1)}
mats = {}
for k, c in COR.items():
    m = bpy.data.materials.new("contato_" + k); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = c; e.inputs["Strength"].default_value = 2.0
    o_ = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs["Emission"], o_.inputs["Surface"]); mats[k] = m
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12; sc.render.resolution_x, sc.render.resolution_y = 760, 520
cam = sc.camera; cam.data.type = "PERSP"; cam.data.lens = 40
res = {}
for item in LISTA:
    nome, q = item.split(":"); act = bpy.data.actions["Lobo_" + nome]
    arm.animation_data_create(); arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    sc.frame_set(int(act.frame_range[0]) + int(q)); bpy.context.view_layer.update()
    ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh(); co = np.array([v.co[:] for v in m.vertices]); ev.to_mesh_clear()
    r = {}; discos = []
    for k, idx in REG.items():
        if len(idx) == 0: continue
        j = idx[np.argmin(co[idx, 2])]; p = co[j]; r[k] = [round(float(p[0]), 2), round(float(p[1]), 2), round(float(p[2]), 3)]
        est = "apoio" if p[2] < 0.12 else ("perto" if p[2] < 0.4 else None)
        if est:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.02, location=(p[0], p[1], 0.012)); d = bpy.context.active_object
            d.data.materials.append(mats[est]); discos.append(d)
    res[item] = r
    print("CONTATOS", item, " ".join("%s:%.2f" % (k, v[2]) for k, v in r.items()))
    zmin = float(co[:, 2].min()); print("   malha z minimo %.3f" % zmin)
    alvo = V((0, -1.8, 1.2))
    for vn, pos in (("lateral", V((22, -1.8, 3.0))), ("tres_quartos", V((14, -15, 9))), ("cima", V((0.01, -1.8, 24)))):
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_%s_%s_%s.png" % (PRE, nome, q, vn)); bpy.ops.render.render(write_still=True)
    for d in discos: bpy.data.objects.remove(d)
json.dump(res, open(os.path.join(OUT, PRE + "_contatos.json"), "w"), indent=1)
