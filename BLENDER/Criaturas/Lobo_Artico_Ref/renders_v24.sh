#!/bin/sh
# v24 (apoios): renders de revisao v23 x v24 com as mesmas cameras (vistas_apoios_v24.py) + montagem dos videos.
# $1 = parte: low | lods | montar. Rodar nesta pasta. Saida: review/v24_apoios/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=review/v24_apoios
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-160; }
P_="$1"
case "$1" in
low) for v in v23 v24; do for ac in "Andar 2" "Trote 3" "Corrida 3"; do set -- $ac
       R anim_$v/CR_LoboArtico_Anim.blend -P vistas_apoios_v24.py -- $D/quadros/$v LOW $1 $2 perfil_E,perfil_D,frente,tras,34_E,patas_E,patas_D; done; done ;;
lods) for v in v23 v24; do for L in LOD1 LOD2; do for ac in "Andar 2" "Trote 3" "Corrida 3"; do set -- $ac
       R anim_$v/CR_LoboArtico_Anim.blend -P vistas_apoios_v24.py -- $D/quadros/$v $L $1 $2 perfil_D,patas_E,patas_D; done; done; done ;;
montar) python prancha_apoios_v24.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/Apoios_$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V24_${P_}_FIM
