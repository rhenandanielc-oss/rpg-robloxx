"""QA dos clipes do jogo nas malhas por idade (19/11/2026). Carrega as acoes de anim_v42b (+ ataque v43r5) no .blend da idade
e mede, por clipe, o ponto mais baixo da malha do corpo (afundar < -0,05 = entra no chao) e o ponto mais baixo das 4 patas
nos quadros de apoio (flutuar = pata mais baixa > 0,08 acima do chao em clipes de pe). Renderiza 4 poses de perfil.
Uso: blender -b idades_v1/export/CR_LoboArtico_<Idade>.blend -P qa_idades_v1.py -- <Idade> <saida>"""
import bpy, sys, os, json, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; IDADE = a[0]; OUT = os.path.abspath(a[1]); os.makedirs(OUT, exist_ok=True)
BASE = os.path.join(os.path.dirname(bpy.data.filepath), "..", "..", "anim_v42b", "CR_LoboArtico_Anim.blend")
CLIPES = ["Repouso", "Andar", "Trote", "Corrida", "Arrancada", "Frenagem", "Deitar", "Descanso", "Dormindo", "Sentado", "Farejando",
          "Comendo", "Bebendo", "Uivando", "Sacudir", "CometaPreparar", "CometaPouso", "AvalancheCorrida", "AvalancheOnda"]
with bpy.data.libraries.load(os.path.abspath(BASE), link=False) as (src, dst):
    dst.actions = [n for n in src.actions if n in CLIPES]
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; ARM.animation_data_create()
corpo = bpy.data.objects["LOW_Corpo"]
TRI_RAIZ = "Raiz" in json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "idade_%s.json" % IDADE)))["ossos_garantidos"]
DEITADOS = {"Deitar", "Descanso", "Dormindo", "Sentado"}
def usar(n):
    ac = bpy.data.actions[n]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    return ac
def zmin_corpo():
    dg = bpy.context.evaluated_depsgraph_get(); ev = corpo.evaluated_get(dg); me = ev.to_mesh()
    n = len(me.vertices) - (3 if TRI_RAIZ else 0)     # ignora o triangulo de ancoragem do osso Raiz (fica abaixo do chao)
    z = min((ev.matrix_world @ me.vertices[i].co).z for i in range(n)); ev.to_mesh_clear(); return z
def patas():
    P = ARM.pose.bones; W = ARM.matrix_world
    return [(W @ P[n].tail).z for n in ("Dedos_E", "Dedos_D", "DedosPe_E", "DedosPe_D")]
res = {}
for n in CLIPES:
    if n not in bpy.data.actions: continue
    ac = usar(n); f0, f1 = int(ac.frame_range[0]), int(ac.frame_range[1]); passo = max(1, (f1 - f0) // 12)
    zc, zp_min, zp_max_apoio = 9, 9, -9
    for q in range(f0, f1 + 1, passo):
        sc.frame_set(q); bpy.context.view_layer.update()
        zc = min(zc, zmin_corpo()); p = patas(); zp_min = min(zp_min, min(p)); zp_max_apoio = max(zp_max_apoio, min(p))
    res[n] = {"corpo_min": round(zc, 3), "pata_min": round(zp_min, 3), "pata_mais_baixa_max": round(zp_max_apoio, 3)}
    print("QA_IDADE", IDADE, n, json.dumps(res[n]), flush=True)
json.dump(res, open(os.path.join(OUT, "qa_%s.json" % IDADE), "w"), indent=0)
# renders de perfil: Repouso, Corrida, Deitar (fim), Sentado
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y = 420, 300
try: sc.eevee.taa_render_samples = 8
except Exception: pass
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.36, 0.42, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.002)); ch = bpy.context.object
mc = bpy.data.materials.new("Chao"); mc.use_nodes = True; mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.52, 0.55, 1); ch.data.materials.append(mc)
for nome, loc, en, sz in (("Chave", (9, -6, 12), 2200, 8), ("Recorte", (-8, 8, 9), 900, 6)):
    ld = bpy.data.lights.new(nome, "AREA"); ld.energy = en; ld.size = sz; lo = bpy.data.objects.new(nome, ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = (V((0, 0, 3)) - V(loc)).to_track_quat("-Z", "Y").to_euler()
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (17, -1.5, 3.4); cam.rotation_euler = (V((0, -1.5, 2.6)) - cam.location).to_track_quat("-Z", "Y").to_euler(); cd.lens = 50
try: sc.view_settings.view_transform = "AgX"
except Exception: pass
for n, qual in (("Repouso", 0), ("Corrida", 4), ("Deitar", -1), ("Sentado", 0)):
    if n not in bpy.data.actions: continue
    ac = usar(n); q = int(ac.frame_range[1]) if qual < 0 else qual; sc.frame_set(q)
    sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (IDADE, n)); bpy.ops.render.render(write_still=True)
print("QA_IDADES_OK", IDADE, flush=True)
