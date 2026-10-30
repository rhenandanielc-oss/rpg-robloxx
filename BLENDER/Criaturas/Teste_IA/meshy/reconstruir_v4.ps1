# Reconstroi o Silverwing do zero (v4): malha soldada antes da reducao -> encaixe -> pesos com pontes RASGADAS (sem
# apagar faces) -> mao da asa -> dobra propria -> animacoes proprias -> correcoes de pesos guiadas pelas animacoes.
# Uso: powershell -File reconstruir_v4.ps1   (rodar dentro da pasta meshy)
$ErrorActionPreference = "Stop"
$p = $PSScriptRoot; $b = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"; $blend = "$p\saida_v4\Silverwing_M2M.blend"
function etapa($nome, $args_) { Write-Output "=== $nome"; & $b @args_ 2>&1 | Select-String -Pattern "PESOS_ASA|PONTES|ERRO_|ASSAR_OK|INFLU|DOBRA_OK|CLIPE|ANIM_OK|PASSADA|PEN_OK|CRUZ_OK|POLIR_OK|INICIO|Traceback|Error" | ForEach-Object { $_.Line } }
etapa "montar" @("-b", "--factory-startup", "-P", "$p\montar_silverwing.py", "--", "$p\m2m_fonte\dragon-animations.glb", "$p\Silverwing_24k_v2.glb", "$p\encaixe\encaixe.json", "$p\saida_v4")
etapa "mao da asa" @("-b", $blend, "-P", "$p\assar_mao.py", "--", "$p\m2m_fonte\dragon-animations.glb")
etapa "limite 4 + camera" @("-b", $blend, "-P", "$p\revisar_silverwing.py", "--", "$p\saida_m2m\revisao", "1")
etapa "dobra propria" @("-b", $blend, "-P", "$p\dobra_asa.py", "--", "35", "35", "30", "35", "0.6", "-0.3", "0.3", "0.4")
etapa "animacoes" @("-b", $blend, "-P", "$p\anim_silverwing.py", "--", "todos")
etapa "polir pesos (corpo)" @("-b", $blend, "-P", "$p\polir_pesos.py", "--", "4", "corpo")
etapa "penetracao" @("-b", $blend, "-P", "$p\corrigir_penetracao.py")
etapa "cruzamentos" @("-b", $blend, "-P", "$p\corrigir_cruzamentos.py")
Write-Output "RECONSTRUIR_OK"

