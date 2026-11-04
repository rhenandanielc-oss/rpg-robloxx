"""Posicoes de referencia (cabeca de osso no mundo) para conferir a conversao JSON -> Studio. Blender (x,y,z) -> Roblox (x, z, -y).
Uso: blender -b CR_Urso_v2_Anim.blend -P studio/ref_poses_blender.py"""
import bpy, json
arm = bpy.data.objects["Urso_Rig"]; sc = bpy.context.scene
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
OSS = ["Raiz", "Pelve", "Cabeca", "Mandibula", "MaoD", "MaoE", "PeD", "PeE", "DedosD", "OrelhaE"]
res = {}
for clip, q in (("Repouso", 0), ("Andar", 9), ("Rugir", 28)):
    arm.animation_data.action = bpy.data.actions["Urso_" + clip]; sc.frame_set(q + 1)
    d = {}
    for n in OSS:
        h = arm.matrix_world @ arm.pose.bones[n].head; d[n] = [round(h.x, 4), round(h.z, 4), round(-h.y, 4)]
    res["%s:%d" % (clip, q)] = d
# repouso sem animacao (rest)
d = {}
for n in OSS:
    h = arm.matrix_world @ arm.data.bones[n].head_local; d[n] = [round(h.x, 4), round(h.z, 4), round(-h.y, 4)]
res["REST"] = d
print("REFPOSES " + json.dumps(res))
