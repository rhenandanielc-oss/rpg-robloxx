"""v47: video de revisao da virada de COMBATE (PIL + ffmpeg, 1 thread, prioridade baixa). Lado a lado: ANTES = virada atual
VirarEsquerda + VirarDireita (90 graus, 3,1 s cada) x DEPOIS = VirarCombate90Esquerda + Direita (1,0 s cada), por vista; a sequencia
mais curta fica parada no ultimo quadro. Depois a de 180 graus (2x2) e trechos lentos 0,5x. Uso: python montar_videos_v47.py <quadros> <saida>"""
import os, sys, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont
Q, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
FF = r"C:\Users\Rhenan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
F1 = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 16); F2 = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 15)
NV = {"topo": "vista superior", "34": "tres-quartos", "perfil_E": "perfil esquerdo", "frente": "frente", "patas_E": "close patas esq"}
def lista(sq, v): return sorted(os.path.join(Q, f) for f in os.listdir(Q) if f.startswith("LOW_%s_%s_t" % (sq, v)))
def rot(im, t, c):
    d = ImageDraw.Draw(im); w = d.textlength(t, font=F1) + 12; d.rectangle((0, 0, w, 24), fill=(20, 22, 26)); d.text((6, 3), t, font=F1, fill=c); return im
def montar(nome, titulo, paineis, lento=False):
    tmp = os.path.join(OUT, "_tmp_" + nome); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    L = [(lista(sq, v), r, c) for sq, v, r, c in paineis]; n = max(len(x[0]) for x in L); k = 0; cols = 2
    for i in range(n):
        ims = [rot(Image.open(fs[min(i, len(fs) - 1)]).convert("RGB"), r, c) for fs, r, c in L]
        w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols; fr = Image.new("RGB", (w * min(cols, len(ims)), h * rows + 54), (20, 22, 26))
        for j, im in enumerate(ims): fr.paste(im, ((j % cols) * w, 28 + (j // cols) * h))
        d = ImageDraw.Draw(fr); d.text((8, 5), titulo + ("   [lento 0,5x]" if lento else ""), font=F1, fill=(235, 235, 235))
        d.text((8, fr.height - 22), "t %.2f s   chao em grade de 0,5/1 stud   rastros: DE azul  DD vermelho  TE verde  TD amarelo   seta = rumo" % (i / 30), font=F2, fill=(200, 210, 220))
        for _ in range(2 if lento else 1): fr.save(os.path.join(tmp, "f%05d.png" % k)); k += 1
    out = os.path.join(OUT, nome + ".mp4")
    subprocess.Popen([FF, "-v", "error", "-y", "-threads", "1", "-framerate", "30", "-i", os.path.join(tmp, "f%05d.png"), "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                      "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-x264-params", "threads=1", out], creationflags=0x40).wait()
    shutil.rmtree(tmp, ignore_errors=True); print("VIDEO", out, n, flush=True); return out
A = (255, 170, 90); D = (140, 230, 140)
P = []
for v in ("topo", "34", "perfil_E", "frente", "patas_E"):
    P.append(montar("ad_" + v, "Virada de 90 graus - ANTES (calma 3,1 s) x DEPOIS (combate 1,0 s, pivo nas traseiras) - ida e volta",
                    [("antes_90E", v, "ANTES  Virar 90  |  " + NV[v], A), ("ida_volta_90E", v, "DEPOIS  VirarCombate90  |  " + NV[v], D)]))
P.append(montar("ad_lento", "Virada de combate 90 graus - detalhe", [("ida_volta_90E", "34", "DEPOIS  tres-quartos", D), ("ida_volta_90E", "patas_E", "DEPOIS  close patas", D)], lento=True))
P.append(montar("c180", "Virada de combate 180 graus (1,6 s) - ida e volta", [("ida_volta_180E", "topo", "DEPOIS  vista superior", D), ("ida_volta_180E", "34", "DEPOIS  tres-quartos", D),
                                                                           ("ida_volta_180E", "perfil_E", "DEPOIS  perfil esquerdo", D), ("ida_volta_180E", "frente", "DEPOIS  frente", D)]))
P.append(montar("c180_lento", "Virada de combate 180 graus - detalhe", [("ida_volta_180E", "34", "DEPOIS  tres-quartos", D), ("ida_volta_180E", "patas_E", "DEPOIS  close patas", D)], lento=True))
lst = os.path.join(OUT, "_lista.txt"); open(lst, "w").write("".join("file '%s'\n" % p.replace("\\", "/") for p in P))
fin = os.path.join(OUT, "video_v47_virada_combate.mp4")
subprocess.Popen([FF, "-v", "error", "-y", "-threads", "1", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", fin], creationflags=0x40).wait()
os.remove(lst); [os.remove(p) for p in P]; print("VIDEO_FINAL", fin, flush=True)
