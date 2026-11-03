"""CR_UrsoSilvestre — etapa 1: corpo (pele), rosto, boca recortada, dentes, lingua, olhos e garras, em POSE NEUTRA.
Referencia: ref/urso-silvestre-referencia.png (ver asset-brief.md). 1 unidade = 1 stud; frente = -Y; pes em Z = 0;
simetrico em X (esquerda do urso = +X). Medidas da referencia sao aproximadas (perspectiva) ou # inferido.
Corpo = metaballs (volumes) -> ajustes de massa -> remesh voxel -> escultura do rosto -> boca por boolean.
Uso: blender -b --factory-startup -P criar_urso_corpo.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, Euler

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; V = Vector; rnd = random.Random(11)
def lerp(a, b, t): return a + (b - a) * t
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def gauss(x, c, w): return math.exp(-((x - c) / w) ** 2)

# ------------------------------------------------------------------ volumes (metaballs) — PELE, sem pelo. (centro, semi-eixos [, rot graus])
# k = 0,574: raio de superficie de um elemento isolado por unidade de "radius" (medido); elementos sobrepostos somam.
K_MB = 0.574
TRONCO = [((0, -2.90, 6.00), (2.20, 1.90, 2.05)),                  # torax / ombros
          ((0, -3.10, 7.05), (1.55, 1.55, 1.05)),                  # corcova escapular
          ((0, -0.50, 5.75), (2.35, 2.30, 1.95)), ((0, 1.10, 5.20), (2.15, 2.10, 1.80)),   # ventre pesado
          ((0, 2.80, 5.85), (2.10, 1.90, 1.70)), ((0, 4.55, 5.80), (2.00, 1.75, 1.65)),   # lombo / garupa
          ((0, 5.85, 5.55), (1.50, 0.95, 1.30)), ((0, 6.75, 5.45), (0.36, 0.50, 0.36)),   # traseira / cauda curta
          ((0, -4.75, 6.30), (1.45, 1.20, 1.40)), ((0, -5.65, 6.42), (1.18, 0.85, 1.12))]  # pescoco grosso
CABECA = [((0, -6.65, 6.55), (1.08, 0.95, 0.92)),                  # cranio largo
          ((0.66, -7.05, 6.15), (0.56, 0.60, 0.55)), ((-0.66, -7.05, 6.15), (0.56, 0.60, 0.55)),   # bochechas/zigomas
          ((0, -7.22, 6.85), (0.72, 0.55, 0.38)),                  # testa (stop)
          ((0, -8.05, 6.27), (0.58, 0.75, 0.46)), ((0, -8.62, 6.22), (0.50, 0.38, 0.40)),  # focinho curto e largo
          ((0, -8.92, 6.26), (0.33, 0.16, 0.24)),                  # nariz
          ((0, -7.95, 5.72), (0.52, 0.82, 0.34)), ((0, -8.50, 5.74), (0.38, 0.28, 0.25)),  # mandibula funda / queixo
          ((0.78, -6.50, 7.42), (0.30, 0.14, 0.28), (0, 0, 25)), ((-0.78, -6.50, 7.42), (0.30, 0.14, 0.28), (0, 0, -25))]  # orelhas
def perna(s, dianteira):
    """juntas (ponto, raio) ate o pe; cotovelo para tras, joelho para a frente; plantigrado"""
    if dianteira:
        return [(V((1.55 * s, -2.90, 6.10)), 1.35), (V((1.80 * s, -2.55, 3.65)), 1.05), (V((1.78 * s, -3.15, 1.00)), 0.82)]
    return [(V((1.60 * s, 4.40, 5.80)), 1.50), (V((1.90 * s, 3.40, 3.00)), 1.08), (V((1.78 * s, 4.70, 0.62)), 0.68)]
def massas_perna(s, dianteira):
    if dianteira:
        return [((1.75 * s, -3.05, 4.65), (1.20, 1.30, 1.40)), ((1.80 * s, -2.95, 2.35), (1.02, 1.08, 1.15)),
                ((1.82 * s, -3.75, 0.42), (0.95, 1.02, 0.42))]                                         # pe largo
    return [((1.85 * s, 4.00, 4.45), (1.45, 1.70, 1.60)), ((1.82 * s, 4.05, 1.85), (0.92, 1.00, 1.05)),
            ((1.80 * s, 3.95, 0.40), (0.86, 1.25, 0.40))]
PE_FRENTE = {True: -4.55, False: 2.85}                                # y da ponta dos dedos
def dedos(s, dianteira):
    """5 dedos em arco; o interno (lado do corpo) e o menor. Retorna [(base, raio), (ponta, raio)]"""
    pe = massas_perna(s, dianteira)[2][0]; out = []
    for k, dx in enumerate((-0.66, -0.33, 0.0, 0.33, 0.64)):
        yf = PE_FRENTE[dianteira] + 0.16 * (abs(dx) / 0.66) ** 1.5
        r = (0.19 if k else 0.15) * (1.0 if dianteira else 0.92)
        out.append([(V((pe[0] + dx * s, yf + 0.30, 0.30)), r), (V((pe[0] + dx * 1.08 * s, yf, 0.22)), r * 0.85)])
    return out

mb = bpy.data.metaballs.new("CR_Urso_Volume"); mbo = bpy.data.objects.new("CR_Urso_Volume", mb); sc.collection.objects.link(mbo)
mb.resolution = mb.render_resolution = 0.09
def bola(c, eixos, rot=(0, 0, 0)):
    e = mb.elements.new(type="ELLIPSOID"); m = max(eixos); e.co = c; e.radius = m / K_MB
    e.size_x, e.size_y, e.size_z = eixos[0] / m, eixos[1] / m, eixos[2] / m
    e.rotation = Euler([math.radians(a) for a in rot]).to_quaternion()
def segmento(a, b, ra, rb):
    """capsula de a ate b (raio medio) + bolas nas juntas"""
    d = b - a; e = mb.elements.new(type="CAPSULE"); r = (ra + rb) * 0.5
    e.co = (a + b) * 0.5; e.radius = r * 0.92 / K_MB; e.size_x = d.length * 0.5
    e.rotation = V((1, 0, 0)).rotation_difference(d.normalized())
for item in TRONCO + CABECA: bola(*item)
for s in (1, -1):
    for dian in (True, False):
        j = perna(s, dian)
        for (a, ra), (b, rb) in zip(j, j[1:]): segmento(a, b, ra * 0.9, rb * 0.9)
        for c, e_ in massas_perna(s, dian): bola(c, e_)
        for (b0, r0), (b1, r1) in dedos(s, dian): segmento(b0, b1, r0, r1)
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(mbo.evaluated_get(dg)); me.name = "CR_Urso_Corpo"
ob = bpy.data.objects.new("CR_Urso_Corpo", me); sc.collection.objects.link(ob); bpy.data.objects.remove(mbo)
zmin = min(v.co.z for v in me.vertices)
for v in me.vertices:                                                  # pes no chao (Z=0) e sola achatada
    v.co.z -= zmin
    if v.co.z < 0.20: v.co.z = 0.20 * suave(v.co.z / 0.20) ** 0.5 if v.co.z > 0.02 else 0.0
bpy.context.view_layer.objects.active = ob; ob.select_set(True)

# ------------------------------------------------------------------ ajustes de massa (referencia: corcova alta, barriga pesada)
for v in ob.data.vertices:
    p = v.co; x, y, z = p
    p.z += 0.25 * gauss(y, -3.1, 1.1) * suave((z - 7.2) / 0.8) * (1 - suave(abs(x) / 1.8))         # corcova
    if y < -6.1 and z > 6.9: p.x *= 1 + 0.10 * gauss(y, -6.7, 0.45) * suave((z - 6.9) / 0.4)       # cranio largo atras
rm = ob.modifiers.new("Remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.055; rm.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=rm.name)
sm = ob.modifiers.new("Liso", "SMOOTH"); sm.factor = 0.5; sm.iterations = 8
bpy.ops.object.modifier_apply(modifier=sm.name)

# ------------------------------------------------------------------ rosto: olhos, sobrancelha, narinas, labio superior
def bater(origem, dirv, dist=5.0):
    ok, hit, nrm, _ = ob.ray_cast(origem, dirv.normalized(), distance=dist)
    return (hit, nrm) if ok else (None, None)
OLHO, _n = bater(V((0.46, -10.0, 6.70)), V((0, 1, 0)))
OLHO = (OLHO - _n * 0.06) if OLHO else V((0.55, -7.85, 6.68))
NARIZ, _ = bater(V((0, -10.5, 6.20)), V((0, 1, 0)))
NARIZ = NARIZ or V((0, -9.45, 6.20))
print("URSO_OLHO", tuple(round(c, 3) for c in OLHO), "NARIZ", tuple(round(c, 3) for c in NARIZ))
for v in ob.data.vertices:
    p, nrm = v.co, v.normal; x, y, z = p
    for s_ in (1, -1):
        d = (p - V((OLHO.x * s_, OLHO.y, OLHO.z))).length
        if d < 0.26: p -= nrm * 0.07 * (1 - d / 0.26) ** 2                                     # orbita
        d = (p - V((OLHO.x * s_ * 0.92, OLHO.y + 0.05, OLHO.z + 0.20))).length
        if d < 0.30: p += nrm * 0.05 * (1 - d / 0.30) ** 2                                     # arco da sobrancelha
        d = (p - V((0.13 * s_, NARIZ.y + 0.02, NARIZ.z + 0.02))).length
        if d < 0.11: p -= nrm * 0.07 * (1 - d / 0.11) ** 2                                     # narinas
        d = (p - V((0.68 * s_, -6.50, 7.56))).length                                           # concha da orelha (frente)
        if d < 0.30 and nrm.y < 0.2: p -= nrm * 0.10 * (1 - d / 0.30) ** 2
    if y < NARIZ.y + 0.25 and z < NARIZ.z - 0.12 and abs(x) < 0.08:                            # sulco do labio superior
        p.y += 0.03 * (1 - abs(x) / 0.08)
ob.data.update()

# ------------------------------------------------------------------ boca: fenda labial ate o canto + cavidade (boolean)
CANTO_Y = -7.25
def labio_z(y): return 5.98 + 0.04 * suave((y + 9.1) / 1.6)
def fenda():
    m = bpy.data.meshes.new("Fenda"); b = bmesh.new(); N = 14; secs = []
    for i in range(N + 1):
        t = i / N; y = lerp(-10.2, CANTO_Y, t); z = labio_z(y)
        meia = 0.016 * (1 - suave((t - 0.80) / 0.20)) + 0.003                                  # afina no canto da boca
        lx = 1.6
        secs.append([b.verts.new((xx, y, z + zz)) for xx, zz in ((-lx, -meia), (lx, -meia), (lx, meia), (-lx, meia))])
    for a, c in zip(secs, secs[1:]):
        for k in range(4): b.faces.new((a[k], a[(k + 1) % 4], c[(k + 1) % 4], c[k]))
    b.faces.new(secs[0][::-1]); b.faces.new(secs[-1])
    bmesh.ops.recalc_face_normals(b, faces=b.faces)
    b.to_mesh(m); b.free(); o = bpy.data.objects.new("Fenda", m); sc.collection.objects.link(o); return o
def elipsoide_obj(nome, c, r):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=c, segments=32, ring_count=16)
    o = bpy.context.object; o.name = nome; o.scale = r; bpy.ops.object.transform_apply(scale=True); return o
CORTES = [fenda(), elipsoide_obj("Cavidade", (0, -8.15, labio_z(-8.15) - 0.02), (0.42, 0.70, 0.14))]
def mat_simples(nome, cor, rug=0.6):
    m = bpy.data.materials.new(nome); m.use_nodes = True if m.node_tree is None else m.use_nodes
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = cor; b.inputs["Roughness"].default_value = rug
    return m
M_BOCA = mat_simples("M_Urso_Boca", (0.30, 0.045, 0.045, 1), 0.35)
ob.data.materials.append(bpy.data.materials.new("M_Urso_Pele_tmp"))
for c in CORTES: c.data.materials.append(M_BOCA)
for c in CORTES:
    bo = ob.modifiers.new("Boca", "BOOLEAN"); bo.operation = "DIFFERENCE"; bo.solver = "EXACT"; bo.object = c
    bo.material_mode = "TRANSFER"
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier=bo.name)
    bpy.data.objects.remove(c)
print("URSO_CORPO faces", len(ob.data.polygons), "boca", sum(1 for p in ob.data.polygons if p.material_index == 1))

# ------------------------------------------------------------------ pecas rigidas: dentes, lingua, olhos, garras
def tubo(pts, r0, nome, expo=1.0, base_r=None):
    m = bpy.data.meshes.new(nome); o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = pts[0]
    b = bmesh.new(); vs = [b.verts.new(p - pts[0]) for p in pts]
    for a, c in zip(vs, vs[1:]): b.edges.new((a, c))
    b.to_mesh(m); b.free()
    k = o.modifiers.new("Pele", "SKIN"); k.use_smooth_shade = True
    n = len(pts)
    for i, d in enumerate(m.skin_vertices[0].data):
        r = r0 * (1 - i / (n - 1)) ** expo + 0.006; d.radius = (r, r * 0.85); d.use_root = i == 0
    s2 = o.modifiers.new("Sub", "SUBSURF"); s2.levels = s2.render_levels = 2
    return o
def borda_arcada(y, z, s, recuo):
    """ponto da arcada dentaria: superficie externa do focinho na altura z, recuada para dentro"""
    hit, nrm = bater(V((0, y, z)), V((s, 0, 0)), 3.0)
    if hit is None: return None
    # o raio sai de dentro: o primeiro acerto e a parede interna da cavidade ou a pele; usa o mais externo
    ult = hit
    for _ in range(4):
        h2, _n2 = bater(ult + V((s * 0.01, 0, 0)), V((s, 0, 0)), 3.0)
        if h2 is None: break
        ult = h2
    return ult - V((s * recuo, 0, 0))
DENTES = []
for sup in (True, False):
    zg = labio_z(-8.6) + (0.024 if sup else -0.024); dz = -1 if sup else 1
    for s in (1, -1):
        for k, (y, comp, r) in enumerate(((-8.80, 0.10, 0.045), (-8.74, 0.11, 0.050), (-8.62, 0.27 if sup else 0.22, 0.085),
                                           (-8.34, 0.08, 0.06), (-8.06, 0.09, 0.07), (-7.78, 0.10, 0.08))):
            p = borda_arcada(y, labio_z(y) + (0.06 if sup else -0.06), s, 0.12 if k != 2 else 0.20)
            if p is None: continue
            if k == 0: p.x *= 0.35
            if k == 1: p.x *= 0.7
            p.z = labio_z(y) + (0.02 if sup else -0.02) - dz * 0.06                             # raiz dentro da gengiva
            ponta = p + V((0, -0.02 if k == 2 else 0, dz * (comp + 0.06)))
            if k == 2: ponta += V((0, 0.03 if sup else -0.03, 0))                               # caninos curvos
            DENTES.append(tubo([p, lerp(p, ponta, 0.6), ponta], r, "Dente_" + ("Sup" if sup else "Inf"), expo=0.8))
LINGUA = elipsoide_obj("Lingua", (0, -8.10, labio_z(-8.10) - 0.10), (0.30, 0.56, 0.07))
OLHOS = []
for s in (1, -1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(OLHO.x * s, OLHO.y, OLHO.z), segments=24, ring_count=12)
    o = bpy.context.object; o.name = "Olho"; o.scale = (0.85, 1.0, 0.9); bpy.ops.object.shade_smooth(); OLHOS.append(o)
GARRAS = []
for s in (1, -1):
    for dian in (True, False):
        L = 0.95 if dian else 0.60
        for d in dedos(s, dian):
            ponta = d[-1][0] - V((0, 0, zmin)); dirv = (d[-1][0] - d[0][0]); dirv.z = 0; dirv.normalize()
            pts = [ponta + dirv * 0.05 + V((0, 0, 0.08)), ponta + dirv * L * 0.40 + V((0, 0, 0.10)),
                   ponta + dirv * L * 0.75 + V((0, 0, 0.02)), ponta + dirv * L + V((0, 0, 0.03 - ponta.z))]
            GARRAS.append(tubo(pts, 0.17 if dian else 0.13, "Garra", expo=1.25))

# ------------------------------------------------------------------ materiais (procedurais; o bake vem na malha de jogo)
def n(nt, t, **kw):
    x = nt.nodes.new(t)
    for k, v in kw.items(): setattr(x, k, v)
    return x
def rampa(nt, L, ent, pares):
    r = n(nt, "ShaderNodeValToRGB"); L.new(ent, r.inputs[0]); el = r.color_ramp.elements
    el[0].position, el[0].color = pares[0]; el[1].position, el[1].color = pares[-1]
    for pos, cor in pares[1:-1]: e = el.new(pos); e.color = cor
    return r
def mr(nt, L, ent, a, b_, c=0.0, d=1.0):
    x = n(nt, "ShaderNodeMapRange"); x.inputs[1].default_value = a; x.inputs[2].default_value = b_
    x.inputs[3].default_value = c; x.inputs[4].default_value = d; L.new(ent, x.inputs[0]); return x.outputs[0]
def mix(nt, L, fac, a, b_):
    x = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(fac, x.inputs["Factor"])
    for i, c in ((6, a), (7, b_)):
        if isinstance(c, tuple): x.inputs[i].default_value = c
        else: L.new(c, x.inputs[i])
    return x.outputs[2]
def op(nt, L, o_, a, b_=None, v=None):
    x = n(nt, "ShaderNodeMath", operation=o_); L.new(a, x.inputs[0])
    if b_ is not None: L.new(b_, x.inputs[1])
    if v is not None: x.inputs[1].default_value = v
    return x.outputs[0]
def mat_pele():
    m = ob.data.materials[0]; m.name = "M_Urso_Pele"; m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]; L = nt.links
    tc = n(nt, "ShaderNodeAttribute", attribute_name="Pos_Repouso"); pos = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Vector"], pos.inputs[0])
    ru = n(nt, "ShaderNodeTexNoise"); ru.inputs["Scale"].default_value = 1.6; ru.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Vector"], ru.inputs["Vector"])
    fino = n(nt, "ShaderNodeTexNoise"); fino.inputs["Scale"].default_value = 22; fino.inputs["Detail"].default_value = 4
    est = n(nt, "ShaderNodeVectorMath", operation="MULTIPLY"); est.inputs[1].default_value = (3.0, 1.0, 0.35)
    L.new(tc.outputs["Vector"], est.inputs[0]); L.new(est.outputs[0], fino.inputs["Vector"])        # estrias de pelo
    medio = rampa(nt, L, ru.outputs["Fac"], [(0.35, (0.105, 0.050, 0.022, 1)), (0.65, (0.20, 0.105, 0.048, 1))])
    escuro = (0.040, 0.020, 0.010, 1)
    baixo = mr(nt, L, pos.outputs["Z"], 3.4, 1.0)                                                # patas e baixo mais escuros
    cor = mix(nt, L, op(nt, L, "MULTIPLY", baixo, v=0.75), medio.outputs["Color"], escuro)
    cab = mr(nt, L, pos.outputs["Y"], -6.4, -7.4)                                                # rosto dourado-claro
    cor = mix(nt, L, op(nt, L, "MULTIPLY", cab, v=0.65), cor, (0.34, 0.20, 0.10, 1))
    foc = op(nt, L, "MULTIPLY", mr(nt, L, pos.outputs["Y"], -7.8, -8.4), mr(nt, L, pos.outputs["Z"], 6.80, 6.50))
    cor = mix(nt, L, op(nt, L, "MULTIPLY", foc, v=0.6), cor, (0.42, 0.27, 0.15, 1))              # focinho claro
    axn = n(nt, "ShaderNodeMath", operation="ABSOLUTE"); L.new(pos.outputs["X"], axn.inputs[0])
    nariz = op(nt, L, "MULTIPLY", op(nt, L, "MULTIPLY", mr(nt, L, pos.outputs["Y"], NARIZ.y + 0.20, NARIZ.y + 0.12), mr(nt, L, pos.outputs["Z"], 6.06, 6.14)), mr(nt, L, axn.outputs[0], 0.36, 0.30))
    cor = mix(nt, L, nariz, cor, (0.012, 0.010, 0.010, 1))
    lab = op(nt, L, "MULTIPLY", mr(nt, L, pos.outputs["Y"], -7.4, -7.7),
             op(nt, L, "SUBTRACT", mr(nt, L, pos.outputs["Z"], labio_z(-8.6) - 0.20, labio_z(-8.6) - 0.06),
                mr(nt, L, pos.outputs["Z"], labio_z(-8.6) + 0.07, labio_z(-8.6) + 0.17)))
    cor = mix(nt, L, op(nt, L, "MAXIMUM", lab, v=0.0), cor, (0.02, 0.014, 0.012, 1))            # labios escuros
    estr = mix(nt, L, op(nt, L, "MULTIPLY", fino.outputs["Fac"], v=0.6), cor, (0.0, 0.0, 0.0, 1))
    L.new(estr, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.85
    rn = mr(nt, L, nariz, 0, 1, 0.85, 0.30); L.new(rn, b.inputs["Roughness"])
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.03
    L.new(fino.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m
def mat_marfim(nome, base, ponta, rug, comp):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; L = nt.links
    tc = n(nt, "ShaderNodeTexCoord"); dist = n(nt, "ShaderNodeVectorMath", operation="LENGTH"); L.new(tc.outputs["Object"], dist.inputs[0])
    gr = rampa(nt, L, mr(nt, L, dist.outputs["Value"], 0, comp), [(0.0, base), (1.0, ponta)])
    L.new(gr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rug
    return m
def mat_olho():
    m = bpy.data.materials.new("M_Urso_Olho"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; L = nt.links
    tc = n(nt, "ShaderNodeTexCoord"); sep = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    r = n(nt, "ShaderNodeVectorMath", operation="LENGTH"); L.new(tc.outputs["Object"], r.inputs[0])
    # pupila redonda no polo frontal (-Y local) ; iris ambar
    py = mr(nt, L, sep.outputs["Y"], -0.095, -0.115)
    cor = mix(nt, L, py, (0.55, 0.26, 0.04, 1), (0.01, 0.006, 0.004, 1))
    L.new(cor, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.08
    return m
MP = mat_pele(); ob.data.materials.append(M_BOCA) if len(ob.data.materials) < 2 else None
MD = mat_marfim("M_Urso_Dente", (0.62, 0.55, 0.42, 1), (0.92, 0.88, 0.78, 1), 0.35, 0.25)
MG = mat_marfim("M_Urso_Garra", (0.16, 0.12, 0.08, 1), (0.86, 0.80, 0.66, 1), 0.40, 0.9)
MO = mat_olho(); ML = mat_simples("M_Urso_Lingua", (0.55, 0.12, 0.13, 1), 0.4)
for o in DENTES: o.data.materials.append(MD)
for o in GARRAS: o.data.materials.append(MG)
for o in OLHOS: o.data.materials.append(MO)
LINGUA.data.materials.append(ML)
col = bpy.data.collections.new("CR_Urso"); sc.collection.children.link(col)
for o in [ob, LINGUA] + DENTES + OLHOS + GARRAS:
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)
for o in DENTES + GARRAS:                                  # aplica pele/subsurf: pecas finais simples
    bpy.context.view_layer.objects.active = o
    for m_ in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m_.name)

# posicao de repouso gravada na malha: o material nao muda quando a malha e posada/deformada
at = ob.data.attributes.new("Pos_Repouso", "FLOAT_VECTOR", "POINT")
for i, v in enumerate(ob.data.vertices): at.data[i].vector = v.co
# medidas
zs = [v.co.z for v in ob.data.vertices]; ys = [v.co.y for v in ob.data.vertices]; xs = [v.co.x for v in ob.data.vertices]
omb = max(v.co.z for v in ob.data.vertices if -4.0 < v.co.y < -2.0)
print("URSO_MEDIDAS pele: corcova %.2f comprimento %.2f largura %.2f altura %.2f" % (omb, max(ys) - min(ys), max(xs) - min(xs), max(zs)))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Urso_corpo.blend"))
print("URSO_OK")
