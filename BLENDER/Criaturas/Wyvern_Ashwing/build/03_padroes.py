# E3 - visual do jogo + 3 padroes oficiais (RPG_02: Verde Musgo, Marrom Rochoso, Cinza Acinzentado).
# Paleta guiada pelo painel 04 Wyvern (REFERENCES/03_CREATURES/02-dragoes-wyvern.png): escamas oliva/musgo,
# membrana caqui com manchas escuras, ferrao escuro com ponta verde de veneno.
# Recolore o albedo do Ashwing por MAPA DE GRADIENTE (preserva o relevo/luminancia da textura original),
# com mascaras por regiao rasterizadas na UV (membrana / corpo / ferrao) e manchas por ruido 3D (sem costura).
# Uso: blender -b Wyvern_E2.blend -P 03_padroes.py -- <saida.blend> <pasta texturas>
import bpy, sys, os, json, math
import numpy as np
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, TEX = argv[0], argv[1]; os.makedirs(TEX, exist_ok=True)
mesh = bpy.data.objects["Wyvern"]; me = mesh.data
mat = me.materials[0]
nt = mat.node_tree
bsdf = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"][0]
nodo_cor = bsdf.inputs["Base Color"].links[0].from_node
img = nodo_cor.image
W, H = img.size
src = np.empty(W * H * 4, dtype=np.float32); img.pixels.foreach_get(src); src = src.reshape(H, W, 4)

# ---------- rasterizacao na UV: regiao e posicao 3D por texel
reg = np.zeros((H, W), dtype=np.uint8)            # 0 corpo, 1 asa (candidata a membrana), 2 ferrao
pos = np.zeros((H, W, 3), dtype=np.float32)
dist = np.zeros((H, W), dtype=np.float32)          # ferrao: 0 no bulbo -> 1 na ponta
asa = {g.index for g in mesh.vertex_groups if any(k in g.name for k in ("strut", "finger", "thumb", "hand", "forearm"))}
g10 = mesh.vertex_groups["tail_10"].index
def dom(v):
    gs = sorted(v.groups, key=lambda g: -g.weight); return (gs[0].group, gs[0].weight) if gs else (-1, 0)
dv = [dom(v) for v in me.vertices]
co = np.array([v.co[:] for v in me.vertices], dtype=np.float32)
ponta_ids = [i for i, (g, w) in enumerate(dv) if g == g10 and w > 0.99]
ponta = co[ponta_ids]
# bulbo = vertice da ponta mais proximo da base; ponta = mais distante
base = ponta[np.argmin(ponta[:, 1] - ponta[:, 2])] if len(ponta) else np.zeros(3)
dmax = float(np.max(np.linalg.norm(ponta - base, axis=1))) if len(ponta) else 1.0
uvl = me.uv_layers.active.data
me.calc_loop_triangles()
for tri in me.loop_triangles:
    uv = np.array([uvl[l].uv[:] for l in tri.loops], dtype=np.float64) * [W, H]
    vs = list(tri.vertices); P = co[vs]
    gs = [dv[i][0] for i in vs]
    if all(g == g10 and dv[i][1] > 0.99 for g, i in zip(gs, vs)): r = 2
    elif sum(g in asa for g in gs) >= 2: r = 1
    else: r = 0
    x0, y0 = np.floor(uv.min(0)).astype(int); x1, y1 = np.ceil(uv.max(0)).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W - 1), min(y1, H - 1)
    if x1 < x0 or y1 < y0: continue
    xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
    (ax, ay), (bx, by), (cx, cy) = uv
    den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-12: continue
    l1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
    l2 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
    l3 = 1 - l1 - l2
    m = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
    if not m.any(): continue
    p = l1[..., None] * P[0] + l2[..., None] * P[1] + l3[..., None] * P[2]
    sub = (slice(y0, y1 + 1), slice(x0, x1 + 1))
    reg[sub][m] = r; pos[sub][m] = p[m]
    if r == 2: dist[sub][m] = np.clip(np.linalg.norm(p[m] - base, axis=1) / dmax, 0, 1)

# ---------- luminancia normalizada por regiao (preserva escamas e veios)
L = 0.2126 * src[..., 0] + 0.7152 * src[..., 1] + 0.0722 * src[..., 2]
memb = (reg == 1) & (L > np.percentile(L[reg == 1], 35) if (reg == 1).any() else False)
def norm(mask):
    if not mask.any(): return
    lo, hi = np.percentile(L[mask], 2), np.percentile(L[mask], 98)
    Ln[mask] = np.clip((L[mask] - lo) / max(hi - lo, 1e-4), 0, 1)
Ln = np.clip(L / max(np.percentile(L, 98), 1e-4), 0, 1)
corpo = ~memb & (reg != 2)
norm(corpo); norm(memb)

# ---------- ruido 3D (value noise suave) para manchas da membrana e variacao do corpo
def ruido3(p, esc, semente):
    q = p / esc; i = np.floor(q).astype(np.int64); f = q - i; f = f * f * (3 - 2 * f)
    def h(a, b, c):
        n = (a * 73856093) ^ (b * 19349663) ^ (c * 83492791) ^ semente
        n = (n ^ (n >> 13)) * 1274126177
        return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[..., 0] if dx else 1 - f[..., 0]) * (f[..., 1] if dy else 1 - f[..., 1]) * (f[..., 2] if dz else 1 - f[..., 2])
                out = out + w * h(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz)
    return out
def hexc(s): s = s.lstrip("#"); return np.array([int(s[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32) ** 2.2
def rampa(t, cores):
    cs = [hexc(c) for c in cores]; n = len(cs) - 1
    t = np.clip(t, 0, 1) * n; i = np.minimum(t.astype(int), n - 1); f = (t - i)[..., None]
    A = np.stack(cs)[i]; B = np.stack(cs)[i + 1]
    return A * (1 - f) + B * f

PADROES = {
    "Verde_Musgo":      {"corpo": ["#1d2014", "#3b4224", "#5f6a38", "#9a9a62"], "memb": ["#4e5030", "#7d7a48", "#ada46e"], "mancha": "#3c3a22", "veneno": "#9fd23c"},
    "Marrom_Rochoso":   {"corpo": ["#1e1712", "#403124", "#6c5541", "#a8917a"], "memb": ["#5e4a38", "#8f7558", "#bba184"], "mancha": "#3e3024", "veneno": "#9fd23c"},
    "Cinza_Acinzentado": {"corpo": ["#18191a", "#36383a", "#5f6265", "#a3a4a1"], "memb": ["#646463", "#8f8e89", "#bab7ae"], "mancha": "#3d3d3c", "veneno": "#9fd23c"},
}
n_grande = ruido3(pos, 2.2, 11); n_fino = ruido3(pos, 0.7, 29); var = ruido3(pos, 4.0, 47)
manchas = np.clip((0.65 * n_grande + 0.35 * n_fino - 0.52) * 7, 0, 1)
res = {}
for nome, p in PADROES.items():
    out = src.copy()
    rgb = rampa(Ln, p["corpo"]) * (0.9 + 0.2 * var)[..., None]
    mrgb = rampa(Ln, p["memb"])
    mrgb = mrgb * (1 - 0.85 * manchas[..., None]) + hexc(p["mancha"]) * (0.85 * manchas[..., None])
    rgb = np.where(memb[..., None], mrgb, rgb)
    # ferrao: queratina escura no bulbo -> verde de veneno na ponta
    t = np.clip((dist - 0.45) / 0.45, 0, 1)[..., None]
    fer = hexc("#1c1c14") * (0.7 + 0.6 * Ln[..., None]) * (1 - t) + hexc(p["veneno"]) * (0.75 + 0.35 * Ln[..., None]) * t
    rgb = np.where((reg == 2)[..., None], fer, rgb)
    out[..., :3] = np.clip(rgb, 0, 1) ** (1 / 2.2)
    im = bpy.data.images.new("Wyvern_Cor_" + nome, W, H, alpha=True)
    im.pixels.foreach_set(out.ravel())
    im.filepath_raw = os.path.join(TEX, "Wyvern_Cor_" + nome + ".png"); im.file_format = "PNG"; im.save()
    im.pack(); im.use_fake_user = True   # sem usuario o Blender descarta os padroes nao usados ao salvar
    res[nome] = im.name
# padrao padrao no material = Verde Musgo (o do painel); escamas foscas de reptil
nodo_cor.image = bpy.data.images[res["Verde_Musgo"]]
if "Metallic" in bsdf.inputs and not bsdf.inputs["Metallic"].is_linked: bsdf.inputs["Metallic"].default_value = 0.0
mat.name = "Wyvern"
# mascaras de revisao
mk = np.zeros((H, W, 4), dtype=np.float32); mk[..., 3] = 1
mk[..., 0] = (reg == 2); mk[..., 1] = memb; mk[..., 2] = corpo * 0.5
im = bpy.data.images.new("mascaras", W, H); im.pixels.foreach_set(mk.ravel())
im.filepath_raw = os.path.join(TEX, "_revisao_mascaras.png"); im.file_format = "PNG"; im.save()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("RJSON" + json.dumps({"tex": [W, H], "texels_membrana": int(memb.sum()), "texels_ferrao": int((reg == 2).sum()), "padroes": list(res)}) + "RFIM")
