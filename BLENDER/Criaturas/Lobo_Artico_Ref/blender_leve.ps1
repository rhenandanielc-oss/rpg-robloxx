# Roda o Blender sem disputar o PC com o usuario (Opera/Roblox abertos): prioridade Idle, 2 threads de CPU, janela oculta.
# Uso (PowerShell): powershell -NoProfile -File blender_leve.ps1 <arquivo.blend> <script.py> [args do script...]
# Renders de revisao: usar Cycles na CPU (variavel BLENDER_LEVE=1 lida pelos scripts) para nao usar a placa de video,
# que o Roblox Studio e o Opera estao usando.
param([Parameter(Mandatory=$true)][string]$Blend, [Parameter(Mandatory=$true)][string]$Script, [Parameter(ValueFromRemainingArguments=$true)][string[]]$Resto)
$env:BLENDER_LEVE = "1"
$args2 = @("-b", $Blend, "-t", "2", "-P", $Script, "--") + $Resto
$p = Start-Process "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -ArgumentList $args2 -WindowStyle Hidden -PassThru -RedirectStandardOutput "$env:TEMP\blender_leve_out.txt"
try { $p.PriorityClass = "Idle" } catch {}
$p.WaitForExit()
Get-Content "$env:TEMP\blender_leve_out.txt" | Select-String -Pattern "OK|EXPORT|Error|Traceback|QA_" | ForEach-Object { $_.Line }
