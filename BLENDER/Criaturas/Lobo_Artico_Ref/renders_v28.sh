#!/bin/sh
# v28 (L2b bloco 3: trocas de marcha AndarParaTrote, TroteParaAndar, TroteParaCorrida, CorridaParaTrote): validacao e renders.
# $1 = parte: auditorias | seq_a | seq_b | seq_c | seq_lods | closes | export | montar. Rodar nesta pasta. Saida: review/v28_marchas/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v28/CR_LoboArtico_Anim.blend; D=review/v28_marchas; P_="$1"
TR=AndarParaTrote,TroteParaAndar,TroteParaCorrida,CorridaParaTrote
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_marchas_v28.py -- $D/aud_marchas_v28.json LOW,LOD1,LOD2
  R $A -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v28.json LOW,LOD1,LOD2
  R $A -P auditar_viradas_v27.py -- $D/aud_viradas_v28.json LOW,LOD1,LOD2
  R $A -P auditar_clipes_v21.py -- $D/aud_clipes_v28_antigas.json LOW,LOD1,LOD2 Andar,Trote,Corrida,Repouso
  R $A -P diag_apoios_v24.py -- $D/diag_apoios_v28_antigas.json
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_marchas_v28.json LOW,LOD1,LOD2 $TR
  ACOES_MET=$TR R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_marchas_v28.json
  ACOES_MET=Trote,Corrida R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_trote_corrida_v28.json ;;
seq_a) R $A -P vistas_marchas_v28.py -- $D/quadros LOW perfil_D,perfil_E ;;
seq_b) R $A -P vistas_marchas_v28.py -- $D/quadros LOW frente,tras,34_E ;;
seq_c) R $A -P vistas_marchas_v28.py -- $D/quadros LOW patas_E,patas_D ;;
seq_lods) for L in LOD1 LOD2; do R $A -P vistas_marchas_v28.py -- $D/quadros $L perfil_D,patas_D; done ;;
closes)
  for ac in AndarParaTrote TroteParaAndar TroteParaCorrida CorridaParaTrote; do n=$(python -c "import json;print(json.load(open('anim_v28/marchas_v28.json'))['acoes']['$ac']['quadros'])")
    R $A -P vistas_closes_v21.py -- $D/closes $ac 0-$n fresta_E,garganta_E,flanco_D_baixo
    R $A -P vistas_closes_v21.py -- $D/closes $ac 0-$n fresta_E,garganta_E,flanco_D_baixo cores; done ;;
export)
  rm -rf anim_v28/export
  R $A -P exportar_clipes_v28.py -- anim_v28/export anim_v28/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v28.py -- anim_v28/export anim_v28/export/ref anim_v28/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200
  "$B" -b --factory-startup -P auditar_marchas_v28.py -- $D/aud_marchas_v28_reimport.json LOW,LOD1,LOD2 --glb anim_v28/export anim_v28 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v28.json "$B" -b --factory-startup -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v28_reimport.json LOW,LOD1,LOD2 --glb anim_v28/export anim_v28 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v28.json "$B" -b --factory-startup -P apoios_reimport_v24.py -- anim_v28/export anim_v28 $D/diag_apoios_v28_antigas.json $D/apoios_reimport_v28_antigas.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_marchas_v28.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V28_${P_}_FIM
