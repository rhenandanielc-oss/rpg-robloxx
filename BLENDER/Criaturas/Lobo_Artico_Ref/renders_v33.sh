#!/bin/sh
# v33 (patas sem virar ao andar e correr: quatro patas): validacao e renders. Base de comparacao = anim_v32.
# $1 = parte: auditorias | seq_a | seq_b | seq_c | seq_d | seq_lods | comp_v28 | comp_v29 | closes | export | montar. Rodar nesta pasta.
# Saida: review/v33_patas/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v33/CR_LoboArtico_Anim.blend; A8=anim_v32/CR_LoboArtico_Anim.blend; D=review/v33_patas; P_="$1"
TR=AndarParaTrote,TroteParaAndar,TroteParaCorrida,CorridaParaTrote; MUD=TroteParaAndar,CorridaParaTrote
CT=287-380; TA=381-534        # janelas da linha do tempo (iguais na v28 e na v29): Corrida q0..CorridaParaTrote..Trote 1 ciclo; Trote 1 ciclo..TroteParaAndar..Andar
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_marchas_v29.py -- $D/aud_marchas_v33.json LOW,LOD1,LOD2
  R $A -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v33.json LOW,LOD1,LOD2
  R $A -P auditar_viradas_v27.py -- $D/aud_viradas_v33.json LOW,LOD1,LOD2
  R $A -P diag_apoios_v24.py -- $D/diag_apoios_v33_antigas.json
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_v33.json LOW,LOD1,LOD2 Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,$TR
  ACOES_MET=Andar,Trote,Corrida,Arrancada,Frenagem,$TR R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_v33.json
  R $A -P comparar_acoes_v29.py -- $A8 $D/comparar_v32_v33.json Repouso,Andar,Trote,Corrida,Arrancada,Frenagem,VirarEsquerda,VirarDireita,AndarParaTrote,TroteParaCorrida,TroteParaAndar,CorridaParaTrote
  R $A -P folga_patas_v30.py -- $D/folga_v33_lods.json LOW,LOD1,LOD2

  R $A -P auditoria_real_v32.py -- $D/auditoria_v33.json
  R $A8 -P auditoria_real_v32.py -- $D/auditoria_v32.json
  R $A -P diag_patas_giro_v30.py -- $D/giro_v33.json ;;
seq_a) R $A -P vistas_marchas_v29.py -- $D/quadros LOW perfil_D,perfil_E ;;
seq_b) R $A -P vistas_marchas_v29.py -- $D/quadros LOW frente,tras,34_E ;;
seq_c) R $A -P vistas_marchas_v29.py -- $D/quadros LOW patas_E,patas_D ;;
seq_d) R $A -P vistas_marchas_v29.py -- $D/quadros LOW traseiras_E,fixa_D ;;
seq_lods) for L in LOD1 LOD2; do R $A -P vistas_marchas_v29.py -- $D/quadros $L perfil_E,frente,patas_E; done ;;
export)
  rm -rf anim_v33/export
  R $A -P exportar_clipes_v29.py -- anim_v33/export anim_v33/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v29.py -- anim_v33/export anim_v33/export/ref anim_v33/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200
  "$B" -b --factory-startup -P auditar_marchas_v29.py -- $D/aud_marchas_v33_reimport.json LOW,LOD1,LOD2 --glb anim_v33/export anim_v33 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v29.json "$B" -b --factory-startup -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v33_reimport.json LOW,LOD1,LOD2 --glb anim_v33/export anim_v33 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v29.json "$B" -b --factory-startup -P apoios_reimport_v24.py -- anim_v33/export anim_v33 $D/diag_apoios_v33_antigas.json $D/apoios_reimport_v33_antigas.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  [ -f $D/folga_v32_lods.json ] && mv $D/folga_v32_lods.json $D/folga_v33_lods.json
  python prancha_patas_v33.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V33_${P_}_FIM
