#!/bin/bash
# Lote 4: folhas, GIFs (normal e lento), pranchas e resumo a partir dos renders de lote4_renders.sh
cd "$(dirname "$0")/.."
L=review/L4; F="python scripts/folha_gif.py"
for c in Montar Desmontar; do for k in lado 34 frente topo subida flanco; do $F $L/demo $c $k 33 1 lento; done; done
for k in lado 34 subida; do $F $L/seq Sequencia $k 66 1 lento; done
for c in Repouso Andar Corrida VirarEsquerda VirarDireita; do for k in lado 34 close; do $F $L/reuso $c $k 33 3; done; done
for c in VirarEsquerda VirarDireita CurvaAquaticaEsquerda CurvaAquaticaDireita; do $F $L/reuso $c topo 33 3; done
$F $L/reuso Corrida frente 33 3
for c in NadoParado Nado CurvaAquaticaEsquerda CurvaAquaticaDireita; do for k in lado_agua 34 close; do $F $L/reuso $c $k 33 3; done; done
for q in entrada saida; do for k in lado 34; do $F $L/agua $q $k 66 1 lento; done; done
R=REFERENCIAS/pantano-nebuloso/crocodilo-primordial/crocodilo-primordial-referencia-principal.png
python scripts/prancha.py ../../../$R review/L3/clipes/Observar_lado_000.png $L/PRANCHA_ref_x_L3_x_L4.png $L/encaixe/encaixe_com_lado.png $L/encaixe/encaixe_com_34.png $L/encaixe/encaixe_sem_lado.png --titulo "Referencia | L3 (sem cavaleiro) | L4: encaixe do manequim R15 aproximado + sela PROPOSTA (estudo, nao definido pela imagem)"
python scripts/prancha.py $L/encaixe/encaixe_com_frente.png $L/encaixe/encaixe_com_topo.png $L/PRANCHA_encaixe_L4.png $L/encaixe/encaixe_com_lado.png $L/encaixe/encaixe_com_tras.png $L/encaixe/encaixe_sem_close_lado.png $L/encaixe/encaixe_sem_close_topo.png $L/encaixe/encaixe_sem_sela_com_frente.png $L/encaixe/encaixe_sem_sela_com_close_lado.png --titulo "Encaixe L4: frente/topo/lado/tras com sela PROPOSTA; cristas (vermelho) sem cavaleiro; sem sela (cavaleiro direto nas cristas)"
python scripts/resumo_l4.py $L
echo LOTE4_POS_OK
