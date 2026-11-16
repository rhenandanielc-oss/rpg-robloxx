#!/bin/bash
# Refaz anim_v13/ (correcao das manchas da cauda E) a partir de anim_v12/ (preservado) e gera as evidencias.
# Uso (na pasta Lobo_Artico_Ref): bash refazer_v13.sh
set -e
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=review/v13_manchas
rm -rf anim_v13
"$B" -b anim_v12/CR_LoboArtico_Anim.blend -P textura_borda_v13.py -- anim_v13      # 1. repintura da faixa escura (efeito pequeno)
"$B" -b anim_v13/CR_LoboArtico_Anim.blend -P lascas_v13.py                         # 2. alisamento das lascas escondidas
"$B" -b anim_v13/CR_LoboArtico_Anim.blend -P normais_tampa_v13.py                  # 3. enrolamento e dobras da tampa
"$B" -b anim_v13/CR_LoboArtico_Anim.blend -P uv_tampa_v13.py                       # 4. CORRECAO: UV propria e limpa das tampas
"$B" -b anim_v13/CR_LoboArtico_Anim.blend -P exportar_clipes_v12.py -- anim_v13/export anim_v13/export/ref
"$B" -b --factory-startup -P reimportar_clipes_v12.py -- anim_v13/export anim_v13/export/ref anim_v13/rig_v11.json
"$B" -b anim_v13/CR_LoboArtico_Anim.blend -P auditar_clipes_v12.py -- $D/aud_clipes_v13.json
for V in v12:anim_v12 v13:anim_v13; do n=${V%%:*}; p=${V#*:}
  "$B" -b $p/CR_LoboArtico_Anim.blend -P vistas_clipes_v12.py -- $D/$n LOW Andar 0-35 cauda_E desloc
  "$B" -b $p/CR_LoboArtico_Anim.blend -P vistas_clipes_v12.py -- $D/$n LOW Andar 0-35 cauda_E desloc sempelo pre=LOW_Andar_desloc_sempelo
  for L in LOD1 LOD2; do "$B" -b $p/CR_LoboArtico_Anim.blend -P vistas_clipes_v12.py -- $D/$n $L Andar 0,3,30 cauda_E desloc; done
  "$B" -b $p/CR_LoboArtico_Anim.blend -P vistas_clipes_v12.py -- $D/$n LOW Repouso 0 perfil_E,perfil_D,tras,34_E,cauda_E
done
python prancha_manchas_v13.py $D
"$B" -b --factory-startup -P video_rig_v9.py -- $D/video_manchas $D/LoboArtico_manchas_antes_depois 1280 960
