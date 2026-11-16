#!/bin/sh
# v31 (pernas dianteiras retas vistas de frente): validacao e renders. Base de comparacao = anim_v30.
# $1 = parte: auditorias | seq_a | seq_b | seq_c | seq_d | seq_lods | comp_v28 | comp_v29 | closes | export | montar. Rodar nesta pasta.
# Saida: review/v31_frontal/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v31/CR_LoboArtico_Anim.blend; A8=anim_v30/CR_LoboArtico_Anim.blend; D=review/v31_frontal; P_="$1"
TR=AndarParaTrote,TroteParaAndar,TroteParaCorrida,CorridaParaTrote; MUD=TroteParaAndar,CorridaParaTrote
CT=287-380; TA=381-534        # janelas da linha do tempo (iguais na v28 e na v29): Corrida q0..CorridaParaTrote..Trote 1 ciclo; Trote 1 ciclo..TroteParaAndar..Andar
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_marchas_v29.py -- $D/aud_marchas_v31.json LOW,LOD1,LOD2
  R $A -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v31.json LOW,LOD1,LOD2
  R $A -P auditar_viradas_v27.py -- $D/aud_viradas_v31.json LOW,LOD1,LOD2
  R $A -P diag_apoios_v24.py -- $D/diag_apoios_v31_antigas.json
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_v31.json LOW,LOD1,LOD2 Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,$TR
  ACOES_MET=Andar,Trote,Corrida,Arrancada,Frenagem,$TR R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_v31.json
  R $A -P comparar_acoes_v29.py -- $A8 $D/comparar_v30_v31.json Repouso,Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,AndarParaTrote,TroteParaCorrida,TroteParaAndar,CorridaParaTrote
  R $A -P folga_patas_v30.py -- $D/folga_v31_lods.json LOW,LOD1,LOD2
  R $A -P diag_patas_giro_v30.py -- $D/giro_v31.json
  R $A -P diag_perna_frontal_v31.py -- $D/frontal_v31.json ;;
seq_a) R $A -P vistas_marchas_v29.py -- $D/quadros LOW perfil_D,perfil_E ;;
seq_b) R $A -P vistas_marchas_v29.py -- $D/quadros LOW frente,tras,34_E ;;
seq_c) R $A -P vistas_marchas_v29.py -- $D/quadros LOW patas_E,patas_D ;;
seq_d) R $A -P vistas_marchas_v29.py -- $D/quadros LOW traseiras_E,fixa_D ;;
seq_lods) for L in LOD1 LOD2; do R $A -P vistas_marchas_v29.py -- $D/quadros $L perfil_E,frente,patas_E; done ;;
export)
  rm -rf anim_v31/export
  R $A -P exportar_clipes_v29.py -- anim_v31/export anim_v31/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v29.py -- anim_v31/export anim_v31/export/ref anim_v31/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200
  "$B" -b --factory-startup -P auditar_marchas_v29.py -- $D/aud_marchas_v31_reimport.json LOW,LOD1,LOD2 --glb anim_v31/export anim_v31 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v29.json "$B" -b --factory-startup -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v31_reimport.json LOW,LOD1,LOD2 --glb anim_v31/export anim_v31 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v29.json "$B" -b --factory-startup -P apoios_reimport_v24.py -- anim_v31/export anim_v31 $D/diag_apoios_v31_antigas.json $D/apoios_reimport_v31_antigas.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_frontal_v31.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V31_${P_}_FIM
