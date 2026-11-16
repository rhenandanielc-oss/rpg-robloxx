"""Rodada 3 do complemento (v4) sobre low_v3/ (preservada): limpeza de malha, pose neutra das patas, LODs e exports.
- Cabeca: remove vertices/arestas soltos (sobras do recorte dos olhos: causa do aviso "malha invalida"), dissolve
  faces degeneradas sem fundir os labios cortados, orienta o interior da boca de forma coerente (por componente).
- Corpo/cabeca: fecha FUROS acidentais (bordas fora da costura, boca e olhos) com UV interpolada dos vizinhos.
- Pose neutra: traseira direita estava 1,17 stud a frente e a dianteira esquerda aberta para fora (Meshy copiou o
  passo da referencia). Cada perna gira com peso suave em torno do quadril/ombro; os cartoes da perna acompanham;
  as UVs e texturas continuam valendo (nada e re-assado). Pes reassentados no chao.
- Opcao A da marca direita (decisao do usuario): remove o objeto OPCAO_Marca_Direita.
- LODs refeitos (com limpeza), GLBs, rig_pivos.json.
Uso: blender -b low_v3/CR_LoboArtico_LOW.blend -P ajuste_r3.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, math, shutil
import numpy as np
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.hide_set(False); o.select_set(True); bpy.context.view_layer.objects.active = o
for im in bpy.data.images:                                              # texturas: copias proprias da v4
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()
op_b = bpy.data.objects.get("OPCAO_Marca_Direita")
if op_b: bpy.data.objects.remove(op_b)
cab, corpo, pel = bpy.data.objects["LOW_Cabeca"], bpy.data.objects["LOW_Corpo"], bpy.data.objects["LOW_Pelagem"]
BA, BB = PIV["mandibula"]["linha_boca"]; CANTO = PIV["mandibula"]["canto_y"]
OLHOS = [V(o["centro_globo"]) for o in PIV["olhos"].values()]
COST_P, COST_N = V(PIV["costura"]["ponto"]), V(PIV["costura"]["normal"])
def intencional(p):
    return (abs((p - COST_P).dot(COST_N)) < 0.03 or (p.y < CANTO + 0.05 and abs(p.z - (BA + BB * p.y)) < 0.15)
            or any((p - s).length < 0.35 for s in OLHOS))
def tapar(o):
    """fecha furos (lacos de borda FECHADOS que nao sao cortes intencionais) criando a face do laco; UV de cada canto
    = media das UVs do vertice nas faces vizinhas"""
    bm = bmesh.new(); bm.from_mesh(o.data); uvl = bm.loops.layers.uv.active
    ar = [e for e in bm.edges if e.is_boundary and not intencional((e.verts[0].co + e.verts[1].co) / 2)]
    antes = len(ar); viz = {}
    for e in ar:
        for v in e.verts: viz.setdefault(v, []).append(e)
    vis, novas = set(), []
    for e0 in ar:
        if e0 in vis: continue
        laco, v, e = [e0.verts[0]], e0.verts[1], e0; vis.add(e0); ok = True
        while v is not laco[0]:
            laco.append(v); prox = [x for x in viz.get(v, []) if x is not e and x not in vis]
            if len(viz.get(v, [])) != 2 or not prox: ok = False; break
            e = prox[0]; vis.add(e); v = e.other_vert(v)
        if not ok or len(laco) < 3 or len(laco) > 16: continue
        try: f = bm.faces.new(laco)
        except ValueError: continue
        f.normal_update(); viz_f = [g for x in f.edges for g in x.link_faces if g is not f]
        if viz_f and f.normal.dot(viz_f[0].normal) < 0: f.normal_flip()
        novas.append(f)
    tri = bmesh.ops.triangulate(bm, faces=novas)["faces"]; novas = set(tri)
    for f in novas:
        f.smooth = True
        for l in f.loops:
            uvs = [l2[uvl].uv.copy() for l2 in l.vert.link_loops if l2.face not in novas]
            if uvs: l[uvl].uv = sum(uvs, V((0, 0))) / len(uvs)
    restantes = sum(1 for e in bm.edges if e.is_boundary and not intencional((e.verts[0].co + e.verts[1].co) / 2))
    bm.to_mesh(o.data); bm.free(); return antes, restantes
# ------------------------------------------------------------------ 1) cabeca: soltos, degeneradas, interior da boca
bm = bmesh.new(); bm.from_mesh(cab.data)
soltos_v = [v for v in bm.verts if not v.link_faces]; soltos_e = [e for e in bm.edges if not e.link_faces]
bmesh.ops.delete(bm, geom=soltos_e, context="EDGES"); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
deg = [f for f in bm.faces if f.calc_area() < 1e-9]
bmesh.ops.delete(bm, geom=deg, context="FACES_ONLY"); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
dl = bm.verts.layers.deform.active
gb = {cab.vertex_groups[n].index for n in ("Boca_Superior", "Boca_Inferior")}
inter = [f for f in bm.faces if all(set(v[dl].keys()) & gb for v in f.verts)]
# componentes conexos do interior; cada um orientado de forma coerente e com a maioria olhando para o eixo da boca
restam, comps = set(inter), []
while restam:
    f0 = restam.pop(); comp, pilha = [f0], [f0]
    while pilha:
        f = pilha.pop()
        for e in f.edges:
            for g in e.link_faces:
                if g in restam: restam.discard(g); comp.append(g); pilha.append(g)
    comps.append(comp)
cx = 0.05
for comp in comps:
    bmesh.ops.recalc_face_normals(bm, faces=comp)
    voto = 0.0
    for f in comp:
        c = f.calc_center_median(); alvo = V((cx, min(c.y, CANTO - 0.12), BA + BB * c.y)); voto += f.normal.dot((alvo - c).normalized())
    if len(comp) > 30 and voto < 0:                                     # superficies da boca (dentes/lingua sao fechados: ficam para fora)
        for f in comp: f.normal_flip()
bm.to_mesh(cab.data); bm.free()
print("R3 cabeca: arestas soltas", len(soltos_e), "vertices soltos", len(soltos_v), "degeneradas", len(deg), "componentes do interior", len(comps), flush=True)
def abas(o):
    """remove triangulos minusculos presos so pelos vertices (sobras da decimacao: a superficie em volta ja e fechada)"""
    bm = bmesh.new(); bm.from_mesh(o.data)
    lixo = [f for f in bm.faces if all(e.is_boundary for e in f.edges) and f.calc_area() < 0.001]
    bmesh.ops.delete(bm, geom=lixo, context="FACES"); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(o.data); bm.free(); return len(lixo)
for o in (corpo, cab):
    print("R3", o.name, "triangulos soltos removidos", abas(o), flush=True)
    a_, r_ = tapar(o); print("R3 furos", o.name, "bordas acidentais antes", a_, "depois", r_, flush=True)

# ------------------------------------------------------------------ 2) pose neutra das patas (so a malha de jogo)
def patas():
    P = np.array([v.co[:] for v in corpo.data.vertices if v.co.z < 0.30]); c = np.array([[1, -3.5], [-1, -3.5], [1, 2], [-1, 2]], float)
    for _ in range(30):
        k = ((P[:, None, :2] - c[None]) ** 2).sum(-1).argmin(1); c = np.array([P[k == i, :2].mean(0) for i in range(4)])
    return c
c0 = patas(); print("R3 patas antes (x,y): DE %s DD %s TE %s TD %s" % tuple(str(np.round(x, 2)) for x in c0), flush=True)
CXc = 0.12                                                               # eixo do tronco (pelagem_r2: cx do corpo)
def girar_perna(objs, pivo, eixo, ang, regiao, peso):
    M = Matrix.Rotation(ang, 3, eixo); n = 0
    for o in objs:
        for v in o.data.vertices:
            if not regiao(v.co): continue
            w = peso(v.co)
            if w <= 0: continue
            q = Matrix.Rotation(ang * w, 3, eixo) @ (v.co - pivo); v.co = pivo + q; n += 1
        o.data.update()
    return n
# traseira direita: gira em torno do quadril (eixo X) ate o pe alinhar com o da esquerda
hd = V((c0[3, 0], 1.75, 4.1)); alvo_y = c0[2, 1]; raio = hd.z
ang_t = math.atan2(alvo_y - hd.y, raio) - math.atan2(c0[3, 1] - hd.y, raio)
reg_t = lambda p: p.x < CXc - 0.2 and 0.0 < p.y < 3.3 and p.z < 4.3
n_t = girar_perna([corpo, pel], hd, V((1, 0, 0)), ang_t, reg_t, lambda p: suave((hd.z - 0.4 - p.z) / 1.0))
# dianteira esquerda: fecha a abertura lateral em torno do ombro (eixo Y)
ombro = V((c0[0, 0] - 0.4, c0[0, 1], 4.3)); alvo_x = CXc + (CXc - c0[1, 0])
ang_d = math.atan2(c0[0, 0] - ombro.x, ombro.z) - math.atan2(alvo_x - ombro.x, ombro.z)
reg_d = lambda p: p.x > CXc + 0.2 and -4.6 < p.y < -2.2 and p.z < 4.4
n_d = girar_perna([corpo, pel], ombro, V((0, 1, 0)), ang_d, reg_d, lambda p: suave((ombro.z - 0.5 - p.z) / 1.0))
c1 = patas()
print("R3 pose: traseira dir girada %.1f graus (%d vert), dianteira esq %.1f graus (%d vert)" % (math.degrees(ang_t), n_t, math.degrees(ang_d), n_d), flush=True)
print("R3 patas depois (x,y): DE %s DD %s TE %s TD %s" % tuple(str(np.round(x, 2)) for x in c1), flush=True)
# pes de volta ao chao (cada pata: o ponto mais baixo em z=0, ajuste suave so na pata)
for i in range(4):
    cx_, cy_ = c1[i]
    pts = [v for v in corpo.data.vertices if (v.co.x - cx_) ** 2 + (v.co.y - cy_) ** 2 < 0.5 ** 2 and v.co.z < 1.2]
    if not pts: continue
    dz = -min(v.co.z for v in pts)
    for o in (corpo, pel):
        for v in o.data.vertices:
            if (v.co.x - cx_) ** 2 + (v.co.y - cy_) ** 2 < 0.6 ** 2 and v.co.z < 1.6: v.co.z += dz * (1 - suave((v.co.z - 0.4) / 1.2))
        o.data.update()

# ------------------------------------------------------------------ 3) LODs (com limpeza), exports, pivos
def lod(o, alvo, nome):
    old = bpy.data.objects.get(nome)
    if old: bpy.data.objects.remove(old)
    c = o.copy(); c.data = o.data.copy(); c.name = c.data.name = nome; sc.collection.objects.link(c); ativo(c)
    d = c.modifiers.new("D", "DECIMATE"); d.ratio = min(1.0, alvo / max(tris(c), 1)); bpy.ops.object.modifier_apply(modifier="D")
    bm = bmesh.new(); bm.from_mesh(c.data)
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS"); bm.to_mesh(c.data); bm.free()
    c.hide_render = True; return c
lod(cab, 3600, "LOD1_Cabeca"); lod(corpo, 6500, "LOD1_Corpo"); lod(cab, 1100, "LOD2_Cabeca"); lod(corpo, 2000, "LOD2_Corpo")
old = bpy.data.objects.get("LOD1_Pelagem")
if old: bpy.data.objects.remove(old)
p1 = pel.copy(); p1.data = pel.data.copy(); p1.name = p1.data.name = "LOD1_Pelagem"; sc.collection.objects.link(p1)
bm = bmesh.new(); bm.from_mesh(p1.data); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[f for i, f in enumerate(bm.faces) if (i // 4) % 2 == 1], context="FACES"); bm.to_mesh(p1.data); bm.free(); p1.hide_render = True
ob = {o.name: o for o in sc.objects}
def exportar(nomes, arq):
    bpy.ops.object.select_all(action="DESELECT")
    for n_ in nomes: ob[n_].hide_set(False); ob[n_].select_set(True)
    bpy.context.view_layer.objects.active = ob[nomes[0]]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, arq), export_format="GLB", use_selection=True, export_image_format="AUTO", export_yup=True)
exportar(["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"], "CR_LoboArtico_LOW.glb")
exportar(["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"], "CR_LoboArtico_LOD1.glb")
exportar(["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"], "CR_LoboArtico_LOD2.glb")
PIV["pose_neutra"] = {"traseira_direita_graus": math.degrees(ang_t), "dianteira_esquerda_graus": math.degrees(ang_d),
                      "patas_xy_depois": np.round(c1, 3).tolist(), "nota": "ajuste so na malha de jogo; texturas/UV inalteradas"}
PIV["marca_direita"] = "opcao A (sem marca) - decisao do usuario 03/11/2026"
json.dump(PIV, open(os.path.join(OUT, "rig_pivos.json"), "w"), indent=1)
for n_ in ("LOD1_Cabeca", "LOD1_Corpo", "LOD2_Cabeca", "LOD2_Corpo", "LOD1_Pelagem"): ob[n_].hide_set(True)
reg = {n_: tris(ob[n_]) for n_ in ob if ob[n_].type == "MESH"}; print("R3_TRIS", reg, flush=True)
json.dump(reg, open(os.path.join(OUT, "custo_v4.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend"))
print("R3_OK")
