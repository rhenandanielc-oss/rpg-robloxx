#!/bin/sh
# v37 (lote de vida, bloco 2: Sentar, Sentado, LevantarSentado): validacao e renders. Base de comparacao = anim_v34 (12 acoes antigas iguais).
# $1 = parte: auditorias | vid_a | vid_b | vid_c | export | montar. Rodar nesta pasta. Saida: review/v37_sentado/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v37/CR_LoboArtico_Anim.blend; A8=anim_v36/CR_LoboArtico_Anim.blend; D=review/v37_sentado; P_="$1"
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_vida_v37.py -- $D/aud_vida_v37.json LOW,LOD1,LOD2
  R $A -P comparar_acoes_v29.py -- $A8 $D/comparar_v36_v37.json Repouso,Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,AndarParaTrote,TroteParaCorrida,TroteParaAndar,CorridaParaTrote,Deitar,Descanso,Adormecer,Dormindo,Despertar,LevantarDeitado
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_vida_v37.json LOW,LOD1,LOD2 Sentar,Sentado,LevantarSentado
  ACOES_MET=Sentar,Sentado,LevantarSentado R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_vida_v37.json ;;
vid_a) for ac in Sentar:57 Sentado:150 LevantarSentado:48; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} perfil_E,frente; done ;;
vid_b) for ac in Sentar:57 Sentado:150 LevantarSentado:48; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} tras,34_E; done ;;
vid_c) for ac in Sentar:57 Sentado:150 LevantarSentado:48; do for L in LOD1 LOD2; do R $A -P vistas_acao_v35.py -- $D/quadros $L ${ac%%:*} 0-${ac##*:} perfil_D,34_E; done; done ;;
export)
  rm -rf anim_v37/export
  R $A -P exportar_clipes_v37.py -- anim_v37/export anim_v37/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v37.py -- anim_v37/export anim_v37/export/ref anim_v37/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_vida_v37.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V37_${P_}_FIM
