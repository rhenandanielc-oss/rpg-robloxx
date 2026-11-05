"""Cena de TESTE (so Blender) para avaliar entrada/saida da agua: margem plana, rampa, fundo e plano de agua (objetos
TESTE_*; nada do mapa do jogo). Poses = quadros dos JSON exportados aplicados no rig (crossfade de 6 quadros nas emendas,
quadros de entrada de clipes/emendas_transicoes.json). O que e do JOGO e reproduzido aqui e documentado:
 - em terra a raiz segue a rampa e inclina junto (alinhamento ao chao);
 - na entrada a raiz sai do fundo para a altura de boiar (nivel da agua - 4,3) enquanto as patas recolhem;
 - na saida a raiz desce da altura de boiar ate o fundo enquanto as patas estendem;
 - velocidade de nado de TESTE 2,5 studs/s (o Nado nao tem velocidade de sincronizacao).
Agua = representacao visual; NAO e teste de fisica/flutuacao do Roblox.
Mede: penetracao da malha no terreno e altura das solas apoiadas.
Uso: blender -b CR_Crocodilo_Rig.blend -P cena_agua.py -- <saida_dir> <entrada|saida> [passo] [cameras] [cavaleiro]
Lote 4: com "cavaleiro" (abrir CR_Crocodilo_Montaria_Teste.blend) o manequim R15 aproximado vai sentado, preso ao osso do
dorso, e mede altura do quadril/tronco/cabeca e dos pes sobre a agua de teste (so superficie; sem mergulho montado)."""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V, Matrix as M, Quaternion as Q
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); SEQ = A[1]; PASSO = int(A[2]) if len(A) > 2 else 2
CAMS = A[3].split(",") if len(A) > 3 else ["lado", "34"]
CAV = len(A) > 4 and A[4] == "cavaleiro"
os.makedirs(OUT, exist_ok=True)
BASE = os.path.dirname(bpy.data.filepath); CL = os.path.join(BASE, "clipes")
sc = bpy.context.scene; arm = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
    pb.rotation_mode = "QUATERNION"
for o in sc.objects:
    if o.type in ("EMPTY",): o.hide_render = True
arm.hide_render = True
if CAV:                                                          # Lote 4: manequim sentado preso ao osso do dorso
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import manequim_r15 as mq
    ra = bpy.data.objects[mq.NOME + "_Rig"]
    for pb in ra.pose.bones:
        for c in pb.constraints: c.mute = True
    ra.animation_data.action = bpy.data.actions["DEMO_Cav_Sentado"]; ra.animation_data.action_slot = bpy.data.actions["DEMO_Cav_Sentado"].slots[0]
    BL_A = arm.data.bones[mq.OSSO_ASSENTO].matrix_local
J = {n: json.load(open(os.path.join(CL, "Crocodilo_%s.json" % n))) for n in ("Andar", "EntradaAgua", "Nado", "SaidaAgua", "Repouso",
     "RepousoParaAndar", "AndarParaCorrida", "Corrida", "Frenagem")}
EM = json.load(open(os.path.join(CL, "emendas_transicoes.json")))
def pose(n, q):
    d = J[n]; q = q % d["quadros"] if d["loop"] else min(q, d["quadros"] - 1); out = {}
    for o, s in d["ossos"].items():
        x, y, z, w, tx, ty, tz = s[q * 7:q * 7 + 7]; out[o] = (Q((w, x, y, z)), V((tx, ty, tz)))
    return out
def mistura(pa, pb_, w):
    return {o: (pa[o][0].slerp(pb_[o][0], w), pa[o][1].lerp(pb_[o][1], w)) for o in pa}
def aplica(p):
    for o, (q, t) in p.items(): pb = arm.pose.bones[o]; pb.rotation_quaternion = q; pb.location = t
# ------------------------------------------------------------------ terreno e agua
ANG = math.radians(10.0); W_AGUA = -1.0; Z_BOIA = W_AGUA - 4.3; FUNDO = -9.0   # margem de 10 graus ate fundo plano
Y_MEIO = (arm.data.bones["Pelve"].head_local.y + arm.data.bones["Coluna2"].tail_local.y) / 2
if SEQ == "terra":
    def h(y): return 0.0
elif SEQ == "entrada":     # margem atras (+Y), desce para a frente (-Y)
    def h(y): return 0.0 if y >= 0 else max(FUNDO, y * math.tan(ANG))
else:                    # fundo plano atras (+Y), sobe para a frente (-Y) ate a margem
    Y_TOPO = -50.0
    def h(y): return 0.0 if y <= Y_TOPO else max(FUNDO, -(y - Y_TOPO) * math.tan(ANG))
def h_med(y): return (h(y - 4.0) + h(y + 4.0)) / 2
def inc(y): return math.atan2(h(y - 8.0) - h(y + 8.0), 16.0)         # >0: chao sobe para a frente (media sob o corpo todo)
ys = np.linspace(-110, 60, 681); xs = (-14, 14)
me = bpy.data.meshes.new("TESTE_Margem"); vs = [(x, y, h(y)) for y in ys for x in xs]
fs = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(ys) - 1)]
me.from_pydata(vs, [], fs); terr = bpy.data.objects.new("TESTE_Margem", me); sc.collection.objects.link(terr)
mt = bpy.data.materials.new("TESTE_M_Margem"); mt.use_nodes = True; nt = mt.node_tree; bt = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 1.0
tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], ck.inputs["Vector"])
ck.inputs["Color1"].default_value = (0.36, 0.30, 0.20, 1); ck.inputs["Color2"].default_value = (0.26, 0.21, 0.14, 1)
nt.links.new(ck.outputs["Color"], bt.inputs["Base Color"]); bt.inputs["Roughness"].default_value = 0.95; me.materials.append(mt)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, -10, W_AGUA)); agua = bpy.context.object; agua.name = "TESTE_Agua"
ma = bpy.data.materials.new("TESTE_M_Agua"); ma.use_nodes = True; ba = ma.node_tree.nodes["Principled BSDF"]
ba.inputs["Base Color"].default_value = (0.10, 0.20, 0.22, 1); ba.inputs["Alpha"].default_value = 0.5; ba.inputs["Roughness"].default_value = 0.08
if hasattr(ma, "surface_render_method"): ma.surface_render_method = "BLENDED"
agua.data.materials.append(ma)
# ------------------------------------------------------------------ roteiro: (clipe, quadro do clipe) por quadro de saida + raiz no mundo
def acha_y(alvo_z, y0, y1):
    """y em que h_med(y) = alvo_z (busca simples entre y0 e y1)"""
    melhor = min(np.linspace(y0, y1, 4001), key=lambda y: abs(h_med(y) - alvo_z)); return float(melhor)
roteiro = []   # (poses, y_c, z, pitch)
CF = 6
if SEQ == "terra":   # emendas em terra plana: Repouso -> RepousoParaAndar -> Andar -> AndarParaCorrida -> Corrida -> Frenagem -> Repouso
    yc = 0.0; ant = None
    SEG = [("Repouso", 0, 30, 0.0), ("RepousoParaAndar", 0, None, "desl"), ("Andar", EM["RepousoParaAndar"]["entrar_no_quadro"], 45, 1.85),
           ("AndarParaCorrida", 0, None, "desl"), ("Corrida", EM["AndarParaCorrida"]["entrar_no_quadro"], 32, 8.75),
           ("Frenagem", 0, None, "desl"), ("Repouso", EM["Frenagem"]["entrar_no_quadro"], 40, 0.0)]
    for nome, q0, n, vel in SEG:
        n = n or J[nome]["quadros"]; des = J[nome].get("sincronizacao", {}).get("deslocamento_studs")
        for i in range(n):
            if vel == "desl": dy = (des[i] - des[i - 1]) if i else 0.0
            else: dy = vel / 30
            yc -= dy; p = pose(nome, q0 + i)
            if ant is not None and i < CF: p = mistura(pose(ant[0], ant[1] + i), p, (i + 1) / (CF + 1))
            roteiro.append((p, yc, 0.0, 0.0))
        ant = (nome, q0 + n)
    agua.hide_render = True
elif SEQ == "entrada":
    n_and = 3 * J["Andar"]["quadros"]; n_ent = J["EntradaAgua"]["quadros"]; q_nado = EM["EntradaAgua"]["entrar_no_quadro"]
    y_s = acha_y(Z_BOIA - 0.4, -60, 0)                           # inicio da entrada: fundo 0,4 abaixo da altura de boiar
    y = y_s; caminho = []
    for i in range(n_and):                                        # integra para tras no tempo a partir de y_s (rampa acima)
        y += 1.85 / 30 * math.cos(inc(y)); caminho.append(y)
    caminho = caminho[::-1]
    for i in range(n_and):
        yc = caminho[i]; roteiro.append((pose("Andar", i), yc, h_med(yc), -inc(yc)))
    des = J["EntradaAgua"]["sincronizacao"]["deslocamento_studs"]; yc = y_s
    for i in range(n_ent):
        t = i / 30; b = min(1, max(0, (t - 1.0) / 0.8)); b = b * b * (3 - 2 * b)
        v_jogo = 1.85 * (1 - b) + 2.5 * b                           # pes no chao: passada do clipe; depois nado de teste 2,5
        if i: yc -= v_jogo / 30 * math.cos(inc(yc))
        z = h_med(yc) * (1 - b) + Z_BOIA * b; pit = -inc(yc)       # inclinacao acompanha o fundo (cauda livre da margem)
        p = pose("EntradaAgua", i)
        if i < CF: p = mistura(pose("Andar", n_and + i), p, (i + 1) / (CF + 1))
        roteiro.append((p, yc, z, pit))
    for i in range(3 * J["Nado"]["quadros"]):
        yc -= 2.5 / 30; p = pose("Nado", q_nado + i)
        if i < CF: p = mistura(pose("EntradaAgua", n_ent - 1), p, (i + 1) / (CF + 1))
        roteiro.append((p, yc, max(Z_BOIA, h_med(yc) + 0.4), -inc(yc)))
else:
    n_sai = J["SaidaAgua"]["quadros"]; q_ini_nado = EM["SaidaAgua"]["quadro_origem_mais_parecido"]; q_and = EM["SaidaAgua"]["entrar_no_quadro"]
    des = J["SaidaAgua"]["sincronizacao"]["deslocamento_studs"]
    y_toque = acha_y(Z_BOIA - 0.4, Y_TOPO, 40)                   # onde as patas alcancam o fundo
    n_nado = 2 * J["Nado"]["quadros"] + q_ini_nado
    yc = y_toque + 2.5 / 30 * n_nado
    for i in range(n_nado):
        yc -= 2.5 / 30; roteiro.append((pose("Nado", i), yc, max(Z_BOIA, h_med(yc) + 0.4), -inc(yc)))
    y_ini = yc
    for i in range(n_sai):
        t = i / 30; yc = y_ini - des[i] * math.cos(inc(yc)); b = min(1, max(0, (t - 0.3) / 0.8)); b = b * b * (3 - 2 * b)
        z = max(Z_BOIA, h_med(yc) + 0.4) * (1 - b) + h_med(yc) * b; pit = -inc(yc)
        p = pose("SaidaAgua", i)
        if i < CF: p = mistura(pose("Nado", n_nado + i), p, (i + 1) / (CF + 1))
        roteiro.append((p, yc, z, pit))
    y = roteiro[-1][1]
    for i in range(4 * J["Andar"]["quadros"]):
        y -= 1.85 / 30 * math.cos(inc(y)); p = pose("Andar", q_and + i)
        if i < CF: p = mistura(pose("SaidaAgua", n_sai - 1), p, (i + 1) / (CF + 1))
        roteiro.append((p, y, h_med(y), -inc(y)))
print("ROTEIRO", SEQ, "quadros", len(roteiro), "| agua z", W_AGUA, "| boiar raiz z", Z_BOIA)
# ------------------------------------------------------------------ medicoes + render
sola = {}
for k in ("MaoE", "MaoD", "PeE", "PeD"):
    g = lo.vertex_groups[k].index
    sola[k] = [v.index for v in lo.data.vertices if v.co.z < 0.35 and any(gg.group == g and gg.weight > 0.5 for gg in v.groups)]
w_ = bpy.data.worlds.new("N"); sc.world = w_; w_.use_nodes = True; w_.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.43, 1)
w_.node_tree.nodes["Background"].inputs[1].default_value = 1.3
cam = sc.camera; cd = cam.data; sc.render.resolution_x, sc.render.resolution_y = 640, 360; sc.eevee.taa_render_samples = 16
CM = V((0, Y_MEIO, 0)); dg = bpy.context.evaluated_depsgraph_get()
pen_max = (0, -1); sola_alt = []; log = []
for fi in range(0, len(roteiro), 1):
    p, yc, z, pit = roteiro[fi]
    aplica(p); arm.matrix_world = M.Translation(V((0, yc, z))) @ M.Rotation(pit, 4, "X") @ M.Translation(-CM)
    bpy.context.view_layer.update()
    if CAV:
        ra.matrix_world = arm.matrix_world @ arm.pose.bones[mq.OSSO_ASSENTO].matrix @ BL_A.inverted(); bpy.context.view_layer.update()
        cav = {k: round((ra.matrix_world @ ra.pose.bones[o].head).z - W_AGUA, 3) for k, o in (("quadril", "LowerTorso"), ("tronco_base", "UpperTorso"), ("pescoco", "Head"))}
        cav["pe_min"] = round(min((ra.matrix_world @ ra.pose.bones[o].tail).z for o in ("LeftFoot", "RightFoot")) - W_AGUA, 3)
    ev = lo.evaluated_get(dg); mm = ev.to_mesh(); co = np.empty(len(mm.vertices) * 3); mm.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    W4 = np.array(lo.matrix_world); cw = co @ W4[:3, :3].T + W4[:3, 3]
    hv = np.array([h(y) for y in cw[::7, 1]]); pen = float(np.max(hv - cw[::7, 2]))
    if pen > pen_max[0]: pen_max = (pen, fi)
    alt = {k: float(cw[sola[k], 2].min() - h(float(cw[sola[k], 1].mean()))) for k in sola}
    sola_alt.append(alt); ev.to_mesh_clear()
    log.append((fi, round(yc, 2), round(z, 2), round(math.degrees(pit), 1), round(pen, 3), {k: round(v, 2) for k, v in alt.items()}) + ((cav,) if CAV else ()))
    if fi % PASSO: continue
    for cn in CAMS:
        alvo = V((0, yc - 3, z + 2.0))
        if cn == "lado":                                            # camera sempre acima da agua (abaixo dela o plano some)
            pc = alvo + V((30, 0, 2.5)); pc.z = max(pc.z, W_AGUA + 1.5); cd.lens = 32
        else: pc = alvo + V((20, -20, 8)); cd.lens = 30
        cam.location = pc; cam.rotation_euler = (alvo - pc).to_track_quat("-Z", "Y").to_euler(); cd.type = "PERSP"
        sc.render.filepath = os.path.join(OUT, "%s_%s_%03d.png" % (SEQ, cn, fi // PASSO)); bpy.ops.render.render(write_still=True)
json.dump(log, open(os.path.join(OUT, "medidas_%s%s.json" % (SEQ, "_cavaleiro" if CAV else "")), "w"))
if CAV:
    for k in ("quadril", "tronco_base", "pescoco", "pe_min"):
        vs = [l[-1][k] for l in log]; print("CAVALEIRO_AGUA %s min %.2f max %.2f (studs sobre a agua de teste)" % (k, min(vs), max(vs)))
print("PENETRACAO malha x terreno max %.3f studs no quadro %d" % pen_max)
print("CENA_AGUA_OK")
