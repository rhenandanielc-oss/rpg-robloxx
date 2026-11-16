#!/bin/sh
# v25 (L2b bloco 1: Arrancada + Frenagem): validacao e renders. $1 = parte: auditorias | seq_low | seq_lods | closes | repouso | export | montar.
# Rodar nesta pasta. Saida: review/v25_transicoes/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v25/CR_LoboArtico_Anim.blend; D=review/v25_transicoes; P_="$1"
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_sequencia_v25.py -- $D/aud_seq_v25.json LOW,LOD1,LOD2
  R $A -P auditar_clipes_v21.py -- $D/aud_clipes_v25_antigas.json LOW,LOD1,LOD2 Andar,Trote,Corrida,Repouso
  R $A -P diag_apoios_v24.py -- $D/diag_apoios_v25_antigas.json
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_transicoes_v25.json LOW,LOD1,LOD2 Arrancada,Frenagem
  ACOES_MET=Arrancada,Frenagem R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_transicoes_v25.json
  ACOES_MET=Corrida R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_corrida_v25.json ;;
seq_low) R $A -P vistas_sequencia_v25.py -- $D/quadros LOW perfil_E,perfil_D,frente,tras,34_E,patas_E,patas_D,fixa_D ;;
seq_lods) for L in LOD1 LOD2; do R $A -P vistas_sequencia_v25.py -- $D/quadros $L perfil_D,patas_E,patas_D; done ;;
closes)
  for ac in "Arrancada 0-75" "Frenagem 0-48"; do set -- $ac
    R $A -P vistas_closes_v21.py -- $D/closes $1 $2 fresta_E,garganta_E,flanco_D_baixo
    R $A -P vistas_closes_v21.py -- $D/closes $1 $2 fresta_E,garganta_E,flanco_D_baixo cores; done ;;
repouso)
  R anim_v24/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/repouso/v24 repouso 0-0 c_perfil_D,c_perfil_E,c_34_D,c_tras real
  R $A -P diag_vistas_v23.py -- $D/repouso/v25 repouso 0-0 c_perfil_D,c_perfil_E,c_34_D,c_tras real
  R $A -P diag_vistas_v23.py -- $D/repouso/v25_fim_frenagem Frenagem 48-48 c_perfil_D,c_perfil_E,c_34_D,c_tras real pre=real_LOW_frenagem_fim ;;
export)
  rm -rf anim_v25/export
  R $A -P exportar_clipes_v25.py -- anim_v25/export anim_v25/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v25.py -- anim_v25/export anim_v25/export/ref anim_v25/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200
  "$B" -b --factory-startup -P auditar_sequencia_v25.py -- $D/aud_seq_v25_reimport.json LOW,LOD1,LOD2 --glb anim_v25/export anim_v25 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v25.json "$B" -b --factory-startup -P apoios_reimport_v24.py -- anim_v25/export anim_v25 $D/diag_apoios_v25_antigas.json $D/apoios_reimport_v25_antigas.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_transicoes_v25.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V25_${P_}_FIM
