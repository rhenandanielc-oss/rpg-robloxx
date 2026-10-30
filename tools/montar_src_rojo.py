"""Monta src/ (layout Rojo) a partir do export JSON dos scripts do Studio (lista de {caminho, classe, contexto, fonte,
tem_filhos}). Script -> .server.luau, LocalScript -> .client.luau, ModuleScript -> .luau; script com scripts filhos
vira pasta com init.*. Uso: python -I montar_src_rojo.py <pasta_export> <repo>"""
import json, os, sys, glob
exp, repo = sys.argv[1], sys.argv[2]
itens = []
for f in sorted(glob.glob(os.path.join(exp, "export_*.json"))):
    with open(f, encoding="utf-8") as h: itens += json.load(h)
EXT = {"Script": ".server.luau", "LocalScript": ".client.luau", "ModuleScript": ".luau"}
avisos = []
for it in itens:
    cam, cls = it["caminho"], it["classe"]
    if cls == "Script" and it.get("contexto") not in (None, "Enum.RunContext.Legacy", "Enum.RunContext.Server"):
        avisos.append("RunContext especial: " + "/".join(cam) + " " + str(it.get("contexto")))
    if it["tem_filhos"]:
        destino = os.path.join(repo, "src", *cam, "init" + EXT[cls])
    else:
        destino = os.path.join(repo, "src", *cam[:-1], cam[-1] + EXT[cls])
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as h: h.write(it["fonte"])
print("scripts:", len(itens)); print("\n".join(avisos) or "sem avisos")
