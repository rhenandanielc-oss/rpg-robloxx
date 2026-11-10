"""Mascara (em UV) da face de baixo da garupa/base da cauda exposta no Sentar (pedido do usuario 04/11: clarear a
textura da peca escura vista de tras). Faces da malha Urso_Corpo_Tras com osso dominante Pelve/Cauda1/Cauda2 que, no
ultimo quadro do Sentar, ficam baixas (centro z < 1,4) e viradas para baixo (normal z < -0,15), e que no REPOUSO
tambem ficam viradas para baixo (normal z < -0,2): assim o Repouso/andar nao muda (a parte de tras da garupa fica igual).
(2) 04/11, depois do teste no Studio: a peca escura vista de tras era, na verdade, a PAREDE INTERNA entre as coxas
(virilha), quase vertical (normal x ~ +-0,95), achada por raio da camera do Studio. Criterio 2: centro no Sentar com
|x| < 1,1, z < 1,2, 4,2 < y < 5,9 e ao menos um vertice da Pelve. So com --virilha: TESTADO e DESCARTADO (essas faces
aparecem tambem no Repouso, atras da coxa; clarear x1,8 mudava a garupa em pe). A versao aplicada usa so o criterio 1.
Uso: blender -b CR_Urso_v2_Anim.blend -P mascara_garupa.py -- <saida.json> [--virilha]"""
import bpy, sys, json
OUT = sys.argv[sys.argv.index("--") + 1]; VIRILHA = "--virilha" in sys.argv
sc = bpy.context.scene; arm = bpy.data.objects["Urso_Rig"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
o = bpy.data.objects["Urso_Corpo_Tras"]; gn = {g.index: g.name for g in o.vertex_groups}
arm.animation_data.action = bpy.data.actions["Urso_Repouso"]; sc.frame_set(1)
ev0 = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me0 = ev0.to_mesh()
NZ0 = [(o.matrix_world.to_3x3() @ p.normal).normalized().z for p in me0.polygons]; ev0.to_mesh_clear()
arm.animation_data.action = bpy.data.actions["Urso_Sentar"]; sc.frame_set(43)
ev = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh(); mw = o.matrix_world; m3 = mw.to_3x3()
uv = o.data.uv_layers.active.data; tris = []; nf = 0
def dom(i):
    vg = o.data.vertices[i].groups
    return gn[max(vg, key=lambda g: g.weight).group] if vg else "-"
for p in me.polygons:
    vs = list(p.vertices)
    base = sum(1 for i in vs if dom(i) in ("Pelve", "Cauda1", "Cauda2")) * 2 >= len(vs)
    c = mw @ p.center; n = (m3 @ p.normal).normalized()
    crit1 = base and c.z < 1.4 and n.z < -0.15 and NZ0[p.index] < -0.2
    crit2 = VIRILHA and abs(c.x) < 1.1 and c.z < 1.2 and 4.2 < c.y < 5.9 and any(dom(i) == "Pelve" for i in vs)
    if crit1 or crit2:
        nf += 1; L = [tuple(uv[li].uv) for li in p.loop_indices]
        for k in range(1, len(L) - 1): tris.append([L[0], L[k], L[k + 1], round(c.z, 3), round(-n.z, 3)])
ev.to_mesh_clear()
json.dump({"faces": nf, "tris": tris}, open(OUT, "w")); print("MASCARA_OK faces", nf, "tris", len(tris))
