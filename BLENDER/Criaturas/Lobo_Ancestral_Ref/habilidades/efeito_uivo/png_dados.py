"""PNG de DADOS da mascara do Uivo para o Roblox (lido pixel a pixel pelo cliente, nao usado como textura direta):
R = linhas (0..255); G = runas 1..127 (valor/2, minimo 1) ou olhos 128..255 (128 + E/2); B = coordenada cabeca->cauda; A = 255.
Fonte: mascara_uivo.bin (gerar_mascara_uivo.py). Saida: mascara_uivo_dados.png (1024x1024 RGBA)."""
import os
from PIL import Image
AQUI = os.path.dirname(os.path.abspath(__file__)); N = 1024
b = open(os.path.join(AQUI, "mascara_uivo.bin"), "rb").read()
im = Image.new("RGBA", (N, N), (0, 0, 0, 255)); px = im.load()
i = 0; ant = -1; n = 0
while i < len(b):
    d = 0; sh = 0
    while True:
        c = b[i]; i += 1; d |= (c & 127) << sh; sh += 7
        if not c & 128: break
    ant += d; L, R, E, S = b[i:i + 4]; i += 4
    g = 128 + E // 2 if E >= R and E > 0 else (max(1, R // 2) if R > 0 else 0)
    px[ant % N, ant // N] = (L, g, S, 255); n += 1
im.save(os.path.join(AQUI, "mascara_uivo_dados.png"))
print("PNG_OK", n)
