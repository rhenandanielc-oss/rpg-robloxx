"""Monta MP4 (H.264) dos quadros do rig piloto v9 com o sequenciador do Blender: velocidade normal (30 qps) e lenta
(15 qps = 0,5x). Uso: blender -b --factory-startup -P video_rig_v9.py -- <dir_quadros (v_NNNN.png)> <saida_sem_extensao> [L A]"""
import bpy, sys, os, glob
a = sys.argv[sys.argv.index("--") + 1:]; DQ, SAI = os.path.abspath(a[0]), os.path.abspath(a[1])
RX, RY = (int(a[2]), int(a[3])) if len(a) > 3 else (640, 480)
fs = sorted(glob.glob(os.path.join(DQ, "v_*.png")))
for qps, suf in ((30, "_normal_30qps"), (15, "_lento_0.5x")):
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; se = sc.sequence_editor_create()
    col = se.strips if hasattr(se, "strips") else se.sequences
    st = col.new_image("q", fs[0], 1, 1)
    for f in fs[1:]: st.elements.append(os.path.basename(f))
    sc.frame_start, sc.frame_end = 1, len(fs); sc.render.fps = qps; sc.render.resolution_x, sc.render.resolution_y = RX, RY
    sc.render.resolution_percentage = 100
    if hasattr(sc.render.image_settings, "media_type"): sc.render.image_settings.media_type = "VIDEO"   # Blender 5.x
    sc.render.image_settings.file_format = "FFMPEG"; sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"; sc.render.filepath = SAI + suf + ".mp4"; sc.render.use_file_extension = False
    bpy.ops.render.render(animation=True); print("VIDEO_OK", sc.render.filepath, len(fs), qps, flush=True)
