# Junta os quadros de ciclo de duas versoes (04b_closes.py modo ciclo) em grade 2x2 e grava MP4 + PNGs.
# Grade: em cima 3/4 (E3 | E4), embaixo lado (E3 | E4).
# Uso: blender -b -P 04d_video.py -- <pasta quadros> <clipe> <saida.mp4> <pasta grade> [fps] [versaoA] [versaoB]
import bpy, sys, os, glob
import numpy as np
argv = sys.argv[sys.argv.index("--") + 1:]
SRC, CLIPE, MP4, GRADE = argv[0], argv[1], argv[2], argv[3]
FPS = int(argv[4]) if len(argv) > 4 else 24
VA = argv[5] if len(argv) > 5 else "E3"; VB = argv[6] if len(argv) > 6 else "E4"
os.makedirs(GRADE, exist_ok=True)
def ler(p):
    im = bpy.data.images.load(p); w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4); bpy.data.images.remove(im); return a
quadros = sorted(int(os.path.basename(p)[-7:-4]) for p in glob.glob(os.path.join(SRC, f"{VB}_{CLIPE}_tres4_*.png")))
saidas = []
for f in quadros:
    q = {(v, e): ler(os.path.join(SRC, f"{e}_{CLIPE}_{v}_{f:03d}.png")) for v in ("tres4", "lado") for e in (VA, VB)}
    h, w = q[("tres4", VA)].shape[:2]
    big = np.ones((2 * h + 4, 2 * w + 4, 4), dtype=np.float32)
    big[h + 4:, :w] = q[("tres4", VA)]; big[h + 4:, w + 4:] = q[("tres4", VB)]   # linha de cima (imagem invertida em y)
    big[:h, :w] = q[("lado", VA)]; big[:h, w + 4:] = q[("lado", VB)]
    im = bpy.data.images.new("G", big.shape[1], big.shape[0]); im.pixels = big.ravel()
    p = os.path.join(GRADE, f"{CLIPE}_{f:03d}.png"); im.filepath_raw = p; im.file_format = "PNG"; im.save()
    bpy.data.images.remove(im); saidas.append(p)
# MP4 pelo editor de video
scn = bpy.context.scene
if not scn.sequence_editor: scn.sequence_editor_create()
st = scn.sequence_editor.strips.new_image("ciclo", saidas[0], 1, 1)
for p in saidas[1:]: st.elements.append(os.path.basename(p))
scn.frame_start = 1; scn.frame_end = len(saidas); scn.render.fps = FPS
h, w = big.shape[:2]; scn.render.resolution_x = w - w % 2; scn.render.resolution_y = h - h % 2; scn.render.resolution_percentage = 100
ims = scn.render.image_settings
try: ims.media_type = "VIDEO"
except Exception: pass
ims.file_format = "FFMPEG"; scn.render.ffmpeg.format = "MPEG4"; scn.render.ffmpeg.codec = "H264"
scn.render.ffmpeg.constant_rate_factor = "HIGH"
scn.render.filepath = MP4
bpy.ops.render.render(animation=True)
print("OK", len(saidas), "quadros")
