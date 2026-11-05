#!/bin/bash
# Evidencias do Lote 2 (mesma geracao dos JSON): renders, folhas e GIFs
cd "$(dirname "$0")/.."
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=$(pwd -W); O="$D/review/L2/clipes"
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" VirarEsquerda,VirarDireita topo,patas 2
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Arrancada,Frenagem lado,patas 2
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" RepousoParaAndar,AndarParaRepouso,AndarParaCorrida,CorridaParaAndar patas 2
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" NadoParado,CurvaAquaticaEsquerda,CurvaAquaticaDireita topo 3
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" NadoParado,Mergulho,Emersao lado 2
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" EntradaAgua,SaidaAgua lado,patas 2
for x in "VirarEsquerda topo 67" "VirarEsquerda patas 67" "VirarDireita topo 67" "VirarDireita patas 67" "NadoParado topo 100" "CurvaAquaticaEsquerda topo 100" "CurvaAquaticaDireita topo 100" "NadoParado lado 67"; do set -- $x; python scripts/folha_gif.py review/L2/clipes $1 $2 $3 3; done
for x in "Arrancada lado 67" "Arrancada patas 67" "Frenagem lado 67" "Frenagem patas 67" "RepousoParaAndar patas 67" "AndarParaRepouso patas 67" "AndarParaCorrida patas 67" "CorridaParaAndar patas 67" "Mergulho lado 67" "Emersao lado 67" "EntradaAgua lado 67" "EntradaAgua patas 67" "SaidaAgua lado 67" "SaidaAgua patas 67"; do set -- $x; python scripts/folha_gif.py review/L2/clipes $1 $2 $3 1 lento; done
echo LOTE2_RENDERS_OK
