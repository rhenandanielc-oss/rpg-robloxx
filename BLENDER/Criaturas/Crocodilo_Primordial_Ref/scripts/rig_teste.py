"""Esqueleto de TESTE do Crocodilo Primordial na LOW (so para conferir abertura/fechamento da mandibula e flexao da
cauda; nao e o rig final nem gera a biblioteca de animacoes). Marcos tirados da propria malha.
Pesos: automaticos (heat) com reserva por distancia; mandibula por conectividade a partir do queixo.
Uso: blender -b CR_Crocodilo_LOW.blend -P rig_teste.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; lo = bpy.data.objects["CR_Croc_LOW"]; me = lo.data
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co[:, 0], co[:, 1], co[:, 2]
Y0, Y1 = y.min(), y.max()

# ------------------------------------------------------------------ marcos
pes = {}
for lado, sx in (("E", 1), ("D", -1)):
    for par, cond in (("dian", y < -4.0), ("tras", y >= -4.0)):
        sel = (z < 0.35) & (x * sx > 1.5) & cond
        pes[(lado, par)] = V(co[sel].mean(axis=0)) if sel.any() else None
print("PES", {k: tuple(round(c, 2) for c in v) for k, v in pes.items() if v})
y_ombro = (pes[("E", "dian")].y + pes[("D", "dian")].y) / 2 + 0.6
y_quad = (pes[("E", "tras")].y + pes[("D", "tras")].y) / 2 + 0.3
def centro(yy, faixa=0.3):
    s = np.abs(y - yy) < faixa
    s2 = s & (np.abs(x) < 1.0)
    return V((0, yy, (z[s2].min() + z[s2].max()) / 2)) if s2.any() else V((0, yy, 3))
# boca: raios verticais no eixo. A malha e casca: cranio (entra), palato (sai), lingua/assoalho (entra), queixo (sai).
# O ar da boca fica entre o 2o e o 3o impacto. Sem boca (atras do canto) so ha 2 impactos.
bpy.context.view_layer.update()
def impactos(xx, yy):
    zs = []; zz = 12.0
    while True:
        ok, h, nrm, _ = lo.ray_cast(V((xx, yy, zz)), V((0, 0, -1)), distance=zz + 1)
        if not ok: break
        zs.append(h.z); zz = h.z - 0.002
        if len(zs) > 12: break
    return zs
fenda = []                                              # (y, z_meio, altura do vao, z_palato, z_assoalho)
for yy in np.arange(Y0 + 0.25, Y0 + 9.0, 0.15):
    vaos = []
    for xx in (0.0, 0.35, -0.35):
        h = impactos(xx, yy)
        if len(h) >= 4: vaos.append((h[1], h[2]))
    if vaos:
        pal = float(np.median([a for a, b in vaos])); ass = float(np.median([b for a, b in vaos]))
        if pal - ass > 0.04: fenda.append((float(yy), (pal + ass) / 2, pal - ass, pal, ass))
# a fenda continua so ate o primeiro buraco grande (a garganta fechada atras do canto encerra a sequencia)
cont = [fenda[0]]
for f in fenda[1:]:
    if f[0] - cont[-1][0] > 0.5: break
    cont.append(f)
fenda = cont
y_canto = fenda[-1][0]
y_dob, z_dob = y_canto + 0.55, fenda[-1][1]                # articulacao: atras e na linha do canto da boca
ab = fenda[0]
print("BOCA fenda de y %.2f a %.2f (canto); vao na ponta %.2f (palato %.2f, assoalho %.2f); dobradica y %.2f z %.2f" % (
    fenda[0][0], y_canto, ab[2], ab[3], ab[4], y_dob, z_dob))
def z_palato(yy):
    if yy <= fenda[0][0]: return fenda[0][3]
    for a, b in zip(fenda, fenda[1:]):
        if a[0] <= yy <= b[0]: t = (yy - a[0]) / (b[0] - a[0]); return a[3] + (b[3] - a[3]) * t
    return fenda[-1][3]
def z_fenda(yy):
    if yy <= fenda[0][0]: return fenda[0][1]
    for a, b in zip(fenda, fenda[1:]):
        if a[0] <= yy <= b[0]: t = (yy - a[0]) / (b[0] - a[0]); return a[1] + (b[1] - a[1]) * t
    return fenda[-1][1]

# ------------------------------------------------------------------ armadura
arm_d = bpy.data.armatures.new("CR_Croc_Rig"); arm = bpy.data.objects.new("CR_Croc_Rig", arm_d); sc.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT")
E = arm_d.edit_bones
def osso(nome, a, b, pai=None, conecta=True):
    o = E.new(nome); o.head = a; o.tail = b
    if pai: o.parent = E[pai]; o.use_connect = conecta and (E[pai].tail - a).length < 1e-4
    return o
c_quad, c_omb = centro(y_quad), centro(y_ombro)
osso("Raiz", V((0, (y_quad + y_ombro) / 2, 0)), V((0, (y_quad + y_ombro) / 2, 1.0)))
osso("Pelve", c_quad, centro((y_quad + y_ombro) / 2), "Raiz", False)
osso("Coluna", E["Pelve"].tail, c_omb, "Pelve")
y_pesc = y_dob + 1.6
osso("Pescoco", c_omb, centro(y_pesc), "Coluna")
cab0 = V((0, y_dob, z_dob + 0.35))
osso("Pescoco2", E["Pescoco"].tail, cab0, "Pescoco")
osso("Cabeca", cab0, V((0, Y0 + 0.6, z_fenda(Y0 + 0.6) + 0.5)), "Pescoco2")
osso("Mandibula", V((0, y_dob, z_dob)), V((0, Y0 + 0.6, z_fenda(Y0 + 0.6) - 0.35)), "Pescoco2", False)
ys_c = np.linspace(y_quad, Y1 - 0.2, 9); ant = "Pelve"
for i in range(8):
    osso("Cauda%d" % (i + 1), centro(ys_c[i]), centro(ys_c[i + 1]), ant, i > 0 or False); ant = "Cauda%d" % (i + 1)
E["Cauda1"].parent = E["Pelve"]
for lado, sx in (("E", 1), ("D", -1)):
    for par, yb, pai, nomes in (("dian", y_ombro, "Coluna", ("Braco", "Antebraco", "Mao")), ("tras", y_quad, "Pelve", ("Coxa", "Canela", "Pe"))):
        p = pes[(lado, par)]
        raiz = V((1.3 * sx, yb, centro(yb).z - 0.3)); joelho = V((p.x * 0.92, (yb + p.y) / 2, 1.9)); tornoz = V((p.x, p.y + (0.35 if par == "dian" else 0.5), 0.75))
        osso(nomes[0] + lado, raiz, joelho, pai, False); osso(nomes[1] + lado, joelho, tornoz, nomes[0] + lado)
        osso(nomes[2] + lado, tornoz, V((p.x, p.y - 1.1, 0.25)), nomes[1] + lado)
bpy.ops.object.mode_set(mode="OBJECT")

# ------------------------------------------------------------------ pesos
for o in sc.objects: o.select_set(False)
lo.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
ok_heat = True
try: bpy.ops.object.parent_set(type="ARMATURE_AUTO")
except Exception as e: ok_heat = False; print("HEAT falhou:", e)
sem_peso = sum(1 for v in me.vertices if not v.groups)
print("PESOS heat ok:", ok_heat, "verts sem peso:", sem_peso)
if sem_peso > n * 0.01:                                  # reserva: pesos por envelope (distancia)
    for vg in list(lo.vertex_groups): lo.vertex_groups.remove(vg)
    lo.parent = None; lo.modifiers.clear()
    lo.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_ENVELOPE"); print("PESOS reserva envelope")
# mandibula x cranio: disputa geodesica (Dijkstra pelas arestas) entre sementes inequivocas - cranio acima do palato e
# queixo abaixo do assoalho. Dentes/gengivas/labios ficam com quem chega primeiro (um contato dente-dente nao vaza).
import heapq
def z_assoalho(yy):
    if yy <= fenda[0][0]: return fenda[0][4]
    for a, b in zip(fenda, fenda[1:]):
        if a[0] <= yy <= b[0]: t = (yy - a[0]) / (b[0] - a[0]); return a[4] + (b[4] - a[4]) * t
    return fenda[-1][4]
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
dono = {}; dist = {}; fila = []
for v in bm.verts:
    if v.co.y > y_canto - 0.10: continue
    if v.co.z > z_palato(v.co.y) + 0.35: dono[v.index] = 0
    elif v.co.z < z_assoalho(v.co.y) - 0.35: dono[v.index] = 1
    else: continue
    dist[v.index] = 0.0; heapq.heappush(fila, (0.0, v.index, dono[v.index]))
while fila:
    d, i, k = heapq.heappop(fila)
    if d > dist.get(i, 1e9): continue
    a = bm.verts[i]
    for e in a.link_edges:
        b = e.other_vert(a)
        if b.co.y > y_canto - 0.10: continue
        zf = z_fenda(b.co.y)
        cruza = (k == 1 and b.co.z > zf) or (k == 0 and b.co.z < zf)   # atravessar a linha da boca custa mais
        nd = d + e.calc_length() * (4.0 if cruza else 1.0)
        if nd < dist.get(b.index, 1e9): dist[b.index] = nd; dono[b.index] = k; heapq.heappush(fila, (nd, b.index, k))
inf = {i for i, k in dono.items() if k == 1}
bm.free()
gc, gm = lo.vertex_groups.get("Cabeca") or lo.vertex_groups.new(name="Cabeca"), lo.vertex_groups.get("Mandibula") or lo.vertex_groups.new(name="Mandibula")
cab_set = 0
for v in me.vertices:
    if v.co.y > y_dob + 0.8: continue
    if v.index in inf:
        gm.add([v.index], 1.0, "REPLACE"); gc.add([v.index], 0.0, "REPLACE")
    elif v.co.y < y_canto - 0.10:
        gc.add([v.index], 1.0, "REPLACE"); gm.add([v.index], 0.0, "REPLACE"); cab_set += 1
    else:                                                # canto -> dobradica: abaixo da linha vai com a mandibula
        t = min(1.0, max(0.0, (y_dob + 0.8 - v.co.y) / (y_dob + 0.8 - y_canto)))
        baixo = min(1.0, max(0.0, (z_dob + 0.15 - v.co.z) / 0.4))
        wm = t * baixo; gm.add([v.index], wm, "REPLACE"); gc.add([v.index], t * (1 - baixo), "REPLACE")
print("MANDIBULA verts", len(inf), "cabeca", cab_set)
# na cabeca o heat espalha pesos para o pescoco; zera grupos que nao sejam Cabeca/Mandibula a frente do canto
for v in me.vertices:
    if v.co.y < y_canto - 0.10:
        for g in list(v.groups):
            nome = lo.vertex_groups[g.group].name
            if nome not in ("Cabeca", "Mandibula"): lo.vertex_groups[g.group].remove([v.index])

# ------------------------------------------------------------------ poses e renders
pt = (V((0, Y0, z_fenda(Y0 + 0.3))))
ang_aberto = math.degrees(math.atan2(fenda[0][2], (y_dob - fenda[0][0])))       # vao na ponta / distancia a dobradica
print("ANGULO de abertura medido ~%.1f graus" % ang_aberto)
cam = sc.camera; cd = cam.data
def pose(nome, rot):
    for pb in arm.pose.bones: pb.rotation_mode = "XYZ"; pb.rotation_euler = (0, 0, 0)
    for b, r in rot.items(): arm.pose.bones[b].rotation_euler = r
    bpy.context.view_layer.update()
def foto(nome, p, a, lente=40, orto=None):
    cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler()
    if orto: cd.type = "ORTHO"; cd.ortho_scale = orto
    else: cd.type = "PERSP"; cd.lens = lente
    sc.render.filepath = os.path.join(OUT, "rig_%s.png" % nome); bpy.ops.render.render(write_still=True)
cabeca_c = V((0, Y0 + 3.5, 3.2))
fecha = math.radians(ang_aberto * 0.80)          # 100% faz os dentes de baixo atravessarem o focinho (sem encaixes no Meshy)
pose("neutra", {}); foto("neutra_cabeca", cabeca_c + V((7.5, -6.5, 1.2)), cabeca_c)
pose("fechada", {"Mandibula": (-fecha, 0, 0)}); foto("fechada_cabeca", cabeca_c + V((7.5, -6.5, 1.2)), cabeca_c)
foto("fechada_frente", cabeca_c + V((0, -9, 0.4)), cabeca_c, 45)
pose("fechada100", {"Mandibula": (-math.radians(ang_aberto), 0, 0)}); foto("fechada100_cabeca", cabeca_c + V((7.5, -6.5, 1.2)), cabeca_c)
pose("aberta", {"Mandibula": (math.radians(14), 0, 0)}); foto("aberta_mais_cabeca", cabeca_c + V((7.5, -6.5, 1.2)), cabeca_c)
curva = {"Cauda%d" % i: (0, 0, math.radians(9)) for i in range(1, 9)}
pose("cauda", curva); foto("cauda_topo", V((0, 0, 40)), V((0, 0.01, 0)), orto=36)
pose("cauda_v", {"Cauda%d" % i: (math.radians(-4), 0, 0) for i in range(1, 9)}); foto("cauda_lado", V((40, 0, 3)), V((0, 0, 3)), orto=36)
pose("neutra", {})
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath), "CR_Crocodilo_LOW_rigteste.blend"))
print("RIG_OK ossos", len(arm_d.bones))
