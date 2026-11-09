"""Malha de jogo PARA O RIG do Lobo Ancestral (a partir da HIGH do Meshy em pose neutra, review/m03):
1. recentra em X pela linha media do tronco/cabeca (a centralizacao pela caixa ficou ~0,45 deslocada pela cauda/patas);
2. solda + decimacao com MAIS densidade na cabeca (boca/olhos/orelhas deformam) -> ALVO tris; tapa furos;
3. boca: corte no plano da linha dos labios (medida por raios laterais) do nariz ate o canto; interior (gengiva/palato,
   lingua, dentes) em geometria propria, com cores pintadas numa faixa reservada da textura;
4. UV nova (rosto x2,2), bake HIGH->LOW de cor e normal 2048 -> 1024; marcos para o rig em marcos_rig.json.
Uso: blender -b review/m03/Lobo_Meshy_endireitado.blend -P preparar_rig.py -- <saida_dir> [alvo_tris=18000]"""
import bpy, bmesh, sys, os, math, json, time
import numpy as np
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True); ALVO = int(A[1]) if len(A) > 1 else 18000
PX = 2048; sc = bpy.context.scene; t0 = time.time()
def suave(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
HI = bpy.data.objects["Lobo_Meshy"]; mh = HI.data
n = len(mh.vertices); co = np.empty(n * 3); mh.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co[:, 0], co[:, 1], co[:, 2]

# ------------------------------------------------------------------ 1. linha media -> recentrar
meios = []
for a in np.arange(-6.6, 2.4, 0.4):                      # tronco + pescoco + cabeca (sem cauda e sem patas baixas)
    m = (y >= a) & (y < a + 0.4) & (z > 4.2)
    if m.sum() > 200: meios.append((x[m].min() + x[m].max()) / 2)
XC = float(np.median(meios)); print("LINHA_MEDIA x", round(XC, 3), "fatias", len(meios))
mh.transform(Matrix.Translation(V((-XC, 0, 0)))); mh.update()

# ------------------------------------------------------------------ 2. curva dos labios (traco escuro da textura, medir_labio.py)
bpy.context.view_layer.update()
vs = [v.co for v in mh.vertices]; NAR = min(vs, key=lambda v: v.y).copy()
LAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "low", "labio.json")))
pts, cantos = [], []
for k, lista in LAB["lados"].items():
    esc = [(yy, zz) for yy, zz, lum, med in lista if lum < 0.16 and yy >= NAR.y + 0.55]
    pts += esc
    if esc: cantos.append(max(p[0] for p in esc))
fr = [(f_[3], f_[1]) for f_ in LAB["frente"] if f_[1] is not None]
if fr: pts.append((min(p[0] for p in fr), sum(p[1] for p in fr) / len(fr)))
Y_CANTO = sum(cantos) / len(cantos)
pts.sort(); Yp = np.array([p[0] for p in pts]); Zp = np.array([p[1] for p in pts])
CUR_Y = np.linspace(Yp.min(), Y_CANTO, 8); CUR_Z = np.polyval(np.polyfit(Yp, Zp, 2), CUR_Y)
def z_boca(yy): return float(np.interp(yy, CUR_Y, CUR_Z))
BA, BB = float(CUR_Z[0]), 0.0
print("BOCA pontos", len(pts), "canto y %.2f" % Y_CANTO, "curva", [(round(float(a), 2), round(float(b), 3)) for a, b in zip(CUR_Y, CUR_Z)])

# ------------------------------------------------------------------ 3. LOW: solda, decimacao com cabeca densa, furos
LO = HI.copy(); LO.data = mh.copy(); LO.name = LO.data.name = "Lobo_Ancestral_LOW"; sc.collection.objects.link(LO)
ativo(LO)
bm = bmesh.new(); bm.from_mesh(LO.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005); bm.to_mesh(LO.data); bm.free()
vg = LO.vertex_groups.new(name="Densidade")
Y0 = NAR.y
for v in LO.data.vertices:                                # peso baixo = mais densidade (cabeca e focinho)
    d = v.co.y - Y0
    w = 0.25 if (d < 2.3 and v.co.z > 5.6) else 1.0
    vg.add([v.index], w, "REPLACE")
tris0 = sum(len(p.vertices) - 2 for p in LO.data.polygons)
dec = LO.modifiers.new("Dec", "DECIMATE"); dec.decimate_type = "COLLAPSE"; dec.vertex_group = "Densidade"
dec.vertex_group_factor = 3.0; dec.invert_vertex_group = False; dec.use_collapse_triangulate = True
dec.ratio = ALVO / tris0
bpy.ops.object.modifier_apply(modifier=dec.name)
me = LO.data; print("DECIMADO", len(me.polygons), "tris de", tris0)
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.0002)
bord = [e for e in bm.edges if e.is_boundary]
r = bmesh.ops.holes_fill(bm, edges=bord, sides=16)
bmesh.ops.triangulate(bm, faces=bm.faces)
print("FUROS tapados", len(r["faces"]), "bordas restantes", sum(1 for e in bm.edges if e.is_boundary),
      "nao_manifold", sum(1 for e in bm.edges if not e.is_manifold))
# ------------------------------------------------------------------ 4. corte da boca: fronteira das faces abaixo da curva
bm.faces.ensure_lookup_table()
def eh_mand(c): return c.y < Y_CANTO and abs(c.x) < 1.1 and c.z < z_boca(c.y) and c.z > z_boca(c.y) - 1.6
mand = {f.index for f in bm.faces if eh_mand(f.calc_center_median())}
for _ in range(2):                                        # limpa pontas soltas (maioria dos vizinhos)
    troca = []
    for f in bm.faces:
        if f.calc_center_median().y > Y_CANTO: continue
        viz = [g.index in mand for e in f.edges for g in e.link_faces if g is not f]
        if viz and (sum(viz) / len(viz) > 0.66) != (f.index in mand) and abs(sum(viz) / len(viz) - 0.5) > 0.16: troca.append(f.index)
    for i in troca: mand.symmetric_difference_update({i})
corte = [e for e in bm.edges if len(e.link_faces) == 2 and ((e.link_faces[0].index in mand) != (e.link_faces[1].index in mand))
         and max(e.verts[0].co.y, e.verts[1].co.y) < Y_CANTO - 0.04]
bmesh.ops.split_edges(bm, edges=corte)
print("BOCA arestas cortadas", len(corte), "faces da mandibula", len(mand))
# interior ligado as bordas do corte: parede interna de cada labio -> palato (em cima) / assoalho (embaixo) -> garganta
IL = bm.faces.layers.int.new("interior"); ML = bm.faces.layers.int.new("mandibula")
bm.faces.ensure_lookup_table()
for f in bm.faces: f[ML] = 1 if f.index in mand else 0
def na_boca(e): return all(v.co.y < Y_CANTO + 0.02 and abs(v.co.x) < 1.2 and abs(v.co.z - z_boca(min(v.co.y, Y_CANTO))) < 0.3 for v in e.verts)
bord = [e for e in bm.edges if e.is_boundary and na_boca(e)]
INT_FACES = []; RIM = {}
for sup in (True, False):
    grupo = [e for e in bord if (e.link_faces[0][ML] == 0) == sup]
    s_ = 1 if sup else -1; prime = {}
    for e in grupo:
        for v in e.verts:
            if v not in prime:
                c = v.co; prime[v] = bm.verts.new((c.x * 0.45, c.y + 0.04, c.z + s_ * (0.10 if sup else 0.08)))
    for e in grupo:
        a_, b_ = e.verts; f = bm.faces.new((a_, b_, prime[b_], prime[a_])); f[IL] = 2; f[ML] = 0 if sup else 1; INT_FACES.append(f)
    grau = {}
    for e in grupo:
        for v in e.verts: grau[v] = grau.get(v, 0) + 1
    pontas = [v for v, g in grau.items() if g == 1]
    arestas = [bm.edges.get((prime[e.verts[0]], prime[e.verts[1]])) or bm.edges.new((prime[e.verts[0]], prime[e.verts[1]])) for e in grupo]
    if len(pontas) == 2:
        pa, pb = sorted(pontas, key=lambda v: v.co.x)
        fecho = bm.edges.get((prime[pa], prime[pb])) or bm.edges.new((prime[pa], prime[pb])); arestas.append(fecho)
        RIM[sup] = (prime[pa], prime[pb])
    r_ = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=arestas)
    for f in r_["geom"]:
        if isinstance(f, bmesh.types.BMFace): f[IL] = 1 if sup else 2; f[ML] = 0 if sup else 1; INT_FACES.append(f)
    print("BOCA", "labio de cima" if sup else "labio de baixo", "bordas", len(grupo), "pontas", len(pontas))
if True in RIM and False in RIM:                          # garganta
    (ua, ub), (la, lb) = RIM[True], RIM[False]
    f = bm.faces.new((ua, ub, lb, la)); f[IL] = 1; f[ML] = 0; INT_FACES.append(f)
for f in INT_FACES:                                       # normais para dentro da boca (lado visto pela abertura)
    c = f.calc_center_median(); yy = min(c.y, Y_CANTO) - 0.15
    alvo = V((0, yy, z_boca(yy)))
    f.normal_update()
    if f.normal.dot(alvo - c) < 0: f.normal_flip()
print("BOCA faces internas", len(INT_FACES))
bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = True
corpo_tris = len(me.polygons)

# ------------------------------------------------------------------ 5. lingua e dentes (objeto a parte, juntado depois)
bm = bmesh.new(); uvb = bm.loops.layers.uv.new("UVMap"); PECAS = {}; PL = bm.faces.layers.int.new("mandibula")
def faixa_uv(i):                                         # quadradinhos na faixa reservada (u > 0.955)
    u0 = 0.958; v0 = 0.02 + i * 0.045; return (u0, v0, u0 + 0.035, v0 + 0.035)
def uv_peca(fs, i):
    u0, v0, u1, v1 = faixa_uv(i)
    for f in fs:
        for lp in f.loops: lp[uvb].uv = (u0 + (u1 - u0) * 0.5, v0 + (v1 - v0) * 0.5)
def bolinha(nome, centro, esc, iuv, seg=8):
    r_ = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(4, seg // 2), radius=1.0)
    for v in r_["verts"]: v.co = V((centro[0] + v.co.x * esc[0], centro[1] + v.co.y * esc[1], centro[2] + v.co.z * esc[2]))
    fs = list({f for v in r_["verts"] for f in v.link_faces}); uv_peca(fs, iuv)
    for f in fs: f[PL] = 1 if nome in ("DentesInf", "Lingua") else 0
yl = (NAR.y + Y_CANTO) / 2 + 0.35
bolinha("Lingua", (0, yl, z_boca(yl) - 0.08), (0.11, 0.33, 0.028), 2)
def dente(nome, base, alt, raio, sobe, iuv):
    r_ = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=5, radius1=raio, radius2=0.002, depth=alt)
    for v in r_["verts"]: v.co = V((base[0] + v.co.x, base[1] + v.co.y, base[2] + sobe * (v.co.z + alt / 2)))
    fs = list({f for v in r_["verts"] for f in v.link_faces})
    if sobe < 0: bmesh.ops.reverse_faces(bm, faces=fs)
    fs = list({f for v in r_["verts"] for f in v.link_faces}); uv_peca(fs, iuv)
    for f in fs: f[PL] = 1 if nome in ("DentesInf", "Lingua") else 0
# dentes junto da borda interna de cada labio (posicoes lidas da propria borda)
mm = me; bocal = {True: [], False: []}
ML_ = mm.attributes["mandibula"].data
for e in mm.edges:
    pass
bmL = bmesh.new(); bmL.from_mesh(mm); ILl = bmL.faces.layers.int["interior"]; MLl = bmL.faces.layers.int["mandibula"]
for f in bmL.faces:
    if f[ILl] == 2:                                       # parede interna: o lado de fora (2 primeiros vertices) e a borda do labio
        for v in f.verts:
            if abs(v.co.x) > 0.12 and v.co.y < Y_CANTO - 0.08: bocal[f[MLl] == 0].append(v.co.copy())
bmL.free()
n_d = 0
for sup in (True, False):
    for sx in (1, -1):
        lado = sorted({(round(p.x, 3), round(p.y, 3), round(p.z, 3)) for p in bocal[sup] if p.x * sx > 0}, key=lambda q: q[1])
        if len(lado) < 4: continue
        for frac, canino in ((0.08, False), (0.22, True), (0.42, False), (0.62, False), (0.80, False)):
            q = lado[min(len(lado) - 1, int(frac * len(lado)))]
            base = (q[0] * 0.78, q[1] + 0.03, q[2] + (0.085 if sup else -0.08))
            alt = (0.11 if sup else 0.09) if canino else 0.045
            dente("DentesSup" if sup else "DentesInf", base, alt, 0.038 if canino else 0.022, -1 if sup else 1, 3); n_d += 1
    yy = NAR.y + 0.45                                     # incisivos da frente
    for xx in (-0.06, 0.06):
        dente("DentesSup" if sup else "DentesInf", (xx, yy + 0.08, z_boca(yy) + (0.085 if sup else -0.08)), 0.04, 0.02, -1 if sup else 1, 3); n_d += 1

boca_me = bpy.data.meshes.new("Boca"); bm.to_mesh(boca_me); bm.free()
BOCA = bpy.data.objects.new("Lobo_Boca", boca_me); sc.collection.objects.link(BOCA)
for p in boca_me.polygons: p.use_smooth = True
print("BOCA lingua+dentes tris", sum(len(p.vertices) - 2 for p in boca_me.polygons), "dentes", n_d)

# ------------------------------------------------------------------ 6. UV (rosto x2,2, faixa reservada u>0,955) + bake
ativo(LO)
while me.uv_layers: me.uv_layers.remove(me.uv_layers[0])
me.uv_layers.new(name="UVMap")
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.003, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
bpy.ops.object.mode_set(mode="OBJECT")
bm = bmesh.new(); bm.from_mesh(me); uvl = bm.loops.layers.uv.active; bm.faces.ensure_lookup_table()
vist = set(); n_cab = 0
for f0 in bm.faces:
    if f0.index in vist: continue
    ilha, pilha = [], [f0]; vist.add(f0.index)
    while pilha:
        f = pilha.pop(); ilha.append(f)
        for lp in f.loops:
            e = lp.edge
            for f2 in e.link_faces:
                if f2.index in vist: continue
                l2 = [l for l in f2.loops if l.edge is e][0]
                if (lp[uvl].uv - l2.link_loop_next[uvl].uv).length < 1e-5 and (lp.link_loop_next[uvl].uv - l2[uvl].uv).length < 1e-5:
                    vist.add(f2.index); pilha.append(f2)
    c3 = sum((f.calc_center_median() for f in ilha), V()) / len(ilha)
    if c3.y < NAR.y + 2.3 and c3.z > 5.6:
        n_cab += 1; luv = [l[uvl] for f in ilha for l in f.loops]
        cu = sum((l.uv for l in luv), V((0, 0))) / len(luv)
        for l in luv: l.uv = cu + (l.uv - cu) * 2.2
bm.to_mesh(me); bm.free()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.pack_islands(margin=0.003, rotate=True, scale=True)
bpy.ops.object.mode_set(mode="OBJECT")
for d in me.uv_layers.active.data: d.uv = (d.uv[0] * 0.95, d.uv[1])     # libera a faixa u > 0,95
IA = me.attributes["interior"].data; uvd = me.uv_layers.active.data; n_int = 0
for p in me.polygons:
    k = IA[p.index].value
    if k:
        u0, v0, u1, v1 = faixa_uv(k - 1); n_int += 1
        for li in p.loop_indices: uvd[li].uv = (u0 + (u1 - u0) * 0.5, v0 + (v1 - v0) * 0.5)
print("UV faces internas na faixa", n_int)
print("UV ilhas_cabeca", n_cab)
while me.materials: me.materials.pop()
mat = bpy.data.materials.new("M_Lobo_Ancestral")
if mat.node_tree is None: mat.use_nodes = True
nt = mat.node_tree; bs = nt.nodes["Principled BSDF"]; me.materials.append(mat); boca_me.materials.append(mat)
def imagem(nome, cor):
    im = bpy.data.images.new(nome, PX, PX, alpha=False)
    if not cor: im.colorspace_settings.name = "Non-Color"
    return im
I_COR, I_NOR = imagem("T_Lobo_Cor", True), imagem("T_Lobo_Normal", False)
tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = I_COR
texn = nt.nodes.new("ShaderNodeTexImage"); texn.image = I_NOR; nm = nt.nodes.new("ShaderNodeNormalMap")
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 4
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.04; bk.max_ray_distance = 0.25; bk.margin = 8
bpy.ops.object.select_all(action="DESELECT"); HI.select_set(True); LO.select_set(True); bpy.context.view_layer.objects.active = LO
for im, tipo, nd in ((I_COR, "DIFFUSE", tex), (I_NOR, "NORMAL", texn)):
    for q in nt.nodes: q.select = False
    nd.select = True; nt.nodes.active = nd
    if tipo == "DIFFUSE": bk.use_pass_direct = False; bk.use_pass_indirect = False; bk.use_pass_color = True
    t1 = time.time(); bpy.ops.object.bake(type=tipo); print("BAKE", tipo, round(time.time() - t1), "s")
# pinta a faixa reservada: palato, assoalho (gengiva), lingua, dentes; normal neutra
CORES = {0: (0.12, 0.045, 0.045), 1: (0.22, 0.07, 0.07), 2: (0.40, 0.14, 0.15), 3: (0.80, 0.76, 0.66)}
for im, cor in ((I_COR, True), (I_NOR, False)):
    p = np.empty(PX * PX * 4, np.float32); im.pixels.foreach_get(p); p = p.reshape(PX, PX, 4)
    if cor:
        lin = lambda c: c ** 2.2                          # imagem sRGB em bytes: pixels guardam valor de exibicao
        for i, c in CORES.items():
            u0, v0, u1, v1 = faixa_uv(i)
            p[int(v0 * PX):int(v1 * PX), int(u0 * PX):int(u1 * PX), :3] = [cc ** (1 / 2.2) for cc in c]
    else:
        p[:, int(0.955 * PX):, :3] = (0.5, 0.5, 1.0)
    im.pixels.foreach_set(p.ravel())
for im in (I_COR, I_NOR):
    im.filepath_raw = os.path.join(OUT, im.name + "_2048.png"); im.file_format = "PNG"; im.save()
    im.scale(1024, 1024); im.filepath_raw = os.path.join(OUT, im.name + ".png"); im.save()
nt.links.new(tex.outputs["Color"], bs.inputs["Base Color"])
nt.links.new(texn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bs.inputs["Normal"])
bs.inputs["Roughness"].default_value = 0.82
if "Specular IOR Level" in bs.inputs: bs.inputs["Specular IOR Level"].default_value = 0.3
# junta o interior da boca na malha (uma MeshPart)
ativo(LO); BOCA.select_set(True); bpy.ops.object.join(); LO = bpy.context.view_layer.objects.active; me = LO.data
bm = bmesh.new(); bm.from_mesh(me)
print("MALHA_FINAL tris", len(bm.faces), "corpo", corpo_tris, "bordas_abertas", sum(1 for e in bm.edges if e.is_boundary))
bm.free()
HI.hide_render = True; HI.hide_set(True); sc.render.engine = "BLENDER_EEVEE"
json.dump({"x_recentro": -XC, "nariz": list(NAR), "curva_y": list(map(float, CUR_Y)), "curva_z": list(map(float, CUR_Z)), "y_canto": Y_CANTO},
          open(os.path.join(OUT, "marcos_rig.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_LOW_rig.blend"))
print("PREPARAR_OK", round(time.time() - t0), "s")
