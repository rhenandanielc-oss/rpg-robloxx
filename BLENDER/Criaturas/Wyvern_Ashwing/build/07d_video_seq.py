# MP4 a partir de uma sequencia de PNGs (<prefixo>_000.png, _001.png...) pelo editor de video do Blender.
# Uso: blender -b -P 07d_video_seq.py -- <pasta> <prefixo[+prefixo2...]> <saida.mp4> [fps=30] [repeticoes=1]
#   varios prefixos com "+": os quadros de mesmo indice sao empilhados (o primeiro em cima) numa pasta _pilha
import bpy, sys, os, glob
import numpy as np
argv = sys.argv[sys.argv.index("--") + 1:]
D, PRE, MP4 = argv[0], argv[1], argv[2]
FPS = int(argv[3]) if len(argv) > 3 else 30; REP = int(argv[4]) if len(argv) > 4 else 1
pres = PRE.split("+")
fs = sorted(glob.glob(os.path.join(D, pres[0] + "_[0-9][0-9][0-9].png")))
if len(pres) > 1:
    pil = os.path.join(D, "_pilha_" + "_".join(pres)); os.makedirs(pil, exist_ok=True); novos = []
    for p0 in fs:
        idx = p0[-7:-4]; cam = []
        for pr in pres:
            im_ = bpy.data.images.load(os.path.join(D, pr + "_" + idx + ".png")); w_, h_ = im_.size
            cam.append(np.array(im_.pixels[:], dtype=np.float32).reshape(h_, w_, 4)); bpy.data.images.remove(im_)
        big = np.concatenate(cam[::-1], axis=0)                       # pixels de baixo para cima: o primeiro fica em cima
        o = bpy.data.images.new("P", big.shape[1], big.shape[0]); o.pixels = big.ravel()
        q = os.path.join(pil, "f_" + idx + ".png"); o.filepath_raw = q; o.file_format = "PNG"; o.save(); bpy.data.images.remove(o); novos.append(q)
    fs = novos
scn = bpy.context.scene
if not scn.sequence_editor: scn.sequence_editor_create()
st = scn.sequence_editor.strips.new_image("seq", fs[0], 1, 1)
for _ in range(REP):
    for i, p in enumerate(fs):
        if _ == 0 and i == 0: continue
        st.elements.append(os.path.basename(p))
im = bpy.data.images.load(fs[0]); w, h = im.size
scn.frame_start = 1; scn.frame_end = len(fs) * REP; scn.render.fps = FPS
scn.render.resolution_x = w - w % 2; scn.render.resolution_y = h - h % 2; scn.render.resolution_percentage = 100
ims = scn.render.image_settings
try: ims.media_type = "VIDEO"
except Exception: pass
ims.file_format = "FFMPEG"; scn.render.ffmpeg.format = "MPEG4"; scn.render.ffmpeg.codec = "H264"
scn.render.ffmpeg.constant_rate_factor = "HIGH"; scn.render.filepath = MP4
bpy.ops.render.render(animation=True)
print("OK", len(fs) * REP)
