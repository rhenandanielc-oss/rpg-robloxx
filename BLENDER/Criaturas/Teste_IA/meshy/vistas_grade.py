"""Vistas ortograficas do Silverwing_20k com grade de 0.05 (linhas grossas a cada 0.1) e opcionalmente as juntas
de um JSON {nome: [x,y,z]} como esferas + ligacoes pai->filho. Workbench X-ray para enxergar o interior.
Uso: blender -b -P vistas_grade.py -- malha.glb pasta_saida [juntas.json] [prefixo]"""
import bpy, sys, os, json, math
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
glb, out = args[0], args[1]; juntas = args[2] if len(args) > 2 and args[2] != "-" else None
pref = args[3] if len(args) > 3 else "grade"
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc = bpy.context.scene; col = sc.collection
mesh = [o for o in bpy.data.objects if o.type == "MESH"][0]
mn = Vector([min((mesh.matrix_world @ v.co)[i] for v in mesh.data.vertices) for i in range(3)])
mx = Vector([max((mesh.matrix_world @ v.co)[i] for v in mesh.data.vertices) for i in range(3)])
print("BBOX", tuple(round(c, 3) for c in mn), tuple(round(c, 3) for c in mx))

def mat(nome, cor):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome); m.diffuse_color = cor; return m
def caixa(nome, centro, tam, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centro); o = bpy.context.object; o.name = nome
    o.scale = tam; o.data.materials.append(m); return o
mg, mgf = mat("grade", (0.2, 0.9, 1.0, 1)), mat("gradef", (0.1, 0.35, 0.45, 1))
# grades em 3 planos atras do modelo (frente: plano y=+1; lado: plano x=-1.2; topo: plano z=-0.1)
L = 1.2
for i in range(-24, 25):
    v = i * 0.05; m = mg if i % 2 == 0 else mgf; e = 0.003 if i % 2 == 0 else 0.0015
    caixa("gf_v", (v, 0.9, 0.6), (e, 0.001, 2.0), m); caixa("gf_h", (0, 0.9, v + 0.6 if False else v), (2.4, 0.001, e), m)
    caixa("gl_v", (-1.1, v, 0.6), (0.001, e, 2.0), m); caixa("gl_h", (-1.1, 0, v), (0.001, 2.4, e), m)
    caixa("gt_v", (v, 0, -0.3), (e, 2.4, 0.001), m); caixa("gt_h", (0, v, -0.3), (2.4, e, 0.001), m)
if juntas:
    J = json.load(open(juntas))
    mj, ml = mat("junta", (1, 0.15, 0.1, 1)), mat("liga", (1, 0.9, 0.1, 1))
    for n, d in J["juntas"].items():
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=d); bpy.context.object.data.materials.append(mj)
    for a, b in J.get("ligacoes", []):
        pa, pb = Vector(J["juntas"][a]), Vector(J["juntas"][b]); d = pb - pa
        if d.length < 1e-4: continue
        bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=d.length, location=(pa + pb) / 2)
        o = bpy.context.object; o.rotation_euler = d.to_track_quat("Z", "Y").to_euler(); o.data.materials.append(ml)
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading
sh.light = "STUDIO"; sh.color_type = "MATERIAL"; sh.show_xray = True; sh.xray_alpha = 0.55
sc.render.resolution_x = sc.render.resolution_y = 1100
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); col.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
vistas = {"frente": ((0, -3, 0.55), (math.pi / 2, 0, 0), 2.0), "lado": ((3, 0, 0.55), (math.pi / 2, 0, math.pi / 2), 2.0),
          "topo": ((0, 0, 3), (0, 0, 0), 2.0)}
for nome, (loc, rot, s) in vistas.items():
    cam.location = loc; cam.rotation_euler = rot; cam.data.ortho_scale = s
    sc.render.filepath = os.path.join(out, "%s_%s.png" % (pref, nome)); bpy.ops.render.render(write_still=True)
print("VISTAS_OK  escala: 1100px = 2.0 unidades; frente centro (x=0,z=0.55), lado centro (y=0,z=0.55; +Y a direita?), topo centro (0,0)")
