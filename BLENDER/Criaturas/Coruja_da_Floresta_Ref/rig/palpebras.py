"""Rig r4 da coruja = r3 + PALPEBRAS (15/11/2026, pedido: "ele dorme com os olhos fechados").
O modelo nao tinha palpebras (olhos so na textura). Cada palpebra e uma cupula (calota de esfera) sobre o olho:
  - olho localizado pela iris na textura (amostrada dentro dos triangulos): E (0,045; -0,206; 0,512), D (-0,047; -0,206; 0,514);
  - esfera centrada ATRAS do olho (PROF) com raio = PROF + FOLGA (a calota fica um pouco acima da superficie do olho);
  - repouso (bind) = ABERTA: calota girada ABRIR graus para cima/tras, escondida dentro da cabeca -> clipes que nao citam
    a palpebra (lotes A/B ja aprovados) continuam de olhos abertos; FECHAR = girar o osso -ABRIR em torno do eixo lateral;
  - UV transferida da cabeca na posicao aberta (pega a pena da sobrancelha) -> mesmo material da cabeca (nada novo);
  - ossos PalpebraE/D (filhos da Cabeca), peso 100%, unidos a malha Coruja_Cabeca.
Grava rig/r4/CR_Coruja_Rig.blend e rig/r4/palpebras.json (eixos e angulo para os clipes) + provas aberta/fechada.
Uso: blender -b rig/r3/CR_Coruja_Rig.blend -P rig/palpebras.py -- rig/r4 [abrir=100] [prof=0.02] [folga=0.003] [abertura_cone=55]"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
def arg(n, d): return type(d)(next((a.split("=")[1] for a in A[1:] if a.startswith(n + "=")), d))
ABRIR, PROF, FOLGA, CONE = arg("abrir", 100.0), arg("prof", 0.02), arg("folga", 0.004), arg("abertura_cone", 70.0)
OFF_UV = arg("off_uv", 0.045)                                         # deslocamento lateral para amostrar a pena clara do disco facial
for im in bpy.data.images:
    if im.filepath and "low_voxel" in im.filepath: im.filepath = im.filepath.replace("low_voxel", "low_v1"); im.reload()
sc = bpy.context.scene; arm = bpy.data.objects["Coruja_Rig"]; CAB = bpy.data.objects["Coruja_Cabeca"]
OLHOS = {"E": V((0.0438, -0.2074, 0.5133)), "D": V((-0.0446, -0.2079, 0.5164))}   # media iris/pupila medida (olhos2)
def normal_olho(sx):
    """olho de coruja olha para a frente, um pouco para fora e quase nada para cima"""
    return V((0.22 * sx, -1.0, 0.06)).normalized()
bvh = BVHTree.FromObject(CAB, bpy.context.evaluated_depsgraph_get())
def dentro(p):
    n_ = 0; o_ = V(p)
    for _ in range(40):
        h = bvh.ray_cast(o_, V((0.0013, 0.0007, 1)).normalized(), 2.0)
        if h[0] is None: break
        n_ += 1; o_ = h[0] + V((0, 0, 1e-5))
    return n_ % 2 == 1
INFO = {}; novos = []; INFO_UV = {}
for l, sx in (("E", 1), ("D", -1)):
    n = normal_olho(sx); lat = n.cross(V((0, 0, 1))).normalized()           # eixo lateral (fechar = girar em torno dele)
    if lat.x * sx < 0: lat = -lat
    # superficie do olho: raio a partir do centro ate a malha ao longo de n
    c0 = OLHOS[l] - n * PROF; hit = bvh.ray_cast(c0, n, 0.1); sup = (hit[0] - c0).length if hit[0] else PROF
    R_ = sup + FOLGA
    bm = bmesh.new(); aneis, seg = 6, 14
    def pt(th, ph):                                                           # th: angulo a partir do eixo n; ph: volta
        u = (lat * math.cos(ph) + n.cross(lat) * math.sin(ph))
        return c0 + (n * math.cos(th) + u * math.sin(th)) * R_
    topo = bm.verts.new(pt(0, 0)); anel_ant = None
    for i in range(1, aneis + 1):
        th = math.radians(CONE) * i / aneis; anel = [bm.verts.new(pt(th, 2 * math.pi * j / seg)) for j in range(seg)]
        for j in range(seg):
            a, b = anel[j], anel[(j + 1) % seg]
            if anel_ant is None: bm.faces.new((topo, a, b))
            else: bm.faces.new((anel_ant[j], anel_ant[(j + 1) % seg], b, a))
        anel_ant = anel
    # abre: gira a calota ABRIR graus em torno do eixo lateral passando pelo centro c0 (para cima e para tras)
    Rm = Matrix.Translation(c0) @ Matrix.Rotation(math.radians(ABRIR), 4, lat) @ Matrix.Translation(-c0)
    teste = (Rm @ (c0 + n * R_));
    if teste.z < (c0 + n * R_).z: Rm = Matrix.Translation(c0) @ Matrix.Rotation(math.radians(-ABRIR), 4, lat) @ Matrix.Translation(-c0); sinal = -1
    else: sinal = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)                # (r5: o leque do polo saia invertido -> anel escuro no centro)
    if bm.faces[0].normal.dot(bm.faces[0].calc_center_median() - c0) < 0:
        for f_ in bm.faces: f_.normal_flip()
    me = bpy.data.meshes.new("Palpebra" + l); bm.to_mesh(me); bm.free()
    # UV: na posicao FECHADA, deslocada para o lado de fora (OFF_UV) sobre o disco facial claro -> pena clara do disco
    # (r2: transferida na posicao aberta, a cor vinha do proprio olho e a palpebra fechada parecia um olho borrado)
    tmp = bpy.data.objects.new("tmpUV", me); sc.collection.objects.link(tmp)
    for v in me.vertices: v.co = v.co + lat * OFF_UV
    tmp.data.materials.append(CAB.data.materials[0]); tmp.data.uv_layers.new(name=CAB.data.uv_layers.active.name)
    for o_ in sc.objects: o_.select_set(False)
    bpy.context.view_layer.objects.active = tmp; tmp.select_set(True)
    dt = tmp.modifiers.new("UV", "DATA_TRANSFER"); dt.object = CAB; dt.use_loop_data = True; dt.data_types_loops = {"UV"}; dt.loop_mapping = "POLYINTERP_NEAREST"
    bpy.ops.object.modifier_apply(modifier=dt.name)
    # UV de um PONTO escolhido do disco facial claro (fora do olho), com variacao minima (r4: a mediana ainda caia num anel da textura)
    alvo_uv = OLHOS[l] + lat * OFF_UV + V((0, 0, -0.004)); vi_ = min(range(len(CAB.data.vertices)), key=lambda i: (CAB.data.vertices[i].co - alvo_uv).length)
    uv_ref = next(np.array(CAB.data.uv_layers.active.data[li].uv[:]) for poly in CAB.data.polygons for li in poly.loop_indices if CAB.data.loops[li].vertex_index == vi_)
    uvs = np.array([d.uv[:] for d in me.uv_layers.active.data]); med = np.median(uvs, 0)
    for d, u in zip(me.uv_layers.active.data, uvs): d.uv = tuple(uv_ref + (u - med) * 0.03)
    INFO_UV[l] = (vi_, list(CAB.data.vertices[vi_].co))
    for v in me.vertices: v.co = Rm @ (v.co - lat * OFF_UV)
    bpy.data.objects.remove(tmp)
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new("Palpebra" + l, me); sc.collection.objects.link(ob)
    fora = sum(1 for v in me.vertices if not dentro(v.co))
    INFO[l] = {"centro": list(c0), "raio": R_, "eixo": list(lat), "fechar_graus": -sinal * ABRIR, "olho": list(OLHOS[l]), "normal": list(n),
               "vertices": len(me.vertices), "tris": sum(len(p.vertices) - 2 for p in me.polygons), "vertices_fora_da_cabeca_aberta": fora}
    novos.append((l, ob)); print("PALPEBRA", l, json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in INFO[l].items() if k in ("raio", "fechar_graus", "tris", "vertices_fora_da_cabeca_aberta")}))
# UV: transfere da cabeca (na posicao aberta pega a pena da sobrancelha) e usa o mesmo material
for l, ob in novos:
    for o_ in sc.objects: o_.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    g = ob.vertex_groups.new(name="Palpebra" + l); g.add([v.index for v in ob.data.vertices], 1.0, "REPLACE")
# ossos
bpy.context.view_layer.objects.active = arm
for o_ in sc.objects: o_.select_set(False)
arm.select_set(True); bpy.ops.object.mode_set(mode="EDIT"); E = arm.data.edit_bones
for l in ("E", "D"):
    b = E.new("Palpebra" + l); c0 = V(INFO[l]["centro"]); b.head = c0; b.tail = c0 + V(INFO[l]["eixo"]) * 0.02; b.parent = E["Cabeca"]; b.use_connect = False; b.roll = 0
bpy.ops.object.mode_set(mode="OBJECT")
# une a cabeca (mantem 2 materiais no total) e religa a armature
for o_ in sc.objects: o_.select_set(False)
for l, ob in novos: ob.select_set(True)
CAB.select_set(True); bpy.context.view_layer.objects.active = CAB; bpy.ops.object.join()
for g in ("PalpebraE", "PalpebraD"): assert CAB.vertex_groups.get(g)
print("CABECA tris", sum(len(p.vertices) - 2 for p in CAB.data.polygons), "materiais", [m.name for m in CAB.data.materials], "grupos", len(CAB.vertex_groups))
json.dump({"abrir_graus": ABRIR, "prof": PROF, "folga": FOLGA, "cone_graus": CONE, "olhos": INFO}, open(os.path.join(OUT, "palpebras.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Coruja_Rig.blend"))
# provas: aberta (repouso) e fechada, close do rosto
PB = arm.pose.bones
for b in PB: b.rotation_mode = "QUATERNION"
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
w = bpy.data.worlds.new("F"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (*lin("8a8580"), 1)
sd = bpy.data.lights.new("S", "SUN"); sd.energy = 2.2; so = bpy.data.objects.new("S", sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(55), 0, math.radians(-25))
def cam(nome, loc, alvo, lente):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); c.lens = lente; return o
CAMS = {"frente": cam("F", (0, -0.75, 0.53), (0, -0.2, 0.50), 60), "34": cam("T", (-0.45, -0.6, 0.58), (0, -0.2, 0.50), 60), "perfil": cam("P", (-0.7, -0.15, 0.52), (0, -0.15, 0.50), 55)}
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 520, 420
def rot_mundo(nome, eixo, ang):
    r = arm.data.bones[nome].matrix_local.to_3x3(); q = Matrix.Rotation(ang, 3, eixo)
    return (r.inverted() @ q @ r).to_quaternion()
for estado, f in (("aberta", 0.0), ("meio", 0.5), ("fechada", 1.0)):
    for l in ("E", "D"):
        PB["Palpebra" + l].rotation_quaternion = rot_mundo("Palpebra" + l, V(INFO[l]["eixo"]), math.radians(INFO[l]["fechar_graus"]) * f)
    bpy.context.view_layer.update()
    for v, c in CAMS.items(): sc.camera = c; sc.render.filepath = os.path.join(OUT, f"prova_palpebra_{estado}_{v}.png"); bpy.ops.render.render(write_still=True)
for b in PB: b.rotation_quaternion = (1, 0, 0, 0)
print("PALPEBRAS_OK")
