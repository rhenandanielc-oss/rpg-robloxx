"""
BUILD PHASE TEMPLATE
Copy this file to <asset>/build/NN_<phase>.py, fill in build(), run:

  blender --background --python build/02_blockout.py -- --master <asset>_master.blend

Every phase script is re-runnable: it opens the master, deletes what it owns
(objects whose names carry OWNER_TAG in a custom property), rebuilds them, saves.
Nothing else in the file is touched, so earlier phases and manual edits survive.

Coordinate convention: metres, Z up, subject faces -Y, origin at the ground
contact point (characters, props, architecture) or the ground centre (vehicles).
"""
import bpy, bmesh, sys, os, math, argparse
from mathutils import Vector, Matrix, Euler

PHASE = "02_blockout"          # change per phase
OWNER_TAG = "phase:" + PHASE   # objects created here get ob["owner"] = OWNER_TAG


# ARGS AND FILE HANDLING

def argv_after_dashes():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def open_master(path):
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(path))
    return bpy.context.scene


def save_master(path):
    bpy.context.preferences.filepaths.save_version = 0   # no .blend1 backups
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(path))


def col(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def clear_owned(tag=None):
    """Delete every object this phase created last time, so the script is idempotent."""
    tag = tag or OWNER_TAG
    for ob in [o for o in bpy.data.objects if o.get("owner") == tag]:
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if data is not None and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)
            elif isinstance(data, bpy.types.Armature):
                bpy.data.armatures.remove(data)


def own(ob):
    ob["owner"] = OWNER_TAG
    return ob


def log(*a):
    print("[" + PHASE + "]", *a)


# MESH PRIMITIVES (bmesh based, no operators, safe in background mode)

def new_mesh_object(name, bm, collection, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    ob.rotation_euler = rotation
    ob.scale = scale
    col(collection).objects.link(ob)
    return own(ob)


def box(name, size, collection="LOW", location=(0, 0, 0), rotation=(0, 0, 0), base_at_origin=False):
    """size = (x, y, z). base_at_origin puts the bottom face on z=0."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    if base_at_origin:
        bmesh.ops.translate(bm, vec=(0, 0, size[2] / 2), verts=bm.verts)
    return new_mesh_object(name, bm, collection, location, rotation)


def cylinder(name, radius, height, collection="LOW", segments=32, axis="Z", location=(0, 0, 0),
             radius_top=None, base_at_origin=False):
    """Cylinder or truncated cone along axis. radius_top defaults to radius."""
    bm = bmesh.new()
    r2 = radius if radius_top is None else radius_top
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=r2, depth=height)
    if base_at_origin:
        bmesh.ops.translate(bm, vec=(0, 0, height / 2), verts=bm.verts)
    if axis == "X":
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"), verts=bm.verts)
    elif axis == "Y":
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-90), 3, "X"), verts=bm.verts)
    return new_mesh_object(name, bm, collection, location)


def sphere(name, radius, collection="LOW", location=(0, 0, 0), u=24, v=12, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    return new_mesh_object(name, bm, collection, location)


def grid(name, size_x, size_y, cuts_x, cuts_y, collection="LOW", location=(0, 0, 0), rotation=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=cuts_x, y_segments=cuts_y, size=0.5)
    bmesh.ops.scale(bm, vec=(size_x, size_y, 1), verts=bm.verts)
    return new_mesh_object(name, bm, collection, location, rotation)


def loft(name, sections, collection="LOW", close_sections=True, cap_ends=True, smooth=True):
    """Bridge a list of cross sections (each a list of Vector/tuple, same point count) into a hull.
    Use it for vehicle bodies, boat hulls, torsos: read section widths/heights off the top and side
    reference views at fixed stations along the length."""
    bm = bmesh.new()
    rings = []
    for sec in sections:
        vs = [bm.verts.new(Vector(p)) for p in sec]
        ring = []
        for i in range(len(vs)):
            if i == len(vs) - 1 and not close_sections:
                break
            ring.append(bm.edges.new((vs[i], vs[(i + 1) % len(vs)])))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        bmesh.ops.bridge_loops(bm, edges=a + b)
    if cap_ends and close_sections:
        bmesh.ops.contextual_create(bm, geom=rings[0])
        bmesh.ops.contextual_create(bm, geom=rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_mesh_object(name, bm, collection)
    if smooth:
        shade_smooth(ob, math.radians(35))
    return ob


def profile_spin(name, profile_xz, collection="LOW", steps=32, location=(0, 0, 0), angle=360):
    """Lathe a 2D profile (list of (radius, z)) around Z: vases, columns, wheel rims, bolts."""
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0, z)) for r, z in profile_xz]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1),
                   angle=math.radians(angle), steps=steps, use_merge=(angle >= 360))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_object(name, bm, collection, location)


def profile_extrude(name, profile_xy, length, collection="LOW", location=(0, 0, 0), rotation=(0, 0, 0)):
    """Extrude a closed 2D outline (list of (x, y)) along Z: arches, mouldings, I-beams, tracks, trims."""
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, 0)) for x, y in profile_xy]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, length), verts=top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_object(name, bm, collection, location, rotation)


def curve_tube(name, points, radius, collection="LOW", resolution=12, taper_to=None, bevel_res=6):
    """Poly/bezier tube through points: cables, horns, tails, pipes, tentacles, railings, roots."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("NURBS")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
        if taper_to is not None:
            t = i / max(1, len(points) - 1)
            sp.points[i].radius = 1.0 + (taper_to - 1.0) * t
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(points))
    cu.resolution_u = resolution
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True
    ob = bpy.data.objects.new(name, cu)
    col(collection).objects.link(ob)
    return own(ob)


def skin_chain(name, joints, collection="HIGH", subdiv=2, root_index=0):
    """Organic blockout in one call. joints = [(x, y, z, radius), ...] connected in order, or a dict
    {"name": [(x, y, z, r), ...], ...} of chains sharing their first point with another chain by position.
    Skin modifier + Subdivision gives a smooth mass with quad loops at every joint, which is a usable
    LOW base for stylized characters after shrinkwrapping to the sculpt."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    chains = joints if isinstance(joints, dict) else {"main": joints}
    vert_by_pos = {}
    order = []
    for cname, pts in chains.items():
        prev = None
        for (x, y, z, r) in pts:
            key = (round(x, 5), round(y, 5), round(z, 5))
            v = vert_by_pos.get(key)
            if v is None:
                v = bm.verts.new((x, y, z))
                vert_by_pos[key] = v
                order.append((v, r))
            if prev is not None and prev is not v:
                if not bm.edges.get((prev, v)):
                    bm.edges.new((prev, v))
            prev = v
    bm.verts.index_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col(collection).objects.link(ob)
    skin = ob.modifiers.new("Skin", "SKIN")
    skin.use_smooth_shade = True
    # skin_vertices layer exists once the modifier is present
    layer = me.skin_vertices[0].data
    for i, (v, r) in enumerate(order):
        layer[i].radius = (r, r)
        layer[i].use_root = (i == root_index)
    sub = ob.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = subdiv
    sub.render_levels = subdiv
    return own(ob)


# MODIFIERS AND EDITS

def mirror_origin():
    """Shared empty at the world origin so mirrors work across the asset's centre line,
    not across each object's own origin (the classic Blender mirror mistake)."""
    ob = bpy.data.objects.get("REF_mirror_origin")
    if ob is None:
        ob = bpy.data.objects.new("REF_mirror_origin", None)
        ob.empty_display_type = "PLAIN_AXES"
        ob.empty_display_size = 0.05
        col("REF").objects.link(ob)
    return ob


def mirror(ob, axis="X", merge=0.001, clip=True, about_world=True):
    """Mirror across the world centre plane by default. Pass about_world=False to mirror
    across the object's own origin (only right when the origin sits on the symmetry plane)."""
    m = ob.modifiers.new("Mirror", "MIRROR")
    m.use_axis = (axis == "X", axis == "Y", axis == "Z")
    m.use_mirror_merge = merge > 0
    m.merge_threshold = merge
    m.use_clip = clip
    if about_world:
        m.mirror_object = mirror_origin()
    return m


def bevel(ob, width=0.01, segments=3, angle_limit=30, harden=True):
    b = ob.modifiers.new("Bevel", "BEVEL")
    b.width = width
    b.segments = segments
    b.limit_method = "ANGLE"
    b.angle_limit = math.radians(angle_limit)
    b.harden_normals = harden
    return b


def subsurf(ob, levels=2):
    s = ob.modifiers.new("Subdivision", "SUBSURF")
    s.levels = levels
    s.render_levels = levels
    return s


def solidify(ob, thickness=0.01, offset=-1.0, rim=True):
    s = ob.modifiers.new("Solidify", "SOLIDIFY")
    s.thickness = thickness
    s.offset = offset
    s.use_rim = rim
    return s


def boolean(ob, cutter, op="DIFFERENCE", hide_cutter=True, solver="EXACT"):
    b = ob.modifiers.new("Bool_" + cutter.name, "BOOLEAN")
    b.operation = op
    b.object = cutter
    b.solver = solver
    if hide_cutter:
        cutter.hide_render = True
        cutter.hide_viewport = True
        cutter.display_type = "WIRE"
    return b


def array(ob, count, offset=(1, 0, 0), relative=True, curve=None):
    a = ob.modifiers.new("Array", "ARRAY")
    a.count = count
    if relative:
        a.relative_offset_displace = offset
    else:
        a.use_relative_offset = False
        a.use_constant_offset = True
        a.constant_offset_displace = offset
    if curve is not None:
        a.fit_type = "FIT_CURVE"
        a.curve = curve
        c = ob.modifiers.new("Curve", "CURVE")
        c.object = curve
    return a


def shrinkwrap(ob, target, offset=0.0, mode="NEAREST_SURFACEPOINT"):
    s = ob.modifiers.new("Shrinkwrap", "SHRINKWRAP")
    s.target = target
    s.offset = offset
    s.wrap_method = mode
    return s


def remesh_voxel(ob, voxel_size=0.02, smooth_normals=True):
    r = ob.modifiers.new("Remesh", "REMESH")
    r.mode = "VOXEL"
    r.voxel_size = voxel_size
    r.use_smooth_shade = smooth_normals
    return r


def decimate(ob, ratio):
    d = ob.modifiers.new("Decimate", "DECIMATE")
    d.ratio = ratio
    return d


def apply_all_modifiers(ob):
    """Bake the modifier stack into the mesh without operators (safe in background)."""
    dg = bpy.context.evaluated_depsgraph_get()
    eo = ob.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(eo)
    old = ob.data
    name = old.name
    ob.data = me
    ob.modifiers.clear()
    if old.users == 0:
        bpy.data.meshes.remove(old)
    me.name = name                      # keep the mesh name free of .001
    return ob


def apply_transform(ob):
    """Freeze location/rotation/scale into the mesh. Only for unparented objects."""
    if ob.parent is not None or ob.type != "MESH":
        return ob
    ob.data.transform(ob.matrix_basis)
    ob.matrix_basis = Matrix.Identity(4)
    return ob


def set_origin(ob, world_point):
    """Move the object origin to world_point without moving the geometry."""
    p = Vector(world_point)
    local = ob.matrix_world.inverted() @ p
    ob.data.transform(Matrix.Translation(-local))
    ob.matrix_world = ob.matrix_world @ Matrix.Translation(local)
    return ob


def join_meshes(name, objects, collection="LOW"):
    """Merge several mesh objects into one new object in world space. Sources are left alone."""
    bm = bmesh.new()
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in objects:
        eo = ob.evaluated_get(dg)
        me = eo.to_mesh()
        tmp = bmesh.new()
        tmp.from_mesh(me)
        bmesh.ops.transform(tmp, matrix=eo.matrix_world, verts=tmp.verts)
        tmp_me = bpy.data.meshes.new("_tmp_join")
        tmp.to_mesh(tmp_me)
        tmp.free()
        bm.from_mesh(tmp_me)
        bpy.data.meshes.remove(tmp_me)
        eo.to_mesh_clear()
    return new_mesh_object(name, bm, collection)


def duplicate(ob, name, collection=None):
    new = ob.copy()
    new.data = ob.data.copy()
    new.name = name
    new.data.name = name
    col(collection or ob.users_collection[0].name).objects.link(new)
    return own(new)


def shade_smooth(ob, sharp_angle=math.radians(30)):
    """Smooth shading with sharp edges marked by angle. Marked sharp edges always split normals in 4.1+."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle(0.0) <= sharp_angle
    bm.to_mesh(me)
    bm.free()
    if hasattr(me, "use_auto_smooth"):      # 4.0 only; removed in 4.1
        me.use_auto_smooth = True
        me.auto_smooth_angle = math.pi
    return ob


def push(ob, center, radius, strength, direction=None, falloff="smooth"):
    """Code sculpting: move vertices within radius of center along their normal (or direction)."""
    me = ob.data
    c = ob.matrix_world.inverted() @ Vector(center)
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    d = None if direction is None else (ob.matrix_world.to_3x3().inverted() @ Vector(direction)).normalized()
    for v in bm.verts:
        t = (v.co - c).length / radius
        if t >= 1.0:
            continue
        w = (1 - t * t) ** 2 if falloff == "smooth" else (1 - t)
        v.co += (d if d is not None else v.normal) * strength * w
    bm.to_mesh(me)
    bm.free()
    return ob


def taper(ob, axis="Z", top_scale=0.5, bottom=None, top=None):
    """Scale cross sections linearly along an axis (limb tapering, spires, hulls)."""
    me = ob.data
    idx = "XYZ".index(axis)
    cos = [v.co[idx] for v in me.vertices]
    lo = min(cos) if bottom is None else bottom
    hi = max(cos) if top is None else top
    for v in me.vertices:
        t = 0 if hi == lo else max(0.0, min(1.0, (v.co[idx] - lo) / (hi - lo)))
        s = 1 + (top_scale - 1) * t
        for j in range(3):
            if j != idx:
                v.co[j] *= s
    return ob


# UV

def smart_uv(ob, angle=66.0, margin=0.02, seams_from_sharp=True):
    """Quick unwrap for blockouts, props and hard surface: Smart UV Project through the operator,
    with seams taken from marked sharp edges when asked. Hero deforming parts get seams placed
    by hand in the phase script (mark_seams) and unwrap_by_seams instead."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    if seams_from_sharp:
        bpy.ops.mesh.edges_select_sharp(sharpness=math.radians(angle))
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin)
    bpy.ops.object.mode_set(mode="OBJECT")
    return ob


def mark_seams(ob, edge_filter):
    """edge_filter(bmesh_edge) -> bool. Marks seams by rule, e.g. lambda e: abs(e.verts[0].co.x) < 1e-4."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    n = 0
    for e in bm.edges:
        if edge_filter(e):
            e.seam = True
            n += 1
    bm.to_mesh(me)
    bm.free()
    log("seams marked on", ob.name, n)
    return ob


def unwrap_by_seams(ob, margin=0.02, method="ANGLE_BASED"):
    """Unwrap along marked seams, then pack islands."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.unwrap(method=method, margin=margin)
    bpy.ops.object.mode_set(mode="OBJECT")
    return ob


# MATERIALS

def material(name, color=(0.5, 0.5, 0.5, 1), roughness=0.5, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if bpy.app.version < (5, 0, 0) and not m.use_nodes:   # 5.0+ materials always use nodes
        m.use_nodes = True
    # look nodes up by type: display names are translated in non-English Blender UIs
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m


def assign(ob, mat):
    if ob.data.materials:
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)
    return ob


# RIG HELPERS

def armature(name, bones, collection="RIG_DEF"):
    """bones = [(name, head, tail, parent_name_or_None, roll_deg, deform_bool), ...]"""
    arm = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, arm)
    col(collection).objects.link(ob)
    own(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    for bname, head, tail, parent, roll, deform in bones:
        eb = arm.edit_bones.new(bname)
        eb.head, eb.tail = Vector(head), Vector(tail)
        eb.roll = math.radians(roll)
        eb.use_deform = deform
        if parent:
            eb.parent = arm.edit_bones[parent]
            eb.use_connect = (Vector(head) - arm.edit_bones[parent].tail).length < 1e-5
    bpy.ops.object.mode_set(mode="OBJECT")
    return ob


def bind(mesh_ob, arm_ob, method="ARMATURE_AUTO"):
    """Parent with automatic weights. Weight painting corrections come after, in a later phase."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    mesh_ob.select_set(True)
    arm_ob.select_set(True)
    bpy.context.view_layer.objects.active = arm_ob
    bpy.ops.object.parent_set(type=method)
    return mesh_ob


def socket(name, location, parent=None, parent_bone=None, rotation=(0, 0, 0), size=0.1, **props):
    """Semantic attachment point. Local +Y = forward of whatever attaches, +Z = its up."""
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "ARROWS"
    ob.empty_display_size = size
    col("SOCKETS").objects.link(ob)
    own(ob)
    if parent is not None:
        ob.parent = parent
        if parent_bone:
            ob.parent_type = "BONE"
            ob.parent_bone = parent_bone
    ob.matrix_world = Matrix.Translation(Vector(location)) @ Euler(rotation).to_matrix().to_4x4()
    for k, v in props.items():
        ob[k] = v
    return ob


def lod_copy(ob, level, ratio):
    """Make <name>_LOD<level> from a LOD0 object with a Decimate at ratio. Rework silhouettes by hand after."""
    base = ob.name.replace("_LOD0", "")
    new = duplicate(ob, base + "_LOD" + str(level))
    decimate(new, ratio)
    return new


# BUILD

# ---------------------------------------------------------------------------------------------
# CR_Leao_Solar: blockout. Unidade = 1 stud. Frente -Y, Z para cima, origem no chao sob o centro.
# Fonte das medidas: ref/lateral_esquerda_matte.png (vista lateral esquerda, 526x366 px, chao na
# linha 366). Escala: 0,052801 stud/px (ombro 11,5 = 218 px). Conversao: y = -(px_x - 263) * S,
# z = altura_px * S. Valores sem medida na referencia levam "# inferred".
# ---------------------------------------------------------------------------------------------
S = 0.052801

def px(x_px, h_px):
    """(y, z) a partir de coluna e altura em px no matte lateral."""
    return (-(x_px - 263) * S, h_px * S)

OMBRO = 11.5                     # oficial 10-13 (meio da faixa)
LARG_PEITO = 0.42 * OMBRO        # inferred: largura de leao ~0,42 do ombro (sem vista frontal)
MEIA = LARG_PEITO / 2            # 2,415
PATA_X = 1.85                    # inferred: afastamento lateral das patas

# passada da referencia (graus, + = pata para tras), medida pelos apoios no matte
PASSADA_REF = {"Pata_DE": -9, "Pata_DD": 19, "Pata_TE": 22, "Pata_TD": -22}   # atan((y_apoio_ref - y_apoio_neutro) / comprimento)


def skin_e(name, pts, collection="LOW", subdiv=2):
    """Cadeia Skin com raio eliptico: pts = [(x, y, z, rx, rz), ...] ligados em ordem."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new((p[0], p[1], p[2])) for p in pts]
    for a, b in zip(vs, vs[1:]):
        bm.edges.new((a, b))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col(collection).objects.link(ob)
    sk = ob.modifiers.new("Skin", "SKIN")
    sk.use_smooth_shade = True
    lay = me.skin_vertices[0].data
    for i, p in enumerate(pts):
        lay[i].radius = (p[3], p[4])
        lay[i].use_root = (i == 0)
    subsurf(ob, subdiv)
    return own(ob)


def com_pivo(ob, pivo):
    bpy.context.view_layer.update()      # matrix_world so e valida depois do update (senao a peca vai para a origem)
    set_origin(ob, pivo)
    ob["pivo"] = tuple(pivo)
    return ob


def tronco():
    # espinha da garupa ao peito; topo = z + rz; fundo = z - rz
    pts = [
        (0, *px(160, 152), 2.1, 2.6),            # nadega (x~135-160 no matte)
        (0, *px(205, 166), 2.5, 3.05),           # garupa: topo 211 px = 11,1 (+folga: o Subsurf encolhe ~8%)
        (0, *px(262, 162), 2.35, 3.35),          # lombo: topo 217 px = 11,5; flanco recolhido ~100 px = 5,3
        (0, *px(320, 150), 2.60, 3.90),          # peito: fundo ~76 px atras das patas dianteiras
        (0, *px(372, 150), 2.30, 3.40),          # peito frontal
    ]
    return skin_e("CR_Leao_Solar_Tronco_LOD0", pts)


def pescoco_cabeca():
    pesc = skin_e("CR_Leao_Solar_Pescoco_LOD0", [
        (0, *px(360, 175), 2.2, 2.4),
        (0, *px(430, 215), 1.9, 2.0),
        (0, *px(470, 228), 1.6, 1.7),
    ])
    com_pivo(pesc, (0, *px(360, 175)))
    cy, cz = px(470, 225)                        # cranio: centro do rosto atras da frente da juba (x 507-518)
    cranio = sphere("CR_Leao_Solar_Cranio_LOD0", 1.0, location=(0, cy, cz), scale=(1.55, 1.9, 1.6))
    fy, fz = px(490, 202)                        # focinho: massa x<=512, h 191-214 no matte
    focinho = sphere("CR_Leao_Solar_Focinho_LOD0", 1.0, location=(0, fy, fz), scale=(1.05, 1.2, 0.8))
    my, mz = px(482, 182)                        # mandibula (separada, abre no rugido) # inferred
    mand = sphere("CR_Leao_Solar_Mandibula_LOD0", 1.0, location=(0, my, mz), scale=(0.95, 1.35, 0.45))
    com_pivo(mand, (0, *px(462, 190)))
    olhos = []
    for s, lado in ((1, "E"), (-1, "D")):
        oy, oz = px(492, 232)
        olhos.append(sphere("CR_Leao_Solar_Olho_%s_LOD0" % lado, 0.24, location=(s * 0.95, oy, oz)))
    return [pesc, cranio, focinho, mand] + olhos


def juba():
    # massa superior: topo 356 px (x~429) = 18,8; frente x 507-518; traseira comeca em x~286
    uy, uz = px(420, 262)
    sup = sphere("CR_Leao_Solar_Juba_Sup_LOD0", 1.0, location=(0, uy, uz), scale=(3.4, 4.9, 5.0))
    sup.rotation_euler = (math.radians(-12), 0, 0)
    # babado do peito: desce ate ~44 px (x~403) = 2,3
    iy, iz = px(398, 130)
    inf = sphere("CR_Leao_Solar_Juba_Peito_LOD0", 1.0, location=(0, iy, iz), scale=(2.9, 2.55, 3.9))
    # transicao sobre a cernelha (x 286-338)
    ty, tz = px(334, 208)                        # transicao: topo ~266 px em x 299-312
    tra = sphere("CR_Leao_Solar_Juba_Nuca_LOD0", 1.0, location=(0, ty, tz), scale=(2.9, 2.5, 2.85))
    # frente da juba sob o rosto: x 455-494 com massa entre h ~110-210
    fy, fz = px(466, 160)
    fre = sphere("CR_Leao_Solar_Juba_Frente_LOD0", 1.0, location=(0, fy, fz), scale=(2.6, 1.5, 2.6))
    return [sup, inf, tra, fre]


def patas():
    obs = []
    for s, lado in ((1, "E"), (-1, "D")):
        # dianteira: escapula -> ombro -> cotovelo -> carpo -> pata -> dedos (neutra, vertical)
        y0 = -6.9                              # apoio dianteiro neutro: media dos apoios x 338-364 e 416-458
        d = skin_e("CR_Leao_Solar_Pata_D%s_LOD0" % lado, [
            (s * 1.95, y0 + 0.9, 10.2, 1.55, 1.9),   # escapula sob a pele # inferred
            (s * 2.05, y0 + 0.3, 7.6, 1.8, 1.9),     # ombro
            (s * PATA_X, y0 + 0.8, 4.9, 1.4, 1.45),  # cotovelo: antebraco largo (~40 px)
            (s * PATA_X, y0 - 0.1, 1.7, 0.95, 0.95), # carpo
            (s * PATA_X, y0 - 0.6, 0.6, 1.05, 0.55), # pata: larga e longa (apoio ~1 stud mais a frente no matte)
            (s * PATA_X, y0 - 2.0, 0.5, 0.95, 0.48), # dedos
        ])
        com_pivo(d, (s * 2.0, y0 + 0.4, 8.8))
        obs.append(d)
        # traseira: anca -> joelho (stifle) -> jarrete (hock) -> pata -> dedos
        y1 = 4.9
        t = skin_e("CR_Leao_Solar_Pata_T%s_LOD0" % lado, [
            (s * 1.95, y1 + 0.2, 9.7, 2.0, 2.3),     # anca/coxa
            (s * 2.1, y1 - 2.2, 6.0, 1.7, 1.75),     # joelho (stifle) a frente da coxa, rente a barriga
            (s * PATA_X, y1 + 1.0, 2.7, 0.8, 0.8),   # jarrete
            (s * PATA_X, y1 + 0.1, 0.6, 1.0, 0.55),  # pata
            (s * PATA_X, y1 - 1.3, 0.5, 0.9, 0.48),  # dedos
        ])
        com_pivo(t, (s * 2.0, y1 + 0.2, 9.6))
        obs.append(t)
    return obs


def cauda():
    # base x~143 h~170; ponto mais baixo x~65 h~88-100; sobe ao tufo (x 26-91, h 175-270)
    # NURBS aproxima (nao passa pelos pontos): pontos de controle um pouco alem do traco medido
    pts = [px(152, 176), px(126, 136), px(102, 100), px(62, 90), px(34, 104), px(10, 150), px(14, 196), px(40, 214)]
    tubo = curve_tube("CR_Leao_Solar_Cauda_LOD0", [(0, y, z) for y, z in pts], 0.42, taper_to=0.75)
    ty, tz = px(62, 221)                         # tufo x 26-91, h 175-270; envolve a ponta do tubo
    tufo = sphere("CR_Leao_Solar_Cauda_Tufo_LOD0", 1.0, location=(0, ty, tz), scale=(0.9, 1.4, 2.95))   # topo ~270 px, base ~172 px
    tufo.rotation_euler = (math.radians(-18), 0, 0)
    return [tubo, tufo]


def posar(passada):
    """Gira as patas nos pivos (eixo X) para comparar com a passada da referencia; {} = neutra.
    Pata reta girada sobe o pe; desce a pata ate o apoio tocar o chao (o topo some dentro do tronco)."""
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in bpy.data.objects:
        if ob.get("owner") == OWNER_TAG and "_Pata_" in ob.name:
            chave = ob.name.split("_Pata_")[1][:2]          # DE, DD, TE, TD
            ob.rotation_euler = (math.radians(passada.get("Pata_" + chave, 0)), 0, 0)
            bpy.context.view_layer.update()
            eo = ob.evaluated_get(dg)
            me = eo.to_mesh()
            zmin = min((eo.matrix_world @ v.co).z for v in me.vertices)
            eo.to_mesh_clear()
            ob.location.z -= zmin


def build(scene, args):
    obs = [tronco()] + pescoco_cabeca() + juba() + patas() + cauda()
    clay = material("BLK_Argila", (0.62, 0.55, 0.45, 1), 0.8)
    for ob in obs:
        if ob.type == "MESH":
            assign(ob, clay)
    scene["blockout_pose"] = "neutra"
    if getattr(args, "pose", "neutra") == "referencia":
        posar(PASSADA_REF)
        scene["blockout_pose"] = "referencia"
    log("primitivas", len(obs), "pose", scene["blockout_pose"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--master", required=True)
    p.add_argument("--pose", default="neutra", choices=["neutra", "referencia"])
    a = p.parse_args(argv_after_dashes())
    scene = open_master(a.master)
    clear_owned()
    build(scene, a)
    save_master(a.master)
    log("saved", a.master)
