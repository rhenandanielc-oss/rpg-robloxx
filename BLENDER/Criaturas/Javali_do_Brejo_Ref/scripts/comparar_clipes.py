"""Compara medidas_clipes_Javali.json x medidas_clipes_JavaliBrejo.json e junta as medidas do render (avanco, deriva).
Uso: python scripts/comparar_clipes.py <pasta_lote> <pasta_render_base>  -> <pasta_lote>/comparacao.json e tabela no terminal"""
import sys, os, json
import numpy as np
D, RB = sys.argv[1], sys.argv[2]
b, v = [json.load(open(os.path.join(D, f"medidas_clipes_{p}.json"), encoding="utf-8"))["clipes"] for p in ("Javali", "JavaliBrejo")]
ROT = {"Repouso": "Repouso", "VirarE": "VirarE", "VirarD": "VirarD", "ParadoParaAndar": "cadeia_ParadoParaAndar", "AndarParaParado": "cadeia_AndarParaParado"}
out = {}
for n in b:
    pb, pv = np.array(b[n]["pose"]), np.array(v[n]["pose"])
    c = {"pose_identica_max_dif": float(np.abs(pb - pv).max()) if pb.shape == pv.shape else "formas diferentes"}
    for k in ("quadros", "pele_z_min_cm", "cabeca_z_min_cm", "cabeca_x_corpo_max", "corpo_auto_media", "corpo_auto_max", "estira_max"):
        c[k] = {"base": b[n][k], "brejo": v[n][k]}
    r = ROT.get(n) or next((x for x in (n, "cadeia_" + n) if os.path.isdir(os.path.join(D, x))), None)   # qualquer lote
    for lado, pasta in (("base", RB), ("brejo", D)):
        f = os.path.join(pasta, r, "medidas.json") if r else None
        if f and os.path.exists(f):
            m = json.load(open(f)); c.setdefault("render", {})[lado] = {k: m.get(k) for k in ("cadeia", "quadros", "avanco_total_u", "avanco_por_ciclo_u", "velocidade_media", "deriva_max_casco_apoiado", "pele_z_min", "estica_max", "salto_entre_clipes_graus")}
    out[n] = c
    print(n, "pose dif", c["pose_identica_max_dif"], "| cabeca min", c["cabeca_z_min_cm"], "| cab x corpo", c["cabeca_x_corpo_max"], "| auto", c["corpo_auto_media"], "| estira", c["estira_max"]["brejo"])
    if "render" in c: print("   render", c["render"])
json.dump(out, open(os.path.join(D, "comparacao.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
