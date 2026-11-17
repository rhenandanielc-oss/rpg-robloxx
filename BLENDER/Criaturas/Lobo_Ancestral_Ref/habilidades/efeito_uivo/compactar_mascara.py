"""Compacta mascara_uivo.bin (formato do gerador) para o Studio: sequencias de texels contiguos.
Formato v2: [gap varint][n byte 1..255] + n * ([L4<<4 | S4], [R4<<4 | E4]); gap = inicio da sequencia - (fim da anterior).
Grava mascara_uivo_v2.txt (base64) e pedacos de 30.000 caracteres com checksum (h = h*31 + byte mod 1000000007)."""
import os, base64, json
AQUI = os.path.dirname(os.path.abspath(__file__))
b = open(os.path.join(AQUI, "mascara_uivo.bin"), "rb").read()
i = 0; ant = -1; tex = []
while i < len(b):
    d = 0; sh = 0
    while True:
        c = b[i]; i += 1; d |= (c & 127) << sh; sh += 7
        if not c & 128: break
    ant += d; Lv, Rv, Ev, Sv = b[i:i + 4]; i += 4
    tex.append((ant, Lv, Rv, Ev, Sv))
def q4(v): return min(15, (v + 8) // 17)
out = bytearray(); k = 0; fim = 0
while k < len(tex):
    j = k
    while j + 1 < len(tex) and tex[j + 1][0] == tex[j][0] + 1 and j + 1 - k < 255: j += 1
    gap = tex[k][0] - fim
    while True:
        b7 = gap & 127; gap >>= 7
        if gap: out.append(b7 | 128)
        else: out.append(b7); break
    out.append(j - k + 1)
    for t in tex[k:j + 1]:
        out.append(q4(t[1]) << 4 | q4(t[4])); out.append(q4(t[2]) << 4 | q4(t[3]))
    fim = tex[j][0] + 1; k = j + 1
s = base64.b64encode(bytes(out)).decode()
open(os.path.join(AQUI, "mascara_uivo_v2.txt"), "w").write(s)
def hs(x):
    h = 0
    for c in x.encode(): h = (h * 31 + c) % 1000000007
    return h
P = 30000; partes = [s[i:i + P] for i in range(0, len(s), P)]
for n, p in enumerate(partes): open(os.path.join(AQUI, "parte_%d.txt" % n), "w").write(p)
print(json.dumps({"texels": len(tex), "bytes": len(out), "base64": len(s), "h_total": hs(s), "partes": [[len(p), hs(p)] for p in partes]}))
