"""Lote 4 (montaria, so apresentacao): manequim de TESTE com proporcoes APROXIMADAS do avatar R15 em bloco, escala 1,0
(15 partes em caixas, altura 5,2 studs, quadril 2,0, ombros +-1,5). NAO e um rig R15 validado: nomes de partes iguais aos
do R15 so para leitura. Partes rigidas (peso 1 no osso), sem malha deformavel. Tambem cria o volume de apoio PROPOSTA
(sela de teste, sem acabamento) e as medicoes de folga contra a malha do crocodilo.
Eixos (iguais aos do crocodilo): frente = -Y, Z para cima, esquerda = +X. Modulo importado pelos scripts do Lote 4."""
import bpy, math
import numpy as np
from mathutils import Vector as V, Matrix as M, Quaternion as Q
from mathutils.bvhtree import BVHTree

# osso: (pai, cabeca, cauda, caixa (tamanho x,y,z), centro da caixa) - de pe, de frente para -Y, pes em z = 0
PARTES = {
    "LowerTorso": (None, (0, 0, 2.0), (0, 0, 2.4), (2.0, 1.0, 0.4), (0, 0, 2.2)),
    "UpperTorso": ("LowerTorso", (0, 0, 2.4), (0, 0, 4.0), (2.0, 1.0, 1.6), (0, 0, 3.2)),
    "Head": ("UpperTorso", (0, 0, 4.0), (0, 0, 5.2), (1.2, 1.2, 1.2), (0, 0, 4.6)),
}
for lado, s in (("Left", 1), ("Right", -1)):
    PARTES.update({
        lado + "UpperArm": ("UpperTorso", (1.5 * s, 0, 3.75), (1.5 * s, 0, 2.85), (1.0, 1.0, 1.1), (1.5 * s, 0, 3.4)),
        lado + "LowerArm": (lado + "UpperArm", (1.5 * s, 0, 2.85), (1.5 * s, 0, 2.05), (1.0, 1.0, 0.85), (1.5 * s, 0, 2.45)),
        lado + "Hand": (lado + "LowerArm", (1.5 * s, 0, 2.05), (1.5 * s, 0, 1.75), (1.0, 1.0, 0.3), (1.5 * s, 0, 1.9)),
        lado + "UpperLeg": ("LowerTorso", (0.5 * s, 0, 2.0), (0.5 * s, 0, 1.15), (1.0, 1.0, 0.95), (0.5 * s, 0, 1.6)),
        lado + "LowerLeg": (lado + "UpperLeg", (0.5 * s, 0, 1.15), (0.5 * s, 0, 0.3), (1.0, 1.0, 0.9), (0.5 * s, 0, 0.72)),
        lado + "Foot": (lado + "LowerLeg", (0.5 * s, 0, 0.3), (0.5 * s, -0.5, 0.3), (1.0, 1.0, 0.3), (0.5 * s, 0, 0.15)),
    })
QUADRIL = 2.0                  # altura da junta do quadril de pe (HipHeight do R15)
NOME = "TESTE_Manequim_R15aprox"

def _caixa(tam, cen):
    sx, sy, sz = (t / 2 for t in tam); cx, cy, cz = cen
    vs = [(cx + a * sx, cy + b * sy, cz + c * sz) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    fs = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return vs, fs

def criar(colecao=None):
    sc = bpy.context.scene; col = colecao or sc.collection
    ad = bpy.data.armatures.new(NOME + "_Rig"); ra = bpy.data.objects.new(NOME + "_Rig", ad); col.objects.link(ra)
    ad.display_type = "STICK"; ra.show_in_front = True
    bpy.context.view_layer.objects.active = ra; bpy.ops.object.mode_set(mode="EDIT")
    for nm, (pai, h, t, _, _) in PARTES.items():
        eb = ad.edit_bones.new(nm); eb.head = h; eb.tail = t; eb.roll = 0.0
        if pai: eb.parent = ad.edit_bones[pai]
    bpy.ops.object.mode_set(mode="OBJECT")
    vs, fs, grupos = [], [], {}
    for nm, (_, _, _, tam, cen) in PARTES.items():
        v, f = _caixa(tam, cen); o = len(vs); vs += v; fs += [tuple(i + o for i in q) for q in f]; grupos[nm] = range(o, o + 8)
    # nariz/viseira escura na frente da cabeca (mostra para onde o manequim olha)
    v, f = _caixa((0.7, 0.12, 0.25), (0, -0.62, 4.75)); o = len(vs); vs += v; fs += [tuple(i + o for i in q) for q in f]; grupos["Head"] = list(grupos["Head"]) + list(range(o, o + 8))
    me = bpy.data.meshes.new(NOME); me.from_pydata(vs, [], fs); me.update()
    ob = bpy.data.objects.new(NOME, me); col.objects.link(ob); ob.parent = ra
    for nm, idx in grupos.items():
        g = ob.vertex_groups.new(name=nm); g.add(list(idx), 1.0, "REPLACE")
    ob.modifiers.new("Armature", "ARMATURE").object = ra
    mt = bpy.data.materials.new("TESTE_M_Manequim"); mt.use_nodes = True; b = mt.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.30, 0.55, 0.85, 1); b.inputs["Roughness"].default_value = 0.6
    mv = bpy.data.materials.new("TESTE_M_Viseira"); mv.use_nodes = True; mv.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.06, 1)
    me.materials.append(mt); me.materials.append(mv)
    for p in me.polygons: p.material_index = 1 if p.index >= len(fs) - 6 else 0
    # IK de 2 ossos nas maos e pes (alvos e polos sao empties); pes/maos copiam a rotacao do alvo
    alvos = {}
    for lado in ("Left", "Right"):
        for parte, ponta in (("Arm", "Hand"), ("Leg", "Foot")):
            for tipo in ("IK", "Polo"):
                e = bpy.data.objects.new("%s_Cav_%s%s" % (tipo, lado, ponta), None); col.objects.link(e); e.empty_display_size = 0.3
                alvos[(tipo, lado + ponta)] = e
            pb = ra.pose.bones[lado + "Lower" + parte]
            c = pb.constraints.new("IK"); c.target = alvos[("IK", lado + ponta)]; c.pole_target = alvos[("Polo", lado + ponta)]
            c.chain_count = 2; c.use_tail = True; c.pole_angle = 0.0
            cr = ra.pose.bones[lado + ponta].constraints.new("COPY_ROTATION"); cr.target = alvos[("IK", lado + ponta)]
    for pb in ra.pose.bones: pb.rotation_mode = "QUATERNION"
    return ra, ob, alvos

def rot_arm(ra, nome, eixos):
    """rotacao em eixos da armadura (X, Y, Z do manequim) convertida para o espaco local do osso (como no crocodilo)"""
    r = ra.data.bones[nome].matrix_local.to_3x3(); q = M.Identity(3)
    for eixo, ang in eixos: q = M.Rotation(math.radians(ang), 3, eixo) @ q
    return (r.inverted() @ q @ r).to_quaternion()

def zerar(ra):
    for pb in ra.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)

def por_pelve(ra, Mw):
    """coloca a JUNTA DO QUADRIL (cabeca do LowerTorso) na matriz de mundo Mw (rotacao = orientacao do corpo)"""
    Mr = ra.matrix_world.inverted() @ Mw @ M.Translation(V((0, 0, 0)))
    bl = ra.data.bones["LowerTorso"].matrix_local
    ra.pose.bones["LowerTorso"].matrix = Mr @ M.Translation(-V(PARTES["LowerTorso"][1])) @ bl

def alvo(alvos, tipo, ponta, Mw):
    e = alvos[(tipo, ponta)]; e.matrix_world = Mw

# ------------------------------------------------------------------ assento (referencial do dorso do crocodilo)
OSSO_ASSENTO = "Coluna1"
ASSENTO_Y = -4.6               # entre as cristas do ombro (y -6..-8) e o quadril; perto do pivo de giro (y -4,2)
def assento_mundo(croc, z_quadril):
    """matriz de mundo do quadril do cavaleiro sentado: preso ao osso do dorso (como um Attachment soldado ao osso no jogo)"""
    pb = croc.pose.bones[OSSO_ASSENTO]; bl = croc.data.bones[OSSO_ASSENTO].matrix_local
    return croc.matrix_world @ pb.matrix @ bl.inverted() @ M.Translation(V((0, ASSENTO_Y, z_quadril)))

def criar_sela(croc, croc_malha, colecao=None, meia_x=1.2, meia_y=1.15, esp=0.22, folga=0.04):
    """volume de apoio PROPOSTA: placa que copia o dorso NA POSE DE DESCANSO (raio de cima para baixo) + espessura; presa
    rigida ao mesmo osso do assento. Sem fivelas, correias ou acabamento: so estudo de encaixe."""
    col = colecao or bpy.context.scene.collection
    dg = bpy.context.evaluated_depsgraph_get(); bvh = BVHTree.FromObject(croc_malha, dg)
    nx, ny = 13, 11; xs = np.linspace(-meia_x, meia_x, nx); ys = np.linspace(ASSENTO_Y - meia_y, ASSENTO_Y + meia_y, ny)
    base = np.zeros((ny, nx))
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            p = croc_malha.matrix_world.inverted() @ V((x, y, 12.0)); hit = bvh.ray_cast(p, V((0, 0, -1)))
            base[j, i] = (croc_malha.matrix_world @ hit[0]).z if hit[0] else 4.5
    # fundo apoia nos pontos mais altos (cristas e coluna) em janela 3x3; topo suave
    from numpy.lib.stride_tricks import sliding_window_view as sw
    alto = sw(np.pad(base, 1, mode="edge"), (3, 3)).max((-1, -2)) + folga
    topo = sw(np.pad(alto, 2, mode="edge"), (5, 5)).mean((-1, -2)); topo = np.maximum(topo, alto) + esp
    vs = [(x, y, alto[j, i]) for j, y in enumerate(ys) for i, x in enumerate(xs)] + [(x, y, topo[j, i]) for j, y in enumerate(ys) for i, x in enumerate(xs)]
    n = nx * ny; fs = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i; fs.append((a, a + nx, a + nx + 1, a + 1)); fs.append((a + n, a + 1 + n, a + nx + 1 + n, a + nx + n))
    borda = ([i for i in range(nx)] + [j * nx + nx - 1 for j in range(1, ny)] + [(ny - 1) * nx + i for i in range(nx - 2, -1, -1)]
             + [j * nx for j in range(ny - 2, 0, -1)])
    for a, b in zip(borda, borda[1:] + borda[:1]): fs.append((a, b, b + n, a + n))
    me = bpy.data.meshes.new("TESTE_Sela_PROPOSTA"); me.from_pydata(vs, [], fs); me.update()
    import bmesh; bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("TESTE_Sela_PROPOSTA", me); col.objects.link(ob)
    mt = bpy.data.materials.new("TESTE_M_Sela_PROPOSTA"); mt.use_nodes = True; b = mt.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.85, 0.55, 0.10, 1); b.inputs["Roughness"].default_value = 0.8; me.materials.append(mt)
    # preso ao osso: matriz de descanso do osso guardada; posicionada a cada quadro por segue_osso()
    ob["osso"] = OSSO_ASSENTO
    return ob, float(topo[ny // 2, nx // 2]), float(topo.max()), float(alto.max())

def segue_osso(ob, croc):
    """objeto rigido preso ao osso (em vez de parentesco: o render move a armadura no mundo a cada quadro)"""
    pb = croc.pose.bones[ob["osso"]]; bl = croc.data.bones[ob["osso"]].matrix_local
    ob.matrix_world = croc.matrix_world @ pb.matrix @ bl.inverted()

# ------------------------------------------------------------------ pose sentada (relativa ao quadril; pernas abertas sobre o dorso)
SENTADO = {   # alvo/polo em coordenadas do quadril (frente -Y); x positivo = lado esquerdo do cavaleiro
    ("IK", "LeftFoot"): (1.15, -0.75, -0.75), ("Polo", "LeftFoot"): (2.0, -1.5, 2.0),
    ("IK", "RightFoot"): (-1.15, -0.75, -0.75), ("Polo", "RightFoot"): (-2.0, -1.5, 2.0),
    ("IK", "LeftHand"): (1.05, -0.65, 0.60), ("Polo", "LeftHand"): (2.6, 1.5, 1.2),
    ("IK", "RightHand"): (-1.05, -0.65, 0.60), ("Polo", "RightHand"): (-2.6, 1.5, 1.2),
}
GIRO_PE = {"Foot": (20.0, 0.0), "Hand": (-60.0, 0.0)}   # arfagem: dedos do pe para baixo / mao para a frente
X = V((1, 0, 0)); Zv = V((0, 0, 1))
def estado_sentado(Mq, inclina=8.0, cabeca=-5.0):
    """estado do manequim sentado: Mq = matriz de mundo do quadril (assento). Alvos = (posicao, orientacao da ponta)"""
    est = {"pelve": Mq.copy(), "tronco": inclina, "cabeca": cabeca, "alvos": {}}
    R = Mq.to_quaternion()
    for (tipo, ponta), p in SENTADO.items():
        base = V((0.5 if "Left" in ponta else -0.5, 0, 0)) if "Foot" in ponta else V()
        est["alvos"][(tipo, ponta)] = (Mq @ (base + V(p)), R @ Q(X, math.radians(GIRO_PE["Foot" if "Foot" in ponta else "Hand"][0])))
    return est
def mistura(ea, eb, w):
    """mistura de estados (posicoes lineares, rotacoes esfericas); w = 0 -> ea, 1 -> eb"""
    def mm(a, b):
        t = a.to_translation().lerp(b.to_translation(), w); q = a.to_quaternion().slerp(b.to_quaternion(), w)
        return M.Translation(t) @ q.to_matrix().to_4x4()
    return {"pelve": mm(ea["pelve"], eb["pelve"]), "tronco": ea["tronco"] * (1 - w) + eb["tronco"] * w,
            "cabeca": ea["cabeca"] * (1 - w) + eb["cabeca"] * w,
            "alvos": {k: (ea["alvos"][k][0].lerp(eb["alvos"][k][0], w), ea["alvos"][k][1].slerp(eb["alvos"][k][1], w)) for k in ea["alvos"]}}
def aplicar(ra, alvos, est):
    zerar(ra); por_pelve(ra, est["pelve"])
    ra.pose.bones["UpperTorso"].rotation_quaternion = rot_arm(ra, "UpperTorso", [(X, est["tronco"])])
    ra.pose.bones["Head"].rotation_quaternion = rot_arm(ra, "Head", [(X, est["cabeca"])])
    for (tipo, ponta), (p, q) in est["alvos"].items():
        qr = q @ (ra.matrix_world.to_quaternion() @ ra.data.bones[ponta].matrix_local.to_quaternion())
        alvos[(tipo, ponta)].matrix_world = M.Translation(p) @ qr.to_matrix().to_4x4()
def sentado(ra, alvos, Mq, inclina=8.0, cabeca=-5.0):
    aplicar(ra, alvos, estado_sentado(Mq, inclina, cabeca))

# ------------------------------------------------------------------ medicoes
def amostras_partes(passo=0.2):
    """pontos na superficie de cada caixa (espaco de descanso), por parte"""
    out = {}
    for nm, (_, _, _, tam, cen) in PARTES.items():
        pts = []
        for ax in range(3):
            for sgn in (-1, 1):
                o = [a for a in range(3) if a != ax]
                ua = np.arange(-tam[o[0]] / 2, tam[o[0]] / 2 + 1e-6, passo); ub = np.arange(-tam[o[1]] / 2, tam[o[1]] / 2 + 1e-6, passo)
                for a in ua:
                    for b in ub:
                        p = [0, 0, 0]; p[ax] = sgn * tam[ax] / 2; p[o[0]] = a; p[o[1]] = b; pts.append([cen[i] + p[i] for i in range(3)])
        out[nm] = np.array(pts)
    return out

def bvh_croc(croc_malha):
    dg = bpy.context.evaluated_depsgraph_get(); ev = croc_malha.evaluated_get(dg); m = ev.to_mesh()
    W = croc_malha.matrix_world; vs = [W @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]
    ev.to_mesh_clear(); return BVHTree.FromPolygons(vs, fs)

def dentro(bvh, p):
    """paridade de cruzamentos em dois raios (+Z e +X): impar nos dois = dentro da malha fechada"""
    res = []
    for d in (V((0, 0, 1)), V((1, 0, 0))):
        n = 0; o = p.copy()
        for _ in range(40):
            loc, _, _, dist = bvh.ray_cast(o, d)
            if loc is None: break
            n += 1; o = loc + d * 1e-4
        res.append(n % 2 == 1)
    return res[0] and res[1]

def folgas(ra, amostras, bvh, partes=None, Minv=None, raio=6.0, passo=1):
    """menor distancia com sinal (negativa = dentro da malha) de cada parte do manequim ate a malha do bvh.
    Dentro/fora por paridade de raios (a normal do ponto mais proximo engana em garras/bordas). Minv: mundo -> espaco do bvh"""
    res = {}
    for nm, pts in amostras.items():
        if partes and nm not in partes: continue
        Mb = ra.matrix_world @ ra.pose.bones[nm].matrix @ ra.data.bones[nm].matrix_local.inverted()
        if Minv is not None: Mb = Minv @ Mb
        melhor = raio
        for p in pts[::passo]:
            w = Mb @ V(p); loc, nor, _, d = bvh.find_nearest(w, raio)
            if loc is None: continue
            s = -d if dentro(bvh, w) else d
            if s < melhor: melhor = s
        res[nm] = round(melhor, 3)
    return res
