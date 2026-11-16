#!/bin/sh
# v34: roda as partes do renders_v34.sh em dois lotes de 4 processos (log por parte em review/v34_convergir/log_<parte>.txt)
D=review/v34_convergir
lote() { for p in "$@"; do sh renders_v34.sh $p > $D/log_$p.txt 2>&1 & done; wait; }
lote auditorias seq_a seq_b seq_c
lote seq_d seq_lods export
echo LOTE_V34_FIM
