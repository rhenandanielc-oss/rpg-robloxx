#!/bin/sh
# v37: partes do renders_v37.sh em dois lotes pequenos (log por parte em review/v37_sentado/log_<parte>.txt)
D=review/v37_sentado
lote() { for p in "$@"; do sh renders_v37.sh $p > $D/log_$p.txt 2>&1 & done; wait; }
lote auditorias vid_a vid_b
lote vid_c export
sh renders_v37.sh montar > $D/log_montar.txt 2>&1
echo LOTE_V37_FIM
