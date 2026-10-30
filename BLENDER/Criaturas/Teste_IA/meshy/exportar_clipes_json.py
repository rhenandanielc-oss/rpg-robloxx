"""Exporta clipes do Silverwing como JSON para o Studio montar os KeyframeSequences SEM a importacao 3D manual.
Conferido: o Pose.CFrame que o importador do Roblox grava = matrix_basis do osso no Blender (mesmos eixos e numeros).
Formato: {"nome", "fps", "loop", "quadros", "ossos": {nome_roblox: [qx,qy,qz,qw,tx,ty,tz, ...por quadro]}}.
Uso: blender -b Silverwing_M2M.blend -P exportar_clipes_json.py -- saida_dir Clipe1,Clipe2,... [fps]"""
import bpy, sys, os, json
a = sys.argv[sys.argv.index("--") + 1:]; out = a[0]; nomes = a[1].split(","); FPS_OUT = int(a[2]) if len(a) > 2 else 30
os.makedirs(out, exist_ok=True)
MAPA = {"head": "Cabeca", "hips": "Quadril", "spine_1": "Coluna2", "mouth_lower": "Mandibula", "spine_4": "Pescoco4",
        "spine_2": "Pescoco2", "tail_3": "Cauda3", "wing_2_l": "AsaE_2", "wing_2_r": "AsaD_2"}
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
fps_cena = sc.render.fps
for nome in nomes:
    act = bpy.data.actions["Silverwing_" + nome]
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = act.frame_range
    dur = (f1 - f0) / fps_cena
    n = int(round(dur * FPS_OUT)) + 1
    ossos = {MAPA.get(b.name, b.name): [] for b in A.pose.bones if b.name not in ("root", "DRV_root")}
    for i in range(n):
        f = f0 + i * fps_cena / FPS_OUT
        sc.frame_set(int(f), subframe=f - int(f))
        for b in A.pose.bones:
            if b.name in ("root", "DRV_root"): continue
            m = b.matrix_basis; q = m.to_quaternion(); t = m.translation
            ossos[MAPA.get(b.name, b.name)].extend([round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5),
                                                     round(t.x, 5), round(t.y, 5), round(t.z, 5)])
    dado = {"nome": "Silverwing_" + nome, "fps": FPS_OUT, "loop": bool(act.get("loop", True)), "quadros": n, "duracao": dur, "ossos": ossos}
    caminho = os.path.join(out, "Silverwing_" + nome + ".json")
    with open(caminho, "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    print("JSON", nome, n, "quadros", round(os.path.getsize(caminho) / 1024), "KB")
A.animation_data.action = None
print("JSON_OK")
