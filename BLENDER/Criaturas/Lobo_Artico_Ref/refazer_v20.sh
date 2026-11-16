#!/bin/sh
# v20 = v18 (corte com crista; refazer_v18.sh) + sulco da coxa E rasado (a borda de tras da coxa parecia mecha solta).
# v19 (parede do vinco por peso) descartada. Rodar nesta pasta depois de refazer_v18.sh.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D=review/v20_sulco; mkdir -p $D/revisao
r() { "$B" "$@" 2>&1 | grep "_OK\|Error\|Traceback" | cut -c1-300; }
rm -rf anim_v20
r -b anim_v18/CR_LoboArtico_Anim.blend -P sulco_coxa_v20.py -- anim_v20
r -b anim_v20/CR_LoboArtico_Anim.blend -P auditar_clipes_v12.py -- $D/aud_clipes_v20.json
r -b anim_v20/CR_LoboArtico_Anim.blend -P exportar_clipes_v12.py -- anim_v20/export anim_v20/export/ref
r -b --factory-startup -P reimportar_clipes_v12.py -- anim_v20/export anim_v20/export/ref anim_v20/rig_v11.json
"$B" -b anim_v20/CR_LoboArtico_Anim.blend -P medir_pelo_cauda_v14.py -- $D/pelo_cauda_v20.json 2>&1 | grep "^PELO"
cp -r review/v18_crista/revisao/v18 $D/revisao/
for m in cores real; do r -b anim_v20/CR_LoboArtico_Anim.blend -P vistas_pelo_cauda_v14.py -- $D/revisao/v20 0-35 fresta_E,fresta_tras,fresta_baixo $( [ $m = cores ] && echo cores ); done
python video_pelo_cauda_v14.py $D/revisao v18 v20
for d in $D/revisao/video_v20_*; do r -b --factory-startup -P video_rig_v9.py -- $d $D/revisao/Pelo_cauda_$(basename $d | sed 's/video_//') 1928 760; done
for v in v18 v20; do r -b anim_$v/CR_LoboArtico_Anim.blend -P vistas_clipes_v12.py -- $D/repouso/$v LOW Repouso 0 perfil_E,perfil_D,tras,34_E,cauda_E; done
echo REFAZER_V20_FIM
