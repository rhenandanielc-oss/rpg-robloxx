#!/bin/sh
# v40: partes do renders_v40.sh em dois lotes pequenos (log por parte em review/v40_bloco3/log_<parte>.txt)
D=review/v40_bloco3
lote() { for p in "$@"; do sh renders_v40.sh $p > $D/log_$p.txt 2>&1 & done; wait; }
lote vid_a vid_b
lote vid_c export
sh renders_v40.sh montar > $D/log_montar.txt 2>&1
echo LOTE_V40_FIM
