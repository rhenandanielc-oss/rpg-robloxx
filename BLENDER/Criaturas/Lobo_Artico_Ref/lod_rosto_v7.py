"""v7: LOD1/LOD2 com reducao PROTEGIDA do rosto, sobre low_v6/ (preservada; low_v5/ tambem intacta).
Diagnostico da v6 (diag em review/v7_final/diag_antes.txt):
- cabeca e corpo eram decimados SEPARADOS -> as bordas da costura deixam de coincidir (fresta 0,032 no LOD1, 0,162 no LOD2);
- Decimate igual no rosto todo -> 3-11 vertices nas palpebras do LOD1, 2-8 no LOD2, corte da boca fechado no LOD2.
Correcao:
0) LOD0 (LOW_Cabeca), so defeitos que atrapalham reducao/deformacao: a aresta nao-manifold do canto do olho E (aresta de
   0,014 com 4 faces: duas dobras minusculas) e colapsada; faces do anel do olho / saco bucal com enrolamento contrario ao
   dos vizinhos E normal geometrica oposta (= face virada numa superficie lisa) sao viradas por maioria dos vizinhos.
   Nao funde os labios cortados (vertices duplicados intencionais).
1) Cabeca + corpo UNIDOS numa malha so (so os vertices da costura sao soldados), decimados juntos e separados de novo
   pelo material: a costura vira a MESMA polilinha nos dois lados (fresta 0 por construcao).
2) Grupo Protecao_LOD (0 = protegido, 1 = reduz livre) no Decimate (vertex_group + fator): margens das palpebras e globo,
   corte dos labios + cantos, faixa de articulacao da Mandibula (peso entre 0,05 e 0,95) e saco bucal parcialmente.
   O fator de protecao e mais fraco no LOD2. O corpo recebe peso <1 so para dividir o orcamento (busca automatica).
3) Grupos de vertices (Palpebra_*, Mandibula, Boca_*) sao interpolados pelo proprio Decimate (nunca entre labios: o corte
   separa as duas superficies); conferidos depois por teste_lod_v7.py e auditar_lod_v7.py.
Uso: blender -b low_v6/CR_LoboArtico_LOW.blend -P lod_rosto_v7.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, math, shutil
from mathutils import Vector as V
from mathutils.kdtree import KDTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def tris(me): return sum(len(p.vertices) - 2 for p in me.polygons)
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.hide_set(False); o.select_set(True); bpy.context.view_layer.objects.active = o
for im in bpy.data.images:                                              # texturas: copias proprias da v7
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()
CP, CN = V(PIV["costura"]["ponto"]), V(PIV["costura"]["normal"])
BA, BB = PIV["mandibula"]["linha_boca"]; CANTO = PIV["mandibula"]["canto_y"]
OLHOS = [(V(o["centro_globo"]), o["raio_margem"]) for o in PIV["olhos"].values()]
cab, corpo = bpy.data.objects["LOW_Cabeca"], bpy.data.objects["LOW_Corpo"]
for o in (cab, corpo): assert o.matrix_world == o.matrix_world.Identity(4), o.name
RELAT = {}
# ------------------------------------------------------------------ 0) defeitos do LOD0 que atrapalham reducao/deformacao
bm = bmesh.new(); bm.from_mesh(cab.data)
nm = [e for e in bm.edges if len(e.link_faces) > 2]
RELAT["lod0_nao_manifold_antes"] = len(nm)
for e in nm:
    if e.is_valid and e.calc_length() < 0.03: bmesh.ops.collapse(bm, edges=[e])
bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
RELAT["lod0_nao_manifold_depois"] = sum(1 for e in bm.edges if len(e.link_faces) > 2)
def mesmo_sentido(e):
    f1, f2 = e.link_faces; a, b = e.verts
    def ordem(f):
        vs = list(f.verts); i = vs.index(a); return vs[(i + 1) % len(vs)] == b
    return ordem(f1) == ordem(f2)
def viradas():                                                          # enrolamento contrario + normal oposta = face virada
    return [e for e in bm.edges if len(e.link_faces) == 2 and mesmo_sentido(e) and e.link_faces[0].normal.dot(e.link_faces[1].normal) < -0.5]
RELAT["lod0_invertidas_antes"] = sum(1 for e in bm.edges if len(e.link_faces) == 2 and mesmo_sentido(e))
for _ in range(12):
    cand = {f for e in viradas() for f in e.link_faces}
    if not cand: break
    mudou = False
    for f in cand:
        ruim = sum(1 for e in f.edges if len(e.link_faces) == 2 and mesmo_sentido(e)); bom = sum(1 for e in f.edges if len(e.link_faces) == 2) - ruim
        if ruim > bom: f.normal_flip(); f.normal_update(); mudou = True
    if not mudou: break
RELAT["lod0_invertidas_depois"] = sum(1 for e in bm.edges if len(e.link_faces) == 2 and mesmo_sentido(e))
RELAT["lod0_dobras_restantes"] = sum(1 for e in bm.edges if len(e.link_faces) == 2 and mesmo_sentido(e) and e.link_faces[0].normal.dot(e.link_faces[1].normal) > 0.5)
bm.to_mesh(cab.data); bm.free(); cab.data.update()
RELAT["lod0_tris"] = tris(cab.data); print("V7 LOD0", RELAT, flush=True)
# ------------------------------------------------------------------ 1) peso de protecao na cabeca (LOD0)
bm = bmesh.new(); bm.from_mesh(cab.data)
def regiao_boca(p): return p.y < CANTO + 0.05 and abs(p.z - (BA + BB * p.y)) < 0.20
corte = [v.co.copy() for v in bm.verts if v.is_boundary and regiao_boca(v.co)]
bm.free()
kd_c = KDTree(len(corte))
for i, p in enumerate(corte): kd_c.insert(p, i)
kd_c.balance()
# perfis de protecao por LOD: olho (margem protegida ate a*R, rampa de b*R), corte (raio protegido, rampa),
# articulacao e saco bucal (peso maximo). LOD2 protege so o essencial (margem interna, borda do corte, cantos).
PERFIS = {1: dict(olho=(1.3, 1.1), corte=(0.05, 0.22), artic=0.35, saco=0.6, nariz=(0.18, 0.25, 0.3)),
          2: dict(olho=(1.1, 0.6), corte=(0.02, 0.10), artic=0.7, saco=1.0, nariz=(0.18, 0.25, 0.5))}
NARIZ = V(PIV.get("endireitar_v6", {}).get("nariz_depois", (0, -6.66, 5.37)))
def peso_prot(v, perfil=PERFIS[1]):
    p = v.co; ws = {cab.vertex_groups[e.group].name: e.weight for e in v.groups}
    w = 1.0; a, b = perfil["olho"]
    for c, R in OLHOS:                                                  # margem das palpebras e globo
        w = min(w, suave(((p - c).length - a * R) / (b * R)))
    if corte:                                                          # corte dos labios e cantos
        r0, r1 = perfil["corte"]; d = kd_c.find(p)[2]; w = min(w, suave((d - r0) / r1))
    m = ws.get("Mandibula", 0.0)
    if 0.05 < m < 0.95: w = min(w, perfil["artic"])                    # articulacao (gradiente da mandibula)
    if ws.get("Boca_Superior", 0) > 0.5 or ws.get("Boca_Inferior", 0) > 0.5: w = min(w, perfil["saco"])
    r0, r1, piso = perfil["nariz"]                                     # volume do nariz (no LOD2 v7 sem isso ele achatava)
    w = min(w, piso + (1 - piso) * suave(((p - NARIZ).length - r0) / r1))
    return w
# ------------------------------------------------------------------ 2) LODs unidos, protegidos e separados de novo
# A cabeca tem a PELE (componente que toca a costura: pele, aneis dos olhos, labios e saco bucal) e PECAS soltas (globos
# dos olhos, dentes, lingua). As pecas sao pequenas e curvas: numa reducao conjunta com o corpo elas seguram o orcamento
# (medido: ~1,7k tris de pecas no LOD2). Por isso: pele+corpo unidos (costura) com protecao; pecas com orcamento proprio.
def copia(o, nome):
    c = o.copy(); c.data = o.data.copy(); c.name = c.data.name = nome; sc.collection.objects.link(c); return c
def manter_faces(o, cond):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not cond(f)], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS"); bm.to_mesh(o.data); bm.free()
def componente_pele(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    semente = [f for f in bm.faces if any(e.is_boundary and abs(((e.verts[0].co + e.verts[1].co) / 2 - CP).dot(CN)) < 0.03 for e in f.edges)]
    vis = set(semente); pilha = list(semente)
    while pilha:
        f = pilha.pop()
        for e in f.edges:
            for g in e.link_faces:
                if g not in vis: vis.add(g); pilha.append(g)
    ids = {f.index for f in vis}; bm.free(); return ids
def base_unida(nivel, perfil):
    c0 = copia(cab, "tmp_cab"); gp = c0.vertex_groups.new(name="Protecao_LOD")
    for v in c0.data.vertices: gp.add([v.index], peso_prot(v, perfil), "REPLACE")
    pele = componente_pele(c0)
    pecas = copia(c0, "LOD%d_Pecas" % nivel); manter_faces(pecas, lambda f: f.index not in pele); manter_faces(c0, lambda f: f.index in pele)
    c1 = copia(corpo, "tmp_corpo"); gb = c1.vertex_groups.new(name="Protecao_LOD"); gb.add([v.index for v in c1.data.vertices], 1.0, "REPLACE")
    ativo(c0); c1.select_set(True); bpy.ops.object.join(); u = bpy.context.active_object; u.name = u.data.name = "LOD%d_Unida" % nivel
    bm = bmesh.new(); bm.from_mesh(u.data)
    cost = [v for v in bm.verts if v.is_boundary and abs((v.co - CP).dot(CN)) < 0.03]
    n0 = len(bm.verts); bmesh.ops.remove_doubles(bm, verts=cost, dist=1e-5); bm.to_mesh(u.data); bm.free()
    print("V7 unida LOD%d: vertices soldados na costura %d, pecas %d tris" % (nivel, n0 - len(u.data.vertices), tris(pecas.data)), flush=True)
    return u, pecas
def contar(u, ratio, fator):
    d = u.modifiers.get("D") or u.modifiers.new("D", "DECIMATE"); d.ratio = ratio; d.vertex_group = "Protecao_LOD"; d.vertex_group_factor = fator
    me = u.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    th = sum(len(p.vertices) - 2 for p in me.polygons if p.material_index == 0); tb = sum(len(p.vertices) - 2 for p in me.polygons if p.material_index == 1)
    u.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear(); return th, tb
def peso_corpo(u, wb):
    gp = u.vertex_groups["Protecao_LOD"]; ids, cab_ids = set(), set()
    for p in u.data.polygons: (ids if p.material_index == 1 else cab_ids).update(p.vertices)
    gp.add([i for i in ids if i not in cab_ids], wb, "REPLACE")
from mathutils.bvhtree import BVHTree
def desdobrar(o, ref):
    """faces de PELE viradas pela reducao (normal oposta a da face mais proxima do LOD0): os vertices livres voltam para o
    ponto mais proximo da superficie do LOD0 (repete); travados: costura, bordas (corte dos labios) e vertices de outras faces"""
    bm0 = bmesh.new(); bm0.from_mesh(ref.data); bm0.faces.ensure_lookup_table(); bvh = BVHTree.FromBMesh(bm0)
    bm = bmesh.new(); bm.from_mesh(o.data); uv = bm.loops.layers.uv.active
    def viradas():
        out = []
        for f in bm.faces:
            if f.loops[0][uv].uv.x > 0.90: continue
            loc, n, i, d = bvh.find_nearest(f.calc_center_median())
            if loc is not None and (f.normal.dot(bm0.faces[i].normal) < -0.2 or d > 0.12): out.append(f)
        return out
    antes = len(viradas())
    for it in range(6):
        fs = viradas()
        if not fs: break
        for f in fs:
            for v in f.verts:
                if v.is_boundary or any(g.loops[0][uv].uv.x > 0.90 for g in v.link_faces): continue
                if it < 3:
                    loc = bvh.find_nearest(v.co)[0]
                    if loc is not None: v.co = loc
                else:                                                   # sobrou: suaviza no anel de vizinhos
                    v.co = sum((e.other_vert(v).co for e in v.link_edges), V()) / len(v.link_edges)
        bm.normal_update()
    depois = len(viradas()); bm.to_mesh(o.data); bm.free(); bm0.free(); return antes, depois
def fechar_furos_costura(u):
    """na malha UNIDA (pele+corpo) a costura e interior: qualquer borda aberta a menos de 0,4 do anel da costura do LOD0
    e um furo que a reducao abriu entre cabeca e corpo. Fecha (holes_fill) com material e UV dos vizinhos, antes de separar"""
    bc = bmesh.new(); bc.from_mesh(cab.data); anel = [v.co.copy() for v in bc.verts if v.is_boundary and abs((v.co - CP).dot(CN)) < 0.03]; bc.free()
    kd = KDTree(len(anel))
    for i, p in enumerate(anel): kd.insert(p, i)
    kd.balance()
    bm = bmesh.new(); bm.from_mesh(u.data); uv = bm.loops.layers.uv.active
    ar = [e for e in bm.edges if e.is_boundary and kd.find((e.verts[0].co + e.verts[1].co) / 2)[2] < 0.4]
    novas = bmesh.ops.holes_fill(bm, edges=ar, sides=16)["faces"] if ar else []
    novas = bmesh.ops.triangulate(bm, faces=novas)["faces"] if novas else []
    for f in novas:
        viz = [g for e in f.edges for g in e.link_faces if g is not f and g not in novas]
        if viz:
            f.material_index = viz[0].material_index
            if f.normal.dot(viz[0].normal) < 0: f.normal_flip()
        for l in f.loops:
            uvs = [l2[uv].uv.copy() for l2 in l.vert.link_loops if l2.face not in novas and l2.face.material_index == f.material_index]
            if uvs: l[uv].uv = sum(uvs, V((0, 0))) / len(uvs)
    bm.to_mesh(u.data); bm.free(); return len(ar), len(novas)
def fazer_lod(nivel, alvo_corpo, fatores, teto_pele, ratio_pecas):
    u, pecas = base_unida(nivel, PERFIS[nivel]); mats = [m for m in u.data.materials]
    assert mats[0] == cab.data.materials[0] and mats[1] == corpo.data.materials[0], [m.name for m in mats]
    melhor = None                                                       # maior protecao (fator) que cabe no teto da pele
    for fator in fatores:
        for wb in (1.0, 0.8, 0.6, 0.4, 0.25):                           # corpo menos livre -> sobra mais reducao para a cabeca
            peso_corpo(u, wb); lo, hi = 0.01, 1.0
            for _ in range(14):                                         # ratio pelo alvo do corpo
                r = (lo + hi) / 2; th, tb = contar(u, r, fator)
                if tb > alvo_corpo: hi = r
                else: lo = r
            th, tb = contar(u, lo, fator); print("V7 LOD%d busca fator %.2f wb %.2f ratio %.4f -> pele %d corpo %d" % (nivel, fator, wb, lo, th, tb), flush=True)
            melhor = (wb, lo, th, tb, fator)
            if th <= teto_pele: break
        if melhor[2] <= teto_pele: break
    wb, r, th, tb, fator = melhor; peso_corpo(u, wb); contar(u, r, fator); ativo(u); bpy.ops.object.modifier_apply(modifier="D")
    furos = fechar_furos_costura(u); print("V7 LOD%d furos junto a costura: %d arestas abertas -> %d faces novas" % (nivel, *furos), flush=True)
    ativo(pecas); d = pecas.modifiers.new("D", "DECIMATE"); d.ratio = ratio_pecas; bpy.ops.object.modifier_apply(modifier="D")
    t_pecas = tris(pecas.data)
    partes = {}
    for k, nome in ((0, "LOD%d_Cabeca" % nivel), (1, "LOD%d_Corpo" % nivel)):
        old = bpy.data.objects.get(nome)
        if old: bpy.data.objects.remove(old)
        bm = bmesh.new(); bm.from_mesh(u.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index != k], context="FACES")
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        for f in bm.faces: f.material_index = 0
        me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free(); me.materials.append(mats[k])
        o = bpy.data.objects.new(nome, me); sc.collection.objects.link(o)
        for g in u.vertex_groups: o.vertex_groups.new(name=g.name)      # mesma ordem = mesmos indices da camada deform
        partes[k] = o
    dob = desdobrar(partes[0], cab); print("V7 LOD%d faces de pele viradas: %d -> %d" % (nivel, *dob), flush=True)
    ativo(partes[0]); pecas.select_set(True); bpy.ops.object.join()     # pecas de volta na cabeca (grupos por nome)
    for k, o in partes.items():
        o.vertex_groups.remove(o.vertex_groups["Protecao_LOD"])
        if k == 1:
            for g in list(o.vertex_groups): o.vertex_groups.remove(g)
        bm = bmesh.new(); bm.from_mesh(o.data)
        if k == 1:                                                      # ilhas minusculas que a reducao solta no corpo
            vis, ilhas = set(), []
            for f0 in bm.faces:
                if f0 in vis: continue
                fs, pilha = [], [f0]; vis.add(f0)
                while pilha:
                    f = pilha.pop(); fs.append(f)
                    for e in f.edges:
                        for g in e.link_faces:
                            if g not in vis: vis.add(g); pilha.append(g)
                if len(fs) <= 3 and sum(f.calc_area() for f in fs) < 1e-3: ilhas += fs
            bmesh.ops.delete(bm, geom=ilhas, context="FACES"); RELAT.setdefault("ilhas_removidas_corpo", {})["LOD%d" % nivel] = len(ilhas)
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS"); bm.to_mesh(o.data); bm.free()
        o.hide_render = True
    bpy.data.objects.remove(u)
    RELAT["LOD%d" % nivel] = {"peso_corpo": wb, "ratio": r, "fator_protecao": fator, "ratio_pecas": ratio_pecas, "tris_pele": th,
                              "tris_pecas": t_pecas, "faces_viradas_antes_depois": dob, "furos_corpo_fechados": furos, "tris_cabeca": tris(partes[0].data), "tris_corpo": tris(partes[1].data)}
    return partes
fazer_lod(1, 6498, (10.0, 6.0, 4.0), 3800, 0.35)                        # v6: cabeca 3598 / corpo 6498
fazer_lod(2, 1998, (3.0, 2.0, 1.4, 1.0, 0.7, 0.5), 1250, 0.14)          # v6: cabeca 1097 / corpo 1998
# grupo de protecao fica documentado so no LOD0 (nao vai ao GLB; nao interfere no rig)
g = cab.vertex_groups.new(name="Protecao_LOD")
for v in cab.data.vertices: g.add([v.index], peso_prot(v, PERFIS[1]), "REPLACE")
print("V7 RELAT", json.dumps(RELAT), flush=True)
# ------------------------------------------------------------------ 3) exports e pivos
ob = {o.name: o for o in sc.objects}
def exportar(nomes, arq):
    bpy.ops.object.select_all(action="DESELECT")
    for n_ in nomes: ob[n_].hide_set(False); ob[n_].select_set(True)
    bpy.context.view_layer.objects.active = ob[nomes[0]]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, arq), export_format="GLB", use_selection=True, export_image_format="AUTO", export_yup=True)
exportar(["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"], "CR_LoboArtico_LOW.glb")
exportar(["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"], "CR_LoboArtico_LOD1.glb")
exportar(["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"], "CR_LoboArtico_LOD2.glb")
PIV["lod_v7"] = dict(RELAT, nota="LOD1/LOD2 = cabeca+corpo decimados juntos (costura compartilhada) com grupo Protecao_LOD "
                     "(margens das palpebras, corte dos labios/cantos, articulacao da mandibula, saco bucal); grupos interpolados pelo Decimate. "
                     "Pivos iguais aos do LOD0 (mesma escala/posicao).")
json.dump(PIV, open(os.path.join(OUT, "rig_pivos.json"), "w"), indent=1)
for n_ in ("LOD1_Cabeca", "LOD1_Corpo", "LOD2_Cabeca", "LOD2_Corpo", "LOD1_Pelagem"): ob[n_].hide_set(True)
print("V7_TRIS", {n_: tris(ob[n_].data) for n_ in ob if ob[n_].type == "MESH"}, flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend")); print("V7_OK", flush=True)
