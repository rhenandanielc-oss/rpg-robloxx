#!/bin/sh
# Renders de evidencia da v10 (separacao cauda x pata traseira E), sempre com o rig real e a MESMA acao (acao_v10) na v9
# (copia em review/v10_cauda/v9_base; rig_v9/ intacto) e na v10. Rodar nesta pasta.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=review/v10_cauda
V9=$D/v9_base/CR_LoboArtico_Rig.blend; V10=rig_v10/CR_LoboArtico_Rig.blend
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback"; }
Q=0,295,498,512,530,558,572,590,621,639,665,678,825,845,871
VC=lado_E_cauda,lado_D_cauda,tras_cauda,34_tras_E,interno_E,interno_D,baixo_cauda
VERS=${VERSOES:-v9 v10}                                                # VERSOES="v10" refaz so a v10
for T0 in $VERS; do
  [ $T0 = v9 ] && N=v9:$V9 || N=v10:$V10
  T=${N%%:*}; F=${N#*:}
  for L in LOW LOD1 LOD2; do R "$F" -P vistas_rig_v9.py -- $D/repouso $L 0 frente,lado_E,lado_D,tras,34_E,34_D,34_tras pre=${T}_$L; done
  R "$F" -P vistas_cauda_v10.py -- $D/$T LOW textura $Q $VC
  R "$F" -P vistas_cauda_v10.py -- $D/$T LOW textura $Q $VC sempelo
  R "$F" -P vistas_cauda_v10.py -- $D/$T LOW pesos 0,512,530,665,825 lado_E_cauda,interno_E,34_tras_E
  R "$F" -P vistas_cauda_v10.py -- $D/$T LOW classe 0 lado_E_cauda,interno_E,34_tras_E,tras_cauda
  for L in LOD1 LOD2; do
    R "$F" -P vistas_cauda_v10.py -- $D/$T $L textura 0,512,530,665,825 lado_E_cauda,34_tras_E,interno_E
    R "$F" -P vistas_cauda_v10.py -- $D/$T $L textura 0,512,530,665,825 lado_E_cauda,34_tras_E,interno_E sempelo
    R "$F" -P vistas_cauda_v10.py -- $D/$T $L pesos 0,530,665 lado_E_cauda,interno_E
  done
done
R $V10 -P vistas_cauda_v10.py -- $D/v10 LOW tampa 0,512,530,665,825 lado_E_cauda,34_tras_E,interno_E,tras_cauda
# video: trechos traseira E/D, cauda e combinacoes (quadros 486-890), 3/4 de tras do lado E, LOD0 com pelo
QV=$(seq -s, 486 1 890)
case "$VERS" in *v9*) R $V9 -P vistas_cauda_v10.py -- $D/video_v9 LOW textura $QV 34_tras_E;; esac
R $V10 -P vistas_cauda_v10.py -- $D/video_v10 LOW textura $QV 34_tras_E
echo RENDERS_CAUDA_V10_FIM
