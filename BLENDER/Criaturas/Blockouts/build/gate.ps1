# Gate de silhueta + renders de uma especie (OPERACAO CREATURE BLOCKOUT).
# 1) pose da referencia -> world_gate contra o matte oficial; 2) pose neutra -> arquivo de trabalho + clay frente/lateral/3/4.
param(
    [Parameter(Mandatory)] [string]$Especie,
    [string]$Matte = "",          # vazio = sem gate (especie sem silhueta oficial)
    [double]$Az = 270, [double]$S = 0.05, [double]$AxisCol = 0, [double]$GroundRow = 0,
    [switch]$SoGate,
    [string]$Sufixo = "blockout"
)
$R = Split-Path $PSScriptRoot
$B = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$K = "C:\Users\Rhenan\.claude\skills\blender-image-to-3d\scripts"
$build = "$R\build\build_$Especie.py"
$rev = "$R\review\$Especie"
New-Item -ItemType Directory -Force $rev | Out-Null
if ($Matte) {
    & $B --background --factory-startup --python $build -- --pose referencia --out "$rev\_gate.blend" 2>&1 | Select-String "Error|Traceback|line \d" | Select-Object -First 6
    & $B --background --factory-startup --python "$K\world_gate.py" -- --blend "$rev\_gate.blend" --out "$rev\gate" --matte $Matte --az $Az --m-per-px $S --axis-col $AxisCol --ground-row $GroundRow --collections $Especie 2>&1 | Select-String "IoU"
}
if ($SoGate) { return }
& $B --background --factory-startup --python $build -- --pose neutra --out "$R\$Especie\${Especie}_$Sufixo.blend" 2>&1 | Select-String "MEDIDAS|Error|Traceback|line \d" | Select-Object -First 6
& $B --background --factory-startup --python "$K\review_render.py" -- --blend "$R\$Especie\${Especie}_$Sufixo.blend" --out "$rev\clay" --collections "$Especie,REF" --views front,side,threequarter --mode clay --res 900 --gameplay-px 128 2>&1 | Select-String "^rendered" | Measure-Object | ForEach-Object { "renders: " + $_.Count }
python "$R\build\folha.py" $Especie

