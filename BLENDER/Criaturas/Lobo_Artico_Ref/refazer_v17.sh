#!/bin/sh
# v17: refaz o corte cauda x coxa E (lobo da cauda do lado certo) a partir do rig v9 e TODA a cascata ate os clipes
# exportados. Nada anterior e alterado (rig_v9..v11, anim_v12..v16 so sao lidos). Rodar nesta pasta.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=review/v17_corte; mkdir -p $D
r() { "$B" "$@" 2>&1 | grep "_OK\|Error\|Traceback\|AssertionError" | cut -c1-300; }
rm -rf rig_v17 rig_v17_garganta anim_v17_clipes anim_v17_tampas anim_v17_pesos anim_v17
r -b anim_v14/CR_LoboArtico_Anim.blend -P exportar_lobo_v17.py -- corte_v17/lobo_pontos.json      # pontos do lobo (diagnostico 8.18)
r -b rig_v9/CR_LoboArtico_Rig.blend -P separar_cauda_v17.py -- rig_v17                           # 1. corte novo
r -b rig_v17/CR_LoboArtico_Rig.blend -P textura_cauda_v10.py                                    #    textura da regiao (v10)
r -b rig_v17/CR_LoboArtico_Rig.blend -P acao_v10.py                                             #    acao de teste (v10)
r -b rig_v17/CR_LoboArtico_Rig.blend -P auditar_cauda_v10.py -- $D/aud_cauda_v17.json
r -b rig_v17/CR_LoboArtico_Rig.blend -P garganta_v11.py -- rig_v17_garganta                     # 2. garganta (v11)
r -b rig_v17_garganta/CR_LoboArtico_Rig.blend -P clipes_v12.py -- anim_v17_clipes               # 3. clipes Repouso/Andar (v12)
r -b anim_v17_clipes/CR_LoboArtico_Anim.blend -P textura_borda_v13.py -- anim_v17_tampas        # 4. v13: borda, lascas,
r -b anim_v17_tampas/CR_LoboArtico_Anim.blend -P lascas_v13.py                                  #    enrolamento e UV propria
r -b anim_v17_tampas/CR_LoboArtico_Anim.blend -P normais_tampa_v13.py                           #    das tampas
r -b anim_v17_tampas/CR_LoboArtico_Anim.blend -P uv_tampa_v13.py
r -b anim_v17_tampas/CR_LoboArtico_Anim.blend -P pesos_cauda_v14.py -- anim_v17_pesos           # 5. pesos cauda x perna (v14)
r -b anim_v17_pesos/CR_LoboArtico_Anim.blend -P pelo_fresta_v15.py -- anim_v17                  # 6. cartoes na fresta (v15)
r -b anim_v17/CR_LoboArtico_Anim.blend -P auditar_clipes_v12.py -- $D/aud_clipes_v17.json        # 7. auditoria, export, reimport
r -b anim_v17/CR_LoboArtico_Anim.blend -P exportar_clipes_v12.py -- anim_v17/export anim_v17/export/ref
r -b --factory-startup -P reimportar_clipes_v12.py -- anim_v17/export anim_v17/export/ref anim_v17/rig_v11.json
r -b anim_v17/CR_LoboArtico_Anim.blend -P medir_pelo_cauda_v14.py -- $D/pelo_cauda_v17.json
echo REFAZER_V17_FIM
