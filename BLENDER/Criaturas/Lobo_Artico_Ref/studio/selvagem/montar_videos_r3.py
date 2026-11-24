"""Monta os videos do teste da IA r3 (Play no rpg_roblox, 20/11/2026) com ffmpeg (prioridade baixa, 2 threads).
- video_r3_limpo.mp4: aproximacao -> ameaca -> recuo -> retorno, normal + lento 0,5x (sem diagnostico).
- video_r3_diagnostico.mp4: insistencia -> ataque, normal + lento, com legenda do REGISTRO DO SERVIDOR (amostras 0,33 s;
  deslocamento video/registro ~0,8 s, +-0,5 s). O gravador do Studio nao captura interface (BillboardGui), por isso a legenda.
Uso: python montar_videos_r3.py"""
import os, subprocess
FF = r"C:\Users\Rhenan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
O = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "review", "rpg_ia_r3"))
DESLOC = 0.8
# registro do servidor do cenario "insiste" (fora_insiste3, IA r3h): t;nivel;motivo;Lider;Guardiao;Membro (estado/contato/focinho)
REG = """0.00;Ameaca;;Lid:Ameacar/no posto/16.8;Gua:Ameacar/indo ao posto/74.8;Mem:Ameacar/no posto/24.8
0.33;Atencao;intruso a vista;Lid:Atencao/-/83.7;Gua:Guardar/-/141.5;Mem:Atencao/-/91.7
4.38;Calmo;intruso recuou: acalma;Lid:Guardar/-/68.0;Gua:Atencao/-/125.8;Mem:Guardar/-/76.0
5.75;Atencao;intruso a vista;Lid:Atencao/-/52.8;Gua:Guardar/-/117.3;Mem:Atencao/-/62.8
6.47;Atencao;intruso a vista;Lid:Atencao/-/43.7;Gua:Atencao/-/113.0;Mem:Atencao/-/54.3
7.12;Atencao;intruso a vista;Lid:Atencao/-/35.8;Gua:Atencao/-/109.1;Mem:Atencao/-/46.3
7.80;Ameaca;intruso perto da toca: aviso;Lid:Ameacar/indo ao posto/28.7;Gua:Atencao/-/105.3;Mem:Ameacar/indo ao posto/37.8
8.83;Ameaca;intruso perto da toca: aviso;Lid:Ameacar/indo ao posto/24.7;Gua:Ameacar/indo ao posto/104.4;Mem:Ameacar/indo ao posto/32.2
9.80;Ameaca;intruso perto da toca: aviso;Lid:Ameacar/indo ao posto/21.8;Gua:Ameacar/indo ao posto/104.4;Mem:Ameacar/indo ao posto/29.3
10.82;Ameaca;intruso perto da toca: aviso;Lid:Ameacar/indo ao posto/18.8;Gua:Ameacar/indo ao posto/104.4;Mem:Ameacar/indo ao posto/27.3
11.82;Ameaca;intruso perto da toca: aviso;Lid:Ameacar/no posto/16.2;Gua:Ameacar/indo ao posto/104.4;Mem:Ameacar/indo ao posto/24.8
12.45;Ameaca;intruso perto da toca: aviso;Lid:Ameacar/no posto/14.7;Gua:Ameacar/indo ao posto/102.9;Mem:Ameacar/indo ao posto/22.0
13.05;Ameaca;intruso perto da toca: aviso;Lid:Ameacar/no posto/12.0;Gua:Ameacar/indo ao posto/100.2;Mem:Ameacar/no posto/17.9
13.37;Ameaca;intruso perto da toca: aviso;Lid:Ameacar/confronto: segura a posicao/11.0;Gua:Ameacar/indo ao posto/99.2;Mem:Ameacar/no posto/16.0
13.72;Ameaca;intruso perto da toca: aviso;Lid:Ameacar/confronto: segura a posicao/9.5;Gua:Ameacar/indo ao posto/97.8;Mem:Ameacar/no posto/14.4
14.35;Defesa;insistiu apos o aviso;Lid:Defender/aproximando/6.5;Gua:Ameacar/indo ao posto/95.1;Mem:Defender/perseguindo/11.5
14.68;Defesa;insistiu apos o aviso;Lid:Defender/aproximando/4.7;Gua:Defender/guarda o ovo/94.3;Mem:Defender/perseguindo/9.7
15.04;Defesa;insistiu apos o aviso;Lid:Defender/aproximando/3.1;Gua:Defender/guarda o ovo/94.3;Mem:Defender/perseguindo/8.2
15.37;Defesa;insistiu apos o aviso;Lid:Defender/contato/1.1;Gua:Defender/guarda o ovo/94.3;Mem:Defender/aproximando/6.0
16.00;Defesa;insistiu apos o aviso;Lid:Defender/reposicionar/3.4;Gua:Defender/guarda o ovo/94.3;Mem:Defender/contato/2.3
16.63;Defesa;insistiu apos o aviso;Lid:Defender/reposicionar/7.5;Gua:Defender/guarda o ovo/94.3;Mem:Defender/reposicionar/3.1
17.30;Defesa;insistiu apos o aviso;Lid:Defender/reposicionar/11.4;Gua:Defender/guarda o ovo/94.3;Mem:Defender/reposicionar/6.7
17.65;Defesa;(registro do servidor termina aqui - o Play seguiu em Defesa);Lid:-/-/-;Gua:-/-/-;Mem:-/-/-"""

def ts(x):
    x = max(0.0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return "%02d:%02d:%06.3f" % (h, m, s)

def srt(caminho, escala=1.0, fim=30.0):
    linhas = [l.split(";") for l in REG.strip().splitlines()]
    out = []
    for i, c in enumerate(linhas):
        t0 = (float(c[0]) + DESLOC) * escala
        t1 = ((float(linhas[i + 1][0]) + DESLOC) * escala) if i + 1 < len(linhas) else fim * escala
        lob = []
        for campo, nome in ((c[3], "Lider"), (c[5], "Membro"), (c[4], "Guardiao")):
            est, cont, dF = campo.split(":", 1)[1].split("/")
            lob.append("%s: %s %s | focinho %s" % (nome, est, "" if cont == "-" else "(" + cont + ")", dF))
        txt = "ALCATEIA: %s%s\\N%s" % (c[1].upper(), (" - " + c[2]) if c[2] else "", "\\N".join(lob))
        out.append("%d\n%s --> %s\n%s\n" % (i + 1, ts(t0).replace(".", ","), ts(t1).replace(".", ","), txt))
    open(caminho, "w", encoding="utf-8").write("\n".join(out))

def ff(args):
    cmd = [FF, "-y", "-v", "error", "-threads", "2"] + args
    p = subprocess.Popen(cmd, cwd=O, creationflags=0x00000040)       # IDLE_PRIORITY_CLASS
    p.wait(); assert p.returncode == 0, cmd

ROT = "drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='%s':x=24:y=20:fontsize=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=8"
# limpo: normal + lento 0,5x
ff(["-i", "bruto_recua_limpo.mp4", "-filter_complex",
    "[0:v]fps=30,scale=1280:-2,split[a][b];[a]%s[n];[b]setpts=2.0*PTS,%s[l];[n][l]concat=n=2:v=1:a=0[v]" % (
        ROT % "IA r3 - aproxima. ve o aviso. para e recua (normal)", ROT % "lento 0.5x"),
    "-map", "[v]", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-pix_fmt", "yuv420p", "video_r3_limpo.mp4"])
# diagnostico: legenda do registro (normal e lento)
srt(os.path.join(O, "diag_normal.srt"), 1.0); srt(os.path.join(O, "diag_lento.srt"), 2.0)
EST = "force_style='FontName=Arial,FontSize=13,Alignment=7,MarginL=12,MarginV=10,BackColour=&H80000000,BorderStyle=4,Outline=0'"
ff(["-i", "bruto_insiste_diag.mp4", "-filter_complex",
    "[0:v]fps=30,scale=1280:-2,split[a][b];[a]subtitles=diag_normal.srt:fontsdir='C\:/Windows/Fonts':%s[n];[b]setpts=2.0*PTS,subtitles=diag_lento.srt:fontsdir='C\:/Windows/Fonts':%s[l];[n][l]concat=n=2:v=1:a=0[v]" % (EST, EST),
    "-map", "[v]", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-pix_fmt", "yuv420p", "video_r3_diagnostico.mp4"])
print("ok", O)
