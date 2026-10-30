import bpy, math, random
from mathutils import Vector

OUTDIR = r"C:\Users\Rhenan\Downloads\RPG_Roblox_GitHub_Pacote_Inicial\BLENDER\Biblioteca\F_Chao_Vivo"

def mat_from(src_name, new_name, image=None):
    m = bpy.data.materials.get(new_name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials[src_name].copy()
    m.name = new_name
    m.use_backface_culling = False
    if image is not None:
        for nd in m.node_tree.nodes:
            if nd.type == 'TEX_IMAGE':
                nd.image = image
    return m

class MB:
    def __init__(self):
        self.v = []
        self.f = []
        self.uv = []
    def add(self, verts, uvs, idx=None):
        base = len(self.v)
        self.v.extend(verts)
        n = len(verts)
        face = list(range(base, base + n))
        self.f.append(face)
        self.uv.append(list(uvs))
    def quad(self, a, b, c, d, uva, uvb, uvc, uvd):
        self.add([a, b, c, d], [uva, uvb, uvc, uvd])
    def build(self, name, mat, loc=(0, 0, 0)):
        old = bpy.data.objects.get(name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(x) for x in self.v], [], self.f)
        me.update()
        uvl = me.uv_layers.new(name="UVMap")
        li = 0
        for fi, face in enumerate(self.f):
            for k in range(len(face)):
                uvl.data[li].uv = self.uv[fi][k]
                li += 1
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = loc
        for p in me.polygons:
            p.use_smooth = False
        return ob

def export(ob, fname):
    import os
    os.makedirs(OUTDIR, exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    loc = ob.location.copy()
    ob.location = (0, 0, 0)
    bpy.ops.export_scene.gltf(filepath=OUTDIR + "\\" + fname + ".glb", export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True)
    ob.location = loc

# ---- ferns -----------------------------------------------------------
FERN_CELLS = [(0.0, 0.0), (0.5, 0.0), (0.0, 0.5), (0.5, 0.5)]
def frond(mb, origin, yaw, L, pitch0, droop, wfac=0.56, roll=0.0, cell=0, N=9):
    f = Vector((math.cos(yaw), math.sin(yaw), 0))
    r = Vector((-math.sin(yaw), math.cos(yaw), 0))
    up = Vector((0, 0, 1))
    pos = Vector(origin)
    th = pitch0
    pts = []
    for i in range(N + 1):
        pts.append((pos.copy(), th))
        if i < N:
            step = L / N
            pos = pos + (f * math.cos(th) + up * math.sin(th)) * step
            th -= droop / N
    u0, v0 = FERN_CELLS[cell % 4]
    uL = u0 + 0.5 * 0.22
    uR = u0 + 0.5 * 0.78
    W = L * wfac
    verts_l, verts_r = [], []
    for p, th in pts:
        tangent = f * math.cos(th) + up * math.sin(th)
        side = r * math.cos(roll) + up * math.sin(roll) * (1 if True else 0)
        side = (r * math.cos(roll) + tangent.cross(r).normalized() * math.sin(roll))
        verts_l.append(p - side * W / 2)
        verts_r.append(p + side * W / 2)
    for i in range(N):
        t0 = i / N
        t1 = (i + 1) / N
        va = v0 + 0.5 * (0.02 + 0.97 * t0)
        vb = v0 + 0.5 * (0.02 + 0.97 * t1)
        mb.quad(verts_l[i], verts_r[i], verts_r[i + 1], verts_l[i + 1], (uL, va), (uR, va), (uR, vb), (uL, vb))

def fern(name, mat, nfr, L, pitch_range, droop, jitter, seed, loc=(0, 0, 0), wfac=0.56, spread=1.0):
    rnd = random.Random(seed)
    mb = MB()
    for k in range(nfr):
        yaw = k / nfr * 2 * math.pi + rnd.uniform(-jitter, jitter)
        Lk = L * rnd.uniform(0.75, 1.1)
        p0 = rnd.uniform(*pitch_range)
        frond(mb, (math.cos(yaw) * 0.6, math.sin(yaw) * 0.6, 0.3), yaw, Lk, p0, droop * rnd.uniform(0.8, 1.2),
              wfac=wfac, roll=rnd.uniform(-0.25, 0.25), cell=rnd.randrange(4))
    return mb.build(name, mat, loc)

# ---- capim alto: planos cruzados com leve curvatura -------------------
def tuft(name, mat, seed, size=14, planes=3, loc=(0, 0, 0)):
    rnd = random.Random(seed)
    mb = MB()
    for k in range(planes):
        a = k * math.pi / planes + rnd.uniform(-0.2, 0.2)
        dx, dy = math.cos(a), math.sin(a)
        hw = size * 0.5 * rnd.uniform(0.85, 1.1)
        h = size * rnd.uniform(0.9, 1.15)
        bend = rnd.uniform(-2.2, 2.2)
        rows = 4
        for i in range(rows):
            t0, t1 = i / rows, (i + 1) / rows
            def P(sx, t):
                bx = bend * t * t
                return (dx * sx + (-dy) * bx * 0.4 + dy * 0 , dy * sx + dx * bx * 0.4, h * t)
            a1 = P(-hw * (1 - 0.15 * t0), t0)
            b1 = P(hw * (1 - 0.15 * t0), t0)
            b2 = P(hw * (1 - 0.15 * t1), t1)
            a2 = P(-hw * (1 - 0.15 * t1), t1)
            u0, u1 = 0.02 + 0.0, 0.48
            v0 = 0.01 + 0.5 * 0.0 + 0.48 * t0
            v1 = 0.01 + 0.48 * t1
            mb.quad(a1, b1, b2, a2, (u0, v0), (u1, v0), (u1, v1), (u0, v1))
    return mb.build(name, mat, loc)

# ---- remendos planos (trevo, serapilheira, musgo) ---------------------
def patch(name, mat, cell, size, seed, loc=(0, 0, 0), lift=0.18, bump=0.25, flip=False, n=6):
    rnd = random.Random(seed)
    mb = MB()
    cu, cv = cell
    h = size / 2
    grid = []
    for iy in range(n + 1):
        row = []
        for ix in range(n + 1):
            x = -h + size * ix / n
            y = -h + size * iy / n
            d = math.sqrt(x * x + y * y) / h
            z = lift + bump * rnd.random() * (1 - 0.5 * min(d, 1))
            row.append((x, y, z))
        grid.append(row)
    for iy in range(n):
        for ix in range(n):
            a, b, c, d = grid[iy][ix], grid[iy][ix + 1], grid[iy + 1][ix + 1], grid[iy + 1][ix]
            def uvf(ix_, iy_):
                u = ix_ / n
                v = iy_ / n
                if flip:
                    u = 1 - u
                return (cu + 0.5 * (0.01 + 0.98 * u), cv + 0.5 * (0.01 + 0.98 * v))
            mb.quad(a, b, c, d, uvf(ix, iy), uvf(ix + 1, iy), uvf(ix + 1, iy + 1), uvf(ix, iy + 1))
    return mb.build(name, mat, loc)

# ---- flores -----------------------------------------------------------
FLOWER_CELLS = [(0.0, 0.5), (0.25, 0.5), (0.5, 0.5), (0.75, 0.5)]
STEM_UV = (0.875, 0.1)    # verde da celula 3 baixo (u 0.75+0.125*... )
def flower_cluster(name, mat, cell, seed, count=6, height=5.0, head=2.6, loc=(0, 0, 0)):
    rnd = random.Random(seed)
    mb = MB()
    cu, cv = FLOWER_CELLS[cell]
    gu = (0.75 + 0.145, 0.15)   # ponto verde (cel. baixo-direita, metade direita)
    for k in range(count):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0.2, 3.2)
        bx, by = math.cos(a) * d, math.sin(a) * d
        hh = height * rnd.uniform(0.7, 1.15)
        lean = rnd.uniform(0.2, 1.1)
        tx, ty = bx + math.cos(a) * lean, by + math.sin(a) * lean
        sw = 0.11
        # haste (dois planos cruzados)
        for (ox, oy) in ((sw, 0), (0, sw)):
            mb.quad((bx - ox, by - oy, 0), (bx + ox, by + oy, 0), (tx + ox * 0.6, ty + oy * 0.6, hh), (tx - ox * 0.6, ty - oy * 0.6, hh),
                    gu, gu, gu, gu)
        # cabeca: quad inclinado para cima/fora
        hs = head * rnd.uniform(0.8, 1.15) / 2
        tilt = rnd.uniform(0.08, 0.4)
        ang = rnd.uniform(0, 2 * math.pi)
        ex = Vector((math.cos(ang), math.sin(ang), 0))
        ey = Vector((-math.sin(ang), math.cos(ang), 0))
        n_ = Vector((math.cos(a) * tilt, math.sin(a) * tilt, 1)).normalized()
        e1 = ex - n_ * ex.dot(n_)
        e1.normalize()
        e2 = n_.cross(e1)
        c = Vector((tx, ty, hh))
        pts = [c + (-e1 - e2) * hs, c + (e1 - e2) * hs, c + (e1 + e2) * hs, c + (-e1 + e2) * hs]
        mb.add(pts, [(cu + 0.003, cv + 0.003), (cu + 0.247, cv + 0.003), (cu + 0.247, cv + 0.247), (cu + 0.003, cv + 0.247)])
    # folhas basais verdes
    for k in range(5):
        a = rnd.uniform(0, 2 * math.pi)
        L = rnd.uniform(2.2, 3.4)
        w = 0.55
        ex = Vector((math.cos(a), math.sin(a), 0))
        ey = Vector((-math.sin(a), math.cos(a), 0))
        p0 = ex * 0.3
        p1 = ex * (L * 0.5) + Vector((0, 0, L * 0.45))
        p2 = ex * L + Vector((0, 0, L * 0.25))
        mb.add([p0 - ey * w * 0.3, p0 + ey * w * 0.3, p1 + ey * w, p2, p1 - ey * w], [gu, gu, gu, gu, gu])
    return mb.build(name, mat, loc)

# ---- cogumelos --------------------------------------------------------
def mushroom_cluster(name, mat, cell, seed, count=5, size=2.6, loc=(0, 0, 0)):
    rnd = random.Random(seed)
    mb = MB()
    capu = cell * 0.25
    stem_uv = (0.75 + 0.06, 0.25)
    for k in range(count):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0, 3.0) * (0.4 if k == 0 else 1)
        bx, by = math.cos(a) * d, math.sin(a) * d
        s = size * rnd.uniform(0.55, 1.15) * (1.2 if k == 0 else 1)
        sh = s * rnd.uniform(0.9, 1.6)
        sr = s * 0.17
        seg = 6
        # caule (cilindro de 6 lados, afinando para cima)
        for i in range(seg):
            a0 = i / seg * 2 * math.pi
            a1 = (i + 1) / seg * 2 * math.pi
            p0 = (bx + math.cos(a0) * sr * 1.15, by + math.sin(a0) * sr * 1.15, 0)
            p1 = (bx + math.cos(a1) * sr * 1.15, by + math.sin(a1) * sr * 1.15, 0)
            p2 = (bx + math.cos(a1) * sr, by + math.sin(a1) * sr, sh)
            p3 = (bx + math.cos(a0) * sr, by + math.sin(a0) * sr, sh)
            mb.quad(p0, p1, p2, p3, stem_uv, stem_uv, stem_uv, stem_uv)
        # chapeu: calota (aneis)
        rings = 4
        capr = s * 0.62
        caph = s * 0.42
        for rI in range(rings):
            t0 = rI / rings
            t1 = (rI + 1) / rings
            a_0 = t0 * math.pi / 2
            a_1 = t1 * math.pi / 2
            r0, z0 = capr * math.cos(a_0), sh * 0.93 + caph * math.sin(a_0)
            r1, z1 = capr * math.cos(a_1), sh * 0.93 + caph * math.sin(a_1)
            for i in range(seg):
                b0 = i / seg * 2 * math.pi
                b1 = (i + 1) / seg * 2 * math.pi
                P = lambda rr, zz, bb: (bx + math.cos(bb) * rr, by + math.sin(bb) * rr, zz)
                def U(rr, bb):
                    return (capu + 0.125 + math.cos(bb) * (rr / capr) * 0.122, 0.125 + math.sin(bb) * (rr / capr) * 0.122)
                if rI == rings - 1:
                    mb.add([P(r0, z0, b0), P(r0, z0, b1), P(0, z1, 0)], [U(r0, b0), U(r0, b1), U(0, 0)])
                else:
                    mb.quad(P(r0, z0, b0), P(r0, z0, b1), P(r1, z1, b1), P(r1, z1, b0), U(r0, b0), U(r0, b1), U(r1, b1), U(r1, b0))
    return mb.build(name, mat, loc)

# ---- galhos -----------------------------------------------------------
def branch_mb(mb, start, direction, length, r0, r1, seed, depth, bark_uv):
    rnd = random.Random(seed)
    segs = 4
    pos = Vector(start)
    d = Vector(direction).normalized()
    pts = [pos.copy()]
    for i in range(segs):
        d = (d + Vector((rnd.uniform(-0.18, 0.18), rnd.uniform(-0.18, 0.18), rnd.uniform(-0.08, 0.05)))).normalized()
        pos = pos + d * (length / segs)
        pts.append(pos.copy())
    sides = 5
    def ring(p, r, dd):
        up = Vector((0, 0, 1)) if abs(dd.z) < 0.9 else Vector((1, 0, 0))
        e1 = dd.cross(up).normalized()
        e2 = dd.cross(e1).normalized()
        return [p + (e1 * math.cos(2 * math.pi * k / sides) + e2 * math.sin(2 * math.pi * k / sides)) * r for k in range(sides)]
    rings = []
    for i, p in enumerate(pts):
        t = i / segs
        r = r0 + (r1 - r0) * t
        dd = (pts[min(i + 1, segs)] - pts[max(i - 1, 0)]).normalized()
        rings.append(ring(p, r, dd))
    for i in range(segs):
        for k in range(sides):
            k2 = (k + 1) % sides
            u0 = bark_uv[0] + (bark_uv[1] - bark_uv[0]) * k / sides
            u1 = bark_uv[0] + (bark_uv[1] - bark_uv[0]) * (k + 1) / sides
            v0 = 0.05 + 0.9 * i / segs
            v1 = 0.05 + 0.9 * (i + 1) / segs
            mb.quad(rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k], (u0, v0), (u1, v0), (u1, v1), (u0, v1))
    if depth > 0:
        for j in range(2):
            idx = rnd.randint(2, segs)
            sub_d = (d + Vector((rnd.uniform(-0.9, 0.9), rnd.uniform(-0.9, 0.9), rnd.uniform(0.0, 0.5)))).normalized()
            branch_mb(mb, pts[idx], sub_d, length * rnd.uniform(0.45, 0.65), r1 * 1.1 + 0.02, 0.03, seed * 7 + j * 13 + 1, depth - 1, bark_uv)

def twigs(name, mat, seed, n=3, loc=(0, 0, 0)):
    rnd = random.Random(seed)
    mb = MB()
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = (math.cos(a), math.sin(a), rnd.uniform(0.0, 0.18))
        start = (rnd.uniform(-2, 2), rnd.uniform(-2, 2), 0.35)
        branch_mb(mb, start, d, rnd.uniform(6, 11), 0.28, 0.1, seed * 31 + k, 2, (0.05, 0.95))
    return mb.build(name, mat, loc)
