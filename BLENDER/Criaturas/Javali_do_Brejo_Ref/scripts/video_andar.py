"""Video MP4 do Andar (lateral fixa em cima, 3/4 fixa embaixo): 2 passadas em velocidade real + 1 em meia velocidade.
Passo 1 (python): compoe os quadros.   python scripts/video_andar.py quadros <dir_render_rotulo> <dir_quadros>
Passo 2 (blender, sem ffmpeg externo): blender -b --factory-startup -P scripts/video_andar.py -- <dir_quadros> <saida.mp4>"""
import sys, os, glob
if sys.argv[1:2] == ["quadros"]:
    from PIL import Image, ImageDraw, ImageFont
    D, Q = sys.argv[2], sys.argv[3]; os.makedirs(Q, exist_ok=True); F = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    DIRS = D.split(",")                 # varias pastas = varios clipes em sequencia, cada um 1x em velocidade real
    seq = []
    for d in DIRS:
        lado = sorted(glob.glob(os.path.join(d, "lado_fixo", "q*.png"))); tq = sorted(glob.glob(os.path.join(d, "34_fixo", "q*.png")))
        rot = os.path.basename(os.path.normpath(d))
        if len(DIRS) == 1:
            seq += [(lado[i], tq[i], i, rot, "velocidade real") for i in range(len(lado))] * 2 + [(lado[i], tq[i], i, rot, "1/2 velocidade") for i in range(len(lado)) for _ in (0, 1)]
        else:
            seq += [(lado[i], tq[i], i, rot, "velocidade real") for i in range(len(lado))]
    for n, (la, tqa, i, rot, txt) in enumerate(seq):
        a = Image.open(la).convert("RGB"); b = Image.open(tqa).convert("RGB"); b = b.resize((a.width, round(b.height * a.width / b.width)))
        o = Image.new("RGB", (a.width, a.height + b.height + 30), (40, 38, 36)); o.paste(a, (0, 30)); o.paste(b, (0, 30 + a.height))
        ImageDraw.Draw(o).text((8, 5), f"Javali-do-Brejo v4 · {rot} (câmeras fixas, quadriculado 10 cm, postes a cada 0,25 u) · q{i:03d} · {txt}", fill=(240, 240, 240), font=F)
        o.save(os.path.join(Q, "f%04d.png" % n))
    print("QUADROS", len(seq), o.size)
else:
    import bpy
    A = sys.argv[sys.argv.index("--") + 1:]; Q, SAIDA = os.path.abspath(A[0]), os.path.abspath(A[1])
    arqs = sorted(glob.glob(os.path.join(Q, "f*.png"))); sc = bpy.context.scene
    im = bpy.data.images.load(arqs[0]); W, H = im.size; W -= W % 2; H -= H % 2
    sed = sc.sequence_editor_create()
    st = sed.strips.new_image("Andar", arqs[0], 1, 1, fit_method="ORIGINAL")
    for a in arqs[1:]: st.elements.append(os.path.basename(a))
    sc.frame_start, sc.frame_end = 1, len(arqs); sc.render.fps = 30
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
    sc.render.image_settings.media_type = "VIDEO"; sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"; sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.filepath = SAIDA; sc.render.use_sequencer = True
    bpy.ops.render.render(animation=True); print("VIDEO", SAIDA, len(arqs), W, H)
