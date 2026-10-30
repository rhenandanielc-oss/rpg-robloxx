"""Junta os PNG de quadros/ em MP4 H.264 (30 fps) pelo editor de video do Blender.
Uso: blender -b --factory-startup -P video_mp4.py -- <pasta_quadros> <saida.mp4>"""
import bpy, sys, os, glob
args = sys.argv[sys.argv.index("--") + 1:]; pasta, saida = os.path.abspath(args[0]), os.path.abspath(args[1])
fs = sorted(glob.glob(os.path.join(pasta, "f_*.png")))
sc = bpy.context.scene; sc.render.fps = 30
sc.sequence_editor_create()
seqs = sc.sequence_editor.strips if hasattr(sc.sequence_editor, "strips") else sc.sequence_editor.sequences
st = seqs.new_image("q", fs[0], 1, 1)
for f in fs[1:]: st.elements.append(os.path.basename(f))
sc.frame_start, sc.frame_end = 1, len(fs)
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.view_settings.view_transform = "Standard"                      # os PNG ja vem com AgX aplicado
if hasattr(sc.render.image_settings, "media_type"): sc.render.image_settings.media_type = "VIDEO"
sc.render.image_settings.file_format = "FFMPEG"
sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"; sc.render.ffmpeg.constant_rate_factor = "HIGH"
sc.render.ffmpeg.ffmpeg_preset = "GOOD"
sc.render.filepath = saida
bpy.ops.render.render(animation=True)
print("MP4_OK", len(fs), saida)
