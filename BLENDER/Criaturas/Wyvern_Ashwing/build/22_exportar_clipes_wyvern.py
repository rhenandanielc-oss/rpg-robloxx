"""Exporta os clipes aprovados da Wyvern (Wyvern_E7_clipes_L6.blend, 49 actions) como JSON para a ponte do Studio
(mesmo formato de Teste_IA/meshy/exportar_clipes_json.py): {"nome","fps","loop","quadros","duracao","ossos":{osso:[qx,qy,qz,qw,tx,ty,tz,...]}}.
- Nomes de osso = os do GLB (21_exportar_wyvern.py, mesmo MAPA).
- CONVENCAO_ROBLOX=giro180y grava q (x,y,z,w) -> (-x,y,-z,w), t -> (-x,y,-z) (Import 3D novo, ver memoria de 10/11);
  sem a variavel grava o basis bruto. Medir no Studio qual vale antes de montar todos.
- Saida "Wyvern_<action>.json" + indice.json com a lista.
Uso: blender -b Wyvern_E7_clipes_L6.blend -P build/22_exportar_clipes_wyvern.py -- <pasta_saida> [Clipe1,Clipe2|todos] [fps]"""
import bpy, sys, os, json
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
SEL = a[1] if len(a) > 1 else "todos"; FPS_OUT = int(a[2]) if len(a) > 2 else 30
MAPA = {"pelvis": "Quadril", "spine_02": "Coluna2", "head": "Cabeca", "jaw": "Mandibula", "neck_02": "Pescoco2",
        "neck_04": "Pescoco4", "tail_03": "Cauda3", "tail_10": "tail_tip", "breath_socket": "mouth_upper_tip",
        "shoulder_L": "shoulder_l", "shoulder_R": "shoulder_r", "toe_L": "toes_tip_l", "toe_R": "toes_tip_r"}
LOOP = {"idle_loop", "walk_loop", "fly_loop", "Corrida", "Planeio", "VooBatido", "PairarCurto", "Empoleirado", "Deitado",
        "GuardaNinho", "RideIdle", "RideWalk", "RideRun", "AndarQuatroApoios", "Subida", "Descida", "Mergulho",
        "CurvaAereaEsquerda", "CurvaAereaDireita", "Alerta"}
GIRO = os.environ.get("CONVENCAO_ROBLOX") == "giro180y"
sc = bpy.context.scene; A = bpy.data.objects["Wyvern_Rig"]; fps_cena = sc.render.fps
nomes = [x.name for x in bpy.data.actions] if SEL == "todos" else SEL.split(",")
sx = -1 if GIRO else 1
indice = []
for nome in nomes:
    act = bpy.data.actions[nome]
    A.animation_data.action = act
    if act.slots: A.animation_data.action_slot = act.slots[0]
    f0, f1 = act.frame_range; dur = (f1 - f0) / fps_cena; n = int(round(dur * FPS_OUT)) + 1
    ossos = {MAPA.get(b.name, b.name): [] for b in A.pose.bones}
    # (13/11) amostras espalhadas exatamente de f0 a f1: com i*fps/FPS_OUT o ultimo quadro caia ate 0,6 quadro DEPOIS
    # do fim quando a duracao nao fecha em 1/30 s (Corrida, RideRun, Arrancada, ReacaoGolpe, VooBatido: erro de ate
    # 0,38 stud no fim e tranco na emenda do loop, medido no Studio). O tempo do quadro i no KFS = i * duracao / (n - 1)
    for i in range(n):
        f = f0 + i * (f1 - f0) / (n - 1)
        sc.frame_set(int(f), subframe=f - int(f))
        for b in A.pose.bones:
            m = b.matrix_basis; q = m.to_quaternion(); t = m.translation
            ossos[MAPA.get(b.name, b.name)].extend([round(sx * q.x, 5), round(q.y, 5), round(sx * q.z, 5), round(q.w, 5),
                                                     round(sx * t.x, 5), round(t.y, 5), round(sx * t.z, 5)])
    nm = "Wyvern_" + nome
    dado = {"nome": nm, "fps": FPS_OUT, "tempoExato": True, "loop": nome in LOOP, "quadros": n, "duracao": dur, "ossos": ossos,
            "convencao": "giro180y" if GIRO else "bruto"}
    with open(os.path.join(OUT, nm + ".json"), "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    indice.append({"nome": nm, "quadros": n, "loop": nome in LOOP, "ossos": len(ossos)})
    print("JSON", nm, n, "quadros", len(ossos), "ossos")
A.animation_data.action = None
with open(os.path.join(OUT, "indice.json"), "w") as fh: json.dump(indice, fh, indent=1)
print("JSON_OK", len(indice))
