"""extrai quadros de MP4 pelo editor de video do Blender (sem ffmpeg no sistema).
Uso: blender -b --factory-startup -P r2_quadros.py -- <saida_dir> <video.mp4>:<quadro>[,<quadro>] ..."""
import bpy, sys, os
A = sys.argv[sys.argv.index("--") + 1:]; OUT = A[0]
sc = bpy.context.scene; sc.sequence_editor_create()
for arg in A[1:]:
    cam, qs = arg.rsplit(":", 1)
    for s in list(sc.sequence_editor.strips): sc.sequence_editor.strips.remove(s)
    st = sc.sequence_editor.strips.new_movie("v", cam, channel=1, frame_start=1)
    sc.render.resolution_x, sc.render.resolution_y = st.elements[0].orig_width, st.elements[0].orig_height; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    for q in qs.split(","):
        sc.frame_set(int(q)); sc.render.filepath = os.path.join(OUT, "_q_%s_%s.png" % (os.path.basename(cam)[7:-4], q)); bpy.ops.render.render(write_still=True)
print("QUADROS_OK")
