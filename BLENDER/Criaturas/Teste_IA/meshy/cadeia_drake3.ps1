# Cadeia do Silverwing Drake v2 SEM lascas nas juncoes (saida_drake3): como cadeia_drake2 +
#  ASA_X_MIN 0.09   peito/dorso medial nao pertence a asa (rachadura na frente do ombro)
#  COSTURA_RAIZ 0.08 asa x tronco/pata se misturam no repose perto da dobradica
#  ANG_QUADRIL_VOO 12 patas de voo giram pouco no quadril/ombro (dobra no joelho/tornozelo)
#  costura_regioes  faixa macia entre regioes nos pesos finais;  suavizar_esticadas  depois das correcoes
$p = $PSScriptRoot; $b = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"; $o = "$p\saida_drake3"; $bl = "$o\Silverwing_M2M.blend"
New-Item -ItemType Directory -Force $o | Out-Null
$pat = "DOBRADICA|COSTURAS_UV|UNIFICAR_OK|ASA_X_MIN|COSTURA|GIRO_ASA|PESOS_REPOSE|MONTAR_OK|PESOS_NOVOS|MAX_INFL|REPESAR_OK|ASSAR_OK|INFLU|DOBRA_OK|CLIPE|ANIM_OK|PASSADA|PEN_OK|CRUZ_OK|SUAVIZAR_OK|QA_OK|NORMAIS|DIAG_FACES|INTER_|VIRADAS_POR|Traceback|Error"
function etapa($n, $a) { Write-Output "== $n"; & $b @a 2>&1 | Select-String -Pattern $pat | ForEach-Object { $_.Line } }
$env:ASA_INTEIRA = "1"; $env:CORPO_FIXO = "1"; $env:NECK_BASE = "0"; $env:PESC_VOO = "-40"; $env:SEM_PONTES = "1"; $env:RAIO_ASA = "0.045"; $env:PERNA_VOO_REL = "1"
$env:ASA_X_MIN = "0.09"; $env:COSTURA_RAIZ = "0.08"; $env:ANG_QUADRIL_VOO = "12"
etapa "montar" @("-b", "--factory-startup", "-P", "$p\montar_silverwing.py", "--", "$p\m2m_fonte\dragon-animations.glb", "$p\drake2\Drake2_lo.glb", "$p\drake2\encaixe.json", $o)
etapa "repesar" @("-b", $bl, "-P", "$p\repesar_silverwing.py")
etapa "mao" @("-b", $bl, "-P", "$p\assar_mao.py", "--", "$p\m2m_fonte\dragon-animations.glb")
etapa "limite4" @("-b", $bl, "-P", "$p\revisar_silverwing.py", "--", "$o\revisao", "1")
etapa "costura" @("-b", $bl, "-P", "$p\costura_regioes.py", "--", "5", "30")
etapa "uv1" @("-b", $bl, "-P", "$p\unificar_costuras_uv.py")
etapa "dobra" @("-b", $bl, "-P", "$p\dobra_asa.py", "--", "35", "35", "30", "35", "0.6", "-0.3", "0.3", "0.4")
etapa "anim" @("-b", $bl, "-P", "$p\anim_silverwing.py", "--", "todos")
etapa "pen" @("-b", $bl, "-P", "$p\corrigir_penetracao.py")
etapa "cruz" @("-b", $bl, "-P", "$p\corrigir_cruzamentos.py")
etapa "suavizar" @("-b", $bl, "-P", "$p\suavizar_esticadas.py", "--", "1.6", "4")
etapa "uv2" @("-b", $bl, "-P", "$p\unificar_costuras_uv.py")
# raiz da asa: gradiente de pesos na dobradica (sem lascas no bater/dobrar) e de novo penetracao/cruzamento/costuras
etapa "dobradica" @("-b", $bl, "-P", "$p\dobradica_asa.py", "--", "-0.03", "0.08", "0.13")
etapa "uv3" @("-b", $bl, "-P", "$p\unificar_costuras_uv.py")
etapa "pen2" @("-b", $bl, "-P", "$p\corrigir_penetracao.py")
etapa "cruz2" @("-b", $bl, "-P", "$p\corrigir_cruzamentos.py")
etapa "uv4" @("-b", $bl, "-P", "$p\unificar_costuras_uv.py")
etapa "qa" @("-b", $bl, "-P", "$p\qa_silverwing.py", "--", "$o\qa.json")
etapa "inter" @("-b", $bl, "-P", "$p\mapa_intersecoes.py")
Write-Output "CADEIA_OK"
