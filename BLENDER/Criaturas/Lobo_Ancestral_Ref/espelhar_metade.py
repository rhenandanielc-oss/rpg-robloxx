"""Lobo Ancestral 100% simetrico: corta a malha LOW no plano x = 0, descarta a metade +X (lado E, com a pata dianteira
torcida e o ombro/peitoral pendendo para a direita) e a substitui pelo espelho da metade -X (lado D). Mesmo esqueleto
(ja simetrico). Copiados no espelho: UV (mesma textura, ilhas sobrepostas), atributos de face (interior/mandibula),
pesos com troca de nomes E<->D, normais personalizadas espelhadas. Na costura (x = 0): vertices fundidos e pesos
simetrizados. v1 (espelhar_frente.py + espelhar_textura.py, ajuste nao rigido) descartada: amassava o pelo do lado +X.
Uso: blender -b rig5/Lobo_Ancestral_Rig.blend -P espelhar_metade.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json
import numpy as np
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
antes = {"vertices": len(me.vertices), "faces": len(me.polygons)}
nome = [g.name for g in LO.vertex_groups]; idx = {g: i for i, g in enumerate(nome)}
par = {}
for i, g in enumerate(nome):
    for a, b in (("E", "D"), ("D", "E")):
        if g.endswith(a) and g[:-1] + b in idx: par[i] = idx[g[:-1] + b]
print("pares E<->D:", len(par) // 2)
cn = np.empty(len(me.loops) * 3); me.corner_normals.foreach_get("vector", cn); cn = cn.reshape(-1, 3)
bm = bmesh.new(); bm.from_mesh(me)
ln = bm.loops.layers.float_vector.new("nrm_tmp")
for f in bm.faces:
    for l in f.loops: l[ln] = cn[l.index]
dl = bm.verts.layers.deform.active
r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, 0), plane_no=(1, 0, 0), clear_outer=True)
for v in bm.verts:
    if abs(v.co.x) < 2e-5: v.co.x = 0.0
metade = len(bm.verts)
d = bmesh.ops.duplicate(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:])
nv = [e for e in d["geom"] if isinstance(e, bmesh.types.BMVert)]; nf = [e for e in d["geom"] if isinstance(e, bmesh.types.BMFace)]
for v in nv:
    v.co.x = -v.co.x
    dv = v[dl]; w = {k: dv[k] for k in dv.keys()}; dv.clear()
    for k, x in w.items(): dv[par.get(k, k)] = x
bmesh.ops.reverse_faces(bm, faces=nf, flip_multires=False)
for f in nf:
    for l in f.loops: n_ = l[ln]; l[ln] = (-n_[0], n_[1], n_[2])
costura = [v for v in bm.verts if v.co.x == 0.0]
bmesh.ops.remove_doubles(bm, verts=costura, dist=1e-5)
costura = [v for v in bm.verts if v.co.x == 0.0]
for v in costura:                                          # pesos simetricos na linha central
    dv = v[dl]; w = {k: dv[k] for k in dv.keys()}; s = {}
    for k, x in w.items(): s[k] = s.get(k, 0) + 0.5 * x; s[par.get(k, k)] = s.get(par.get(k, k), 0) + 0.5 * x
    dv.clear()
    for k, x in s.items(): dv[k] = x
grandes = [f for f in bm.faces if len(f.verts) > 4]
if grandes: bmesh.ops.triangulate(bm, faces=grandes)
bm.to_mesh(me); bm.free(); me.update()
nrm = me.attributes["nrm_tmp"]; a = np.empty(len(me.loops) * 3); nrm.data.foreach_get("vector", a)
a = a.reshape(-1, 3); a /= np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-9)
me.attributes.remove(me.attributes["nrm_tmp"]); me.normals_split_custom_set(a.tolist()); me.update()
# a metade D e mais densa: o espelho passa do limite de 20 mil tris do Roblox -> Decimate SIMETRICO (eixo X), cabeca
# preservada (peso baixo = menos reducao); normais personalizadas transferidas da malha antes da reducao
ALVO_TRIS = 18700
tris = sum(len(p.vertices) - 2 for p in me.polygons)
if tris > ALVO_TRIS:
    fonte = LO.copy(); fonte.data = me.copy(); bpy.context.scene.collection.objects.link(fonte); fonte.modifiers.clear()
    gcab = [idx[g] for g in ("Cabeca", "Mandibula", "OrelhaE", "OrelhaD")]
    dens = LO.vertex_groups.new(name="_densidade")
    for v in me.vertices:
        h = sum(g.weight for g in v.groups if g.group in gcab); dens.add([v.index], 1.0 - 0.85 * min(1.0, h), "REPLACE")
    bpy.context.view_layer.objects.active = LO
    md = LO.modifiers.new("Reduzir", "DECIMATE"); md.decimate_type = "COLLAPSE"; md.use_symmetry = True; md.symmetry_axis = "X"
    md.vertex_group = "_densidade"; md.vertex_group_factor = 1.0; md.ratio = ALVO_TRIS / tris * 0.97
    with bpy.context.temp_override(object=LO, active_object=LO):
        bpy.ops.object.modifier_move_to_index(modifier="Reduzir", index=0); bpy.ops.object.modifier_apply(modifier="Reduzir")
    LO.vertex_groups.remove(LO.vertex_groups["_densidade"])
    dt = LO.modifiers.new("Normais", "DATA_TRANSFER"); dt.object = fonte; dt.use_loop_data = True; dt.data_types_loops = {"CUSTOM_NORMAL"}
    dt.loop_mapping = "POLYINTERP_NEAREST"
    with bpy.context.temp_override(object=LO, active_object=LO):
        bpy.ops.object.modifier_move_to_index(modifier="Normais", index=0); bpy.ops.object.modifier_apply(modifier="Normais")
    fd = fonte.data; bpy.data.objects.remove(fonte); bpy.data.meshes.remove(fd)
    # limpa pesos residuais minimos e renormaliza (max 4 influencias, como no rig)
    for v in me.vertices:
        gs = sorted([(g.weight, g.group) for g in v.groups], reverse=True)
        for wgt, gidx in gs[4:]: LO.vertex_groups[gidx].remove([v.index])
        s = sum(wgt for wgt, _ in gs[:4])
        if s > 0:
            for wgt, gidx in gs[:4]: LO.vertex_groups[gidx].add([v.index], wgt / s, "REPLACE")
    me.update(); print("REDUCAO tris %d -> %d" % (tris, sum(len(p.vertices) - 2 for p in me.polygons)))
# conferencia de simetria: cada vertice tem um espelho exato
co = np.array([v.co[:] for v in me.vertices])
from mathutils.kdtree import KDTree
kd = KDTree(len(co))
for i, p in enumerate(co): kd.insert(p, i)
kd.balance()
erro = max(kd.find((-p[0], p[1], p[2]))[2] for p in co)
sem = sum(1 for v in me.vertices if not v.groups)
depois = {"vertices": len(me.vertices), "faces": len(me.polygons), "tris": sum(len(p.vertices) - 2 for p in me.polygons),
          "vertices_costura": len(costura), "erro_espelho_max": float(erro), "vertices_sem_peso": sem, "zmin": float(co[:, 2].min())}
print("ANTES", antes, "DEPOIS", depois)
json.dump({"antes": antes, "depois": depois}, open(os.path.join(OUT, "espelhar_metade.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("ESPELHAR_METADE_OK")
