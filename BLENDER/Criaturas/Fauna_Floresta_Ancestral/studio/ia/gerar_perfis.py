"""Gera studio/ia/Perfis.luau (v_perfil dos clipes aprovados de Javali e Coruja) a partir de studio/inventario.json.
Uso: python studio/ia/gerar_perfis.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
inv = json.load(open(os.path.join(os.path.dirname(AQUI), "inventario.json"), encoding="utf-8"))
L = ["-- Perfis (gerado por studio/ia/gerar_perfis.py a partir dos JSON aprovados; nao editar a mao).",
     "-- v_perfil = velocidade de avanco por quadro (m/s do Blender, 30 fps). Multiplicar pela escala do modelo.", "return {"]
for a, cl in inv.items():
    ent = []
    for n, v in cl.items():
        d = json.load(open(os.path.join(RAIZ, v["fonte"]), encoding="utf-8"))
        if "v_perfil" in d: ent.append("\t\t%s = {%s}," % (n, ",".join("%.3f" % x for x in d["v_perfil"])))
    if ent: L += ["\t%s = {" % a] + ent + ["\t},"]
L.append("}")
open(os.path.join(AQUI, "Perfis.luau"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
