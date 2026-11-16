#!/bin/sh
# v41 (lote de vida, bloco 4: Uivar/Uivando/PararUivar e Sacudir): validacao e renders. Base de comparacao = anim_v40 (30 acoes iguais).
# $1 = parte: auditorias | vid_a | vid_b | vid_c | export | montar. Rodar nesta pasta. Saida: review/v41_bloco4/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v41/CR_LoboArtico_Anim.blend; A8=anim_v40/CR_LoboArtico_Anim.blend; D=review/v41_bloco4; P_="$1"
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_vida_v41.py -- $D/aud_vida_v41.json LOW,LOD1,LOD2
  R $A -P comparar_acoes_v29.py -- $A8 $D/comparar_v40_v41.json Repouso,Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,AndarParaTrote,TroteParaCorrida,TroteParaAndar,CorridaParaTrote,Deitar,Descanso,Adormecer,Dormindo,Despertar,LevantarDeitado,Sentar,Sentado,LevantarSentado,Farejar,Farejando,PararFarejar,Comer,Comendo,PararComer,Beber,Bebendo,PararBeber
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_vida_v41.json LOW,LOD1,LOD2 Uivar,Uivando,PararUivar,Sacudir
  ACOES_MET=Uivando,Sacudir R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_vida_v41.json ;;
vid_a) for ac in Uivar:36 Uivando:150 PararUivar:36 Sacudir:60; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} perfil_E,frente; done ;;
vid_b) for ac in Uivar:36 Uivando:150 PararUivar:36 Sacudir:60; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} tras,34_E; done ;;
vid_c) for ac in Uivar:36 Uivando:150 PararUivar:36 Sacudir:60; do for L in LOD1 LOD2; do R $A -P vistas_acao_v35.py -- $D/quadros $L ${ac%%:*} 0-${ac##*:} perfil_D,34_E; done; done ;;
export)
  rm -rf anim_v41/export
  R $A -P exportar_clipes_v41.py -- anim_v41/export anim_v41/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v41.py -- anim_v41/export anim_v41/export/ref anim_v41/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_vida_v41.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V41_${P_}_FIM
