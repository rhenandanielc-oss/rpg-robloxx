"""CR_UrsoSilvestre — etapa 3: malha de JOGO a partir do master (CR_Urso_master.blend).
- Corpo LOW: pele decimada + dentes/lingua/olhos/garras reduzidos, numa so malha e UV unica; cor e normal assadas
  do master (Cycles, selecionado->ativo) em 1024.
- Pelo: cartoes do master divididos em 2 malhas (<= 20k cada) + LOD1 (55% das mechas, mais largas).
- Vegetacao (alfa) e Casca+cipo (opaco) com o atlas T_Urso_Veg (1024).
- Exporta GLB (sem rig: o rig vem depois da aprovacao) e grava medidas/triangulos em low/relatorio_low.txt.
Uso: blender -b CR_Urso_master.blend -P low_urso.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector as V
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
AQUI = os.path.dirname(os.path.abspath(__file__)); TEX = os.path.join(AQUI, "tex")
sc = bpy.context.scene; rnd = random.Random(5)
ALVO_CORPO, ALVO_DET = 11000, 3000
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
def copia(o, nome):
    c = o.copy(); c.data = o.data.copy(); c.name = nome; c.data.name = nome; sc.collection.objects.link(c); return c
def aplicar_mods(o):
    ativar(o)
    for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
def decimar(o, alvo):
    ativar(o); r = min(1.0, alvo / max(1, tris(o)))
    d = o.modifiers.new("Dec", "DECIMATE"); d.decimate_type = "COLLAPSE"; d.ratio = r; d.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=d.name)
    t = o.modifiers.new("Tri", "TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=t.name)

CORPO = bpy.data.objects["CR_Urso_Corpo"]
RIGIDAS = [o for o in bpy.data.objects if o.type == "MESH" and o.name.split(".")[0] in ("Dente_Sup", "Dente_Inf", "Garra", "Olho", "Lingua")]
for o in RIGIDAS: aplicar_mods(o)
# ------------------------------------------------------------------ corpo LOW
low = copia(CORPO, "Urso_Corpo"); low.data.materials.clear()
decimar(low, ALVO_CORPO)
det = []
for o in RIGIDAS:
    c = copia(o, "tmp_" + o.name); c.data.materials.clear(); ativar(c); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); det.append(c)
olhos = [c for c in det if c.name.startswith("tmp_Olho")]; det = [c for c in det if c not in olhos]
ativar(det[0])
for c in det: c.select_set(True)
bpy.ops.object.join(); dj = bpy.context.object; decimar(dj, ALVO_DET)          # garras/dentes/lingua reduzidos; olhos inteiros
ativar(low); dj.select_set(True)
for c in olhos: c.select_set(True)
bpy.ops.object.join(); low = bpy.context.object; low.name = "Urso_Corpo"
for p in low.data.polygons: p.use_smooth = True
# UV unica
ativar(low); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004, area_weight=0.0)
bpy.ops.uv.pack_islands(margin=0.003); bpy.ops.object.mode_set(mode="OBJECT")
# ------------------------------------------------------------------ bake cor + normal (master -> LOW)
img_c = bpy.data.images.new("T_Urso_Corpo_Cor", 1024, 1024); img_n = bpy.data.images.new("T_Urso_Corpo_Normal", 1024, 1024)
img_n.colorspace_settings.name = "Non-Color"
mat = bpy.data.materials.new("M_Urso_Corpo"); mat.use_nodes = True; nt = mat.node_tree; b = nt.nodes["Principled BSDF"]
tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = img_c
tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img_n
nm = nt.nodes.new("ShaderNodeNormalMap"); b.inputs["Roughness"].default_value = 0.8
low.data.materials.append(mat)
sc.render.engine = "CYCLES"; sc.cycles.samples = 4; sc.cycles.device = "CPU"
sc.render.bake.use_selected_to_active = True; sc.render.bake.cage_extrusion = 0.08; sc.render.bake.max_ray_distance = 0.25
sc.render.bake.margin = 10
for o in sc.objects: o.select_set(False)
for o in [CORPO] + RIGIDAS: o.select_set(True)
low.select_set(True); bpy.context.view_layer.objects.active = low
nt.nodes.active = tc
bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"})
img_c.filepath_raw = os.path.join(OUT, "T_Urso_Corpo_Cor.png"); img_c.file_format = "PNG"; img_c.save()
nt.nodes.active = tn
bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")
img_n.filepath_raw = os.path.join(OUT, "T_Urso_Corpo_Normal.png"); img_n.file_format = "PNG"; img_n.save()
nt.links.new(tc.outputs["Color"], b.inputs["Base Color"]); nt.links.new(tn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs[0], b.inputs["Normal"])

# ------------------------------------------------------------------ pelo: 2 malhas (frente/tras) + LOD1
PELO = bpy.data.objects["CR_Urso_Pelo"]
def mechas(o):
    """cada mecha = 6 faces consecutivas (pelo_urso.py)"""
    return [list(range(i, i + 6)) for i in range(0, len(o.data.polygons), 6)]
def sub_malha(o, grupos, nome, escala=1.0):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    manter = set(i for g in grupos for i in g)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in manter], context="FACES")
    if escala != 1.0:                                   # LOD: alarga cada mecha em torno do eixo central
        for f_ in bm.faces: pass
    m = bpy.data.meshes.new(nome); bm.to_mesh(m); bm.free()
    ob = bpy.data.objects.new(nome, m); sc.collection.objects.link(ob); ob.data.materials.append(o.data.materials[0])
    if escala != 1.0:
        bm2 = bmesh.new(); bm2.from_mesh(m); bm2.verts.ensure_lookup_table()
        # 3 verts por anel (esq, centro, dir): afasta esq/dir do centro
        for i in range(0, len(bm2.verts), 3):
            if i + 2 >= len(bm2.verts): break
            a_, c_, d_ = bm2.verts[i], bm2.verts[i + 1], bm2.verts[i + 2]
            a_.co = c_.co + (a_.co - c_.co) * escala; d_.co = c_.co + (d_.co - c_.co) * escala
        bm2.to_mesh(m); bm2.free()
    return ob
G = mechas(PELO)
def centro_y(g): return sum(PELO.data.polygons[i].center.y for i in g) / len(g)
G.sort(key=centro_y); meio = len(G) // 2
PELO_A = sub_malha(PELO, G[:meio], "Urso_Pelo_A"); PELO_B = sub_malha(PELO, G[meio:], "Urso_Pelo_B")
lod = [g for g in G if rnd.random() < 0.55]
PELO_L1 = sub_malha(PELO, lod, "Urso_Pelo_LOD1", escala=1.30)
# ------------------------------------------------------------------ vegetacao e casca
VEG = copia(bpy.data.objects["CR_Urso_Vegetacao"], "Urso_Vegetacao")
cas = copia(bpy.data.objects["CR_Urso_Casca"], "Urso_Casca"); cip = copia(bpy.data.objects["CR_Urso_Cipo"], "Urso_Cipo")
ativar(cas); cip.select_set(True); bpy.ops.object.join(); CASCA = bpy.context.object; CASCA.name = "Urso_Casca"
for o in (PELO_A, PELO_B, PELO_L1, VEG, CASCA):
    ativar(o); t_ = o.modifiers.new("Tri", "TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=t_.name)

# ------------------------------------------------------------------ exporta so a malha de jogo
JOGO = [low, PELO_A, PELO_B, VEG, CASCA]
for o in sc.objects: o.select_set(o in JOGO)
glb = os.path.join(OUT, "CR_Urso_Silvestre_LOW.glb")
bpy.ops.export_scene.gltf(filepath=glb, use_selection=True, export_format="GLB", export_yup=True, export_apply=True,
                          export_image_format="AUTO", export_texcoords=True, export_normals=True, export_materials="EXPORT")
for o in sc.objects: o.select_set(o is PELO_L1)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "CR_Urso_Silvestre_Pelo_LOD1.glb"), use_selection=True, export_format="GLB", export_yup=True)
# relatorio
linhas = ["malha;triangulos;material;texturas"]
TEXT = {"Urso_Corpo": "T_Urso_Corpo_Cor 1024 + T_Urso_Corpo_Normal 1024 (assadas)", "Urso_Pelo_A": "T_Urso_Pelo_Cor 1024 (alfa) + Normal 1024",
        "Urso_Pelo_B": "T_Urso_Pelo_Cor 1024 (alfa) + Normal 1024", "Urso_Pelo_LOD1": "T_Urso_Pelo (mesmas)",
        "Urso_Vegetacao": "T_Urso_Veg_Cor 1024 (alfa) + Normal 1024", "Urso_Casca": "T_Urso_Veg_Cor 1024 (regiao opaca) + Normal 1024"}
for o in JOGO + [PELO_L1]:
    linhas.append("%s;%d;%s;%s" % (o.name, tris(o), o.data.materials[0].name if o.data.materials else "-", TEXT[o.name]))
total = sum(tris(o) for o in JOGO)
linhas.append("TOTAL_LOD0;%d;;" % total)
linhas.append("TOTAL_LOD1 (pelo LOD1 no lugar de A+B);%d;;" % (total - tris(PELO_A) - tris(PELO_B) + tris(PELO_L1)))
zs = [(low.matrix_world @ v.co).z for v in low.data.vertices]
omb = max((o.matrix_world @ v.co).z for o in (low, PELO_A, PELO_B) for v in o.data.vertices if -4.0 < (o.matrix_world @ v.co).y < -2.0)
ys = [(o.matrix_world @ v.co).y for o in JOGO for v in o.data.vertices]
linhas.append("medidas;ombro_com_pelo=%.2f;comprimento_total=%.2f;pe_min_z=%.3f" % (omb, max(ys) - min(ys), min(zs)))
open(os.path.join(OUT, "relatorio_low.txt"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
print("\n".join(linhas))
# cena de revisao do LOW (renders): esconde o master
for o in sc.objects:
    if o.type == "MESH" and o not in JOGO and o.name != "Chao": o.hide_render = True; o.hide_set(True)
sc.render.engine = "BLENDER_EEVEE"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Urso_LOW.blend"))
print("URSO_LOW_OK")
