"""Revisao da queda lateral: renderiza acoes em quadros-chave e vistas frente / lado / tres quartos / cima (Workbench) e
mede, por quadro, a malha abaixo do chao (onde) e as patas. Uso:
blender -b rig18/Lobo_Ancestral_Anim_Queda.blend -P habilidades/render_queda.py -- <saida> <acao:t1,t2,...> [<acao:...>]"""
import bpy, sys, os, math, json
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
gi = {g.index: g.name for g in LO.vertex_groups}
def grupo(v): return gi[max(v.groups, key=lambda g: g.weight).group] if v.groups else "-"
sc.render.engine = "BLENDER_WORKBENCH"; sc.render.resolution_x, sc.render.resolution_y = 520, 380
sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
cam = bpy.data.objects.new("CamQ", bpy.data.cameras.new("CamQ")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 38
alvo = V((-1.6, -2.0, 1.2))
VIS = {"frente": V((0, -16, 4)), "lado": V((-16, -1, 3.5)), "tres_quartos": V((-11, -12, 7)), "cima": V((0.2, 0.3, 17))}
rel = {}
for item in A[1:]:
    nome, ts = item.split(":"); ts = [float(x) for x in ts.split(",")]
    arm.animation_data.action = bpy.data.actions["Lobo_" + nome]
    nq = int(arm.animation_data.action.frame_range[1])
    piores = []
    for f in range(1, nq + 1, 2):
        sc.frame_set(f); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
        zmin, g = 9, "-"
        for v in ev.vertices:
            if v.co.z < zmin: zmin, g = v.co.z, grupo(LO.data.vertices[v.index])
        piores.append((round((f - 1) / FPS, 2), round(zmin, 3), g))
    rel[nome] = {"pior": min(piores, key=lambda x: x[1]), "amostras": piores[::4]}
    for vis, pos in VIS.items():
        cam.location = alvo + pos; cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
        for t in ts:
            sc.frame_set(int(round(t * FPS)) + 1)
            sc.render.filepath = os.path.join(OUT, "%s_%s_%04d.png" % (nome, vis, int(t * 1000))); bpy.ops.render.render(write_still=True)
json.dump(rel, open(os.path.join(OUT, "malha_chao.json"), "w"), indent=1)
for k, v in rel.items(): print("MALHA", k, "pior", v["pior"])
print("RENDER_OK")
