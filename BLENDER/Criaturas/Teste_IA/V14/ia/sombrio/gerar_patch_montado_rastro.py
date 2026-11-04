"""Sombrio montado com poderes + Rastro do Breu v3 (04/11). Gera V14/ia/patch_sombrio_montado_rastro.luau a partir do
src/: (1) atributo HabilidadesForma do modelo Sombrio = "Sopro,Arremetida,Coracao" (era "" = HUD/teclas do cavaleiro
sem nenhuma habilidade); (2) StarterPlayerScripts.RastroBreu_Cliente = v3 (linhas retas e mais longas). Backup unico
ServerStorage.Backup_Sombrio_Montado_Rastro_2026-11-04 (RastroBreu_Cliente v2 + atributo anterior)."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
cli = open(os.path.join(RAIZ, "src/StarterPlayer/StarterPlayerScripts/RastroBreu_Cliente.client.luau"), encoding="utf-8").read().replace("\r\n", "\n")
assert "]=====]" not in cli
L = ['-- patch_sombrio_montado_rastro.luau (Studio, Edit) — poderes do Sombrio para o cavaleiro + Rastro do Breu v3 (04/11).',
     '-- Gerado por sombrio/gerar_patch_montado_rastro.py a partir do src/. Backup unico ServerStorage.Backup_Sombrio_Montado_Rastro_2026-11-04.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage")',
     'local m = workspace:FindFirstChild("Sombrio"); assert(m, "Sombrio ausente")',
     'local S = game:GetService("StarterPlayer").StarterPlayerScripts:FindFirstChild("RastroBreu_Cliente"); assert(S, "RastroBreu_Cliente ausente")',
     'local cli = [=====[' + "\n" + cli + ']=====]',
     'assert(loadstring(cli), "RastroBreu_Cliente nao compila")',
     'local nome = "Backup_Sombrio_Montado_Rastro_2026-11-04"',
     'if not SS:FindFirstChild(nome) then local f = Instance.new("Folder"); f.Name = nome; S:Clone().Parent = f; f:SetAttribute("HabilidadesFormaAntes", tostring(m:GetAttribute("HabilidadesForma"))); f.Parent = SS end',
     'm:SetAttribute("HabilidadesForma", "Sopro,Arremetida,Coracao")',
     'S.Source = cli',
     'return "aplicado: HabilidadesForma=" .. m:GetAttribute("HabilidadesForma") .. " | RastroBreu_Cliente v3 (" .. #cli .. " bytes) | backup ServerStorage." .. nome']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_sombrio_montado_rastro.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado", len(cli))
