"""
Biblioteca de blockout de criaturas (OPERACAO CREATURE BLOCKOUT).
Tecnica da skill blender-image-to-3d ("fused organic base"): massas anatomicas (elipsoides de musculo,
cadeias de membros com articulacoes, mechas) -> uniao por voxel remesh numa MASSA UNICA -> suavizacao
das juncoes -> reducao ao orcamento. Partes rigidas (chifres, garras, cristais, ferrao) ficam separadas.

Unidade = 1 stud (Roblox, Scale Unit = Stud). Frente = -Y, Z para cima, chao em z = 0, centro em x = 0.
Uso (headless):  blender -b --factory-startup -P build_<especie>.py -- --pose neutra|referencia --out <arquivo.blend>
"""
import bpy, bmesh, math, os, sys, argparse
from mathutils import Vector, Matrix, Euler, Quaternion

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # .../Blockouts


# ARQUIVO E COLECOES ---------------------------------------------------------------------------

def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--pose", default="neutra", choices=["neutra", "referencia"])
    p.add_argument("--out", required=True)
    return p.parse_args(a)


def cena_nova():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc["unidade"] = "1 unidade = 1 stud"
    sc["frente"] = "-Y"
    return sc


def colecao(especie):
    """CREATURES / BLOCKOUTS / <especie>"""
    def filho(pai, nome):
        c = bpy.data.collections.get(nome)
        if c is None:
            c = bpy.data.collections.new(nome)
            pai.children.link(c)
        return c
    cr = filho(bpy.context.scene.collection, "CREATURES")
    bl = filho(cr, "BLOCKOUTS")
    return filho(bl, especie)


def salvar(caminho):
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(caminho))
    print("SALVO", caminho)


# PRIMITIVAS EM UM BMESH UNICO (sobrepostas; o remesh faz a uniao) -------------------------------

def elipsoide(bm, c, r, rot=(0, 0, 0), u=32, v=16):
    """c = centro, r = (rx, ry, rz) raios reais, rot = graus (X, Y, Z)."""
    tmp = bmesh.new()
    bmesh.ops.create_uvsphere(tmp, u_segments=u, v_segments=v, radius=1.0)
    m = Matrix.Translation(Vector(c)) @ Euler([math.radians(a) for a in rot]).to_matrix().to_4x4() @ Matrix.Diagonal((r[0], r[1], r[2], 1))
    bmesh.ops.transform(tmp, matrix=m, verts=tmp.verts)
    _anexar(bm, tmp)


def segmento(bm, a, b, ra, rb, seg=24):
    """Tronco de cone de a ate b (raios ra, rb) + esferas nas pontas: articulacao lisa."""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    if L < 1e-6:
        return
    tmp = bmesh.new()
    bmesh.ops.create_cone(tmp, cap_ends=True, cap_tris=False, segments=seg, radius1=ra, radius2=rb, depth=L)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    m = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
    bmesh.ops.transform(tmp, matrix=m, verts=tmp.verts)
    _anexar(bm, tmp)


def cadeia(bm, pts, seg=24):
    """pts = [(x, y, z, r), ...]: membro/cauda/pescoco com juntas arredondadas."""
    for p in pts:
        elipsoide(bm, p[:3], (p[3], p[3], p[3]), u=seg, v=seg // 2)
    for p, q in zip(pts, pts[1:]):
        segmento(bm, p[:3], q[:3], p[3], q[3], seg)


def _anexar(bm, tmp):
    me = bpy.data.meshes.new("_tmp")
    tmp.to_mesh(me)
    tmp.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


# POSE DOS MEMBROS ANTES DA FUSAO --------------------------------------------------------------

def girar_cadeia(pts, pivo, graus, eixo="X"):
    """Gira os pontos de um membro em torno do pivo (graus + = para tras, eixo X)."""
    R = Matrix.Rotation(math.radians(graus), 4, eixo)
    pv = Vector(pivo)
    out = []
    for p in pts:
        v = R @ (Vector(p[:3]) - pv) + pv
        out.append((v.x, v.y, v.z) + tuple(p[3:]))
    return out


def posar_membros(membros, passada, pose):
    """membros = [{"pivo", "cad": [(x,y,z,r)], "musc": [(c, r, rot)], "chave"}]. Na pose 'referencia' gira cada
    membro no pivo (graus de passada[chave], + = para tras) e o desce ate o apoio tocar o chao."""
    for m in membros:
        g = passada.get(m["chave"], 0) if pose == "referencia" else 0
        if not g:
            continue
        m["cad"] = girar_cadeia(m["cad"], m["pivo"], g)
        R = Matrix.Rotation(math.radians(g), 4, "X")
        pv = Vector(m["pivo"])
        m["musc"] = [(tuple(R @ (Vector(c) - pv) + pv), r, (rot[0] + g, rot[1], rot[2])) for c, r, rot in m["musc"]]
        if "pe" in m:                                   # centro do pe (pata/casco) gira junto
            m["pe"] = tuple(R @ (Vector(m["pe"]) - pv) + pv)
        zmin = min([p[2] - p[3] for p in m["cad"]] + [c[2] - r[2] for c, r, rot in m["musc"]] + ([m["pe"][2]] if "pe" in m else []))
        m["cad"] = [(p[0], p[1], p[2] - zmin) + tuple(p[3:]) for p in m["cad"]]
        m["musc"] = [((c[0], c[1], c[2] - zmin), r, rot) for c, r, rot in m["musc"]]
        if "pe" in m:
            m["pe"] = (m["pe"][0], m["pe"][1], m["pe"][2] - zmin)
    return membros


# REFINAMENTO (fase 3 da skill: formas) -------------------------------------------------------

MATERIAIS = {   # papel -> (cor base neutra sRGB linear aprox., rugosidade); nomes = slots futuros no Roblox
    "pele": ((0.42, 0.36, 0.30, 1), 0.75), "pelo": ((0.45, 0.38, 0.30, 1), 0.9), "escama": ((0.30, 0.31, 0.26, 1), 0.6),
    "garra": ((0.12, 0.11, 0.10, 1), 0.35), "osso": ((0.62, 0.58, 0.50, 1), 0.5), "membrana": ((0.36, 0.30, 0.27, 1), 0.7),
    "cristal": ((0.62, 0.72, 0.80, 1), 0.08), "olho": ((0.05, 0.04, 0.03, 1), 0.05), "quitina": ((0.20, 0.15, 0.11, 1), 0.4),
}


class Partes:
    """Acumula partes rigidas por PAPEL DE MATERIAL (garra, osso, cristal, olho...) para virar um objeto por material."""
    def __init__(self):
        self.bm = {}

    def __call__(self, papel):
        if papel not in self.bm:
            self.bm[papel] = bmesh.new()
        return self.bm[papel]

    def criar(self, especie, col):
        obs = []
        for papel, b in self.bm.items():
            if len(b.verts) == 0:
                b.free(); continue
            ob = rigida("%s_%s_Blockout" % (especie, papel.capitalize()), b, col)
            material_papel(ob, papel)
            obs.append(ob)
        return obs


def material_papel(ob, papel, cor=None):
    nome = "MAT_" + papel.capitalize()
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    c, r = MATERIAIS.get(papel, ((0.5, 0.5, 0.5, 1), 0.6))
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = cor or c
        bsdf.inputs["Roughness"].default_value = r
        if papel == "cristal":
            bsdf.inputs["Transmission Weight"].default_value = 0.4
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob["papel_material"] = papel
    return m


def garra(rg, base, direcao, comp, r0, curva=0.35, seg=8):
    """Garra curva (unha/garra): sai de 'base' na 'direcao', curvando para baixo."""
    b = Vector(base); d = Vector(direcao).normalized()
    meio = b + d * comp * 0.55 + Vector((0, 0, -comp * curva * 0.3))
    fim = b + d * comp + Vector((0, 0, -comp * curva))
    chifre(rg, b, [meio, fim], r0, 0.02, seg=seg)


def pata_digitigrada(bm, rg, c, s, larg, comp, dedos=4, garra_comp=0.25, frente=(0, -1, 0)):
    """Pata de canideo/felino: almofada central + dedos em arco + garras (rigidas). c = centro da almofada no chao."""
    c = Vector(c); f = Vector(frente).normalized()
    elipsoide(bm, c + Vector((0, 0, larg * 0.35)), (larg * 0.55, comp * 0.5, larg * 0.38))
    pontas = []
    for i in range(dedos):
        t = (i / (dedos - 1) - 0.5) if dedos > 1 else 0
        p = c + f * comp * (0.55 - abs(t) * 0.25) + Vector((t * larg * 1.05, 0, larg * 0.22))
        elipsoide(bm, p, (larg * 0.22, larg * 0.28, larg * 0.22), u=12, v=6)
        pontas.append(p)
        if garra_comp:
            garra(rg, p + f * larg * 0.18 + Vector((0, 0, 0.02)), f + Vector((0, 0, -0.2)), garra_comp, larg * 0.1)
    return pontas


def pe_plantigrado(bm, rg, c, s, larg, comp, garra_comp=0.8):
    """Pe de urso: sola larga apoiada inteira, 5 dedos, garras longas (o painel destaca)."""
    c = Vector(c)
    elipsoide(bm, c + Vector((0, 0, larg * 0.3)), (larg * 0.6, comp * 0.55, larg * 0.32))
    for i in range(5):
        t = i / 4 - 0.5
        p = c + Vector((t * larg * 1.1, -comp * (0.5 - abs(t) * 0.15), larg * 0.28))
        elipsoide(bm, p, (larg * 0.2, larg * 0.24, larg * 0.2), u=12, v=6)
        garra(rg, p + Vector((0, -larg * 0.15, 0)), (0, -1, -0.25), garra_comp, larg * 0.09, curva=0.45)


def casco_fendido(rg, c, larg, alt):
    """Casco de bisao: duas metades (material garra/casco)."""
    c = Vector(c)
    for t in (-1, 1):
        elipsoide(rg, c + Vector((t * larg * 0.26, -larg * 0.05, alt * 0.5)), (larg * 0.26, larg * 0.42, alt * 0.55), u=14, v=7)


def pe_reptil(bm, rg, c, s, larg, comp, dedos=5, garra_comp=0.4, abertura=50):
    """Pe de reptil espalhado: palma baixa + dedos abertos em leque + garras."""
    c = Vector(c)
    elipsoide(bm, c + Vector((0, 0, larg * 0.22)), (larg * 0.55, comp * 0.45, larg * 0.22))
    for i in range(dedos):
        a = math.radians(-abertura / 2 + abertura * i / (dedos - 1))
        d = Vector((math.sin(a) * s, -math.cos(a), 0))
        p0 = c + d * comp * 0.3 + Vector((0, 0, larg * 0.18))
        p1 = c + d * comp * 0.85 + Vector((0, 0, larg * 0.12))
        segmento(bm, p0, p1, larg * 0.16, larg * 0.11, seg=10)
        garra(rg, p1, d + Vector((0, 0, -0.3)), garra_comp, larg * 0.08)


def prisma(bm, base, direcao, alt, r, lados=6, ponta=0.35):
    """Prisma hexagonal com ponta piramidal (cristal natural)."""
    b = Vector(base); d = Vector(direcao).normalized()
    up = Vector((1, 0, 0)) if abs(d.x) < 0.9 else Vector((0, 1, 0))
    u = d.cross(up).normalized(); v = d.cross(u).normalized()
    anel0 = [bm.verts.new(b + (u * math.cos(2 * math.pi * i / lados) + v * math.sin(2 * math.pi * i / lados)) * r) for i in range(lados)]
    topo = b + d * alt * (1 - ponta)
    anel1 = [bm.verts.new(topo + (u * math.cos(2 * math.pi * i / lados) + v * math.sin(2 * math.pi * i / lados)) * r * 0.92) for i in range(lados)]
    pico = bm.verts.new(b + d * alt)
    for i in range(lados):
        j = (i + 1) % lados
        bm.faces.new((anel0[i], anel0[j], anel1[j], anel1[i]))
        bm.faces.new((anel1[i], anel1[j], pico))
    bm.faces.new(list(reversed(anel0)))


def aglomerado(rg, base, normal, n, hmin, hmax, rmin, rmax, semente=1, abertura=28):
    """Aglomerado natural de cristais: n prismas de tamanhos/inclinacoes variados (deterministico pela semente)."""
    import random
    rnd = random.Random(semente)
    nb = Vector(normal).normalized()
    for i in range(n):
        h = rnd.uniform(hmin, hmax) * (1.0 if i == 0 else rnd.uniform(0.45, 0.85))
        r = rnd.uniform(rmin, rmax) * (1.0 if i == 0 else 0.7)
        a, b2 = math.radians(rnd.uniform(-abertura, abertura)), math.radians(rnd.uniform(-abertura, abertura))
        d = (Matrix.Rotation(a, 3, "X") @ Matrix.Rotation(b2, 3, "Y") @ nb).normalized()
        off = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * rmax * 0.9 * (0 if i == 0 else 1)
        prisma(rg, Vector(base) + off - d * h * 0.15, d, h, r)


def lamina(bm, base, alt, comp, esp, incl=0.5):
    """Crista em lamina (placa espinhosa achatada lateralmente), inclinada para tras."""
    b = Vector(base)
    elipsoide(bm, b + Vector((0, comp * 0.15 + incl * alt * 0.3, alt * 0.45)), (esp, comp * 0.5, alt * 0.55), rot=(-math.degrees(math.atan(incl)), 0, 0), u=12, v=8)
    chifre(bm, b + Vector((0, incl * alt * 0.4, alt * 0.7)), [b + Vector((0, incl * alt * 0.8, alt * 1.05))], esp * 1.1, 0.02, seg=6)


def olhos(rg, centro_e, r, s_eixo_x=True):
    """Par de olhos (material olho) espelhados em x."""
    for s in (1, -1):
        elipsoide(rg, (s * abs(centro_e[0]), centro_e[1], centro_e[2]), (r, r, r), u=14, v=7)


def apoiar(pts, raio_pe_idx=-1):
    """Desce o membro ate o ponto mais baixo (centro - raio) tocar z = 0."""
    zmin = min(p[2] - p[3] for p in pts)
    return [(p[0], p[1], p[2] - zmin) + tuple(p[3:]) for p in pts]


# FUSAO ---------------------------------------------------------------------------------------

def massa(bm, voxel, suav_iter, suav_fator, laplace=0):
    """Funde e suaviza um grupo de primitivas a parte (ex.: juba, com suavizacao forte) e devolve
    um bmesh novo, para ser anexado ao corpo antes da fusao final.
    laplace > 0: suavizacao Laplaciana com preservacao de volume (tira calombos sem afinar membros)."""
    me = bpy.data.meshes.new("_massa")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("_massa", me)
    bpy.context.scene.collection.objects.link(ob)
    r = ob.modifiers.new("Remesh", "REMESH"); r.mode = "VOXEL"; r.voxel_size = voxel; r.adaptivity = 0.0
    if laplace:
        l = ob.modifiers.new("Laplace", "LAPLACIANSMOOTH")
        l.iterations = laplace; l.lambda_factor = 1.0; l.lambda_border = 0.0; l.use_volume_preserve = True
        l.use_normalized = True
    s = ob.modifiers.new("Suavizar", "SMOOTH"); s.factor = suav_fator; s.iterations = suav_iter
    _aplicar(ob)
    out = bmesh.new()
    out.from_mesh(ob.data)
    m = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(m)
    return out


def juntar(bm, outro):
    _anexar(bm, outro)


def anel(bm, centro, rx, rz, r_mecha, n=24, eixo_y=True, achatar=1.0):
    """Anel continuo (toro) de massas sobrepostas em volta do eixo Y: colar/juba em volta do rosto."""
    for i in range(n):
        t = 2 * math.pi * i / n
        elipsoide(bm, (centro[0] + rx * math.cos(t), centro[1], centro[2] + rz * math.sin(t)),
                  (r_mecha, r_mecha * achatar, r_mecha), u=16, v=8)

def fundir(nome, bm, col, voxel, suav_iter=8, suav_fator=0.5, tris=16000):
    """Uniao por voxel remesh + suavizacao + decimacao; devolve um objeto de malha unica."""
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    col.objects.link(ob)
    r = ob.modifiers.new("Remesh", "REMESH")
    r.mode = "VOXEL"
    r.voxel_size = voxel
    r.adaptivity = 0.0
    s = ob.modifiers.new("Suavizar", "SMOOTH")
    s.factor = suav_fator
    s.iterations = suav_iter
    _aplicar(ob)
    n = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    if n > tris:
        d = ob.modifiers.new("Decimar", "DECIMATE")
        d.ratio = tris / n
        _aplicar(ob)
    for p in ob.data.polygons:
        p.use_smooth = True
    ob["tris"] = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    return ob


def _aplicar(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    eo = ob.evaluated_get(dg)
    novo = bpy.data.meshes.new_from_object(eo)
    velho = ob.data
    ob.modifiers.clear()
    ob.data = novo
    nome = velho.name
    if velho.users == 0:
        bpy.data.meshes.remove(velho)
    novo.name = nome


def rigida(nome, bm, col, tris=None):
    """Parte rigida separada (chifre, garra, cristal): malha direta, sombreamento liso."""
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    col.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    ob["tris"] = sum(len(p.vertices) - 2 for p in me.polygons)
    return ob


def chifre(bm, base, pontos, r0, r1=0.05, seg=16):
    """Chifre/espinho/ferrao conico curvo: base -> pontos, raio afinando de r0 a r1."""
    pts = [Vector(base)] + [Vector(p) for p in pontos]
    n = len(pts) - 1
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n
        rb = r0 + (r1 - r0) * (i + 1) / n
        segmento(bm, pts[i], pts[i + 1], ra, rb, seg)
        elipsoide(bm, pts[i], (ra, ra, ra), u=seg, v=seg // 2)


def trilha(bm, pts, achatar=(1.0, 1.0), passo=0.35, u=20, v=10):
    """Corpo/cauda/pescoco continuo: elipsoides densos ao longo de pts [(x,y,z,r)], raio interpolado.
    achatar = (fator lateral, fator vertical) da secao (cauda de crocodilo: lateral < vertical)."""
    for (a, b) in zip(pts, pts[1:]):
        A, Bv = Vector(a[:3]), Vector(b[:3])
        n = max(1, int((Bv - A).length / passo))
        for i in range(n + (1 if b is pts[-1] else 0)):
            t = i / n
            p = A.lerp(Bv, t)
            r = a[3] + (b[3] - a[3]) * t
            elipsoide(bm, p, (r * achatar[0], r, r * achatar[1]), u=u, v=v)


def membrana(nome, col, contorno, centro, esp=0.3):
    """Membrana de asa/nadadeira: leque de triangulos a partir de 'centro' pelo 'contorno' (lista de pontos em ordem),
    com espessura (Solidify aplicado). Objeto proprio (deforma junto com os ossos da asa no rig futuro)."""
    bm = bmesh.new()
    c = bm.verts.new(Vector(centro))
    vs = [bm.verts.new(Vector(p)) for p in contorno]
    for a, b in zip(vs, vs[1:]):
        bm.faces.new((c, a, b))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(nome, me); col.objects.link(ob)
    s = ob.modifiers.new("Esp", "SOLIDIFY"); s.thickness = esp; s.offset = 0.0
    _aplicar(ob)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def fileira(bm, base_pts, alturas, inclinar=(0, 0.4, 0.0), r0=0.4, seg=8, lados=None):
    """Espinhos/cristais/placas ao longo de uma linha: cone de cada base, altura propria, inclinado por 'inclinar'
    (vetor somado a direcao vertical). lados = lista de deslocamentos x (ex.: (-0.4, 0.4) para fileira dupla)."""
    lados = lados or (0.0,)
    for (p, h) in zip(base_pts, alturas):
        for dx in lados:
            b = Vector(p) + Vector((dx, 0, 0))
            d = (Vector((math.copysign(abs(inclinar[0]), dx) if dx else 0, inclinar[1], 1.0 + inclinar[2]))).normalized()
            chifre(bm, b, [b + d * h * 0.5, b + d * h], r0 * (h / max(alturas)) ** 0.5 + 0.12, 0.03, seg=seg)


def argila(ob, cor=(0.62, 0.55, 0.45, 1)):
    m = bpy.data.materials.get("BLK_Argila") or bpy.data.materials.new("BLK_Argila")
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = cor
        bsdf.inputs["Roughness"].default_value = 0.8
    if ob.data.materials:
        ob.data.materials[0] = m
    else:
        ob.data.materials.append(m)


def humano(x, y=0.0):
    """Personagem do Roblox (5,2 studs) na colecao REF, so para escala nas renderizacoes."""
    ref = bpy.data.collections.get("REF") or bpy.data.collections.new("REF")
    if ref.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(ref)
    bm = bmesh.new()
    elipsoide(bm, (0, 0, 4.6), (0.55, 0.55, 0.6))                     # cabeca
    segmento(bm, (0, 0, 1.0), (0, 0, 3.9), 0.75, 0.85)                # corpo
    ob = rigida("REF_Humano_5_2_studs", bm, ref)
    ob.location = (x, y, 0)
    m = bpy.data.materials.get("REF_Branco") or bpy.data.materials.new("REF_Branco")
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.85, 0.85, 0.85, 1)
    ob.data.materials.append(m)
    return ob


def reaproveitar(especie, blend, malha, oficial, humano_xy=(6, -10), extras=()):
    """Traz a malha de um modelo ja feito no Blender (pose de ligacao do esqueleto, sem modificadores) para a
    colecao de blockout da especie. O arquivo de origem nao e alterado."""
    cena_nova()
    col = colecao(especie)
    nomes = [malha] + list(extras)
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in nomes]
    for ob in dst.objects:
        if ob is None:
            continue
        ob.modifiers.clear()
        ob.parent = None
        ob.vertex_groups.clear()
        ob.name = especie + ("_Corpo_Blockout" if ob.name == malha else "_" + ob.name)
        col.objects.link(ob)
        argila(ob)
    bpy.context.view_layer.update()
    humano(*humano_xy)
    md = medidas(col)
    md.update({"oficial": oficial, "origem": os.path.basename(blend) + " (reaproveitado)"})
    return col, md


def registrar(especie, pose, dados):
    import json
    d = os.path.join(RAIZ, "review", especie)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "medidas_%s.json" % pose), "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def medidas(col):
    """Caixa envolvente da colecao (mundo) para o relatorio."""
    dg = bpy.context.evaluated_depsgraph_get()
    mn = Vector((1e9, 1e9, 1e9)); mx = -mn
    tris = 0
    for ob in col.all_objects:
        if ob.type != "MESH":
            continue
        for v in ob.data.vertices:
            w = ob.matrix_world @ v.co
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
        tris += sum(len(p.vertices) - 2 for p in ob.data.polygons)
    return {"largura_x": round(mx.x - mn.x, 2), "comprimento_y": round(mx.y - mn.y, 2), "altura_z": round(mx.z, 2),
            "z_min": round(mn.z, 3), "tris": tris}
