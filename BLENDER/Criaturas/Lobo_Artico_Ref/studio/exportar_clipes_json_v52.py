"""v52 = exportar_clipes_json_v51 com as 16 CURVAS DO ANDAR corrigidas (anim_v52) + PartidaCurva E/D v51 + ParadaAndar (igual);
para a reimportacao local da sequencia inteira. Grava studio/json_v52 e rest_v52.json."""
import os, sys, runpy
_S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exportar_clipes_json_v51.py")
_src = open(_S, encoding="utf-8").read()
_lados = ("Esquerda", "Direita")
_curvas = [a + l for l in _lados for a in ("AndarCurva", "AndarCurvaFechada", "AndarParaCurva", "CurvaParaAndar", "CurvaParaFechada", "FechadaParaCurva", "CurvaBreve", "CurvaCurta")]
_acoes = tuple(_curvas + ["PartidaCurvaEsquerda", "PartidaCurvaDireita", "ParadaAndar"])
_a = 'ACOES = ("PartidaCurvaEsquerda", "PartidaCurvaDireita", "AndarCurvaEsquerda", "AndarCurvaDireita", "CurvaParaAndarEsquerda", "CurvaParaAndarDireita", "ParadaAndar")'
assert _a in _src
_src = _src.replace(_a, "ACOES = %r" % (_acoes,)).replace('LACOS = {"AndarCurvaEsquerda", "AndarCurvaDireita"}', 'LACOS = {a + l for l in ("Esquerda", "Direita") for a in ("AndarCurva", "AndarCurvaFechada")}').replace("rest_v51.json", "rest_v52.json")
exec(compile(_src, _S, "exec"))
