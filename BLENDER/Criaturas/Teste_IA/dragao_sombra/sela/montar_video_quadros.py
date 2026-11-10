"""Junta quadros (jpg/png, na ordem de uma lista) num MP4 com o codificador do Blender (sem ffmpeg no sistema).
Usado para os videos da montaria capturados no Studio (07/11). Cada quadro repete REPETE vezes (10 fps capturados ->
30 fps no arquivo com REPETE 3 = tempo real).
Uso: blender -b -P sela/montar_video_quadros.py -- <lista.txt> <saida.mp4> [fps_saida] [repete]"""
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]
LISTA, SAIDA = a[0], os.path.abspath(a[1]); FPS = int(a[2]) if len(a) > 2 else 30; REPETE = int(a[3]) if len(a) > 3 else 3
quadros = [l.strip() for l in open(LISTA, encoding="utf-8") if l.strip()]
sc = bpy.context.scene
im = bpy.data.images.load(quadros[0]); w, h = im.size
sc.render.resolution_x, sc.render.resolution_y = w - w % 2, h - h % 2; sc.render.resolution_percentage = 100
sc.render.fps = FPS
se = sc.sequence_editor_create(); col = se.strips if hasattr(se, "strips") else se.sequences
for i, q in enumerate(quadros):
    s = col.new_image(name="q%03d" % i, filepath=q, channel=1, frame_start=1 + i * REPETE)
    s.frame_final_duration = REPETE
sc.frame_start, sc.frame_end = 1, len(quadros) * REPETE
try: sc.render.image_settings.media_type = "VIDEO"            # Blender 5.x: video separado das imagens
except Exception: pass
sc.render.image_settings.file_format = "FFMPEG"
sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"; sc.render.ffmpeg.constant_rate_factor = "HIGH"
sc.render.use_sequencer = True; sc.render.filepath = SAIDA
bpy.ops.render.render(animation=True)
print("VIDEO_OK", SAIDA, len(quadros), "quadros", round(len(quadros) * REPETE / FPS, 1), "s")
