import bpy
for o in bpy.data.objects:
    if o.type == "ARMATURE" and o.animation_data:
        o.animation_data.action = None
        for t in o.animation_data.nla_tracks: t.mute = True
        for pb in o.pose.bones:
            pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_mainfile()
print("OK", bpy.data.filepath)
