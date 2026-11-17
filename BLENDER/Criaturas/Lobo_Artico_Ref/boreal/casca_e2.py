"""E2 (17/11/2026) - VOO da referencia PREPARO/VOO/POUSO: casca de gelo vitreo facetada sobre corpo e patas + rastro de cristais.
Casca: copia da LOW_Corpo reduzida (Decimate em repouso, mantem os pesos), empurrada para fora pela normal com variacao
(facetas irregulares), sombreamento plano, Armature no mesmo rig -> acompanha qualquer clipe. Material vidro com borda ciano.
Rastro: cristais pequenos e po de gelo num cone atras do lobo (+Y), diminuindo com a distancia (no Roblox vira ParticleEmitter).
Uso: blender -b boreal/CR_LoboArtico_Boreal_r8.blend -P boreal/casca_e2.py -- [ratio=0.10] [folga=0.10]
Saidas: boreal/CR_LoboArtico_Boreal_E2.blend, boreal/export/casca_e2.json"""
import bpy, bmesh, os, sys, math, json, random
from mathutils import Vector as V
AQUI = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.join(AQUI, "export")
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
op = dict(x.split("=") for x in a if "=" in x)
RATIO = float(op.get("ratio", 0.10)); FOLGA = float(op.get("folga", 0.10))
rig = bpy.data.objects["LoboArtico_Rig"]; rig.animation_data.action = None
for pb in rig.pose.bones: pb.matrix_basis.identity()
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
corpo = bpy.data.objects["LOW_Corpo"]

# ------------------------------------------------------------------ CASCA ----------------------------------------------
casca = corpo.copy(); casca.data = corpo.data.copy(); casca.name = casca.data.name = "Casca_Gelo_E2"
bpy.context.scene.collection.objects.link(casca)
for m in list(casca.modifiers): casca.modifiers.remove(m)
dec = casca.modifiers.new("Dec", "DECIMATE"); dec.ratio = RATIO; dec.use_collapse_triangulate = True
with bpy.context.temp_override(object=casca, active_object=casca, selected_objects=[casca]):
    bpy.ops.object.modifier_apply(modifier="Dec")
bm = bmesh.new(); bm.from_mesh(casca.data); bm.normal_update(); rnd = random.Random(11)
desl = {}
for v in bm.verts:                                        # folga por vertice: facetas irregulares como placas de gelo
    desl[v.index] = v.normal * (FOLGA + rnd.uniform(-0.02, 0.05))
for v in bm.verts: v.co += desl[v.index]
bm.to_mesh(casca.data); bm.free()
for f in casca.data.polygons: f.use_smooth = False
casca.data.materials.clear()
arm = casca.modifiers.new("Armature", "ARMATURE"); arm.object = rig

MAT_C = bpy.data.materials.new("M_Gelo_Casca_E2"); MAT_C.use_nodes = True; nt = MAT_C.node_tree
pc = nt.nodes["Principled BSDF"]
pc.inputs["Base Color"].default_value = (0.70, 0.90, 1.0, 1); pc.inputs["Roughness"].default_value = 0.05
pc.inputs["Transmission Weight"].default_value = 0.9; pc.inputs["IOR"].default_value = 1.31
pc.inputs["Emission Color"].default_value = (0.25, 0.80, 1.0, 1)
lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.45
em = nt.nodes.new("ShaderNodeMath"); em.operation = "MULTIPLY"; em.inputs[1].default_value = 3.0
nt.links.new(lw.outputs["Facing"], em.inputs[0]); nt.links.new(em.outputs[0], pc.inputs["Emission Strength"])
al = nt.nodes.new("ShaderNodeMapRange"); al.inputs["To Min"].default_value = 0.10; al.inputs["To Max"].default_value = 0.75
nt.links.new(lw.outputs["Facing"], al.inputs["Value"]); nt.links.new(al.outputs["Result"], pc.inputs["Alpha"])
try: MAT_C.surface_render_method = "BLENDED"
except Exception: pass
MAT_C.use_backface_culling = True
casca.data.materials.append(MAT_C)

# ------------------------------------------------------------------ RASTRO ---------------------------------------------
MAT_E = bpy.data.materials.get("M_Gelo_Espinho_r8")
def cristal(bm, base, eixo, altura, raio, lados, giro):
    eixo = eixo.normalized(); a_ = eixo.orthogonal().normalized(); b_ = eixo.cross(a_)
    anel = [bm.verts.new(base - eixo * altura * 0.35 + (a_ * math.cos(giro + 2 * math.pi * k / lados) + b_ * math.sin(giro + 2 * math.pi * k / lados)) * raio) for k in range(lados)]
    p1 = bm.verts.new(base + eixo * altura); p0 = bm.verts.new(base - eixo * altura * 0.7)
    for k in range(lados):
        k2 = (k + 1) % lados; bm.faces.new((anel[k], anel[k2], p1)); bm.faces.new((anel[k2], anel[k], p0))
bm = bmesh.new(); rnd = random.Random(23); n_cr = 0; n_po = 0
ORIG = V((0, 2.4, 3.4))                                     # sai da anca/costas e se abre para tras (+Y)
for i in range(70):                                          # cristais
    t = rnd.random() ** 0.8; d = 0.3 + 7.5 * t; abre = 0.35 + 0.30 * d
    p = ORIG + V((rnd.gauss(0, abre * 0.6), d, rnd.gauss(0, abre * 0.5) - 0.12 * d))
    s = (0.32 - 0.26 * t) * rnd.uniform(0.6, 1.2)
    ei = V((rnd.uniform(-0.4, 0.4), 1.0, rnd.uniform(-0.3, 0.3)))           # alongados no sentido do voo
    cristal(bm, p, ei, s, s * 0.32, rnd.choice((4, 5)), rnd.random() * 6.28); n_cr += 1
for i in range(160):                                         # po de gelo (pequenos pontos brilhantes)
    t = rnd.random(); d = 0.2 + 8.5 * t; abre = 0.5 + 0.35 * d
    p = ORIG + V((rnd.gauss(0, abre * 0.6), d, rnd.gauss(0, abre * 0.5) - 0.10 * d))
    s = 0.035 + 0.04 * (1 - t); cristal(bm, p, V((0, 1, 0)), s * 1.6, s, 4, rnd.random() * 6.28); n_po += 1
me = bpy.data.meshes.new("Rastro_Gelo_E2"); bm.normal_update(); bm.to_mesh(me); bm.free()
for f in me.polygons: f.use_smooth = False
rastro = bpy.data.objects.new("Rastro_Gelo_E2", me); bpy.context.scene.collection.objects.link(rastro)
MAT_R = MAT_E.copy(); MAT_R.name = "M_Gelo_Rastro_E2"
MAT_R.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.5
for n in MAT_R.node_tree.nodes:
    if n.type == "MATH": n.inputs[1].default_value = 6.0
me.materials.append(MAT_R)
rastro.parent = rig; rastro.parent_type = "BONE"; rastro.parent_bone = "Quadril"
rastro.matrix_world = rastro.matrix_world.copy()
from mathutils import Matrix
rastro.matrix_world = Matrix.Identity(4)                    # geometria ja em coordenadas do mundo do repouso

def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
rel = {"versao": "E2", "ratio": RATIO, "folga": FOLGA, "casca_tris": tris(casca), "corpo_tris": tris(corpo),
       "rastro_cristais": n_cr, "rastro_po": n_po, "rastro_tris": tris(rastro)}
json.dump(rel, open(os.path.join(EXP, "casca_e2.json"), "w"), indent=1); print("E2", json.dumps(rel))
rig.data.pose_position = "POSE"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "CR_LoboArtico_Boreal_E2.blend")); print("CASCA_E2_OK")
