#!/bin/sh
# v38: partes do renders_v38.sh em dois lotes pequenos (log por parte em review/v38_cauda/log_<parte>.txt)
D=review/v38_cauda
lote() { for p in "$@"; do sh renders_v38.sh $p > $D/log_$p.txt 2>&1 & done; wait; }
lote auditorias vid_a vid_b
lote vid_c export
sh renders_v38.sh montar > $D/log_montar.txt 2>&1
echo LOTE_V38_FIM
