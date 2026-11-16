#!/bin/sh
# v35 (lote de vida, bloco 1: Deitar, Deitado, LevantarDeitado): validacao e renders. Base de comparacao = anim_v34 (12 acoes antigas iguais).
# $1 = parte: auditorias | vid_a | vid_b | vid_c | export | montar. Rodar nesta pasta. Saida: review/v35_vida/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v35/CR_LoboArtico_Anim.blend; A8=anim_v34/CR_LoboArtico_Anim.blend; D=review/v35_vida; P_="$1"
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_vida_v35.py -- $D/aud_vida_v35.json LOW,LOD1,LOD2
  R $A -P comparar_acoes_v29.py -- $A8 $D/comparar_v34_v35.json Repouso,Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,AndarParaTrote,TroteParaCorrida,TroteParaAndar,CorridaParaTrote
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_vida_v35.json LOW,LOD1,LOD2 Deitar,Deitado,LevantarDeitado
  ACOES_MET=Deitar,Deitado,LevantarDeitado R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_vida_v35.json ;;
vid_a) for ac in Deitar:93 Deitado:120 LevantarDeitado:72; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} perfil_E,frente; done ;;
vid_b) for ac in Deitar:93 Deitado:120 LevantarDeitado:72; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} tras,34_E; done ;;
vid_c) for ac in Deitar:93 Deitado:120 LevantarDeitado:72; do for L in LOD1 LOD2; do R $A -P vistas_acao_v35.py -- $D/quadros $L ${ac%%:*} 0-${ac##*:} perfil_D,34_E; done; done ;;
export)
  rm -rf anim_v35/export
  R $A -P exportar_clipes_v35.py -- anim_v35/export anim_v35/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v35.py -- anim_v35/export anim_v35/export/ref anim_v35/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_vida_v35.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V35_${P_}_FIM
