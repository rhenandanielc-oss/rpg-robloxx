#!/bin/sh
# Renders de evidencia do lote 1 (Repouso, Andar) com o rig real. Rodar nesta pasta.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; A=anim_v12/CR_LoboArtico_Anim.blend; D=review/v12_clipes
R() { "$B" -b "$@" 2>&1 | grep "_OK\|Error\|Traceback"; }
# repouso: v11 (rig sem clipe) x quadro 0 do Repouso, mesmas cameras
R rig_v11/CR_LoboArtico_Rig.blend -P vistas_rig_v9.py -- $D/repouso LOW 0 frente,lado_E,lado_D,tras,34_E pre=v11
R $A -P vistas_rig_v9.py -- $D/repouso LOW 0 frente,lado_E,lado_D,tras,34_E acao=Repouso pre=v12_Repouso
# Andar: 3 ciclos com deslocamento (apresentacao) e 1 ciclo no lugar, cinco vistas de corpo inteiro
R $A -P vistas_clipes_v12.py -- $D/andar LOW Andar 0-107 perfil_E,perfil_D,frente,tras,34_E desloc
R $A -P vistas_clipes_v12.py -- $D/andar LOW Andar 0-35 34_E,perfil_E pre=LOW_Andar_nolugar
R $A -P vistas_clipes_v12.py -- $D/andar LOW Andar 0-71 patas_E,patas_D,cauda_E desloc
R $A -P vistas_clipes_v12.py -- $D/andar LOW Andar 0-35 garganta
R $A -P vistas_clipes_v12.py -- $D/andar LOW Andar 0-35 patas_E,cauda_E desloc sempelo pre=LOW_Andar_desloc_sempelo
# Repouso: ciclo inteiro (8 s)
R $A -P vistas_clipes_v12.py -- $D/repouso_clipe LOW Repouso 0-240 perfil_E,34_E,frente
R $A -P vistas_clipes_v12.py -- $D/repouso_clipe LOW Repouso 0-240:4 garganta,cauda_E
# LOD1 / LOD2
for L in LOD1 LOD2; do
  R $A -P vistas_clipes_v12.py -- $D/lods $L Andar 0-71 perfil_E,34_E desloc
  R $A -P vistas_clipes_v12.py -- $D/lods $L Repouso 0-240:2 34_E
done
# transicao tecnica (nao exportada)
R $A -P vistas_clipes_v12.py -- $D/transicao LOW Teste_Transicao 0-264 perfil_E,34_E desloc
echo RENDERS_CLIPES_V12_FIM
