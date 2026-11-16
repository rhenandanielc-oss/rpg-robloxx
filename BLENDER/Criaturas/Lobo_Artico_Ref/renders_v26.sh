#!/bin/sh
# v26 (L2b bloco 2: VirarEsquerda + VirarDireita): validacao e renders. $1 = parte: auditorias | seq_low | seq_lods | closes | repouso | export | montar.
# Rodar nesta pasta. Saida: review/v26_viradas/.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v26/CR_LoboArtico_Anim.blend; D=review/v26_viradas; P_="$1"
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-200; }
case "$P_" in
auditorias)
  R $A -P auditar_viradas_v26.py -- $D/aud_viradas_v26.json LOW,LOD1,LOD2
  R $A -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v26.json LOW,LOD1,LOD2
  R $A -P auditar_clipes_v21.py -- $D/aud_clipes_v26_antigas.json LOW,LOD1,LOD2 Andar,Trote,Corrida,Repouso
  R $A -P diag_apoios_v24.py -- $D/diag_apoios_v26_antigas.json
  R $A -P auditar_clipes_v21.py -- $D/aud_deform_viradas_v26.json LOW,LOD1,LOD2 VirarEsquerda,VirarDireita
  ACOES_MET=VirarEsquerda,VirarDireita R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_viradas_v26.json
  ACOES_MET=Andar R $A -P metricas_flanco_v23.py -- $D/metricas_flanco_andar_v26.json ;;
seq_low) for sq in ida_volta_E ida_volta_D; do R $A -P vistas_viradas_v26.py -- $D/quadros LOW $sq topo,perfil_E,perfil_D,frente,tras,34,patas_E,patas_D; done ;;
seq_lods) for L in LOD1 LOD2; do R $A -P vistas_viradas_v26.py -- $D/quadros $L ida_volta_E topo,perfil_D,patas_D; done ;;
closes)
  for ac in VirarEsquerda VirarDireita; do
    R $A -P vistas_closes_v21.py -- $D/closes $ac 0-92 fresta_E,garganta_E,flanco_D_baixo
    R $A -P vistas_closes_v21.py -- $D/closes $ac 0-92 fresta_E,garganta_E,flanco_D_baixo cores; done ;;
repouso)
  R anim_v25/CR_LoboArtico_Anim.blend -P diag_vistas_v23.py -- $D/repouso/v25 repouso 0-0 c_perfil_D,c_perfil_E,c_34_D,c_tras real
  R $A -P diag_vistas_v23.py -- $D/repouso/v26 repouso 0-0 c_perfil_D,c_perfil_E,c_34_D,c_tras real
  R $A -P diag_vistas_v23.py -- $D/repouso/v26_fim VirarEsquerda 92-92 c_perfil_D,c_perfil_E,c_34_D,c_tras real pre=real_LOW_VE_fim
  R $A -P diag_vistas_v23.py -- $D/repouso/v26_fim VirarDireita 92-92 c_perfil_D,c_perfil_E,c_34_D,c_tras real pre=real_LOW_VD_fim ;;
export)
  rm -rf anim_v26/export
  R $A -P exportar_clipes_v26.py -- anim_v26/export anim_v26/export/ref
  "$B" -b --factory-startup -P reimportar_clipes_v26.py -- anim_v26/export anim_v26/export/ref anim_v26/rig_v11.json 2>&1 | grep "_OK\|Error" | cut -c1-200
  "$B" -b --factory-startup -P auditar_viradas_v26.py -- $D/aud_viradas_v26_reimport.json LOW,LOD1,LOD2 --glb anim_v26/export anim_v26 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v26.json "$B" -b --factory-startup -P auditar_sequencia_v25.py -- $D/aud_seq_transicoes_v26_reimport.json LOW,LOD1,LOD2 --glb anim_v26/export anim_v26 2>&1 | grep "_OK\|Error" | cut -c1-200
  EXP_JSON=export_clipes_v26.json "$B" -b --factory-startup -P apoios_reimport_v24.py -- anim_v26/export anim_v26 $D/diag_apoios_v26_antigas.json $D/apoios_reimport_v26_antigas.json 2>&1 | grep "_OK\|Error" | cut -c1-200 ;;
montar)
  python prancha_viradas_v26.py
  for d in $D/revisao/video_*; do "$B" -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/$(basename $d | sed 's/video_//') $(cat $d/res.txt) 2>&1 | grep VIDEO_OK; done ;;
esac
echo RENDERS_V26_${P_}_FIM
