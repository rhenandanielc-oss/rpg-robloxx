"""Renders de revisao do CR_Urso v2 com luz neutra de estudio.
Grupos: corpo (frente, perfil, costas, 3/4, cima), cabeca (frente, perfil, 3/4), cabeca sem pelagem longa, boca fechada/aberta,
patas e garras, dorso, e POSE ESTATICA DE TESTE (cabeca erguida + boca aberta) na camera aproximada da referencia.
A pose e deformacao direta por pesos procedurais, NAO e rig nem animacao. Nada e salvo no .blend.
Uso: blender -b <arquivo.blend> -P render_v2.py -- <saida_dir> [rapido] [grupos=corpo,cabeca,boca,patas,dorso,pose,nu]"""
import bpy, sys, os, math
from mathutils import Vector as V, Matrix
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True); RAPIDO = "rapido" in ARGS
GR = next((a.split("=")[1].split(",") for a in ARGS if a.startswith("grupos=")), ["corpo", "cabeca", "nu", "boca", "patas", "dorso", "pose"])
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
w = bpy.data.worlds.new("Neutro"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.42, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
for nome, en, cor, rot in (("Chave", 3.0, (1.0, 0.97, 0.93), (math.radians(48), 0, math.radians(-35))),
                           ("Recorte", 2.0, (0.95, 0.97, 1.0), (math.radians(120), 0, math.radians(160))),
                           ("Preench", 1.0, (1.0, 1.0, 1.0), (math.radians(65), 0, math.radians(110)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor; l.angle = math.radians(3)
    lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
if "Chao" not in bpy.data.objects:
    bpy.ops.mesh.primitive_plane_add(size=80); chao = bpy.context.object; chao.name = "Chao"
    mc = bpy.data.materials.new("Chao"); mc.use_nodes = True
    mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.30, 0.30, 0.30, 1)
    mc.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95; chao.data.materials.append(mc)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16 if RAPIDO else 64
for k, v in (("use_raytracing", True), ("use_shadows", True)):
    if hasattr(sc.eevee, k): setattr(sc.eevee, k, v)
sc.view_settings.view_transform = "AgX"
camd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
camd.clip_start = 0.02; camd.clip_end = 400
def render(nome, pos, alvo, lente, rx=1280, ry=720):
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
MALHAS = [o for o in sc.objects if o.type == "MESH" and o.name != "Chao" and not o.hide_render]
LONGO = [o for o in MALHAS if o.name.startswith(("CR_Urso_Pelo", "Urso_Pelo", "CR_Urso_Vegetacao", "Urso_Vegetacao", "CR_Urso_Casca", "Urso_Casca", "CR_Urso_Cipo"))]
REPOUSO = {o.name: [v.co.copy() for v in o.data.vertices] for o in MALHAS}

if "corpo" in GR:
    for nome, pos, alvo, lente in (("vista_frente", (0, -30, 5.0), (0, 0, 4.6), 50), ("vista_lado", (-34, 0, 5.0), (0, -0.8, 4.6), 50),
                                   ("vista_tras", (0, 30, 6.0), (0, 0, 4.6), 50), ("vista_34", (-21, -22, 9.0), (0, -0.8, 4.4), 50),
                                   ("vista_cima", (-9, -2, 26), (0, -1.5, 6), 45)):
        render(nome, pos, alvo, lente)
# alvos automaticos: ponta do focinho e patas dianteiras medidas na malha principal (serve para v2 por codigo e Meshy)
amostra = []
for o_ in MALHAS:
    passo = max(1, len(o_.data.vertices) // 40000)
    amostra += [o_.matrix_world @ o_.data.vertices[i].co for i in range(0, len(o_.data.vertices), passo)]
YMIN = min(p.y for p in amostra if p.z > 3.0); ZF = sum(p.z for p in amostra if p.y < YMIN + 0.35 and p.z > 3.0) / max(1, len([p for p in amostra if p.y < YMIN + 0.35 and p.z > 3.0]))
T = V((0, YMIN + 1.1, ZF + 0.15))
PD = [p for p in amostra if p.z < 0.6 and p.y < (YMIN + 6)]; PE = V((sum(p.x for p in PD if p.x < 0) / max(1, len([p for p in PD if p.x < 0])), sum(p.y for p in PD) / max(1, len(PD)), 0.4))
print("ALVOS cabeca", tuple(round(c, 2) for c in T), "pata", tuple(round(c, 2) for c in PE))
CAB = [("cab_frente", tuple(T + V((0, -6.5, 0.4))), tuple(T), 70), ("cab_lado", tuple(T + V((-6.5, 0, 0.2))), tuple(T), 70),
       ("cab_34", tuple(T + V((-4.6, -4.6, 0.8))), tuple(T), 70)]
if "cabeca" in GR:
    for c in CAB: render(*c, rx=1000, ry=800)
if "dorso" in GR:
    render("dorso_34", (-12, -9, 15), (0, -2.0, 7.2), 45); render("dorso_perto", (-7.5, -6.5, 11.5), (0, -2.6, 7.6), 40)
if "patas" in GR:
    render("patas_frente", tuple(PE + V((-2.2, -5.3, 1.0))), tuple(PE + V((0.8, 0, 0.1))), 45, 1100, 700); render("pata_perto", tuple(PE + V((-1.7, -2.6, 0.7))), tuple(PE + V((0, -0.4, -0.05))), 50, 1000, 700)
if "nu" in GR:                                                          # volumes sem cor: argila cinza (e sem cartoes de pelo, se houver)
    for o in LONGO: o.hide_render = True
    arg_ = bpy.data.materials.new("Argila"); arg_.use_nodes = True
    arg_.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.55, 0.53, 0.50, 1)
    arg_.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.7
    orig = {o.name: list(o.data.materials) for o in MALHAS}
    for o in MALHAS:
        for i in range(len(o.data.materials)): o.data.materials[i] = arg_
    for c in CAB: render(c[0] + "_argila", *c[1:], rx=1000, ry=800)
    render("corpo_argila_34", (-21, -22, 9.0), (0, -0.8, 4.4), 50)
    for o in MALHAS:
        for i, m in enumerate(orig[o.name]): o.data.materials[i] = m
    for o in LONGO: o.hide_render = False

# ------------------------------------------------------------------ pose estatica de teste
PERFIL = next((x.split("=")[1] for x in ARGS if x.startswith("perfil=")), "codigo")
if PERFIL == "meshy":                      # cabeca da malha do Meshy (linha dos labios medida por raio na malha)
    DOBRA = V((0, -4.70, 6.30)); CANTO = -5.13
    LAB = [(-5.13, 6.263), (-5.24, 6.213), (-5.39, 6.153), (-5.55, 6.133), (-5.72, 6.150), (-5.90, 6.140), (-6.25, 6.140)]
    def lab(y):
        if y >= LAB[0][0]: return LAB[0][1]
        for (y0, z0), (y1, z1) in zip(LAB, LAB[1:]):
            if y1 <= y <= y0: return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
        return LAB[-1][1]
    YJ = -4.75
    PESC = [(V((0, -2.6, 6.9)), lambda p: suave((-2.4 - p.y) / 1.4) * suave((p.z - 4.8) / 1.2), 0.40),
            (V((0, -3.5, 7.0)), lambda p: suave((-3.3 - p.y) / 1.0) * suave((p.z - 4.8) / 1.2), 0.35),
            (V((0, -4.3, 7.0)), lambda p: suave((-4.1 - p.y) / 0.5) * suave((p.z - 4.8) / 1.2), 0.25)]
else:
    DOBRA = V((0, -6.85, 5.95)); CANTO = -7.30; YJ = -6.7
    def lab(y): return 6.00 - 0.05 * suave((y + 9.0) / 1.6)
    PESC = [(V((0, -3.9, 6.4)), lambda p: suave((-3.6 - p.y) / 1.6) * suave((p.z - 4.6) / 1.2), 0.40),
            (V((0, -5.2, 6.5)), lambda p: suave((-4.9 - p.y) / 1.2) * suave((p.z - 4.6) / 1.2), 0.35),
            (V((0, -6.4, 6.4)), lambda p: suave((-6.2 - p.y) / 0.6) * suave((p.z - 4.6) / 1.2), 0.25)]
def w_mand(p, duro=False):
    if p.y > YJ: return 0.0
    if p.y < CANTO: return (1.0 if p.z < lab(p.y) else 0.0) if duro else suave((lab(p.y) - p.z) / 0.012 + 0.5)
    return suave((lab(CANTO) - 0.02 - p.z) / 0.25) * suave((YJ - p.y) / (YJ - CANTO))
MAND = ("Dente_Inf", "Gengiva_Inf", "Lingua"); CRANIO = ("Dente_Sup", "Gengiva_Sup", "Olho", "Palpebra", "Orelha")
def posar(abre, ergue):
    for o in MALHAS:
        mw = o.matrix_world; inv = mw.inverted(); rep = REPOUSO[o.name]
        base = o.name.split(".")[0]; am = o.data.attributes.get("mand")
        for i, v in enumerate(o.data.vertices):
            p0 = mw @ rep[i]
            wm = am.data[i].value if am else (1.0 if base in MAND else (0.0 if base in CRANIO else w_mand(p0)))
            p = DOBRA + Matrix.Rotation(abre * wm, 3, "X") @ (p0 - DOBRA) if wm > 0 else p0.copy()
            for piv, fw, parte in PESC:
                wv = fw(p0)
                if wv > 0: p = piv + Matrix.Rotation(-ergue * parte * wv, 3, "X") @ (p - piv)
            v.co = inv @ p
        o.data.update()
if "boca" in GR:
    TB = T + V((0, -0.3, -0.45))
    render("boca_fechada", tuple(TB + V((-3.0, -3.4, 0.4))), tuple(TB), 75, 1000, 800)
    posar(math.radians(36), 0.0)
    render("boca_aberta_34", tuple(TB + V((-3.0, -3.4, 0.4))), tuple(TB), 75, 1000, 800)
    render("boca_aberta_frente", tuple(TB + V((0, -4.4, 0.25))), tuple(TB + V((0, 0, -0.1))), 75, 1000, 800)
    render("boca_aberta_lado", tuple(TB + V((-4.4, 0, 0.1))), tuple(TB + V((0, 0, -0.1))), 70, 1000, 800)
if "pose" in GR:
    posar(math.radians(38), math.radians(30))
    render("pose_ref", (-15.5, -12.0, 2.2), (0.6, -1.6, 5.4), 26, 1672, 941)
    render("pose_lado", (-26, -5.0, 6.5), (0, -5.0, 6.5), 50, 1100, 700)
    render("pose_cab", tuple(T + V((-4.0, -5.5, 2.4))), tuple(T + V((0, 0.4, 1.6))), 60, 900, 700)
for o in MALHAS:
    for i, v in enumerate(o.data.vertices): v.co = REPOUSO[o.name][i]
print("RENDER_OK")
