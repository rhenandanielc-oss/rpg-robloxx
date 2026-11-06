"""Lote 4: renders e medicoes do cavaleiro de teste (cena CR_Crocodilo_Montaria_Teste.blend, gerada por demo_montaria.py).
 - demo:   Montar / Desmontar (crocodilo no lugar, manequim pela acao DEMO_Cav_*)
 - seq:    Repouso -> Montar -> Repouso montado -> Desmontar -> Repouso (continuidade)
 - reuso:  clipes existentes com o manequim SENTADO preso ao osso do dorso (acao DEMO_Cav_Sentado), corpo movido como em
           render_clipes_v2.py (velocidade/giro de sincronizacao do clipe); agua de TESTE z 4,3 nos clipes de agua
Mede por quadro: folga das partes do manequim ate a pele e ate a sela (negativa = atravessa), deriva do quadril em
relacao ao osso do dorso, altura do tronco/cabeca sobre a agua. Agua = representacao visual, NAO e flutuacao do Roblox.
Uso: blender -b CR_Crocodilo_Montaria_Teste.blend -P render_montaria.py -- <saida_dir> <demo|seq|reuso> <clipes|-> <cameras> [passo] [ciclos] [sem_render]"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix as Mx
from mathutils.bvhtree import BVHTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manequim_r15 as mq
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
MODO = A[1]; CLIPES = A[2].split(","); CAMS_Q = A[3].split(","); PASSO = int(A[4]) if len(A) > 4 else 1
CICLOS = int(A[5]) if len(A) > 5 else 1; SEM_RENDER = len(A) > 6 and A[6] == "sem_render"
sc = bpy.context.scene; FPS = 30
croc = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]; cam = sc.camera; cd = cam.data
ra = bpy.data.objects[mq.NOME + "_Rig"]; sela = bpy.data.objects.get("CR_Croc_Sela") or bpy.data.objects["TESTE_Sela_PROPOSTA"]
for o in (croc, ra):
    for pb in o.pose.bones:
        for c in pb.constraints: c.mute = True
for o in sc.objects:
    if o.type in ("EMPTY", "ARMATURE"): o.hide_render = True
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, 0)); chao = bpy.context.object; chao.name = "Chao_Teste"
m = bpy.data.materials.new("M_Chao"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 300; ck.inputs["Color1"].default_value = (0.55, 0.55, 0.56, 1)
ck.inputs["Color2"].default_value = (0.36, 0.36, 0.38, 1); nt.links.new(ck.outputs["Color"], b.inputs["Base Color"]); chao.data.materials.append(m)
W_AGUA = 4.3; agua = None
AGUA = ("Nado", "NadoParado", "CurvaAquaticaEsquerda", "CurvaAquaticaDireita")
manif = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "clipes", "manifesto_clipes.json"), encoding="utf-8"))
def acao(obj, nome):
    act = bpy.data.actions[nome]; obj.animation_data.action = act; obj.animation_data.action_slot = act.slots[0]; return act
if not ra.animation_data: ra.animation_data_create()
bl = croc.data.bones[mq.OSSO_ASSENTO].matrix_local
def preso():
    """manequim sentado preso ao osso do dorso (o mesmo que um Attachment soldado ao osso)"""
    pb = croc.pose.bones[mq.OSSO_ASSENTO]; ra.matrix_world = croc.matrix_world @ pb.matrix @ bl.inverted()
amo = mq.amostras_partes(0.2)
# ------------------------------------------------------------------ roteiro: lista de (clipe croc, quadro, acao cav, quadro cav, deslocamento/giro)
rot = []
def junta(nome, q0, n, cav, qc0=None, mov=False):
    act = bpy.data.actions["Croc_" + nome]; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); nq = f1 - f0 + 1
    vel = manif[nome]["velocidade_studs_s"]
    sinc = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "clipes", "Crocodilo_%s.json" % nome))).get("sincronizacao", {})
    giro = math.radians(sinc.get("giro_graus_s", sinc.get("giro_graus_s_proposto", 0.0))) if mov else 0.0
    pivo_y = sinc.get("pivo_y", -4.0); dq_ = sinc.get("deslocamento_studs")
    for i in range(n):
        q = (q0 + i) % nq if act.get("loop") else min(q0 + i, nq - 1); t = i / FPS
        dq = (dq_[min(len(dq_) - 1, q)] if dq_ else vel * t) if mov else 0.0
        rot.append((nome, f0 + q, cav, None if qc0 is None else qc0 + i, dq, giro * t, pivo_y))
if MODO == "demo":
    for nome in CLIPES: junta(nome, 0, int(round(manif[nome]["duracao"] * FPS)) + 1, "DEMO_Cav_" + nome, 1)
elif MODO in ("seq", "seq_d"):                            # seq_d (Lote 5): o mesmo pelo lado direito
    d_ = "Direita" if MODO == "seq_d" else ""
    junta("Repouso", 0, 30, None); junta("Montar" + d_, 0, 121, "DEMO_Cav_Montar" + d_, 1); junta("Repouso", 0, 60, "DEMO_Cav_Sentado")
    junta("Desmontar" + d_, 0, 109, "DEMO_Cav_Desmontar" + d_, 1); junta("Repouso", 0, 30, None)
else:
    for nome in CLIPES:
        act = bpy.data.actions["Croc_" + nome]; nq = int(act.frame_range[1] - act.frame_range[0]) + 1
        junta(nome, 0, nq * CICLOS if act.get("loop") else nq, "DEMO_Cav_Sentado", None, mov=True)
# ------------------------------------------------------------------ medicao + render
sc.render.resolution_x, sc.render.resolution_y = 640, 360; sc.eevee.taa_render_samples = 16
CAMS = {"lado": (V((30, -3, 9.0)), V((0, -3, 4.0)), 36, None), "34": (V((24, -22, 11)), V((0, -4, 4.0)), 32, None),
        "frente": (V((0, -32, 11)), V((0, -4.6, 5.5)), 38, None), "topo": (V((0, -2, 46)), V((0, -1.99, 0)), 0, 38),
        "tras": (V((-10, 26, 13)), V((0, -4.6, 5.0)), 34, None), "close": (V((12, -11, 9.5)), V((0, -4.8, 6.0)), 34, None),
        "lado_agua": (V((30, -3, 6.5)), V((0, -3, 5.0)), 36, None),
        "subida": (V((17, -15, 5.5)), V((3.2, -5.6, 3.4)), 30, None), "flanco": (V((17, -2.5, 4.5)), V((3.0, -5.2, 3.2)), 30, None)}
for k_ in list(CAMS):                                        # Lote 5: as mesmas cameras pelo lado direito (x espelhado), sufixo _d
    p_, a_, l_, o_ = CAMS[k_]; CAMS[k_ + "_d"] = (V((-p_.x, p_.y, p_.z)), V((-a_.x, a_.y, a_.z)), l_, o_)
log = []; prev_cena = None; ult = {}
for i, (nome, f, cav, qc, dq, ang, pivo_y) in enumerate(rot):
    acao(croc, "Croc_" + nome); sc.frame_set(f)
    croc.matrix_world = Mx.Translation(V((0, -dq, 0)) + V((0, pivo_y, 0))) @ Mx.Rotation(ang, 4, "Z") @ Mx.Translation(V((0, -pivo_y, 0)))
    if nome in AGUA and agua is None:
        bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, W_AGUA)); agua = bpy.context.object; agua.name = "Agua_Teste"
        ma = bpy.data.materials.new("M_Agua"); ma.use_nodes = True; ba = ma.node_tree.nodes["Principled BSDF"]
        ba.inputs["Base Color"].default_value = (0.12, 0.22, 0.24, 1); ba.inputs["Alpha"].default_value = 0.45; ba.inputs["Roughness"].default_value = 0.1
        if hasattr(ma, "surface_render_method"): ma.surface_render_method = "BLENDED"
        agua.data.materials.append(ma)
    if agua: agua.hide_render = nome not in AGUA; agua.location = (0, -dq, W_AGUA)
    ra.hide_render = cav is None; ra.hide_viewport = cav is None
    if cav:                                                   # acoes DEMO usam o mesmo quadro da cena que o clipe do crocodilo
        acao(ra, cav); bpy.context.view_layer.update()
        if cav == "DEMO_Cav_Sentado": preso()
        else: ra.matrix_world = croc.matrix_world
    bpy.context.view_layer.update()
    reg = {"i": i, "clipe": nome, "q": f}
    if cav:
        bv = mq.bvh_croc(lo); reg["folga_croc"] = mq.folgas(ra, amo, bv, passo=2)
        bs = BVHTree.FromObject(sela, bpy.context.evaluated_depsgraph_get())
        reg["folga_sela"] = mq.folgas(ra, amo, bs, Minv=sela.matrix_world.inverted(), raio=3.0, passo=2)
        pel = ra.matrix_world @ ra.pose.bones["LowerTorso"].head
        pb = croc.pose.bones[mq.OSSO_ASSENTO]; Mb = croc.matrix_world @ pb.matrix @ bl.inverted()
        reg["quadril_no_osso"] = [round(c, 4) for c in Mb.inverted() @ pel]            # deriva = variacao disto
        reg["quadril"] = [round(c, 3) for c in pel]
        if nome in AGUA:
            tor = ra.matrix_world @ ra.pose.bones["UpperTorso"].head; cab = ra.matrix_world @ ra.pose.bones["Head"].head
            reg["agua"] = {"base_tronco_sobre_agua": round(tor.z - W_AGUA, 3), "pescoco_sobre_agua": round(cab.z - W_AGUA, 3),
                           "quadril_sobre_agua": round(pel.z - W_AGUA, 3),
                           "pe_min_sobre_agua": round(min((ra.matrix_world @ ra.pose.bones[k].tail).z for k in ("LeftFoot", "RightFoot")) - W_AGUA, 3)}
    log.append(reg)
    if SEM_RENDER or i % PASSO: continue
    for cn in CAMS_Q:
        p, a, lente, orto = CAMS[cn]; d = V((0, -dq, 0))
        cam.location = p + d; cam.rotation_euler = (a + d - cam.location).to_track_quat("-Z", "Y").to_euler()
        if cn == "topo": cam.rotation_euler = (0, 0, math.pi / 2)
        if orto: cd.type = "ORTHO"; cd.ortho_scale = orto
        else: cd.type = "PERSP"; cd.lens = lente
        tag = MODO if MODO != "demo" and MODO != "reuso" else nome
        sc.render.filepath = os.path.join(OUT, "%s_%s_%03d.png" % (tag if not MODO.startswith("seq") else {"seq": "Sequencia", "seq_d": "SequenciaDireita"}[MODO], cn, i // PASSO)); bpy.ops.render.render(write_still=True)
json.dump(log, open(os.path.join(OUT, "medidas_%s_%s.json" % (MODO, "_".join(CLIPES) if not MODO.startswith("seq") else MODO)), "w"))
print("RENDER_MONTARIA_OK", MODO, len(rot))
