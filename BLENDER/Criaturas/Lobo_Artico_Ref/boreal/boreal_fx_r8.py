"""Efeitos de gelo r8 (17/11/2026) - E1 do pedido "efeitos 100% fieis a imagem PREPARO/VOO/POUSO" (mesmo efeito em todos os poderes).
O que a referencia mostra e este script gera (sobre anim_v42, pose de REPOUSO):
  * ESPINHOS: crista ALTA de cristais translucidos azul-gelo, aglomerada na nuca/cernelha (varios por posicao, abrindo em
    leque para os lados), diminuindo ate o meio das costas; inclinados para tras. Cada POSICAO e um objeto rigido preso
    ao osso mais proximo (mesmo contrato do r6 no Roblox: OssoEspinho/OffsetOsso/BaseLocal/TamanhoCheio/Altura).
  * LINHAS (fitas de bake, viram mascara de emissao na UV da LOW_Corpo, como no r7): ESPIRAL no ombro, linha da nuca
    descendo ao ombro, onda pelo flanco ate o quadril com volta na anca, linha alta nas costas, linhas nas pernas e na
    cauda. Desenhadas no perfil (y, z) e projetadas na pele por raio lateral; espelhadas para o lado direito.
Saidas: boreal/CR_LoboArtico_Boreal_r8.blend, boreal/export/boreal_fx_r8.json
Uso: blender -b anim_v42/CR_LoboArtico_Anim.blend -P boreal/boreal_fx_r8.py"""
import bpy, bmesh, os, math, json
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
AQUI = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.join(AQUI, "export"); os.makedirs(EXP, exist_ok=True)
rig = bpy.data.objects["LoboArtico_Rig"]; rig.animation_data.action = None
for pb in rig.pose.bones: pb.matrix_basis.identity()
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
corpo = bpy.data.objects["LOW_Corpo"]; cab = bpy.data.objects["LOW_Cabeca"]

def bvh_de(objs):
    dg = bpy.context.evaluated_depsgraph_get(); bm = bmesh.new()
    for o in objs:
        me = o.evaluated_get(dg).to_mesh(); tmp = bmesh.new(); tmp.from_mesh(me); tmp.transform(o.matrix_world)
        me2 = bpy.data.meshes.new("tmp"); tmp.to_mesh(me2); tmp.free(); bm.from_mesh(me2); bpy.data.meshes.remove(me2)
        o.evaluated_get(dg).to_mesh_clear()
    t = BVHTree.FromBMesh(bm); bm.free(); return t
BVH = bvh_de([corpo]); BVH_TOPO = bvh_de([corpo, cab])
def osso(n): b = rig.data.bones[n]; return rig.matrix_world @ b.head_local, rig.matrix_world @ b.tail_local

# ------------------------------------------------------------------ LINHAS ---------------------------------------------
def suavizar(p, n=2, it=3):
    p = [v.copy() for v in p]
    for _ in range(it):
        q = [v.copy() for v in p]
        for i in range(1, len(p) - 1):
            a, b = max(0, i - n), min(len(p), i + n + 1); q[i] = sum((p[k] for k in range(a, b)), V((0, 0, 0))) / (b - a)
        p = q
    return p
def spline(cp, passo=0.08):
    """Catmull-Rom pelos pontos de controle (y, z) -> amostras com passo ~constante"""
    P = [V((0, y, z)) for y, z in cp]; P = [P[0]] + P + [P[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]; n = max(2, int((p2 - p1).length / passo))
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2]); return [(v.y, v.z) for v in out]
def projetar(yz, lado, folga=0.04):
    """ponto (y, z) do perfil -> superficie da pele vista do lado (+1 = esquerda/+X)"""
    res = []
    for y, z in yz:
        hit, nrm, idx, d = BVH.ray_cast(V((lado * 4.0, y, z)), V((-lado, 0, 0)), 8.0)
        if hit is not None and hit.x * lado > 0.05: res.append(hit + nrm * folga)
        else: res.append(None)
    # quebra em trechos continuos
    trechos, cur = [], []
    for p in res:
        if p is None:
            if len(cur) > 3: trechos.append(cur)
            cur = []
        else: cur.append(p)
    if len(cur) > 3: trechos.append(cur)
    return [suavizar(t) for t in trechos]
def espiral(cy, cz, r0, r1, voltas, passo=0.06, giro0=0.0):
    pts, n = [], int(voltas * 2 * math.pi * r0 / passo)
    for k in range(n + 1):
        u = k / n; a = giro0 + voltas * 2 * math.pi * u; r = r0 + (r1 - r0) * u
        pts.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    return pts
# perfil esquerdo (frente = -y). Ombro (escapula) ~ y -2.45, z 3.95
# r8h (17/11, "ainda nao esta igual"): espiral DESCE para a parte de cima da pata dianteira (sobre a perna, como na
#   referencia), menor e com mais voltas; dela saem: pescoco (sobe a frente), dorso (sob a crista ate a anca),
#   flanco (contorna a coxa e desce a traseira) e frente da pata dianteira.
CE = (-3.06, 2.62); R0 = 0.42                # r8l: simbolo na perna (sem costura de UV); a ESPIRAL e desenhada direto na mascara (uv_simbolo_r8 + mascara_r8)
def _p(a): return (CE[0] + R0 * math.cos(math.radians(a)), CE[1] + R0 * math.sin(math.radians(a)))
DESENHO = {
    "pescoco": spline([_p(110), (-3.15, 3.45), (-3.15, 4.10), (-3.20, 4.80)]),
    "dorso": spline([_p(60), (-2.62, 3.45), (-2.30, 4.10), (-1.65, 4.58), (-0.70, 4.75), (0.35, 4.66), (1.25, 4.80), (1.95, 4.62), (2.35, 4.22), (2.55, 3.75)]),
    "flanco": spline([_p(5), (-2.20, 2.80), (-1.55, 3.18), (-0.80, 3.35), (0.00, 3.52), (0.80, 3.78), (1.50, 3.95), (2.00, 3.75), (2.25, 3.30), (2.30, 2.80), (2.15, 2.30)]),
    "pata_frente": spline([_p(270), (-3.00, 1.95), (-2.95, 1.70)]),
}
LARG = {"pescoco": 0.045, "dorso": 0.045, "flanco": 0.05, "pata_frente": 0.045}

def linha_perna(nomes, lado, passo=0.10):
    pts = []
    for n in nomes: pts.append(osso(n)[0])
    pts.append(osso(nomes[-1])[1]); amostras = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; k = max(2, int((b - a).length / passo))
        amostras += [a.lerp(b, j / k) for j in range(k)]
    res = []
    for i, P in enumerate(amostras):
        T = (amostras[min(i + 1, len(amostras) - 1)] - amostras[max(i - 1, 0)]).normalized()
        fora = V((lado, 0, 0)); fora = (fora - T * fora.dot(T)).normalized(); fr = V((0, -1, 0)); fr = (fr - T * fr.dot(T)).normalized()
        d = (fora * 0.9 + fr * 0.25).normalized(); hit, nrm, idx, dd = BVH.ray_cast(P + d * 3, -d, 3.0)
        if hit is not None and (hit - P).length < 1.6: res.append(hit + nrm * 0.05)
    return suavizar(res)
def linha_cauda():
    pts = [osso("Cauda1")[0]] + [osso(n)[1] for n in ("Cauda1", "Cauda2", "Cauda3", "Cauda4")]; am = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; k = max(2, int((b - a).length / 0.1)); am += [a.lerp(b, j / k) for j in range(k)]
    res = []
    for P in am:
        hit, nrm, idx, dd = BVH.ray_cast(P + V((0, 0, 2.5)), V((0, 0, -1)), 3.0)
        if hit is not None: res.append(hit + nrm * 0.05)
    return suavizar(res)

def fita(pl, largura, nfix=None):
    """nfix: direcao 'para fora' fixa (lado do corpo) misturada a normal da pele -> a fita nao torce no pelo aspero"""
    vs, fs, n = [], [], len(pl)
    for i, p in enumerate(pl):
        T = (pl[min(i + 1, n - 1)] - pl[max(i - 1, 0)]).normalized()
        loc, nrm, idx, dist = BVH.find_nearest(p); N = nrm if nrm is not None else V((0, 0, 1))
        if nfix is not None: N = (N * 0.25 + nfix * 0.75).normalized()
        W = T.cross(N).normalized(); afina = min(1.0, i / 4.0, (n - 1 - i) / 4.0); w = largura * (0.35 + 0.65 * afina) / 2
        vs += [p + W * w, p - W * w]
        if i: k = 2 * i; fs.append((k - 2, k - 1, k + 1, k))
    return vs, fs
def objeto_de(nome, partes, mat):
    me = bpy.data.meshes.new(nome); bm = bmesh.new()
    for vs, fs in partes:
        vv = [bm.verts.new(v) for v in vs]
        for f in fs:
            try: bm.faces.new([vv[j] for j in f])
            except ValueError: pass
    bm.normal_update(); bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(mat); return ob
MAT_L = bpy.data.materials.new("M_Gelo_Linhas_r8"); MAT_L.use_nodes = True
pl_ = MAT_L.node_tree.nodes["Principled BSDF"]; pl_.inputs["Emission Color"].default_value = (0.3, 0.8, 1.0, 1); pl_.inputs["Emission Strength"].default_value = 2.0
partes = []; rel_l = {}
for lado in (1, -1):
    for nome, yz in DESENHO.items():
        for t in projetar(yz, lado): partes.append(fita(t, LARG[nome], V((lado, 0, 0)))); rel_l[nome] = rel_l.get(nome, 0) + len(t)
    for nomes in (["Antebraco", "Metacarpo"], ["Tibia", "Metatarso"]):          # r8g: continuam as linhas que descem da espiral e da coxa
        suf = "_E" if lado > 0 else "_D"; t = linha_perna([n + suf for n in nomes], lado)
        if len(t) > 3: partes.append(fita(t, 0.04, V((lado, 0, 0))))
t = linha_cauda()
if len(t) > 3: partes.append(fita(t, 0.04, V((0, 0, 1))))
linhas = objeto_de("Linhas_r8", partes, MAT_L)

# ------------------------------------------------------------------ ESPINHOS -------------------------------------------
MAT_E = bpy.data.materials.new("M_Gelo_Espinho_r8"); MAT_E.use_nodes = True
pe = MAT_E.node_tree.nodes["Principled BSDF"]
pe.inputs["Base Color"].default_value = (0.78, 0.92, 1.0, 1); pe.inputs["Roughness"].default_value = 0.08
pe.inputs["Transmission Weight"].default_value = 0.85; pe.inputs["IOR"].default_value = 1.31
pe.inputs["Emission Color"].default_value = (0.20, 0.75, 1.0, 1); pe.inputs["Emission Strength"].default_value = 0.0
ntE = MAT_E.node_tree; lw = ntE.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
mul = ntE.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 4.0
ntE.links.new(lw.outputs["Facing"], mul.inputs[0]); ntE.links.new(mul.outputs[0], pe.inputs["Emission Strength"])
pe.inputs["Alpha"].default_value = 0.8
try: MAT_E.surface_render_method = "BLENDED"
except Exception: pass
def cristal(bm, base, eixo, altura, raio, lados, giro):
    eixo = eixo.normalized(); a = eixo.orthogonal().normalized(); b = eixo.cross(a); anel = []
    for k in range(lados):
        ang = giro + 2 * math.pi * k / lados; rr = raio * (0.8 + 0.4 * ((k * 37 + int(giro * 10)) % 7) / 7)
        anel.append(bm.verts.new(base + (a * math.cos(ang) + b * math.sin(ang)) * rr))
    meio = [bm.verts.new(base + eixo * altura * 0.62 + (v.co - base) * 0.55) for v in anel]
    ponta = bm.verts.new(base + eixo * altura)
    for k in range(lados):
        k2 = (k + 1) % lados; bm.faces.new((anel[k], anel[k2], meio[k2], meio[k])); bm.faces.new((meio[k], meio[k2], ponta))
    bm.faces.new(list(reversed(anel)))
def ponto_dorso(y):
    hit, nrm, idx, dist = BVH_TOPO.ray_cast(V((0, y, 12)), V((0, 0, -1)), 20)
    return hit + V((0, 0, 0.10)), nrm
# posicoes da nuca (logo atras das orelhas) ao meio das costas; altura de pico na cernelha
# r8f (pedido 17/11: "cristais mais baixos e decrescentes"): maior na nuca e diminuindo sempre ate o meio das costas
_YS = [-3.40, -2.68, -1.96, -1.24, -0.52, 0.20, 0.92, 1.60]           # r8h: mais espaco entre os cristais (8, a cada ~0,72)
POS = [(y, round(1.35 - (1.35 - 0.32) * (k / (len(_YS) - 1)) ** 0.85, 3)) for k, y in enumerate(_YS)]
espinhos = []
for i, (y, h) in enumerate(POS):
    p, nrm = ponto_dorso(y)
    eixo = (V((0, 0, 1)) + V((0, 1.75, 0))).normalized()                       # r8h: ~60 graus para tras (penteados como na referencia)
    me = bpy.data.meshes.new("Espinho_%02d" % (i + 1)); bm = bmesh.new()
    j = (1.0, 0.97, 1.0, 0.97, 1.0, 0.97, 1.0, 0.97)[i]                # r8f: variacao leve que nunca inverte a ordem
    h = h * j; eixo = (eixo + V((0.10 * math.sin(2.3 * i), 0.10 * math.cos(1.7 * i), 0))).normalized()
    cristal(bm, V((0, 0, 0)), eixo, h, max(0.10, 0.17 * h), 6, 0.5 * i)          # central
    for k in range(2):                                                           # lascas pequenas na base
        sk = 1 if (i + k) % 2 else -1
        cristal(bm, V((0.22 * sk, -0.12 + 0.24 * k, -0.06)), (eixo + V((0.7 * sk, 0.4, 0.0))).normalized(), 0.22 * h + 0.08, 0.05 + 0.04 * h, 5, 0.9 * i + k)
    if h > 0.6:                                                                  # laterais em leque (lado E e D)
        for lado in (1, -1):
            e2 = (eixo + V((0.50 * lado, 0.25, -0.05))).normalized()
            cristal(bm, V((0.16 * lado, 0.10, -0.05)), e2, h * (0.62 if i % 2 else 0.55), max(0.07, 0.12 * h), 5, 1.3 * i + lado)
    if h > 1.2:                                                                  # ponta secundaria atras
        cristal(bm, V((0.05 * (1 if i % 2 else -1), 0.22, -0.02)), (eixo + V((0, 0.35, 0))).normalized(), h * 0.45, 0.09 * h, 5, 2.1 * i)
    base = p - eixo * 0.18 * h
    bm.normal_update(); bm.to_mesh(me); bm.free()
    for f in me.polygons: f.use_smooth = False
    ob = bpy.data.objects.new(me.name, me); bpy.context.scene.collection.objects.link(ob); ob.data.materials.append(MAT_E)
    melhor, dm = None, 1e9
    for b in rig.data.bones:
        if b.name.startswith(("Coluna", "Pescoco", "Quadril")):
            h0, t0 = osso(b.name); ab = t0 - h0; u = max(0, min(1, (base - h0).dot(ab) / ab.length_squared)); d = (h0 + ab * u - base).length
            if d < dm: dm, melhor = d, b.name
    ob.parent = rig; ob.parent_type = "BONE"; ob.parent_bone = melhor; ob.matrix_world = Matrix.Translation(base)
    espinhos.append({"nome": ob.name, "osso": melhor, "base": [round(c, 4) for c in base], "eixo": [round(c, 4) for c in eixo], "altura": h})
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
rel = {"versao": "r8", "espinhos": espinhos, "espinhos_tris": sum(tris(bpy.data.objects[e["nome"]]) for e in espinhos),
       "linhas_pontos": rel_l, "linhas_tris": tris(linhas)}
json.dump(rel, open(os.path.join(EXP, "boreal_fx_r8.json"), "w"), indent=1); print("R8", json.dumps({k: v for k, v in rel.items() if k != "espinhos"}))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "CR_LoboArtico_Boreal_r8.blend")); print("BOREAL_R8_OK")
