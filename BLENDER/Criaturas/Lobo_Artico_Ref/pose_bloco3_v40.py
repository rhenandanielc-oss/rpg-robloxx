"""Lote de vida, bloco 3, etapa 1 (v40): POSES ESTATICAS Farejar, Comer e Beber, para revisao antes de animar.
Lobo real: farejar = focinho rente ao chao, pescoco baixo, de pe e com as patas no lugar; comer = cabeca no chao sobre o alimento, boca
aberta, frente um pouco mais baixa e dianteiras um pouco abertas; beber = de pe na beira da agua, dianteiras um pouco abertas e a frente,
cotovelos dobrando, pescoco estendido para baixo e a frente, focinho na superficie (lambendo), boca entreaberta.
Parte do Repouso q0 da anim_v39 (postura aprovada). Tronco gira em X com a FRENTE descendo (pivo no quadril) e o quadril baixa um pouco;
patas por IK (marcha_v21.ik) com alvo no chao (pe/dedo do Repouso: phi=0, phd=0 reproduz o Repouso); pescoco (Pescoco1/2) desce por
bisseccao ate o PONTO DO FOCINHO (vertice mais a frente da LOW_Cabeca no Repouso) ficar na altura pedida; cabeca com inclinacao absoluta.
Mede o ponto mais baixo por regiao na malha deformada e renderiza vistas sobre grade.
Uso: blender -b anim_v39/CR_LoboArtico_Anim.blend -P pose_bloco3_v40.py -- <dir_saida> [poses] ; ajuste por env AJUSTE_V40 (JSON {pose: {...}})"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
import marcha_v21 as M
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
POSES = a[1].split(",") if len(a) > 1 else ["farejar", "comer", "beber"]
PAR = {
 "farejar": {"pitch_graus": 7.0, "desce_quadril": 0.10, "y_quadril": 0.0, "focinho_z": 0.35, "cabeca_graus": 62.0, "pescoco_divisao": [0.6, 0.4],
             "boca_graus": 0.0, "pata_D_x": 0.0, "pata_D_y": 0.0, "pata_T_x": 0.0, "pata_T_y": 0.0, "orelhas_graus": 12.0},
 "comer":   {"pitch_graus": 11.0, "desce_quadril": 0.25, "y_quadril": 0.0, "focinho_z": 0.15, "cabeca_graus": 78.0, "pescoco_divisao": [0.6, 0.4],
             "boca_graus": 16.0, "pata_D_x": 0.25, "pata_D_y": -0.35, "pata_T_x": 0.0, "pata_T_y": 0.0, "orelhas_graus": -6.0},
 "beber":   {"pitch_graus": 13.0, "desce_quadril": 0.30, "y_quadril": 0.15, "focinho_z": 0.08, "cabeca_graus": 50.0, "pescoco_divisao": [0.6, 0.4],
             "boca_graus": 8.0, "pata_D_x": 0.35, "pata_D_y": -0.45, "pata_T_x": 0.0, "pata_T_y": 0.0, "orelhas_graus": 0.0}}
if os.environ.get("AJUSTE_V40"):
    for k, v in json.loads(os.environ["AJUSTE_V40"]).items(): PAR[k].update(v)
ARM = M.ARM; P = M.P; sc = bpy.context.scene
for pb in P: pb.rotation_mode = "QUATERNION"
def girar(osso, eixo, graus, piv=None):
    pb = P[osso]; h = (pb.head if piv is None else piv).copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix; bpy.context.view_layer.update()
def mover(osso, d):
    pb = P[osso]; m = pb.matrix.copy(); m.translation = m.translation + d; pb.matrix = m; bpy.context.view_layer.update()
def repouso_q0():
    ac = bpy.data.actions["Repouso"]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(0); bpy.context.view_layer.update(); ARM.animation_data.action = None
CAB = bpy.data.objects["LOW_Cabeca"]
repouso_q0()
def malha(o):
    dg = bpy.context.evaluated_depsgraph_get(); m = o.evaluated_get(dg).to_mesh(); r = [o.matrix_world @ v.co for v in m.vertices]; o.evaluated_get(dg).to_mesh_clear(); return r
_vs = malha(CAB); I_NARIZ = min(range(len(_vs)), key=lambda i: _vs[i].y)
MCP_S = {k: P[c[2]].tail.copy() for k, c in M.PATAS.items()}
def ang_cabeca():
    yc = P["Cabeca"].matrix.col[1].xyz; return math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y)))
def montar(pz, a_pesc):
    repouso_q0()
    mover("Quadril", V((0, pz["y_quadril"], -pz["desce_quadril"]))); girar("Quadril", "X", pz["pitch_graus"])
    err = 0.0
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        sg = 1 if k[1] == "E" else -1; fr = k[0]
        alvo = MCP_S[k] + V((sg * pz["pata_%s_x" % fr], pz["pata_%s_y" % fr], 0))
        e, x = M.ik(k, alvo, 0.0, 0.0); err = max(err, e)
        for n in (sup, inf, pe, dedo): P[n].location = (0, 0, 0)
        bpy.context.view_layer.update()
    d1, d2 = pz["pescoco_divisao"]; girar("Pescoco1", "X", a_pesc * d1); girar("Pescoco2", "X", a_pesc * d2)
    girar("Cabeca", "X", pz["cabeca_graus"] - ang_cabeca())
    if pz["boca_graus"]: girar("Mandibula", "X", pz["boca_graus"])
    if pz["orelhas_graus"]: girar("Orelha_E", "X", -pz["orelhas_graus"]); girar("Orelha_D", "X", -pz["orelhas_graus"])
    return err
GR = {"pelve/ventre": ("Quadril", "Coluna1"), "barriga": ("Coluna2",), "esterno/peito": ("Coluna3", "Escapula_E", "Escapula_D", "Pescoco1"),
      "cotovelo+antebraco": ("Umero_E", "Umero_D", "Antebraco_E", "Antebraco_D"), "patas_D": ("Metacarpo_E", "Metacarpo_D", "Dedos_E", "Dedos_D"),
      "jarrete+canela": ("Tibia_E", "Tibia_D", "Metatarso_E", "Metatarso_D"), "patas_T": ("DedosPe_E", "DedosPe_D"),
      "queixo/cabeca": ("Cabeca", "Mandibula", "Pescoco2"), "cauda": ("Cauda1", "Cauda2", "Cauda3", "Cauda4")}
def contatos():
    C = {}
    for on in ("LOW_Corpo", "LOW_Cabeca"):
        o = bpy.data.objects[on]; gn = {g.index: g.name for g in o.vertex_groups}; vs = malha(o)
        for v, w in zip(o.data.vertices, vs):
            if not v.groups: continue
            nm = gn.get(max(v.groups, key=lambda g: g.weight).group)
            for reg, ossos in GR.items():
                if nm in ossos: C[reg] = min(C.get(reg, 9), w.z)
    return {k: round(v, 3) for k, v in C.items()}
# cenario de render
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
C0 = V((0, -1.2, 2.6))
VIS = {"perfil_E": (C0 + V((22, 0, 0.3)), ("o", 13.5)), "frente": (C0 + V((0, -22, 0.5)), ("o", 9.0)), "34_E": (C0 + V((11, -11, 6)), 34), "baixo_E": (C0 + V((12, -5, -0.9)), 30)}
TODOS = {}
for ps in POSES:
    pz = PAR[ps]; lo, hi = 0.0, 110.0
    for _ in range(18):
        md = 0.5 * (lo + hi); montar(pz, md); z = malha(CAB)[I_NARIZ].z
        if z > pz["focinho_z"]: lo = md
        else: hi = md
    err = montar(pz, hi); nz = malha(CAB)[I_NARIZ]
    R = {"pose": ps, "parametros": pz, "pescoco_graus": round(hi, 1), "erro_ik": round(err, 5), "focinho": [round(x, 3) for x in nz],
         "contatos_min_z": contatos(), "cernelha_z": round(P["Coluna3"].head.z, 3), "quadril_z": round(P["Quadril"].head.z, 3),
         "rot_local": {pb.name: [round(x, 6) for x in pb.rotation_quaternion] for pb in P}, "loc_quadril": [round(x, 6) for x in P["Quadril"].location]}
    TODOS[ps] = R; print("POSE", ps, json.dumps({k: v for k, v in R.items() if k not in ("rot_local", "parametros")}), flush=True)
    json.dump(R, open(os.path.join(OUT, "%s.json" % ps), "w"), indent=1)
    for v, (pos, l_) in VIS.items():
        cam.location = pos; cam.rotation_euler = (C0 - pos).to_track_quat("-Z", "Y").to_euler()
        if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
        else: cd.type = "PERSP"; cd.lens = l_
        sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (ps, v)); bpy.ops.render.render(write_still=True)
print("POSE_BLOCO3_V40_OK", flush=True)
