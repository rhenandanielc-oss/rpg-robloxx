# = blender_leve.ps1, ainda mais leve (pedido do usuario 20/11: "mesmo que demore, nao quero o pc lagando"):
# prioridade Idle, 1 thread (-t 1), afinidade em 1 nucleo (o ultimo), janela oculta. Saida completa em $env:TEMP\blender_levissimo_out.txt
param([Parameter(Mandatory=$true)][string]$Blend, [Parameter(Mandatory=$true)][string]$Script, [Parameter(ValueFromRemainingArguments=$true)][string[]]$Resto)
$env:BLENDER_LEVE = "1"
$args2 = @("-b", $Blend, "-t", "1", "-P", $Script, "--") + $Resto
$out = "$env:TEMP\blender_levissimo_out.txt"
$p = Start-Process "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -ArgumentList $args2 -WindowStyle Hidden -PassThru -RedirectStandardOutput $out -RedirectStandardError "$out.err"
try { $p.PriorityClass = "Idle" } catch {}
try { $n = [Environment]::ProcessorCount; $p.ProcessorAffinity = [IntPtr](1 -shl ($n - 1)) } catch {}
$p.WaitForExit()
Get-Content $out, "$out.err" | Select-String -Pattern "OK|DIAG|V46|AUD|Error|Traceback|QA_" | ForEach-Object { $_.Line }
