# Blockout do Cervo-do-Bosque (fauna de recurso da Floresta Ancestral).
# Uso (segundo plano):
#   blender -b --factory-startup --python cervo_blockout.py -- <passagem 1|2> <pasta_saida>
# Gera o .blend editavel, renders das vistas e metricas.json na pasta de saida.
# Medidas tiradas da vista lateral da referencia (cervo-do-bosque-referencia.png).
# Escala: altura no ombro ~1,2 unidades do Blender (PROPOSTA, nao e porte oficial).
import bpy, sys, os, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
PASSAGEM = int(argv[0])
SAIDA = os.path.abspath(argv[1])
os.makedirs(SAIDA, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene

# px da vista lateral ampliada 2x (recorte 1000..1400 x 0..440) -> metros.
# Frente do animal = -Y, alto = +Z, lado direito do animal = -X.
K = 0.0025
def P(x, y, X=0.0):
    return Vector((X, -(x - 360) * K, (845 - y) * K))

R2 = PASSAGEM >= 2  # refinamentos da 2a passagem

# ---------- Corpo: pecas primitivas (ilhas editaveis) + Remesh por voxel ----------
# Cada peca e uma ilha da mesma malha, com grupo de vertices proprio (selecione pelo grupo
# no modo de edicao para mover/escalar). O Remesh funde as ilhas numa pele unica.
import bmesh
from mathutils import Matrix
bm = bmesh.new()
grupos = []
dl = bm.verts.layers.deform.verify()
def _marca(verts, nome):
    if nome not in grupos: grupos.append(nome)
    gi = grupos.index(nome)
    for v in verts: v[dl][gi] = 1.0
def elip(nome, c, sx, sy, sz, rot=(0, 0, 0)):
    m = Matrix.Translation(c) @ Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ \
        Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[0]), 4, "X") @ \
        Matrix.Diagonal((sx, sy, sz, 1))
    r = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0, matrix=m)
    _marca(r["verts"], nome)
def capsula(nome, a, b, ra, rb):
    d = b - a; L = d.length
    q = d.normalized().to_track_quat("Z", "Y")
    m = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=ra, radius2=rb, depth=L, matrix=m)
    _marca(r["verts"], nome)
    for c, rr in ((a, ra), (b, rb)):
        r = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=rr, matrix=Matrix.Translation(c))
        _marca(r["verts"], nome)

# tronco (largura X, comprimento Y, altura Z)
capsula("Tronco", P(185, 462), P(470, 462), 0.165, 0.20)
elip("Tronco_Garupa", P(160, 456), 0.155, 0.24, 0.165)
elip("Tronco_Barriga", P(350, 470), 0.19, 0.42, 0.19)
elip("Tronco_Peito", P(482, 452) if R2 else P(482, 458), 0.18, 0.24, 0.23 if R2 else 0.215)
if R2:  # cernelha: leva o dorso a altura do ombro da referencia
    elip("Cernelha", P(468, 392), 0.11, 0.17, 0.075)
elip("Peito_Frente", P(566, 472), 0.13, 0.10, 0.165 if not R2 else 0.175)
# pescoco (base funda por causa da juba) e cabeca
elip("Pescoco_Base", P(566, 405), 0.13, 0.15, 0.165 if not R2 else 0.175, rot=(-35, 0, 0))
capsula("Pescoco", P(578, 380), P(608, 280), 0.145 if R2 else 0.13, 0.095 if R2 else 0.09)
if R2:  # pelagem da garganta (juba clara da referencia)
    elip("Juba_Garganta", P(612, 352), 0.10, 0.09, 0.14, rot=(-20, 0, 0))
elip("Cranio", P(626, 246), 0.105 if R2 else 0.10, 0.10, 0.095 if R2 else 0.085)
capsula("Face", P(640, 254), P(735 if R2 else 742, 287), 0.085 if R2 else 0.082, 0.045 if R2 else 0.036)
elip("Mandibula", P(660, 284), 0.07, 0.085, 0.045, rot=(-15, 0, 0))
if R2:
    elip("Focinho_Ponta", P(738, 289), 0.046, 0.035, 0.042)
# cauda curta pendente
capsula("Cauda", P(108, 415), P(80, 500), 0.06 if R2 else 0.05, 0.045 if R2 else 0.034)

def perna(s, lado):
    X = lambda x, y, k: P(x, y, s * k)
    # dianteira: escapula, braco, antebraco, canela, quartela, casco
    elip(f"Escapula_{lado}", X(528, 468, 0.115), 0.07, 0.11, 0.17, rot=(25, 0, 0))
    capsula(f"Braco_{lado}", X(536, 520, 0.105), X(522, 598, 0.10), 0.085, 0.06)
    capsula(f"Antebraco_{lado}", X(522, 598, 0.10), X(504, 716, 0.095), 0.055, 0.034 if R2 else 0.036)
    capsula(f"Canela_D_{lado}", X(504, 716, 0.095), X(499, 798, 0.095), 0.03, 0.022 if R2 else 0.025)
    capsula(f"Quartela_D_{lado}", X(499, 798, 0.095), X(504, 822, 0.095), 0.024, 0.026)
    elip(f"Casco_D_{lado}", X(509, 832, 0.095), 0.03, 0.042, 0.022)
    # traseira: coxa, gamba, canela, quartela, casco
    capsula(f"Coxa_{lado}", X(178, 462, 0.11), X(238, 585, 0.12), 0.135, 0.075)
    capsula(f"Gamba_{lado}", X(238, 585, 0.12), X(142, 700, 0.11), 0.07, 0.038)
    capsula(f"Canela_T_{lado}", X(142, 700, 0.11), X(150, 798, 0.11), 0.03, 0.022 if R2 else 0.025)
    capsula(f"Quartela_T_{lado}", X(150, 798, 0.11), X(155, 822, 0.11), 0.024, 0.026)
    elip(f"Casco_T_{lado}", X(160, 832, 0.11), 0.03, 0.042, 0.022)
perna(1, "E"); perna(-1, "D")

me = bpy.data.meshes.new("Cervo_Pecas")
bm.to_mesh(me); bm.free()
corpo = bpy.data.objects.new("Cervo_Corpo_Pecas", me)
cena.collection.objects.link(corpo)
for g in grupos:
    corpo.vertex_groups.new(name=g)
rm = corpo.modifiers.new("Remesh", "REMESH")
rm.mode = "VOXEL"; rm.voxel_size = 0.009; rm.use_smooth_shade = True
sm = corpo.modifiers.new("Suavizar", "SMOOTH"); sm.factor = 0.6; sm.iterations = 6
dc = corpo.modifiers.new("Reduzir", "DECIMATE"); dc.ratio = 0.10

# ---------- Galhada (peca provisoria separada) ----------
gn, gr, ga = [], [], []
def gno(pos, r):
    gn.append(pos); gr.append(r); return len(gn) - 1
def gliga(*ids):
    for a, b in zip(ids, ids[1:]):
        ga.append((a, b))
def galhada(s):
    v = lambda x, y, z: Vector((s * x, y, z))
    b0 = gno(v(0.04, -0.672, 1.56), 0.032)
    b1 = gno(v(0.12, -0.60, 1.70), 0.027)
    b2 = gno(v(0.22, -0.46, 1.83), 0.023)
    b3 = gno(v(0.31, -0.29, 1.95), 0.019)
    b4 = gno(v(0.36, -0.17, 2.04), 0.013)
    pt = gno(v(0.37, -0.19, 2.07), 0.006)
    gliga(b0, b1, b2, b3, b4, pt)
    # pontas: testa (frente), duas verticais e uma externa
    ta = gno(v(0.065, -0.665, 1.62), 0.022)
    gliga(b0, ta, gno(v(0.10, -0.80, 1.74), 0.006))
    gliga(b1, gno(v(0.13, -0.66, 1.93), 0.006))
    gliga(b2, gno(v(0.21, -0.55, 2.03), 0.006))
    gliga(b3, gno(v(0.43, -0.33, 1.99), 0.006))
    if R2:  # ponta extra na coroa, como na referencia
        gliga(b3, gno(v(0.28, -0.40, 2.09), 0.006))
galhada(1); galhada(-1)
gm = bpy.data.meshes.new("Galhada_Esqueleto")
gm.from_pydata([tuple(v) for v in gn], ga, [])
gal = bpy.data.objects.new("Cervo_Galhada_Skin", gm)
cena.collection.objects.link(gal)
gsk = gal.modifiers.new("Skin", "SKIN"); gsk.use_smooth_shade = True
for i, r in enumerate(gr):
    gm.skin_vertices[0].data[i].radius = (r, r)
    gm.skin_vertices[0].data[i].use_root = (i == 0 or i == len(gr) // 2)
gss = gal.modifiers.new("Subdiv", "SUBSURF"); gss.levels = 1; gss.render_levels = 1

# ---------- Orelhas (pecas provisorias) ----------
def elipsoide(nome, loc, esc, rot):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, location=loc)
    o = bpy.context.active_object; o.name = nome
    o.scale = esc; o.rotation_euler = rot
    bpy.ops.object.shade_smooth()
    return o
orelhas = []
for s, lado in ((1, "E"), (-1, "D")):
    # aponta para fora e um pouco para cima/tras; achatada
    if R2:  # folha mais longa e mais erguida, como na referencia
        orelhas.append(elipsoide(f"Cervo_Orelha_{lado}", (s * 0.17, -0.63, 1.60),
                                 (0.10, 0.022, 0.05), (0, 0, 0)))
        orelhas[-1].rotation_euler = (math.radians(10), math.radians(s * -32), math.radians(s * 12))
    else:
        orelhas.append(elipsoide(f"Cervo_Orelha_{lado}", (s * 0.165, -0.635, 1.585),
                                 (0.085, 0.022, 0.042), (0, 0, 0)))
        orelhas[-1].rotation_euler = (math.radians(8), math.radians(s * -22), math.radians(s * 15))

extras = []
if R2:
    for s, lado in ((1, "E"), (-1, "D")):
        extras.append(elipsoide(f"Cervo_Olho_{lado}", (s * 0.072, -0.78, 1.488), (0.018, 0.016, 0.016), (0, 0, 0)))
    extras.append(elipsoide("Cervo_Nariz", (0, -0.968, 1.39), (0.032, 0.02, 0.024), (0, 0, 0)))

# ---------- Chao: apoiar os cascos em Z=0 ----------
dg = bpy.context.evaluated_depsgraph_get()
ev = corpo.evaluated_get(dg)
zmin = min((ev.matrix_world @ v.co).z for v in ev.data.vertices)
for o in [corpo, gal] + orelhas + extras:
    o.location.z -= zmin

bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
chao = bpy.context.active_object; chao.name = "Plano_Apoio"

# ---------- Materiais (cores provisorias so na 2a passagem) ----------
def mat(nome, cor):
    m = bpy.data.materials.new(nome); m.diffuse_color = (*cor, 1); return m
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)

M_CHAO = mat("M_Chao", lin("756c68"))
chao.data.materials.append(M_CHAO)

colecao_fonte = None
if R2:
    M_PEL = mat("M_Pelagem", lin("9a5326"))
    M_CREME = mat("M_Creme", lin("d8bf98"))
    M_ESCURO = mat("M_Casco_Nariz", lin("2c2522"))
    M_PERNA = mat("M_Perna", lin("7a4220"))
    M_GALHA = mat("M_Galhada", lin("cdb898"))
    M_GBASE = mat("M_Galhada_Base", lin("5a3e2c"))
    M_OREI = mat("M_Orelha", lin("9a5a30"))
    M_OLHO = mat("M_Olho", lin("1a1210"))
    # Corpo: copia aplicada recebe cores por regiao; a fonte Skin fica editavel e oculta.
    colecao_fonte = bpy.data.collections.new("Fonte_Editavel")
    cena.collection.children.link(colecao_fonte)
    dg = bpy.context.evaluated_depsgraph_get()
    def aplica(obj, nome):
        novo = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
        o = bpy.data.objects.new(nome, novo); o.matrix_world = obj.matrix_world
        cena.collection.objects.link(o)
        cena.collection.objects.unlink(obj); colecao_fonte.objects.link(obj)
        obj.hide_render = True; obj.hide_viewport = True
        return o
    corpo_ap = aplica(corpo, "Cervo_Corpo")
    for m in (M_PEL, M_CREME, M_ESCURO, M_PERNA):
        corpo_ap.data.materials.append(m)
    zc = -zmin
    for f in corpo_ap.data.polygons:
        c = f.center; c = Vector((c.x, c.y, c.z + 0))
        z = c.z
        idx = 0
        if z < 0.06:
            idx = 2                       # cascos
        elif 0.68 < z < 0.84 and -0.40 < c.y < 0.30 and f.normal.z < -0.45:
            idx = 1                       # barriga clara
        elif z < 0.68 and abs(c.x) > 0.04:
            idx = 3                       # pernas mais escuras
        # garganta/peito claro na frente do pescoco
        if c.y < -0.45 and c.y > -0.75 and 0.75 < z < 1.42 and abs(c.x) < 0.11 and f.normal.y < -0.3:
            idx = 1
        # parte de baixo da cauda clara
        if c.y > 0.60 and 0.80 < z < 1.02 and abs(c.x) < 0.075:
            idx = 1
        # focinho escuro na ponta
        if c.y < -0.955 and z > 1.3:
            idx = 2
        f.material_index = idx
    gal_ap = aplica(gal, "Cervo_Galhada")
    gal_ap.data.materials.append(M_GALHA); gal_ap.data.materials.append(M_GBASE)
    for f in gal_ap.data.polygons:
        f.material_index = 1 if f.center.z < 1.80 else 0
    for o in orelhas: o.data.materials.append(M_OREI)
    for o in extras: o.data.materials.append(M_OLHO if "Olho" in o.name else M_ESCURO)

# ---------- Render (Workbench, leve) ----------
cena.render.engine = "BLENDER_WORKBENCH"
sh = cena.display.shading
sh.light = "STUDIO"
sh.color_type = "MATERIAL" if R2 else "SINGLE"
sh.single_color = (0.62, 0.60, 0.58)
sh.show_shadows = True
sh.show_cavity = True; sh.cavity_type = "WORLD"
mundo = bpy.data.worlds.new("Fundo"); mundo.color = lin("7d746f"); cena.world = mundo
cena.render.film_transparent = False
cena.display_settings.display_device = "sRGB"
cena.view_settings.view_transform = "Standard"
cena.render.image_settings.file_format = "PNG"
if not R2:
    chao.data.materials.append(M_CHAO)

def camera(nome, loc, rot=None, orto=None, alvo=None, lente=50):
    c = bpy.data.cameras.new(nome)
    o = bpy.data.objects.new(nome, c); cena.collection.objects.link(o)
    o.location = loc
    if orto:
        c.type = "ORTHO"; c.ortho_scale = orto
    else:
        c.lens = lente
    if rot: o.rotation_euler = [math.radians(a) for a in rot]
    if alvo:
        d = Vector(alvo) - Vector(loc)
        o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return o

vistas = {
    # nome: (camera, resolucao)
    "frente": (camera("Cam_Frente", (0, -6, 1.07), rot=(90, 0, 0), orto=2.3), (360, 840)),
    "lado":   (camera("Cam_Lado", (-6, -0.12, 1.07), rot=(90, 0, -90), orto=2.3), (720, 792)),
    "tres_quartos": (camera("Cam_TresQuartos", (-1.4, -1.8, 0.7), alvo=(0, -0.15, 1.02), lente=28), (700, 1024)),
}
def render(nome, cam, res, arquivo):
    cena.camera = cam
    cena.render.resolution_x, cena.render.resolution_y = res
    cena.render.resolution_percentage = 100
    cena.render.filepath = os.path.join(SAIDA, arquivo)
    bpy.ops.render.render(write_still=True)

for nome, (cam, res) in vistas.items():
    render(nome, cam, res, f"p{PASSAGEM}_{nome}.png")

if R2:
    # captura reduzida (leitura de longe)
    render("pequena", vistas["tres_quartos"][0], (140, 205), "p2_pequena.png")
    # arame: copia com Wireframe por cima da malha
    alvos = [o for o in cena.collection.objects if o.type == "MESH" and o.name != "Plano_Apoio"]
    fios = []
    M_FIO = mat("M_Fio", (0.02, 0.02, 0.02))
    for o in alvos:
        f = o.copy(); f.data = o.data.copy(); f.name = o.name + "_FIO"
        cena.collection.objects.link(f)
        w = f.modifiers.new("Fio", "WIREFRAME"); w.thickness = 0.004; w.use_replace = True
        w.use_even_offset = False; w.material_offset = 99
        f.data.materials.clear(); f.data.materials.append(M_FIO)
        fios.append(f)
    render("arame", vistas["tres_quartos"][0], (700, 1024), "p2_arame.png")
    for f in fios:
        bpy.data.objects.remove(f, do_unlink=True)
    bpy.data.materials.remove(M_FIO)

# ---------- Metricas ----------
dg = bpy.context.evaluated_depsgraph_get()
met = {"passagem": PASSAGEM, "objetos": {}, "tris_total": 0}
for o in cena.objects:
    if o.type != "MESH" or o.name == "Plano_Apoio":
        continue
    if o.hide_render:
        continue
    e = o.evaluated_get(dg); m = e.to_mesh()
    tris = sum(len(p.vertices) - 2 for p in m.polygons)
    pts = [o.matrix_world @ v.co for v in m.vertices]
    dims = [round(max(p[i] for p in pts) - min(p[i] for p in pts), 3) for i in range(3)]
    met["objetos"][o.name] = {"tris": tris, "dim_xyz": dims,
                              "materiais": [s.material.name for s in o.material_slots if s.material]}
    met["tris_total"] += tris
    e.to_mesh_clear()
corpo_vis = "Cervo_Corpo" if R2 else "Cervo_Corpo_Pecas"
ec = cena.objects[corpo_vis].evaluated_get(dg); mc = ec.to_mesh()
zs = [(cena.objects[corpo_vis].matrix_world @ v.co) for v in mc.vertices]
met["corpo_altura_total"] = round(max(p.z for p in zs), 3)
met["nariz_y"] = round(min(p.y for p in zs), 3)
ec.to_mesh_clear()
gz = max((cena.objects["Cervo_Galhada" if R2 else "Cervo_Galhada_Skin"].matrix_world @ v.co).z
         for v in cena.objects["Cervo_Galhada" if R2 else "Cervo_Galhada_Skin"].evaluated_get(dg).to_mesh().vertices)
met["galhada_topo_z"] = round(gz, 3)
met["materiais_total"] = len([m for m in bpy.data.materials if m.users])
met["objetos_mesh"] = len([o for o in cena.objects if o.type == "MESH"])
with open(os.path.join(SAIDA, f"p{PASSAGEM}_metricas.json"), "w", encoding="utf-8") as fh:
    json.dump(met, fh, ensure_ascii=False, indent=1)

cena.camera = vistas["tres_quartos"][0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, f"CR_CervoDoBosque_Blockout_p{PASSAGEM}.blend"))
print("OK", json.dumps(met))
