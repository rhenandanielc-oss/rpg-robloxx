"""Exporta clipes do Silverwing como JSON para o Studio montar os KeyframeSequences SEM a importacao 3D manual.
Conferido: o Pose.CFrame que o importador do Roblox grava = matrix_basis do osso no Blender (mesmos eixos e numeros).
Formato: {"nome", "fps", "loop", "quadros", "ossos": {nome_roblox: [qx,qy,qz,qw,tx,ty,tz, ...por quadro]}}.
Uso: blender -b Silverwing_M2M.blend -P exportar_clipes_json.py -- saida_dir Clipe1,Clipe2,... [fps]
PREFIXO_SAIDA (ambiente) troca o "Silverwing_" do nome gravado (ex.: Glacial_), sem mudar a acao lida."""
import bpy, sys, os, json
a = sys.argv[sys.argv.index("--") + 1:]; out = a[0]; nomes = a[1].split(","); FPS_OUT = int(a[2]) if len(a) > 2 else 30
os.makedirs(out, exist_ok=True)
MAPA = {"head": "Cabeca", "hips": "Quadril", "spine_1": "Coluna2", "mouth_lower": "Mandibula", "spine_4": "Pescoco4",
        "spine_2": "Pescoco2", "tail_3": "Cauda3", "wing_2_l": "AsaE_2", "wing_2_r": "AsaD_2"}
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
fps_cena = sc.render.fps
PREFIXO = os.environ.get("PREFIXO_SAIDA", "Silverwing_")
# (10/11, Sombrio) medido no Teste-animacoes: nos dragoes M2M importados, cada osso do jogo = osso do Blender girado 180
# no proprio Y -> o basis bruto toca ESPELHADO (pitch/rolagem invertidos; cauda que devia cair sobe). CONVENCAO_ROBLOX=giro180y
# grava q (x,y,z,w) -> (-x,y,-z,w) e t -> (-x,y,-z) (erro 0,0 stud contra o Blender no teste do Pairar). Sem a variavel:
# como antes (os clipes ja montados das outras formas nao mudam).
GIRO = os.environ.get("CONVENCAO_ROBLOX") == "giro180y"
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
            sx = -1 if GIRO else 1
            ossos[MAPA.get(b.name, b.name)].extend([round(sx * q.x, 5), round(q.y, 5), round(sx * q.z, 5), round(q.w, 5),
                                                     round(sx * t.x, 5), round(t.y, 5), round(sx * t.z, 5)])
    dado = {"nome": PREFIXO + nome, "fps": FPS_OUT, "loop": bool(act.get("loop", True)), "quadros": n, "duracao": dur, "ossos": ossos}
    caminho = os.path.join(out, PREFIXO + nome + ".json")
    with open(caminho, "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    print("JSON", nome, n, "quadros", round(os.path.getsize(caminho) / 1024), "KB")
A.animation_data.action = None
print("JSON_OK")
