#!/bin/sh
# v23 (retopologia da prega coxa D x ventre): renders de revisao com as MESMAS cameras para v21 / v22 / v23 (diag_vistas_v23.py).
# $1 = parte: repouso | poses | lods | video | montar. Rodar nesta pasta. Saida: review/v23_flanco/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=review/v23_flanco
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-160; }
CL=barriga,flanco_D_baixo,virilha_D; CORPO=c_perfil_D,c_perfil_E,c_34_D,c_tras,c_baixo
case "$1" in
repouso)
  for v in v21 v22 v23; do
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/repouso/$v repouso 0-0 $CORPO real
    for m in real sempelo wire pesos; do R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/repouso/$v repouso 0-0 $CL $m; done
  done ;;
poses)
  for v in v21 v22 v23; do for m in real sempelo wire pesos dobras; do
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/poses/$v Trote 6-6 $CL $m
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/poses/$v Corrida 6-12:2 $CL $m
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/poses/$v Andar 14-14 $CL $m
  done; done ;;
lods)
  for v in v21 v23; do for L in LOD1 LOD2; do for m in sempelo wire; do
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/lods/$v repouso 0-0 barriga,flanco_D_baixo $m $L
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/lods/$v Trote 6-6 barriga,flanco_D_baixo $m $L
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/lods/$v Corrida 12-12 barriga,virilha_D $m $L
  done; R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/lods/$v repouso 0-0 c_perfil_D,c_34_D real $L; done; done ;;
video)
  for v in ${2:-v21 v22 v23}; do
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/video/$v Trote 0-17 barriga,virilha_D,c_34_D real
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/video/$v Corrida 0-13 barriga,virilha_D,c_34_D real
    R anim_$v/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/video/$v Andar 0-35 barriga,virilha_D,c_34_D real
  done ;;
montar)
  python prancha_flanco_v23.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/Flanco_$(basename $d | sed 's/video_//') 1928 1088 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V23_$1_FIM
