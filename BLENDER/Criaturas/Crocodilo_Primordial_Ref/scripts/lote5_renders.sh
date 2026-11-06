#!/bin/bash
# Lote 5 (sela definitiva + subida/descida pelos dois lados): renders e medicoes em review/L5/ a partir de
# CR_Crocodilo_Montaria_L5.blend (gerada por demo_montaria_l5.py) e CR_Crocodilo_Sela.blend (sela_crocodilo.py).
cd "$(dirname "$0")/.."
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=$(pwd -W); O="$D/review/L5"; T=CR_Crocodilo_Montaria_L5.blend
R() { "$B" -b $T -P scripts/render_montaria.py -- "$@"; }
R "$O/demo" demo Montar,Desmontar lado,34,subida,flanco,frente 1 | grep RENDER
R "$O/demo" demo MontarDireita,DesmontarDireita lado_d,34_d,subida_d,flanco_d,frente 1 | grep RENDER
R "$O/seq" seq - lado,34 2 | grep RENDER
R "$O/seq" seq_d - lado_d,34_d 2 | grep RENDER
R "$O/reuso" reuso Repouso,Andar,Corrida,VirarEsquerda,VirarDireita 34,close 1 | grep RENDER
R "$O/reuso" reuso NadoParado,Nado 34,close 1 | grep RENDER
R "$O/qa3" reuso Repouso,Andar,Corrida,VirarEsquerda,VirarDireita,NadoParado,Nado,CurvaAquaticaEsquerda,CurvaAquaticaDireita - 1 3 sem_render | grep RENDER
echo LOTE5_RENDER_OK
