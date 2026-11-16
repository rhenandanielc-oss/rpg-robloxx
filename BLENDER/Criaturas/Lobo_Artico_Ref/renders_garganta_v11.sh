#!/bin/sh
# Renders de evidencia da v11 (garganta/juba), rig real, mesma acao (acao_v10) e cameras na v10 e na v11. Rodar nesta pasta.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=review/v11_garganta
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback"; }
Q=0,99,119,149,169,782,251,295,378,438
VG=garganta_frente,garganta_E,garganta_D,garganta_baixo,garganta_34,garganta_34_D,geral_jogo
for T in ${VERSOES:-v10 v11}; do
  F=rig_$T/CR_LoboArtico_Rig.blend
  for L in LOW LOD1 LOD2; do R "$F" -P vistas_rig_v9.py -- $D/repouso $L 0 frente,lado_E,lado_D,34_E,34_D pre=${T}_$L; done
  R "$F" -P vistas_cauda_v10.py -- $D/$T LOW textura $Q $VG
  R "$F" -P vistas_cauda_v10.py -- $D/$T LOW textura $Q $VG sempelo
  R "$F" -P vistas_cauda_v10.py -- $D/$T LOW pescoco 0,169,782,378 garganta_frente,garganta_E,garganta_baixo,garganta_34
  for L in LOD1 LOD2; do
    R "$F" -P vistas_cauda_v10.py -- $D/$T $L textura 0,99,169,782 garganta_E,garganta_34,garganta_baixo,geral_jogo
    R "$F" -P vistas_cauda_v10.py -- $D/$T $L textura 0,169,782 garganta_E,garganta_34 sempelo
    R "$F" -P vistas_cauda_v10.py -- $D/$T $L pescoco 0,169,782 garganta_E,garganta_34
  done
  # video: cabeca (82-184, ida e volta continua), combinacao (758-806) e ombro dianteiro E (366-426), 3/4 da garganta, LOD0
  QV=$(seq -s, 82 1 184),$(seq -s, 366 1 426),$(seq -s, 758 1 806)
  R "$F" -P vistas_cauda_v10.py -- $D/video_$T LOW textura $QV garganta_34
done
echo RENDERS_GARGANTA_V11_FIM
