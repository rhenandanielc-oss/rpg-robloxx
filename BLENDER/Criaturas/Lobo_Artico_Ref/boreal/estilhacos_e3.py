"""E3 (17/11/2026) - POUSO da referencia PREPARO/VOO/POUSO: a casca se parte e lascas de gelo explodem do chao.
Gera (sobre CR_LoboArtico_Boreal_E2.blend):
  * Estilhacos_Chao_E3: coroa de cristais cravados no chao em volta das patas, inclinados para fora, maiores perto do lobo.
  * Lascas_Ar_E3: fragmentos soltos voando para fora/cima (estado de ~0,15 s apos o impacto) + po de gelo.
  * Placa_Gelo_E3: crosta de gelo rachada no chao (disco facetado fino) sob o impacto.
A casca do voo (Casca_Gelo_E2) e escondida no pouso: ela "vira" as lascas. No Roblox: lascas = Parts ancoradas que crescem
e somem + ParticleEmitter (mesmo efeito para todos os poderes).
Uso: blender -b boreal/CR_LoboArtico_Boreal_E2.blend -P boreal/estilhacos_e3.py
Saidas: boreal/CR_LoboArtico_Boreal_E3.blend, boreal/export/estilhacos_e3.json"""
import bpy, bmesh, os, math, json, random
from mathutils import Vector as V
AQUI = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.join(AQUI, "export")
sc = bpy.context.scene
MAT_E = bpy.data.materials["M_Gelo_Espinho_r8"]; MAT_R = bpy.data.materials["M_Gelo_Rastro_E2"]

def cristal(bm, base, eixo, altura, raio, lados, giro):
    eixo = eixo.normalized(); a_ = eixo.orthogonal().normalized(); b_ = eixo.cross(a_)
    anel = [bm.verts.new(base + (a_ * math.cos(giro + 2 * math.pi * k / lados) + b_ * math.sin(giro + 2 * math.pi * k / lados)) * raio * (0.8 + 0.4 * ((k * 5) % 3) / 2)) for k in range(lados)]
    meio = [bm.verts.new(base + eixo * altura * 0.55 + (v.co - base) * 0.6) for v in anel]
    p1 = bm.verts.new(base + eixo * altura)
    for k in range(lados):
        k2 = (k + 1) % lados; bm.faces.new((anel[k], anel[k2], meio[k2], meio[k])); bm.faces.new((meio[k], meio[k2], p1))
    bm.faces.new(list(reversed(anel)))
def lasca(bm, c, eixo, comp, larg, giro):              # fragmento achatado de duas pontas
    eixo = eixo.normalized(); a_ = eixo.orthogonal().normalized(); a_ = (a_ * math.cos(giro) + eixo.cross(a_) * math.sin(giro)); b_ = eixo.cross(a_)
    p = [c + eixo * comp, c - eixo * comp * 0.6, c + a_ * larg, c - a_ * larg * 0.8, c + b_ * larg * 0.35, c - b_ * larg * 0.35]
    v = [bm.verts.new(x) for x in p]
    for f in ((0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2), (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5)): bm.faces.new([v[i] for i in f])
def objeto(nome, bm, mat):
    me = bpy.data.meshes.new(nome); bm.normal_update(); bm.to_mesh(me); bm.free()
    for f in me.polygons: f.use_smooth = False
    ob = bpy.data.objects.new(nome, me); sc.collection.objects.link(ob); me.materials.append(mat); return ob

C = V((0, -0.4, 0.0))                                    # centro do impacto (entre as patas, levemente a frente)
rnd = random.Random(31)
# coroa cravada no chao: 2 aneis (elipse alongada no comprimento do lobo)
bm = bmesh.new(); n_ch = 0
for anel, (rx, ry, n, hmax) in enumerate(((2.0, 4.2, 20, 2.7), (3.2, 5.6, 26, 1.6))):
    for k in range(n):
        ang = 2 * math.pi * (k + rnd.uniform(-0.3, 0.3)) / n
        d = V((math.cos(ang) * rx, math.sin(ang) * ry, 0)) * rnd.uniform(0.92, 1.12)
        p = C + d; fora = V((d.x, d.y, 0)).normalized()
        h = hmax * rnd.uniform(0.55, 1.0); inc = rnd.uniform(0.45, 0.85) + 0.25 * anel
        cristal(bm, p - V((0, 0, 0.15)), V((0, 0, 1)) + fora * inc, h, 0.10 + 0.07 * h, rnd.choice((5, 6)), rnd.random() * 6.28); n_ch += 1
        if rnd.random() < 0.6:                         # filhote ao lado
            q = p + fora.cross(V((0, 0, 1))) * rnd.uniform(-0.35, 0.35)
            cristal(bm, q - V((0, 0, 0.1)), V((0, 0, 1)) + fora * (inc + 0.4), h * 0.45, 0.06 + 0.05 * h, 5, rnd.random() * 6.28); n_ch += 1
chao = objeto("Estilhacos_Chao_E3", bm, MAT_E)
# lascas no ar: saem do centro para fora e para cima
bm = bmesh.new(); n_ar = 0
for i in range(55):
    ang = rnd.random() * 2 * math.pi; r = rnd.uniform(1.5, 6.5); up = rnd.uniform(0.3, 3.8) * (1.2 - r / 8)
    p = C + V((math.cos(ang) * r * 0.75, math.sin(ang) * r * 1.15, up))
    dirv = (p - C).normalized() + V((0, 0, 0.3))
    s = rnd.uniform(0.12, 0.34) * (1.25 - r / 9)
    lasca(bm, p, dirv, s, s * 0.55, rnd.random() * 6.28); n_ar += 1
for i in range(170):                                     # po de gelo
    ang = rnd.random() * 2 * math.pi; r = rnd.uniform(0.8, 7.5); up = abs(rnd.gauss(0, 1.2)) * (1.3 - r / 9)
    p = C + V((math.cos(ang) * r * 0.8, math.sin(ang) * r * 1.1, up + 0.05)); s = rnd.uniform(0.03, 0.07)
    lasca(bm, p, V((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0.5)), s * 1.5, s, rnd.random() * 6.28); n_ar += 1
ar = objeto("Lascas_Ar_E3", bm, MAT_R)
# crosta de gelo rachada: disco de placas (Voronoi simples por setores) levemente desniveladas
bm = bmesh.new(); n_pl = 0
for anel, (r0, r1, n) in enumerate(((0.0, 1.5, 6), (1.5, 3.0, 11), (3.0, 4.7, 15))):   # E3 r2: placas irregulares (angulos/raios sorteados)
    cortes = sorted(rnd.uniform(0, 2 * math.pi) for _ in range(n)); gap = 0.05
    for k in range(n):
        a0 = cortes[k]; a1 = cortes[(k + 1) % n] + (2 * math.pi if k == n - 1 else 0)
        if a1 - a0 < 0.12: continue
        ri = r0 + rnd.uniform(-0.15, 0.25) if r0 else 0; ro = r1 + rnd.uniform(-0.35, 0.3); am = (a0 + a1) / 2 + rnd.uniform(-0.15, 0.15) * (a1 - a0)
        prof = 0.012 + rnd.uniform(0, 0.05); tilt = V((rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04), 0))
        poly = [(ri + gap, a0 + gap / max(ri, 0.8)), (ri * 0.5 + ro * 0.5 + rnd.uniform(-0.2, 0.2), a0 + gap / ro), (ro - gap, a0 + gap / ro),
                (ro + rnd.uniform(-0.25, 0.15), am), (ro - gap, a1 - gap / ro), (ri * 0.5 + ro * 0.5 + rnd.uniform(-0.2, 0.2), a1 - gap / ro), (ri + gap, a1 - gap / max(ri, 0.8))]
        if r0 == 0: poly = [(0.05, am)] + poly[1:6]
        pts = [C + V((math.cos(a) * r * 0.85, math.sin(a) * r * 1.25, prof)) + tilt * r for r, a in poly]
        try: bm.faces.new([bm.verts.new(q) for q in pts]); n_pl += 1
        except ValueError: pass
MAT_P = MAT_E.copy(); MAT_P.name = "M_Gelo_Crosta_E3"
pp = MAT_P.node_tree.nodes["Principled BSDF"]; pp.inputs["Alpha"].default_value = 0.55; pp.inputs["Roughness"].default_value = 0.2
placa = objeto("Placa_Gelo_E3", bm, MAT_P)
casca = bpy.data.objects.get("Casca_Gelo_E2")
if casca: casca.hide_render = True
rastro = bpy.data.objects.get("Rastro_Gelo_E2")
if rastro: rastro.hide_render = True
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
rel = {"versao": "E3", "centro": list(C), "cristais_chao": n_ch, "lascas_ar_e_po": n_ar, "placas": n_pl,
       "tris": {o.name: tris(o) for o in (chao, ar, placa)}}
json.dump(rel, open(os.path.join(EXP, "estilhacos_e3.json"), "w"), indent=1); print("E3", json.dumps(rel))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "CR_LoboArtico_Boreal_E3.blend")); print("E3_OK")
