#!/bin/sh
# v29: roda as partes do renders_v29.sh em dois lotes de 4 processos (log por parte em review/v29_desacel/log_<parte>.txt)
D=review/v29_desacel
lote() { for p in "$@"; do sh renders_v29.sh $p > $D/log_$p.txt 2>&1 & done; wait; }
lote auditorias seq_a seq_b seq_c
lote seq_d seq_lods closes export
echo LOTE_V29_FIM
