#!/bin/sh
# Refaz a v11 (garganta/juba) a partir da v10 (rig_v10/ so e lido). Rodar nesta pasta. $1 = pasta da referencia de deformacao.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; REF=${1:-review/v11_garganta/_ref}; D=review/v11_garganta
rm -rf rig_v11
"$B" -b rig_v10/CR_LoboArtico_Rig.blend -P garganta_v11.py -- rig_v11 2>&1 | grep "V11_OK\|Error\|Traceback"
"$B" -b rig_v10/CR_LoboArtico_Rig.blend -P diag_garganta_v11.py -- $D/diag_v10.json 2>&1 | grep "DIAG_GARGANTA_OK\|Traceback"
"$B" -b rig_v11/CR_LoboArtico_Rig.blend -P diag_garganta_v11.py -- $D/diag_v11.json 2>&1 | grep "DIAG_GARGANTA_OK\|Traceback"
"$B" -b rig_v11/CR_LoboArtico_Rig.blend -P auditar_rig_v9.py -- $D/global 2>&1 | grep "AUD_RIG_OK\|Traceback"
python resumo_rig_v9.py $D/global > /dev/null
"$B" -b rig_v11/CR_LoboArtico_Rig.blend -P auditar_cauda_v10.py -- $D/aud_cauda_v11.json 2>&1 | grep "AUD_CAUDA_OK\|Traceback"
"$B" -b rig_v11/CR_LoboArtico_Rig.blend -P exportar_rig_v9.py -- rig_v11/export "$REF" 2>&1 | grep "EXPORT_RIG_OK\|Traceback"
"$B" -b --factory-startup -P reimportar_rig_v9.py -- rig_v11/export "$REF" rig_v11/rig_v11.json 2>&1 | grep "REIMPORT_RIG_OK\|Traceback"
echo REFAZER_V11_FIM
