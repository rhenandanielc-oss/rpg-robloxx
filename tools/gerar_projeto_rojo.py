"""Gera default.project.json a partir de src/. Seguranca: TODO no com $path tem $ignoreUnknownInstances=true, entao o
Rojo nunca apaga o que nao esta em src/ (KeyframeSequences, sons, particulas, modelos, backups do ServerStorage).
Uso: python -I gerar_projeto_rojo.py <repo>"""
import json, os, sys
repo = sys.argv[1]; src = os.path.join(repo, "src")
def nome_inst(f):
    for e in (".server.luau", ".client.luau", ".luau"):
        if f.endswith(e): return f[: -len(e)]
    return None
def no_dir(rel):
    d = {"$path": "src/" + rel.replace("\\", "/"), "$ignoreUnknownInstances": True}
    meta = os.path.join(src, rel, "init.meta.json")                     # vale tambem para subpastas montadas pelo Rojo
    if not os.path.exists(meta):
        with open(meta, "w", encoding="utf-8") as h: json.dump({"ignoreUnknownInstances": True}, h)
    return d
def conteudo(rel):
    out = {}
    for f in sorted(os.listdir(os.path.join(src, rel))):
        p = os.path.join(rel, f)
        if os.path.isdir(os.path.join(src, p)): out[f] = no_dir(p)
        elif nome_inst(f): out[nome_inst(f)] = {"$path": "src/" + p.replace("\\", "/")}
    return out
arv = {"$className": "DataModel"}
for svc in sorted(os.listdir(src)):
    if not os.path.isdir(os.path.join(src, svc)): continue
    n = {"$className": svc, "$ignoreUnknownInstances": True}
    if svc == "StarterPlayer":
        for sub in sorted(os.listdir(os.path.join(src, svc))):
            n[sub] = {"$className": sub, "$ignoreUnknownInstances": True, **conteudo(os.path.join(svc, sub))}
    else:
        n.update(conteudo(svc))
    arv[svc] = n
proj = {"name": "RPG_Dragoes", "servePort": 34872, "tree": arv}
with open(os.path.join(repo, "default.project.json"), "w", encoding="utf-8") as h: json.dump(proj, h, indent=2, ensure_ascii=False)
print("ok")
