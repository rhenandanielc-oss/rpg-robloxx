"""Montar com a asa em RAMPA e animacao do cavaleiro (06/11, pedidos do usuario: "faca a animacao de uma pessoa montando"
e "para o jogador montar, a animacao deve abrir a asa ao montar (como uma rampa)").
Troca INTEIRA (src/ e a fonte) de 2 scripts + cria 1 modulo, cada um so se o do Studio for IGUAL ao do git HEAD (assim nao
apaga mudanca feita por outro chat):
  - ServerScriptService.Montaria_Dragao_Servidor (PATCH_ANIM_CAVALEIRO + PATCH_RAMPA_MONTAR);
  - ReplicatedStorage.Comportamento_Dragoes.EstadosDragao (estados MontariaRampaE/D e o levantar delas);
  - ReplicatedStorage.Montaria_Dragoes.AnimCavaleiro (novo).
Gera V14/ia/patch_anim_cavaleiro.luau (tudo-ou-nada; backup unico ServerStorage.Backup_Anim_Cavaleiro_2026-11-06)."""
import os, subprocess
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
# (06/11, v3) a rampa saiu a pedido do usuario ("Prefiro a animacao de pulo. E por tras pulando pela cauda"); o
# EstadosDragao voltou a ser igual ao HEAD e nao entra mais. Entradas: frente (pulo) e tras (cauda).
ARQS = [("src/ServerScriptService/Montaria_Dragao_Servidor.server.luau", 'game:GetService("ServerScriptService").Montaria_Dragao_Servidor', "PATCH_ENTRADAS_MONTAR"),
        ("src/ReplicatedStorage/Montaria_Dragoes/ConfigMontaria.luau", 'game:GetService("ReplicatedStorage").Montaria_Dragoes.ConfigMontaria', "seguirOsso = 1.0")]
NOVO = "src/ReplicatedStorage/Montaria_Dragoes/AnimCavaleiro.luau"
def ler(p): return open(os.path.join(RAIZ, p), encoding="utf-8", newline="").read().replace("\r\n", "\n")
def head(p): return subprocess.run(["git", "-C", RAIZ, "show", "HEAD:" + p], capture_output=True, check=True).stdout.decode("utf-8").replace("\r\n", "\n")
L = ['-- patch_anim_cavaleiro.luau (Studio, Edit) — montar com a asa em rampa + animacao do cavaleiro (06/11).',
     '-- Gerado por sombrio/gerar_patch_anim_cavaleiro.py. Troca scripts inteiros so se o do Studio == git HEAD.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage"); local P = game:GetService("ReplicatedStorage").Montaria_Dragoes',
     'local norm = function(s) return (s:gsub("\\r\\n", "\\n")) end', 'local trocas = {}']
for i, (p, caminho, marca) in enumerate(ARQS):
    novo, velho = ler(p), head(p)
    assert marca in novo and "]======]" not in novo + velho
    L += ['do local s = %s; local src = norm(s.Source)' % caminho,
          '\tif src:find("%s", 1, true) then return "ja aplicado (%s)" end' % (marca, os.path.basename(p)),
          '\tlocal antes = [======[' + velho + ']======]',
          '\tassert(src == antes, "%s no Studio difere do git HEAD (" .. #src .. " x " .. #antes .. " bytes): nao troco")' % os.path.basename(p),
          '\tlocal depois = [======[' + novo + ']======]; assert(loadstring(depois), "%s nao compila")' % os.path.basename(p),
          '\ttable.insert(trocas, {s, depois}) end']
mod = ler(NOVO); assert "]======]" not in mod
L += ['local mod = [======[' + mod + ']======]', 'assert(loadstring(mod), "AnimCavaleiro nao compila")',
      'if not SS:FindFirstChild("Backup_Anim_Cavaleiro_2026-11-06") then local f = Instance.new("Folder"); f.Name = "Backup_Anim_Cavaleiro_2026-11-06"; for _, t in ipairs(trocas) do t[1]:Clone().Parent = f end; f.Parent = SS end',
      'for _, t in ipairs(trocas) do t[1].Source = t[2] end',
      'local Mo = P:FindFirstChild("AnimCavaleiro") or Instance.new("ModuleScript"); Mo.Name = "AnimCavaleiro"; Mo.Source = mod; Mo.Parent = P',
      'local r = {}; for _, t in ipairs(trocas) do local _, n = t[2]:gsub("\\n", ""); table.insert(r, t[1].Name .. " " .. #t[2] .. "/" .. n) end',
      'return "aplicado: " .. table.concat(r, ", ") .. "; AnimCavaleiro " .. #mod .. " bytes"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_anim_cavaleiro.luau"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("patch gerado", [(os.path.basename(p), len(ler(p).encode())) for p, _, _ in ARQS], "AnimCavaleiro", len(mod.encode()))
