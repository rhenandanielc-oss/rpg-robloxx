#!/bin/sh
# Refaz a v10 inteira a partir do rig v9 (rig_v9/ so e lido). Rodar nesta pasta. $1 = pasta da referencia de deformacao.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; REF=${1:-review/v10_cauda/_ref}
rm -rf rig_v10
"$B" -b rig_v9/CR_LoboArtico_Rig.blend -P separar_cauda_v10.py -- rig_v10 2>&1 | grep "V10_OK\|Error\|Traceback"
"$B" -b rig_v10/CR_LoboArtico_Rig.blend -P textura_cauda_v10.py 2>&1 | grep "TEX_V10_OK\|Error\|Traceback"
"$B" -b rig_v10/CR_LoboArtico_Rig.blend -P acao_v10.py 2>&1 | grep "_OK\|Error\|Traceback"
"$B" -b rig_v10/CR_LoboArtico_Rig.blend -P diag_cauda_v10.py -- review/v10_cauda/diag_depois.json 2>&1 | grep "DIAG_CAUDA_OK\|fusao \['"
"$B" -b rig_v10/CR_LoboArtico_Rig.blend -P auditar_cauda_v10.py -- review/v10_cauda/aud_cauda_v10.json 2>&1 | grep "AUD_CAUDA_OK\|Traceback"
"$B" -b rig_v10/CR_LoboArtico_Rig.blend -P auditar_rig_v9.py -- review/v10_cauda/global 2>&1 | grep "AUD_RIG_OK\|Traceback"
python resumo_rig_v9.py review/v10_cauda/global > /dev/null
"$B" -b rig_v10/CR_LoboArtico_Rig.blend -P exportar_rig_v9.py -- rig_v10/export "$REF" 2>&1 | grep "EXPORT_RIG_OK\|Traceback"
"$B" -b --factory-startup -P reimportar_rig_v9.py -- rig_v10/export "$REF" rig_v10/rig_v10.json 2>&1 | grep "REIMPORT_RIG_OK\|Traceback"
echo REFAZER_V10_FIM
