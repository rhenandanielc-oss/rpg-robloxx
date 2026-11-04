"""Correntes: alvo no ar -> as correntes vem do CHAO (sobem em 0,35 s qualquer altura; elos suficientes para o
comprimento, ate 90 por corrente); fenda no ar so sem chao embaixo; aviso roxo/erupcao tambem no chao (04/11; pedido do usuario). So o VFXSombra (cliente)
muda. Gera V14/ia/patch_correntes_chao_ar.luau; backup unico ServerStorage.Backup_Correntes_Chao_Ar_2026-11-04."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
vfx = open(os.path.join(RAIZ, "src/ReplicatedStorage/Combate_Dragoes/VFXSombra.luau"), encoding="utf-8").read().replace("\r\n", "\n")
assert "PATCH_CORRENTES_CHAO_AR" in vfx and "]=====]" not in vfx
L = ['-- patch_correntes_chao_ar.luau (Studio, Edit) — correntes do chao ate o alvo no ar (04/11). Gerado por',
     '-- sombrio/gerar_patch_correntes_chao_ar.py a partir do src/. Backup unico ServerStorage.Backup_Correntes_Chao_Ar_2026-11-04.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage"); local M = game:GetService("ReplicatedStorage").Combate_Dragoes.VFXSombra',
     'local vfx = [=====[' + "\n" + vfx + ']=====]',
     'assert(loadstring(vfx), "VFXSombra nao compila")',
     'if not SS:FindFirstChild("Backup_Correntes_Chao_Ar_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Correntes_Chao_Ar_2026-11-04"; M:Clone().Parent = f; f.Parent = SS end',
     'M.Source = vfx',
     'return "aplicado: VFXSombra (" .. #vfx .. " bytes); backup ServerStorage.Backup_Correntes_Chao_Ar_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_correntes_chao_ar.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado", len(vfx))
