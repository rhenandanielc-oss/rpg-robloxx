"""Rodada 2 do complemento: pelagem, marca do ombro e cristais, sobre a m11 (low_ref/, preservada) -> <saida>.
Depois roda-se rosto_v2.py sobre a saida (olhos/palpebras/boca da rodada 1).
- HIGH (Meshy, pose neutra) so para o bake: pontas de mecha suavizadas (mais forte sobre a marca, que era um "tubo"),
  relevo de fios finos no mapa de normal, placas azuis do dorso -> pelo gelado claro, tinta ciano grossa da marca -> pelo,
  espiral fina propria (tex/marca_mascara.png) so no ombro ESQUERDO, com emissao contida.
- LOW: pontas agudas suavizadas (fora do rosto e da costura), pernas com mais volume de pelo (pes no chao intactos),
  bake 2048 -> 1024 com as UVs atuais (o rosto da rodada 1 continua valido) e preenchimento dos pixels pretos de falha.
- LOW_Pelagem: cartoes de mechas com alpha so na silhueta (pernas, franja da barriga, peito, cauda); atlas 1024.
- LOW_Cristais: 4+1 cristais lapidados novos, com UV e textura de veios (512, alpha), presos ao dorso por raio.
Uso: blender -b low_ref/CR_LoboArtico_LOW.blend -P pelagem_r2.py -- <saida_dir> [res]"""
import bpy, bmesh, sys, os, math, json, random, shutil
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
a_ = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a_[0]); RES = int(a_[1]) if len(a_) > 1 else 2048; FINAL = 1024
os.makedirs(os.path.join(OUT, "bake%d" % RES), exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); AQUI = os.path.dirname(SRC); rnd = random.Random(21)
sc = bpy.context.scene; Z = V((0, 0, 1))
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
cab, corpo = bpy.data.objects["LOW_Cabeca"], bpy.data.objects["LOW_Corpo"]
COST_P, COST_N = V((0, -4.55, 4.90)), V((0, -1.0, 0.9)).normalized()
def perto_costura(p): return abs((p - COST_P).dot(COST_N)) < 0.15

# ------------------------------------------------------------------ HIGH (anexado so para o bake)
NEU = os.path.join(AQUI, "meshy", "CR_LoboArtico_meshy_neutro.blend")
bpy.ops.wm.append(filepath=NEU + "/Object/CR_LoboArtico_Meshy", directory=NEU + "/Object/", filename="CR_LoboArtico_Meshy")
hi = bpy.data.objects["CR_LoboArtico_Meshy"]; me = hi.data
nt = me.materials[0].node_tree; L = nt.links; bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
tcor = next(l.from_node for l in L if l.to_node == bsdf and l.to_socket.name == "Base Color")
nmap = next(l.from_node for l in L if l.to_node == bsdf and l.to_socket.name == "Normal")
img = tcor.image; W_, H_ = img.size; px = np.empty(W_ * H_ * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(H_, W_, 4)
nl = len(me.loops); uv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
vi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", vi)
co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
rgb = px[np.clip((uv[:, 1] % 1) * H_, 0, H_ - 1).astype(int), np.clip((uv[:, 0] % 1) * W_, 0, W_ - 1).astype(int), :3]
mx_, mn_ = rgb.max(1), rgb.min(1); sat = (mx_ - mn_) / np.maximum(mx_, 1e-3)
ciano = (sat > 0.28) & (rgb[:, 1] > rgb[:, 0] + 0.10) & (rgb[:, 2] > rgb[:, 0] + 0.10)
lo, hi_ = co.min(0), co.max(0); Lc = hi_[1] - lo[1]
P_ = co[vi[ciano]]; reg_m = (P_[:, 1] > lo[1] + 0.22 * Lc) & (P_[:, 1] < lo[1] + 0.60 * Lc) & (P_[:, 2] > 2.5)
esq, dir_ = P_[reg_m & (P_[:, 0] > 0.35)], P_[reg_m & (P_[:, 0] < -0.25)]
CX = float(np.median(co[(co[:, 1] > lo[1] + 0.4 * Lc) & (co[:, 1] < lo[1] + 0.6 * Lc)][:, 0]))
MC = V(np.median(esq, 0).tolist()) if len(esq) else V((1.1, -2.3, 5.1)); TAM = 2.0
CAIXAS = [(np.percentile(q, 3, 0) - 0.15, np.percentile(q, 97, 0) + 0.15) for q in (esq, dir_) if len(q) > 50]
print("R2 marca: centro esq", tuple(round(c, 2) for c in MC), "caixas", len(CAIXAS), "cx %.3f" % CX, flush=True)
del px, rgb, uv, vi
# suavizacao das pontas de mecha (peso 0,5 em tudo; 1 nas caixas da marca: o relevo de "tubo" some)
vg = hi.vertex_groups.new(name="suave"); vg.add(list(range(len(me.vertices))), 0.5, "REPLACE")
na_caixa = np.zeros(len(co), bool)
for c0, c1 in CAIXAS: na_caixa |= np.all((co >= c0) & (co <= c1), 1)
vg.add(np.nonzero(na_caixa)[0].tolist(), 1.0, "REPLACE")
vgm = hi.vertex_groups.new(name="marca"); vgm.add(np.nonzero(na_caixa)[0].tolist(), 1.0, "REPLACE")
for nome, grp, it in (("S1", "suave", 4), ("S2", "marca", 10)):
    sm = hi.modifiers.new(nome, "SMOOTH"); sm.factor = 0.5; sm.iterations = it; sm.vertex_group = grp
del co
# ---------------- nos do material do HIGH (cor/emissao/normal assados)
def no(t, **kw):
    x = nt.nodes.new(t)
    for k, v in kw.items(): setattr(x, k, v)
    return x
def mr(ent, a, b, c=0.0, d=1.0):
    x = no("ShaderNodeMapRange"); x.inputs[1].default_value = a; x.inputs[2].default_value = b
    x.inputs[3].default_value = c; x.inputs[4].default_value = d; L.new(ent, x.inputs[0]); return x.outputs[0]
def op(o_, a, b=None, v=None):
    x = no("ShaderNodeMath", operation=o_); L.new(a, x.inputs[0])
    if b is not None: L.new(b, x.inputs[1])
    if v is not None: x.inputs[1].default_value = v
    return x.outputs[0]
def faixa(ent, a0, a1, b0, b1): return op("MULTIPLY", mr(ent, a0, a1), mr(ent, b1, b0))
def mix(fac, a, b):
    x = no("ShaderNodeMix", data_type="RGBA"); L.new(fac, x.inputs["Factor"])
    for i, c in ((6, a), (7, b)):
        if isinstance(c, tuple): x.inputs[i].default_value = c
        else: L.new(c, x.inputs[i])
    return x.outputs[2]
tc = no("ShaderNodeTexCoord"); sp = no("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sp.inputs[0])
hsv = no("ShaderNodeSeparateColor", mode="HSV"); L.new(tcor.outputs["Color"], hsv.inputs[0])
satm = mr(hsv.outputs[1], 0.18, 0.32)
cianom = op("MULTIPLY", faixa(hsv.outputs[0], 0.42, 0.46, 0.60, 0.66), satm)
caixa = None
for c0, c1 in CAIXAS:
    f = op("MULTIPLY", op("MULTIPLY", faixa(sp.outputs["X"], c0[0] - .1, c0[0], c1[0], c1[0] + .1), faixa(sp.outputs["Y"], c0[1] - .1, c0[1], c1[1], c1[1] + .1)),
           faixa(sp.outputs["Z"], c0[2] - .1, c0[2], c1[2], c1[2] + .1))
    caixa = f if caixa is None else op("MAXIMUM", caixa, f)
cor = mix(op("MULTIPLY", op("MULTIPLY", cianom, caixa), v=0.9), tcor.outputs["Color"], (0.84, 0.86, 0.89, 1))          # tinta grossa da marca -> pelo
dorso = op("MULTIPLY", op("MULTIPLY", mr(sp.outputs["Z"], 5.7, 6.1), mr(op("ABSOLUTE", op("SUBTRACT", sp.outputs["X"], v=CX)), 0.8, 0.5)),
           faixa(sp.outputs["Y"], -4.4, -4.0, 1.4, 1.8))
azul = op("MULTIPLY", faixa(hsv.outputs[0], 0.50, 0.54, 0.66, 0.72), mr(hsv.outputs[1], 0.10, 0.25))
cor = mix(op("MULTIPLY", op("MULTIPLY", azul, dorso), v=0.65), cor, (0.80, 0.86, 0.92, 1))                         # placas do dorso -> pelo gelado
# espiral fina propria, projetada no lado esquerdo (y,z), centrada no centro da marca do Meshy
mu = mr(sp.outputs["Y"], MC.y - TAM / 2, MC.y + TAM / 2); mv = mr(sp.outputs["Z"], MC.z - TAM / 2, MC.z + TAM / 2)
cxy = no("ShaderNodeCombineXYZ"); L.new(mu, cxy.inputs[0]); L.new(mv, cxy.inputs[1])
mim = bpy.data.images.load(os.path.join(AQUI, "tex", "marca_mascara_v3.png")); MW = mim.size[0]       # desenho v3 (marca_v3.py)
ma = np.empty(MW * MW * 4, np.float32); mim.pixels.foreach_get(ma); ma = ma.reshape(MW, MW, 4)
r_ = ma[..., 0].copy()
for _ in range(2):                                                     # linhas um pouco mais grossas (legiveis na distancia de jogo)
    r_ = np.maximum.reduce([r_, np.roll(r_, 1, 0), np.roll(r_, -1, 0), np.roll(r_, 1, 1), np.roll(r_, -1, 1)])
g_ = r_.copy()
for _ in range(10): g_ = (g_ + np.roll(g_, 2, 0) + np.roll(g_, -2, 0) + np.roll(g_, 2, 1) + np.roll(g_, -2, 1)) / 5
ma[..., 0] = r_; ma[..., 1] = np.clip(g_ * 1.8, 0, 1)
mg = bpy.data.images.new("marca_grossa", MW, MW, alpha=True); mg.pixels.foreach_set(ma.ravel())
mg.filepath_raw = os.path.join(OUT, "marca_mascara_grossa.png"); mg.file_format = "PNG"; mg.save()   # o bake le do arquivo
bpy.data.images.remove(mg); mg = bpy.data.images.load(os.path.join(OUT, "marca_mascara_grossa.png")); mg.colorspace_settings.name = "Non-Color"
tm = no("ShaderNodeTexImage", extension="CLIP"); tm.image = mg; L.new(cxy.outputs[0], tm.inputs[0])
sm_ = no("ShaderNodeSeparateColor"); L.new(tm.outputs["Color"], sm_.inputs[0])
lado = mr(sp.outputs["X"], CX + 0.30, CX + 0.55)
linha = op("MULTIPLY", sm_.outputs[0], lado); halo = op("MULTIPLY", sm_.outputs[1], lado)
cor = mix(op("MULTIPLY", halo, v=0.22), cor, (0.70, 0.88, 0.98, 1))                 # so o halo: as linhas vao no decalque
escuro = op("MULTIPLY", op("MULTIPLY", mr(hsv.outputs[2], 0.42, 0.22), mr(sp.outputs["Y"], -5.75, -5.55)), mr(sp.outputs["Z"], 0.30, 0.45))
cor = mix(op("MULTIPLY", escuro, v=0.85), cor, (0.74, 0.77, 0.81, 1))
L.new(cor, bsdf.inputs["Base Color"])
bsdf.inputs["Emission Color"].default_value = (0.30, 0.90, 1.0, 1)
L.new(op("MULTIPLY", halo, v=0.06), bsdf.inputs["Emission Strength"])
# fios finos no relevo: ruido esticado no sentido do pelo (Y no tronco, Z nas pernas)
mt = no("ShaderNodeMapping"); mt.inputs["Scale"].default_value = (70, 9, 70); L.new(tc.outputs["Object"], mt.inputs[0])
mp = no("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (70, 70, 9); L.new(tc.outputs["Object"], mp.inputs[0])
nt1, nt2 = no("ShaderNodeTexNoise"), no("ShaderNodeTexNoise")
for t_, m_ in ((nt1, mt), (nt2, mp)): t_.inputs["Scale"].default_value = 1.0; t_.inputs["Detail"].default_value = 4; L.new(m_.outputs[0], t_.inputs["Vector"])
fx = no("ShaderNodeMix", data_type="FLOAT"); L.new(mr(sp.outputs["Z"], 3.4, 2.8), fx.inputs["Factor"]); L.new(nt1.outputs["Fac"], fx.inputs[2]); L.new(nt2.outputs["Fac"], fx.inputs[3])
bp = no("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.30; bp.inputs["Distance"].default_value = 0.004
L.new(fx.outputs[0], bp.inputs["Height"]); L.new(nmap.outputs["Normal"], bp.inputs["Normal"]); L.new(bp.outputs["Normal"], bsdf.inputs["Normal"])

# ------------------------------------------------------------------ LOW: pontas agudas suavizadas e pernas com volume
def espinhos(o, filtro):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); bm.normal_update()
    alvo = []
    for v in bm.verts:
        if v.is_boundary or not filtro(v.co) or len(v.link_edges) < 3: continue
        viz = [e.other_vert(v) for e in v.link_edges]; m = sum((w.normal for w in viz), V()).normalized()
        if v.normal.dot(m) < math.cos(math.radians(45)): alvo.append(v)
    for _ in range(2): bmesh.ops.smooth_vert(bm, verts=alvo, factor=0.6, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.to_mesh(o.data); bm.free(); return len(alvo)
def suavizar(o, filtro, it, fator):
    bm = bmesh.new(); bm.from_mesh(o.data); vs = [v for v in bm.verts if not v.is_boundary and filtro(v.co)]
    for _ in range(it): bmesh.ops.smooth_vert(bm, verts=vs, factor=fator, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.to_mesh(o.data); bm.free(); return len(vs)
def na_marca(p): return any(all(c0[i] - 0.1 <= p[i] <= c1[i] + 0.1 for i in range(3)) for c0, c1 in CAIXAS)
ns = suavizar(corpo, lambda p: not perto_costura(p) and p.z > 0.45, 3, 0.35)
ns += suavizar(cab, lambda p: not perto_costura(p) and p.y > -5.30, 3, 0.35)
nm_ = suavizar(corpo, lambda p: na_marca(p) and not perto_costura(p), 8, 0.6)
nm_ += suavizar(corpo, lambda p: na_marca(p) and p.x < CX and not perto_costura(p), 10, 0.6)   # relevo do lado direito
print("R2 LOW: suavizacao geral", ns, "| marca achatada", nm_, flush=True)
n1 = espinhos(corpo, lambda p: not perto_costura(p))
n2 = espinhos(cab, lambda p: not perto_costura(p) and p.y > -5.30)           # rosto fica para a rodada 1/3
bm = bmesh.new(); bm.from_mesh(corpo.data); bm.normal_update(); inflados = 0
for v in bm.verts:
    z = v.co.z
    if v.is_boundary or z > 3.1 or z < 0.28 or abs(v.co.x - CX) < 0.22 or perto_costura(v.co): continue
    k = 0.055 * suave((z - 0.28) / 0.45) * (1 - suave((z - 2.5) / 0.6))
    if k > 0: v.co += v.normal * k; inflados += 1
bm.to_mesh(corpo.data); bm.free()
print("R2 LOW: pontas suavizadas corpo", n1, "cabeca", n2, "| pernas infladas", inflados, flush=True)

# ------------------------------------------------------------------ bake (UVs atuais) e preenchimento de falhas
MAPAS = (("cor", "DIFFUSE"), ("normal", "NORMAL"), ("rugosidade", "ROUGHNESS"), ("emissao", "EMIT"))
sc.render.engine = "CYCLES"; sc.cycles.samples = 8
try:
    pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "CUDA"; pr.get_devices(); sc.cycles.device = "GPU"
except Exception as e: print("sem GPU:", e)
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.14; bk.max_ray_distance = 0.55; bk.margin = 10
bk.use_pass_direct = bk.use_pass_indirect = False; bk.use_pass_color = True
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o not in (hi, cab, corpo)
def preencher(arr, ruim, it=6):
    """troca pixels de falha (preto absoluto) pela media dos vizinhos validos (filtro de caixa 5x5, iterado)"""
    for _ in range(it):
        if not ruim.any(): break
        val = (~ruim).astype(np.float32); acc = arr[..., :3] * val[..., None]
        def caixa(x):
            c = np.cumsum(np.cumsum(np.pad(x, ((3, 2), (3, 2)) + ((0, 0),) * (x.ndim - 2)), 0), 1)
            return c[5:, 5:] - c[:-5, 5:] - c[5:, :-5] + c[:-5, :-5]
        s = caixa(acc); w = caixa(val)
        ok = ruim & (w > 0.5); arr[ok, :3] = s[ok] / w[ok][:, None]; ruim = ruim & ~ok
    return arr
def assar(o, pref):
    mat = o.data.materials[0]; nt_ = mat.node_tree
    tex = {n.image.name.split("_")[-1]: n for n in nt_.nodes if n.type == "TEX_IMAGE"}
    bpy.ops.object.select_all(action="DESELECT"); hi.select_set(True); o.select_set(True); bpy.context.view_layer.objects.active = o
    for k, tipo in MAPAS:
        n_ = tex[k]; velho = n_.image; nome = velho.name
        im = bpy.data.images.new(nome + "_novo", RES, RES, alpha=False)
        im.colorspace_settings.name = "sRGB" if k in ("cor", "emissao") else "Non-Color"; n_.image = im
        bpy.data.images.remove(velho); im.name = nome
        for x in nt_.nodes: x.select = False
        n_.select = True; nt_.nodes.active = n_
        bpy.ops.object.bake(type=tipo, **({"pass_filter": {"COLOR"}} if tipo == "DIFFUSE" else {}))
        arr = np.empty(RES * RES * 4, np.float32); im.pixels.foreach_get(arr); arr = arr.reshape(RES, RES, 4)
        ruim = arr[..., :3].sum(-1) < 0.003 if k != "emissao" else np.zeros((RES, RES), bool)
        if k == "normal": ruim = (np.abs(arr[..., :3] - 0.5).sum(-1) > 1.2) | (arr[..., :3].sum(-1) < 0.003)
        nruim = int(ruim.sum()); arr = preencher(arr, ruim); im.pixels.foreach_set(arr.ravel())
        im.filepath_raw = os.path.join(OUT, "bake%d" % RES, "LoboArtico_%s_%s_%d.png" % (pref, k, RES)); im.file_format = "PNG"; im.save()
        im.scale(FINAL, FINAL); im.filepath_raw = os.path.join(OUT, "LoboArtico_%s_%s.png" % (pref, k)); im.save()
        print("BAKE", pref, k, "pixels de falha preenchidos", nruim, flush=True)
assar(corpo, "Corpo"); assar(cab, "Cabeca")

# ------------------------------------------------------------------ cartoes de mecha (silhueta)
shutil.copy(os.path.join(AQUI, "tex", "pelo_atlas.png"), os.path.join(OUT, "LoboArtico_pelo_atlas.png"))
cbm = bmesh.new(); uvc = cbm.loops.layers.uv.new("UVMap"); NC = 0
def cartao(c, nrm, t1, L_, W_c, inc, col):
    global NC
    t1 = (t1 - nrm * t1.dot(nrm)).normalized(); t2 = nrm.cross(t1).normalized()
    t1 = (t1 * math.cos(inc) + nrm * math.sin(inc)).normalized(); g = rnd.uniform(-0.2, 0.2); t1 = (t1 + t2 * g).normalized(); t2 = nrm.cross(t1).normalized()
    raiz = c - nrm * 0.02; ponta = raiz + t1 * L_
    if ponta.z < 0.04: return
    u0, u1 = col * 0.25 + 0.012, col * 0.25 + 0.238; fil = []
    for j in range(3):
        t = j / 2; e = raiz + t1 * L_ * t - nrm * (L_ * math.sin(inc) * 0.5) * t * t; w = W_c * (1 - 0.2 * t)
        fil.append(([cbm.verts.new(e - t2 * w / 2), cbm.verts.new(e + t2 * w / 2)], t))
    for (a, ta), (b, tb) in zip(fil, fil[1:]):
        f = cbm.faces.new((a[0], a[1], b[1], b[0]))
        for l_, q in zip(f.loops, ((u0, ta), (u1, ta), (u1, tb), (u0, tb))): l_[uvc].uv = q
    NC += 1
for o in (corpo, cab):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median(); n = f.normal; x, y, z = c; ax = abs(x - CX)
        if perto_costura(c) or c.z < 0.35: continue
        if o is cab:
            if not (y > -5.75 and ax > 0.50 and z < 6.3 and n.dot(V((math.copysign(1, x - CX), 0, 0))) > 0.3): continue   # colar das bochechas
            dens, L_, Wc, inc, fl = 14, rnd.uniform(0.30, 0.50), 0.16, 0.30, V((0, 0.6, -0.8))
        elif y > 3.0 and z < 5.0:                                       # cauda: franja
            dens, L_, Wc, inc, fl = 10, rnd.uniform(0.55, 0.95), 0.26, 0.40, V((0, 0.25, -1))
        elif z < 3.1 and ax > 0.22:                                     # pernas: penugem em volta, franja atras
            atras = n.y > 0.3
            dens, L_, Wc, inc, fl = (16 if atras else 9), rnd.uniform(0.18, 0.34), 0.13, 0.25, V((0, 0.15, -1))
        elif n.z < -0.45 and 3.0 < z < 4.8:                             # franja da barriga
            dens, L_, Wc, inc, fl = 10, rnd.uniform(0.35, 0.60), 0.20, 0.35, V((0, 0.2, -1))
        elif y < -3.4 and 3.0 < z < 5.3 and n.y < -0.3:                 # peito / babador
            dens, L_, Wc, inc, fl = 9, rnd.uniform(0.40, 0.70), 0.22, 0.30, V((0, -0.1, -1))
        elif -4.5 < y < -1.6 and z > 4.2 and abs(n.x) > 0.35 and not na_marca(c) and abs(y + 2.45) + abs(z - 6.6) > 0.9:   # juba lateral
            dens, L_, Wc, inc, fl = 6, rnd.uniform(0.40, 0.70), 0.20, 0.22, V((0, 0.55, -0.85))
        elif -1.6 < y < 2.6 and 3.8 < z < 6.2 and abs(n.x) > 0.45:      # flancos: mechas deitadas que quebram as lascas
            dens, L_, Wc, inc, fl = 3.5, rnd.uniform(0.30, 0.50), 0.18, 0.12, V((0, 1.0, -0.35))
        else: continue
        if rnd.random() > dens * f.calc_area(): continue
        cartao(c, n, fl, L_, Wc, inc, rnd.choice((0, 0, 1)))
    bm.free()
mp_ = bpy.data.meshes.new("LOW_Pelagem"); cbm.to_mesh(mp_); cbm.free()
pel = bpy.data.objects.new("LOW_Pelagem", mp_); sc.collection.objects.link(pel)
mpm = bpy.data.materials.new("M_LoboArtico_Pelagem_LOW")
if mpm.node_tree is None: mpm.use_nodes = True
b2 = mpm.node_tree.nodes["Principled BSDF"]; ta = mpm.node_tree.nodes.new("ShaderNodeTexImage"); ta.image = bpy.data.images.load(os.path.join(OUT, "LoboArtico_pelo_atlas.png"))
mpm.node_tree.links.new(ta.outputs["Color"], b2.inputs["Base Color"]); mpm.node_tree.links.new(ta.outputs["Alpha"], b2.inputs["Alpha"])
b2.inputs["Roughness"].default_value = 0.8; mpm.surface_render_method = "DITHERED"; mpm.use_backface_culling = False
pel.data.materials.append(mpm)
ativo(pel); bpy.ops.object.modifier_add(type="TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=pel.modifiers[-1].name)
print("R2 cartoes", NC, "tris", tris(pel), flush=True)

# ------------------------------------------------------------------ cristais novos (lapidados, com UV e veios)
old = bpy.data.objects.get("LOW_Cristais")
if old: bpy.data.objects.remove(old)
TW = 512; yy, xx = np.mgrid[0:TW, 0:TW] / TW
veio = 0.5 + 0.5 * np.sin(xx * 6.28 * 7 + np.sin(yy * 9 + xx * 4) * 2.2)
corc = np.stack([0.30 + 0.45 * yy, 0.62 + 0.30 * yy, 0.92 + 0.08 * yy], -1) * (0.85 + 0.25 * veio[..., None])
borda = (np.abs(((xx * 7) % 1) - 0.5) > 0.46)                                   # arestas das facetas mais claras
corc[borda] = np.minimum(corc[borda] + 0.25, 1.0)
alfa = 0.55 + 0.25 * yy + 0.15 * borda
imc = bpy.data.images.new("LoboArtico_Cristal_cor", TW, TW, alpha=True)
imc.pixels.foreach_set(np.concatenate([np.clip(corc, 0, 1), np.clip(alfa, 0, 1)[..., None]], -1).astype(np.float32).ravel())
imc.filepath_raw = os.path.join(OUT, "LoboArtico_Cristal_cor.png"); imc.file_format = "PNG"; imc.save()
bmc = bmesh.new(); uvk = bmc.loops.layers.uv.new("UVMap")
bvh_c = BVHTree.FromObject(corpo, bpy.context.evaluated_depsgraph_get())
def cristal(base, direc, alt, r, lados=7):
    z_ = direc.normalized(); x_ = z_.cross(V((1, 0, 0))).normalized() if abs(z_.x) < 0.9 else z_.cross(V((0, 1, 0))).normalized(); y_ = z_.cross(x_)
    perf = ((-0.25, 0.80), (0.0, 1.0), (0.38, 1.04), (0.70, 0.78), (0.86, 0.42))
    jit = [1 + rnd.uniform(-0.14, 0.14) for _ in range(lados)]
    aneis = [[bmc.verts.new(base + z_ * (h * alt) + (x_ * math.cos(2 * math.pi * i / lados + 0.2) + y_ * math.sin(2 * math.pi * i / lados + 0.2) * 0.8) * r * rf * jit[i])
              for i in range(lados)] for h, rf in perf]
    topo = bmc.verts.new(base + z_ * alt + x_ * r * 0.10)
    for k in range(len(perf) - 1):
        for i in range(lados):
            i2 = (i + 1) % lados; f = bmc.faces.new((aneis[k][i], aneis[k][i2], aneis[k + 1][i2], aneis[k + 1][i]))
            for l_, q in zip(f.loops, ((i / lados, k / 5), ((i + 1) / lados, k / 5), ((i + 1) / lados, (k + 1) / 5), (i / lados, (k + 1) / 5))): l_[uvk].uv = q
    for i in range(lados):
        f = bmc.faces.new((aneis[-1][i], aneis[-1][(i + 1) % lados], topo))
        for l_, q in zip(f.loops, ((i / lados, 0.8), ((i + 1) / lados, 0.8), ((i + 0.5) / lados, 1.0))): l_[uvk].uv = q
    fb = bmc.faces.new(aneis[0][::-1])
    for l_ in fb.loops: l_[uvk].uv = (0.5, 0.02)
# referencia: 4 cristais em fileira logo atras da crista da juba, diminuindo para tras, inclinados para tras; 1 pequeno a direita [PROPOSTA]
for (y, dx, alt, r, inc, lat) in ((-2.95, 0.10, 0.88, 0.26, 0.60, 0.22), (-2.58, 0.18, 0.74, 0.23, 0.68, 0.30),
                                  (-2.24, 0.10, 0.60, 0.20, 0.76, 0.22), (-1.94, 0.16, 0.46, 0.16, 0.84, 0.30), (-2.45, -0.18, 0.40, 0.14, 0.72, -0.35)):
    loc, nr, i, d = bvh_c.ray_cast(V((CX + dx, y, 12.0)), V((0, 0, -1)), 20)
    if loc is None: continue
    cristal(loc - V((0, 0, 0.16)), V((lat, inc, 1.0)), alt, r)
mc = bpy.data.meshes.new("LOW_Cristais"); bmc.to_mesh(mc); bmc.free()
cr = bpy.data.objects.new("LOW_Cristais", mc); sc.collection.objects.link(cr)
for p in mc.polygons: p.use_smooth = False
mcm = bpy.data.materials.new("M_LoboArtico_Cristal")
if mcm.node_tree is None: mcm.use_nodes = True
b3 = mcm.node_tree.nodes["Principled BSDF"]; tk = mcm.node_tree.nodes.new("ShaderNodeTexImage"); tk.image = imc
mcm.node_tree.links.new(tk.outputs["Color"], b3.inputs["Base Color"]); mcm.node_tree.links.new(tk.outputs["Alpha"], b3.inputs["Alpha"])
b3.inputs["Roughness"].default_value = 0.08; b3.inputs["Emission Color"].default_value = (0.40, 0.80, 1.0, 1); b3.inputs["Emission Strength"].default_value = 0.20
if "Coat Weight" in b3.inputs: b3.inputs["Coat Weight"].default_value = 0.5
mcm.surface_render_method = "BLENDED"; mcm.use_backface_culling = False; cr.data.materials.append(mcm)
ativo(cr); bpy.ops.object.modifier_add(type="TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=cr.modifiers[-1].name)
print("R2 cristais tris", tris(cr), flush=True)

# ------------------------------------------------------------------ decalque da marca (nitida, independe da textura do corpo)
DW = 512; md = np.asarray(ma)                                            # mascara engrossada (R linhas, G halo) em MW x MW
from math import floor
ys_, xs_ = np.mgrid[0:DW, 0:DW] * (MW / DW); md = md[ys_.astype(int), xs_.astype(int)]
lin_, hal_ = md[..., 0], md[..., 1]
dcor = np.stack([0.30 + 0.30 * lin_, 0.80 + 0.15 * lin_, np.ones_like(lin_)], -1)
dalfa = np.clip(lin_ * 1.0 + hal_ * 0.35, 0, 1)
imd = bpy.data.images.new("LoboArtico_Marca_cor", DW, DW, alpha=True)
imd.pixels.foreach_set(np.concatenate([dcor, dalfa[..., None]], -1).astype(np.float32).ravel())
imd.filepath_raw = os.path.join(OUT, "LoboArtico_Marca_cor.png"); imd.file_format = "PNG"; imd.save()
bvh_m = BVHTree.FromObject(corpo, bpy.context.evaluated_depsgraph_get()); NG = 26
grade = [[None] * (NG + 1) for _ in range(NG + 1)]; bmd = bmesh.new(); uvd = bmd.loops.layers.uv.new("UVMap")
for j in range(NG + 1):
    for i in range(NG + 1):
        y = MC.y - TAM / 2 + TAM * i / NG; z = MC.z - TAM / 2 + TAM * j / NG
        loc, nr, k_, d = bvh_m.ray_cast(V((CX + 3.0, y, z)), V((-1, 0, 0)), 4.0)
        if loc is not None and nr.x > 0.15: grade[j][i] = (bmd.verts.new(loc + nr * 0.012), (i / NG, j / NG))
for j in range(NG):
    for i in range(NG):
        q = (grade[j][i], grade[j][i + 1], grade[j + 1][i + 1], grade[j + 1][i])
        if all(q):
            f = bmd.faces.new([x[0] for x in q])
            for l_, x in zip(f.loops, q): l_[uvd].uv = x[1]
md_ = bpy.data.meshes.new("LOW_Marca"); bmd.to_mesh(md_); bmd.free()
marca = bpy.data.objects.new("LOW_Marca", md_); sc.collection.objects.link(marca)
mmk = bpy.data.materials.new("M_LoboArtico_Marca")
if mmk.node_tree is None: mmk.use_nodes = True
b4 = mmk.node_tree.nodes["Principled BSDF"]; tdk = mmk.node_tree.nodes.new("ShaderNodeTexImage"); tdk.image = imd
mmk.node_tree.links.new(tdk.outputs["Color"], b4.inputs["Base Color"]); mmk.node_tree.links.new(tdk.outputs["Alpha"], b4.inputs["Alpha"])
mmk.node_tree.links.new(tdk.outputs["Color"], b4.inputs["Emission Color"]); b4.inputs["Emission Strength"].default_value = 1.4
b4.inputs["Roughness"].default_value = 0.5; mmk.surface_render_method = "BLENDED"; mmk.use_backface_culling = True
marca.data.materials.append(mmk)
for p_ in md_.polygons: p_.use_smooth = True
ativo(marca); bpy.ops.object.modifier_add(type="TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=marca.modifiers[-1].name)
print("R2 decalque da marca tris", tris(marca), flush=True)
bmd = bmesh.new(); uvd = bmd.loops.layers.uv.new("UVMap"); grade = [[None] * (NG + 1) for _ in range(NG + 1)]
for j in range(NG + 1):
    for i in range(NG + 1):
        y = MC.y - TAM / 2 + TAM * i / NG; z = MC.z - TAM / 2 + TAM * j / NG
        loc, nr, k_, d = bvh_m.ray_cast(V((CX - 3.0, y, z)), V((1, 0, 0)), 4.0)
        if loc is not None and nr.x < -0.15: grade[j][i] = (bmd.verts.new(loc + nr * 0.012), (i / NG, j / NG))
for j in range(NG):
    for i in range(NG):
        q = (grade[j][i], grade[j][i + 1], grade[j + 1][i + 1], grade[j + 1][i])
        if all(q):
            f = bmd.faces.new([x[0] for x in q][::-1])
            for l_, x in zip(f.loops, q[::-1]): l_[uvd].uv = x[1]
mdb = bpy.data.meshes.new("OPCAO_Marca_Direita"); bmd.to_mesh(mdb); bmd.free()
ob_b = bpy.data.objects.new("OPCAO_Marca_Direita", mdb); sc.collection.objects.link(ob_b); ob_b.data.materials.append(mmk)
ob_b.hide_render = True; ob_b.hide_set(True)
print("R2 opcao B (marca direita, oculta e fora do export) tris", len(mdb.polygons) * 2, flush=True)

# ------------------------------------------------------------------ LODs do corpo/pelagem e saida
def lod(o, alvo, nome):
    old = bpy.data.objects.get(nome)
    if old: bpy.data.objects.remove(old)
    c = o.copy(); c.data = o.data.copy(); c.name = c.data.name = nome; sc.collection.objects.link(c)
    ativo(c); d = c.modifiers.new("D", "DECIMATE"); d.ratio = min(1.0, alvo / max(tris(c), 1)); bpy.ops.object.modifier_apply(modifier="D"); c.hide_render = True; return c
lod(corpo, 6500, "LOD1_Corpo"); lod(corpo, 2000, "LOD2_Corpo")
p1 = pel.copy(); p1.data = pel.data.copy(); p1.name = p1.data.name = "LOD1_Pelagem"; sc.collection.objects.link(p1)
bm = bmesh.new(); bm.from_mesh(p1.data); bm.faces.ensure_lookup_table()
apagar = [f for i, f in enumerate(bm.faces) if (i // 4) % 2 == 1]                  # LOD1: metade dos cartoes (4 tris por cartao)
bmesh.ops.delete(bm, geom=apagar, context="FACES"); bm.to_mesh(p1.data); bm.free(); p1.hide_render = True
bpy.data.objects.remove(hi)
reg = {o.name: tris(o) for o in sc.objects if o.type == "MESH"}
json.dump(reg, open(os.path.join(OUT, "custo_r2.json"), "w"), indent=1); print("R2_TRIS", reg, flush=True)
shutil.copy(os.path.join(SRC, "rig_pivos.json"), os.path.join(OUT, "rig_pivos.json"))
for im in bpy.data.images:
    if im.filepath and not os.path.exists(bpy.path.abspath(im.filepath)): pass
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend"))
print("R2_OK")
