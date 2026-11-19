"""Proposta visual das 5 idades do Lobo Artico (19/11/2026, pedido: "quero diferencas no visual do bebe-jovem-preadulto-
adulto-anciao"). PROTOTIPO: so pose dos ossos (escala por osso) + tinta da pelagem + tamanho dos cristais, sobre o modelo
aprovado (anim_v42b). Nao altera o .blend (nao salva). Se aprovado, cada idade vira malha propria (pose aplicada como
repouso, mesmos nomes de osso) para o Roblox.
Base real (lobo-artico): filhotes nascem escuros (cinza-acastanhado) e clareiam com a idade; cabeca grande, focinho curto,
orelhas e patas grandes, cauda curta; o jovem e pernalta e magro; o anciao engrossa pescoco/juba e baixa a cabeca.
Fantasia (proposta): os cristais do dorso nascem no Jovem e crescem com a idade; a Marca acende a partir do Jovem.
Uso: blender -b anim_v42b/CR_LoboArtico_Anim.blend -P idades_v1.py -- <saida>"""
import bpy, sys, os, math, bmesh
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; rig = bpy.data.objects["LoboArtico_Rig"]; P = rig.pose.bones
for o in sc.objects:
    if o.type == "MESH" and o.name.startswith(("LOD1", "LOD2")): o.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y = 560, 400
try: sc.eevee.taa_render_samples = 12
except Exception: pass
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.36, 0.42, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, -0.002)); ch = bpy.context.object
mc = bpy.data.materials.new("Chao"); mc.use_nodes = True; mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.52, 0.55, 1); ch.data.materials.append(mc)
for nome, loc, en, sz in (("Chave", (9, -6, 12), 2200, 8), ("Recorte", (-8, 8, 9), 900, 6), ("Frente", (2, -16, 6), 600, 6)):
    ld = bpy.data.lights.new(nome, "AREA"); ld.energy = en; ld.size = sz; lo = bpy.data.objects.new(nome, ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = (V((0, 0, 3)) - V(loc)).to_track_quat("-Z", "Y").to_euler()
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
try: sc.view_settings.view_transform = "AgX"
except Exception: pass

# escala de um osso NAO passa aos filhos (senao 3 segmentos de coluna a 0,85 encolhem a frente toda: 0,85^3); a posicao
# dos filhos continua seguindo o comprimento do pai
for bo in rig.data.bones: bo.inherit_scale = "NONE"
# --- pose de repouso (Repouso q0) ------------------------------------------------------------------------------------
ac = bpy.data.actions.get("Repouso")
rig.animation_data_create(); rig.animation_data.action = ac
if ac and len(ac.slots): rig.animation_data.action_slot = ac.slots[0]
sc.frame_set(0); bpy.context.view_layer.update()
BASE = {pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P}
rig.animation_data.action = None

# --- tinta da pelagem: multiplica a cor da textura (Corpo, Cabeca, Pelagem) ---------------------------------------------
MIX = {}
for mn in ("M_LoboArtico_Corpo_LOW", "M_LoboArtico_Cabeca_LOW", "M_LoboArtico_Pelagem_LOW"):
    m = bpy.data.materials[mn]; nt = m.node_tree; bs = nt.nodes["Principled BSDF"]
    lk = bs.inputs["Base Color"].links
    if not lk: continue
    src = lk[0].from_socket
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
    nt.links.new(src, mx.inputs[6]); nt.links.new(mx.outputs[2], bs.inputs["Base Color"])
    MIX[mn] = mx

# --- cristais: escala de cada cristal em torno da propria base (ilhas da malha, no repouso) -------------------------------
cri = bpy.data.objects.get("LOW_Cristais")
ORIG = [v.co.copy() for v in cri.data.vertices] if cri else []
ILHAS = []
if cri:
    bm = bmesh.new(); bm.from_mesh(cri.data); bm.verts.ensure_lookup_table(); vistos = set()
    for v in bm.verts:
        if v.index in vistos: continue
        pilha = [v]; ilha = []
        while pilha:
            x = pilha.pop()
            if x.index in vistos: continue
            vistos.add(x.index); ilha.append(x.index)
            for e in x.link_edges: pilha.append(e.other_vert(x))
        zs = [ORIG[i].z for i in ilha]; base = sum((ORIG[i] for i in ilha), V()) / len(ilha); base.z = min(zs)
        ILHAS.append((ilha, base))
    bm.free()
def cristais(f):
    if not cri: return
    cri.hide_render = f <= 0.01
    for ilha, base in ILHAS:
        for i in ilha: cri.data.vertices[i].co = base + (ORIG[i] - base) * max(f, 0.01)
    cri.data.update()

# --- idades ------------------------------------------------------------------------------------------------------------
# s = escala por osso (x, y, z no espaco do osso; y = comprimento). rot = graus extras em X (+ baixa a frente).
PERNAS = ("Umero", "Antebraco", "Coxa", "Tibia")
def idade(cab, cab_y, orelha, perna, pata, cauda, corpo_y, pesc_xz=1.0, pesc_y=1.0, rot_pesc=0.0):
    s = {"Cabeca": (cab, cab_y, cab), "Orelha_E": (orelha,) * 3, "Orelha_D": (orelha,) * 3,
         "Cauda1": (1, cauda, 1), "Cauda2": (1, cauda, 1), "Cauda3": (1, cauda, 1), "Cauda4": (1, cauda, 1),
         "Coluna1": (1, corpo_y, 1), "Coluna2": (1, corpo_y, 1), "Coluna3": (1, corpo_y, 1),
         "Pescoco1": (pesc_xz, pesc_y, pesc_xz), "Pescoco2": (pesc_xz, pesc_y, pesc_xz)}
    for l in ("E", "D"):
        for n in PERNAS: s[n + "_" + l] = (1, perna, 1)
        s["Dedos_" + l] = (pata,) * 3; s["DedosPe_" + l] = (pata,) * 3
    return s, rot_pesc
IDADES = [  # nome, escala no jogo, proporcoes, tinta (multiplica), cristais, marca
    ("Filhote",    0.40, idade(1.30, 0.90, 1.30, 0.80, 1.32, 0.60, 0.85, pesc_y=0.75), (0.30, 0.27, 0.25), 0.0, False),
    ("Jovem",      0.65, idade(1.14, 1.00, 1.16, 1.08, 1.14, 0.84, 0.93, pesc_y=0.95), (0.58, 0.57, 0.56), 0.45, True),
    ("Pre-adulto", 0.85, idade(1.05, 1.01, 1.05, 1.03, 1.04, 0.95, 0.98), (0.84, 0.84, 0.84), 0.75, True),
    ("Adulto",     1.00, idade(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0), 1.0, True),
    ("Anciao",     1.10, idade(1.0, 1.0, 0.97, 0.99, 1.0, 1.0, 1.0, pesc_xz=1.16, rot_pesc=10.0), (1.0, 0.91, 0.76), 1.35, True),
]
corpo = bpy.data.objects["LOW_Corpo"]
def chao_min():
    dg = bpy.context.evaluated_depsgraph_get(); ev = corpo.evaluated_get(dg); me = ev.to_mesh()
    z = min((ev.matrix_world @ v.co).z for v in me.vertices); ev.to_mesh_clear(); return z
for pb in P: pb.rotation_quaternion, pb.location = BASE[pb.name]; pb.scale = (1, 1, 1)
rig.location = (0, 0, 0); rig.scale = (1, 1, 1); bpy.context.view_layer.update()
Z0 = chao_min()
from mathutils import Quaternion
def aplicar(prop):
    s, rot = prop
    for pb in P:
        pb.rotation_quaternion, pb.location = BASE[pb.name]; pb.scale = s.get(pb.name, (1, 1, 1))
    if rot:
        q = Quaternion((1, 0, 0), math.radians(rot))
        P["Pescoco1"].rotation_quaternion = BASE["Pescoco1"][0] @ q
    bpy.context.view_layer.update()
def caixa():
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in (corpo, bpy.data.objects["LOW_Cabeca"], bpy.data.objects["LOW_Pelagem"]):
        ev = o.evaluated_get(dg); me = ev.to_mesh(); pts += [ev.matrix_world @ v.co for v in list(me.vertices)[::7]]; ev.to_mesh_clear()
    mn = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx
def olhar(pos, alvo, lente=50):
    cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
def render(nome):
    sc.render.filepath = os.path.join(OUT, nome); bpy.ops.render.render(write_still=True)
marca = bpy.data.objects.get("LOW_Marca")
# enquadramento unico = o do Adulto (pose base, escala 1): as idades ficam comparaveis lado a lado
aplicar(IDADES[3][2]); rig.scale = (1, 1, 1); rig.location = (0, 0, 0); bpy.context.view_layer.update()
_a0, _a1 = caixa(); ADULTO_CX = ((_a0 + _a1) / 2, max(_a1.y - _a0.y, _a1.z - _a0.z) * 1.08)
for nome, esc, prop, tinta, cr, mk in IDADES:
    aplicar(prop)
    for mx in MIX.values(): mx.inputs[7].default_value = (*tinta, 1)
    cristais(cr)
    if marca: marca.hide_render = not mk
    rig.scale = (1, 1, 1); rig.location = (0, 0, 0); bpy.context.view_layer.update()
    rig.location.z = Z0 - chao_min(); bpy.context.view_layer.update()    # patas no chao
    c, L = ADULTO_CX; mn = c - V((0, L / 2, L / 2))
    # proporcoes (tamanho normalizado): perfil e 3/4 de frente
    olhar(c + V((L * 1.55, 0, L * 0.10)), c, 50); render("%s_perfil.png" % nome)
    olhar(c + V((L * 0.95, -L * 1.05, L * 0.30)), c + V((0, -L * 0.2, L * 0.05)), 50); render("%s_34.png" % nome)
    olhar(c + V((L * 0.45, -L * 0.75, L * 0.12)), V((c.x, mn.y + L * 0.12, c.z + L * 0.18)), 50); render("%s_cabeca.png" % nome)
    # fila no tamanho do jogo: escala do objeto, camera fixa do Adulto
    if ADULTO_CX is None:                       # camera fixa = enquadramento do Adulto (pose base, escala 1)
        aplicar(IDADES[3][2]); rig.scale = (1, 1, 1); rig.location = (0, 0, 0); bpy.context.view_layer.update()
        a0, a1 = caixa(); ADULTO_CX = ((a0 + a1) / 2, max(a1.y - a0.y, a1.z - a0.z)); aplicar(prop)
    rig.scale = (esc,) * 3; rig.location = (0, 0, 0); bpy.context.view_layer.update()
    rig.location.z = Z0 - chao_min(); bpy.context.view_layer.update()
    ca, La = ADULTO_CX
    olhar(V((ca.x + La * 1.75, ca.y, La * 0.35)), V((ca.x, ca.y, La * 0.28)), 50); render("%s_fila.png" % nome)
    print("IDADE_OK", nome, flush=True)
print("IDADES_V1_OK", flush=True)
