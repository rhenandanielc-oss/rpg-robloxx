"""r2 (20/11): a r1 (roblox_A3/r1_cheia) acendia a REGIAO inteira por igual (corpo laranja/veu marrom no Studio). Agora
so LINGUAS de fogo: ruido 3D pela POSICAO do vertice (continuo nas costuras), esticado na vertical, limiar 0,45..0,72 como
a "lingua" da A3; tinta da cor so nas linguas (k <= 0,55).
Aura A3 no Roblox (20/11): assa a PELE de fogo para a SurfaceAppearance (o Roblox nao anima shader).
Para Cerbero_Corpo e Cerbero_Cabecas (atributo de vertice "fogo" da A3, UV igual ao GLB do rig):
  * T_Cerbero_<malha>_EmissivaMascara.png - cinza: fogo x (0,35 + 0,65 x fios do pelo pela luminancia da textura), mesma
    regra de "fios" da A3 (MapRange 0,012..0,09 da luminancia linear). No Roblox: SurfaceAppearance.EmissiveMaskContent.
  * T_Cerbero_<malha>_Cor_Fogo.png - textura de cor com as areas de fogo tingidas pela rampa da A3 (brasa -> vermelho ->
    laranja -> amarelo so no mais quente). No Roblox a emissao e MULTIPLICADA pelo albedo: pelo preto nao brilharia.
Sem bake do Cycles (recusava o objeto em modo de fundo): o atributo "fogo" e rasterizado nas UVs com numpy (baricentrico
por triangulo) + dilatacao de 6 px nas bordas das ilhas. Leve, so CPU.
Uso: blender -b -t 2 CR_Cerbero_Fogo_A3.blend -P assar_aura_roblox.py -- <saida>"""
import bpy, sys, os
import numpy as np
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
RES = 1024

def lin(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return np.array([(v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c])
RAMPA = [(0.0, lin("5a0a00")), (0.35, lin("c42200")), (0.75, lin("ff6a00")), (1.0, lin("ffe07a"))]
def rampa(v):
    out = np.zeros(v.shape + (3,))
    for (p0, c0), (p1, c1) in zip(RAMPA, RAMPA[1:]):
        k = np.clip((v - p0) / (p1 - p0), 0, 1)[..., None]
        sel = ((v >= p0) & (v <= p1))[..., None]
        out = np.where(sel, c0 + (c1 - c0) * k, out)
    return out
def para_srgb(c):
    c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
def de_srgb(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def rasterizar(o):
    me = o.data; me.calc_loop_triangles()
    uv = me.uv_layers.active.data; fogo = me.attributes["fogo"].data
    val = np.zeros((RES, RES, 4)); cob = np.zeros((RES, RES), bool)
    for tri in me.loop_triangles:
        P = np.array([uv[l].uv[:] for l in tri.loops]) * RES - 0.5
        F = np.array([[fogo[v].value] + list(o.matrix_world @ me.vertices[v].co) for v in tri.vertices])   # fogo + posicao no MUNDO (studs)
        x0, y0 = np.floor(P.min(0)).astype(int); x1, y1 = np.ceil(P.max(0)).astype(int)
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, RES - 1), min(y1, RES - 1)
        if x1 < x0 or y1 < y0: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        (ax, ay), (bx, by), (cx, cy) = P
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12: continue
        w0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        w1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
        w2 = 1 - w0 - w1
        dentro = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
        v = w0[..., None] * F[0] + w1[..., None] * F[1] + w2[..., None] * F[2]
        val[ys[dentro], xs[dentro]] = v[dentro]; cob[ys[dentro], xs[dentro]] = True
    for _ in range(6):                                     # dilatacao: bordas das ilhas sem costura escura
        novo = ~cob; acc = np.zeros_like(val); n = np.zeros((RES, RES))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            vs = np.roll(np.roll(val, dy, 0), dx, 1); cs = np.roll(np.roll(cob, dy, 0), dx, 1)
            acc += np.where(cs[..., None], vs, 0); n += cs
        ok = novo & (n > 0); val[ok] = acc[ok] / n[ok][..., None]; cob |= ok
    return val                                              # linha 0 = v=0 (base da imagem, como o Blender)

def salvar(nome, rgb):
    img = bpy.data.images.new(nome, RES, RES, alpha=False)
    px = np.ones((RES, RES, 4)); px[..., :3] = rgb
    img.pixels.foreach_set(px.ravel().astype(np.float32))
    img.filepath_raw = os.path.join(OUT, nome + ".png"); img.file_format = "PNG"; img.save()
    print("ASSADO", nome, flush=True)

RELATO = {}
for nome in ("Corpo", "Cabecas"):
    o = bpy.data.objects["Cerbero_" + nome]
    cor_img = bpy.data.images["T_Cerbero_%s_Cor" % nome]
    w, h = cor_img.size
    if (w, h) != (RES, RES): raise SystemExit("textura com tamanho inesperado")
    cor = np.array(cor_img.pixels[:], dtype=np.float64).reshape(h, w, 4)[..., :3]
    cor_lin = de_srgb(cor) if cor_img.colorspace_settings.name == "sRGB" else cor
    dados = rasterizar(o); fogo = dados[..., 0]; P = dados[..., 1:]
    # linguas: soma de ondas 3D pela posicao (continua nas costuras), esticada na vertical (z do Blender = altura)
    rng = np.random.default_rng(7); ruido = np.zeros(fogo.shape)
    for k_ in range(9):
        d = rng.normal(size=3); d /= np.linalg.norm(d); f = rng.uniform(8.0, 15.0)   # ~1,3-2,4 ciclos por stud na horizontal (linguas finas como a A3)
        esc = np.array([1.0, 1.0, 0.12])                              # ondas lentas em z -> linguas verticais
        ruido += np.sin((P * esc) @ (d * f) + rng.uniform(0, 6.28)) / 9
    ruido = (ruido - ruido.min()) / (ruido.max() - ruido.min())
    lingua = np.clip((ruido - 0.44) / (0.70 - 0.44), 0, 1)
    lum = cor_lin @ np.array([0.2126, 0.7152, 0.0722])
    fio = np.clip((lum - 0.012) / (0.09 - 0.012), 0, 1)
    placa = np.clip((lum - 0.10) / (0.17 - 0.10), 0, 1)          # placas claras da armadura: atenuadas como na A3 r2
    mascara = np.clip(fogo * (1 - 0.85 * placa) * (0.25 + 0.75 * fio) * lingua * 1.5, 0, 1)
    salvar("T_Cerbero_%s_EmissivaMascara" % nome, np.repeat(mascara[..., None], 3, 2))
    k = np.clip(mascara * 0.75, 0, 0.55)[..., None]
    tinto = cor_lin * (1 - k) + rampa(mascara) * k
    salvar("T_Cerbero_%s_Cor_Fogo" % nome, para_srgb(tinto))
    RELATO[nome] = {"pixels_com_fogo_%": round(float((fogo > 0.05).mean() * 100), 1), "mascara_media": round(float(mascara.mean()), 3)}
print("ASSAR_OK", RELATO, flush=True)
