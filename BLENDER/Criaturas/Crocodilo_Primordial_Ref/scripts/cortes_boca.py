"""Somente leitura: cortes transversais (planos y = constante) da cabeca; arestas cortadas desenhadas em (x, z) e coloridas
pelo peso da Mandibula (vermelho = mandibula, azul = cranio). Uso: blender -b CR_Crocodilo_Rig.blend -P cortes_boca.py -- <saida.png> y1,y2,..."""
import bpy, sys, json, subprocess, os
A = sys.argv[sys.argv.index("--") + 1:]; SAIDA = A[0]; YS = [float(v) for v in A[1].split(",")]
lo = bpy.data.objects["CR_Croc_LOW"]; me = lo.data; gi = lo.vertex_groups["Mandibula"].index
w = [0.0] * len(me.vertices)
for v in me.vertices:
    for g in v.groups:
        if g.group == gi: w[v.index] = g.weight
dados = {}
for yc in YS:
    segs = []
    for p in me.polygons:
        vs = [me.vertices[i].co for i in p.vertices]; ids = list(p.vertices); pts = []
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            if (a.y - yc) * (b.y - yc) < 0:
                t = (yc - a.y) / (b.y - a.y); wa, wb = w[ids[k]], w[ids[(k + 1) % len(vs)]]
                pts.append((a.x + (b.x - a.x) * t, a.z + (b.z - a.z) * t, wa + (wb - wa) * t))
        if len(pts) == 2: segs.append(pts)
    dados[yc] = segs
json.dump(dados, open(SAIDA + ".json", "w"))
print("CORTES", {k: len(v) for k, v in dados.items()})
