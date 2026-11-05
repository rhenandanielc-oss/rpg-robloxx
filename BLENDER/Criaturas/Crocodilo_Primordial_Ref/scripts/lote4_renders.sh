#!/bin/bash
# Lote 4 (montaria, so apresentacao): renders e medicoes em review/L4/ a partir de CR_Crocodilo_Montaria_Teste.blend
# (gerada por demo_montaria.py depois de anim_crocodilo.py). Manequim = R15 APROXIMADO, sela = PROPOSTA.
cd "$(dirname "$0")/.."
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=$(pwd -W); O="$D/review/L4"; T=CR_Crocodilo_Montaria_Teste.blend
R() { "$B" -b $T -P scripts/render_montaria.py -- "$@"; }
# 1. encaixe (Repouso q0): com sela PROPOSTA e sem sela (cavaleiro direto nas cristas)
"$B" -b CR_Crocodilo_Anim.blend -P scripts/encaixe_l4.py -- "$O/encaixe" 0.65 | grep -E "CRISTAS|ENCAIXE"
"$B" -b CR_Crocodilo_Anim.blend -P scripts/encaixe_l4.py -- "$O/encaixe" 0.5 sem_sela | grep -E "ENCAIXE"
# 2. Montar / Desmontar (todas as quadros) e continuidade Repouso -> Montar -> montado -> Desmontar -> Repouso
R "$O/demo" demo Montar,Desmontar lado,34,frente,topo,subida,flanco 1 | grep RENDER
R "$O/seq" seq - lado,34,subida 2 | grep RENDER
# 3. reutilizacao com o cavaleiro sentado: 1 ciclo renderizado (GIF repete 3), medicao em 3 ciclos
R "$O/reuso" reuso Repouso,Andar,Corrida,VirarEsquerda,VirarDireita lado,34,close 1 | grep RENDER
R "$O/reuso" reuso VirarEsquerda,VirarDireita topo 1 | grep RENDER
R "$O/reuso" reuso Corrida frente 1 | grep RENDER
R "$O/reuso" reuso NadoParado,Nado,CurvaAquaticaEsquerda,CurvaAquaticaDireita lado_agua,34,close 1 | grep RENDER
R "$O/reuso" reuso CurvaAquaticaEsquerda,CurvaAquaticaDireita topo 1 | grep RENDER
R "$O/qa3" reuso Repouso,Andar,Corrida,VirarEsquerda,VirarDireita,NadoParado,Nado,CurvaAquaticaEsquerda,CurvaAquaticaDireita - 1 3 sem_render | grep RENDER
# 4. terra <-> agua superficial com cavaleiro (cena de margem de teste; sem Mergulho/Emersao montado)
for q in entrada saida; do "$B" -b $T -P scripts/cena_agua.py -- "$O/agua" $q 2 lado,34 cavaleiro | grep -E "PENETRACAO|CAVALEIRO|ROTEIRO"; done
echo LOTE4_RENDER_OK
