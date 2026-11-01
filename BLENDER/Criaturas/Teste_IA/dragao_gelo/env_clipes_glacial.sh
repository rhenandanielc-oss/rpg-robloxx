# Variaveis do gerador de clipes (meshy/anim_silverwing.py) para o Dragao Glacial r4. Uso: source env_clipes_glacial.sh
# Base: as do CR_Dragao (mesmas pernas/asas); pescoco ja erguido no repouso (NECK_BASE=0); sentado com as asas menos
# varridas para tras (recua 30 em vez de 48): com 48 os bracos e as pontas das asas se cruzavam sobre o dorso.
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$D/../dragao_novo/env_clipes_cr.sh"
export NECK_BASE=0
export P_ERGUIDA='{"recua": 30, "ergue": 54}'
# personalidade (sistema universal 01/11): movimentos mais calculados (corpo/cabeca menos amplos que o Fogo, 2,5) e
# batidas de asa amplas e cadenciadas (3 por clipe no voo e no pairar em vez de 4); velocidades da montaria iguais
export AMP=2.0 NB_VOO=3 NB_PAIRAR=3
export ROAR_ESTILO=gelo                    # rugido padrao v2 no estilo frio/controlado
