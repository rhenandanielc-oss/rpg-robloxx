#!/bin/bash
# Evidencias das correcoes do Lote 2 (L2b): sequencias continuas na cena de teste e viradas em 3 ciclos
cd "$(dirname "$0")/.."
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=$(pwd -W)
for q in entrada saida terra; do "$B" -b CR_Crocodilo_Rig.blend -P scripts/cena_agua.py -- "$D/review/L2b/seq" $q 2 lado,34; done
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$D/review/L2b/virar" VirarDireita,VirarEsquerda topo,patas 1
"$B" -b versao_L2/CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$D/review/L2b/virar_antes" VirarDireita patas 1
for x in "VirarDireita topo" "VirarDireita patas" "VirarEsquerda topo" "VirarEsquerda patas"; do set -- $x; python scripts/folha_gif.py review/L2b/virar $1 $2 33 3 lento; done
python scripts/folha_gif.py review/L2b/virar_antes VirarDireita patas 33 3 lento
for q in entrada saida terra; do for c in lado 34; do python scripts/folha_gif.py review/L2b/seq $q $c 67 1 lento; done; done
echo LOTE2B_OK
