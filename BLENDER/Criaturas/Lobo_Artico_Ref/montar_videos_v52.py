"""v52: video da CORRECAO DO APOIO nas curvas do Andar compartilhadas (laco/saida/fechada). ANTES = v51 (partida corrigida, curvas
v46c como instaladas), DEPOIS = v52 (curvas com o rolamento do pe no rumo em que a pata pousou). Mesma trajetoria e mesmo giro.
Uso: python montar_videos_v52.py <dir_quadros> <dir_saida>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar_videos_v46 as MV
MV.ROT_ANTES = "ANTES  v51  (laco v46c: DD 0,040 / TE 0,034)"; MV.ROT_DEPOIS = "DEPOIS  v52  (laco corrigido; partida <= 0,030)"
MV.NOTA_ANTES = "   (v51: no laco o rolamento do pe girava junto com o corpo; v52: fica no rumo em que a pata pousou)"
P = []
for v in ("perfil_E", "c34", "close_E"):
    P.append(MV.montar("e_" + v, "Partida em curva a ESQUERDA + laco + saida + parada - v51 x v52", "partida_curva_E", [[("ANTES", v), ("V46B", v)]]))
P.append(MV.montar("e_lento_close_E", "Partida em curva a ESQUERDA - camera lenta (patas)", "partida_curva_E", [[("ANTES", "close_E"), ("V46B", "close_E")]], lento=True))
for v in ("topo", "close_D"):
    P.append(MV.montar("d_" + v, "Partida em curva a DIREITA + laco + saida + parada - v51 x v52", "partida_curva_D", [[("ANTES", v), ("V46B", v)]]))
P.append(MV.montar("d_lento_close_D", "Partida em curva a DIREITA - camera lenta (patas)", "partida_curva_D", [[("ANTES", "close_D"), ("V46B", "close_D")]], lento=True))
for v in ("topo", "close_D"):
    P.append(MV.montar("f_" + v, "Curva FECHADA a direita (45 graus/s) - v51 x v52", "fechada_D", [[("ANTES", v), ("V46B", v)]]))
MV.juntar("video_v52_laco_corrigido", P)
