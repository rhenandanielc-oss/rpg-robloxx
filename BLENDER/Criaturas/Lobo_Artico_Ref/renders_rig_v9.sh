#!/bin/sh
# Renders de evidencia do rig piloto v9 (todos com o rig real; o v8 so para comparar o repouso). Rodar nesta pasta.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; R=rig_v9/CR_LoboArtico_Rig.blend; D=review/v9_rig
V() { "$B" -b "$@" 2>&1 | grep "VISTAS_RIG_OK\|Error\|Traceback"; }
CORPO=frente,lado_E,lado_D,tras,34_E,34_D,34_tras
CLOSE=canto_E,canto_D,boca_34,boca_baixo,olhos,olho_E,olho_D,costura_E,costura_D,costura_baixo
# 1) repouso: v8 (sem rig) x rig no quadro 0
for L in LOW LOD1 LOD2; do
  V low_v8/CR_LoboArtico_LOW.blend -P vistas_rig_v9.py -- $D/repouso $L 0 $CORPO,$CLOSE pre=v8_$L
  V $R -P vistas_rig_v9.py -- $D/repouso $L 0 $CORPO,$CLOSE pre=rig_$L
done
# 2) poses-pico de cada trecho (corpo inteiro)
PICOS=0,25,43,72,99,119,149,169,201,221,251,269,295,313,339,355,378,392,410,438,452,470,498,512,530,558,572,590,621,639,665,678,699,712,732,750,782
V $R -P vistas_rig_v9.py -- $D/poses LOW $PICOS 34_E,lado_E,frente res=640x480
V $R -P vistas_rig_v9.py -- $D/poses LOD1 $PICOS 34_E res=640x480
V $R -P vistas_rig_v9.py -- $D/poses LOD2 $PICOS 34_E res=640x480
V $R -P vistas_rig_v9.py -- $D/poses LOW 0,201,251,295,339,410,470,530,590 patas,34_tras res=640x480
# 3) closes do rosto e da costura, 3 LODs
for L in LOW LOD1 LOD2; do
  V $R -P vistas_rig_v9.py -- $D/closes $L 0,25,43,782 canto_E,canto_D,boca_34,boca_baixo
  V $R -P vistas_rig_v9.py -- $D/closes $L 0,64,72 olhos,olho_E,olho_D
  V $R -P vistas_rig_v9.py -- $D/closes $L 0,99,119,149,169,782 costura_E,costura_D,costura_baixo
done
V $R -P vistas_rig_v9.py -- $D/closes LOW 0,43,782 canto_E,canto_D arame pre=arame_LOW
# 4) esqueleto REIMPORTADO do GLB (acao tocada pelo armature importado)
for L in LOW LOD1 LOD2; do
  V rig_v9/export/reimport_$L.blend -P vistas_rig_v9.py -- $D/reimport $L 0,43,72,99,169,201,295,410,530,621,699,782 34_E res=640x480 pre=reimp_$L
done
# 5) video: todos os quadros, 3/4 esquerdo, LOD0
V $R -P vistas_rig_v9.py -- $D/video LOW 0-806 34_E res=640x480
echo RENDERS_V9_FIM
