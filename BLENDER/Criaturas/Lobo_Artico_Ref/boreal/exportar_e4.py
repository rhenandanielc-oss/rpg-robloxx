"""E4 (17/11/2026) - exporta os efeitos de gelo aprovados (E1 r8l, E2, E3) para o Import 3D do Roblox.
Conteudo do GLB (mesmas opcoes do exportar_boreal.py: Y para cima, pele 4 influencias, sem animacoes):
  * LoboArtico_Rig (so para medir o encaixe; nao e usado no lobo)
  * Espinho_01..08 (cristais r8l, soltos na posicao de REPOUSO; o Studio mede o encaixe em cada osso)
  * Casca_Gelo (casca do voo, COM pele nos ossos do lobo: liga pelo NOME no Studio)
  * Molde_Coroa_1..3 (cristal cravado, base na origem, ponta em +Z, altura 1) e Molde_Lasca_1..2 (lasca solta, comp. 1)
    -> o cliente clona, escala e orienta (coroa do pouso e lascas no ar)
  * Molde_Crosta (crosta rachada do pouso, centrada na origem, plana)
Uso: blender -b boreal/CR_LoboArtico_Boreal_E3.blend -P boreal/exportar_e4.py
Saida: boreal/export/CR_LoboArtico_GeloFX_E4.glb"""
import bpy, bmesh, os, math, random
from mathutils import Vector as V, Matrix
AQUI = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.join(AQUI, "export")
sc = bpy.context.scene; rig = bpy.data.objects["LoboArtico_Rig"]; rig.animation_data.action = None
for pb in rig.pose.bones: pb.matrix_basis.identity()
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
MAT_E = bpy.data.materials["M_Gelo_Espinho_r8"]

def cristal(bm, base, eixo, altura, raio, lados, giro):
    eixo = eixo.normalized(); a_ = eixo.orthogonal().normalized(); b_ = eixo.cross(a_)
    anel = [bm.verts.new(base + (a_ * math.cos(giro + 2 * math.pi * k / lados) + b_ * math.sin(giro + 2 * math.pi * k / lados)) * raio * (0.8 + 0.4 * ((k * 5) % 3) / 2)) for k in range(lados)]
    meio = [bm.verts.new(base + eixo * altura * 0.55 + (v.co - base) * 0.6) for v in anel]
    p1 = bm.verts.new(base + eixo * altura)
    for k in range(lados):
        k2 = (k + 1) % lados; bm.faces.new((anel[k], anel[k2], meio[k2], meio[k])); bm.faces.new((meio[k], meio[k2], p1))
    bm.faces.new(list(reversed(anel)))
def lasca(bm, c, eixo, comp, larg, giro):
    eixo = eixo.normalized(); a_ = eixo.orthogonal().normalized(); a_ = (a_ * math.cos(giro) + eixo.cross(a_) * math.sin(giro)); b_ = eixo.cross(a_)
    p = [c + eixo * comp, c - eixo * comp * 0.6, c + a_ * larg, c - a_ * larg * 0.8, c + b_ * larg * 0.35, c - b_ * larg * 0.35]
    v = [bm.verts.new(x) for x in p]
    for f in ((0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2), (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5)): bm.faces.new([v[i] for i in f])
def objeto(nome, bm, mat):
    me = bpy.data.meshes.new(nome); bm.normal_update(); bm.to_mesh(me); bm.free()
    for f in me.polygons: f.use_smooth = False
    ob = bpy.data.objects.new(nome, me); sc.collection.objects.link(ob); me.materials.append(mat); return ob

sel = [rig]
for o in [o for o in bpy.data.objects if o.name.startswith("Espinho_")]:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw; sel.append(o)
casca = bpy.data.objects["Casca_Gelo_E2"]; casca.name = "Casca_Gelo"; sel.append(casca)
moldes = []
rnd = random.Random(5)
for i in range(3):                                    # cristais da coroa: base na origem, ponta +Z, altura 1
    bm = bmesh.new(); cristal(bm, V((0, 0, 0)), V((0, 0, 1)), 1.0, 0.17, (5, 6, 5)[i], 0.7 * i)
    if i > 0: cristal(bm, V((0.12, 0.05, 0)), V((0.5, 0.2, 1)), 0.45, 0.08, 5, 1.1 * i)   # filhote
    moldes.append(objeto("Molde_Coroa_%d" % (i + 1), bm, MAT_E))
for i in range(2):                                    # lascas soltas: comprimento 1 no eixo +Z
    bm = bmesh.new(); lasca(bm, V((0, 0, 0)), V((0, 0, 1)), 0.5, 0.28 + 0.06 * i, 0.9 * i)
    moldes.append(objeto("Molde_Lasca_%d" % (i + 1), bm, MAT_E))
crosta = bpy.data.objects["Placa_Gelo_E3"]; crosta.name = "Molde_Crosta"
c0 = V((0, -0.4, 0.0)); crosta.data.transform(Matrix.Translation(-c0)); moldes.append(crosta)
for k, o in enumerate(moldes): o.location = V((12 + 3 * k, 0, 0))   # afastados do lobo (o Studio usa so a forma)
sel += moldes
bpy.ops.object.select_all(action="DESELECT")
for o in sel: o.hide_set(False); o.hide_render = False; o.select_set(True)
bpy.context.view_layer.objects.active = rig
ops = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
def kw(**d): return {k: v for k, v in d.items() if k in ops}
arq = os.path.join(EXP, "CR_LoboArtico_GeloFX_E4.glb")
bpy.ops.export_scene.gltf(filepath=arq, **kw(export_format="GLB", use_selection=True, export_yup=True, export_materials="EXPORT",
                                             export_skins=True, export_all_influences=False, export_influence_nb=4,
                                             export_def_bones=False, export_animations=False, export_morph=False))
print("EXPORT_E4_OK", arq, round(os.path.getsize(arq) / 1e6, 3), "MB", [o.name for o in sel])
