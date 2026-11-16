#!/bin/sh
# v41: partes do renders_v41.sh em dois lotes pequenos (log por parte em review/v41_bloco4/log_<parte>.txt)
D=review/v41_bloco4
lote() { for p in "$@"; do sh renders_v41.sh $p > $D/log_$p.txt 2>&1 & done; wait; }
lote vid_a vid_b
lote vid_c export
sh renders_v41.sh montar > $D/log_montar.txt 2>&1
echo LOTE_V41_FIM
