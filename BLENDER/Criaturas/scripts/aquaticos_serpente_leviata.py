# Criaturas aquaticas (Costas Selvagens): Serpente Marinha e Leviata Jovem. 1 BU = 1 stud; frente -Y, cima +Z, esquerda +X.
# OFICIAL Serpente: serpentina SEM patas, nadadeiras e cristas, 30-45 de comprimento (usado 38); desliza em terra por magia (periodo moderado).
# OFICIAL Leviata: reptil oceanico colossal, corpo alongado, QUATRO nadadeiras, cauda poderosa, 55-80 de comprimento (usado 66).
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix, Quaternion
OUT = sys.argv[sys.argv.index("--") + 1]; DEST = sys.argv[sys.argv.index("--") + 2]; ESP = sys.argv[sys.argv.index("--") + 3]
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
def skin_obj(name, pts, edges, radii, sub=2):
    me = bpy.data.meshes.new(name); me.from_pydata(pts, edges, [])
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    sk = ob.modifiers.new("Skin", "SKIN"); sk.use_smooth_shade = True
    ss = ob.modifiers.new("Sub", "SUBSURF"); ss.levels = sub
    for i, r in enumerate(radii):
        v = me.skin_vertices[0].data[i]; v.radius = (r[0], r[1]) if isinstance(r, tuple) else (r, r)
    me.skin_vertices[0].data[0].use_root = True
    return ob
def tubo(name, path, radii, achatar=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []; n = len(path)
    for k in range(n):
        p = Vector(path[k]); d = (Vector(path[min(k + 1, n - 1)]) - Vector(path[max(k - 1, 0)])).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0)); u = d.cross(up).normalized(); v = d.cross(u).normalized()
        rings.append([bm.verts.new(p + u * math.cos(a / 10 * 2 * math.pi) * radii[k] + v * math.sin(a / 10 * 2 * math.pi) * radii[k] * (achatar or 1)) for a in range(10)])
    for k in range(n - 1):
        for a in range(10):
            b = (a + 1) % 10; bm.faces.new((rings[k][a], rings[k][b], rings[k + 1][b], rings[k + 1][a]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1]); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    for f in me.polygons: f.use_smooth = True
    return ob
def membrana(name, contorno, esp=0.1, cuts=3):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); vs = [bm.verts.new(Vector(p)) for p in contorno]
    for i in range(len(vs)): bm.edges.new((vs[i], vs[(i + 1) % len(vs)]))
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bm.edges[:])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True); bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    so = ob.modifiers.new("Esp", "SOLIDIFY"); so.thickness = esp
    for f in me.polygons: f.use_smooth = True
    return ob

partes = []; NADAD = []
if ESP == "Serpente":
    NOME = "Serpente_Marinha"; COMP = 38.0
    N = 26; ys = [-COMP / 2 + COMP * i / (N - 1) for i in range(N)]
    def raio(t):  # t 0 = focinho, 1 = ponta da cauda
        if t < 0.06: return 0.35 + (t / 0.06) * 1.25
        if t < 0.11: return 1.6 - (t - 0.06) / 0.05 * 0.55  # nuca bem mais fina que a cabeca
        if t < 0.35: return 1.1 + (t - 0.10) / 0.25 * 0.75
        return 1.85 * (1 - (t - 0.35) / 0.65) ** 1.3 + 0.12
    spine = [(0, y, 2.5) for y in ys]
    # cabeca larga e achatada (serpente marinha), corpo um pouco mais alto que largo
    rad = [((raio(i / (N - 1)) * 1.22, raio(i / (N - 1)) * 0.78) if i / (N - 1) < 0.07 else (raio(i / (N - 1)) * 0.95, raio(i / (N - 1)) * 1.08)) for i in range(N)]
    corpo = skin_obj("Corpo", spine, [(i, i + 1) for i in range(N - 1)], rad); partes.append(corpo)
    # babados laterais atras da cabeca (nadadeiras/cristas naturais)
    for s in (-1, 1):
        partes.append(membrana("Babado", [(s * 1.3, ys[2] - 0.2, 2.9), (s * 3.4, ys[3] + 0.6, 3.9), (s * 3.0, ys[4] + 0.9, 2.5), (s * 1.2, ys[4] + 0.4, 2.3)], 0.07)); NADAD.append(partes[-1])
    # crista dorsal (nadadeira continua), da nuca ate perto da cauda
    topo = [(0, spine[i][1], 2.5 + rad[i][1] * 0.9) for i in range(3, N - 2)]
    alto = [(0, spine[i][1] + 0.3, 2.5 + rad[i][1] * 0.9 + 0.55 + 0.6 * math.sin(math.pi * (i - 3) / (N - 5)) + 0.25 * (i % 2)) for i in range(N - 3, 2, -1)]
    partes.append(membrana("Crista", topo + alto, 0.08)); NADAD.append(partes[-1])
    # nadadeiras peitorais (um par, atras da cabeca) e nadadeira caudal vertical
    for s in (-1, 1):
        y0 = spine[5][1]
        partes.append(membrana("Peitoral", [(s * 1.0, y0 - 0.6, 2.2), (s * 3.4, y0 + 0.4, 1.6), (s * 3.0, y0 + 1.6, 1.4), (s * 1.0, y0 + 1.2, 2.0)], 0.08)); NADAD.append(partes[-1])
    yt = spine[-1][1]
    partes.append(membrana("Caudal", [(0, yt - 2.5, 2.6), (0, yt + 1.6, 4.6), (0, yt + 0.8, 2.5), (0, yt + 1.6, 0.4)], 0.08)); NADAD.append(partes[-1])
    # cristas da cabeca (espinhos para tras) e mandibula
    for s in (-1, 1):
        partes.append(tubo("CristaCabeca", [(s * 0.6, ys[1] + 0.2, 3.5), (s * 0.9, ys[2] + 0.6, 4.2), (s * 1.1, ys[3] + 0.6, 4.4)], [0.25, 0.14, 0.02], achatar=0.4))
    BONES_SPINE = 13  # cadeia: Cabeca, Pescoco, Corpo1..10, Cauda
    PAD = [("Azul_Oceanico", (0.02, 0.07, 0.14), (0.12, 0.33, 0.55), (0.10, 0.30, 0.48), (0.35, 0.62, 0.78)),
           ("Verde_Profundo", (0.015, 0.07, 0.05), (0.08, 0.30, 0.22), (0.06, 0.24, 0.18), (0.25, 0.50, 0.40)),
           ("Prateado_Marinho", (0.10, 0.12, 0.14), (0.55, 0.60, 0.64), (0.30, 0.34, 0.38), (0.70, 0.74, 0.78))]
else:
    NOME = "Leviata_Jovem"; COMP = 66.0
    N = 24; ys = [-COMP / 2 + COMP * i / (N - 1) for i in range(N)]
    def raio(t):  # focinho longo de reptil marinho (mosassauro), cranio achatado
        if t < 0.05: return 0.8 + t / 0.05 * 1.0
        if t < 0.10: return 1.8 + (t - 0.05) / 0.05 * 1.4
        if t < 0.16: return 3.2 - (t - 0.10) / 0.06 * 0.5    # pescoco curto e grosso
        if t < 0.45: return 2.7 + (t - 0.16) / 0.29 * 3.6     # tronco massivo
        return 6.3 * (1 - (t - 0.45) / 0.55) ** 1.15 + 0.3
    spine = [(0, y, 8.0) for y in ys]
    rad = [((raio(i / (N - 1)) * 1.12, raio(i / (N - 1)) * 0.7) if i / (N - 1) < 0.1 else (raio(i / (N - 1)) * 1.05, raio(i / (N - 1)) * 0.88)) for i in range(N)]
    corpo = skin_obj("Corpo", spine, [(i, i + 1) for i in range(N - 1)], rad); partes.append(corpo)
    # cristas sobre os olhos e linha da boca saliente
    for s in (-1, 1):
        partes.append(tubo("Sobrancelha", [(s * 1.6, ys[1] - 0.8, 9.6), (s * 2.1, ys[2] + 0.2, 10.2), (s * 1.9, ys[2] + 2.0, 10.1)], [0.4, 0.5, 0.2]))
        partes.append(tubo("Labio", [(s * 0.9, ys[0] + 0.6, 7.4), (s * 1.9, ys[1] + 0.6, 7.3), (s * 2.7, ys[2] + 1.2, 7.4)], [0.22, 0.3, 0.25]))
    # quatro nadadeiras (dianteiras maiores), como remos com dedos longos
    FL = {}
    for s, lado in ((1, "E"), (-1, "D")):
        for nome_n, i0, comp, larg in (("Dianteira", 8, 15.0, 4.6), ("Traseira", 13, 11.0, 3.6)):
            y0 = spine[i0][1]; x0 = s * rad[i0][0] * 0.8; z0 = 8.0 - rad[i0][1] * 0.35
            base = Vector((x0, y0, z0)); ponta = Vector((x0 + s * comp, y0 + comp * 0.35, z0 - comp * 0.18))
            meio = base.lerp(ponta, 0.45)
            cont = [base + Vector((0, -larg * 0.45, 0)), meio + Vector((0, -larg * 0.5, 0)), ponta, meio + Vector((0, larg * 0.45, 0)), base + Vector((0, larg * 0.5, 0))]
            partes.append(membrana("Nadadeira" + nome_n, [tuple(p) for p in cont], 0.55, 3)); NADAD.append(partes[-1])
            FL[nome_n + "_" + lado] = (base, meio, ponta)
    # nadadeira caudal vertical (reptil oceanico) e crista dorsal baixa
    yt = spine[-1][1]
    partes.append(membrana("Caudal", [(0, yt - 5.0, 8.4), (0, yt + 3.2, 15.5), (0, yt + 1.6, 8.0), (0, yt + 3.8, 2.6)], 0.4, 3)); NADAD.append(partes[-1])
    for i in range(6, N - 3, 2):
        z = 8.0 + rad[i][1] * 0.9
        partes.append(tubo("Placa", [(0, spine[i][1], z - 0.3), (0, spine[i][1] + 0.9, z + 0.9), (0, spine[i][1] + 1.6, z + 1.2)], [0.55 + rad[i][1] * 0.08, 0.35, 0.03], achatar=0.35))
    for s in (-1, 1):
        partes.append(tubo("CristaCabeca", [(s * 1.4, ys[1] + 0.6, 10.2), (s * 2.0, ys[2] + 1.2, 11.2), (s * 2.3, ys[3] + 1.4, 11.4)], [0.5, 0.28, 0.03], achatar=0.45))
    BONES_SPINE = 12
    PAD = [("Azul_Abissal", (0.01, 0.03, 0.08), (0.08, 0.20, 0.38), (0.04, 0.12, 0.25), (0.20, 0.36, 0.55)),
           ("Negro_Oceanico", (0.008, 0.01, 0.015), (0.08, 0.09, 0.11), (0.02, 0.025, 0.03), (0.14, 0.15, 0.17)),
           ("Prateado_Profundo", (0.08, 0.09, 0.11), (0.45, 0.50, 0.55), (0.20, 0.24, 0.28), (0.58, 0.62, 0.66))]
for o in partes:
    if o.name.startswith(("CristaCabeca", "Placa", "Sobrancelha", "Labio")):
        m = o.modifiers.new("Sub", "SUBSURF"); m.levels = 1
def marcar(o, g):
    vg = o.vertex_groups.new(name=g); vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
for o in partes:
    bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target="MESH")
    marcar(o, "REG_NAD" if o in NADAD else "REG_CORPO")
bpy.ops.object.select_all(action="DESELECT")
for o in partes: o.select_set(True)
bpy.context.view_layer.objects.active = corpo; bpy.ops.object.join()
mesh = bpy.context.view_layer.objects.active; mesh.name = NOME
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.remove_doubles(threshold=0.001); bpy.ops.object.mode_set(mode="OBJECT")
tris = sum(len(p.vertices) - 2 for p in mesh.data.polygons)
if tris > 17000:
    dec = mesh.modifiers.new("Dec", "DECIMATE"); dec.ratio = 16500 / tris; bpy.ops.object.modifier_apply(modifier="Dec")
print("TRIS_FINAL", sum(len(p.vertices) - 2 for p in mesh.data.polygons))

# ---------- armature: cadeia da coluna (cabeca na frente) + mandibula (+ nadadeiras do Leviata)
arm_d = bpy.data.armatures.new("Esqueleto"); arm = bpy.data.objects.new(NOME + "_Rig", arm_d); scn.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT"); EB = arm_d.edit_bones
def osso(nome, h, t, pai=None, deform=True):
    b = EB.new(nome); b.head = Vector(h); b.tail = Vector(t); b.roll = 0
    if pai: b.parent = EB[pai]
    b.use_deform = deform
z0 = spine[0][2]
osso("Raiz", (0, 0, 0), (0, 0, 2), None, False)
# pontos da cadeia distribuidos ao longo do comprimento (mais densos na cabeca)
cad = [0.0, 0.07, 0.14] + [0.14 + (1 - 0.14) * (k + 1) / (BONES_SPINE - 2) for k in range(BONES_SPINE - 2)]
P = [Vector((0, -COMP / 2 + COMP * c, z0)) for c in cad]
NOMES = ["Cabeca", "Pescoco"] + ["Corpo%d" % (k + 1) for k in range(BONES_SPINE - 3)] + ["Cauda"]
# raiz do corpo no centro: a cadeia sai do meio para as duas pontas (tronco estavel, cabeca e cauda ondulam)
meio = len(NOMES) // 2
osso(NOMES[meio], P[meio], P[meio + 1], "Raiz")
for k in range(meio - 1, -1, -1): osso(NOMES[k], P[k + 1], P[k], NOMES[k + 1])
for k in range(meio + 1, len(NOMES)): osso(NOMES[k], P[k], P[k + 1], NOMES[k - 1])
hd = Vector((0, P[1].y, z0 - (0.5 if ESP == "Serpente" else 1.4)))
osso("Mandibula", hd, Vector((0, P[0].y + 0.2, z0 - (0.45 if ESP == "Serpente" else 1.2))), "Cabeca")
FLB = []
if ESP != "Serpente":
    for k, (base, me_, ponta) in FL.items():
        par = "Corpo2" if k.startswith("Dianteira") else "Corpo4"
        osso("Nad" + k + "_1", base, me_, par); osso("Nad" + k + "_2", me_, ponta, "Nad" + k + "_1"); FLB += ["Nad" + k + "_1", "Nad" + k + "_2"]
bpy.ops.object.mode_set(mode="OBJECT")
print("OSSOS", len(arm_d.bones))
segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm_d.bones if b.use_deform}
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
vgs = {n: mesh.vertex_groups.new(name=n) for n in segs}
NADV = set()
for v in mesh.data.vertices:
    nad = any(mesh.vertex_groups[g.group].name == "REG_NAD" for g in v.groups)
    if nad: NADV.add(v.index)
    lst = [n for n in segs if (n not in FLB) or nad]
    # nadadeiras do Leviata: so ossos da nadadeira + coluna proxima
    ws = sorted(((1.0 / (dist_seg(v.co, *segs[n]) ** 4 + 0.02), n) for n in lst), reverse=True)[:4]
    tot = sum(w for w, _ in ws)
    for w, n in ws:
        if w / tot > 0.02: vgs[n].add([v.index], w / tot, "REPLACE")
for g in [g for g in mesh.vertex_groups if g.name.startswith("REG_")]: mesh.vertex_groups.remove(g)
m = mesh.modifiers.new("Armature", "ARMATURE"); m.object = arm; mesh.parent = arm

PB = arm.pose.bones
for pb in PB: pb.rotation_mode = "QUATERNION"
def R(ax, ay, az): return Matrix.Rotation(math.radians(az), 3, "Z") @ Matrix.Rotation(math.radians(ay), 3, "Y") @ Matrix.Rotation(math.radians(ax), 3, "X")
def aplicar(pose):
    for pb in PB: pb.rotation_quaternion = Quaternion(); pb.location = Vector()
    for nome, val in pose.items():
        pb = PB[nome]; M3 = pb.bone.matrix_local.to_3x3(); rot, loc = val if isinstance(val, tuple) else (val, None)
        pb.rotation_quaternion = (M3.inverted() @ rot @ M3).to_quaternion()
        if loc is not None: pb.location = M3.inverted() @ Vector(loc)
def S(x): return math.sin(2 * math.pi * x)
def C(x): return math.cos(2 * math.pi * x)
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
# onda lateral (yaw) que percorre a coluna da cabeca a cauda; cada osso gira relativo ao pai
# lado da cadeia: ossos "a frente" do meio giram em sentido oposto (o pai deles fica atras)
def onda(t, amp_cab, amp_cauda, compr_onda=1.0, pitch=0.0, curva=0.0, vertical=0.0):
    p = {}
    n = len(NOMES)
    for k, nome in enumerate(NOMES):
        u = k / (n - 1)
        a = (amp_cab + (amp_cauda - amp_cab) * u ** 1.4) * S(t - u / compr_onda)
        sinal = -1 if k < meio else 1
        yaw = sinal * (a * 0.5) + curva * (1 if k >= meio else -1) * 0.6
        pit = vertical * S(t - u / compr_onda) * (1 if k >= meio else -1) + (pitch if k == meio else 0)
        p[nome] = R(pit, 0, yaw)
    return p
FPS = 30; scn.render.fps = FPS; ACOES = {}
def acao(nome, dur, loop, f):
    act = bpy.data.actions.new(nome); arm.animation_data_create(); arm.animation_data.action = act
    nfr = max(2, int(dur * FPS))
    for fr in range(nfr + 1):
        aplicar(f(fr / nfr))
        for pb in PB: pb.keyframe_insert("rotation_quaternion", frame=fr + 1); pb.keyframe_insert("location", frame=fr + 1)
    act.use_fake_user = True; ACOES[nome] = act
    tr = arm.animation_data.nla_tracks.new(); tr.name = nome; tr.strips.new(nome, 1, act); arm.animation_data.action = None
def nadadeiras(p, t, amp, fase=0.0):
    for k in [b for b in FLB if b.endswith("_1")]:
        s = 1 if "_E_" in k + "_" else -1
        tras = "Traseira" in k; f = fase + (0.5 if tras else 0.0)
        p[k] = R(-25 * amp * S(t - f) * 0.6, -s * 22 * amp * S(t - f), s * 10 * amp * C(t - f))
        p[k.replace("_1", "_2")] = R(0, -s * 14 * amp * S(t - f - 0.15), 0)
    return p
if ESP == "Serpente":
    acao("Repouso", 4.0, True, lambda t: onda(t, 2, 6, 0.8))
    acao("Natacao", 1.6, True, lambda t: onda(t, 4, 26, 0.9))
    acao("NatacaoRapida", 0.9, True, lambda t: onda(t, 5, 34, 1.0))
    acao("VirarEsquerda", 1.6, True, lambda t: onda(t, 4, 20, 0.9, curva=8))
    acao("VirarDireita", 1.6, True, lambda t: onda(t, 4, 20, 0.9, curva=-8))
    acao("Subir", 1.6, True, lambda t: onda(t, 4, 22, 0.9, pitch=-10, vertical=3))
    acao("Descer", 1.6, True, lambda t: onda(t, 4, 22, 0.9, pitch=10, vertical=3))
    def espiral(t):  # Espiral Aquatica: o corpo se enrola (curva constante crescente) e solta
        u = ease(t / 0.4) * (1 - ease((t - 0.75) / 0.25)); p = onda(t, 2, 6, 0.8)
        for k, nome in enumerate(NOMES):
            if k > meio: p[nome] = R(0, 0, 30 * u)
            elif k < meio - 1: p[nome] = R(0, 0, -14 * u)
        return p
    acao("EspiralAquatica", 3.0, False, espiral)
    def mordida(t):
        u = ease(t / 0.3) * (1 - ease((t - 0.45) / 0.55)); p = onda(t, 2, 8, 0.9)
        p["Pescoco"] = R(6 * u, 0, 0); p["Cabeca"] = R(-8 * u, 0, 0); p["Mandibula"] = R(28 * u * (1 - ease((t - 0.3) / 0.15)), 0, 0)
        return p
    acao("MordidaProfunda", 1.2, False, mordida)
    acao("DeslizeTerrestre", 2.0, True, lambda t: onda(t, 3, 16, 0.6))
    ALT = 2.5
else:
    acao("Repouso", 5.0, True, lambda t: nadadeiras(onda(t, 1, 4, 0.7), t, 0.25))
    acao("Natacao", 2.4, True, lambda t: nadadeiras(onda(t, 1.5, 14, 0.8), t, 1.0))
    acao("NatacaoRapida", 1.4, True, lambda t: nadadeiras(onda(t, 2, 20, 0.85), t, 1.3))
    acao("VirarEsquerda", 2.4, True, lambda t: nadadeiras(onda(t, 1.5, 12, 0.8, curva=5), t, 0.9))
    acao("VirarDireita", 2.4, True, lambda t: nadadeiras(onda(t, 1.5, 12, 0.8, curva=-5), t, 0.9))
    acao("Subir", 2.4, True, lambda t: nadadeiras(onda(t, 1.5, 12, 0.8, pitch=-8, vertical=2), t, 1.0))
    acao("Descer", 2.4, True, lambda t: nadadeiras(onda(t, 1.5, 12, 0.8, pitch=8, vertical=2), t, 1.0))
    def mergulho(t):
        u = ease(t / 0.3) * (1 - ease((t - 0.7) / 0.3)); p = nadadeiras(onda(t, 2, 18, 0.85, pitch=18 * u, vertical=3), t, 1.3)
        return p
    acao("MergulhoAbissal", 3.0, False, mergulho)
    def rugido(t):
        u = ease(t / 0.3) * (1 - ease((t - 0.7) / 0.3)); p = nadadeiras(onda(t, 1, 5, 0.7), t, 0.4)
        p["Pescoco"] = R(-10 * u, 0, 0); p["Cabeca"] = R(-12 * u, 0, 0); p["Mandibula"] = R(26 * u, 0, 0)
        return p
    acao("RugidoOceanico", 3.0, False, rugido)
    def ruptura(t):  # Ruptura das Mares: giro do corpo e golpe da cauda
        u = ease(t / 0.4) * (1 - ease((t - 0.6) / 0.4)); p = nadadeiras(onda(t, 1, 10, 0.8), t, 0.8)
        p[NOMES[meio]] = R(0, 40 * u * S(t), 0)
        for k in range(meio + 1, len(NOMES)): p[NOMES[k]] = R(0, 0, 22 * u * S(t * 1.5))
        return p
    acao("RupturaDasMares", 2.4, False, ruptura)
    acao("DeslizeTerrestre", 3.0, True, lambda t: nadadeiras(onda(t, 1, 6, 0.6), t, 0.6))
    ALT = 8.0
print("ACOES", len(ACOES))

# ---------- material: escamas + nadadeiras (assado em atlas), 3 padroes oficiais
bpy.context.view_layer.objects.active = mesh
for o in scn.objects: o.select_set(False)
mesh.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003); bpy.ops.object.mode_set(mode="OBJECT")
def mk(nome, escala, vor=True):
    mat = bpy.data.materials.new(nome); mat.use_nodes = True; Nn = mat.node_tree.nodes; L = mat.node_tree.links
    b = Nn["Principled BSDF"]; tc = Nn.new("ShaderNodeTexCoord"); nz = Nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.15; nz.inputs["Detail"].default_value = 5
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    # barriga mais clara: mistura pela altura local (normal para baixo)
    geo = Nn.new("ShaderNodeNewGeometry"); sz = Nn.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sz.inputs[0])
    mr = Nn.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.8; mr.inputs["From Max"].default_value = 0.2; L.new(sz.outputs["Z"], mr.inputs["Value"])
    rp = Nn.new("ShaderNodeValToRGB")
    ad = Nn.new("ShaderNodeMath"); ad.operation = "MULTIPLY"; L.new(mr.outputs["Result"], ad.inputs[0]); L.new(nz.outputs["Fac"], ad.inputs[1])
    if vor:
        vo = Nn.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = escala; vo.feature = "DISTANCE_TO_EDGE"; L.new(tc.outputs["Object"], vo.inputs["Vector"])
        eg = Nn.new("ShaderNodeMapRange"); eg.inputs["From Max"].default_value = 0.1; L.new(vo.outputs["Distance"], eg.inputs["Value"])
        mu = Nn.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; L.new(ad.outputs[0], mu.inputs[0]); L.new(eg.outputs["Result"], mu.inputs[1])
        L.new(mu.outputs[0], rp.inputs["Fac"])
        bp = Nn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.45; bp.inputs["Distance"].default_value = 0.08; L.new(eg.outputs["Result"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    else:
        L.new(ad.outputs[0], rp.inputs["Fac"])
    L.new(rp.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.42
    return mat, rp
mat, rp = mk("Escamas", 7.0 if ESP == "Serpente" else 3.5); mat2, rp2 = mk("Nadadeira", 1.0, vor=False)
mesh.data.materials.clear(); mesh.data.materials.append(mat); mesh.data.materials.append(mat2)
for poly in mesh.data.polygons:
    if all(i in NADV for i in poly.vertices): poly.material_index = 1
scn.render.engine = "CYCLES"; scn.cycles.samples = 4
def cores(pd):
    rp.color_ramp.elements[0].color = pd[1] + (1,); rp.color_ramp.elements[1].color = pd[2] + (1,)
    rp2.color_ramp.elements[0].color = pd[3] + (1,); rp2.color_ramp.elements[1].color = pd[4] + (1,)
def assar(tipo, nome, cs):
    img = bpy.data.images.new(nome, 2048, 2048, alpha=False); img.colorspace_settings.name = cs; nodes = []
    for mt in (mat, mat2):
        Nn = mt.node_tree.nodes; tn = Nn.new("ShaderNodeTexImage"); tn.image = img
        for n in Nn: n.select = False
        tn.select = True; Nn.active = tn; nodes.append(tn)
    if tipo == "DIFFUSE": bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
    else: bpy.ops.object.bake(type="NORMAL", margin=4)
    img.filepath_raw = os.path.join(DEST, nome + ".png"); img.file_format = "PNG"; img.save(); return nodes[0]
cores(PAD[0]); tnor = assar("NORMAL", NOME + "_Normal", "Non-Color")
for pd in PAD[1:]: cores(pd); assar("DIFFUSE", NOME + "_Cor_" + pd[0], "sRGB")
cores(PAD[0]); tcor = assar("DIFFUSE", NOME + "_Cor_" + PAD[0][0], "sRGB")
Nn = mat.node_tree.nodes; L = mat.node_tree.links
for n in list(Nn):
    if n not in (tcor, tnor): Nn.remove(n)
o_ = Nn.new("ShaderNodeOutputMaterial"); b_ = Nn.new("ShaderNodeBsdfPrincipled"); nm = Nn.new("ShaderNodeNormalMap")
L.new(tcor.outputs["Color"], b_.inputs["Base Color"]); L.new(tnor.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b_.inputs["Normal"]); b_.inputs["Roughness"].default_value = 0.42; L.new(b_.outputs["BSDF"], o_.inputs["Surface"])
for poly in mesh.data.polygons: poly.material_index = 0
mesh.data.materials.pop(index=1)

# ---------- previas (agua azul como fundo)
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 600
sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.0; so = bpy.data.objects.new("Sol", sun); scn.collection.objects.link(so); so.rotation_euler = (math.radians(40), 0, math.radians(30))
scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes = True; scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.36, 0.48, 1)
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=4.2, location=(COMP * 0.18, -COMP * 0.35, ALT)); h1 = bpy.context.active_object
cam = bpy.data.cameras.new("Cam"); co = bpy.data.objects.new("Cam", cam); scn.collection.objects.link(co); scn.camera = co; cam.lens = 35
def foto(nome, an, t, loc, alvo):
    act = ACOES[an]; arm.animation_data.action = act; scn.frame_set(1 + int(t * (act.frame_range[1] - 1)))
    co.location = loc; co.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(OUT, "%s_%s.png" % (ESP, nome)); bpy.ops.render.render(write_still=True); arm.animation_data.action = None
foto("natacao_cima", "Natacao", 0.0, (0, COMP * 0.05, COMP * 1.05), (0, 0, ALT))
foto("natacao_34", "Natacao", 0.3, (COMP * 0.8, -COMP * 0.8, ALT + COMP * 0.35), (0, 0, ALT))
foto("lateral", "Repouso", 0.0, (COMP * 1.1, 0, ALT + 2), (0, 0, ALT))
foto("especial", "EspiralAquatica" if ESP == "Serpente" else "RugidoOceanico", 0.55, (COMP * 0.7, -COMP * 0.7, ALT + COMP * 0.4), (0, 0, ALT))
for o in (h1, co, so): bpy.data.objects.remove(o, do_unlink=True)
for o in scn.objects: o.select_set(False)
arm.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=os.path.join(DEST, NOME + ".glb"), export_format="GLB", use_selection=True, export_animations=True, export_animation_mode="ACTIONS", export_skins=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(DEST, NOME + ".fbx"), use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True,
                         bake_anim_use_nla_strips=False, path_mode="COPY", embed_textures=True, axis_forward="-Z", axis_up="Y")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DEST, NOME + ".blend"))
d = mesh.dimensions; print("DIM %.1f x %.1f x %.1f" % (d.x, d.y, d.z)); print("EXPORTADO")

