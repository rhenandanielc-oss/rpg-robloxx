"""Teste visual SEM rig do refino: numa copia da cabeca, abre a mandibula (gira o que fica abaixo do corte dos
labios em torno do pivo sugerido) e fecha as palpebras (gira em torno do centro do globo). So para revisao; nao salva.
Uso: blender -b low_ref/CR_LoboArtico_LOW.blend -P teste_boca_olhos.py -- <dir_saida> [graus_boca] [fechar 0/1]"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); GB = float(a[1]) if len(a) > 1 else 25; FECHA = len(a) > 2 and a[2] == "1"
AQUI = os.path.dirname(os.path.abspath(__file__)); os.makedirs(OUT, exist_ok=True)
PIV = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "rig_pivos.json")))
R = json.load(open(os.path.join(AQUI, "meshy", "rosto.json")))
cab = bpy.data.objects["LOW_Cabeca"]; me = cab.data
BA, BB = PIV["mandibula"]["linha_boca"]; CANTO = PIV["mandibula"]["canto_y"]; pv = V(PIV["mandibula"]["pivo_sugerido"])
n_boca = V((0, -BB, 1)).normalized(); P0 = V((0, CANTO, BA + BB * CANTO))
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
movidos = 0
# palpebras: cada casca gira RIGIDA; o sentido e decidido uma vez pelo centro da casca
for lado, ol in PIV["olhos"].items():
    S, ax, up, Rc = V(ol["centro_globo"]), V(ol["eixo"]), V(ol["cima"]), ol["raio_casca"]
    def membros(nome):
        g = cab.vertex_groups.get(nome)
        return [v.index for v in me.vertices if g and any(e.group == g.index for e in v.groups)] if g else []
    ids = membros("Palpebra_Sup_" + lado) + membros("Palpebra_Inf_" + lado)
    for sup in (True, False):
        grp = membros(("Palpebra_Sup_" if sup else "Palpebra_Inf_") + lado)
        if not grp or not FECHA: continue
        rec = V(ol["recuo_sup"] if sup else ol["recuo_inf"])
        for i in grp: me.vertices[i].co -= rec                            # desfaz o recuo do repouso
        cen = sum((me.vertices[i].co for i in grp), V()) / len(grp)
        ang = math.radians(ol["fechar_sup_graus"] if sup else ol["fechar_inf_graus"])
        n_ol = V(R["olhos"][lado]["normal"]).normalized()                 # fechar = girar a casca para a FRENTE do olho
        sgn = max((1, -1), key=lambda g: (Matrix.Rotation(g * ang, 3, ax) @ (cen - S)).normalized().dot(n_ol))
        M = Matrix.Rotation(sgn * ang, 3, ax)
        for i in grp: me.vertices[i].co = S + M @ (me.vertices[i].co - S)
    print("TESTE palpebra", lado, len(ids))
gi = cab.vertex_groups.get("Boca_Inferior"); gs = cab.vertex_groups.get("Boca_Superior")
palp = {cab.vertex_groups[n].index for n in cab.vertex_groups.keys() if n.startswith("Palpebra")}
grupos = [{e.group for e in v.groups} for v in me.vertices]
# mandibula pelas FACES: abaixo do plano dos labios, a frente do canto, no queixo; um vertice so entra se TODAS
# as suas faces estao do lado de baixo (a copia do labio de cima, criada pelo corte, fica parada)
baixo = [False] * len(me.polygons)
for f in me.polygons:
    c = f.center; gv = set().union(*(grupos[i] for i in f.vertices))
    if gv & palp or (gs and gs.index in gv): continue
    if (gi and gi.index in gv) or ((c - P0).dot(n_boca) < 0 and c.y < CANTO + 0.35 and c.z > BA + BB * c.y - 0.30 and abs(c.x) < 0.6):
        baixo[f.index] = True
vfaces = [[] for _ in me.vertices]
for f in me.polygons:
    for i in f.vertices: vfaces[i].append(f.index)
for v in me.vertices:
    if vfaces[v.index] and all(baixo[k] for k in vfaces[v.index]):
        p = v.co; w = suave((CANTO + 0.35 - p.y) / 0.35)
        v.co = pv + Matrix.Rotation(math.radians(GB) * w, 3, V((1, 0, 0))) @ (p - pv); movidos += 1
me.update(); print("TESTE vertices da mandibula", movidos)
sc = bpy.context.scene
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
w = bpy.data.worlds.new("E"); sc.world = w
if w.node_tree is None: w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.43, 0.45, 1)
for nome, en, rot in (("K", 3.2, (50, 0, 35)), ("C", 2.2, (120, 0, 205)), ("F", 1.0, (65, 0, -120))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo)
    lo.rotation_euler = [math.radians(x) for x in rot]
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.render.resolution_x, sc.render.resolution_y = 1200, 900
sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
n0 = V(R["nariz"])
for nome, pos, alvo, lente in (("boca_34", n0 + V((2.6, -2.6, 0.4)), n0 + V((0, 0.7, -0.15)), 60),
                               ("boca_frente", n0 + V((0.0, -4.0, 0.2)), n0 + V((0, 0.6, -0.1)), 60),
                               ("olhos", n0 + V((0.6, -2.6, 1.0)), n0 + V((0, 0.95, 0.75)), 70)):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
    sc.render.filepath = os.path.join(OUT, "teste_%s_%s.png" % (nome, ("boca%d_olhos_fechados" % GB) if FECHA else ("boca%d_olhos_abertos" % GB))); bpy.ops.render.render(write_still=True)
print("TESTE_OK")
