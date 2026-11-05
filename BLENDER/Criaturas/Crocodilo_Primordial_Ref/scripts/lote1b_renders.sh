#!/bin/bash
# Evidencias da correcao final do Lote 1 (versao L1b), todas da mesma geracao
cd "$(dirname "$0")/.."
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=$(pwd -W); O="$D/review/L1b/clipes"
"$B" -b CR_Crocodilo_Rig.blend -P scripts/render_boca_estados.py -- "$D/review/L1b/boca" L1b 12
"$B" -b versao_L1/CR_Crocodilo_Rig.blend -P scripts/render_boca_estados.py -- "$D/review/L1b/boca" L1 12
python scripts/grade_estados.py review/L1b/boca L1 review/L1b/boca/GRADE_L1_antes.png "ANTES (versao L1) - fechada 100% / meia / repouso / aberta +12"
python scripts/grade_estados.py review/L1b/boca L1b review/L1b/boca/GRADE_L1b_depois.png "DEPOIS (L1b) - fechada 100% / meia / repouso / aberta +12"
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Corrida lado,patas 1
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Mordida cabeca,34 1
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Ameaca cabeca,34 2
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Andar patas 2
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Nado lado,topo 3
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Repouso 34 4
for x in "Corrida lado 33" "Corrida patas 33"; do set -- $x; python scripts/folha_gif.py review/L1b/clipes $1 $2 $3 3 lento; done
for x in "Mordida cabeca 33" "Mordida 34 33" "Ameaca cabeca 67" "Ameaca 34 67"; do set -- $x; python scripts/folha_gif.py review/L1b/clipes $1 $2 $3 1 lento; done
for x in "Andar patas 67" "Nado lado 100" "Nado topo 100" "Repouso 34 133"; do set -- $x; python scripts/folha_gif.py review/L1b/clipes $1 $2 $3 3; done
echo LOTE1B_OK
