"""Perna dianteira como COLUNA lisa (referencia): no rig10 a perna afina ate o punho e alarga de novo logo abaixo
(parte branca mais larga e deslocada) -> de frente parece um "cotovelo" a ~40% da altura. Aqui, por altura (z Z_BAIXO..Z_ALTO),
o centro (x, y) da perna vira uma RETA ajustada e as meias-larguras (x e y) viram uma curva LINEAR (afinamento suave),
escalando cada vertice em torno do centro. Pata (abaixo de Z_BAIXO) e cotovelo/ombro (acima de Z_ALTO) com transicao
macia. Depois o punho (osso) vai para o novo centro e o IK e refeito. Simetrico. Pesos/UV/textura intactos.
Uso: blender -b rig10/Lobo_Ancestral_Rig.blend -P coluna_perna.py -- <saida_dir>"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
Z_PATA = 0.45
Z_BAIXO, Z_ALTO, BORDA = 0.65, 2.95, 0.30          # so de FRENTE (x): de lado a v2 engrossava a perna (a ponta de baixo pegava a pata)
n = len(me.vertices); co = np.array([v.co[:] for v in me.vertices]); co0 = co.copy()
gi = {g.index: g.name for g in LO.vertex_groups}
cad = {"AntebracoE", "MaoE", "AntebracoD", "MaoD"}
w = np.array([sum(g.weight for g in v.groups if gi[g.group] in cad) for v in me.vertices])
rel = {"Z_BAIXO": Z_BAIXO, "Z_ALTO": Z_ALTO}
# v2: cada CONTORNO (fora/dentro em x, frente/tras em y) vira uma reta entre o valor medido logo acima da pata e logo
# abaixo do cotovelo (medias em janelas nas pontas, sem ajuste por minimos quadrados): v1 (percentis + reta ajustada)
# afinou demais o alto da perna e abriu um vinco claro por dentro.
zs = np.arange(Z_BAIXO - BORDA, Z_ALTO + BORDA + 0.01, 0.08)
viz = [[] for _ in range(n)]
for e in me.edges: a_, b_ = e.vertices; viz[a_].append(b_); viz[b_].append(a_)
VZ = [np.array(v, int) for v in viz]
wm = w.copy()
for _ in range(3): wm = 0.5 * wm + 0.5 * np.array([wm[VZ[i]].mean() if len(VZ[i]) else wm[i] for i in range(n)])
def suav3(v): return np.convolve(np.pad(v, 2, mode="edge"), np.ones(5) / 5, mode="valid")
for lado, sx_ in (("E", 1), ("D", -1)):
    sel = (w > 0.6) & (co0[:, 0] * sx_ > 0.3) & (co0[:, 1] < -2.6)
    regiao = (wm > 0.25) & (co0[:, 0] * sx_ > 0.25) & (co0[:, 1] < -2.6)
    perfil = {k: [] for k in ("xmin", "xmax", "ymin", "ymax")}
    for z0 in zs:
        s_ = sel & (np.abs(co0[:, 2] - z0) < 0.14)
        if s_.sum() < 4:
            for k in perfil: perfil[k].append(np.nan)
            continue
        perfil["xmin"].append(np.percentile(co0[s_, 0], 3)); perfil["xmax"].append(np.percentile(co0[s_, 0], 97))
        perfil["ymin"].append(np.percentile(co0[s_, 1], 3)); perfil["ymax"].append(np.percentile(co0[s_, 1], 97))
    P = {}
    for k, v in perfil.items():
        v = np.array(v); ok = ~np.isnan(v); v = np.interp(zs, zs[ok], v[ok]); P[k] = suav3(v)
    def ponta(k, z_):
        m_ = np.abs(zs - z_) < 0.12; return float(P[k][m_].mean())
    alvo_ = {k: (ponta(k, Z_BAIXO), ponta(k, Z_ALTO)) for k in P}
    def reta(k, z): t = np.clip((z - Z_BAIXO) / (Z_ALTO - Z_BAIXO), 0, 1); return alvo_[k][0] + (alvo_[k][1] - alvo_[k][0]) * t
    zv = co0[:, 2]
    peso = regiao * np.clip(wm * 1.4, 0, 1) * suave((zv - (Z_BAIXO - BORDA)) / BORDA) * suave(((Z_ALTO + BORDA) - zv) / BORDA)
    for eixo, kmin, kmax in ((0, "xmin", "xmax"),):
        lo0 = np.interp(zv, zs, P[kmin]); hi0 = np.interp(zv, zs, P[kmax]); lo1 = reta(kmin, zv); hi1 = reta(kmax, zv)
        t = (co0[:, eixo] - lo0) / np.maximum(hi0 - lo0, 1e-3)                 # posicao relativa dentro do contorno
        novo = lo1 + t * (hi1 - lo1)
        co[:, eixo] += (novo - co0[:, eixo]) * peso                              # soma (o outro lado nao desfaz)
    # DE LADO: so o CENTRO vira vertical (sem mudar a largura); a pata (abaixo de Z_PATA) acompanha o deslocamento do
    # ponto Z_PATA. Medido no rig10: o centro recuava 0,16 de z 2,2 a 0,8 (perna inclinada para tras embaixo).
    yc = (P["ymin"] + P["ymax"]) / 2
    Y_T = float(yc[(zs >= 1.6) & (zs <= 2.8)].mean())
    dyc = Y_T - yc
    def dy_em(z):
        z = np.maximum(z, Z_PATA); return np.interp(z, zs, dyc) * suave(((Z_ALTO + BORDA) - z) / BORDA)
    peso_y = regiao * np.clip(wm * 1.4, 0, 1)
    co[:, 1] += dy_em(zv) * peso_y
    rel[lado + "_y_centro"] = {"alvo": round(Y_T, 3), "antes": [round(float(v), 3) for v in yc[::3]], "z": [round(float(z), 2) for z in zs[::3]]}
    rel[lado + "_dy_pata"] = float(dy_em(np.array([Z_PATA]))[0])
    zz = zs[(zs >= Z_BAIXO) & (zs <= Z_ALTO)]
    rel[lado] = {"z": [round(float(z), 2) for z in zz[::3]],
                 "largura_x_antes": [round(float(np.interp(z, zs, P["xmax"]) - np.interp(z, zs, P["xmin"])), 3) for z in zz[::3]],
                 "largura_x_depois": [round(float(reta("xmax", z) - reta("xmin", z)), 3) for z in zz[::3]]}
    zp = BD["Mao" + lado].head_local.z
    rel[lado + "_punho_alvo"] = [float((reta("xmin", zp) + reta("xmax", zp)) / 2), Y_T]
    print(lado, "largura x:", " ".join("z%.1f:%.2f->%.2f" % (z, a1, b1) for z, a1, b1 in zip(rel[lado]["z"], rel[lado]["largura_x_antes"], rel[lado]["largura_x_depois"])))
me.vertices.foreach_set("co", co.ravel()); me.update()
d = np.linalg.norm(co - co0, axis=1); rel["vertices_movidos"] = int((d > 0.005).sum()); rel["desloc_max"] = round(float(d.max()), 3)
print("MOVIDOS", rel["vertices_movidos"], "max %.3f" % d.max())
# punho (osso) no novo centro da coluna
bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); EB = arm.data.edit_bones
for s in ("E", "D"):
    px_, py_ = rel[s + "_punho_alvo"]; p = EB["Mao" + s].head.copy(); p.x = px_; p.y = py_
    for nm in ("Antebraco" + s,):
        eb = EB[nm]; r_ = eb.roll; eb.tail = p; eb.roll = r_
    d_ = rel[s + "_dy_pata"]; bd = EB["Dedos" + s].head.copy(); bd.y += d_; td = EB["Dedos" + s].tail.copy(); td.y += d_
    eb = EB["Mao" + s]; r_ = eb.roll; eb.head = p; eb.tail = bd; eb.roll = r_
    eb = EB["Dedos" + s]; r_ = eb.roll; eb.head = bd; eb.tail = td; eb.roll = r_
bpy.ops.object.mode_set(mode="OBJECT")
for s in ("E", "D"):
    b1, b2 = BD["Antebraco" + s], BD["Mao" + s]
    alvo_ = bpy.data.objects["IK_Mao" + s]; alvo_.location = b2.head_local.copy(); alvo_.rotation_mode = "QUATERNION"; alvo_.rotation_quaternion = b2.matrix_local.to_quaternion()
    bpy.data.objects["Polo_Antebraco" + s].location = b1.head_local + V((0.0, 2.5, 0.0))
bpy.context.view_layer.update()
rel["polo"] = {}
for s in ("E", "D"):
    c = arm.pose.bones["Antebraco" + s].constraints["IK"]; b0 = BD["Braco" + s]
    def erro(a_):
        c.pole_angle = a_; bpy.context.view_layer.update(); return (arm.pose.bones[b0.name].tail - b0.tail_local).length
    a_ = min((erro(math.radians(g)), math.radians(g)) for g in range(-180, 180, 3))[1]
    for passo in (1.0, 0.25, 0.05): a_ = min([a_ + math.radians(passo * q) for q in range(-4, 5)], key=erro)
    c.pole_angle = a_; rel["polo"]["Mao" + s] = [round(math.degrees(a_), 2), round(erro(a_), 5)]
dg = bpy.context.evaluated_depsgraph_get(); ev = LO.evaluated_get(dg); mm = ev.to_mesh()
ce = np.array([v.co[:] for v in mm.vertices]); ev.to_mesh_clear()
rel["desvio_repouso_ik"] = float(np.abs(ce - co).max()); print("DESVIO repouso com IK %.5f" % rel["desvio_repouso_ik"], "POLO", rel["polo"])
json.dump(rel, open(os.path.join(OUT, "coluna_perna.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("COLUNA_PERNA_OK")
