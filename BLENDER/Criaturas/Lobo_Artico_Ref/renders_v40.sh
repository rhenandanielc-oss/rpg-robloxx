#!/bin/sh
# v40 (lote de vida, bloco 3: Farejar, Comer, Beber; entrada/laco/saida): validacao e renders. Base de comparacao = anim_v39 (21 acoes iguais).
# $1 = parte: auditorias | vid_a | vid_b | vid_c | export | montar. Rodar nesta pasta. Saida: review/v40_bloco3/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v40/CR_LoboArtico_Anim.blend; A8=anim_v39/CR_LoboArtico_Anim.blend; D=review/v40_bloco3; P_="$1"
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_vida_v40.py -- $D/aud_vida_v40.json LOW,LOD1,LOD2
  R $A -P comparar_acoes_v29.py -- $A8 $D/comparar_v39_v40.json Repouso,Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,AndarParaTrote,TroteParaCorrida,TroteParaAndar,CorridaParaTrote,Deitar,Descanso,Adormecer,Dormindo,Despertar,LevantarDeitado,Sentar,Sentado,LevantarSentado
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_vida_v40.json LOW,LOD1,LOD2 Farejar,Farejando,PararFarejar,Comer,Comendo,PararComer,Beber,Bebendo,PararBeber
  ACOES_MET=Comer,Comendo,Beber,Bebendo R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_vida_v40.json ;;
vid_a) for ac in Farejar:30 Farejando:120 PararFarejar:30 Comer:45 Comendo:150 PararComer:45 Beber:54 Bebendo:90 PararBeber:54; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} perfil_E,frente; done ;;
vid_b) for ac in Farejar:30 Farejando:120 PararFarejar:30 Comer:45 Comendo:150 PararComer:45 Beber:54 Bebendo:90 PararBeber:54; do R $A -P vistas_acao_v35.py -- $D/quadros LOW ${ac%%:*} 0-${ac##*:} tras,34_E; done ;;
vid_c) for ac in Farejar:30 Farejando:120 PararFarejar:30 Comer:45 Comendo:150 PararComer:45 Beber:54 Bebendo:90 PararBeber:54; do for L in LOD1 LOD2; do R $A -P vistas_acao_v35.py -- $D/quadros $L ${ac%%:*} 0-${ac##*:} perfil_D,34_E; done; done ;;
export)
  rm -rf anim_v40/export
  R $A -P exportar_clipes_v40.py -- anim_v40/export anim_v40/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v40.py -- anim_v40/export anim_v40/export/ref anim_v40/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_vida_v40.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V40_${P_}_FIM
