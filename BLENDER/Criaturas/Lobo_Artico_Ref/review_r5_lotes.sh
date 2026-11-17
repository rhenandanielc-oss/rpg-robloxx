#!/bin/sh
# lotes de render da revisao das garras v43 r5 (um processo do Blender por vez; PC compartilhado; Eevee 8 amostras)
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; F=anim_v43r5/CR_LoboArtico_Anim.blend; R=render_garra_r5.py; O=review/v43r5
"$B" -b $F -P $R -- $O/comp quadros R4_GarraE@Andar:3,GarraE_Andar@Andar:32,R4_GarraD@Andar:21,GarraD_Andar@Andar:14 perfil_E,pata,frente_pata 0,3,5,7,9,11,13,15 alvo 2>&1 | grep -E "OK|Error"
"$B" -b $F -P $R -- $O/bases quadros GarraE@Repouso:0,GarraE_Andar@Andar:32,GarraE_Trote@Trote:8,GarraE_Corrida@Corrida:10,GarraD@Repouso:0,GarraD_Andar@Andar:14,GarraD_Trote@Trote:17,GarraD_Corrida@Corrida:9 perfil_E,pata 0,3,7,10,13,15 alvo 2>&1 | grep -E "OK|Error"
for par in "R4_GarraE@Repouso:0 r4_E_Repouso perfil_E" "GarraE@Repouso:0 r5_E_Repouso perfil_E,pata" "R4_GarraE@Andar:3 r4_E_Andar perfil_E" "GarraE_Andar@Andar:32 r5_E_Andar perfil_E,pata" \
           "R4_GarraE@Trote:12 r4_E_Trote perfil_E" "GarraE_Trote@Trote:8 r5_E_Trote perfil_E,pata" "R4_GarraE_Corrida@Corrida:1 r4_E_Corrida perfil_E" "GarraE_Corrida@Corrida:10 r5_E_Corrida perfil_E,pata" \
           "R4_GarraD@Repouso:0 r4_D_Repouso perfil_E" "GarraD@Repouso:0 r5_D_Repouso perfil_E,pata" "R4_GarraD@Andar:21 r4_D_Andar perfil_E" "GarraD_Andar@Andar:14 r5_D_Andar perfil_E,pata" \
           "R4_GarraD@Trote:13 r4_D_Trote perfil_E" "GarraD_Trote@Trote:17 r5_D_Trote perfil_E,pata" "R4_GarraD_Corrida@Corrida:13 r4_D_Corrida perfil_E" "GarraD_Corrida@Corrida:9 r5_D_Corrida perfil_E,pata"; do
  set -- $par
  "$B" -b $F -P $R -- $O/seq seq $1 $3 $2 alvo 2>&1 | grep -E "Error"
done
echo "LOTES_R5_FIM comp=$(ls $O/comp | wc -l) bases=$(ls $O/bases | wc -l) seq=$(ls $O/seq | wc -l)"
