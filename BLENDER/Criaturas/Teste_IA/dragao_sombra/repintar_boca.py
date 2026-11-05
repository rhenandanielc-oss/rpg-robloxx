"""Boca do Sombrio (05/11, usuario: "arrume a boca interna do dragao sombrio, quando ele abre esta preto").
Causa: as paredes internas da v9 (SB_Dragao_Boca_Parede_L/R, BJ no DOCS/estado) foram pintadas de vermelho quase preto
(0,26; 0,05; 0,09) e, com a mandibula aberta, esticam e cobrem o rosado do interior.
Aqui so a TEXTURA muda (malha/UV/rig iguais): os pixels das paredes recebem um degrade de tecido de boca pela
profundidade de cada vertice (rosado perto dos labios -> vermelho -> escuro na garganta), com leve variacao.
Saidas: low/SB_Dragao_cor_boca.png (2048) e final/SB_Dragao_cor_boca_1024.png (para a Roblox); o original fica intocado.
Renders antes/depois em review/v10_boca/. Uso: blender -b rig/SB_Dragao_M2M_v9.blend -P repintar_boca.py"""
import bpy, os, math, random
import numpy as np
from mathutils import Vector as V
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "review", "v10_boca"); os.makedirs(OUT, exist_ok=True)
PAREDE = np.array([0.26, 0.05, 0.09])                 # cor pintada pela low_sombrio.py (valores do PNG sRGB)
# degrade (sRGB): labios -> meio -> garganta
# (1a tentativa 0,72/0,55/0,34/0,20 ainda lia escuro: as paredes ficam na sombra da cabeca -> tons mais claros)
CORES = [(0.0, (0.90, 0.52, 0.58)), (0.45, (0.78, 0.38, 0.45)), (0.8, (0.56, 0.20, 0.27)), (1.0, (0.36, 0.09, 0.14))]
def degrade(t):
    t = min(1, max(0, t))
    for (a, ca), (b, cb) in zip(CORES, CORES[1:]):
        if t <= b: k = (t - a) / (b - a); return np.array(ca) * (1 - k) + np.array(cb) * k
    return np.array(CORES[-1][1])
M = bpy.data.objects["Silverwing"]; me = M.data
img = bpy.data.images["SB_Dragao_cor"]; W, H = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)
mask = np.abs(px[..., :3] - PAREDE).sum(-1) < 0.02
print("BOCA pixels de parede", int(mask.sum()))
# camada UV que cai nas paredes
melhor = None
for uv in me.uv_layers:
    hits = []
    for p in me.polygons:
        c = sum((uv.data[li].uv for li in p.loop_indices), V((0, 0))) / p.loop_total
        x, y = int(c.x % 1 * W), int(c.y % 1 * H)
        if 0 <= x < W and 0 <= y < H and mask[y, x]: hits.append(p.index)
    if not melhor or len(hits) > len(melhor[1]): melhor = (uv, hits)
uv, faces = melhor
print("BOCA camada UV", uv.name, "faces de parede", len(faces))
assert len(faces) > 50, "paredes nao encontradas"
# profundidade: eixo Y do repouso (ponta do focinho = y menor)
vs = {li: me.vertices[me.loops[li].vertex_index].co for f in faces for li in me.polygons[f].loop_indices}
ys = [co.y for co in vs.values()]; y0, y1 = min(ys), max(ys)
print("BOCA profundidade y", round(y0, 3), round(y1, 3))
novo = px.copy(); pintado = np.zeros((H, W), bool)
rnd = random.Random(7)
for f in faces:
    p = me.polygons[f]; L = list(p.loop_indices)
    for k in range(1, len(L) - 1):
        tri = [L[0], L[k], L[k + 1]]
        P = [np.array((uv.data[li].uv.x * W, uv.data[li].uv.y * H)) for li in tri]
        C = [degrade((vs[li].y - y0) / (y1 - y0)) for li in tri]
        xa, xb = int(min(q[0] for q in P)) - 2, int(max(q[0] for q in P)) + 3
        ya, yb = int(min(q[1] for q in P)) - 2, int(max(q[1] for q in P)) + 3
        (x1, y1_), (x2, y2), (x3, y3) = P
        den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1_ - y3)
        if abs(den) < 1e-9: continue
        for yy in range(max(0, ya), min(H, yb)):
            for xx in range(max(0, xa), min(W, xb)):
                if not mask[yy, xx]: continue                          # so a parede (nunca dentes/labios vizinhos)
                cx, cy = xx + 0.5, yy + 0.5
                a = ((y2 - y3) * (cx - x3) + (x3 - x2) * (cy - y3)) / den
                b = ((y3 - y1_) * (cx - x3) + (x1 - x3) * (cy - y3)) / den
                c = 1 - a - b
                if min(a, b, c) < -0.15: continue                    # ~2 px de folga na borda
                a, b, c = max(a, 0), max(b, 0), max(c, 0); s = a + b + c
                cor = (C[0] * a + C[1] * b + C[2] * c) / s
                novo[yy, xx, :3] = np.clip(cor * (0.94 + 0.12 * rnd.random()), 0, 1); pintado[yy, xx] = True
# sobra da cor antiga (folga do empacotamento): cor pintada vizinha
resto = mask & ~pintado
for _ in range(6):
    if not resto.any(): break
    ys_, xs_ = np.nonzero(resto)
    for yy, xx in zip(ys_, xs_):
        viz = [(yy + dy, xx + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if 0 <= yy + dy < H and 0 <= xx + dx < W and pintado[yy + dy, xx + dx]]
        if viz: novo[yy, xx, :3] = np.mean([novo[a, b, :3] for a, b in viz], 0); pintado[yy, xx] = True; resto[yy, xx] = False
print("BOCA pintados", int(pintado.sum()), "sobra antiga", int((np.abs(novo[..., :3] - PAREDE).sum(-1) < 0.02).sum()))
def salvar(nome, arr, tam, caminho):
    im = bpy.data.images.new(nome, W, H, alpha=True); im.pixels.foreach_set(arr.ravel())
    if tam != W: im.scale(tam, tam)
    im.filepath_raw = caminho; im.file_format = "PNG"; im.save(); return im
os.makedirs(os.path.join(AQUI, "final"), exist_ok=True)
salvar("cor_boca_2048", novo, 2048, os.path.join(AQUI, "low", "SB_Dragao_cor_boca.png"))
salvar("cor_boca_1024", novo, 1024, os.path.join(AQUI, "final", "SB_Dragao_cor_boca_1024.png"))
# ---- renders antes/depois: boca aberta no Rugido_Territorial (pico) ----
A = bpy.data.objects["Silverwing_Rig"]; sc = bpy.context.scene
act = bpy.data.actions.get("Silverwing_Rugido_Territorial") or bpy.data.actions.get("Silverwing_Ninho_Ameaca")
if not A.animation_data: A.animation_data_create()
A.animation_data.action = act
if hasattr(A.animation_data, "action_slot") and act.slots: A.animation_data.action_slot = act.slots[0]
f0, f1 = act.frame_range; sc.frame_set(int(f0 + (f1 - f0) * 0.45))
dg = bpy.context.evaluated_depsgraph_get()
up = A.matrix_world @ A.pose.bones["mouth_upper_tip"].head; lo = A.matrix_world @ A.pose.bones["mouth_lower_tip"].head
hd = A.matrix_world @ A.pose.bones["head"].head
alvo = (up + lo) / 2 * 0.6 + hd * 0.4; frente = (up - hd).normalized(); dist = (up - hd).length * 2.6
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items} else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y = 640, 480
cam = bpy.data.objects.get("CamBoca") or bpy.data.objects.new("CamBoca", bpy.data.cameras.new("CamBoca")); sc.collection.objects.link(cam) if cam.name not in sc.collection.objects else None
sc.camera = cam; cam.data.lens = 50
if not any(o.type == "LIGHT" for o in sc.objects):
    l = bpy.data.objects.new("SolBoca", bpy.data.lights.new("SolBoca", "SUN")); l.data.energy = 3.5; sc.collection.objects.link(l); l.rotation_euler = (0.8, 0.2, 0.6)
lado = frente.cross(V((0, 0, 1))).normalized()
VISTAS = {"frente": frente * dist + V((0, 0, dist * 0.15)), "34": (frente * 0.75 + lado * 0.65).normalized() * dist + V((0, 0, dist * 0.1)),
          "lado": lado * dist * 1.1, "cima": (frente * 0.8).normalized() * dist + V((0, 0, dist * 0.55))}
mat_img = None
for n in M.data.materials[0].node_tree.nodes:
    if n.type == "TEX_IMAGE" and n.image == img: mat_img = n
novo_img = bpy.data.images["cor_boca_2048"]
for fase, im in (("antes", img), ("depois", novo_img)):
    mat_img.image = im
    for nome, off in VISTAS.items():
        cam.location = alvo + off; cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (fase, nome)); bpy.ops.render.render(write_still=True)
mat_img.image = img
print("BOCA_OK", OUT)
