#!/bin/sh
# lotes de render da revisao v43 r4c (um processo do Blender por vez; PC compartilhado)
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; F=anim_v43r4/CR_LoboArtico_Anim.blend; R=render_ataque_r4.py; O=review/v43r4
Q=0,3,4,5,6,7,9,12
"$B" -b $F -P $R -- $O/comp quadros R3_GarraE,GarraE,R3_GarraD,GarraD Andar:6 perfil_E,pata $Q 2>&1 | grep -E "OK|Error"
"$B" -b $F -P $R -- $O/bases quadros Mordida1,Mordida2,GarraE,GarraD Repouso:0,Andar:0,Andar:18,Trote:9 perfil_E 0,4,6,7,10 2>&1 | grep -E "OK|Error"
"$B" -b $F -P $R -- $O/bases quadros Mordida1_Corrida,Mordida2_Corrida,GarraE_Corrida,GarraD_Corrida Corrida:7 perfil_E 0,4,6,7,10 2>&1 | grep -E "OK|Error"
"$B" -b $F -P $R -- $O/seq seq R3_Mordida1,R3_GarraE,R3_Mordida2,R3_GarraD Andar:0 perfil_E,cabeca r3_andar 2>&1 | grep -E "OK|Error"
"$B" -b $F -P $R -- $O/seq seq Mordida1,GarraE,Mordida2,GarraD Andar:0 perfil_E,cabeca r4_andar 2>&1 | grep -E "OK|Error"
"$B" -b $F -P $R -- $O/seq seq Mordida1_Corrida,GarraE_Corrida,Mordida2_Corrida,GarraD_Corrida Corrida:0 perfil_E,pata r4_corrida 2>&1 | grep -E "OK|Error"
"$B" -b $F -P $R -- $O/seq seq Mordida1,GarraE,Mordida2,GarraD Trote:0 perfil_E r4_trote 2>&1 | grep -E "OK|Error"
echo "LOTES_FIM comp=$(ls $O/comp | wc -l) bases=$(ls $O/bases | wc -l) seq=$(ls $O/seq | wc -l)"
