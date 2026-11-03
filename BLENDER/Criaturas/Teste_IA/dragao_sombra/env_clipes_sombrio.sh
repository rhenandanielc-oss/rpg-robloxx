# Variaveis do gerador de clipes (meshy/anim_silverwing.py) para o DRAGAO SOMBRIO. Uso: source env_clipes_sombrio.sh
# Base: as do Glacial (mesmo esqueleto, pescoco ja erguido no repouso, asas armadas no chao, raiz da asa presa no voo).
# Personalidade (proposta do DOCS/SISTEMA-ANIMACAO-DRAGOES.md, secao 5 -- NAO_APROVADO, validar com o usuario):
# predador silencioso e controlado -- corpo e cabeca com MENOS amplitude que o Fogo (2,5) e o Glacial (2,0), passada
# leve (sem o tranco do PASSO_PESADO do Fogo), batidas firmes e regulares (4 por clipe, sem o golpe lento do Glacial),
# rugido no estilo frio/contido (o "sombra" proprio fica para quando o kit/sons forem definidos).
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$D/../dragao_gelo/env_clipes_glacial.sh"
unset CABECA_RUGIDO                        # (03/11) cabeca dos rugidos do Glacial NAO vale para o Sombrio
export AMP=1.6 PASSO_PESADO=0
export NB_VOO=4 NB_PAIRAR=4 T_VOO=3.2 AMP_ASA=1.0 ASA_GOLPE=0.2
export ROAR_ESTILO=gelo
