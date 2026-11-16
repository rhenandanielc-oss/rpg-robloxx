#!/bin/sh
# v27 (viradas com as pernas sem entrar para dentro): validacao e renders. $1 = parte: auditorias | pernas | seq_low | seq_lods | closes | export | montar.
# Rodar nesta pasta. Saida: review/v27_pernas/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v27/CR_LoboArtico_Anim.blend; D=review/v27_pernas; P_="$1"
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
pernas)
  for L in LOW LOD1 LOD2; do
    R anim_v26/CR_LoboArtico_Anim.blend -P diag_pernas_v27.py -- $D/diag_pernas_v26_$L.json Andar,Trote,Corrida,VirarEsquerda,VirarDireita $L
    R $A -P diag_pernas_v27.py -- $D/diag_pernas_v27_$L.json Andar,Trote,Corrida,VirarEsquerda,VirarDireita $L; done ;;
auditorias)
  R $A -P auditar_viradas_v27.py -- $D/aud_viradas_v27.json LOW,LOD1,LOD2
  R $A -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v27.json LOW,LOD1,LOD2
  R $A -P auditar_clipes_v21.py -- $D/aud_clipes_v27_antigas.json LOW,LOD1,LOD2 Andar,Trote,Corrida,Repouso
  R $A -P diag_apoios_v24.py -- $D/diag_apoios_v27_antigas.json
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_viradas_v27.json LOW,LOD1,LOD2 VirarEsquerda,VirarDireita
  ACOES_MET=VirarEsquerda,VirarDireita R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_viradas_v27.json ;;
seq_low)
  for sq in ida_volta_E ida_volta_D; do R $A -P vistas_viradas_v27.py -- $D/quadros LOW $sq topo,perfil_E,perfil_D,frente,tras,34,patas_E,patas_D; done
  R anim_v26/CR_LoboArtico_Anim.blend -P vistas_viradas_v26.py -- $D/quadros_v26 LOW ida_volta_E frente,tras,topo ;;
seq_lods) for L in LOD1 LOD2; do R $A -P vistas_viradas_v27.py -- $D/quadros $L ida_volta_E topo,frente,patas_D; done ;;
closes)
  for ac in VirarEsquerda VirarDireita; do
    R $A -P vistas_closes_v21.py -- $D/closes $ac 0-92 fresta_E,garganta_E,flanco_D_baixo
    R $A -P vistas_closes_v21.py -- $D/closes $ac 0-92 fresta_E,garganta_E,flanco_D_baixo cores; done ;;
export)
  rm -rf anim_v27/export
  R $A -P exportar_clipes_v27.py -- anim_v27/export anim_v27/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v27.py -- anim_v27/export anim_v27/export/ref anim_v27/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200
  "$B" -b --factory-startup -P auditar_viradas_v27.py -- $D/aud_viradas_v27_reimport.json LOW,LOD1,LOD2 --glb anim_v27/export anim_v27 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v27.json "$B" -b --factory-startup -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v27_reimport.json LOW,LOD1,LOD2 --glb anim_v27/export anim_v27 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v27.json "$B" -b --factory-startup -P apoios_reimport_v24.py -- anim_v27/export anim_v27 $D/diag_apoios_v27_antigas.json $D/apoios_reimport_v27_antigas.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_pernas_v27.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V27_${P_}_FIM
