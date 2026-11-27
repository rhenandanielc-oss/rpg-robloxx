"""Montaria M0 (27/11/2026): mede o dorso do Cerbero Sombrio (so leitura) em pe (repouso) e deitado (ultimo quadro do
Deitar): topo da pele no meio e nas laterais, barriga, largura abaixo do topo, juba, raizes dos pescocos, ombros/quadril.
Frente = -y (cabecas). Uso:
blender -b -t 1 rig/clipes_L3r7/CR_Cerbero_Anim.blend -P montaria/m0_medir_dorso.py -- <saida.json>"""
import bpy, sys, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
malhas = [o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers)]
print("ARM", arm.name, "MALHAS", [o.name for o in malhas], "ACOES", [a.name for a in bpy.data.actions][:80], flush=True)
OSSOS = ["Raiz", "Pelve", "Coluna1", "Coluna2", "Coluna3", "PescocoC1", "PescocoE1", "PescocoD1", "EscapulaE", "EscapulaD",
         "BracoE", "BracoD", "CoxaE", "CoxaD", "CabecaC"]

def bvh_atual():
    dg = bpy.context.evaluated_depsgraph_get(); vs = []; fs = []
    for o in malhas:
        m = o.evaluated_get(dg).to_mesh(); W = o.matrix_world; b = len(vs)
        vs += [W @ v.co for v in m.vertices]; fs += [tuple(b + i for i in p.vertices) for p in m.polygons]
        o.evaluated_get(dg).to_mesh_clear()
    return BVHTree.FromPolygons(vs, fs), np.array([tuple(v) for v in vs])

def medir(rotulo):
    bpy.context.view_layer.update()
    bvh, P = bvh_atual()
    mn, mx = P.min(0), P.max(0)
    out = {"bbox_min": mn.round(2).tolist(), "bbox_max": mx.round(2).tolist(), "perfil": [],
           "ossos": {n: [round(c, 2) for c in (arm.matrix_world @ arm.pose.bones[n].head)] for n in OSSOS if n in arm.pose.bones}}
    lx = max(abs(mn[0]), abs(mx[0]))
    for y in np.arange(round(mn[1]), mx[1] + 0.01, 1.0):
        row = {"y": round(float(y), 2)}
        for x in (-0.6, -0.3, 0.0, 0.3, 0.6):
            xx = x * lx; h = bvh.ray_cast(V((xx, y, mx[2] + 5)), V((0, 0, -1)))
            row["topo_x%+.1f" % xx] = round(h[0].z, 2) if h[0] else None
        b = bvh.ray_cast(V((0, y, -5)), V((0, 0, 1))); row["barriga"] = round(b[0].z, 2) if b[0] else None
        if row["topo_x+0.0"]:
            for dz in (1.0, 2.5, 5.0):
                zz = row["topo_x+0.0"] - dz; r = bvh.ray_cast(V((lx + 10, y, zz)), V((-1, 0, 0))); l = bvh.ray_cast(V((-lx - 10, y, zz)), V((1, 0, 0)))
                row["lados_%.1fabaixo" % dz] = [round(r[0].x, 2) if r[0] else None, round(l[0].x, 2) if l[0] else None]
        out["perfil"].append(row)
    print("MEDIDO", rotulo, out["bbox_min"], out["bbox_max"], flush=True)
    return out

res = {}
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
res["repouso_rest"] = medir("rest")
ac = next((a for a in bpy.data.actions if a.name.endswith("Deitar")), None)
if ac:
    arm.animation_data_create(); arm.animation_data.action = ac
    try:
        if ac.slots: arm.animation_data.action_slot = ac.slots[0]
    except Exception: pass
    f0, f1 = ac.frame_range; bpy.context.scene.frame_set(int(f1)); res["deitado_fim"] = medir("deitado"); res["deitar_acao"] = [ac.name, f0, f1]
json.dump(res, open(A[0], "w"), indent=1)
