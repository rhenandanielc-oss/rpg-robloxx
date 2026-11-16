"""Refino da malha de jogo do Lobo Artico (base Meshy em pose neutra) para o rig/animacao:
1. LOW unica (voxel -> decimacao com MAIS densidade na cabeca) cortada num plano escondido na juba em 2 MeshParts
   que dividem a costura (mesmos vertices): LOW_Cabeca e LOW_Corpo, cada uma com UV e mapas 1024 PROPRIOS.
2. Boca: corte dos labios no traco escuro do Meshy (rosto.json) -> mandibula separada do focinho, unidas no canto;
   cavidade (gengiva), lingua e dentes por dentro, nas cores de amostras reservadas da textura da cabeca.
3. Palpebras superiores/inferiores em geometria, ABERTAS no repouso (giram em torno do centro do olho no rig).
4. Cristais translucidos proprios (LOW_Cristais) e brilho da marca so no ombro esquerdo (como low_meshy.py).
Pivos para o rig em rig_pivos.json. LOD1/LOD2, GLB, custo.
Uso: blender -b meshy/CR_LoboArtico_meshy_neutro.blend -P refinar_meshy.py -- <saida_dir> [res]"""
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); RES = int(a[1]) if len(a) > 1 else 2048
FINAL = 1024; AQUI = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(3)
os.makedirs(os.path.join(OUT, "bake%d" % RES), exist_ok=True)
ROSTO = json.load(open(os.path.join(AQUI, "meshy", "rosto.json")))
sc = bpy.context.scene; hi_ob = bpy.data.objects["CR_LoboArtico_Meshy"]; me = hi_ob.data
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
NARIZ = V(ROSTO["nariz"]); BA, BB, CANTO = ROSTO["boca"]["a"], ROSTO["boca"]["b"], ROSTO["boca"]["canto_y"]
def z_boca(y): return BA + BB * y
# plano da costura cabeca/corpo: atras das orelhas e das bochechas, escondido na juba
COST_P, COST_N = V((0, -4.55, 4.90)), V((0, -1.0, 0.9)).normalized()
def lado_cabeca(p): return (p - COST_P).dot(COST_N) > 0

# ------------------------------------------------------------------ marca (brilho so no ombro esquerdo) — igual a low_meshy.py
nt_hi = me.materials[0].node_tree; bsdf_hi = next(n for n in nt_hi.nodes if n.type == "BSDF_PRINCIPLED")
def origem(sock):
    for lk in sock.links:
        n_ = lk.from_node
        if n_.type == "TEX_IMAGE": return n_
        for s in n_.inputs:
            r = origem(s) if s.is_linked else None
            if r: return r
tn = origem(bsdf_hi.inputs["Base Color"]); tex_cor = tn.image; W_, H_ = tex_cor.size
px = np.empty(W_ * H_ * 4, np.float32); tex_cor.pixels.foreach_get(px); px = px.reshape(H_, W_, 4)
nl = len(me.loops); uv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
vi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", vi)
co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
rgb = px[np.clip((uv[:, 1] % 1) * H_, 0, H_ - 1).astype(int), np.clip((uv[:, 0] % 1) * W_, 0, W_ - 1).astype(int), :3]
mx_, mn_ = rgb.max(1), rgb.min(1); sat = (mx_ - mn_) / np.maximum(mx_, 1e-3)
ciano = (sat > 0.28) & (rgb[:, 1] > rgb[:, 0] + 0.10) & (rgb[:, 2] > rgb[:, 0] + 0.10)
lo, hi = co.min(0), co.max(0); L = hi[1] - lo[1]
p_ = co[vi[ciano]]
esq = p_[(p_[:, 0] > 0.35) & (p_[:, 1] > lo[1] + 0.22 * L) & (p_[:, 1] < lo[1] + 0.60 * L) & (p_[:, 2] > 2.5)]
cmin, cmax = np.percentile(esq, 3, axis=0) - 0.12, np.percentile(esq, 97, axis=0) + 0.12
del px, rgb, uv, vi
Ln = nt_hi.links
def no(t, **kw):
    x = nt_hi.nodes.new(t)
    for k, v in kw.items(): setattr(x, k, v)
    return x
def faixa(ent, a0, a1, b0, b1):
    m1 = no("ShaderNodeMapRange"); m1.inputs[1].default_value = a0; m1.inputs[2].default_value = a1; Ln.new(ent, m1.inputs[0])
    m2 = no("ShaderNodeMapRange"); m2.inputs[1].default_value = b1; m2.inputs[2].default_value = b0; Ln.new(ent, m2.inputs[0])
    x = no("ShaderNodeMath", operation="MULTIPLY"); Ln.new(m1.outputs[0], x.inputs[0]); Ln.new(m2.outputs[0], x.inputs[1]); return x.outputs[0]
def mul(a_, b_):
    x = no("ShaderNodeMath", operation="MULTIPLY"); Ln.new(a_, x.inputs[0]); Ln.new(b_, x.inputs[1]); return x.outputs[0]
hsv = no("ShaderNodeSeparateColor", mode="HSV"); Ln.new(tn.outputs["Color"], hsv.inputs[0])
ms = no("ShaderNodeMapRange"); ms.inputs[1].default_value = 0.22; ms.inputs[2].default_value = 0.36; Ln.new(hsv.outputs[1], ms.inputs[0])
tc = no("ShaderNodeTexCoord"); sp = no("ShaderNodeSeparateXYZ"); Ln.new(tc.outputs["Object"], sp.inputs[0])
caixa = mul(mul(faixa(sp.outputs["X"], cmin[0] - .1, cmin[0] + .05, cmax[0] - .05, cmax[0] + .1),
                faixa(sp.outputs["Y"], cmin[1] - .1, cmin[1] + .05, cmax[1] - .05, cmax[1] + .1)),
            faixa(sp.outputs["Z"], cmin[2] - .1, cmin[2] + .05, cmax[2] - .05, cmax[2] + .1))
bsdf_hi.inputs["Emission Color"].default_value = (0.30, 0.92, 1.0, 1)
Ln.new(mul(mul(faixa(hsv.outputs[0], 0.44, 0.47, 0.56, 0.60), ms.outputs[0]), caixa), bsdf_hi.inputs["Emission Strength"])

# ------------------------------------------------------------------ LOW unica com mais densidade na cabeca
dg = bpy.context.evaluated_depsgraph_get()
low = bpy.data.objects.new("LOW_Tudo", bpy.data.meshes.new_from_object(hi_ob.evaluated_get(dg))); sc.collection.objects.link(low)
ativo(low); low.data.materials.clear()
vx = low.modifiers.new("V", "REMESH"); vx.mode = "VOXEL"; vx.voxel_size = 0.03; bpy.ops.object.modifier_apply(modifier="V")
def decimar_regiao(obj, alvo_cab, alvo_corpo):
    """decima cabeca e corpo com razoes diferentes, sem abrir a costura: as faces de cada lado sao decimadas
    separadamente com a borda da costura travada (Decimate com grupo de vertices = 0 na faixa da costura)"""
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=COST_P, plane_no=COST_N)
    bm.to_mesh(obj.data); bm.free()
    for nome, sel, alvo in (("cab", True, alvo_cab), ("corpo", False, alvo_corpo)):
        vg = obj.vertex_groups.new(name=nome)
        ids = [v.index for v in obj.data.vertices if lado_cabeca(v.co) == sel and abs((v.co - COST_P).dot(COST_N)) > 0.06]
        vg.add(ids, 1.0, "REPLACE")
        tot = len(obj.data.polygons); n_lado = sum(1 for p in obj.data.polygons if lado_cabeca(p.center) == sel)
        d = obj.modifiers.new("D_" + nome, "DECIMATE"); d.vertex_group = nome
        d.ratio = max((tot - n_lado + alvo / 2) / tot, 0.001)              # so o grupo decima: o resto entra inteiro na conta
        d.use_symmetry = False
        ativo(obj); bpy.ops.object.modifier_apply(modifier=d.name)
        print("REF decimar", nome, "faces lado", sum(1 for p in obj.data.polygons if lado_cabeca(p.center) == sel), "total", len(obj.data.polygons), flush=True)
decimar_regiao(low, 11000, 14500)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.002); bpy.ops.mesh.dissolve_degenerate(threshold=0.0005); bpy.ops.mesh.delete_loose()
for _ in range(2):
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False, use_multi_face=True, use_non_contiguous=True, use_verts=True)
    bpy.ops.mesh.delete(type="VERT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.fill_holes(sides=12)
bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.quads_convert_to_tris(); bpy.ops.object.mode_set(mode="OBJECT")
for pl in low.data.polygons: pl.use_smooth = True
print("REF low", tris(low), flush=True)

# ------------------------------------------------------------------ boca: corte dos labios
bm = bmesh.new(); bm.from_mesh(low.data); bm.faces.ensure_lookup_table()
b_ = V((0, 1, BB)).normalized(); n_boca = V((0, -BB, 1)).normalized()          # direcao da linha e normal do plano
P0 = V((0, CANTO, z_boca(CANTO)))
reg = [f for f in bm.faces if f.calc_center_median().y < CANTO - 0.02 and abs(f.calc_center_median().z - z_boca(f.calc_center_median().y)) < 0.45
       and abs(f.calc_center_median().x) < 0.9]
geom = list({v for f in reg for v in f.verts}) + list({e for f in reg for e in f.edges}) + reg
res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=P0, plane_no=n_boca)
cortadas = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)
            and all(v.co.y < CANTO - 0.06 for v in e.verts)]
bmesh.ops.split_edges(bm, edges=cortadas)
bm.to_mesh(low.data); bm.free()
print("REF boca arestas cortadas", len(cortadas), flush=True)

# ------------------------------------------------------------------ separa cabeca / corpo pela costura
ativo(low); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="DESELECT"); bpy.ops.object.mode_set(mode="OBJECT")
for pl in low.data.polygons: pl.select = lado_cabeca(pl.center)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.separate(type="SELECTED"); bpy.ops.object.mode_set(mode="OBJECT")
cab = [o for o in sc.objects if o.name.startswith("LOW_Tudo.")][0]; cab.name = cab.data.name = "LOW_Cabeca"
corpo = low; corpo.name = corpo.data.name = "LOW_Corpo"
for o in (cab, corpo):
    for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
print("REF tris cabeca", tris(cab), "corpo", tris(corpo), flush=True)
bvh_cab = BVHTree.FromObject(cab, bpy.context.evaluated_depsgraph_get())
def raio(o_, d_, dist=3.0):
    h = bvh_cab.ray_cast(o_, d_.normalized(), dist); return h[0]
def saida(o_, d_, dist=3.0):
    """distancia ate a pele saindo por dentro (normal no mesmo sentido do raio); None se o ponto esta fora"""
    loc, nrm, _, dd = bvh_cab.ray_cast(o_, d_.normalized(), dist)
    return dd if loc is not None and nrm.dot(d_.normalized()) > 0 else None

# ------------------------------------------------------------------ interior da boca (cavidade, lingua, dentes) e palpebras
def loft(aneis, nome):
    m = bpy.data.meshes.new(nome); b2 = bmesh.new(); vs = [[b2.verts.new(p) for p in a_] for a_ in aneis]; n = len(aneis[0])
    for a1, a2 in zip(vs, vs[1:]):
        for i in range(n): b2.faces.new((a1[i], a1[(i + 1) % n], a2[(i + 1) % n], a2[i]))
    b2.faces.new(vs[0][::-1]); b2.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(b2, faces=b2.faces); b2.to_mesh(m); b2.free()
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o); return o
# interior so onde o ponto da linha da boca esta DENTRO da cabeca (4 raios saem pela pele); o centro em X segue
# o meio entre as paredes (a cabeca do Meshy nao e perfeitamente centrada)
medidas = []
for y in np.linspace(NARIZ.y + 0.05, CANTO - 0.05, 16):
    c = V((0.0, y, z_boca(y)))
    e, d = saida(c, V((1, 0, 0))), saida(c, V((-1, 0, 0)))
    if e is None or d is None: continue
    c.x += (e - d) / 2; e = d = (e + d) / 2
    up, dn = saida(c, V((0, 0, 1))), saida(c, V((0, 0, -1)))
    if up is None or dn is None or min(e, up, dn) < 0.03: continue
    medidas.append((y, e, d, up, dn, c.x))
medidas = medidas[1:] if len(medidas) > 9 else medidas                   # folga da ponta
print("REF boca fileiras validas", len(medidas), "de y", round(medidas[0][0], 3), "a", round(medidas[-1][0], 3), flush=True)
def anel(c, rx, rz_cima, rz_baixo, n=10):
    return [c + V((math.cos(2 * math.pi * i / n) * rx, 0, math.sin(2 * math.pi * i / n) * (rz_cima if math.sin(2 * math.pi * i / n) > 0 else rz_baixo)))
            for i in range(n)]
# cavidade: dentro da pele por cima (60% da espessura do focinho) e por baixo (60% da mandibula fina)
cav = loft([anel(V((cx_, y, z_boca(y))), 0.70 * min(e, d), 0.60 * up, 0.60 * dn) for y, e, d, up, dn, cx_ in medidas], "Boca_Cavidade")
lin = loft([anel(V((cx_, y, z_boca(y) - 0.30 * dn)), 0.45 * min(e, d), 0.15 * dn + 0.005, 0.15 * dn + 0.005, 8) for y, e, d, up, dn, cx_ in medidas[1:-1]], "Boca_Lingua")
dentes = []
def dente(base, direc, comp, r, nome):
    m = bpy.data.meshes.new(nome); b2 = bmesh.new(); n = 5
    anel_ = [b2.verts.new(base + V((math.cos(2 * math.pi * i / n) * r, math.sin(2 * math.pi * i / n) * r * 0.7, 0))) for i in range(n)]
    ponta = b2.verts.new(base + direc * comp)
    for i in range(n): b2.faces.new((anel_[i], anel_[(i + 1) % n], ponta))
    b2.faces.new(anel_[::-1]); bmesh.ops.recalc_face_normals(b2, faces=b2.faces); b2.to_mesh(m); b2.free()
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o); dentes.append(o)
# dentes proporcionais: os de cima descem ate 55% da mandibula (80% no canino) e os de baixo sobem o mesmo,
# tudo por dentro dos labios (fechado nao atravessa a pele)
for k, (y, e, d, up, dn, cx_) in enumerate(medidas[:-1:2]):
    for s, larg in ((1, e), (-1, d)):
        x = cx_ + s * 0.72 * larg; canino = k == 1; comp = (0.80 if canino else 0.50) * dn; r = 0.030 if canino else 0.018
        dente(V((x, y, z_boca(y) + 0.015)), V((0, 0, -1)), comp, r, "Dente_Sup")
        dente(V((cx_ + (x - cx_) * 0.95, y + 0.03, z_boca(y) - 0.015)), V((0, 0, 1)), comp * 0.9, r * 0.9, "Dente_Inf")
y0, e0, d0, up0, dn0, cx0 = medidas[0]
for xx in (-0.45, -0.15, 0.15, 0.45):                                        # incisivos da frente
    xx = cx0 + xx * 0.6 * min(e0, d0)
    dente(V((xx, y0 + 0.02, z_boca(y0) + 0.015)), V((0, 0, -1)), 0.45 * dn0, 0.013, "Dente_Sup")
    dente(V((cx0 + (xx - cx0) * 0.9, y0 + 0.04, z_boca(y0) - 0.015)), V((0, 0, 1)), 0.40 * dn0, 0.012, "Dente_Inf")
PALP = []; PIVOS_OLHO = {}
for lado, ol in ROSTO["olhos"].items():
    c = V(ol["centro"]); n = V(ol["normal"]).normalized()
    up = (V((0, 0, 1)) - n * n.z).normalized(); side = n.cross(up).normalized()
    larg = max(ol["largura_iris"] * 1.9, 0.20); R = larg * 0.62; S = c - n * R          # esfera do "globo" atras da superficie
    dist = []
    for th in range(-15, 61, 5):                                         # direcoes que a palpebra cobre quando fechada
        for ph in range(-50, 51, 10):
            t_, p_ = math.radians(th), math.radians(ph)
            d_ = (n * math.cos(t_) * math.cos(p_) + up * math.sin(t_) + side * math.cos(t_) * math.sin(p_)).normalized()
            loc, nr_, _, dd = bvh_cab.ray_cast(S, d_, 1.0)
            if loc is not None: dist.append((dd, th))
    # casca por fora da pele sobre o olho (centro da abertura) e o mais justa possivel no resto
    centro_ol = [dd for dd, th in dist if -10 <= th <= 20]
    R_C = float(np.clip(max(np.percentile([dd for dd, _ in dist], 60), max(centro_ol) if centro_ol else 0) + 0.006,
                        R + 0.005, R + 0.08)) if dist else R + 0.01
    print("REF palpebra", lado, "raio globo", round(R, 3), "raio casca", round(R_C, 3), flush=True)
    def calota(t0, t1, nome, R_=R_C):
        aneis = []
        for j in range(7):
            th = math.radians(t0 + (t1 - t0) * j / 6)
            fileira = []
            for i in range(11):
                ph = math.radians(-42 + 84 * i / 10)
                d_ = (n * math.cos(th) * math.cos(ph) + up * math.sin(th) + side * math.cos(th) * math.sin(ph)).normalized()
                fileira.append(S + d_ * R_)
            aneis.append(fileira)
        m = bpy.data.meshes.new(nome); b2 = bmesh.new(); vs = [[b2.verts.new(p) for p in f] for f in aneis]
        for a1, a2 in zip(vs, vs[1:]):
            for i in range(10): b2.faces.new((a1[i], a1[i + 1], a2[i + 1], a2[i]))
        b2.to_mesh(m); b2.free(); o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
        for pl in o.data.polygons:                                               # normal para fora
            if (pl.center - S).dot(pl.normal) < 0: pl.flip()
        return o
    # a casca e modelada FECHADA em volta do olho (sem degenerar no polo) e girada inteira ate o repouso ABERTO,
    # recolhida dentro da sobrancelha (superior, +80 graus) e da bochecha (inferior, -55 graus); o rig faz o caminho inverso
    def abrir(o, graus):
        cen = sum((v.co for v in o.data.vertices), V()) / len(o.data.vertices)
        sgn = max((1, -1), key=lambda g: (Matrix.Rotation(g * math.radians(graus), 3, side) @ (cen - S)).normalized().dot(up)
                  * (1 if graus > 0 else -1))
        M = Matrix.Rotation(sgn * math.radians(abs(graus)), 3, side)
        for v in o.data.vertices: v.co = S + M @ (v.co - S)
        cen = sum((v.co for v in o.data.vertices), V()) / len(o.data.vertices)
        rec = -(cen - S).normalized() * RECOLHE                     # repouso tambem RECUADO para dentro da cabeca
        for v in o.data.vertices: v.co += rec
        o.data.update(); return sgn, list(rec)
    RECOLHE = 0.07
    sup_o = calota(-12, 58, "Palpebra_Sup_" + lado); inf_o = calota(-40, -8, "Palpebra_Inf_" + lado)
    sg_s, rec_s = abrir(sup_o, 80); sg_i, rec_i = abrir(inf_o, -55)
    PALP.append(sup_o); PALP.append(inf_o)
    PIVOS_OLHO[lado] = {"centro_globo": list(S), "eixo": list(side), "cima": list(up), "fechar_sup_graus": 80, "fechar_inf_graus": 55, "recuo_sup": rec_s, "recuo_inf": rec_i,
                        "nota": "piscar: desfazer o recuo (transladar -recuo) e girar em torno de 'eixo' no centro_globo para a frente do olho",
                        "raio_globo": R, "raio_casca": R_C}

# ------------------------------------------------------------------ UV e bake de cada parte
def uv_parte(o, escala=1.0):
    ativo(o); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.003, area_weight=0.7)
    bpy.ops.uv.pack_islands(margin=0.003); bpy.ops.object.mode_set(mode="OBJECT")
    if escala != 1.0:
        for l_ in o.data.uv_layers.active.data: l_.uv = l_.uv * escala
uv_parte(corpo); uv_parte(cab, 0.90)                                         # cabeca: faixa u,v > 0,9 reservada para as cores da boca/palpebra
MAPAS = (("cor", "sRGB"), ("normal", "Non-Color"), ("rugosidade", "Non-Color"), ("emissao", "sRGB"))
sc.render.engine = "CYCLES"; sc.cycles.samples = 8
try:
    pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "CUDA"; pr.get_devices(); sc.cycles.device = "GPU"
except Exception as e: print("sem GPU:", e)
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.10; bk.max_ray_distance = 0.40; bk.margin = 8
bk.use_pass_direct = bk.use_pass_indirect = False; bk.use_pass_color = True
for o in list(sc.objects):
    if o.type == "MESH" and o not in (hi_ob, cab, corpo): o.hide_render = True
def assar_parte(o, pref):
    mat = bpy.data.materials.new("M_LoboArtico_%s_LOW" % pref)
    if mat.node_tree is None: mat.use_nodes = True
    nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]; o.data.materials.clear(); o.data.materials.append(mat)
    imgs = {}
    for k, cs in MAPAS:
        im = bpy.data.images.new("LoboArtico_%s_%s" % (pref, k), RES, RES, alpha=False); im.colorspace_settings.name = cs
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = im; imgs[k] = (im, t)
    bpy.ops.object.select_all(action="DESELECT"); hi_ob.select_set(True); o.select_set(True); bpy.context.view_layer.objects.active = o
    for k, tipo in (("cor", "DIFFUSE"), ("normal", "NORMAL"), ("rugosidade", "ROUGHNESS"), ("emissao", "EMIT")):
        for n_ in nt.nodes: n_.select = False
        imgs[k][1].select = True; nt.nodes.active = imgs[k][1]
        bpy.ops.object.bake(type=tipo, **({"pass_filter": {"COLOR"}} if tipo == "DIFFUSE" else {}))
        print("BAKE", pref, k, flush=True)
    Lk = nt.links
    Lk.new(imgs["cor"][1].outputs["Color"], bsdf.inputs["Base Color"]); Lk.new(imgs["rugosidade"][1].outputs["Color"], bsdf.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap"); Lk.new(imgs["normal"][1].outputs["Color"], nm.inputs["Color"]); Lk.new(nm.outputs[0], bsdf.inputs["Normal"])
    Lk.new(imgs["emissao"][1].outputs["Color"], bsdf.inputs["Emission Color"]); bsdf.inputs["Emission Strength"].default_value = 1.0
    return imgs
img_corpo = assar_parte(corpo, "Corpo"); img_cab = assar_parte(cab, "Cabeca")

# amostras de cor reservadas na cabeca (u > 0,92): cavidade, lingua, dentes, pelo da palpebra, borda escura
AMOSTRAS = {"cavidade": ((0.30, 0.07, 0.08), 0.02), "lingua": ((0.62, 0.24, 0.27), 0.17), "dente": ((0.90, 0.87, 0.78), 0.32),
            "palpebra": ((0.86, 0.87, 0.90), 0.47), "borda": ((0.42, 0.43, 0.46), 0.62)}
def pintar(imgs):
    for k, (im, _) in imgs.items():
        W2 = im.size[0]; arr = np.empty(W2 * W2 * 4, np.float32); im.pixels.foreach_get(arr); arr = arr.reshape(W2, W2, 4)
        for nome, (cor, v0) in AMOSTRAS.items():
            r0, r1 = int(v0 * W2), int((v0 + 0.12) * W2); c0 = int(0.92 * W2)
            if k == "cor": arr[r0:r1, c0:, :3] = cor
            elif k == "normal": arr[r0:r1, c0:, :3] = (0.5, 0.5, 1.0)
            elif k == "rugosidade": arr[r0:r1, c0:, :3] = 0.25 if nome in ("cavidade", "lingua") else (0.3 if nome == "dente" else 0.75)
            else: arr[r0:r1, c0:, :3] = 0.0
        im.pixels.foreach_set(arr.ravel()); im.update()
pintar(img_cab)
def uv_amostra(o, nome):
    u, v = 0.96, AMOSTRAS[nome][1] + 0.06
    uvl = o.data.uv_layers.new(name="UVMap") if not o.data.uv_layers else o.data.uv_layers[0]
    for l_ in uvl.data: l_.uv = (u, v)
for o in (cav,): uv_amostra(o, "cavidade")
uv_amostra(lin, "lingua")
for o in dentes: uv_amostra(o, "dente")
for o in PALP:
    uv_amostra(o, "palpebra")
interior = [cav, lin] + dentes + PALP
for o in interior:
    o.data.materials.clear(); o.data.materials.append(cab.data.materials[0])
    for pl in o.data.polygons: pl.use_smooth = True
# borda escura das palpebras: fileira da beirada
for o in PALP:
    uvl = o.data.uv_layers[0]; sup = "Sup" in o.name
    for pl in o.data.polygons:
        if (sup and pl.index < 10) or ((not sup) and pl.index >= 50):
            for li in pl.loop_indices: uvl.data[li].uv = (0.96, AMOSTRAS["borda"][1] + 0.06)
# grupos de vertices (sobrevivem ao join): base dos pesos do rig e do teste sem rig
def grupo(o, nome, ids=None):
    vg = o.vertex_groups.get(nome) or o.vertex_groups.new(name=nome)
    vg.add(list(range(len(o.data.vertices))) if ids is None else ids, 1.0, "REPLACE")
for o in PALP: grupo(o, o.name)
grupo(lin, "Boca_Inferior")
for o in dentes: grupo(o, "Boca_Inferior" if "Inf" in o.name else "Boca_Superior")
grupo(cav, "Boca_Inferior", [v.index for v in cav.data.vertices if v.co.z < z_boca(v.co.y)])
grupo(cav, "Boca_Superior", [v.index for v in cav.data.vertices if v.co.z >= z_boca(v.co.y)])
bpy.ops.object.select_all(action="DESELECT")
for o in interior: o.select_set(True)
cab.select_set(True); bpy.context.view_layer.objects.active = cab; bpy.ops.object.join()
print("REF cabeca com boca e palpebras", tris(cab), flush=True)
for k, _ in MAPAS:
    for pref, imgs in (("Corpo", img_corpo), ("Cabeca", img_cab)):
        im = imgs[k][0]; im.filepath_raw = os.path.join(OUT, "bake%d" % RES, "LoboArtico_%s_%s_%d.png" % (pref, k, RES)); im.file_format = "PNG"; im.save()
        im.scale(FINAL, FINAL); im.filepath_raw = os.path.join(OUT, "LoboArtico_%s_%s.png" % (pref, k)); im.save()

# ------------------------------------------------------------------ cristais
def cristal(base, direc, alt, raio_, nome, lados=6):
    m = bpy.data.meshes.new(nome); b2 = bmesh.new(); aneis = []
    for zf, rf in ((-0.30 * alt, 0.80), (0.0, 1.0), (0.55 * alt, 0.95), (0.78 * alt, 0.55)):
        aneis.append([b2.verts.new((math.cos(2 * math.pi * i / lados + .3) * raio_ * rf * (1 + rnd.uniform(-.1, .1)),
                                    math.sin(2 * math.pi * i / lados + .3) * raio_ * rf * 0.78, zf)) for i in range(lados)])
    topo = b2.verts.new((raio_ * 0.12, 0, alt))
    for k in range(3):
        for i in range(lados): b2.faces.new((aneis[k][i], aneis[k][(i + 1) % lados], aneis[k + 1][(i + 1) % lados], aneis[k + 1][i]))
    for i in range(lados): b2.faces.new((aneis[3][i], aneis[3][(i + 1) % lados], topo))
    b2.faces.new(aneis[0][::-1]); b2.to_mesh(m); b2.free()
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = base; o.rotation_euler = direc.normalized().to_track_quat("Z", "Y").to_euler(); return o
CRIS = []
for (f, dx, alt, r, inc, lat) in ((0.33, 0.14, 0.80, 0.24, 0.60, 0.25), (0.365, 0.26, 0.66, 0.21, 0.68, 0.40),
                                  (0.40, 0.10, 0.55, 0.18, 0.75, 0.20), (0.43, 0.24, 0.42, 0.15, 0.82, 0.45),
                                  (0.30, 0.34, 0.48, 0.16, 0.50, 0.50), (0.385, -0.14, 0.42, 0.15, 0.70, -0.30)):
    y = lo[1] + f * L; ok, hit, nrm, _ = hi_ob.ray_cast(V((dx, y, 12.0)), V((0, 0, -1)))
    CRIS.append(cristal((hit + V((0, 0, -0.06))) if ok else V((dx, y, 6.3)), V((lat, inc, 1.0)), alt, r, "Cristal"))
mc = bpy.data.materials.new("M_LoboArtico_Cristal")
if mc.node_tree is None: mc.use_nodes = True
b3 = mc.node_tree.nodes["Principled BSDF"]; b3.inputs["Base Color"].default_value = (0.55, 0.86, 1.0, 1)
b3.inputs["Alpha"].default_value = 0.62; b3.inputs["Roughness"].default_value = 0.06
b3.inputs["Emission Color"].default_value = (0.45, 0.85, 1.0, 1); b3.inputs["Emission Strength"].default_value = 0.35
mc.surface_render_method = "BLENDED"; mc.use_backface_culling = False
for o in CRIS: o.data.materials.append(mc)
bpy.ops.object.select_all(action="DESELECT")
for o in CRIS: o.select_set(True)
bpy.context.view_layer.objects.active = CRIS[0]; bpy.ops.object.join(); cr = CRIS[0]; cr.name = cr.data.name = "LOW_Cristais"
ativo(cr); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ------------------------------------------------------------------ LODs, export, registro
def lod(o, alvo, nome):
    c = o.copy(); c.data = o.data.copy(); c.name = c.data.name = nome; sc.collection.objects.link(c)
    ativo(c); dd = c.modifiers.new("D", "DECIMATE"); dd.ratio = min(1.0, alvo / tris(c)); bpy.ops.object.modifier_apply(modifier="D")
    c.hide_render = True; return c
l1c, l1b = lod(cab, 3500, "LOD1_Cabeca"), lod(corpo, 6500, "LOD1_Corpo")
l2c, l2b = lod(cab, 1000, "LOD2_Cabeca"), lod(corpo, 2000, "LOD2_Corpo")
def exportar(objs, nome):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, nome), export_format="GLB", use_selection=True, export_image_format="AUTO", export_yup=True)
exportar([cab, corpo, cr], "CR_LoboArtico_LOW.glb"); exportar([l1c, l1b, cr], "CR_LoboArtico_LOD1.glb"); exportar([l2c, l2b, cr], "CR_LoboArtico_LOD2.glb")
json.dump({"mandibula": {"canto_y": CANTO, "linha_boca": [BA, BB], "pivo_sugerido": [0.0, CANTO + 0.55, z_boca(CANTO) + 0.02],
           "nota": "corte dos labios a frente do canto; cavidade/lingua/dentes inferiores seguem a mandibula"},
           "olhos": PIVOS_OLHO, "costura": {"ponto": list(COST_P), "normal": list(COST_N)}},
          open(os.path.join(OUT, "rig_pivos.json"), "w"), indent=1)
reg = {"LOD0": {"LOW_Cabeca": tris(cab), "LOW_Corpo": tris(corpo), "LOW_Cristais": tris(cr)},
       "LOD1": {"LOD1_Cabeca": tris(l1c), "LOD1_Corpo": tris(l1b), "LOW_Cristais": tris(cr)},
       "LOD2": {"LOD2_Cabeca": tris(l2c), "LOD2_Corpo": tris(l2b), "LOW_Cristais": tris(cr)},
       "texturas": "Cabeca e Corpo: cor/normal/rugosidade/emissao 1024 cada (bake 2048)"}
for k in ("LOD0", "LOD1", "LOD2"): reg[k]["total"] = sum(v for v in reg[k].values())
json.dump(reg, open(os.path.join(OUT, "custo_lobo_artico.json"), "w"), indent=1)
print("REF_REGISTRO", json.dumps(reg), flush=True)
bpy.data.objects.remove(hi_ob)
for o in (l1c, l1b, l2c, l2b): o.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend"))
print("REF_OK")
