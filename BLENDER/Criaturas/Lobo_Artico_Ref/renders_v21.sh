#!/bin/sh
# Lote 2 L2a: renders de revisao (anim_v21). $1 = parte (corpo | closes | base). Rodar nesta pasta.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v21/CR_LoboArtico_Anim.blend; D=review/v21_lote2
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$1" in
corpo)
  R $A -P vistas_clipes_v21.py -- $D/corpo LOW Trote 0-53 perfil_E,perfil_D,frente,tras,34_E desloc
  R $A -P vistas_clipes_v21.py -- $D/corpo LOW Corrida 0-41 perfil_E,perfil_D,frente,tras,34_E desloc
  R $A -P vistas_clipes_v21.py -- $D/corpo LOW Trote 0-17 perfil_E,34_E,patas_E,patas_D pre=LOW_Trote_nolugar
  R $A -P vistas_clipes_v21.py -- $D/corpo LOW Corrida 0-13 perfil_E,34_E,patas_E,patas_D pre=LOW_Corrida_nolugar ;;
closes)
  for m in cores real; do for ac in Trote Corrida; do
    R $A -P vistas_closes_v21.py -- $D/closes $ac 0-$( [ $ac = Trote ] && echo 17 || echo 13 ) fresta_E,fresta_baixo,garganta_E,garganta_baixo,flanco_D,flanco_D_baixo $( [ $m = cores ] && echo cores )
  done; done ;;
base)
  for m in cores real; do R $A -P vistas_closes_v21.py -- $D/closes Andar 0-35 fresta_E,fresta_baixo,garganta_E,garganta_baixo,flanco_D,flanco_D_baixo $( [ $m = cores ] && echo cores ); done
  for L in LOD1 LOD2; do for ac in Trote Corrida; do R $A -P vistas_clipes_v21.py -- $D/lods $L $ac 0-$( [ $ac = Trote ] && echo 35 || echo 27 ) perfil_E,34_E desloc; done; done ;;
esac
echo RENDERS_V21_$1_FIM
