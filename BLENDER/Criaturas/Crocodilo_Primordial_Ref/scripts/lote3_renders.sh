#!/bin/bash
# Lote 3 (reacoes e vida): gera os 29 clipes (mesma geracao), QA e evidencias em review/L3/
cd "$(dirname "$0")/.."
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=$(pwd -W); O="$D/review/L3/clipes"
N="ReacaoGolpe,Morte,Comer,Deitar,DescansoDeitado,Levantar,Observar,Alerta"
"$B" -b CR_Crocodilo_Rig.blend -P scripts/anim_crocodilo.py -- "$D/clipes" | grep -E "CLIPE|ANIM_OK" > review/L3/geracao_L3.txt
python scripts/qa_transicoes.py clipes clipes/emendas_transicoes.json > review/L3/qa_transicoes_L3.txt
python scripts/qa_clipes_json.py clipes export/CR_Crocodilo_Primordial.glb > review/L3/qa_json_L3.txt
"$B" -b CR_Crocodilo_Anim.blend -P scripts/qa_malha_chao.py -- "Repouso,Andar,$N" "$D/review/L3/qa_chao_L3.json" | grep CHAO > review/L3/qa_chao_L3.txt
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" "$N" lado,34 1
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" ReacaoGolpe,Comer,Observar,Alerta,Morte cabeca 1
"$B" -b CR_Crocodilo_Anim.blend -P scripts/render_clipes_v2.py -- "$O" Deitar,Levantar,DescansoDeitado patas 2
for c in ReacaoGolpe Morte Comer Deitar Levantar Observar Alerta; do for k in lado 34; do python scripts/folha_gif.py review/L3/clipes $c $k 33 1 lento; done; done
for c in ReacaoGolpe Comer Observar Alerta Morte; do python scripts/folha_gif.py review/L3/clipes $c cabeca 33 1 lento; done
for k in lado 34; do python scripts/folha_gif.py review/L3/clipes DescansoDeitado $k 33 3; done
for c in Deitar Levantar; do python scripts/folha_gif.py review/L3/clipes $c patas 66 1 lento; done
python scripts/folha_gif.py review/L3/clipes DescansoDeitado patas 66 3
echo LOTE3_OK
