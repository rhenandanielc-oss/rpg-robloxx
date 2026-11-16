#!/bin/sh
# v38 (LevantarSentado com a cauda voltando por fora): validacao e renders. Base de comparacao = anim_v37 (20 acoes iguais).
# $1 = parte: auditorias | vid_a | vid_b | vid_c | export | montar. Rodar nesta pasta. Saida: review/v38_cauda/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v38/CR_LoboArtico_Anim.blend; A8=anim_v37/CR_LoboArtico_Anim.blend; D=review/v38_cauda; P_="$1"
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_vida_v38.py -- $D/aud_vida_v38.json LOW,LOD1,LOD2
  R $A -P comparar_acoes_v29.py -- $A8 $D/comparar_v37_v38.json Repouso,Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,AndarParaTrote,TroteParaCorrida,TroteParaAndar,CorridaParaTrote,Deitar,Descanso,Adormecer,Dormindo,Despertar,LevantarDeitado,Sentar,Sentado
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_vida_v38.json LOW,LOD1,LOD2 LevantarSentado
  ACOES_MET=LevantarSentado R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_vida_v38.json ;;
vid_a) for ac in LevantarSentado:48; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} perfil_E,frente; done ;;
vid_b) for ac in LevantarSentado:48; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} tras,34_E; done ;;
vid_c) for ac in LevantarSentado:48; do for L in LOD1 LOD2; do R $A -P vistas_acao_v35.py -- $D/quadros $L ${ac%%:*} 0-${ac##*:} perfil_D,34_E; done; done ;;
export)
  rm -rf anim_v38/export
  R $A -P exportar_clipes_v38.py -- anim_v38/export anim_v38/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v38.py -- anim_v38/export anim_v38/export/ref anim_v38/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_vida_v38.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V38_${P_}_FIM
