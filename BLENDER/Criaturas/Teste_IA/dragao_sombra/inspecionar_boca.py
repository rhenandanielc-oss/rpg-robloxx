"""Inspecao da BOCA do Sombrio no rig de jogo (externo e interno), fechada e aberta nos clipes reais.
Os clipes vem do rig com animacoes (mesmo esqueleto, copiados por nome); nada e salvo.
Checagens: (1) pecas soltas da cabeca (dentes, lingua) presas ao osso certo pela posicao em relacao a linha da boca;
(2) dentes/lingua atravessando a pele do rosto (boca fechada e aberta); (3) estiramento da pele da boca aberta
(arestas que crescem demais = rasgo); (4) bordas abertas na cabeca (furos). Renders: fechada e aberta, 3 vistas de fora
e 3 de dentro. Uso: blender -b rig_sem_clipes.blend -P inspecionar_boca.py -- <rig_com_clipes.blend> <saida_dir> [Clipe,...]"""
import bpy, bmesh, sys, os, math, json
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]; FONTE, OUT = a[0], os.path.abspath(a[1]); os.makedirs(OUT, exist_ok=True)
CLIPES = a[2].split(",") if len(a) > 2 else ["Rugido_Combate", "Ninho_Ameaca", "Ataque_Mordida", "Sopro_Loop"]
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
if not all("Silverwing_" + c in bpy.data.actions for c in CLIPES):
    with bpy.data.libraries.load(FONTE) as (src, dst): dst.actions = ["Silverwing_" + c for c in CLIPES + ["Parado"] if "Silverwing_" + c in src.actions]
if not A.animation_data: A.animation_data_create()
gi = {g.index: g.name for g in M.vertex_groups}
def dono(v): return gi[max(v.groups, key=lambda g: g.weight).group] if v.groups else ""
# ilhas da malha de jogo
bm = bmesh.new(); bm.from_mesh(M.data); bm.verts.ensure_lookup_table(); vis = set(); IL = []
for v in bm.verts:
    if v.index in vis: continue
    st, il = [v], []
    while st:
        x = st.pop()
        if x.index in vis: continue
        vis.add(x.index); il.append(x.index); st += [e.other_vert(x) for e in x.link_edges]
    IL.append(il)
IL.sort(key=len, reverse=True); CORPO = IL[0]
mw = M.matrix_world
H = A.matrix_world @ A.pose.bones["head"].head; ML = A.matrix_world @ A.pose.bones["mouth_lower"].head
TIP = A.matrix_world @ A.pose.bones["mouth_upper_tip"].tail
rel = {}
# (1) pecas na regiao da boca: entre a dobradica e a ponta do focinho
pecas = []
for il in IL[1:]:
    c = sum((mw @ M.data.vertices[i].co for i in il), V()) / len(il)
    if TIP.y - 0.02 < c.y < ML.y + 0.03 and abs(c.x) < 0.09 and ML.z - 0.07 < c.z < H.z + 0.06:
        donos = {}
        for i in il: d = dono(M.data.vertices[i]); donos[d] = donos.get(d, 0) + 1
        pecas.append((il, c, max(donos, key=donos.get), len(il)))
# linha da boca no eixo da cabeca: reta de ML (dobradica) ate a ponta do mouth_lower_tip
LT = A.matrix_world @ A.pose.bones["mouth_lower_tip"].tail
def z_linha(y): t = (y - ML.y) / (LT.y - ML.y); return ML.z + (LT.z - ML.z) * max(0.0, min(1.0, t))
erro_osso = []
for il, c, d, n in pecas:
    baixo = c.z < z_linha(c.y)
    if (d == "mouth_lower") != baixo and n < 400: erro_osso.append((round(c.x, 3), round(c.y, 3), round(c.z, 3), d, n))
rel["pecas_boca"] = len(pecas); rel["pecas_osso_errado"] = erro_osso
rel["por_osso"] = {}
for _, _, d, _ in pecas: rel["por_osso"][d] = rel["por_osso"].get(d, 0) + 1
# (4) bordas abertas na pele da cabeca (fora as da membrana/pecas): furos
cab = {i for i in CORPO if dono(M.data.vertices[i]) in ("head", "mouth_lower")}
bordas = [e for e in bm.edges if e.is_boundary and e.verts[0].index in cab and e.verts[1].index in cab]
rel["bordas_abertas_cabeca"] = len(bordas); bm.free()
REST = None
def pose(clipe, frac):
    act = bpy.data.actions["Silverwing_" + clipe]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = act.frame_range
    if frac is None:                                  # quadro de boca mais aberta
        best = (0, f0)
        for f in range(int(f0), int(f1) + 1):
            sc.frame_set(f); q = A.pose.bones["mouth_lower"].matrix_basis.to_quaternion()
            ang = math.degrees(2 * math.acos(min(1.0, abs(q.w))))
            if ang > best[0]: best = (ang, f)
        sc.frame_set(best[1]); return best
    f = int(round(f0 + frac * (f1 - f0))); sc.frame_set(f); return (0, f)
def medir(rotulo):
    dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
    co = [mw @ v.co for v in me.vertices]
    b2 = bmesh.new(); b2.from_mesh(me); b2.verts.ensure_lookup_table(); b2.transform(mw)
    so_corpo = set(CORPO); tira = [v for v in b2.verts if v.index not in so_corpo]
    # estiramento: arestas da pele da cabeca/boca
    est = []
    if REST is not None:
        for e in b2.edges:
            i, j = e.verts[0].index, e.verts[1].index
            if i in cab and j in cab:
                L0 = REST[(min(i, j), max(i, j))]
                if L0 > 1e-5: est.append(e.calc_length() / L0)
    bmesh.ops.delete(b2, geom=tira, context="VERTS"); tree = BVHTree.FromBMesh(b2)
    fura = []
    for il, c, d, n in pecas:
        base = min(il, key=lambda i: tree.find_nearest(co[i])[3]); k = 0
        for i in il:
            loc, nrm, _, dd = tree.find_nearest(co[i])
            if nrm is not None and (co[i] - co[base]).length > 0.006 and (co[i] - loc).dot(nrm) < -0.0015: k += 1
        if k: fura.append((d, n, k))
    b2.free(); M.evaluated_get(dg).to_mesh_clear()
    r = {"pecas_atravessando": fura}
    if est: est.sort(); r["estira_max"] = round(est[-1], 2); r["estira_p99"] = round(est[int(len(est) * 0.99)], 2); r["arestas_x2"] = sum(1 for x in est if x > 2.0)
    rel[rotulo] = r
# repouso
A.animation_data.action = None
for b in A.pose.bones: b.matrix_basis.identity()
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
b0 = bmesh.new(); b0.from_mesh(me); b0.transform(mw)
REST = {(min(e.verts[0].index, e.verts[1].index), max(e.verts[0].index, e.verts[1].index)): e.calc_length() for e in b0.edges}
b0.free(); M.evaluated_get(dg).to_mesh_clear()
medir("fechada_repouso")
# cena de render
cam = sc.camera
if cam is None:
    cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
for nm, en, rot in (("SolB", 4.5, (0.9, 0, 0.6)), ("ContraB", 2.5, (2.0, 0, 3.4)), ("Baixo", 1.5, (2.6, 0, 0.3))):
    l = bpy.data.lights.new(nm, "SUN"); l.energy = en; lo = bpy.data.objects.new(nm, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
if not sc.world: sc.world = bpy.data.worlds.new("w")
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 800, 560
def fotos(rotulo):
    # base da camera: frente = direcao real do focinho na pose (head -> ponta do maxilar), cima = Z do mundo
    h0 = A.matrix_world @ A.pose.bones["head"].head; tp = A.matrix_world @ A.pose.bones["mouth_upper_tip"].tail
    fr_ = (tp - h0).normalized(); up_ = (V((0, 0, 1)) - fr_ * fr_.z).normalized(); lado_ = fr_.cross(up_)
    L_ = (tp - h0).length
    def P(v): return h0 + (fr_ * v[0] + lado_ * v[1] + up_ * v[2]) * L_       # unidades = comprimento da cabeca
    alvo = P((0.55, 0, -0.05))
    vistas = {"fora_34": ((1.6, 1.3, 0.35), alvo, 45), "fora_lado": ((0.55, 2.6, 0.0), alvo, 45),
              "fora_frente": ((3.0, 0.0, 0.05), alvo, 50), "dentro_frente": ((2.2, 0.0, 0.0), P((0.35, 0, -0.10)), 32),
              "dentro_baixo": ((1.9, 0.35, -0.85), P((0.4, 0, -0.08)), 32), "dentro_canto": ((1.1, 1.0, -0.15), P((0.4, 0, -0.10)), 34)}
    for nome, (p, t, lente) in vistas.items():
        cam.location = P(p); cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lente
        cam.data.clip_start = 0.005
        sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (rotulo, nome)); bpy.ops.render.render(write_still=True)
fotos("fechada")
for c in CLIPES:
    if "Silverwing_" + c not in bpy.data.actions: rel["falta_" + c] = True; continue
    ang, f = pose(c, None); medir("%s_aberta" % c); rel["%s_aberta" % c]["angulo"] = round(ang, 1); rel["%s_aberta" % c]["quadro"] = f
    if c == CLIPES[0]: fotos("aberta")
json.dump(rel, open(os.path.join(OUT, "boca.json"), "w"), indent=1)
print("BOCA", json.dumps(rel))
