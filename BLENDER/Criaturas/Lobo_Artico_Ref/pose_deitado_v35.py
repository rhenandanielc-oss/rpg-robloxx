"""Lote de vida, bloco 1, etapa 1 (v35): POSE DEITADO (esfinge) do Lobo Artico, estatica, para revisao antes de animar Deitar/Levantar.
Licoes do Lobo Ancestral (DOCS/criaturas/lobo-ancestral.md 6o-6s): o usuario quer o lobo TOTALMENTE deitado - barriga no chao, sem
corcunda, cara encostada no chao; patas e jarretes nao podem atravessar o chao; antebracos deitados para a frente; metatarsos traseiros
deitados para a frente com os joelhos um pouco para fora; cauda no chao para o lado.
Monta a pose sobre o rig (37 ossos, sem mudar o rig): tronco (Quadril) desce e inclina, coluna achatada, pernas por IK analitico
(marcha_v21.ik) com pe e dedos rentes ao chao, pescoco/cabeca descem ate o queixo encostar, cauda deitada para o lado. Mede o ponto
mais baixo de cada regiao na malha deformada (LOW_Corpo + LOW_Cabeca; ossos dominantes) e renderiza 5 vistas sobre grade.
Parametros por env AJUSTE_V35 (JSON). Uso: blender -b anim_v34/CR_LoboArtico_Anim.blend -P pose_deitado_v35.py -- <dir_saida> [rotulo]"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
import marcha_v21 as M
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); ROT = a[1] if len(a) > 1 else "t1"; os.makedirs(OUT, exist_ok=True)
PAR = {"desce_quadril": 1.45, "desce_peito": 1.55, "y_corpo": 0.0, "coluna_achata": [0.0, 0.0, 0.0],
       "pata_D_y": -1.7, "pata_D_x": 0.0, "pata_D_z": 0.22, "pe_D_graus": None, "dedo_D_graus": None,
       "pata_T_y": -1.2, "pata_T_x": 0.25, "pata_T_z": 0.22, "pe_T_graus": None, "dedo_T_graus": None,
       "queixo_z": 0.06, "pescoco_divisao": [0.55, 0.45], "cabeca_alvo_graus": 12.0,
       "cauda": [30.0, 15.0, 10.0, 5.0], "cauda_lado": 35.0}
if os.environ.get("AJUSTE_V35"): PAR.update(json.loads(os.environ["AJUSTE_V35"]))
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
# 1) tronco: quadril desce, pitch para o peito descer mais (pivo no quadril)
qh = P["Quadril"].head.copy(); c3 = P["Coluna3"].head.copy(); Lc = qh.y - c3.y
pitch = math.degrees(math.atan2(PAR["desce_peito"] - PAR["desce_quadril"], Lc))
mover("Quadril", V((0, PAR["y_corpo"], -PAR["desce_quadril"]))); girar("Quadril", "X", pitch)
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
# 3) pescoco/cabeca ate o queixo encostar (bisseccao no angulo total)
def queixo(): return P["Mandibula"].tail.z
base = {n: P[n].matrix.copy() for n in ("Pescoco1", "Pescoco2", "Cabeca")}
def aplicar_pescoco(t):
    for n in ("Pescoco1", "Pescoco2", "Cabeca"): P[n].matrix = base[n]; bpy.context.view_layer.update()
    d1, d2 = PAR["pescoco_divisao"]; girar("Pescoco1", "X", t * d1); girar("Pescoco2", "X", t * d2)
    yc = P["Cabeca"].matrix.col[1].xyz; atual = math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y)))   # graus abaixo da horizontal
    girar("Cabeca", "X", PAR["cabeca_alvo_graus"] - atual)            # focinho quase nivelado (queixo apoiado), nao de testa
lo, hi = 0.0, PAR.get("pescoco_max", 150.0)
for _ in range(30):
    md = 0.5 * (lo + hi); aplicar_pescoco(md)
    if queixo() > PAR["queixo_z"]: lo = md
    else: hi = md
aplicar_pescoco(lo); ANG_PESC = lo
# 4) cauda deitada para o lado
for n, g in zip(("Cauda1", "Cauda2", "Cauda3", "Cauda4"), PAR["cauda"]):
    girar(n, "X", g)                                                  # + ergue o que aponta para tras
girar("Cauda1", "Z", PAR["cauda_lado"])
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
print("DEITADO", json.dumps(REL), flush=True)
json.dump(REL, open(os.path.join(OUT, "deitado_%s.json" % ROT), "w"), indent=1)
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
C0 = V((0, -0.8, 1.6))
VIS = {"perfil_E": (C0 + V((22, 0, 0.3)), ("o", 13.0)), "perfil_D": (C0 + V((-22, 0, 0.3)), ("o", 13.0)), "frente": (C0 + V((0, -22, 0.5)), ("o", 8.5)),
       "tras": (C0 + V((0, 22, 0.5)), ("o", 8.5)), "34_E": (C0 + V((11, -11, 6)), 34), "baixo_E": (C0 + V((12, -3, -0.9)), 30)}
for v, (pos, l_) in VIS.items():
    cam.location = pos; cam.rotation_euler = (C0 - pos).to_track_quat("-Z", "Y").to_euler()
    if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
    else: cd.type = "PERSP"; cd.lens = l_
    sc.render.filepath = os.path.join(OUT, "deitado_%s_%s.png" % (ROT, v)); bpy.ops.render.render(write_still=True)
print("POSE_DEITADO_V35_OK", flush=True)
