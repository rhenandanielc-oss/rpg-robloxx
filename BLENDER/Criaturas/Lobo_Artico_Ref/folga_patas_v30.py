"""v30: folga das patas no BALANCO (malha): menor z dos vertices da pata (regiao da pata no repouso, raio 0,8) nos quadros sem apoio,
por acao, pata e LOD; chao = z da sola no repouso. Negativo = atravessa o chao no ar. Tambem as patas TRASEIRAS (controle).
Uso: blender -b <blend> -P folga_patas_v30.py -- <saida_json> [LOW,LOD1,LOD2]"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marchas_v29 as MV
a = sys.argv[sys.argv.index("--") + 1:]; OUTJ = a[0]; LODS = a[1].split(",") if len(a) > 1 else ["LOW"]
SRC = os.path.dirname(bpy.data.filepath); sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); G = MV.marchas(CJ)
TJ = {}
for fn in ("marchas_v29.json", "transicoes_v25.json", "viradas_v27.json"):
    for k, v in json.load(open(os.path.join(SRC, fn)))["acoes"].items(): TJ[k] = v
def apoio(ac, k, q): return bool(TJ[ac]["apoio_por_quadro"][k][q]) if ac in TJ else bool(MV.apoio(G, {"acoes": {}}, ac, k, q))
ACS = ["Andar", "Trote", "Corrida"] + [k for k in TJ if k in bpy.data.actions]
R = {}
for L in LODS:
    C = bpy.data.objects[L + "_Corpo"]; me = C.data
    ARM.animation_data.action = None
    for pb in ARM.pose.bones: pb.matrix_basis.identity()
    bpy.context.view_layer.update()
    ids = {k: [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
    chao = {k: min(me.vertices[i].co.z for i in v) for k, v in ids.items()}; R[L] = {}
    for ac in ACS:
        acn = bpy.data.actions[ac]; ARM.animation_data.action = acn
        if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
        f0, f1 = (int(x) for x in acn.frame_range); res = {k: [9.0, None] for k in ids}
        for q in range(f1 - f0 + 1):
            sw = [k for k in ids if not apoio(ac, k, q)]
            if not sw: continue
            sc.frame_set(f0 + q); dg = bpy.context.evaluated_depsgraph_get(); e = C.evaluated_get(dg); m = e.to_mesh()
            for k in sw:
                z = min(m.vertices[i].co.z for i in ids[k]) - chao[k]
                if z < res[k][0]: res[k] = [round(z, 4), q]
            e.to_mesh_clear()
        R[L][ac] = res; print("FOLGA", L, ac, json.dumps(res), flush=True)
json.dump(R, open(OUTJ, "w"), indent=1); print("FOLGA_PATAS_V30_OK", flush=True)
