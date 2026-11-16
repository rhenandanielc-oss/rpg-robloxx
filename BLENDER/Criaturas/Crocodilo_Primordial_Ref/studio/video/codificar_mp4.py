"""Blender (headless): sequencia q*.jpg -> MP4 H.264 30 qps, sem audio (largura/altura pares).
Uso: blender -b --factory-startup --python codificar_mp4.py -- PASTA_QUADROS SAIDA.mp4"""
import bpy, sys, os, glob
a = sys.argv[sys.argv.index("--") + 1:]; pasta, saida = a
fs = sorted(glob.glob(os.path.join(pasta, "q*.jpg")))
sc = bpy.context.scene
im = bpy.data.images.load(fs[0]); w, h = im.size
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w - (w % 2), h - (h % 2), 100
sc.render.fps, sc.render.fps_base = 30, 1.0
sc.frame_start, sc.frame_end = 1, len(fs)
ed = sc.sequence_editor_create()
strips = ed.strips if hasattr(ed, "strips") else ed.sequences
img = strips.new_image("quadros", fs[0], channel=1, frame_start=1)
for f in fs[1:]: img.elements.append(os.path.basename(f))
r = sc.render
if hasattr(r.image_settings, "media_type"): r.image_settings.media_type = "VIDEO"
r.image_settings.file_format = "FFMPEG"
r.ffmpeg.format = "MPEG4"; r.ffmpeg.codec = "H264"; r.ffmpeg.constant_rate_factor = "HIGH"; r.ffmpeg.ffmpeg_preset = "GOOD"; r.ffmpeg.gopsize = 30
r.ffmpeg.audio_codec = "NONE"
sc.render.use_sequencer = True; sc.render.use_compositing = False
sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
sc.render.filepath = saida
print("quadros", len(fs), w, h, "->", saida)
bpy.ops.render.render(animation=True)
print("MP4_OK")
