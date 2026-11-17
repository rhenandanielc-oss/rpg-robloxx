"""Mascara emissiva do Uivo Ancestral (16/11/2026; REFERENCIAS_PODERES_E_EFEITOS v6.2 §5.1/§5.2) [PROPOSTA].
Gera, no UV da malha LOW do lobo (1024x1024, o mesmo da SurfaceAppearance do Studio), 4 canais:
  L = linhas finas e continuas na direcao do pelo (tronco/pescoco/cauda ao longo do corpo; patas descendo), mais fortes nas costas
      e nos ombros, mais fracas nas pernas; rosto limpo.
  R = runas pequenas (ombro, flanco, coxa, dos dois lados) - acendem no pico do uivo.
  E = olhos (brilho proprio).
  S = coordenada cabeca->cauda (0..255) para o pulso de luz que percorre o corpo (calculado no cliente).
Saidas: habilidades/efeito_uivo/mascara_uivo.png (preview RGBA = L,R,E,S), mascara_uivo.bin (texels nao nulos) e
mascara_uivo.txt (base64 do .bin para o Studio) + render de conferencia.
Uso: blender -b rig18/Lobo_Ancestral_Anim_v31.blend -P habilidades/efeito_uivo/gerar_mascara_uivo.py"""
import bpy, bmesh, os, math, struct, base64, json
import numpy as np
from mathutils import Vector as V
AQUI = os.path.dirname(os.path.abspath(__file__))
N = 1024
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
lobo = [o for o in bpy.data.objects if o.type == "MESH" and o.find_armature() == arm and "LOW" in o.name][0]
BD = arm.data.bones
me = lobo.data
uvl = me.uv_layers.active.data
gnome = {g.index: g.name for g in lobo.vertex_groups}
# grupo dominante de cada vertice
dom = []
for v in me.vertices:
    best, bw = None, 0
    for g in v.groups:
        if g.weight > bw: best, bw = gnome[g.group], g.weight
    dom.append(best or "")
CO = np.array([v.co[:] for v in me.vertices], dtype=np.float64)
NO = np.array([v.normal[:] for v in me.vertices], dtype=np.float64)

def h(b): return np.array(BD[b].head_local[:])
def t(b): return np.array(BD[b].tail_local[:])
# eixos (polilinhas) - a linha do pelo segue o eixo; o angulo em volta do eixo define cada linha
ESPINHA = [t("Cabeca") * 0 + h("Cabeca"), h("Pescoco2"), h("Pescoco1"), h("Peito"), h("Coluna2"), h("Coluna1"), h("Pelve")]
CAUDA = [h("Pelve")] + [t("Cauda%d" % i) for i in range(1, 8)]
EIXO_CORPO = ESPINHA + CAUDA[1:]
def perna(lado, frente):
    if frente: return [h("Escapula" + lado), h("Braco" + lado), h("Antebraco" + lado), h("Mao" + lado), t("Mao" + lado)]
    return [h("Coxa" + lado), h("Canela" + lado), h("Metatarso" + lado), t("Metatarso" + lado)]
PERNAS = {"PernaFE": perna("E", True), "PernaFD": perna("D", True), "PernaTE": perna("E", False), "PernaTD": perna("D", False)}
def regiao(g):
    if g in ("Cabeca", "Mandibula", "OrelhaE", "OrelhaD", "PeloBochechaE", "PeloBochechaD", "PalpebraE", "PalpebraD"): return "Cabeca"
    for lado in "ED":
        if g in ("Escapula" + lado, "Braco" + lado, "Antebraco" + lado, "Mao" + lado, "Dedos" + lado, "Carpo" + lado, "PeloCotovelo" + lado):
            return "PernaF" + lado if g != "Escapula" + lado else "Corpo"
        if g in ("Coxa" + lado, "Canela" + lado, "Metatarso" + lado, "Pe" + lado, "PeloCoxa" + lado):
            return "PernaT" + lado if g not in ("Coxa" + lado, "PeloCoxa" + lado) else "Corpo"
    return "Corpo"
REG = [regiao(g) for g in dom]

# ---------------------------------------------------------------- rasterizacao no UV (posicao 3D, normal, regiao por texel)
OLHOF = np.zeros((N, N))                                             # olhos marcados por triangulo (UV compartilhado nao apaga)
OLHOS = [(np.array(BD['Palpebra' + l].head_local[:]) + np.array(BD['Palpebra' + l].tail_local[:])) / 2 + np.array([0, 0.0, -0.03]) for l in 'ED']
ROSTO = np.zeros((N, N), bool)                                     # texels usados pela frente da cabeca (UV compartilhado)
P = np.zeros((N, N, 3)); NRM = np.zeros((N, N, 3)); RG = np.full((N, N), -1, dtype=np.int16); COB = np.zeros((N, N), bool)
NOMES = ["Corpo", "Cabeca", "PernaFE", "PernaFD", "PernaTE", "PernaTD"]
ri = {n: i for i, n in enumerate(NOMES)}
bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.verts.ensure_lookup_table()
uvb = bm.loops.layers.uv.active
for f in bm.faces:
    ls = f.loops
    uv = np.array([[l[uvb].uv.x * N - 0.5, (1 - l[uvb].uv.y) * N - 0.5] for l in ls])
    vi = [l.vert.index for l in ls]
    x0, x1 = int(math.floor(uv[:, 0].min())), int(math.ceil(uv[:, 0].max()))
    y0, y1 = int(math.floor(uv[:, 1].min())), int(math.ceil(uv[:, 1].max()))
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, N - 1), min(y1, N - 1)
    if x1 < x0 or y1 < y0: continue
    xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
    a, b, c = uv
    den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if abs(den) < 1e-12: continue
    w0 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / den
    w1 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / den
    w2 = 1 - w0 - w1
    m = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
    if not m.any(): continue
    yy, xx = ys[m], xs[m]
    W = np.stack([w0[m], w1[m], w2[m]], 1)
    P[yy, xx] = W @ CO[vi]; NRM[yy, xx] = W @ NO[vi]
    k = int(np.argmax(W.sum(0)))
    rr = [ri[REG[i]] for i in vi]
    RG[yy, xx] = np.where(W[:, 0] >= np.maximum(W[:, 1], W[:, 2]), rr[0], np.where(W[:, 1] >= W[:, 2], rr[1], rr[2]))
    COB[yy, xx] = True
    for oc in OLHOS:
        if np.linalg.norm(CO[vi].mean(0) - oc) < 0.35:
            dd = np.linalg.norm(P[yy, xx] - oc, axis=1)
            OLHOF[yy, xx] = np.maximum(OLHOF[yy, xx], np.clip(1 - (dd - 0.17) / 0.05, 0, 1) * (NRM[yy, xx][:, 1] < 0.3))
    if all(REG[i] == "Cabeca" for i in vi) and CO[vi][:, 1].mean() < -4.95: ROSTO[yy, xx] = True
bm.free()
idx = np.argwhere(COB); pts = P[COB]; nrm = NRM[COB]; reg = RG[COB]
print("texels cobertos", len(idx))

def proj_polilinha(pts, poly):
    """ponto mais proximo na polilinha: retorna (ponto, tangente, s acumulado 0..1)"""
    poly = np.array(poly); seg = poly[1:] - poly[:-1]; L = np.linalg.norm(seg, axis=1); cum = np.concatenate([[0], np.cumsum(L)])
    best_d = np.full(len(pts), np.inf); best_c = np.zeros((len(pts), 3)); best_t = np.zeros((len(pts), 3)); best_s = np.zeros(len(pts))
    for i in range(len(seg)):
        d = seg[i]; u = np.clip(((pts - poly[i]) @ d) / (d @ d), 0, 1)
        c = poly[i] + u[:, None] * d; dist = np.linalg.norm(pts - c, axis=1)
        mm = dist < best_d
        best_d[mm] = dist[mm]; best_c[mm] = c[mm]; best_t[mm] = d / L[i]; best_s[mm] = (cum[i] + u[mm] * L[i]) / cum[-1]
    return best_c, best_t, best_s

def linhas_ang(pts, c, tg, ref, angs, larg):
    """intensidade de linhas de angulo constante em volta do eixo (arco = r * dang); suave na borda (anti-alias)"""
    rv = pts - c; rv -= (rv * tg).sum(1, keepdims=True) * tg; r = np.linalg.norm(rv, axis=1) + 1e-9
    e1 = ref - (ref * tg).sum(1, keepdims=True) * tg; e1 /= np.linalg.norm(e1, axis=1, keepdims=True) + 1e-9
    e2 = np.cross(tg, e1)
    phi = np.arctan2((rv * e2).sum(1), (rv * e1).sum(1))
    best = np.full(len(pts), np.inf)
    for a in angs:
        da = np.abs((phi - a + np.pi) % (2 * np.pi) - np.pi); best = np.minimum(best, da * r)
    return np.clip(1 - (best - larg / 2) / 0.02, 0, 1), phi

L = np.zeros(len(pts)); R = np.zeros(len(pts)); E = np.zeros(len(pts)); S = np.zeros(len(pts))
ALT = 8.49; LARG = 0.013 * ALT                                     # ~1,3% da altura do corpo (r2 a pedido do usuario: mais visivel)
# corpo (tronco, pescoco, cauda): linhas ao longo do eixo, referencia "para cima"
mc = reg == ri["Corpo"]
c, tg, s = proj_polilinha(pts[mc], EIXO_CORPO)
onda = 0.10 * np.sin(pts[mc][:, 1] * 0.9)                          # leve ondulacao organica
angs = [math.radians(a) for a in (0, 25, -25, 50, -50, 78, -78, 110, -110)]   # 9 linhas: dorso, flancos e lado da barriga
up = np.tile([0, 0, 1.0], (mc.sum(), 1))
li, phi = linhas_ang(pts[mc] + 0 * onda[:, None], c, tg, up, [a for a in angs], LARG)
li2, _ = linhas_ang(pts[mc], c, tg, up, [a + 0.0 for a in angs], LARG)
peso = 0.75 + 0.25 * np.clip(1 - np.abs(phi) / 2.2, 0, 1)         # mais forte nas costas, mais fraco na barriga
ombro = np.exp(-((pts[mc][:, 1] + 3.6) / 1.6) ** 2)                # reforco nos ombros
L[mc] = li * np.clip(peso + 0.25 * ombro, 0, 1)
S[mc] = s
# patas: linhas descendo (angulo em volta do eixo da perna), metade da forca
s_ombro = proj_polilinha(np.array([h("EscapulaE")]), EIXO_CORPO)[2][0]; s_quadril = proj_polilinha(np.array([h("CoxaE")]), EIXO_CORPO)[2][0]
for nome, poly in PERNAS.items():
    mp = reg == ri[nome]
    if not mp.any(): continue
    c, tg, s = proj_polilinha(pts[mp], poly)
    fora = np.tile([1.0 if nome.endswith("E") else -1.0, 0, 0], (mp.sum(), 1))
    li, _ = linhas_ang(pts[mp], c, tg, fora, [math.radians(a) for a in (0, 90, 180, -90)], LARG * 0.9)
    L[mp] = li * 0.7
    S[mp] = (s_ombro if "F" in nome[5] else s_quadril) + 0.25 * s
# cabeca: rosto limpo; so atras dos olhos (topo da cabeca/nuca) continua a linha do dorso, fraca
mh = reg == ri["Cabeca"]
c, tg, s = proj_polilinha(pts[mh], EIXO_CORPO)
li, phi = linhas_ang(pts[mh], c, tg, np.tile([0, 0, 1.0], (mh.sum(), 1)), [0.0], LARG * 0.8)
atras = np.clip((pts[mh][:, 1] + 4.95) / 0.3, 0, 1)                 # so na nuca, atras das orelhas (rosto limpo)
L[mh] = li * 0.85 * atras; S[mh] = 0
# olhos: perto das palpebras, voltados para a frente
for lado in "ED":
    olho = (h("Palpebra" + lado) + t("Palpebra" + lado)) / 2 + np.array([0, 0.02, -0.08])
    d = np.linalg.norm(pts - olho, axis=1)
    E = np.maximum(E, np.clip(1 - (d - 0.12) / 0.06, 0, 1) * (nrm[:, 1] < 0.3))
# runas (ombro, flanco, coxa; dois lados): glifo de Natureza (haste + ramos + arco) no plano tangente
def seg_d(p, a, b):
    ab = b - a; u = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1); return np.linalg.norm(p - (a + u[:, None] * ab), axis=1)
RUNAS = []
for lado, sx in (("E", 1), ("D", -1)):
    for nome, cen in (("ombro", (1.25 * sx, -3.5, 5.0)), ("flanco", (1.6 * sx, -0.6, 4.4)), ("coxa", (1.25 * sx, 1.15, 3.7))):
        cen = np.array(cen); k = np.argmin(np.linalg.norm(CO - cen, axis=1)); cen = CO[k]; nn = NO[k] / np.linalg.norm(NO[k])
        RUNAS.append((lado + "_" + nome, cen, nn))
TAM = 0.30; LR = 0.04
for nome, cen, nn in RUNAS:
    eu = np.array([0, 1.0, 0]); eu -= (eu @ nn) * nn; eu /= np.linalg.norm(eu); ev = np.cross(nn, eu)
    d3 = pts - cen; perto = (np.linalg.norm(d3, axis=1) < TAM * 1.6) & ((nrm @ nn) > 0.3)
    if not perto.any(): continue
    q = np.stack([d3[perto] @ eu, d3[perto] @ ev], 1) / TAM            # coordenadas do glifo (-1..1)
    dd = np.full(len(q), np.inf)
    for a, b in (((0, -0.85), (0, 0.85)), ((0, 0.1), (-0.55, 0.75)), ((0, 0.1), (0.55, 0.75)), ((0, -0.35), (-0.4, -0.8)), ((0, -0.35), (0.4, -0.8))):
        dd = np.minimum(dd, seg_d(q, np.array(a), np.array(b)))
    ring = np.abs(np.linalg.norm(q, axis=1) - 1.0)
    dd = np.minimum(dd, ring)
    R[np.where(perto)[0]] = np.maximum(R[np.where(perto)[0]], np.clip(1 - (dd * TAM - LR / 2) / 0.02, 0, 1))
    print("RUNA", nome, np.round(cen, 2))

# rosto limpo: zera linhas/runas em qualquer texel que a frente da cabeca tambem use (UV reaproveitado); olhos ficam
rz = ROSTO[idx[:, 0], idx[:, 1]]; L[rz] = 0; R[rz] = 0
E = np.maximum(E, OLHOF[idx[:, 0], idx[:, 1]])
print("texels do rosto zerados", int(rz.sum()))
# ---------------------------------------------------------------- imagem + dilatacao (2 px) para nao abrir costura no UV
img = np.zeros((N, N, 4), np.float32)
img[idx[:, 0], idx[:, 1]] = np.stack([L, R, E, S], 1)
cob = COB.copy()
for _ in range(2):
    viz = np.zeros_like(img); cnt = np.zeros((N, N))
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sh = np.roll(np.roll(img, dy, 0), dx, 1); shc = np.roll(np.roll(cob, dy, 0), dx, 1)
        viz += sh * shc[..., None]; cnt += shc
    novo = (~cob) & (cnt > 0)
    img[novo] = viz[novo] / cnt[novo][:, None]; cob = cob | novo
out8 = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
# preview png
pi = bpy.data.images.new("mascara_uivo", N, N, alpha=True)
prev = out8.astype(np.float32) / 255; prev[..., 3] = 1
pv = prev.copy(); pv[..., 0] = np.maximum(prev[..., 0], prev[..., 2]); pv[..., 1] = np.maximum(prev[..., 0] * 0.8, prev[..., 1]); pv[..., 2] = prev[..., 1]
pi.pixels = pv[::-1].ravel(); pi.filepath_raw = os.path.join(AQUI, "mascara_uivo_preview.png"); pi.file_format = "PNG"; pi.save()
# binario: so texels com L, R ou E > 0. Registro: delta do indice (varint) + L,R,E,S (1 byte cada)
flat = out8.reshape(-1, 4); nz = np.where((flat[:, 0] > 0) | (flat[:, 1] > 0) | (flat[:, 2] > 0))[0]
buf = bytearray(); ant = -1
for i in nz:
    d = int(i - ant); ant = int(i)
    while True:
        b7 = d & 127; d >>= 7
        if d: buf.append(b7 | 128)
        else: buf.append(b7); break
    buf += bytes(flat[i])
open(os.path.join(AQUI, "mascara_uivo.bin"), "wb").write(bytes(buf))
b64 = base64.b64encode(bytes(buf)).decode()
open(os.path.join(AQUI, "mascara_uivo.txt"), "w").write(b64)
info = {"N": N, "texels": int(len(nz)), "bytes": len(buf), "base64": len(b64), "largura_linha_studs": LARG,
        "runas": [r[0] for r in RUNAS], "max": {"L": float(L.max()), "R": float(R.max()), "E": float(E.max())},
        "cobertura_L": float((L > 0.5).mean()), "texels_olho": int((E > 0.5).sum())}
json.dump(info, open(os.path.join(AQUI, "mascara_uivo_info.json"), "w"), indent=1)
print("MASCARA_OK", json.dumps(info))
