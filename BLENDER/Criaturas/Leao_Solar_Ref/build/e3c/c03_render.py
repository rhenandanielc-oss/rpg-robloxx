"""E3b: renders da boca por pose e vista (luz neutra das pranchas) + medicoes de intersecao por pose.
Vistas: 34 (lado X+), 34e (lado X-), perfil, frente, baixo, interna. Poses em graus.
Medicoes por pose:
  pen_pele   vertices da mandibula (peso>0,5) que entram na pele da cabeca/juba (como na E3);
  dentes_sxi sobreposicao (pares de triangulos) entre dentes superiores e inferiores;
  sup_ass    dentes superiores x assoalho/labio inferior; inf_pal  dentes inferiores x palato/labio superior;
  lingua_pal lingua x palato e dentes superiores;  lingua_inf lingua x dentes inferiores;
  fora       (so fechada) vertices do interior/dentes/lingua fora da pele.
Uso: blender -b <e3b.blend> -P c03_render.py -- <saida_dir> <graus,...> <vistas,...> [res] [lingua_graus_por_grau]"""
import bpy, sys, os, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
GRAUS = [float(x) for x in A[1].split(",")]; VISTAS = A[2].split(","); RES = int(A[3]) if len(A) > 3 else 800
LG = float(A[4]) if len(A) > 4 else 0.0
sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("Neutro"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.2; sol.angle = math.radians(40)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
arm = bpy.data.objects["Leao_Rig_Teste_Boca"]; pb = arm.pose.bones["Mandibula"]; pb.rotation_mode = "XYZ"
pl = arm.pose.bones.get("Lingua")
if pl: pl.rotation_mode = "XYZ"
corpo = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]
def queixo_z(a):
    pb.rotation_euler = (math.radians(a), 0, 0); bpy.context.view_layer.update(); return (arm.matrix_world @ pb.tail).z
SINAL = 1 if queixo_z(10) < queixo_z(0) else -1
def pose(g):
    pb.rotation_euler = (math.radians(SINAL * g), 0, 0)
    if pl: pl.rotation_euler = (math.radians(SINAL * LG * g), 0, 0)
    bpy.context.view_layer.update()
CX = -0.22
VIS = {"34": ((CX, -14.4, 12.2), -40, 6, 6.5, 50), "34e": ((CX, -14.4, 12.2), 40, 6, 6.5, 50),
       "perfil": ((CX, -14.3, 12.2), -90, 0, 6.5, 50), "frente": ((CX, -14.8, 12.25), 0, 3, 5.5, 50),
       "baixo": ((CX, -14.5, 12.0), -25, -40, 6.5, 50), "interna": ((CX, -14.4, 12.3), -6, -3, 4.2, 50),
       "geral34": ((CX, -13.6, 12.8), -38, 6, 13, 50),
       "jogo": ((0, -10, 9), -40, 10, 80, 50)}
def corte(nome, x, res, metade=1.9):
    """corte sagital: camera ortografica do lado X+, plano de recorte em x (abre a cavidade)"""
    cam_d.type = "ORTHO"; cam_d.ortho_scale = 2 * metade; cam_d.clip_start = 20.0; cam_d.clip_end = 60.0
    cam.location = Vector((x + 20.0, -14.0, 12.1)); cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
    cam_d.clip_start = 0.1; cam_d.clip_end = 1000
def persp(nome, alvo, az, el, dist, lens, res):
    cam_d.type = "PERSP"; cam_d.lens = lens; alvo = Vector(alvo)
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)),
                                  math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
def malha(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); m = ev.to_mesh()
    vs = [v.co.copy() for v in m.vertices]; ps = [(list(p.vertices), p.material_index) for p in m.polygons]
    ev.to_mesh_clear(); return vs, ps
def pesos(o, nome):
    gi = o.vertex_groups[nome].index; out = []
    for v in o.data.vertices:
        x = 0.0
        for g in v.groups:
            if g.group == gi: x = g.weight
        out.append(x)
    return out
WM = pesos(corpo, "Mandibula")
PROF = [i for i, x in enumerate(pesos(corpo, "Boca_Profundo")) if x > 0.5] if "Boca_Profundo" in corpo.vertex_groups else []
INTERIOR = {i for p in corpo.data.polygons if p.material_index == 1 for i in p.vertices}
_borda = [corpo.data.vertices[i].co.copy() for p in corpo.data.polygons if p.material_index == 0 for i in p.vertices if i in INTERIOR]
_bb = BVHTree.FromPolygons(_borda, [[i, i, i] for i in range(len(_borda))]) if _borda else None
LONGE_LABIO = {i for i, v in enumerate(corpo.data.vertices) if i not in INTERIOR and -15.6 < v.co.y < -12.6 and
               (_bb is None or (_bb.find_nearest(v.co)[3] or 9) > 0.3)}
def bvh(vs, ps): return BVHTree.FromPolygons(vs, ps) if ps else None
def medir(g):
    vs, ps = malha(corpo)
    cab = [p for p, m in ps if m == 0 and max(WM[i] for i in p) < 0.05]
    b_cab = bvh(vs, cab); n = 0
    for i, v in enumerate(vs):
        if WM[i] < 0.5 or corpo.data.vertices[i].co.y > -11.5: continue
        hit = b_cab.find_nearest(v, 0.25)
        if hit[0] is not None and (v - hit[0]).dot(hit[1]) < -0.01: n += 1
    pal = bvh(vs, [p for p, m in ps if m == 1 and sum(WM[i] for i in p) / len(p) < 0.3])
    ass = bvh(vs, [p for p, m in ps if m == 1 and sum(WM[i] for i in p) / len(p) > 0.7])
    obj = {}
    for nome in ("Leao_Dentes_Sup", "Leao_Dentes_Inf", "Leao_Lingua"):
        v2, p2 = malha(bpy.data.objects[nome]); obj[nome] = bvh(v2, [p for p, _ in p2])
    S, I, L = obj["Leao_Dentes_Sup"], obj["Leao_Dentes_Inf"], obj["Leao_Lingua"]
    oS = S.overlap(I)
    if oS and g > 0:
        vS, pS = malha(bpy.data.objects["Leao_Dentes_Sup"]); vI, pI = malha(bpy.data.objects["Leao_Dentes_Inf"])
        print("  dentes_sxi ex:", sorted({(tuple(round(c, 2) for c in vS[pS[a][0][0]]), tuple(round(c, 2) for c in vI[pI[b][0][0]])) for a, b in oS})[:6])
    r = {"graus": g, "pen_pele": n, "dentes_sxi": len(oS), "sup_ass": len(S.overlap(ass)), "inf_pal": len(I.overlap(pal)),
         "lingua_pal": len(L.overlap(pal)) + len(L.overlap(S)), "lingua_inf": len(L.overlap(I))}
    pele = bvh(vs, [p for p, m in ps if m == 0]); kf = 0
    SP = set(PROF); pf_l = [p for p, m in ps if m == 1 and all(i in SP for i in p)]; prof_f = bvh(vs, pf_l)
    pl_l = [p for p, m in ps if m == 0]
    ov = prof_f.overlap(pele) if prof_f else []
    r["cav_x_pele"] = len(ov)
    toca = {i for p, m in ps if m == 0 for i in p}
    ab_l = [p for p, m in ps if m == 1 and not any(i in toca for i in p)]; ab = bvh(vs, ab_l)
    oa = ab.overlap(pele) if ab else []
    r["aba_x_pele"] = len(oa)                                # qualquer face do interior (fora a 1a fileira) atravessando a pele
    if oa and g in (20, 32): print("  aba ex:", sorted({tuple(round(c, 2) for c in sum((corpo.data.vertices[i].co for i in ab_l[a]), Vector()) / len(ab_l[a])) for a, b in oa})[:10])
    if ov and g in (0, 32): print("  cav_x_pele ex:", sorted({tuple(round(c, 1) for c in sum((corpo.data.vertices[i].co for i in pf_l[a]), Vector()) / len(pf_l[a])) for a, b in ov})[:10])
    for nome_, B_ in (("Leao_Dentes_Sup", None), ("Leao_Dentes_Inf", None), ("Leao_Lingua", None)):
        v2, p2 = malha(bpy.data.objects[nome_]); b2 = bvh(v2, [p for p, _ in p2]); o2 = b2.overlap(pele)
        if o2 and g == 0: print("  %s x pele ex:" % nome_, sorted({tuple(round(c, 2) for c in sum((v2[i] for i in p2[a][0]), Vector()) / len(p2[a][0])) for a, b in o2})[:6])
    r["dentes_x_pele"] = len(S.overlap(pele)) + len(I.overlap(pele)); r["lingua_x_pele"] = len(L.overlap(pele))
    ex = []
    for i in PROF:                                           # interior profundo que aparece por fora da pele
        hit = pele.find_nearest(vs[i], 0.6)
        if hit[0] is not None and (vs[i] - hit[0]).dot(hit[1]) > 0.005: kf += 1; ex.append(tuple(round(c, 2) for c in corpo.data.vertices[i].co))
    if ex: print("  fora_prof ex:", ex[:8])
    r["fora_prof_aprox"] = kf
    kp = 0                                                   # pele entre o palato e o assoalho (aparece dentro da boca)
    ex = []
    for i in LONGE_LABIO:
        v = vs[i]; a = pal.ray_cast(v, Vector((0, 0, 1)), 1.2); b = ass.ray_cast(v, Vector((0, 0, -1)), 1.2)
        if a[0] is not None and b[0] is not None: kp += 1; ex.append(tuple(round(c, 2) for c in corpo.data.vertices[i].co))
    if ex: print("  pele_na_boca ex:", ex[:8])
    r["pele_na_boca"] = kp
    if g == 0:
        pele = bvh(vs, [p for p, m in ps if m == 0]); pv = {i for p, m in ps if m == 0 for i in p}
        pts = [vs[i] for p, m in ps if m == 1 for i in p if i not in pv]
        for nome in ("Leao_Dentes_Sup", "Leao_Dentes_Inf", "Leao_Lingua"): pts += malha(bpy.data.objects[nome])[0]
        DIRS = [Vector((0.31, 0.05, 0.95)).normalized(), Vector((-0.6, -0.7, 0.38)).normalized(), Vector((0.7, -0.2, -0.68)).normalized()]
        def dentro(p):
            votos = 0
            for dv in DIRS:
                n, q = 0, p.copy()
                for _ in range(60):
                    hit = pele.ray_cast(q, dv, 40.0)
                    if hit[0] is None: break
                    n += 1; q = hit[0] + dv * 1e-4
                votos += n % 2
            return votos >= 2
        k = 0; exf = []
        for p in set(tuple(x) for x in pts):                 # fechada: a pele e uma casca fechada -> paridade
            if not dentro(Vector(p)): k += 1; exf.append(tuple(round(c, 2) for c in p))
        if exf: print("  fora ex:", exf[:10])
        r["fora"] = k; r["pts_interior"] = len(pts)
    return r
rel = []
for g in GRAUS:
    pose(g); t = "%02d" % int(round(g))
    for v in VISTAS:
        if v == "interna" and g == 0: continue
        if v.startswith("corte"):
            corte("boca_%s_%s" % (t, v), CX + float(v[5:] or 0), RES); continue
        if v not in VIS: continue
        alvo, az, el, dist, lens = VIS[v]
        persp("boca_%s_%s" % (t, v), alvo, az, el, dist, lens, 360 if v == "jogo" else RES)
    if "Leao_Dentes_Sup" not in bpy.data.objects: continue   # malha de jogo unida (E4): medir no arquivo antes da uniao
    m = medir(g); rel.append(m); print("MEDIDA", json.dumps(m))
json.dump(rel, open(os.path.join(OUT, "medidas.json"), "w"), indent=1)
print("RENDER_OK")
