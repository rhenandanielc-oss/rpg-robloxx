#!/bin/sh
# v36: partes do renders_v36.sh em dois lotes pequenos (log por parte em review/v36_descanso/log_<parte>.txt)
D=review/v36_descanso
lote() { for p in "$@"; do sh renders_v36.sh $p > $D/log_$p.txt 2>&1 & done; wait; }
lote auditorias vid_a vid_b
lote vid_c export
sh renders_v36.sh montar > $D/log_montar.txt 2>&1
echo LOTE_V36_FIM
