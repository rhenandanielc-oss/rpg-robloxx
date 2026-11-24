"""v46: monta os videos de revisao das curvas andando a partir dos quadros de vistas_curvas_v46.py (PIL + ffmpeg, leve:
1 thread, prioridade baixa). Cada painel tem rotulo (versao + vista); a barra de baixo mostra o diagnostico do quadro (clipe,
quadro do clipe, omega pedido, rumo acumulado). Trechos 'lento' repetem cada quadro (0,5x).
Uso: python montar_videos_v46.py <dir_quadros> <dir_saida>"""
import os, sys, json, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont
Q, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
FF = r"C:\Users\Rhenan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
F1 = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 17); F2 = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 15)
NOME_V = {"topo": "vista superior (camera fixa)", "c34": "tres-quartos (camera fixa)", "perfil_E": "perfil esquerdo (segue)", "perfil_D": "perfil direito (segue)",
          "frente": "frente (segue)", "tras": "traseira (segue)", "close_E": "close patas esq (segue)", "close_D": "close patas dir (segue)"}
def quadros(pre, cen, v):
    d = os.path.join(Q, v); p = "%s_LOW_%s_%s_t" % (pre, cen, v)
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.startswith(p))
def linha(pre, cen):
    p = os.path.join(Q, "%s_LOW_%s_linha.json" % (pre, cen)); return json.load(open(p)) if os.path.exists(p) else None
def rotular(im, txt, cor):
    d = ImageDraw.Draw(im); w = d.textlength(txt, font=F1) + 14; d.rectangle((0, 0, w, 26), fill=(20, 22, 26)); d.text((7, 4), txt, font=F1, fill=cor); return im
def montar(nome, titulo, cen, linhas_painel, lento=False):
    """linhas_painel: lista de linhas; cada linha = lista de (prefixo 'ANTES'|'V46B', vista)"""
    tmp = os.path.join(OUT, "_tmp_" + nome); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    fontes = {(p, v): quadros(p, cen, v) for row in linhas_painel for p, v in row}
    n = min(len(x) for x in fontes.values()); LJ = linha("V46B", cen); LA = linha("ANTES", cen); k = 0
    for i in range(n):
        rows = []
        for row in linhas_painel:
            ims = []
            for p, v in row:
                im = Image.open(fontes[(p, v)][i]).convert("RGB")
                rotular(im, ("ANTES  r10e  clipe reto + pivo girando" if p == "ANTES" else "DEPOIS  v46b  curva com passos") + "  |  " + NOME_V[v],
                        (255, 170, 90) if p == "ANTES" else (140, 230, 140)); ims.append(im)
            W = sum(x.width for x in ims); H = max(x.height for x in ims); r = Image.new("RGB", (W, H)); x0 = 0
            for x in ims: r.paste(x, (x0, 0)); x0 += x.width
            rows.append(r)
        W = max(r.width for r in rows); H = sum(r.height for r in rows) + 58; fr = Image.new("RGB", (W, H), (20, 22, 26)); y0 = 30
        for r in rows: fr.paste(r, (0, y0)); y0 += r.height
        d = ImageDraw.Draw(fr); d.text((8, 6), titulo + ("   [lento 0,5x]" if lento else ""), font=F1, fill=(235, 235, 235))
        if LJ and i < len(LJ):
            e = LJ[i]; t = "clipe %s q%d   omega %.0f graus/s   rumo %.0f graus   t %.2f s" % (e["clipe"], e["qc"], e["omega"], e["psi"], i * 2 / 30)
            if LA and i < len(LA) and any(p == "ANTES" for row in linhas_painel for p, _ in row): t += "   (antes: mesmo giro aplicado ao pivo com o Andar reto)"
            d.text((8, H - 24), t, font=F2, fill=(200, 210, 220))
        for _ in range(2 if lento else 1):
            fr.save(os.path.join(tmp, "f%05d.png" % k)); k += 1
    out = os.path.join(OUT, nome + ".mp4")
    cmd = [FF, "-v", "error", "-y", "-threads", "1", "-framerate", "15", "-i", os.path.join(tmp, "f%05d.png"), "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-x264-params", "threads=1", out]
    p = subprocess.Popen(cmd, creationflags=0x00000040); p.wait(); shutil.rmtree(tmp, ignore_errors=True)   # IDLE_PRIORITY_CLASS
    print("VIDEO", out, n, "quadros", flush=True); return out
def juntar(nome, partes):
    lst = os.path.join(OUT, "_lista_%s.txt" % nome); open(lst, "w").write("".join("file '%s'\n" % p.replace("\\", "/") for p in partes))
    out = os.path.join(OUT, nome + ".mp4")
    p = subprocess.Popen([FF, "-v", "error", "-y", "-threads", "1", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], creationflags=0x00000040); p.wait()
    os.remove(lst); [os.remove(x) for x in partes]; print("VIDEO_FINAL", out, flush=True)
if __name__ == "__main__":
    qual = sys.argv[3] if len(sys.argv) > 3 else "tudo"
    if qual in ("tudo", "antes_depois"):
        P = []
        for v in ("topo", "c34", "perfil_E", "perfil_D", "frente", "tras"):
            P.append(montar("ad_" + v, "Curva aberta a esquerda 30 graus por s  -  antes x depois", "aberta_E", [[("ANTES", v), ("V46B", v)]]))
        for v in ("c34", "perfil_E"):
            P.append(montar("ad_lento_" + v, "Curva aberta a esquerda 30 graus por s  -  antes x depois", "aberta_E", [[("ANTES", v), ("V46B", v)]], lento=True))
        juntar("video_v46_antes_depois_aberta_E", P)
        P = [montar("fd_" + v, "Curva fechada a direita 45 graus por s  -  antes x depois", "fechada_D", [[("ANTES", v), ("V46B", v)]]) for v in ("topo", "c34", "perfil_D")]
        juntar("video_v46_antes_depois_fechada_D", P)
    if qual in ("tudo", "cenarios"):
        P = [montar("c_fd", "DEPOIS  curva fechada a direita  (entrada 30 -> 45 -> saida)", "fechada_D", [[("V46B", "c34"), ("V46B", "perfil_D")], [("V46B", "close_D"), ("V46B", "frente")]]),
             montar("c_fd_lento", "DEPOIS  curva fechada a direita  close das patas", "fechada_D", [[("V46B", "close_D"), ("V46B", "frente")]], lento=True),
             montar("c_180", "DEPOIS  destino atras  180 graus em curva (curvas concatenadas)", "volta_180_E", [[("V46B", "topo"), ("V46B", "c34")], [("V46B", "perfil_E")]]),
             montar("c_inv", "DEPOIS  curva em S  esquerda -> direita", "inverte_EparaD", [[("V46B", "topo"), ("V46B", "c34")]]),
             montar("c_parado", "DEPOIS  partindo parado para a curva  (fade Repouso -> Andar ainda escorrega)", "parado_para_curva_E", [[("V46B", "topo"), ("V46B", "c34"), ("V46B", "close_E")]])]
        juntar("video_v46_cenarios", P)
