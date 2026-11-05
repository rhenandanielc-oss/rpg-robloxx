"""E4b: videos curtos de demonstracao de deformacao (NAO sao os clipes finais), com chao visivel, vista lateral e 3/4:
passo_dianteiro, passo_traseiro, pescoco, cauda, juba (cabeca virando + corrida simulada no tronco + parada) e boca.
Secundarios da juba/tufo: mola amortecida simples (atraso e retorno) calculada aqui e gravada em chaves; sem fisica.
Mede por quadro: altura minima e escorregamento das patas apoiadas (as que o clipe nao mexe).
Uso: blender -b Leao_Solar_Ref_E4b.blend -P e4b_05_videos.py -- <saida_dir> [clipes separados por virgula] [res=480]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Euler, Matrix
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
SO = A[1].split(",") if len(A) > 1 and A[1] else None; RES = int(A[2]) if len(A) > 2 else 480
sc = bpy.context.scene; FPS = 24; sc.render.fps = FPS
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
for pb in arm.pose.bones: pb.rotation_mode = "XYZ"
# chao, luz, camera
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0)); chao = bpy.context.active_object; chao.name = "_chao"
mc = bpy.data.materials.new("_chao"); mc.use_nodes = True; bs = mc.node_tree.nodes["Principled BSDF"]; bs.inputs["Base Color"].default_value = (0.42, 0.40, 0.36, 1); bs.inputs["Roughness"].default_value = 0.9
chao.data.materials.append(mc)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.4; sol.angle = math.radians(30)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(40), 0, math.radians(25))
sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = False; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
def camera(alvo, az, el, dist):
    alvo = Vector(alvo)
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
def suave(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def onda(t, a, b):                                            # 0 -> 1 -> 0 entre a e b
    if t <= a or t >= b: return 0.0
    u = (t - a) / (b - a); return math.sin(math.pi * u) ** 2
def sinal_flex(filho, eixo=0):
    """sinal do eixo X local que dobra a junta (aumenta o desvio entre pai e filho)"""
    pb = arm.pose.bones[filho]; pai = pb.parent
    def ang():
        bpy.context.view_layer.update()
        a0 = arm.matrix_world @ pai.head; a1 = arm.matrix_world @ pai.tail; b0 = arm.matrix_world @ pb.head; b1 = arm.matrix_world @ pb.tail
        return (a1 - a0).normalized().angle((b1 - b0).normalized())
    pb.rotation_euler = (0.3, 0, 0); a = ang(); pb.rotation_euler = (-0.3, 0, 0); b = ang(); pb.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
    return 1 if a > b else -1
def sinal_avanco(nome, direcao):
    pb = arm.pose.bones[nome]; r = []
    for s_ in (1, -1):
        pb.rotation_euler = (0.3 * s_, 0, 0); bpy.context.view_layer.update(); r.append((Vector(arm.matrix_world @ pb.tail).dot(Vector(direcao)), s_))
    pb.rotation_euler = (0, 0, 0); bpy.context.view_layer.update(); return max(r)[1]
SG = {}
for p in ("DD", "DE"):
    SG["Antebraco_" + p] = sinal_flex("Antebraco_" + p); SG["Mao_" + p] = sinal_flex("Mao_" + p); SG["Umero_" + p] = sinal_avanco("Umero_" + p, (0, -1, 0))
for p in ("TD", "TE"):
    SG["Canela_" + p] = sinal_flex("Canela_" + p); SG["Metatarso_" + p] = sinal_flex("Metatarso_" + p); SG["Coxa_" + p] = sinal_avanco("Coxa_" + p, (0, -1, 0))
def mandibula_sinal():
    pb = arm.pose.bones["Mandibula"]; pb.rotation_euler = (0.3, 0, 0); bpy.context.view_layer.update(); z = (arm.matrix_world @ pb.tail).z
    pb.rotation_euler = (0, 0, 0); bpy.context.view_layer.update(); return 1 if z < (arm.matrix_world @ pb.tail).z else -1
SG["Mandibula"] = mandibula_sinal()
R = math.radians
# ---------------------------------------------------------------- clipes: funcao(t) -> {osso: (rx, ry, rz)} em graus (rx usa o sinal certo)
def c_passo_d(t):
    u = onda(t, 0.3, 1.9)
    return {"Escapula_DD": (-8 * u * SG["Umero_DD"], 0, 0), "Umero_DD": (SG["Umero_DD"] * 22 * onda(t, 0.6, 1.9) - SG["Umero_DD"] * 8 * onda(t, 0.3, 0.9), 0, 0),
            "Antebraco_DD": (SG["Antebraco_DD"] * 75 * onda(t, 0.3, 1.6), 0, 0), "Mao_DD": (SG["Mao_DD"] * 60 * onda(t, 0.25, 1.4), 0, 0)}
def c_passo_t(t):
    return {"Coxa_TD": (SG["Coxa_TD"] * 20 * onda(t, 0.5, 1.9) - SG["Coxa_TD"] * 6 * onda(t, 0.3, 0.8), 0, 0), "Canela_TD": (SG["Canela_TD"] * 55 * onda(t, 0.3, 1.7), 0, 0),
            "Metatarso_TD": (SG["Metatarso_TD"] * 55 * onda(t, 0.3, 1.6), 0, 0)}
def c_pescoco(t):
    a = onda(t, 0.2, 1.4); b = onda(t, 1.2, 2.6)
    return {"Pescoco1": (-18 * a + 6 * b, 0, 20 * b), "Pescoco2": (-14 * a + 4 * b, 0, 16 * b), "Cabeca": (-8 * a, 0, 10 * b)}
def c_cauda(t):
    s_ = math.sin(2 * math.pi * 0.8 * t) * suave(t / 0.4) * suave((2.8 - t) / 0.4); up = onda(t, 0.2, 2.6)
    return {"Cauda%d" % i: (10 * up, 0, 14 * s_ * (0.6 + 0.15 * i)) for i in range(1, 7)}
def c_juba(t):
    vira = math.sin(2 * math.pi * 0.9 * t) * onda(t, 0.0, 1.3) * 1.0
    corre = suave((t - 1.3) / 0.2) * suave((2.7 - t) / 0.15); fase = math.sin(2 * math.pi * 2.3 * (t - 1.3))
    return {"Pescoco1": (5 * corre * fase, 0, 18 * vira), "Pescoco2": (4 * corre * fase, 0, 14 * vira), "Cabeca": (-3 * corre * fase, 0, 8 * vira),
            "Pescoco1_extra": 0}                                    # tronco parado: so pescoco/cabeca balancam (patas apoiadas nao mexem)
def c_boca(t):
    g = 32 * (suave((t - 0.3) / 0.8) - suave((t - 1.6) / 0.8))
    return {"Mandibula": (SG["Mandibula"] * g, 0, 0), "Lingua2": (-SG["Mandibula"] * 0.15 * g, 0, 0)}
CLIPES = {"passo_dianteiro": (c_passo_d, 2.2, ["DE", "TD", "TE"], ((1.5, -8.5, 4.5), (-90, -40), 26)),
          "passo_traseiro": (c_passo_t, 2.2, ["DD", "DE", "TE"], ((1.8, 5.0, 4.0), (-90, -40), 24)),
          "pescoco": (c_pescoco, 2.8, ["DD", "DE", "TD", "TE"], ((0, -9.5, 11), (-90, -40), 30)),
          "cauda": (c_cauda, 3.0, ["DD", "DE", "TD", "TE"], ((0.8, 11.0, 6.0), (-90, -40), 26)),
          "juba": (c_juba, 4.0, ["DD", "DE", "TD", "TE"], ((0, -9.5, 11), (-90, -40), 30)),
          "boca": (c_boca, 2.8, ["DD", "DE", "TD", "TE"], ((-0.2, -14.0, 12.6), (-90, -40), 10))}
SEC = [b.name for b in arm.pose.bones if b.name.startswith(("Juba_", "Tufo"))]
# patas apoiadas: vertices com peso dominante nos dedos/patas
W = {g.name: g.index for g in ob.vertex_groups}
def verts_pata(p):
    nomes = ["Dedos_" + p, "Mao_" + p if p.startswith("D") else "Metatarso_" + p]; ids = []
    for v in ob.data.vertices:
        for g in v.groups:
            if ob.vertex_groups[g.group].name in nomes and g.weight > 0.5 and v.co.z < 0.6: ids.append(v.index); break
    return ids
PATAS = {p: verts_pata(p) for p in ("DD", "DE", "TD", "TE")}
def posado():
    dg = bpy.context.evaluated_depsgraph_get(); m = ob.evaluated_get(dg).to_mesh(); p = np.array([v.co for v in m.vertices]); ob.evaluated_get(dg).to_mesh_clear(); return p
def matriz_mundo(nome): return arm.matrix_world @ arm.pose.bones[nome].matrix
rel = {}
for nome, (fn, dur, apoiadas, (alvo, azs, dist)) in CLIPES.items():
    if SO and nome not in SO: continue
    nq = int(round(dur * FPS)); sc.frame_start, sc.frame_end = 1, nq
    if arm.animation_data: arm.animation_data_clear()
    # 1) chaves dos ossos principais
    for f in range(1, nq + 1):
        t = (f - 1) / FPS; r = fn(t)
        for pb in arm.pose.bones:
            if pb.name in SEC: continue
            e = r.get(pb.name, (0, 0, 0))
            if not isinstance(e, tuple): e = (0, 0, 0)
            pb.rotation_euler = (R(e[0]), R(e[1]), R(e[2])); pb.keyframe_insert("rotation_euler", frame=f)
    # 2) secundarios: mola sobre a velocidade angular do pai (juba -> Pescoco1; tufo -> Cauda4..6)
    estado = {b: np.zeros(4) for b in SEC}                   # (ax, az, vx, vz)
    ant = {}
    K, DAMP = (2 * math.pi * 1.6) ** 2, 2 * 0.35 * (2 * math.pi * 1.6); dt = 1 / FPS
    for f in range(1, nq + 1):
        sc.frame_set(f)
        for b in SEC:
            pb = arm.pose.bones[b]; pai = "Pescoco1" if b.startswith("Juba") else ("Cauda5" if b == "Tufo1" else "Cauda6")
            Mw = matriz_mundo(pai); q = Mw.to_quaternion()
            if b in ant:
                dq = ant[b].inverted() @ q; eixo, ang = dq.to_axis_angle(); omega = Vector(eixo) * ang / dt   # no referencial do pai
            else: omega = Vector((0, 0, 0))
            ant[b] = q
            st = estado[b]; alvo_x = -0.06 * omega.x; alvo_z = -0.06 * omega.z
            acc = np.array([K * (alvo_x - st[0]) - DAMP * st[2], K * (alvo_z - st[1]) - DAMP * st[3]])
            st[2:] += acc * dt; st[:2] += st[2:] * dt; st[:2] = np.clip(st[:2], -0.35, 0.35)
            ganho = 1.0 if b.endswith("_1") or b == "Tufo1" else 1.5
            base = arm.pose.bones["Cauda5" if b == "Tufo1" else "Cauda6"].rotation_euler if b.startswith("Tufo") else Euler((0, 0, 0))
            pb.rotation_euler = (base.x + st[0] * ganho, base.y, base.z + st[1] * ganho); pb.keyframe_insert("rotation_euler", frame=f)
    # 3) medicao das patas apoiadas
    sc.frame_set(1); P0 = posado(); mede = {p: {"altura_min": 9.0, "altura_max_min": -9.0, "escorrega_max": 0.0} for p in apoiadas}
    for f in range(1, nq + 1, 2):
        sc.frame_set(f); P = posado()
        for p in apoiadas:
            ids = PATAS[p]
            if not ids: continue
            z = P[ids, 2]; d = np.linalg.norm(P[ids, :2] - P0[ids, :2], axis=1)
            mede[p]["altura_min"] = round(min(mede[p]["altura_min"], float(z.min())), 3)
            mede[p]["altura_max_min"] = round(max(mede[p]["altura_max_min"], float(z.min())), 3); mede[p]["escorrega_max"] = round(max(mede[p]["escorrega_max"], float(d.max())), 3)
    rel[nome] = {"quadros": nq, "fps": FPS, "patas_apoiadas": mede}; print("CLIPE", nome, json.dumps(rel[nome]), flush=True)
    # 4) videos
    im = sc.render.image_settings
    try: im.media_type = "VIDEO"
    except Exception: pass
    im.file_format = "FFMPEG"; sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"; sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.resolution_x, sc.render.resolution_y = int(RES * 1.33), RES
    for vista, az in zip(("lado", "34"), azs):
        camera(alvo, az, 8 if vista == "lado" else 14, dist)
        sc.render.filepath = os.path.join(OUT, "E4b_%s_%s.mp4" % (nome, vista)); bpy.ops.render.render(animation=True)
json.dump(rel, open(os.path.join(OUT, "contatos.json"), "w"), indent=1); print("VIDEOS_OK")
