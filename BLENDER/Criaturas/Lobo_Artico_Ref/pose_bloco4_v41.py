"""Lote de vida, bloco 4, etapa 1 (v41): POSES ESTATICAS Uivar e Sacudir (pico), para revisao antes de animar.
Lobo real: UIVAR = de pe (ou sentado), peito um pouco erguido, pescoco esticado para cima, focinho apontando ~50-60 graus acima do
horizonte, boca entreaberta em 'O', orelhas um pouco para tras, cauda neutra/baixa. SACUDIR = base aberta e um pouco agachada; a onda de
torcao corre da cabeca a cauda: cabeca gira forte para um lado, peito para o outro, quadril de volta, cauda balanca para o lado - aqui o
PICO da torcao (o clipe alterna os lados ~4-5x/s).
Mesmo construtor do bloco 3 (pose_bloco3_v40): parte do Repouso q0 da anim_v40; tronco (Quadril) baixa/gira; colunas podem rolar no
proprio eixo; patas por IK com alvo no chao (phi=phd=0 = pe do Repouso); pescoco, cabeca (inclinacao absoluta e rolo), boca, orelhas e
cauda. Mede o ponto mais baixo por regiao e renderiza vistas sobre grade.
Uso: blender -b anim_v40/CR_LoboArtico_Anim.blend -P pose_bloco4_v41.py -- <dir_saida> [poses] ; ajuste por env AJUSTE_V41"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
import marcha_v21 as M
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
POSES = a[1].split(",") if len(a) > 1 else ["uivar", "sacudir"]
PAR = {
 "uivar":   {"pitch_graus": -6.0, "desce_quadril": 0.0, "y_quadril": 0.0, "rolos": {}, "pata_D_x": 0.0, "pata_D_y": 0.0, "pata_T_x": 0.0, "pata_T_y": 0.0,
             "pescoco_graus": -38.0, "pescoco_divisao": [0.45, 0.55], "cabeca_graus": -55.0, "cabeca_rolo": 0.0, "boca_graus": 18.0,
             "orelhas_graus": -18.0, "cauda_lado": 0.0, "cauda_ergue": -8.0},
 "sacudir": {"pitch_graus": 2.0, "desce_quadril": 0.35, "y_quadril": 0.0, "rolos": {"Quadril": -10.0, "Coluna2": 14.0, "Coluna3": 16.0},
             "pata_D_x": 0.25, "pata_D_y": 0.0, "pata_T_x": 0.25, "pata_T_y": 0.0,
             "pescoco_graus": 6.0, "pescoco_divisao": [0.5, 0.5], "cabeca_graus": 10.0, "cabeca_rolo": -42.0, "boca_graus": 4.0,
             "orelhas_graus": -10.0, "cauda_lado": 35.0, "cauda_ergue": 10.0}}
if os.environ.get("AJUSTE_V41"):
    for k, v in json.loads(os.environ["AJUSTE_V41"]).items(): PAR[k].update(v)
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
def malha(o):
    dg = bpy.context.evaluated_depsgraph_get(); m = o.evaluated_get(dg).to_mesh(); r = [o.matrix_world @ v.co for v in m.vertices]; o.evaluated_get(dg).to_mesh_clear(); return r
repouso_q0(); CAB = bpy.data.objects["LOW_Cabeca"]; _vs = malha(CAB); I_NARIZ = min(range(len(_vs)), key=lambda i: _vs[i].y)
MCP_S = {k: P[c[2]].tail.copy() for k, c in M.PATAS.items()}
def eixo_osso(n): return (P[n].tail - P[n].head).normalized()
def ang_cabeca():
    yc = P["Cabeca"].matrix.col[1].xyz; return math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y)))
def montar(pz):
    repouso_q0()
    mover("Quadril", V((0, pz["y_quadril"], -pz["desce_quadril"]))); girar("Quadril", "X", pz["pitch_graus"])
    for n, g in pz["rolos"].items(): girar(n, -eixo_osso("Coluna1") if n == "Quadril" else eixo_osso(n), g)   # rolo no eixo do corpo
    err = 0.0
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        sg = 1 if k[1] == "E" else -1; fr = k[0]
        e, x = M.ik(k, MCP_S[k] + V((sg * pz["pata_%s_x" % fr], pz["pata_%s_y" % fr], 0)), 0.0, 0.0); err = max(err, e)
        for n in (sup, inf, pe, dedo): P[n].location = (0, 0, 0)
        bpy.context.view_layer.update()
    d1, d2 = pz["pescoco_divisao"]; girar("Pescoco1", "X", pz["pescoco_graus"] * d1); girar("Pescoco2", "X", pz["pescoco_graus"] * d2)
    girar("Cabeca", "X", pz["cabeca_graus"] - ang_cabeca())
    if pz["cabeca_rolo"]: girar("Cabeca", eixo_osso("Cabeca"), pz["cabeca_rolo"])
    if pz["boca_graus"]: girar("Mandibula", "X", pz["boca_graus"])
    if pz["orelhas_graus"]: girar("Orelha_E", "X", -pz["orelhas_graus"]); girar("Orelha_D", "X", -pz["orelhas_graus"])
    if pz["cauda_ergue"]: girar("Cauda1", "X", pz["cauda_ergue"])
    if pz["cauda_lado"]:
        for n, f in (("Cauda1", 0.4), ("Cauda2", 0.3), ("Cauda3", 0.3)): girar(n, "Z", pz["cauda_lado"] * f)
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
C0 = V((0, -0.8, 4.6))
VIS = {"perfil_E": (C0 + V((22, 0, 0.3)), ("o", 15.5)), "frente": (C0 + V((0, -22, 0.5)), ("o", 12.5)), "34_E": (C0 + V((11, -11, 6)), 34), "tras": (C0 + V((0, 22, 0.5)), ("o", 12.5))}
for ps in POSES:
    pz = PAR[ps]; err = montar(pz); nz = malha(CAB)[I_NARIZ]
    yc = P["Cabeca"].matrix.col[1].xyz
    R = {"pose": ps, "parametros": pz, "erro_ik": round(err, 5), "focinho": [round(x, 3) for x in nz], "cabeca_graus_horizonte": round(-ang_cabeca(), 1),
         "contatos_min_z": contatos(), "cernelha_z": round(P["Coluna3"].head.z, 3), "quadril_z": round(P["Quadril"].head.z, 3)}
    print("POSE", ps, json.dumps({k: v for k, v in R.items() if k != "parametros"}), flush=True)
    json.dump(R, open(os.path.join(OUT, "%s.json" % ps), "w"), indent=1)
    for v, (pos, l_) in VIS.items():
        cam.location = pos; cam.rotation_euler = (C0 - pos).to_track_quat("-Z", "Y").to_euler()
        if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
        else: cd.type = "PERSP"; cd.lens = l_
        sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (ps, v)); bpy.ops.render.render(write_still=True)
print("POSE_BLOCO4_V41_OK", flush=True)
