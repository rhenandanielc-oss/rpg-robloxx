# Cadeia completa do Silverwing Drake (pose neutra): montar (asa inteira) -> pesos novos no descanso -> mao -> limite 4
# -> dobra -> animacoes -> penetracao/cruzamentos -> QA -> faces (culling). Uso: powershell -File cadeia_drake.ps1
$p = $PSScriptRoot; $b = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"; $o = "$p\saida_drake2"; $bl = "$o\Silverwing_M2M.blend"
New-Item -ItemType Directory -Force $o | Out-Null
$pat = "PESOS_REPOSE|PONTES|ERRO_|MONTAR_OK|PESOS_NOVOS|REGIOES|MAX_INFL|REPESAR_OK|ASSAR_OK|INFLU|DOBRA_OK|APOIO|CLIPE|ANIM_OK|PASSADA|PEN_OK|CRUZ_OK|QA_OK|NORMAIS|DIAG_FACES|Traceback|Error"
function etapa($n, $a) { Write-Output "== $n"; & $b @a 2>&1 | Select-String -Pattern $pat | ForEach-Object { $_.Line } }
$env:ASA_INTEIRA = "1"; $env:CORPO_FIXO = "1"; $env:NECK_BASE = "0"; $env:PESC_VOO = "-40"; $env:SEM_PONTES = "1"; $env:RAIO_ASA = "0.045"; $env:PERNA_VOO_REL = "1"
etapa "montar" @("-b", "--factory-startup", "-P", "$p\montar_silverwing.py", "--", "$p\m2m_fonte\dragon-animations.glb", "$p\drake2\Drake2_lo.glb", "$p\drake2\encaixe.json", $o)
etapa "repesar" @("-b", $bl, "-P", "$p\repesar_silverwing.py")
etapa "mao" @("-b", $bl, "-P", "$p\assar_mao.py", "--", "$p\m2m_fonte\dragon-animations.glb")
etapa "limite4" @("-b", $bl, "-P", "$p\revisar_silverwing.py", "--", "$o\revisao", "1")
etapa "dobra" @("-b", $bl, "-P", "$p\dobra_asa.py", "--", "35", "35", "30", "35", "0.6", "-0.3", "0.3", "0.4")
etapa "anim" @("-b", $bl, "-P", "$p\anim_silverwing.py", "--", "todos")
etapa "pen" @("-b", $bl, "-P", "$p\corrigir_penetracao.py")
etapa "cruz" @("-b", $bl, "-P", "$p\corrigir_cruzamentos.py")
etapa "qa" @("-b", $bl, "-P", "$p\qa_silverwing.py", "--", "$o\qa.json")
etapa "faces" @("-b", $bl, "-P", "$p\diag_faces.py", "--", "$o\faces", "repouso:1", "Parado:31", "Voo:9", "Andar:13", "Pairar:11")
Write-Output "CADEIA_OK"



