"""Renders de revisao do CR_Urso (luz neutra): frente, lado, tras, 3/4, cabeca; depois uma POSE DE TESTE (cabeca
erguida + boca aberta, por deformacao direta, sem rig) na camera aproximada da referencia, e pranchas lado a lado.
A pose de teste NAO e salva no .blend.
Uso: blender -b <arquivo.blend> -P render_urso.py -- <saida_dir> [rapido]"""
import bpy, sys, os, math
from mathutils import Vector as V, Matrix
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True); RAPIDO = "rapido" in ARGS
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref", "urso-silvestre-referencia.png")
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

# ------------------------------------------------------------------ luz neutra de estudio
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
w = bpy.data.worlds.new("Neutro"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.42, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.55
for nome, en, cor, rot in (("Chave", 3.2, (1.0, 0.97, 0.93), (math.radians(48), 0, math.radians(-35))),
                           ("Recorte", 2.4, (0.95, 0.97, 1.0), (math.radians(120), 0, math.radians(160))),
                           ("Preench", 0.9, (1.0, 1.0, 1.0), (math.radians(65), 0, math.radians(110)))):
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
camd.clip_start = 0.05; camd.clip_end = 400
def render(nome, pos, alvo, lente, rx=1280, ry=720):
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
    return sc.render.filepath

VISTAS = [("vista_frente", (0, -30, 5.0), (0, 0, 4.6), 50), ("vista_lado", (-34, 0, 5.0), (0, -0.8, 4.6), 50),
          ("vista_tras", (0, 30, 6.0), (0, 0, 4.6), 50), ("vista_34", (-21, -22, 9.0), (0, -0.8, 4.4), 50),
          ("vista_cima", (-9, -2, 26), (0, -1.5, 6), 45), ("dorso_34", (-12, -9, 15), (0, -2.0, 7.2), 45),
          ("cab_lado", (-7.5, -8.0, 6.6), (0, -8.0, 6.4), 60), ("cab_frente", (0, -16.5, 6.9), (0, -8.0, 6.4), 60),
          ("cab_34", (-5.5, -13.5, 7.5), (0, -8.0, 6.4), 60)]
feitos = []
for nome, pos, alvo, lente in VISTAS:
    if RAPIDO and nome.startswith("cab_") and nome != "cab_34": continue
    if "so_dorso" in ARGS and nome not in ("vista_cima", "dorso_34", "cab_34"): continue
    feitos.append(render(nome, pos, alvo, lente))

# ------------------------------------------------------------------ pose de teste (so para comparar com a referencia)
ABRE, ERGUE = math.radians(38), math.radians(34)
DOBRA = V((0, -6.80, 5.95))
def lab(y): return 5.98 + 0.04 * suave((y + 9.1) / 1.6)
def w_mand(p):
    if p.y > -6.75: return 0.0
    abaixo = suave((lab(min(p.y, -7.25)) + 0.01 - p.z) / 0.02) if p.y < -7.25 else suave((6.0 - p.z) / 0.35)
    return abaixo * (1.0 if p.y < -7.25 else suave((-6.75 - p.y) / 0.5))
PESC = [(V((0, -4.3, 6.6)), lambda p: suave((-4.0 - p.y) / 1.4) * suave((p.z - 4.4) / 1.0), 0.55), (V((0, -6.0, 6.5)), lambda p: suave((-5.6 - p.y) / 0.9) * suave((p.z - 4.4) / 1.0), 0.45)]
def posar(p0):
    p = p0.copy(); wm = w_mand(p0)
    if wm > 0: p = DOBRA + Matrix.Rotation(ABRE * wm, 3, "X") @ (p - DOBRA)
    for piv, fw, parte in PESC:
        wv = fw(p0)
        if wv > 0: p = piv + Matrix.Rotation(-ERGUE * parte * wv, 3, "X") @ (p - piv)
    return p
for o in sc.objects:
    if o.type != "MESH" or o.name == "Chao": continue
    mw = o.matrix_world; inv = mw.inverted()
    eh_mand = o.name.startswith("Dente_Inf") or o.name.startswith("Lingua")
    for v in o.data.vertices:
        p0 = mw @ v.co
        if eh_mand:                                         # pecas da mandibula: peso 1 da mandibula
            q = DOBRA + Matrix.Rotation(ABRE, 3, "X") @ (p0 - DOBRA)
            for piv, fw, parte in PESC: q = piv + Matrix.Rotation(-ERGUE * parte * fw(p0), 3, "X") @ (q - piv)
            v.co = inv @ q
        elif o.name.startswith("Dente_Sup") or o.name.startswith("Olho"):   # pecas do cranio: so a cabeca
            q = p0.copy()
            for piv, fw, parte in PESC: q = piv + Matrix.Rotation(-ERGUE * parte * fw(p0), 3, "X") @ (q - piv)
            v.co = inv @ q
        else: v.co = inv @ posar(p0)
    o.data.update()
# camera da referencia: baixa, 3/4 frente-direita, grande-angular
feitos.append(render("pose_ref", (-15.5, -12.0, 2.2), (0.6, -1.6, 5.4), 26, 1672, 941))
feitos.append(render("pose_lado", (-26, -5.0, 6.5), (0, -5.0, 6.0), 50, 1100, 700))
feitos.append(render("pose_cab", (-6.0, -12.5, 9.4), (0, -8.2, 8.0), 60, 900, 700))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_pose_teste_NAO_USAR.blend")) if "salvar_pose" in ARGS else None
print("RENDER_OK", len(feitos))
