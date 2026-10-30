"""Renderiza o video_demo.blend. Uso: blender -b video_demo.blend -P video_render.py -- teste <saida_abs> 40,120 | final <saida_abs> [ini fim]"""
import bpy, sys, os
args = sys.argv[sys.argv.index("--") + 1:]; modo, out = args[0], os.path.abspath(args[1])
sc = bpy.context.scene
if modo == "teste":
    sc.render.resolution_x, sc.render.resolution_y = 960, 540; sc.eevee.taa_render_samples = 16
    for f in map(int, args[2].split(",")):
        sc.frame_set(f); sc.render.filepath = os.path.join(out, "teste_%04d.png" % f); bpy.ops.render.render(write_still=True)
else:
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    if len(args) > 3: sc.frame_start, sc.frame_end = int(args[2]), int(args[3])
    sc.render.image_settings.file_format = "PNG"; sc.render.use_overwrite = False; sc.render.use_placeholder = True
    os.makedirs(os.path.join(out, "quadros"), exist_ok=True)
    sc.render.filepath = os.path.join(out, "quadros", "f_"); bpy.ops.render.render(animation=True)
print("RENDER_OK")
