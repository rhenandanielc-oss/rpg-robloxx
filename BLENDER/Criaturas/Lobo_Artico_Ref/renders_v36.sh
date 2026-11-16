#!/bin/sh
# v36 (lote de vida, bloco 1 revisto: Deitar, Descanso, Adormecer, Dormindo, Despertar, LevantarDeitado): validacao e renders. Base de comparacao = anim_v34 (12 acoes antigas iguais).
# $1 = parte: auditorias | vid_a | vid_b | vid_c | export | montar. Rodar nesta pasta. Saida: review/v36_descanso/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v36/CR_LoboArtico_Anim.blend; A8=anim_v34/CR_LoboArtico_Anim.blend; D=review/v36_descanso; P_="$1"
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_vida_v36.py -- $D/aud_vida_v36.json LOW,LOD1,LOD2
  R $A -P comparar_acoes_v29.py -- $A8 $D/comparar_v34_v36.json Repouso,Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,AndarParaTrote,TroteParaCorrida,TroteParaAndar,CorridaParaTrote
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_vida_v36.json LOW,LOD1,LOD2 Deitar,Descanso,Adormecer,Dormindo,Despertar,LevantarDeitado
  ACOES_MET=Deitar,Descanso,Dormindo,LevantarDeitado R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_vida_v36.json ;;
vid_a) for ac in Deitar:80 Descanso:150 Adormecer:66 Dormindo:180 Despertar:45 LevantarDeitado:66; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} perfil_E,frente; done ;;
vid_b) for ac in Deitar:80 Descanso:150 Adormecer:66 Dormindo:180 Despertar:45 LevantarDeitado:66; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} tras,34_E; done ;;
vid_c) for ac in Deitar:80 Descanso:150 Adormecer:66 Dormindo:180 Despertar:45 LevantarDeitado:66; do for L in LOD1 LOD2; do R $A -P vistas_acao_v35.py -- $D/quadros $L ${ac%%:*} 0-${ac##*:} perfil_D,34_E; done; done ;;
export)
  rm -rf anim_v36/export
  R $A -P exportar_clipes_v36.py -- anim_v36/export anim_v36/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v36.py -- anim_v36/export anim_v36/export/ref anim_v36/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_vida_v36.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V36_${P_}_FIM
