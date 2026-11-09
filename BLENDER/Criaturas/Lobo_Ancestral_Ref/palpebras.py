"""Palpebras do Lobo Ancestral (09/11/2026). Os olhos sao so pintados na textura (sem globo/palpebra na malha).
Cria, para cada olho, uma PELE fina (palpebra superior) assentada sobre a sobrancelha, logo acima do olho, a 0,008 da
pele, com a pintura da propria sobrancelha (assada da malha LOW para uma area vazia da textura) - aberta, ela some
na sobrancelha. Um osso proprio (PalpebraE/PalpebraD, filho de Cabeca, pivo no centro da curvatura da cabeca no olho)
gira em torno do eixo do olho (X local) e desce a palpebra sobre o olho; o peso cai a 0 nos cantos (canto fica preso),
entao a borda de baixo (a linha escura de cima do olho) vira a linha do olho fechado.
Uso: blender -b rig17/Lobo_Ancestral_Rig.blend -P palpebras.py -- rig18   (grava rig18/Lobo_Ancestral_Rig.blend)"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
SAI = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(SAI, exist_ok=True)
sc = bpy.context.scene
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; me = LO.data
assert LO.matrix_world == Matrix.Identity(4) or True
MW = LO.matrix_world.copy(); MWI = MW.inverted()
gi = {g.index: g.name for g in LO.vertex_groups}
dom = [gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in me.vertices]
P = dict(U=0.28, NU=14, HT=0.075, SOBRA=0.04, NV=6, OFF=0.010, PIV=0.25, ABRE=0.03, DENTRO=0.005, CLARO=1.3, PHI=23.0, MS=0.01, MT=-0.02, FECHA=0.15)
for k in list(P): P[k] = float(os.environ.get("LOBO_P_" + k, P[k]))
P["NU"] = int(P["NU"]); P["NV"] = int(P["NV"])
# ---- BVH so da pele da cabeca (sem tufos/cartoes de pelo: ilhas pequenas)
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
ilha = [-1] * len(bm.verts); tam = []
for v in bm.verts:
    if ilha[v.index] >= 0: continue
    st = [v]; ilha[v.index] = len(tam); n = 0
    while st:
        x = st.pop(); n += 1
        for e in x.link_edges:
            o = e.other_vert(x)
            if ilha[o.index] < 0: ilha[o.index] = len(tam); st.append(o)
    tam.append(n)
pele = [f for f in bm.faces if all(dom[v.index] == "Cabeca" and tam[ilha[v.index]] > 500 for v in f.verts)]
cos = [MW @ v.co for v in bm.verts]
bvh = BVHTree.FromPolygons(cos, [[v.index for v in f.verts] for f in pele])
print("PELE faces", len(pele))
# ---- area vazia da textura (rasteriza a cobertura de UV)
mat = me.materials[0]; nt = mat.node_tree
img_cor = [n.image for n in nt.nodes if n.type == "TEX_IMAGE" and "Cor" in n.image.name][0]
img_nor = [n.image for n in nt.nodes if n.type == "TEX_IMAGE" and "Normal" in n.image.name][0]
W, H = img_cor.size
uvl = me.uv_layers.active.data; cobn = np.zeros((H, W), bool)        # cobertura conservadora (caixa de cada face, linha 0 = topo)
for f in me.polygons:
    us = [uvl[l].uv[0] * W for l in f.loop_indices]; vs_ = [(1 - uvl[l].uv[1]) * H for l in f.loop_indices]
    cobn[max(0, int(min(vs_)) - 1):int(max(vs_)) + 2, max(0, int(min(us)) - 1):int(max(us)) + 2] = True
RW, RH = int(os.environ.get("LOBO_P_RW", "96")), int(os.environ.get("LOBO_P_RH", "40"))                                                    # retangulo por palpebra (px)
def acha_vazio(ocup):
    pad = 3; occ = ocup.copy()
    ii = np.cumsum(np.cumsum(occ.astype(np.int32), 0), 1)
    for y in range(pad, H - RH - pad, 4):
        for x in range(pad, W - RW - pad, 4):
            y0, x0, y1, x1 = y - pad, x - pad, y + RH + pad, x + RW + pad
            s = ii[y1 - 1, x1 - 1] - (ii[y0 - 1, x1 - 1] if y0 else 0) - (ii[y1 - 1, x0 - 1] if x0 else 0) + (ii[y0 - 1, x0 - 1] if x0 and y0 else 0)
            if s == 0: return x, y
    raise SystemExit("SEM AREA VAZIA NA TEXTURA")
# ---- cria as palpebras (v2): construida na forma FECHADA sobre o olho (a 0,01 da pele do olho, do canto ao canto,
# da borda de baixo do olho ate logo acima da de cima); a forma ABERTA (repouso) e a fechada girada para cima em torno
# do pivo, que a esconde sob a sobrancelha (o olho e fundo: a sobrancelha fica 0,04-0,10 acima). So a borda escura
# (linha dos cilios) fica rente a borda de cima do olho quando aberta. Pintura propria: pelo escuro da mascara + cilios.
from mathutils.interpolate import poly_3d_calc
uvb = bm.loops.layers.uv.active
cpix = np.array(img_cor.pixels[:]).reshape(H, W, 4)
def cor_em(p):
    loc, nor, idx, d = bvh.find_nearest(p)
    f = pele[idx]; ws = poly_3d_calc([cos[v.index] for v in f.verts], loc)
    uv = sum((l[uvb].uv * w for l, w in zip(f.loops, ws)), V((0, 0)))
    return cpix[int(uv.y * (H - 1)), int(uv.x * (W - 1)), :3]
RET = {}; INFO = {}; lids = []
for lado, s in (("E", 1), ("D", -1)):
    C = V((0.501 * s, -6.061, 7.085))
    nn = V((0, 0, 0)); pts = []
    for f in pele:
        c = MW @ f.calc_center_median()
        if (c - C).length < 0.35: nn += (MW.to_3x3() @ f.normal) * f.calc_area(); pts.append(c)
    n = nn.normalized()
    a = V((0, 0, 1)).cross(n).normalized() * s
    t = n.cross(a).normalized() * s
    if t.z < 0: t = -t
    fi = math.radians(P["PHI"])
    e1 = (a * math.cos(fi) + t * math.sin(fi)).normalized(); e2 = (-a * math.sin(fi) + t * math.cos(fi)).normalized()
    M0 = C + a * P["MS"] + t * P["MT"]
    X = np.array([p[:] for p in pts]); A_ = np.c_[2 * X, np.ones(len(X))]; b_ = (X ** 2).sum(1)
    sol = np.linalg.lstsq(A_, b_, rcond=None)[0]; cen = V(sol[:3]); R = math.sqrt(sol[3] + cen.length_squared)
    if R > 3.0 or (cen - C).dot(n) > 0: cen = C - n * 0.6; R = 0.6
    if P["PIV"] > 0: cen = C - n * P["PIV"]                            # v2b: pivo no fundo do olho, ao longo da normal
    R = (C - cen).length                                                # raio REAL ate o olho (o arco usa este)
    d = (C - cen).normalized(); k = (e1 - d * d.dot(e1)).normalized()     # eixo de giro = eixo do olho (X do osso = -k)
    alfa = (P["FECHA"] + P["ABRE"]) / R                                               # radianos para descer a borda HT+HB
    if (Matrix.Rotation(alfa, 3, k) @ (C - cen)).dot(e2) > (C - cen).dot(e2): alfa = -alfa   # sinal que DESCE
    Rf = Matrix.Rotation(alfa, 3, k)
    U, NU, NV = P["U"], P["NU"], P["NV"]; HB = P["FECHA"] - P["HT"]
    vs, uvs, pesos = [], [], []
    for j in range(NV + 1):
        for i in range(NU + 1):
            u = -U + 2 * U * i / NU; w = max(0.0, 1 - (u / U) ** 2)
            fr = j / NV; v = -HB * w + (P["HT"] * w + P["SOBRA"] * w ** 0.5 + HB * w) * fr      # de baixo (borda de baixo) ao topo
            q = M0 + e1 * u + e2 * v
            hit = bvh.ray_cast(q + n * 0.5, -n, 1.5)
            if hit[0] is None: hit = bvh.find_nearest(q)
            hz = (hit[0] - q).dot(n)
            if j > 0: hz = min(hz, base_h[i] + 0.012 * fr)                     # nao sobe na sobrancelha: segue a curva do olho
            else: pass
            fechado = q + n * (hz + P["OFF"] * w - 0.006 * (1 - w))      # cantos (peso ~0) ficam sob a pele
            if j == 0: base_h = base_h if i else {}; base_h[i] = hz
            # forma aberta: desfaz o giro ponderado (LBS: fechado = (1-w) o + w R o)
            Mw = Matrix.Identity(3) * (1 - w) + Rf * w
            aberto = cen + Mw.inverted() @ (fechado - cen)
            loc_, nor_, _i, _d = bvh.find_nearest(aberto)                   # v2c: aberta NUNCA fora da pele (canto interno
            sd_ = (aberto - loc_).dot(nor_)                                 # e linha de baixo apareciam como lasca escura)
            if sd_ > -P["DENTRO"]: aberto = aberto - nor_.normalized() * (sd_ + P["DENTRO"])
            vs.append(aberto); uvs.append((i / NU, fr)); pesos.append(w)
    faces = [(j * (NU + 1) + i, j * (NU + 1) + i + 1, (j + 1) * (NU + 1) + i + 1, (j + 1) * (NU + 1) + i) for j in range(NV) for i in range(NU)]
    m = bpy.data.meshes.new("Palpebra" + lado); m.from_pydata([MWI @ p for p in vs], [], faces); m.update()
    if m.polygons[NU * NV // 2].normal.dot(MWI.to_3x3() @ n) < 0: m.flip_normals()
    ob = bpy.data.objects.new("Palpebra" + lado, m); sc.collection.objects.link(ob); ob.matrix_world = MW
    m.materials.append(mat); ul = m.uv_layers.new(name=me.uv_layers.active.name)
    ocup = cobn.copy()
    for r in RET.values(): ocup[max(0, r[1] - 4):r[1] + RH + 4, max(0, r[0] - 4):r[0] + RW + 4] = True
    x0, y0 = acha_vazio(ocup); RET[lado] = (x0, y0)
    for poly in m.polygons:
        poly.use_smooth = True
        for l in poly.loop_indices:
            iu, iv = uvs[m.loops[l].vertex_index]
            ul.data[l].uv = ((x0 + 2 + iu * (RW - 4)) / W, 1 - (y0 + RH - 2 - iv * (RH - 4)) / H)
    # cores da mascara em volta do olho
    baixo = np.median([cor_em(M0 + e1 * uu + e2 * vv) for uu in np.linspace(-0.12, 0.12, 7) for vv in (-0.15, -0.12, -0.10)], 0)
    cima = np.median([cor_em(M0 + e1 * uu + e2 * vv) for uu in np.linspace(-0.12, 0.12, 7) for vv in (0.10, 0.12)], 0)
    INFO[lado] = dict(C=C, n=n, e1=e1, e2=e2, cen=cen, R=R, M0=M0, alfa=alfa, k=k, baixo=baixo, cima=cima)
    ob["pesos"] = pesos; lids.append(ob)
    print("PALPEBRA", lado, "verts", len(vs), "uv px", RET[lado], "R %.3f giro %.1f graus" % (R, math.degrees(alfa)),
          "cor baixo", np.round(baixo, 3), "cima", np.round(cima, 3))
# ---- pintura das palpebras (cor da textura; normal neutra): pelo da mascara com riscos + linha escura dos cilios
cp = cpix.copy(); npx = np.array(img_nor.pixels[:]).reshape(H, W, 4); rng = np.random.default_rng(7)
for lado, (x0, y0) in RET.items():
    I = INFO[lado]
    for yy in range(RH):
        iv = min(1.0, max(0.0, ((RH - 2) - yy) / (RH - 4)))            # yy = linha a partir do topo do retangulo
        base = (I["baixo"] * (1 - 0.5 * iv) + I["cima"] * 0.5 * iv) * P["CLARO"]   # mascara cinza (mais clara perto da linha)
        cil = np.array([0.04, 0.035, 0.035])
        if iv < 0.07: c_ = cil
        elif iv < 0.16: tt = (iv - 0.07) / 0.09; c_ = cil * (1 - tt) + base * tt
        else: c_ = base
        row = H - 1 - (y0 + yy)
        risco = 1 + 0.04 * np.sin(yy * 1.7 + np.arange(RW) * 0.05) + rng.normal(0, 0.02, RW)   # riscos ao longo da palpebra
        cp[row, x0:x0 + RW, :3] = np.clip(c_[None, :] * risco[:, None], 0, 1); cp[row, x0:x0 + RW, 3] = 1
    npx[H - (y0 + RH):H - y0, x0:x0 + RW] = (0.5, 0.5, 1.0, 1.0)
img_cor.pixels = cp.ravel().tolist(); img_cor.update(); img_cor.pack()
img_nor.pixels = npx.ravel().tolist(); img_nor.update(); img_nor.pack()
img_cor.save_render(os.path.join(SAI, "T_Lobo_Cor.png")); img_nor.save_render(os.path.join(SAI, "T_Lobo_Normal.png"))
# ---- ossos
bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); eb = arm.data.edit_bones; AWI = arm.matrix_world.inverted()
for lado, I in INFO.items():
    b = eb.new("Palpebra" + lado); b.head = AWI @ I["cen"]; d = (I["C"] - I["cen"]).normalized()
    b.tail = AWI @ (I["cen"] + d * 0.25); b.parent = eb["Cabeca"]; b.use_connect = False; b.use_deform = True
    b.align_roll(AWI.to_3x3() @ I["e2"].cross(d).cross(d) * -1)          # provisorio; abaixo garante X local ~ e1
    # z-axis do osso perpendicular a d e a e1 -> X local = e1
    z = d.cross(I["e1"]).normalized(); b.align_roll(AWI.to_3x3() @ z)
bpy.ops.object.mode_set(mode="OBJECT")
for lado, I in INFO.items():
    bx = (arm.matrix_world.to_3x3() @ arm.data.bones["Palpebra" + lado].matrix_local.to_3x3().col[0]).normalized()
    print("OSSO Palpebra%s X local . eixo do olho = %.3f" % (lado, bx.dot(I["e1"])))
    I["local"] = math.degrees(I["alfa"]) * (1.0 if bx.dot(I["k"]) > 0 else -1.0)   # graus em X local que FECHAM
# ---- pesos e juncao na LOW
for ob in lids:
    lado = ob.name[-1]; ps = ob["pesos"]
    gp = ob.vertex_groups.new(name="Palpebra" + lado); gc = ob.vertex_groups.new(name="Cabeca")
    for i, w in enumerate(ps):
        if w > 0: gp.add([i], w, "REPLACE")
        if w < 1: gc.add([i], 1 - w, "REPLACE")
bpy.ops.object.select_all(action="DESELECT")
for ob in lids: ob.select_set(True)
LO.select_set(True); bpy.context.view_layer.objects.active = LO
nv0 = len(me.vertices); bpy.ops.object.join()
print("JUNTOU", nv0, "->", len(LO.data.vertices), "verts; tris", sum(len(p.vertices) - 2 for p in LO.data.polygons))
# angulo de fechar (radianos) = arco / raio
fecha = {l: I["local"] for l, I in INFO.items()}
arm["palpebra_fecha_graus"] = json.dumps(fecha)
json.dump({"param": P, "retangulos_px": RET, "fecha_graus": fecha,
           "info": {l: {k: (list(map(float, v)) if hasattr(v, "__len__") else float(v)) for k, v in I.items()} for l, I in INFO.items()}},
          open(os.path.join(SAI, "palpebras.json"), "w"), indent=1, default=float)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAI, "Lobo_Ancestral_Rig.blend"))
print("PALPEBRAS_OK fecha", fecha)
