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
# CERTIFICACAO (02/11, pedido do usuario "Glacial r9 — refinamento completo"):
# - asas RECOLHIDAS no chao (repouso, andar, correr, sentado, deitado): dobra lateral do DOBRA_JSON em vez das asas
#   armadas do Fogo (ASAS_ARMADAS=1 volta ao visual anterior);
# - deitado/dormindo com a barriga no chao (agachamento 0,235; antes 0,09 deixava o quadril ~2 studs acima do piso);
# - voo: batida mais profunda (ombro/umero x1,18) e com golpe forte (descida mais rapida, subida mais lenta) e mais
#   lenta (3 batidas em 3,6 s = 1,2 s por batida; o Fogo faz 0,8 s). A subida continua com 4 batidas (esforco).
export ASAS_ARMADAS=1 AG_DEITADO=0.235 AMP_ASA=1.18 ASA_GOLPE=0.35 T_VOO=3.6
# (usuario 02/11, depois da certificacao: "nao quero ele em nenhuma animacao com as asas dobradas, fica feio") -> asas
#   ARMADAS em todas as posturas de chao (parado, andar, sentado, deitado...); a dobra lateral nao e mais usada no Glacial
# (usuario 02/11) deitado/descansando: asas BAIXAS, leve dobra, pontas rentes ao chao (asas_descanso + asas_rente_chao)
export P_DESCANSO='{"ergue": -8, "recua": 6, "cotovelo": -26, "punho": 46, "leque": 0.4}' ALVO_DESCANSO=0.062
# (usuario 02/11) "ao voar as asas nao ficam grudadas ao corpo, mas sim fora do corpo, com o movimento": com AMP_ASA 1,18
#   as pontas chegavam a 0,2 stud da linha do corpo (asas se encostando no alto e rentes as patas embaixo). 0,7 mantem
#   ~117 graus de batida (-40 a +77) com as pontas a 7-10 studs do corpo; o golpe forte (ASA_GOLPE) e a cadencia ficam
export AMP_ASA=0.7
# (usuario 02/11, esclarecido) o pedido era a asa NAO se soltar do corpo no voo (defeito), nao asas mais afastadas: volta a
#   batida profunda AMP_ASA 1,18 e liga OMBRO_FIXO (raiz da asa presa ao tronco; o giro do ombro passa para o umero). Costura
#   asa-corpo no ar: Pairar 4,2 -> 0,84 stud, Subida 2,1 -> 0,81, Voo 1,3 -> 0,80 (= nivel do dragao parado no chao)
export AMP_ASA=1.18 OMBRO_FIXO=1
