"""v24, passo 2: pesos LOCAIS da SOLA das patas no LOD1 e no LOD2 (anim_v24_clipes so lido; saida <dir>).
Diagnostico (diag_apoios_v24.py): no LOD2 o deslize de Andar DD (0,044), Trote DD (0,037) e Corrida TE (0,037) e 100% PELE
(componente do osso ~0): vertices da sola da malha reduzida misturam o osso de cima (ex.: Metacarpo 0,45 + Dedos 0,40 +
ANTEBRACO 0,15), que nao fica parado no apoio. O LOW (referencia; nao mexido) tem a sola presa a Metacarpo/Dedos.
Correcao: em cada pata do LOD (mesma selecao da auditoria: z < 0,5 a 0,8 do pe), peso = pesos do LOW interpolados no ponto
mais proximo da pele do LOW da mesma pata (baricentrico), com mistura gradual com o peso proprio do LOD:
fator 1 ate Z_CHEIO acima da sola e 0 a partir de Z_ZERO (sem degrau na canela). <= 4 influencias, soma 1.
Faixa ESTREITA (Z_CHEIO 0,03 / Z_ZERO 0,06 = so os vertices de CONTATO, os que a auditoria mede): com faixa larga (0,18/0,40)
o calcanhar do LOD2 (aresta direta ate o jarrete) perdia o peso de Tibia e a face longa DOBRAVA no balanco (0,14 stud2 na TE,
medido). F_VIZ (mistura dos vertices com aresta ate > Z_VIZ acima da sola) fica 1,0 com a faixa estreita (testado: igual).
Geometria, UV, rig e acoes iguais. Uso: blender -b anim_v24_clipes/CR_LoboArtico_Anim.blend -P pesos_sola_v24.py -- <dir>"""
import bpy, sys, os, json, math, shutil
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
Z_CHEIO, Z_ZERO = float(os.environ.get("Z_CHEIO", 0.03)), float(os.environ.get("Z_ZERO", 0.06)); Z_VIZ = float(os.environ.get("Z_VIZ", 0.8)); F_VIZ = float(os.environ.get("F_VIZ", 1.0)); NIVEIS = os.environ.get("NIVEIS", "LOD1,LOD2").split(",")
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; SL = ARM.animation_data.action_slot; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update(); OSS = {b.name for b in ARM.data.bones}
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); PXY = dict(zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"]))
def pata(co):
    for k, xy in PXY.items():
        if co.z < 0.5 and math.hypot(co.x - xy[0], co.y - xy[1]) < 0.8: return k
LO = bpy.data.objects["LOW_Corpo"]; gl = {g.index: g.name for g in LO.vertex_groups}
LP = [v.co.copy() for v in LO.data.vertices]; LW = [{gl[g.group]: g.weight for g in v.groups if gl[g.group] in OSS} for v in LO.data.vertices]
BV = {}
for k in PXY:
    fs = [list(p.vertices) for p in LO.data.polygons if all(pata(LP[i]) == k for i in p.vertices)]; BV[k] = (BVHTree.FromPolygons(LP, fs), fs)
REL = {"parametros": {"Z_CHEIO": Z_CHEIO, "Z_ZERO": Z_ZERO, "Z_VIZ": Z_VIZ}}
for L in NIVEIS:
    o = bpy.data.objects[L + "_Corpo"]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}; R = {}
    VZ = {}
    for e in me.edges:
        a_, b_ = e.vertices; VZ.setdefault(a_, []).append(b_); VZ.setdefault(b_, []).append(a_)
    for k in PXY:
        ids = [v.index for v in me.vertices if pata(v.co) == k]; zs = min(me.vertices[i].co.z for i in ids); bvh, fs = BV[k]; n = 0; pulados = 0; dmax = 0.0; troca = 0.0
        for i in ids:
            v = me.vertices[i]; h = v.co.z - zs; fat = 1.0 if h <= Z_CHEIO else max(0.0, 1 - (h - Z_CHEIO) / (Z_ZERO - Z_CHEIO))
            if fat <= 0: continue
            if max(me.vertices[j].co.z for j in VZ.get(i, [i])) - zs > Z_VIZ:          # aresta longa ate o jarrete/carpo (LOD2): mistura parcial
                fat *= F_VIZ; pulados += 1
                if fat <= 0: continue

            loc, nr, fi, d = bvh.find_nearest(v.co); dmax = max(dmax, d); bc = poly_3d_calc([LP[j] for j in fs[fi]], loc); wl = {}
            for j, b in zip(fs[fi], bc):
                for kk, x in LW[j].items(): wl[kk] = wl.get(kk, 0) + x * b
            wp = {gn[g.group]: g.weight for g in v.groups if gn[g.group] in OSS}
            w = {kk: fat * wl.get(kk, 0) + (1 - fat) * wp.get(kk, 0) for kk in set(wl) | set(wp)}
            w = dict(sorted(((kk, x) for kk, x in w.items() if x > 1e-4), key=lambda t: -t[1])[:4]); s = sum(w.values())
            troca = max(troca, sum(abs(w.get(kk, 0) / s - wp.get(kk, 0)) for kk in set(w) | set(wp)) / 2)
            for g in list(v.groups): o.vertex_groups[g.group].remove([i])
            for kk, x in w.items(): (o.vertex_groups.get(kk) or o.vertex_groups.new(name=kk)).add([i], x / s, "REPLACE")
            n += 1
        R[k] = {"vertices_pata": len(ids), "vertices_repesados": n, "mantidos_por_aresta_longa": pulados, "dist_max_a_pele_LOW": round(dmax, 4), "mudanca_max_de_peso": round(troca, 3)}
    REL[L] = R; print("V24 sola", L, json.dumps(R), flush=True)
json.dump(REL, open(os.path.join(OUT, "pesos_sola_v24.json"), "w"), indent=1)
ARM.animation_data.action = AC
if SL: ARM.animation_data.action_slot = SL
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("PESOS_SOLA_V24_OK", flush=True)
