"""render_garra_r5.py = render_ataque_r4 + fade de entrada do jogo (Play 0,06 s = 1,8 q), alvo de ensaio (HRP 2x5x2, face a
7 studs do pivo) e vista frente_pata. Itens "acao@base:fase". Uso: ... -- <dir> quadros <itens,> <vistas,> <q,...> [alvo]
                                                              ou -- <dir> seq <acao@base:fase> <vistas,> <tag> [alvo]
Revisao do ataque basico v43 r4 x r3 (17/11/2026). Sobrepoe cada golpe PARCIAL a uma locomocao (como o Roblox em
prioridade Action2: ossos com chave do golpe substituem os da locomocao, inclusive a translacao do Pescoco1 na r4).
Os ossos com chave sao lidos das proprias acoes (fcurves). As acoes R3_* sao a r3 copiada pelo gen_ataque_v43r4.
Modos (argumento 2):
  quadros  <acoes,> <base:fase,> <vistas,> <q,q,...>   -> PNG por (acao, base, vista, q)
  seq      <acoes,> <base:fase> <vistas,>               -> sequencia continua dos golpes (15 q cada) sobre a base andando
Vistas: perfil_E (corpo inteiro), cabeca (3/4 frente, close), frente (close de frente da boca), pata (close das dianteiras).
Uso: blender -b anim_v43r4/CR_LoboArtico_Anim.blend -P render_ataque_r4.py -- <dir> <modo> ..."""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True); MODO = a[1]
sc = bpy.context.scene; rig = bpy.data.objects["LoboArtico_Rig"]; rig.data.pose_position = "POSE"; P = rig.pose.bones
for o in sc.objects:
    if o.type == "MESH" and o.name.startswith(("LOD1", "LOD2")): o.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y = 480, 330
try: sc.eevee.taa_render_samples = 8          # revisao: rapido (PC compartilhado)
except Exception: pass
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.36, 0.42, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.002)); ch = bpy.context.object
mc = bpy.data.materials.new("Chao"); mc.use_nodes = True; mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.52, 0.55, 1); ch.data.materials.append(mc)
for nome, loc, en, sz in (("Chave", (9, -6, 12), 2200, 8), ("Recorte", (-8, 8, 9), 900, 6), ("Frente", (2, -16, 6), 600, 6)):
    ld = bpy.data.lights.new(nome, "AREA"); ld.energy = en; ld.size = sz; lo = bpy.data.objects.new(nome, ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = (V((0, 0, 3)) - V(loc)).to_track_quat("-Z", "Y").to_euler()
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
try: sc.view_settings.view_transform = "AgX"
except Exception: pass
def ossos_de(ac):
    r = {}
    for fc in ac.fcurves if hasattr(ac, "fcurves") else []:
        n = fc.data_path.split('"')[1] if '"' in fc.data_path else None
        if n: r.setdefault(n, set()).add(fc.data_path.split(".")[-1])
    if not r:                                   # acoes em camadas (Blender 5): canais por slot
        for ly in ac.layers:
            for st in ly.strips:
                for cb in st.channelbags:
                    for fc in cb.fcurves:
                        n = fc.data_path.split('"')[1]; r.setdefault(n, set()).add(fc.data_path.split(".")[-1])
    return r
def aplicar(nome, q):
    ac = bpy.data.actions[nome]; rig.animation_data.action = ac
    if len(ac.slots): rig.animation_data.action_slot = ac.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update(); rig.animation_data.action = None
CACHE = {}
def pose(golpe, qg, base, qb):
    if golpe not in CACHE: CACHE[golpe] = ossos_de(bpy.data.actions[golpe])
    canais = CACHE[golpe]; w = min(1.0, qg / 1.8)                 # fade de entrada do jogo
    for pb in P: pb.matrix_basis.identity()
    aplicar(golpe, qg); val = {o: (P[o].rotation_quaternion.copy(), P[o].location.copy()) for o in canais}
    for pb in P: pb.matrix_basis.identity()
    aplicar(base, qb)
    for o, (r, l) in val.items():
        r0 = P[o].rotation_quaternion.copy()
        if r0.dot(r) < 0: r = -r
        P[o].rotation_quaternion = r0.slerp(r, w)
        if "location" in canais[o]: P[o].location = P[o].location.lerp(l, w)
    bpy.context.view_layer.update()
def camera(v):
    W = rig.matrix_world
    if v == "perfil_E": c0 = W @ P["Coluna2"].head; c0 = V((c0.x, c0.y - 1.6, 3.4)); pos = c0 + V((23, 0, 1.4)); cd.lens = 50
    elif v == "cabeca": c0 = W @ P["Cabeca"].head; pos = c0 + V((6.0, -5.2, 0.9)); cd.lens = 55
    elif v == "frente": c0 = W @ P["Cabeca"].tail + V((0, 0.4, -0.2)); pos = c0 + V((0.6, -6.5, 0.3)); cd.lens = 55
    elif v == "pata":
        pe, pd = W @ P["Dedos_E"].tail, W @ P["Dedos_D"].tail; c0 = (pe + pd) / 2 + V((0, -0.6, 1.1)); pos = c0 + V((7.5, -7.0, 1.4)); cd.lens = 45
    if v == "frente_pata":
        pe, pd = W @ P["Dedos_E"].tail, W @ P["Dedos_D"].tail; c0 = (pe + pd) / 2 + V((0, -0.4, 1.0)); pos = c0 + V((0.8, -9.0, 0.6)); cd.lens = 45
    cam.location = pos; cam.rotation_euler = (c0 - pos).to_track_quat("-Z", "Y").to_euler()
def render(path): sc.render.filepath = path; bpy.ops.render.render(write_still=True)
if a[-1] == "alvo":                                                   # alvo de ensaio do teste no Studio
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -8.0, 2.5)); al = bpy.context.object; al.scale = (2, 2, 5)
    ma = bpy.data.materials.new("Alvo"); ma.use_nodes = True; ma.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.6, 0.08, 0.06, 1)
    ma.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.55
    try: ma.surface_render_method = "BLENDED"
    except Exception: pass
    al.data.materials.append(ma)
if MODO == "quadros":
    itens = [x.split("@") for x in a[2].split(",")]; vistas = a[3].split(","); qs = [int(x) for x in a[4].split(",")]
    for ac, bf in itens:
        b, f = bf.split(":"); f = int(f); nb = int(bpy.data.actions[b].frame_range[1])
        for q in qs:
            pose(ac, q, b, (f + q) % max(nb, 1))
            for v in vistas:
                camera(v); render(os.path.join(OUT, "%s__%s%d__%s__q%02d.png" % (ac, b, f, v, q)))
elif MODO == "seq":
    ac, bf = a[2].split("@"); b, f = bf.split(":"); f = int(f); vistas = a[3].split(","); tag = a[4]
    nb = int(bpy.data.actions[b].frame_range[1])
    for q in range(16):
        pose(ac, q, b, (f + q) % max(nb, 1))
        for v in vistas: camera(v); render(os.path.join(OUT, "%s__%s__%04d.png" % (tag, v, q)))
print("RENDER_GARRA_R5_OK", flush=True)
