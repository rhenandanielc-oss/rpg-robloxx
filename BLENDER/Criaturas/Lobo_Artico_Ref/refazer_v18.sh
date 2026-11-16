#!/bin/sh
# v18 = v17 + crista: o corte entra 1 anel a mais no vinco (LOW/LOD1), tirando a "mecha" fina que ficava do lado da perna.
# exportados. Nada anterior e alterado (rig_v9..v11, anim_v12..v16 so sao lidos). Rodar nesta pasta.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=review/v18_crista; mkdir -p $D
r() { "$B" "$@" 2>&1 | grep "_OK\|Error\|Traceback\|AssertionError" | cut -c1-300; }
rm -rf rig_v18 rig_v18_garganta anim_v18_clipes anim_v18_tampas anim_v18_pesos anim_v18
r -b rig_v9/CR_LoboArtico_Rig.blend -P separar_cauda_v18.py -- rig_v18                           # 1. corte novo
r -b rig_v18/CR_LoboArtico_Rig.blend -P textura_cauda_v10.py                                    #    textura da regiao (v10)
r -b rig_v18/CR_LoboArtico_Rig.blend -P acao_v10.py                                             #    acao de teste (v10)
r -b rig_v18/CR_LoboArtico_Rig.blend -P auditar_cauda_v10.py -- $D/aud_cauda_v18.json
r -b rig_v18/CR_LoboArtico_Rig.blend -P garganta_v11.py -- rig_v18_garganta                     # 2. garganta (v11)
r -b rig_v18_garganta/CR_LoboArtico_Rig.blend -P clipes_v12.py -- anim_v18_clipes               # 3. clipes Repouso/Andar (v12)
r -b anim_v18_clipes/CR_LoboArtico_Anim.blend -P textura_borda_v13.py -- anim_v18_tampas        # 4. v13: borda, lascas,
r -b anim_v18_tampas/CR_LoboArtico_Anim.blend -P lascas_v13.py                                  #    enrolamento e UV propria
r -b anim_v18_tampas/CR_LoboArtico_Anim.blend -P normais_tampa_v13.py                           #    das tampas
r -b anim_v18_tampas/CR_LoboArtico_Anim.blend -P uv_tampa_v13.py
r -b anim_v18_tampas/CR_LoboArtico_Anim.blend -P pesos_cauda_v14.py -- anim_v18_pesos           # 5. pesos cauda x perna (v14)
r -b anim_v18_pesos/CR_LoboArtico_Anim.blend -P pelo_fresta_v15.py -- anim_v18                  # 6. cartoes na fresta (v15)
r -b anim_v18/CR_LoboArtico_Anim.blend -P auditar_clipes_v12.py -- $D/aud_clipes_v18.json        # 7. auditoria, export, reimport
r -b anim_v18/CR_LoboArtico_Anim.blend -P exportar_clipes_v12.py -- anim_v18/export anim_v18/export/ref
r -b --factory-startup -P reimportar_clipes_v12.py -- anim_v18/export anim_v18/export/ref anim_v18/rig_v11.json
r -b anim_v18/CR_LoboArtico_Anim.blend -P medir_pelo_cauda_v14.py -- $D/pelo_cauda_v18.json
echo REFAZER_V18_FIM
