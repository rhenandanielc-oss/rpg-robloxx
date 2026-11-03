"""Teste de dobra do pescoco no rig do Sombrio: gira spine_2..4 + head (baixo, tras, lado), conta vertices das cristas
(TAG de detalhe = ilhas pequenas da malha) que entram na pele do corpo e renderiza cada pose.
Uso: blender -b rig.blend -P dobra_pescoco.py -- <saida_dir>"""
import bpy, sys, os, math, bmesh
from mathutils import Vector as V, Euler
from mathutils.bvhtree import BVHTree
OUT = sys.argv[sys.argv.index("--") + 1]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
if A.animation_data: A.animation_data.action = None
gi = {g.index: g.name for g in M.vertex_groups}
POSES = {"baixo": (35, 0, 0), "tras": (-35, 0, 0), "lado": (0, 0, 45), "lado_baixo": (25, 0, 40)}
CAD = ["spine_2", "spine_3", "spine_4", "head"]
def ilhas(me):
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); vis = set(); out = []
    for v in bm.verts:
        if v.index in vis: continue
        st, il = [v], []
        while st:
            x = st.pop()
            if x.index in vis: continue
            vis.add(x.index); il.append(x.index); st += [e.other_vert(x) for e in x.link_edges]
        out.append(il)
    bm.free(); return out
IL = sorted(ilhas(M.data), key=len, reverse=True); CORPO = set(IL[0])
# cristas/espinhos do pescoco e da cabeca: ilhas pequenas cujo osso dominante e da cadeia
def dono(i):
    v = M.data.vertices[i]; return gi[max(v.groups, key=lambda g: g.weight).group] if v.groups else ""
CRISTAS = [il for il in IL[1:] if len(il) < 400 and dono(il[0]) in CAD]
print("CRISTAS", len(CRISTAS))
cam = sc.camera
if cam is None:
    cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
for nm, en, rot in (("SolT", 5.0, (0.9, 0, 0.5)), ("ContraT", 3.0, (2.0, 0, 3.4))):
    l = bpy.data.lights.new(nm, "SUN"); l.energy = en; lo = bpy.data.objects.new(nm, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 960, 540
for nome, (px, py, pz) in POSES.items():
    for b in A.pose.bones: b.rotation_mode = "XYZ"; b.rotation_euler = (0, 0, 0)
    for n in CAD: A.pose.bones[n].rotation_euler = Euler((math.radians(px / 4), math.radians(py / 4), math.radians(pz / 4)))
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    me = M.evaluated_get(dg).to_mesh(); mw = M.matrix_world
    co = [mw @ v.co for v in me.vertices]
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    tira = [v for v in bm.verts if v.index not in CORPO]; bmesh.ops.delete(bm, geom=tira, context="VERTS")
    bm.transform(mw); tree = BVHTree.FromBMesh(bm)
    dentro = 0; pecas = 0
    for il in CRISTAS:
        base = min(il, key=lambda i: tree.find_nearest(co[i])[3])   # vertice mais perto da pele = base
        n_ = 0
        for i in il:
            p = co[i]; loc, nrm, _, d = tree.find_nearest(p)
            if (p - co[base]).length > 0.03 and nrm is not None and (p - loc).dot(nrm) < -0.003: n_ += 1
        dentro += n_; pecas += n_ > 0
    print("DOBRA", nome, "vertices_dentro", dentro, "pecas_afetadas", pecas, "de", len(CRISTAS))
    bm.free(); M.evaluated_get(dg).to_mesh_clear()
    h = A.matrix_world @ A.pose.bones["head"].head
    cam.location = h + V((-1.9, 0.35, 0.25)); cam.rotation_euler = (h + V((0, 0.25, -0.15)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 40; sc.render.filepath = os.path.join(OUT, "dobra_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("DOBRA_OK")
