import bpy, bmesh, math, random
from mathutils import Vector

def find_islands(bm):
    bm.verts.ensure_lookup_table()
    seen = set()
    res = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack = [v]
        comp = [v.index]
        seen.add(v.index)
        while stack:
            a = stack.pop()
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index)
                    comp.append(b.index)
                    stack.append(b)
        zs = [bm.verts[i].co.z for i in comp]
        res.append((comp, min(zs), max(zs)))
    return res

def bez(p0, p1, p2, t):
    return p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t

def add_root(bm, uvl, p0, p1, p2, w0, h_ratio, segs, sides, vscale, expo=1.25, tipf=0.08, flat_bottom=0.55):
    rings = []
    for i in range(segs + 1):
        t = i / segs
        c = bez(p0, p1, p2, t)
        tan = (bez(p0, p1, p2, min(1, t + 0.02)) - bez(p0, p1, p2, max(0, t - 0.02)))
        if tan.length < 1e-6:
            tan = Vector((1, 0, 0))
        tan.normalize()
        side = Vector((-tan.y, tan.x, 0))
        if side.length < 1e-4:
            side = Vector((0, 1, 0))
        side.normalize()
        up = side.cross(tan)
        if up.z < 0:
            up = -up
        up.normalize()
        w = w0 * ((1 - t) ** expo * (1 - tipf) + tipf)
        hh = w * h_ratio
        ring = []
        for k in range(sides):
            ph = 2 * math.pi * k / sides
            sx, sy = math.cos(ph), math.sin(ph)
            vy = hh * sy * (flat_bottom if sy < 0 else 1.0)
            ring.append(bm.verts.new(c + side * w * sx + up * vy))
        rings.append(ring)
    for i in range(segs):
        for k in range(sides):
            k2 = (k + 1) % sides
            f = bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
            f.smooth = True
            u0, u1 = k / sides, (k + 1) / sides
            v0, v1 = i / segs * vscale, (i + 1) / segs * vscale
            for l, uv in zip(f.loops, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]):
                l[uvl].uv = uv
    # tampa da ponta
    tip = rings[-1]
    f = bm.faces.new(tip)
    f.smooth = True
    for l in f.loops:
        l[uvl].uv = (0.5, vscale)

def fix_trunk(src_name, lod, seed):
    src = bpy.data.objects[src_name]
    new_name = src_name + "_R"
    old = bpy.data.objects.get(new_name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    me = src.data.copy()
    ob = bpy.data.objects.new(new_name, me)
    for c in src.users_collection:
        c.objects.link(ob)
    ob.location = src.location
    ob.rotation_euler = src.rotation_euler
    ob.scale = src.scale
    bm = bmesh.new()
    bm.from_mesh(me)
    isl = find_islands(bm)
    H = max(i[2] for i in isl)
    total = len(bm.verts)
    kill = []
    for comp, zmin, zmax in isl:
        if zmax < 0.2 * H and len(comp) < total * 0.5:
            kill += comp
    kill_set = set(kill)
    bm.verts.ensure_lookup_table()
    geom = [bm.verts[i] for i in kill_set]
    if geom:
        bmesh.ops.delete(bm, geom=geom, context='VERTS')
    # galhos: refazer como arcos curvos e grossos (sem "espinhos")
    bm.verts.ensure_lookup_table()
    isl2 = find_islands(bm)
    main = max(isl2, key=lambda t: len(t[0]))
    uvl0 = bm.loops.layers.uv.active
    new_branches = []
    del_list = []
    for comp, zmin, zmax in isl2:
        if comp is main[0] or len(comp) == len(main[0]):
            continue
        pts = [bm.verts[i].co.copy() for i in comp]
        pts.sort(key=lambda v: math.hypot(v.x, v.y))
        nb = max(4, len(pts) // 8)
        base = sum(pts[:nb], Vector()) / nb
        tip = sum(pts[-nb:], Vector()) / nb
        rb = sum(((q - base).length for q in pts[:nb]), 0.0) / nb
        new_branches.append((base, tip, max(rb, 0.6)))
        del_list += [bm.verts[i] for i in comp]
    bmesh.ops.delete(bm, geom=del_list, context='VERTS')
    bm.verts.ensure_lookup_table()
    uvl1 = bm.loops.layers.uv.active
    for base, tip, rb in new_branches:
        ln = (tip - base).length
        if ln > 11.0:
            tip = base + (tip - base).normalized() * 11.0
            ln = 11.0
        hd = Vector((tip.x - base.x, tip.y - base.y, 0))
        hd = hd.normalized() if hd.length > 1e-6 else Vector((1, 0, 0))
        p0 = base - hd * 0.8
        p1 = (base + tip) / 2 + Vector((0, 0, ln * 0.16))
        p2 = tip + (tip - base).normalized() * ln * 0.08 + Vector((0, 0, ln * 0.06))
        add_root(bm, uvl1, p0, p1, p2, max(rb * 1.35, 1.1), 1.0, 7 if lod == 0 else 4, 8 if lod == 0 else 6, 0.6, expo=0.9, tipf=0.16, flat_bottom=1.0)
    # raio da base
    bm.verts.ensure_lookup_table()
    rs = [math.hypot(v.co.x, v.co.y) for v in bm.verts if v.co.z < 4]
    R = max(rs) if rs else 8.0
    uvl = bm.loops.layers.uv.active
    rnd = random.Random(seed)
    zs = max(5.0, min(R * 0.95, 11.0))
    if lod == 0:
        n_main, n_small, segs, sides = 8, 0, 9, 8
    else:
        n_main, n_small, segs, sides = 5, 0, 4, 6
    base_ang = rnd.uniform(0, 6.28)
    for k in range(n_main):
        a = base_ang + k / n_main * 2 * math.pi + rnd.uniform(-0.18, 0.18)
        d = Vector((math.cos(a), math.sin(a), 0))
        s = Vector((-d.y, d.x, 0))
        reach = R * rnd.uniform(2.2, 2.9)
        p0 = d * R * 0.30 + Vector((0, 0, zs))
        p1 = d * R * 1.15 + s * rnd.uniform(-0.5, 0.5) * R * 0.3 + Vector((0, 0, zs * 0.28))
        p2 = d * reach + s * rnd.uniform(-0.35, 0.35) * R * 0.4 + Vector((0, 0, -1.1))
        add_root(bm, uvl, p0, p1, p2, R * rnd.uniform(0.72, 0.9), 0.5, segs, sides, 0.55, expo=1.0, tipf=0.1, flat_bottom=0.4)
    for k in range(n_small):
        a = base_ang + (k + 0.5) / n_small * 2 * math.pi + rnd.uniform(-0.2, 0.2)
        d = Vector((math.cos(a), math.sin(a), 0))
        s = Vector((-d.y, d.x, 0))
        p0 = d * R * 0.8 + Vector((0, 0, zs * 0.18))
        p1 = d * R * 1.4 + s * rnd.uniform(-0.4, 0.4) * R * 0.3 + Vector((0, 0, zs * 0.06))
        p2 = d * R * rnd.uniform(2.0, 2.6) + Vector((0, 0, -0.9))
        add_root(bm, uvl, p0, p1, p2, R * rnd.uniform(0.17, 0.24), 0.8, 5, 6, 0.4)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return ob, R, zs
