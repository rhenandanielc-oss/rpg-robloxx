"""Revestimento V5 generico (27/10/2026) para as especies alem dos lobos, guiado pelo ESQUELETO de cada especie
(esqueletos.py): cada vertice e classificado pelo osso mais proximo (cabeca, pescoco, tronco, perna, cauda, asa...).
Modos:
  pelo  -> subpelo volumoso (superficie inflada com mechas alongadas no sentido do crescimento) + cartoes de pelo com
           transparencia (tecnica aprovada nos lobos) + vegetacao opcional; fios finos assados no corpo pelo pipeline.
  placa -> escamas/placas sobrepostas de geometria (maiores no dorso, menores nos flancos, nenhuma no ventre),
           com atlas proprio (relevo, borda escura, fissuras opcionais) para dragoes, repteis, artropodes e aquaticos.
Entrada: <Esp>/<Esp>_refinado.blend (silhueta V2 aprovada). Saida: <Esp>/<Esp>_refinado_v5.blend (V2 preservada).
Uso: blender -b --factory-startup -P revest.py -- <Especie>"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix, noise
from mathutils.kdtree import KDTree

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- parametros por especie (referencias: pranchas 01-04)
# esp: espessura do subpelo por grupo (studs); L: comprimento dos cartoes; d: espacamento; cores: (principal, segunda)
SP = {
    "Urso_Silvestre": dict(modo="pelo", esp=dict(cabeca=0.1, pescoco=0.5, tronco=0.42, perna=0.22, cauda=0.3),
                           L=dict(cabeca=(0.25, 0.4), pescoco=(0.9, 1.4), tronco=(0.8, 1.3), perna=(0.5, 0.8), cauda=(0.5, 0.8)),
                           d=dict(cabeca=0.16, pescoco=0.2, tronco=0.22, perna=0.2, cauda=0.2), W=0.5,
                           cores=[(0.075, 0.048, 0.028), (0.14, 0.095, 0.055)], folhas=26, base_atlas=[(0.08, 0.05, 0.03), (0.04, 0.03, 0.02), (0.15, 0.1, 0.06), (0.06, 0.08, 0.025)]),
    "Leao_Solar": dict(modo="pelo", esp=dict(cabeca=0.03, pescoco=0.05, tronco=0.05, perna=0.03, cauda=0.03, juba=0.85, tufo=0.3),
                       L=dict(cabeca=(0.15, 0.22), pescoco=(0.2, 0.3), tronco=(0.18, 0.28), perna=(0.15, 0.22), cauda=(0.15, 0.2), juba=(1.4, 2.3), tufo=(0.6, 0.9)),
                       d=dict(cabeca=0.3, pescoco=0.35, tronco=0.4, perna=0.45, cauda=0.4, juba=0.17, tufo=0.1), W=0.5,
                       cores=[(0.42, 0.24, 0.07), (0.3, 0.12, 0.03)], folhas=0, juba=True),
    "Bufalo_Colossal": dict(modo="pelo", esp=dict(cabeca=0.35, pescoco=0.7, tronco=0.12, perna=0.1, cauda=0.08, capa=0.65),
                            L=dict(cabeca=(0.6, 1.0), pescoco=(1.0, 1.6), tronco=(0.3, 0.45), perna=(0.4, 0.7), cauda=(0.3, 0.5), capa=(1.0, 1.6)),
                            d=dict(cabeca=0.2, pescoco=0.22, tronco=0.35, perna=0.3, cauda=0.3, capa=0.2), W=0.55,
                            cores=[(0.06, 0.04, 0.025), (0.11, 0.075, 0.045)], folhas=0, capa=True),
    "Cerbero_Sombrio": dict(modo="pelo", esp=dict(cabeca=0.02, pescoco=0.4, tronco=0.3, perna=0.14, cauda=0.35),
                            L=dict(cabeca=(0.12, 0.2), pescoco=(1.0, 1.5), tronco=(0.8, 1.2), perna=(0.5, 0.75), cauda=(0.8, 1.2)),
                            d=dict(cabeca=0.28, pescoco=0.22, tronco=0.25, perna=0.24, cauda=0.22), W=0.5,
                            cores=[(0.028, 0.025, 0.025), (0.06, 0.05, 0.05)], folhas=0),
}
PLACA = {   # modo placa: tamanho base, cor (principal, variacao, borda), fissura (cor emissiva ou None), cobertura
    "Dragao_das_Montanhas": dict(modo="placa", tam=1.15, cor=((0.05, 0.045, 0.042), (0.11, 0.1, 0.09), (0.02, 0.018, 0.016)), fissura=(1.0, 0.32, 0.05)),
    "Dragao_Glacial": dict(modo="placa", tam=1.05, cor=((0.55, 0.62, 0.7), (0.75, 0.82, 0.88), (0.25, 0.35, 0.48)), fissura=None, angular=True),
    "Dragao_Sombrio": dict(modo="placa", tam=1.1, cor=((0.02, 0.018, 0.025), (0.05, 0.045, 0.06), (0.01, 0.008, 0.012)), fissura=(0.75, 0.08, 0.6), angular=True),
    "Wyvern": dict(modo="placa", tam=0.55, cor=((0.12, 0.13, 0.07), (0.2, 0.18, 0.1), (0.05, 0.05, 0.03)), fissura=None),
    "Basilisco": dict(modo="placa", tam=0.55, cor=((0.06, 0.08, 0.04), (0.11, 0.13, 0.06), (0.03, 0.035, 0.02)), fissura=None, musgo=True),
    "Crocodilo_Primordial": dict(modo="placa", tam=0.6, cor=((0.06, 0.07, 0.045), (0.1, 0.1, 0.07), (0.03, 0.03, 0.02)), fissura=None, osteo=True),
    "Lagarto_Cristalino": dict(modo="placa", tam=0.5, cor=((0.2, 0.18, 0.15), (0.3, 0.27, 0.22), (0.1, 0.09, 0.08)), fissura=None),
    "Escorpiao_Colossal": dict(modo="placa", tam=0.8, cor=((0.11, 0.05, 0.025), (0.2, 0.1, 0.045), (0.03, 0.015, 0.01)), fissura=(0.8, 0.35, 0.08), quitina=True),   # castanho-cobre (prancha 03)
    "Serpente_Marinha": dict(modo="placa", tam=0.55, cor=((0.04, 0.1, 0.16), (0.07, 0.16, 0.2), (0.02, 0.05, 0.08)), fissura=None),
    "Leviata_Jovem": dict(modo="placa", tam=1.0, cor=((0.035, 0.06, 0.1), (0.07, 0.1, 0.14), (0.015, 0.03, 0.05)), fissura=None),
}


# ---------------------------------------------------------------- classificacao anatomica pelo esqueleto
def grupo(n):
    if n.startswith(("Cabeca", "Mandibula")): return "cabeca"
    if n.startswith("Pescoco"): return "pescoco"
    if n.startswith(("Cauda", "Ferrao")): return "cauda"
    if n.startswith(("Perna", "Pata", "Pinca")): return "perna"
    if n.startswith(("Asa", "Dedo")): return "asa"
    if n.startswith("Nad"): return "nadadeira"
    return "tronco"


class Anat:
    def __init__(self, esp):
        import esqueletos
        self.E = esqueletos.todos()[esp]
        self.S = [(n, np.array(a), np.array(b)) for n, a, b, p in self.E.ossos if n != "Raiz"]
        self.A = np.array([s[1] for s in self.S]); self.B = np.array([s[2] for s in self.S])
        alt = [s[2][2] for s in self.S if grupo(s[0]) == "tronco"] or [5.0]
        self.H = max(alt)                                            # altura do dorso: escala da especie
        pts = np.vstack([self.A, self.B]); self.C = float((pts.max(0) - pts.min(0)).max())   # maior dimensao (corpos baixos e compridos)

    def osso(self, p):
        P = np.array(p); AB = self.B - self.A
        t = np.clip(((P - self.A) * AB).sum(1) / np.maximum(1e-9, (AB * AB).sum(1)), 0, 1)
        D = np.linalg.norm(P - (self.A + t[:, None] * AB), axis=1)
        j = int(np.argmin(D))
        return self.S[j][0], Vector(self.A[j]), Vector(self.B[j]), float(t[j]), float(D[j])

    def fluxo(self, p, n):
        nome, a, b, t, _ = self.osso(p); g = grupo(nome); d = (b - a).normalized()
        if g == "cabeca": f = -d + Vector((0, 0, -0.1))
        elif g == "pescoco": f = -d + Vector((0, 0, -0.7))
        elif g == "perna": f = d if d.z < 0 else -d
        elif g in ("cauda", "asa", "nadadeira"): f = d + Vector((0, 0, -0.15))
        else: f = (d if d.y >= 0 else -d) + Vector((0, 0, -0.4))      # tronco: para tras (cauda) e para baixo
        return f, g, nome, t


class Grade:
    """Hash espacial para espacamento minimo (Poisson aproximado) sem custo quadratico."""
    def __init__(self, c): self.c = c; self.g = {}
    def livre(self, p, r):
        k = lambda q: (int(q.x // self.c), int(q.y // self.c), int(q.z // self.c))
        i, j, l = k(p); n = int(r // self.c) + 1
        for a in range(i - n, i + n + 1):
            for b in range(j - n, j + n + 1):
                for c in range(l - n, l + n + 1):
                    for q in self.g.get((a, b, c), ()):
                        if (p - q).length < r: return False
        return True
    def add(self, p):
        self.g.setdefault((int(p.x // self.c), int(p.y // self.c), int(p.z // self.c)), []).append(p)


def olhos_e_focinho(col):
    """Pontos a proteger (olhos e ponta do focinho): sem pelo/placas por cima."""
    pts = []
    for o in col.objects:
        if o.type == "MESH" and "_Olho" in o.name:
            vs = [o.matrix_world @ v.co for v in o.data.vertices]
            for s in (1, -1):
                lado = [v for v in vs if v.x * s > 0]
                if lado: pts.append(sum(lado, Vector()) / len(lado))
    return pts


# ---------------------------------------------------------------- PELO
def regiao_pelo(sp, an, p, n):
    f, g, nome, t = an.fluxo(p, n)
    if g in ("asa", "nadadeira"): return None, f
    if sp.get("juba") and (g == "pescoco" or (g == "cabeca" and nome.startswith("Cabeca") and t < 0.22)):
        if g == "cabeca":                                          # juba em volta do rosto: para tras e para fora
            f = Vector((math.copysign(0.7, p.x), 1.0, -0.2))
        else:
            f = f + Vector((math.copysign(0.4, p.x), 0, -0.4))
        return "juba", f
    if sp.get("juba") and g == "cauda" and nome == sorted([s[0] for s in an.S if s[0].startswith("Cauda")])[-1] and t > 0.4:
        return "tufo", f
    if sp.get("capa"):                                              # bisao: capa densa na frente (cabeca, pescoco, corcova)
        _, a, b, _, _ = an.osso(p)
        ys = [s[1][1] for s in an.S if grupo(s[0]) == "tronco"]
        meio = (min(ys) + max(ys)) / 2
        if g in ("tronco", "perna") and p.y < meio - 0.1 * (max(ys) - min(ys)) and p.z > an.H * 0.45:
            return "capa", f
    return g, f


def espessura_pelo(sp, an, p, n, prot):
    r, f = regiao_pelo(sp, an, p, n)
    if r is None or any((p - q).length < 0.12 * an.H for q in prot): return 0.0, r, f
    e = sp["esp"].get(r, 0.0)
    if r == "perna":                                               # mais curto perto das patas
        e *= min(1.0, max(0.25, p.z / (an.H * 0.6)))
    return e, r, f


def volume(o, sp, an, prot, semente=4.0):
    me = o.data
    bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
    novo = []
    for v in bm.verts:
        p = v.co.copy(); n = v.normal.copy()
        e, r, f = espessura_pelo(sp, an, p, n, prot)
        if e <= 0: novo.append(p); continue
        d = f - n * f.dot(n)
        if d.length < 1e-3: d = Vector((0, 1, 0))
        d.normalize(); b = n.cross(d)
        esc = 1.0 / max(0.5, e)
        c = Vector((p.dot(d) * 1.2 * esc * 0.3 + semente, p.dot(b) * 5.0 * esc * 0.3, p.dot(n)))
        novo.append(p + n * e * (0.5 + 0.7 * (0.5 + 0.5 * noise.noise(c))))
    for v, p in zip(bm.verts, novo): v.co = p
    bm.to_mesh(me); bm.free()
    sm = o.modifiers.new("Lap", "LAPLACIANSMOOTH"); sm.iterations = 4; sm.lambda_factor = 0.6; sm.use_volume_preserve = True
    dg = bpy.context.evaluated_depsgraph_get(); m2 = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); o.data = m2


def pelagem(o, col, sp, an, prot, esp_nome):
    import lobo_v5 as L5
    L5.CORES_CARTAO = sp["cores"]
    rnd = random.Random(21)
    cands = [(Vector(v.co), Vector(v.normal)) for v in o.data.vertices]; rnd.shuffle(cands)
    bms = {}
    def bm_de(k):
        if k not in bms:
            b = bmesh.new(); bms[k] = (b, b.loops.layers.uv.new("UVMap"))
        return bms[k]
    cont = {}
    s = an.H / 5.6                                                 # escala relativa ao lobo (dorso ~5,6)
    grades = {}
    for p, n in cands:
        e, r, f = espessura_pelo(sp, an, p, n, prot)
        if r is None or r not in sp["L"] or e <= 0.0 and r not in ("juba", "tufo"): continue
        dmin = sp["d"][r] * s * 0.72                                   # densidade: cobertura continua
        gr = grades.setdefault(r, Grade(max(0.05, dmin)))
        if not gr.livre(p, dmin): continue
        gr.add(p)
        d = f - n * f.dot(n)
        if d.length < 1e-3: continue
        d.normalize(); d = Matrix.Rotation(math.radians(rnd.uniform(-16, 16)), 3, n) @ d
        if d.z > 0.1 and r not in ("cauda", "tufo", "juba"):
            d.z = 0.1; d = (d - n * d.dot(n)).normalized()
        L0, L1 = sp["L"][r]; L = rnd.uniform(L0, L1) * s * (1.25 if r == "perna" else 1.0)
        W = sp["W"] * s * (1.25 if r in ("juba", "capa") else 0.8 if r == "perna" else 1.0) * rnd.uniform(0.8, 1.2)
        linha = 1 if rnd.random() < (0.5 if r in ("juba", "tufo") else 0.25) else 0
        k = {"cabeca": "Cabeca", "pescoco": "Pescoco", "juba": "Juba", "capa": "Capa", "perna": "Pernas", "cauda": "Cauda", "tufo": "Cauda"}.get(r, "Tronco")
        bm, uvl = bm_de(k)
        L5.cartao(bm, uvl, p, n, d, L, W, 0.35 if r in ("juba", "capa") else 0.3 if r == "perna" else 0.22, linha, rnd)
        cont[r] = cont.get(r, 0) + 1
    mat = bpy.data.materials.new("MAT_%s_Pelagem" % esp_nome)
    nt = mat.node_tree; bs = next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED")
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = L5.atlas_cartoes("%s_Pelagem_Cartoes" % esp_nome)
    nt.links.new(tx.outputs["Color"], bs.inputs["Base Color"]); nt.links.new(tx.outputs["Alpha"], bs.inputs["Alpha"])
    bs.inputs["Roughness"].default_value = 0.95
    if hasattr(mat, "surface_render_method"): mat.surface_render_method = "DITHERED"
    mat.use_backface_culling = False
    if sp.get("folhas"):                                           # vegetacao localizada (Urso Silvestre: prancha 01)
        L5.CORES_ATLAS = sp["base_atlas"]
        fb, fu = bm_de("Folhas"); nf = 0
        for p, n in cands:
            if nf >= sp["folhas"] * 6: break
            f, g, nome, t = an.fluxo(p, n)
            if g not in ("tronco", "pescoco") or n.z < 0.35 or rnd.random() > 0.05: continue
            for i in range(rnd.randint(3, 7)):
                q = p + Vector((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), 0)) * s
                d = Matrix.Rotation(math.radians(rnd.uniform(-70, 70)), 3, n) @ (f - n * f.dot(n)).normalized()
                if i == 0 and rnd.random() < 0.4: L5.samambaia(fb, fu, q + n * 0.05 * s, n, d, rnd.uniform(0.7, 1.1) * s)
                else: L5.folha_real(fb, fu, q + n * 0.05 * s, n, d, rnd.uniform(0.4, 0.6) * s, rnd.uniform(0.15, 0.22) * s, rnd.choice((0, 1, 1, 2)), rnd)
                nf += 1
        matf = bpy.data.materials.new("MAT_%s_Folhagem" % esp_nome)
        ntf = matf.node_tree; bf = next(x for x in ntf.nodes if x.type == "BSDF_PRINCIPLED")
        txf = ntf.nodes.new("ShaderNodeTexImage"); txf.image = L5.atlas()
        ntf.links.new(txf.outputs["Color"], bf.inputs["Base Color"]); bf.inputs["Roughness"].default_value = 0.8
    tris = {}
    for k, (bm, uvl) in bms.items():
        m = bpy.data.meshes.new("%s_Pelagem%s" % (esp_nome, k)); bm.to_mesh(m); bm.free()
        for pl in m.polygons: pl.use_smooth = True
        ob = bpy.data.objects.new("%s_Pelagem%s" % (esp_nome, k), m); col.objects.link(ob)
        m.materials.append(matf if k == "Folhas" else mat); ob["papel_material"] = "pelagem"
        tris[k] = sum(len(pl.vertices) - 2 for pl in m.polygons)
    print("CARTOES", cont, "TRIS", tris)


def fios_alta(o, esp, n_fios=30000, semente=5):
    """Malha de alta (copia do corpo + fios finos no sentido do pelo) para o pipeline assar normal/oclusao no corpo."""
    import lobo_v5 as L5
    an = Anat(esp); sp = SP.get(esp, {})
    rnd = random.Random(semente); me = o.data; M = o.matrix_world
    polys = list(me.polygons); areas = np.array([p.area for p in polys]); acc = np.cumsum(areas) / areas.sum()
    bm = bmesh.new(); bm.from_mesh(me); s = an.H / 5.6
    for idx in np.searchsorted(acc, np.random.default_rng(semente).random(n_fios)):
        pl = polys[min(idx, len(polys) - 1)]
        vs = [me.vertices[i].co for i in pl.vertices[:3]]; a, b = sorted((rnd.random(), rnd.random()))
        p = M @ (vs[0] * a + vs[1] * (b - a) + vs[2] * (1 - b)); n = (M.to_3x3() @ pl.normal).normalized()
        f, g, nome, t = an.fluxo(p, n)
        if g == "cabeca" or p.z < 0.3 * s: continue
        d = f - n * f.dot(n)
        if d.length < 1e-3: continue
        d.normalize(); d = Matrix.Rotation(math.radians(rnd.uniform(-20, 20)), 3, n) @ d
        L = rnd.uniform(0.14, 0.26) * s * (0.5 if g == "perna" else 1.0)
        L5.fio(bm, None, p + n * 0.065 * s, n, d, L, 0.036 * s, 0.12, 0, 0)
    m = bpy.data.meshes.new("_FiosAlta"); bm.to_mesh(m); bm.free()
    ob = bpy.data.objects.new("_FiosAlta", m); bpy.context.scene.collection.objects.link(ob)
    return ob


# ---------------------------------------------------------------- PLACAS / ESCAMAS
def atlas_placas(nome, cfg):
    """Atlas 512x512 de placas: 4 variantes (colunas) x 2 tamanhos; relevo central, borda escura, estrias,
    fissura opcional (cor quente/magenta) e pontas angulares (glacial/sombrio)."""
    rng = np.random.default_rng(3)
    W_ = H_ = 512; cw, rh = 128, 256
    img = np.ones((H_, W_, 4))
    c0, c1, cb = [np.array(c) for c in cfg["cor"]]
    yy, xx = np.mgrid[0:rh, 0:cw]; u = (xx - cw / 2) / (cw / 2); v = yy / rh
    for linha in range(2):
        for col in range(4):
            larg = 1 - 0.85 * v ** (1.6 if not cfg.get("angular") else 1.0)
            dentro = np.abs(u) < larg
            borda = np.clip((larg - np.abs(u)) / 0.18, 0, 1)
            estria = 0.85 + 0.15 * np.sin(u * (9 + col * 2) + rng.uniform(0, 6))
            mancha = 0.8 + 0.4 * rng.random((rh, cw))
            mix = np.clip(0.5 + 0.5 * np.sin(v * 7 + col), 0, 1)[..., None]
            cor = (c0 * (1 - mix) + c1 * mix) * (estria * mancha)[..., None]
            cor = cor * borda[..., None] + cb * (1 - borda[..., None])
            if cfg.get("fissura") is not None and col in (1, 3):
                fx = np.abs(u - 0.25 * np.sin(v * 9 + col)) < 0.045
                cor[fx & dentro] = np.array(cfg["fissura"]) * 0.6
            cor[~dentro] = cb
            y0, x0 = linha * rh, col * cw
            img[y0:y0 + rh, x0:x0 + cw, :3] = np.clip(cor, 0, 1) ** (1 / 2.2)
    im = bpy.data.images.new(nome, W_, H_, alpha=False)
    im.pixels.foreach_set(img.astype(np.float32).ravel()); im.pack()
    return im


def placa(bm, uvl, p, n, d, L, W, h, col, linha):
    """Escama/placa: lamina curva em escudo (secao em arco, crista central, ponta para tras), assentada na pele e
    sobreposta as vizinhas. 16 triangulos."""
    b = n.cross(d).normalized()
    perfil = [(-1, 0.0), (-0.55, 0.65), (0, 1.0), (0.55, 0.65), (1, 0.0)]
    u0, u1 = col * 0.25 + 0.01, (col + 1) * 0.25 - 0.01; v0 = linha * 0.5
    aneis = []
    for s, larg, alt in ((0.0, 0.85, 0.5), (0.45, 1.0, 1.0), (0.8, 0.6, 0.7)):
        c = p - n * 0.15 * h + d * L * s + n * h * 0.6 * s
        aneis.append([bm.verts.new(c + b * W * 0.5 * larg * a + n * h * alt * z) for a, z in perfil])
    tip = bm.verts.new(p + d * L + n * h * 0.25)
    vs = (0.02, 0.45, 0.8)
    us = [u0 + (u1 - u0) * k / 4 for k in range(5)]
    for i in range(2):
        for k in range(4):
            f = bm.faces.new((aneis[i][k], aneis[i][k + 1], aneis[i + 1][k + 1], aneis[i + 1][k]))
            for lp, uv in zip(f.loops, ((us[k], v0 + vs[i] * 0.5), (us[k + 1], v0 + vs[i] * 0.5), (us[k + 1], v0 + vs[i + 1] * 0.5), (us[k], v0 + vs[i + 1] * 0.5))):
                lp[uvl].uv = uv
    for k in range(4):
        f = bm.faces.new((aneis[2][k], aneis[2][k + 1], tip))
        for lp, uv in zip(f.loops, ((us[k], v0 + 0.4), (us[k + 1], v0 + 0.4), ((u0 + u1) / 2, v0 + 0.49))):
            lp[uvl].uv = uv


def escamas(o, col, cfg, an, prot, esp_nome):
    rnd = random.Random(31)
    cands = [(Vector(v.co), Vector(v.normal)) for v in o.data.vertices]; rnd.shuffle(cands)
    bms = {}; cont = {}; pos = []
    tam = cfg["tam"] * max(an.H, an.C / 3.2) / 10.0 * 2.2
    gr = Grade(max(0.05, tam * 0.4))
    for p, n in cands:
        f, g, nome, t = an.fluxo(p, n)
        if g == "nadadeira" or (g == "asa" and not cfg.get("quitina")): continue
        if any((p - q).length < 0.18 * an.H / 5 for q in prot): continue
        if n.z < -0.6: continue                                      # ventre: escamas so na textura (escudos ventrais)
        dorsal = max(0.0, n.z)
        fator = {"tronco": 1.0, "pescoco": 0.8, "cauda": 0.85, "cabeca": 0.4, "perna": 0.7, "asa": 0.5}.get(g, 0.8)
        if cfg.get("osteo") and g in ("tronco", "cauda") and dorsal > 0.55: fator *= 1.35  # osteodermos do crocodilo
        T = tam * fator * (0.7 + 0.45 * dorsal)
        if not gr.livre(p, T * 0.42): continue                        # sobreposicao (telhado) continua
        gr.add(p)
        d = f - n * f.dot(n)
        if d.length < 1e-3: continue
        d.normalize()
        k = "Cabeca" if g == "cabeca" else ("Membros" if g in ("perna", "asa") else ("Cauda" if g == "cauda" else "Tronco"))
        if k in ("Membros", "Tronco"): k += "E" if p.x >= 0 else "D"     # cada MeshPart abaixo do limite
        if k not in bms:
            b = bmesh.new(); bms[k] = (b, b.loops.layers.uv.new("UVMap"))
        bm, uvl = bms[k]
        placa(bm, uvl, p, n, d, T * rnd.uniform(0.9, 1.15), T * rnd.uniform(0.75, 0.95), T * 0.14, rnd.randrange(4), 0 if dorsal > 0.5 else 1)
        cont[g] = cont.get(g, 0) + 1
    mat = bpy.data.materials.new("MAT_%s_Placas" % esp_nome)
    nt = mat.node_tree; bs = next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED")
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = atlas_placas("%s_Placas_Atlas" % esp_nome, cfg)
    nt.links.new(tx.outputs["Color"], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.35 if cfg.get("quitina") or esp_nome == "Dragao_Glacial" else 0.6
    tris = {}
    for k, (bm, uvl) in bms.items():
        m = bpy.data.meshes.new("%s_Pelagem%s" % (esp_nome, k)); bm.to_mesh(m); bm.free()     # "Pelagem": pesos copiados da pele
        for pl in m.polygons: pl.use_smooth = False
        ob = bpy.data.objects.new("%s_Placas%s_Pelagem" % (esp_nome, k), m); col.objects.link(ob)
        m.materials.append(mat); ob["papel_material"] = "pelagem"
        tris[k] = sum(len(pl.vertices) - 2 for pl in m.polygons)
    print("PLACAS", cont, "TRIS", tris)


# ---------------------------------------------------------------- principal
def principal(esp):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(RAIZ, esp, esp + "_refinado.blend"))
    bpy.context.preferences.filepaths.save_version = 0
    col = bpy.data.collections[esp]
    o = next(x for x in col.objects if x.type == "MESH" and x.name.endswith("_Corpo_Blockout"))
    an = Anat(esp); prot = olhos_e_focinho(col)
    if esp in SP:
        sp = SP[esp]
        volume(o, sp, an, prot)
        pelagem(o, col, sp, an, prot, esp)
        o["fios_assados"] = True
    else:
        escamas(o, col, PLACA[esp], an, prot, esp)
    dest = os.path.join(RAIZ, esp, esp + "_refinado_v5.blend")
    bpy.ops.wm.save_as_mainfile(filepath=dest)
    print("REVEST_OK", esp, sum(sum(len(p.vertices) - 2 for p in x.data.polygons) for x in col.objects if x.type == "MESH"))


if __name__ == "__main__":
    principal(sys.argv[sys.argv.index("--") + 1])
