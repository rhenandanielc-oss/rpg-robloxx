"""Decodifica um MP4 em PNGs (todos os quadros ou a cada N) usando o sequenciador do Blender (sem ffmpeg/opencv).
So leitura do video. Uso: blender -b --factory-startup -P quadros_mp4.py -- <video.mp4> <saida_dir> [passo]"""
import bpy, sys, os
A = sys.argv[sys.argv.index("--") + 1:]; VID = os.path.abspath(A[0]); OUT = os.path.abspath(A[1]); PASSO = int(A[2]) if len(A) > 2 else 1
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; sc.sequence_editor_create()
st = sc.sequence_editor.strips.new_movie("v", VID, 1, 1)
sc.render.resolution_x, sc.render.resolution_y = st.elements[0].orig_width, st.elements[0].orig_height
sc.render.resolution_percentage = 100; sc.frame_start = 1; sc.frame_end = st.frame_final_duration; sc.frame_step = PASSO
sc.render.image_settings.file_format = "PNG"; sc.render.filepath = os.path.join(OUT, "q_####")
sc.render.use_sequencer = True; sc.view_settings.view_transform = "Standard"
bpy.ops.render.render(animation=True); print("QUADROS", st.frame_final_duration, "passo", PASSO)
