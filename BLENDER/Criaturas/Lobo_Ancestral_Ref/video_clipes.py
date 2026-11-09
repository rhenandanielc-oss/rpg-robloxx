"""Videos de revisao dos clipes: 3 vistas (lateral, frontal, 3/4) lado a lado, chao quadriculado que CORRE na
velocidade do clipe (pata apoiada deve parecer parada sobre o chao; escorregao fica visivel), em 30 fps (normal) e
10 fps (lenta, 1/3). Ciclos curtos sao repetidos. Quadros em PNG -> montagem (PIL do Python do sistema nao existe no
Blender; a montagem e feita com numpy nas imagens do Blender) -> MP4 pelo sequenciador do Blender.
Uso: blender -b rig/Lobo_Ancestral_Anim.blend -P video_clipes.py -- <saida_dir> <clipes,separados> [manifesto.json]"""
import bpy, sys, os, json, math, shutil
import numpy as np
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
NOMES = A[1].split(","); MAN = json.load(open(A[2], encoding="utf-8")) if len(A) > 2 else {}
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for o in sc.objects:
    if o.type == "MESH" and o is not LO and not o.name.startswith("Plane"): o.hide_render = True
    if o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
# chao quadriculado (1 stud) com deslocamento animado
chao = next((o for o in sc.objects if o.name.startswith("Plane")), None)
if chao is None:
    bpy.ops.mesh.primitive_plane_add(size=80); chao = bpy.context.object
chao.hide_render = False
mat = bpy.data.materials.new("ChaoXadrez")
if mat.node_tree is None: mat.use_nodes = True
nt = mat.node_tree; bs = nt.nodes["Principled BSDF"]; tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 1.0
ck.inputs["Color1"].default_value = (0.20, 0.22, 0.12, 1); ck.inputs["Color2"].default_value = (0.11, 0.13, 0.07, 1)
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], ck.inputs["Vector"]); nt.links.new(ck.outputs["Color"], bs.inputs["Base Color"])
bs.inputs["Roughness"].default_value = 0.95
chao.data.materials.clear(); chao.data.materials.append(mat)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8
W, H = 640, 400; sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.image_settings.file_format = "PNG"
cam = sc.camera; camd = cam.data; camd.type = "PERSP"
VISTAS = [("lateral", V((24, -1.5, 4.0)), V((0, -1.5, 3.4)), 40), ("frontal", V((0, -24, 4.0)), V((0, -1, 3.4)), 40),
          ("tres_quartos", V((15, -16, 7.5)), V((0, -1, 3.2)), 40)]
# MARCAS DE CONTATO (env LOBO_MARCAS=1): disco verde no chao sob cada regiao apoiada (z < 0,12), laranja se perto (< 0,4)
MARCAS = os.environ.get("LOBO_MARCAS") == "1"
if MARCAS:
    _gi = {g.index: g.name for g in LO.vertex_groups}
    _D = np.array([_gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in LO.data.vertices])
    _pel = np.array([sum(g.weight for g in v.groups if _gi[g.group].startswith(("Pelo", "Cauda"))) for v in LO.data.vertices])
    def _g(ns, sem=True): return np.nonzero(np.isin(_D, ns) & ((_pel < 0.05) if sem else True))[0]
    REGS = [_g(["Pelve", "Coluna1"]), _g(["Peito", "Coluna2"]), _g(["AntebracoE"]), _g(["AntebracoD"]), _g(["MaoE", "DedosE"]), _g(["MaoD", "DedosD"]),
            _g(["MetatarsoE", "PeE"]), _g(["MetatarsoD", "PeD"]), _g(["Cabeca", "Mandibula"], False), _g(["Cauda%d" % i for i in range(1, 8)], False)]
    MATM = {}
    for k_, c_ in (("ok", (0.1, 0.95, 0.2, 1)), ("perto", (1.0, 0.55, 0.05, 1))):
        m_ = bpy.data.materials.new("marca_" + k_); m_.use_nodes = True; n_ = m_.node_tree; n_.nodes.clear()
        e_ = n_.nodes.new("ShaderNodeEmission"); e_.inputs["Color"].default_value = c_; e_.inputs["Strength"].default_value = 2.5
        o_ = n_.nodes.new("ShaderNodeOutputMaterial"); n_.links.new(e_.outputs["Emission"], o_.inputs["Surface"]); MATM[k_] = m_
    DISCOS = []
    for _ in REGS:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.02); d_ = bpy.context.active_object; d_.data.materials.append(MATM["ok"]); DISCOS.append(d_)
    def marcas():
        ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        for d_, idx in zip(DISCOS, REGS):
            j = min(idx, key=lambda i: ev[i].co.z); c = ev[j].co
            if c.z < 0.4:
                d_.hide_render = False; d_.location = (c.x, c.y, 0.012); d_.data.materials[0] = MATM["ok" if c.z < 0.12 else "perto"]
            else: d_.hide_render = True
def ler_png(caminho):
    im = bpy.data.images.load(caminho); a = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)
    bpy.data.images.remove(im); return a
def codificar(pasta, padrao, n, fps, destino):
    s2 = bpy.data.scenes.new("Video"); s2.render.resolution_x, s2.render.resolution_y = 3 * W, H
    s2.render.fps = fps
    if hasattr(s2.render.image_settings, "media_type"): s2.render.image_settings.media_type = "VIDEO"
    s2.render.image_settings.file_format = "FFMPEG"; s2.render.ffmpeg.format = "MPEG4"
    s2.render.ffmpeg.codec = "H264"; s2.render.ffmpeg.constant_rate_factor = "HIGH"
    se = s2.sequence_editor_create()
    arquivos = sorted(f for f in os.listdir(pasta) if f.startswith(padrao))
    st = se.strips.new_image("q", os.path.join(pasta, arquivos[0]), 1, 1) if hasattr(se, "strips") else se.sequences.new_image("q", os.path.join(pasta, arquivos[0]), 1, 1)
    for f in arquivos[1:]: st.elements.append(f)
    s2.frame_start = 1; s2.frame_end = len(arquivos); s2.render.filepath = destino
    bpy.context.window_manager  # noqa
    with bpy.context.temp_override(scene=s2):
        bpy.ops.render.render(animation=True, scene=s2.name)
    bpy.data.scenes.remove(s2)
for nome in NOMES:
    act = bpy.data.actions["Lobo_" + nome]; arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = [int(round(v)) for v in act.frame_range]; nq = f1 - f0 + 1
    info = MAN.get(nome, {}); loop = info.get("loop", act.get("loop", False)); vel = info.get("velocidade_studs_s", act.get("velocidade", 0.0))
    rep = max(1, int(math.ceil(48 / nq))) if loop else 1
    total = nq * rep if loop else nq
    tmp = os.path.join(OUT, "_q_" + nome); os.makedirs(tmp, exist_ok=True)
    for i in range(total):
        fr = f0 + (i % nq); sc.frame_set(fr)
        if MARCAS: marcas()
        mp.inputs["Location"].default_value[1] = -vel * (i / 30.0) * 0 + vel * (i / 30.0)   # chao corre para +Y (o lobo "anda" para -Y)
        tiras = []
        for vn, pos, alvo, lente in VISTAS:
            cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
            caminho = os.path.join(tmp, "%s_%04d.png" % (vn, i)); sc.render.filepath = caminho; bpy.ops.render.render(write_still=True)
            tiras.append(ler_png(caminho)); os.remove(caminho)
        quad = np.concatenate(tiras, axis=1)
        im = bpy.data.images.new("m", 3 * W, H, alpha=True); im.pixels.foreach_set(quad.ravel())
        im.filepath_raw = os.path.join(tmp, "m_%04d.png" % i); im.file_format = "PNG"; im.save(); bpy.data.images.remove(im)
        if i in (0, total // 2) and rep == 1 or i == 0:
            shutil.copy(os.path.join(tmp, "m_%04d.png" % i), os.path.join(OUT, "%s_quadro%04d.png" % (nome, i)))
    codificar(tmp, "m_", total, 30, os.path.join(OUT, "Lobo_%s_normal.mp4" % nome))
    codificar(tmp, "m_", total, 10, os.path.join(OUT, "Lobo_%s_lento.mp4" % nome))
    # folha de poses: 6 quadros da lateral (para comparar silhueta/poses)
    print("VIDEO", nome, "quadros", total, "loop", loop, "vel", vel, flush=True)
print("VIDEOS_OK")
