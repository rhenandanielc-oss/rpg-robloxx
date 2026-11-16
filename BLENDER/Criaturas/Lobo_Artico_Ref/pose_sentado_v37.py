"""Lote de vida, bloco 2, etapa 1 (v37): POSE SENTADO (copia adaptada do pose_deitado_v35). Lobo real (etograma IWC: Sit = peso nos
quartos baixados, tronco ereto; Lobo Ancestral 6o: coluna ~44 graus, metatarsos traseiros deitados para a frente, joelhos um pouco para
fora, dianteiras retas sob o peito, cabeca nivelada, cauda no chao). Tronco gira (frente sobe) e o quadril desce ate a garupa encostar;
dianteiras retas por IK com o pe normal; traseiras com metatarso deitado para a frente; pescoco compensa para a cabeca ficar nivelada.
-------------------------------------------------------------------------------------------------------------------------------
v35: Lote de vida, bloco 1, etapa 1 (v35): POSE DEITADO (esfinge) do Lobo Artico, estatica, para revisao antes de animar Deitar/Levantar.
Licoes do Lobo Ancestral (DOCS/criaturas/lobo-ancestral.md 6o-6s): o usuario quer o lobo TOTALMENTE deitado - barriga no chao, sem
corcunda, cara encostada no chao; patas e jarretes nao podem atravessar o chao; antebracos deitados para a frente; metatarsos traseiros
deitados para a frente com os joelhos um pouco para fora; cauda no chao para o lado.
Monta a pose sobre o rig (37 ossos, sem mudar o rig): tronco (Quadril) desce e inclina, coluna achatada, pernas por IK analitico
(marcha_v21.ik) com pe e dedos rentes ao chao, pescoco/cabeca descem ate o queixo encostar, cauda deitada para o lado. Mede o ponto
mais baixo de cada regiao na malha deformada (LOW_Corpo + LOW_Cabeca; ossos dominantes) e renderiza 5 vistas sobre grade.
Parametros por env AJUSTE_V35 (JSON). Uso: blender -b anim_v36/CR_LoboArtico_Anim.blend -P pose_sentado_v37.py -- <dir_saida> [rotulo]"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
import marcha_v21 as M
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); ROT = a[1] if len(a) > 1 else "t1"; os.makedirs(OUT, exist_ok=True)
PAR = {"pitch_graus": 38.0, "desce_quadril": 2.9, "y_quadril": 0.0, "coluna_achata": [0.0, 0.0, 0.0],
       "pata_D_y": -0.3, "pata_D_x": 0.0, "pata_D_z": 0.30, "pe_D_graus": 0.0, "dedo_D_graus": 0.0,
       "pata_T_y": -1.3, "pata_T_x": 0.35, "pata_T_z": 0.45, "pe_T_graus": None, "dedo_T_graus": None,
       "pescoco_graus": 22.0, "pescoco_divisao": [0.55, 0.45], "cabeca_alvo_graus": 8.0,
       "cauda": [80.0, 20.0, 10.0, 0.0], "cauda_lado": 55.0}
if os.environ.get("AJUSTE_V37"): PAR.update(json.loads(os.environ["AJUSTE_V37"]))
ARM = M.ARM; P = M.P; B = M.B; sc = bpy.context.scene
ARM.animation_data.action = None
for pb in P: pb.rotation_mode = "QUATERNION"; pb.matrix_basis.identity()
bpy.context.view_layer.update()
def girar(osso, eixo, graus, piv=None):
    pb = P[osso]; h = (pb.head if piv is None else piv).copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix; bpy.context.view_layer.update()
def mover(osso, d):
    pb = P[osso]; m = pb.matrix.copy(); m.translation = m.translation + d; pb.matrix = m; bpy.context.view_layer.update()
def plano_graus(vec):                                                 # giro em X que deixa o vetor horizontal para a frente
    return -math.degrees(math.atan2(-vec.z, -vec.y))
# 1) tronco: o quadril desce e o tronco gira em X com a FRENTE subindo (pivo no quadril)
mover("Quadril", V((0, PAR["y_quadril"], -PAR["desce_quadril"]))); girar("Quadril", "X", -PAR["pitch_graus"]); pitch = -PAR["pitch_graus"]
for nm, g in zip(("Coluna1", "Coluna2", "Coluna3"), PAR["coluna_achata"]):
    if g: girar(nm, "X", g)
# 2) pernas por IK, pe e dedos rentes
RES = {}
for k, (sup, inf, pe, dedo) in M.PATAS.items():
    fr = k[0] == "D"; sg = 1 if k[1] == "E" else -1
    vpe = M.MCP0[k] - M.CAR0[k]; vdd = M.TIP0[k] - M.MCP0[k]
    phi = PAR["pe_%s_graus" % k[0]]; phd = PAR["dedo_%s_graus" % k[0]]
    phi = plano_graus(vpe) if phi is None else phi; phd = plano_graus(vdd) if phd is None else phd   # (marcha_v21.ik: dedos com giro ABSOLUTO)
    ombro = P[sup].head
    alvo = V((M.MCP0[k].x + sg * PAR["pata_%s_x" % k[0]], ombro.y + PAR["pata_%s_y" % k[0]], PAR["pata_%s_z" % k[0]]))
    e, x = M.ik(k, alvo, math.radians(phi), math.radians(phd)); RES[k] = {"erro_ik": round(e, 4), "ext": round(x, 3), "phi": round(phi, 1), "phd": round(phd, 1)}
    for n in (sup, inf, pe, dedo): P[n].location = (0, 0, 0)
    bpy.context.view_layer.update()
# 3) pescoco desce (compensa o tronco erguido) e a cabeca fica quase nivelada
d1, d2 = PAR["pescoco_divisao"]; girar("Pescoco1", "X", PAR["pescoco_graus"] * d1); girar("Pescoco2", "X", PAR["pescoco_graus"] * d2)
yc = P["Cabeca"].matrix.col[1].xyz; atual = math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y))); girar("Cabeca", "X", PAR["cabeca_alvo_graus"] - atual)
ANG_PESC = PAR["pescoco_graus"]
# 4) cauda DEITADA NO CHAO atras do lobo (pedido 11/11: "deite a sua cauda atras dele, ela esta levantada"): cada osso e apontado -
#    Cauda1 desce da base ate a altura 'cauda_z' no chao, Cauda2..4 seguem rentes ao chao para tras, com uma curva leve para o lado
def apontar(osso, d):
    pb = P[osso]; y = pb.matrix.col[1].xyz.normalized(); d = d.normalized(); ax = y.cross(d)
    if ax.length > 1e-8: girar(osso, ax.normalized(), math.degrees(math.acos(max(-1.0, min(1.0, y.dot(d))))))
MODO = PAR.get("cauda_modo", "chao")
if MODO == "chao":
    cz = PAR.get("cauda_z", 0.28); curva = PAR.get("cauda_curva", [6.0, 10.0, 14.0])
    h = P["Cauda1"].head; L1 = P["Cauda1"].bone.length; dz = max(-L1 * 0.98, cz - h.z); hz = math.sqrt(max(L1 * L1 - dz * dz, 1e-6))
    lado = math.radians(PAR.get("cauda_lado_graus", 8.0)); apontar("Cauda1", V((math.sin(lado) * hz, math.cos(lado) * hz, dz)))
    rolo = PAR.get("cauda_rolo_graus", 90.0)                           # a cauda e larga de perfil: rolar deita a parte larga no chao
    if rolo: girar("Cauda1", P["Cauda1"].matrix.col[1].xyz.normalized(), rolo)
    ang = lado
    for n, cv in zip(("Cauda2", "Cauda3", "Cauda4"), curva):
        ang += math.radians(cv); apontar(n, V((math.sin(ang), math.cos(ang), (cz - P[n].head.z) * 0.6)))
else:
    # variantes "em pe, na direcao do corpo, levemente curvada" (11/11): direcao base no plano do corpo + curva por osso (graus, no plano)
    eixo = (P["Quadril"].head - P["Coluna3"].head).normalized()       # linha do corpo, apontando para tras/baixo
    if MODO == "corpo_baixo":   base = eixo                                # continua a linha do corpo para tras
    elif MODO == "corpo_alto":  base = -eixo                               # erguida, ao longo das costas
    else:                       base = V((0.35, -0.2, -1.0)).normalized()  # 'lado': desce junto ao corpo e curva para a frente ao lado das traseiras
    curva = PAR.get("cauda_curva", [10.0, 12.0, 14.0]); sinal = PAR.get("cauda_curva_sinal", 1.0)
    apontar("Cauda1", base)
    ref = V((1, 0, 0)) if MODO != "lado" else V((0, 0, 1))
    d = base.copy()
    for n, cv in zip(("Cauda2", "Cauda3", "Cauda4"), curva):
        d = (Matrix.Rotation(math.radians(cv * sinal), 3, ref) @ d).normalized(); apontar(n, d)
# medicao de contatos na malha deformada
GR = {"pelve/ventre": ("Quadril", "Coluna1"), "barriga": ("Coluna2",), "esterno/peito": ("Coluna3", "Escapula_E", "Escapula_D", "Pescoco1"),
      "cotovelo+antebraco": ("Umero_E", "Umero_D", "Antebraco_E", "Antebraco_D"), "patas_D": ("Metacarpo_E", "Metacarpo_D", "Dedos_E", "Dedos_D"),
      "coxa": ("Coxa_E", "Coxa_D"), "jarrete+canela": ("Tibia_E", "Tibia_D", "Metatarso_E", "Metatarso_D"), "patas_T": ("DedosPe_E", "DedosPe_D"),
      "queixo/cabeca": ("Cabeca", "Mandibula", "Pescoco2"), "cauda": ("Cauda1", "Cauda2", "Cauda3", "Cauda4")}
CONT = {}
for on in ("LOW_Corpo", "LOW_Cabeca"):
    o = bpy.data.objects[on]; gn = {g.index: g.name for g in o.vertex_groups}; dg = bpy.context.evaluated_depsgraph_get(); m = o.evaluated_get(dg).to_mesh()
    for v, vb in zip(o.data.vertices, m.vertices):
        if not v.groups: continue
        dom = max(v.groups, key=lambda g: g.weight); nm = gn.get(dom.group)
        for reg, ossos in GR.items():
            if nm in ossos:
                z = (o.matrix_world @ vb.co).z; CONT[reg] = min(CONT.get(reg, 9), z)
    o.evaluated_get(dg).to_mesh_clear()
CONT = {k: round(v, 3) for k, v in CONT.items()}
REL = {"rotulo": ROT, "parametros": PAR, "pitch_tronco_graus": round(pitch, 2), "pescoco_graus": round(ANG_PESC, 1), "pernas": RES, "contatos_min_z": CONT,
       "quadril_z": round(P["Quadril"].head.z, 3), "cernelha_z": round(P["Coluna3"].head.z, 3)}
print("CAUDA", [(n, tuple(round(x, 2) for x in P[n].head), tuple(round(x, 2) for x in P[n].tail)) for n in ("Quadril", "Cauda1", "Cauda2", "Cauda3", "Cauda4")], flush=True)
print("SENTADO", json.dumps(REL), flush=True)
json.dump(REL, open(os.path.join(OUT, "sentado_%s.json" % ROT), "w"), indent=1)
# renders (workbench, grade)
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in ("LOW_Corpo", "LOW_Cabeca", "LOW_Marca", "LOW_Cristais", "LOW_Pelagem")
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=40, y_subdivisions=40, size=24, location=(0, 0, 0)); gr = bpy.context.object
gr.modifiers.new("w", "WIREFRAME").thickness = 0.02
bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, -0.005)); chao = bpy.context.object
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "OBJECT"; sh.show_shadows = True
sh.background_type = "VIEWPORT"; sh.background_color = (0.4, 0.42, 0.45)
for o in sc.objects:
    if o.type == "MESH": o.color = (0.55, 0.57, 0.6, 1) if o == chao else ((0.2, 0.21, 0.24, 1) if o == gr else (0.85, 0.86, 0.88, 1))
sc.render.resolution_x, sc.render.resolution_y = 640, 480
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
C0 = V((0, -0.8, 3.0))
VIS = {"perfil_E": (C0 + V((22, 0, 0.3)), ("o", 13.0)), "perfil_D": (C0 + V((-22, 0, 0.3)), ("o", 13.0)), "frente": (C0 + V((0, -22, 0.5)), ("o", 8.5)),
       "tras": (C0 + V((0, 22, 0.5)), ("o", 8.5)), "34_E": (C0 + V((11, -11, 6)), 34), "baixo_E": (C0 + V((12, -3, -0.9)), 30)}
for v, (pos, l_) in VIS.items():
    cam.location = pos; cam.rotation_euler = (C0 - pos).to_track_quat("-Z", "Y").to_euler()
    if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
    else: cd.type = "PERSP"; cd.lens = l_
    sc.render.filepath = os.path.join(OUT, "sentado_%s_%s.png" % (ROT, v)); bpy.ops.render.render(write_still=True)
print("POSE_SENTADO_V37_OK", flush=True)
