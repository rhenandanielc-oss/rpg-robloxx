"""Quadros da mascara emissiva do Uivo (cinza; o Roblox usa o canal vermelho), para alternar no cliente sem EditableImage.
Quadros 0-4: pulso de luz percorrendo o corpo da cabeca (0) para a cauda (1): linhas = L*(0,5 + 0,5*pulso), runas fracas (0,25),
olhos 0,9. Quadro 5: pico do uivo - linhas 0,8, runas 1,0, olhos 1,0.
Fonte: mascara_uivo.bin. Saida: quadros/uivo_q0.png .. uivo_q5.png (1024x1024)."""
import os, math
import numpy as np
from PIL import Image
AQUI = os.path.dirname(os.path.abspath(__file__)); N = 1024
OUT = os.path.join(AQUI, "quadros"); os.makedirs(OUT, exist_ok=True)
b = open(os.path.join(AQUI, "mascara_uivo.bin"), "rb").read()
idx, L, R, E, S = [], [], [], [], []
i = 0; ant = -1
while i < len(b):
    d = 0; sh = 0
    while True:
        c = b[i]; i += 1; d |= (c & 127) << sh; sh += 7
        if not c & 128: break
    ant += d; idx.append(ant); L.append(b[i]); R.append(b[i + 1]); E.append(b[i + 2]); S.append(b[i + 3]); i += 4
idx = np.array(idx); L = np.array(L) / 255; R = np.array(R) / 255; E = np.array(E) / 255; S = np.array(S) / 255
def salvar(v, nome):
    img = np.zeros(N * N, np.uint8); img[idx] = np.clip(v * 255 + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(img.reshape(N, N), "L").convert("RGB").save(os.path.join(OUT, nome))
for k in range(5):
    c = k / 5 * 1.3 - 0.15 + 0.13
    v = L * (0.5 + 0.5 * np.exp(-((S - c) / 0.14) ** 2)) + R * 0.25 + E * 0.9
    salvar(np.minimum(v, 1), "uivo_q%d.png" % k)
salvar(np.minimum(L * 0.8 + R * 1.0 + E * 1.0, 1), "uivo_q5.png")
print("QUADROS_OK", sorted(os.listdir(OUT)))
# r2 (16/11, pedido do usuario: mais linhas no corpo e olhos verdes fortes): mascara FIXA usada no jogo
# linhas 0,7, runas 1,0, olhos 1,0 (olhos e runas mais fortes que as linhas)
salvar(np.minimum(L * 0.7 + R * 1.0 + E * 1.0, 1), "uivo_fixa_r2.png")
print("FIXA_R2_OK")
