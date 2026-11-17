"""v43: exporta os 4 golpes PARCIAIS do ataque basico (anim_v43) para a ponte JSON, so com os ossos que tem chave
(lista em anim_v43/ataque_v43.json). Mesmo formato/canais da v42 (matrix_basis bruto). Campo extra "parcial": true.
Uso: blender -b anim_v43/CR_LoboArtico_Anim.blend -P studio/exportar_ataque_json_v43.py -- studio/json_v43"""
import bpy, sys, os, json
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; FPS = sc.render.fps
REL = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "ataque_v43.json")))
for nome, info in REL["acoes"].items():
    act = bpy.data.actions[nome]; ARM.animation_data.action = act
    if len(act.slots): ARM.animation_data.action_slot = act.slots[0]
    f0, f1 = [int(round(x)) for x in act.frame_range]; n = f1 - f0 + 1
    ossos = {o: [] for o in info["ossos"]}
    for f in range(f0, f1 + 1):
        for pb in ARM.pose.bones: pb.matrix_basis.identity()
        sc.frame_set(f)
        for o in info["ossos"]:
            m = ARM.pose.bones[o].matrix_basis; q = m.to_quaternion(); t = m.translation
            ossos[o].extend([round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5), round(t.x, 5), round(t.y, 5), round(t.z, 5)])
    dado = {"nome": "LoboArtico_" + nome, "fps": FPS, "loop": False, "quadros": n, "duracao": (n - 1) / FPS, "parcial": True,
            "marcadores_s": info.get("marcadores_s", {}), "ossos": ossos}
    with open(os.path.join(OUT, "LoboArtico_" + nome + ".json"), "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    print("JSON", nome, n, "quadros", len(ossos), "ossos", flush=True)
print("JSON_V43_OK", flush=True)
