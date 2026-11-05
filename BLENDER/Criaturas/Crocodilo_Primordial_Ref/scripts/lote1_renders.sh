#!/bin/bash
# Renders do Lote 1 (todos os clipes, cameras por clipe) e folhas/GIFs
cd "$(dirname "$0")/.."
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=$(pwd -W); O="$D/review/L1_clipes"
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Repouso 34,cabeca 4
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Andar lado,patas,topo 2
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Corrida lado,patas 1
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Nado lado,topo 3
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Mordida 34,cabeca 1
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Ameaca 34,cabeca 2
for x in "Repouso 34 133" "Repouso cabeca 133" "Andar lado 67" "Andar patas 67" "Andar topo 67" "Corrida lado 33" "Corrida patas 33" "Nado lado 100" "Nado topo 100"; do set -- $x; python scripts/folha_gif.py review/L1_clipes $1 $2 $3 3; done
for x in "Mordida 34 33" "Mordida cabeca 33" "Ameaca 34 67" "Ameaca cabeca 67"; do set -- $x; python scripts/folha_gif.py review/L1_clipes $1 $2 $3 1 lento; done
echo LOTE1_RENDERS_OK
