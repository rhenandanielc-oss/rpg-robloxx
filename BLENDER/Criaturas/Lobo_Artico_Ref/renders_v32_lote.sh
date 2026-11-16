#!/bin/sh
# v32: roda as partes do renders_v32.sh em dois lotes de 4 processos (log por parte em review/v32_postura/log_<parte>.txt)
D=review/v32_postura
lote() { for p in "$@"; do sh renders_v32.sh $p > $D/log_$p.txt 2>&1 & done; wait; }
lote auditorias seq_a seq_b seq_c
lote seq_d seq_lods export
echo LOTE_V32_FIM
