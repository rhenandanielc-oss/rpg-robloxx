"""v51 = exportar_clipes_json_v49 com a PARTIDA EM CURVA CORRIGIDA (anim_v51) + os clipes compartilhados da sequencia auditada
(AndarCurva E/D, CurvaParaAndar E/D, ParadaAndar; iguais aos ja instalados) para a reimportacao local. Grava rest_v51.json."""
"""v49 = exportar_clipes_json_v48 com as CURVAS DE TROTE E CORRIDA (anim_v49, 32 clipes; lacos TroteCurva*/CorridaCurva*)."""
"""v48 = exportar_clipes_json_v47 com PARTIDA/PARADA do Andar (anim_v48); grava rest_v48.json."""
"""v47 = exportar_clipes_json_v46b so com as VIRADAS DE COMBATE (anim_v47b); grava rest_v47.json."""
"""v46b = exportar_clipes_json_v45 com as CURVAS ANDANDO (anim_v46b: 4 lacos + 8 transicoes); grava rest_v46b.json."""
"""v45 = exportar_clipes_json_v44 com os clipes de AMEACA (anim_v45); grava rest_v45.json."""
"""v44 = exportar_clipes_json_v42 so com as viradas curtas (VirarCurtoEsquerda/Direita), lendo anim_v44b; grava rest_v45.json."""
"""v42 = exportar_clipes_json_v41 so com as 5 acoes do kit (Cometa/Avalanche), lendo anim_v42."""
"""Lobo Artico anim_v41 -> JSON por clipe para a ponte JSON -> KeyframeSequence do Studio (place Teste-animacoes).
So LE o .blend (nao salva). Formato igual ao da ponte dos dragoes (meshy/exportar_clipes_json.py):
  {"nome","fps","loop","quadros","duracao","ossos": {Osso: [qx,qy,qz,qw,tx,ty,tz, ...por quadro]}}
Canais = matrix_basis BRUTO do Blender (sem conversao). A conversao de convencao (giro 180 no Y por osso, ver memoria
clipes-json-espelhados) e decidida NO STUDIO comparando os ossos importados com o repouso gravado em rest_v45.json.
Tambem grava rest_v45.json: repouso de cada osso relativo ao pai (Blender, espaco do osso) + pontos de conferencia
(posicao no mundo Blender Z-up de Cabeca/Mandibula/patas em quadros amostrados) para medir o desvio no Studio.
Uso: blender -b anim_v41/CR_LoboArtico_Anim.blend -P studio/exportar_clipes_json_v41.py -- <dir_saida>"""
import bpy, sys, os, json
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; FPS = sc.render.fps
ACOES = ("PartidaCurvaEsquerda", "PartidaCurvaDireita", "AndarCurvaEsquerda", "AndarCurvaDireita", "CurvaParaAndarEsquerda", "CurvaParaAndarDireita", "ParadaAndar")
LACOS = {"AndarCurvaEsquerda", "AndarCurvaDireita"}
PONTOS = ("Cabeca", "Mandibula", "Dedos_E", "Dedos_D", "DedosPe_E", "DedosPe_D", "Quadril", "Cauda4")
rest = {"fps_cena": FPS, "ossos": {}, "pontos": {}, "escala_max_desvio": 0.0}
for b in ARM.data.bones:
    m = (b.parent.matrix_local.inverted() @ b.matrix_local) if b.parent else b.matrix_local
    q = m.to_quaternion(); t = m.translation
    rest["ossos"][b.name] = {"pai": b.parent.name if b.parent else None, "q": [q.x, q.y, q.z, q.w], "t": [t.x, t.y, t.z],
                             "cabeca_mundo": list(ARM.matrix_world @ b.head_local), "cauda_mundo": list(ARM.matrix_world @ b.tail_local)}
for nome in ACOES:
    act = bpy.data.actions[nome]; ARM.animation_data.action = act
    if ARM.animation_data.action_slot is None and len(act.slots): ARM.animation_data.action_slot = act.slots[0]
    f0, f1 = [int(round(x)) for x in act.frame_range]; n = f1 - f0 + 1
    ossos = {b.name: [] for b in ARM.pose.bones}; pts = {p: [] for p in PONTOS}; amostra = sorted(set([f0, (f0 + f1) // 2, f1]))
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        for b in ARM.pose.bones:
            m = b.matrix_basis; q = m.to_quaternion(); t = m.translation; s = m.to_scale()
            rest["escala_max_desvio"] = max(rest["escala_max_desvio"], max(abs(x - 1) for x in s))
            ossos[b.name].extend([round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5), round(t.x, 5), round(t.y, 5), round(t.z, 5)])
        if f in amostra:
            for p in PONTOS:
                pb = ARM.pose.bones[p]; pts[p].append([f - f0] + [round(x, 4) for x in (ARM.matrix_world @ pb.tail)])
    rest["pontos"][nome] = pts
    dado = {"nome": "LoboArtico_" + nome, "fps": FPS, "loop": nome in LACOS, "quadros": n, "duracao": (n - 1) / FPS, "ossos": ossos}
    with open(os.path.join(OUT, "LoboArtico_" + nome + ".json"), "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    print("JSON", nome, n, "quadros", "laco" if nome in LACOS else "uma vez", flush=True)
ARM.animation_data.action = None
json.dump(rest, open(os.path.join(OUT, "rest_v51.json"), "w"), indent=1)
print("JSON_OK escala_max_desvio", rest["escala_max_desvio"], flush=True)
