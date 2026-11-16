"""Resumo da auditoria do rig v9 (pior caso por LOD e por metrica, com o quadro). Uso: python resumo_rig_v9.py review/v9_rig"""
import sys, os, json
D = sys.argv[1]; A = json.load(open(os.path.join(D, "auditoria_rig.json")))["niveis"]; S = {}
for L, R in A.items():
    q = R["quadros"]; mh, mc = [k for k in q["repouso"] if k.endswith("_Cabeca")][0], [k for k in q["repouso"] if k.endswith("_Corpo")][0]
    def pior(f, chaves=None):
        it = [(f(r), k) for k, r in q.items() if chaves is None or k in chaves]; v, k = max(it); return {"valor": v, "pico": k}
    fora_boca = [k for k in q if not k.startswith(("boca", "combinacao"))]
    tronco = [k for k in q if k.startswith(("coluna", "inclina", "peso"))]
    s = S[L] = {
        "repouso_desvio": q["repouso"]["desvio_repouso_max"], "costura_fresta_max": pior(lambda r: r["costura_fresta_max"]),
        "cabeca_>2x_fora_boca": pior(lambda r: r[mh]["esticadas_>2x"], fora_boca), "corpo_>2x": pior(lambda r: r[mc]["esticadas_>2x"]),
        "corpo_max_razao": pior(lambda r: r[mc]["max_razao"]), "cabeca_max_razao_fora_boca": pior(lambda r: r[mh]["max_razao"], fora_boca),
        "faces_viradas_corpo": pior(lambda r: r[mc]["faces_viradas"]), "area_viradas_corpo": pior(lambda r: r[mc]["area_viradas"]),
        "faces_viradas_cabeca": pior(lambda r: r[mh]["faces_viradas"]), "colapso_corpo": pior(lambda r: r[mc]["colapso_vertices"]),
        "patas_plantadas_deslize_tronco": pior(lambda r: max(r["patas_deslize"].values()), tronco),
        "patas_plantadas_afundam_tronco": pior(lambda r: -min(r["patas_zmin_delta"].values()), tronco),
        "pata_testada_afunda": pior(lambda r: -min(r["patas_zmin_delta"].values()), [k for k in q if k.startswith(("diant", "tras"))]),
        "cristais_variacao_aresta": pior(lambda r: r["cristais_variacao_aresta_max"]), "cristais_base_delta": pior(lambda r: r["cristais_base_dist_delta_max"]),
        "boca_max": {k: q["boca_max"][k] for k in ("boca_rig_x_v8", "cantos_rig", "cantos_teste_v8")}, "iris_piscar_total": q["piscar_total"]["iris"]}
    if "marca_dist_pele_max" in q["repouso"]:
        s["marca_dist_pele"] = {"repouso": q["repouso"]["marca_dist_pele_max_repouso"], "pior": pior(lambda r: r["marca_dist_pele_max"])}
    if "pelagem_raiz_delta_max" in q["repouso"]:
        s["pelagem_raiz_delta"] = {"p99_pior": pior(lambda r: r["pelagem_raiz_delta_p99"]), "max_pior": pior(lambda r: r["pelagem_raiz_delta_max"])}
    if "cruzamentos_novos" in q["boca_max"]:
        s["cruzamentos_novos"] = pior(lambda r: r.get("cruzamentos_novos", 0)); s["cruzamentos_por_pico"] = {k: r.get("cruzamentos_novos", 0) for k, r in q.items()}
json.dump(S, open(os.path.join(D, "resumo_rig.json"), "w"), indent=1)
for L, s in S.items():
    print("==", L)
    for k, v in s.items():
        if k != "cruzamentos_por_pico": print("  %-32s %s" % (k, v))
