"""Revisao visual do Sopro Umbral (v2) e das Correntes da Noite (v4) — Dragao Sombrio, 04/11.
Gera V14/ia/patch_vfx_sombra_revisao.luau a partir do src/ (fonte unica): troca SO o ModuleScript
ReplicatedStorage.Combate_Dragoes.VFXSombra (mecanica intacta: servidor nao muda) e cria/recria o elo
Combate_Dragoes.Elo_Sombra (CSG, sombrio/criar_elo_sombra.luau). Backup unico em
ServerStorage.Backup_VFXSombra_Revisao_2026-11-04 (VFXSombra antes da revisao; nao sobrescreve)."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
AQUI = os.path.dirname(os.path.abspath(__file__))
vfx = open(os.path.join(RAIZ, "src/ReplicatedStorage/Combate_Dragoes/VFXSombra.luau"), encoding="utf-8").read().replace("\r\n", "\n")
elo = open(os.path.join(AQUI, "criar_elo_sombra.luau"), encoding="utf-8").read().replace("\r\n", "\n")
assert "]=====]" not in vfx and "]=====]" not in elo
L = ['-- patch_vfx_sombra_revisao.luau (Studio, Edit) — revisao VISUAL do Sopro Umbral (v2) e das Correntes da Noite (v4).',
     '-- Gerado por sombrio/gerar_patch_vfx_revisao.py a partir do src/. Troca so o VFXSombra (cliente) e cria o Elo_Sombra.',
     '-- Backup unico: ServerStorage.Backup_VFXSombra_Revisao_2026-11-04.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage")',
     'local M = game:GetService("ReplicatedStorage").Combate_Dragoes.VFXSombra',
     'local vfx = [=====[' + "\n" + vfx + ']=====]',
     'local fn, err = loadstring(vfx); assert(fn, "VFXSombra nao compila: " .. tostring(err))',
     'local criarElo = loadstring([=====[' + "\n" + elo + ']=====]); assert(criarElo, "criar_elo nao compila")',
     'local nome = "Backup_VFXSombra_Revisao_2026-11-04"',
     'if not SS:FindFirstChild(nome) then local f = Instance.new("Folder"); f.Name = nome; M:Clone().Parent = f; f.Parent = SS end',
     'local r = criarElo()',
     'M.Source = vfx',
     'return "aplicado: VFXSombra (" .. #vfx .. " bytes) | " .. r .. " | backup ServerStorage." .. nome']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_vfx_sombra_revisao.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado", len(vfx))
