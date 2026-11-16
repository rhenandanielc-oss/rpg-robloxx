#!/bin/sh
# v35: partes do renders_v35.sh em dois lotes pequenos (log por parte em review/v35_vida/log_<parte>.txt)
D=review/v35_vida
lote() { for p in "$@"; do sh renders_v35.sh $p > $D/log_$p.txt 2>&1 & done; wait; }
lote auditorias vid_a vid_b
lote vid_c export
sh renders_v35.sh montar > $D/log_montar.txt 2>&1
echo LOTE_V35_FIM
