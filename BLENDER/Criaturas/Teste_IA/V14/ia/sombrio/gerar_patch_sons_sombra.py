"""Sons do kit da Sombra (04/11, pedido do usuario "Faca os sons"). Novo ModuleScript
ReplicatedStorage.Combate_Dragoes.SonsSombra (src/ e a fonte) e o VFXSombra passa a chamar o audio em todo evento de
Sombra, antes do LOD visual. Gera V14/ia/patch_sons_sombra.luau (tudo-ou-nada; backup unico
ServerStorage.Backup_Sons_Sombra_2026-11-04 com o VFXSombra anterior)."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
MARCA = "PATCH_SONS_SOMBRA"
CD = os.path.join(RAIZ, "src/ReplicatedStorage/Combate_Dragoes")
A = 'function S.evento(d, f)\n\tlocal m = d.d\n'
B = ('function S.evento(d, f)\n\tlocal m = d.d\n'
     '\tlocal SN = script.Parent:FindFirstChild("SonsSombra")               -- PATCH_SONS_SOMBRA: audio antes do LOD visual\n'
     '\tif SN and d.fase ~= "reacao" then local ok, e = pcall(require(SN).evento, d); if not ok then warn("SonsSombra: " .. tostring(e)) end end\n')
p = os.path.join(CD, "VFXSombra.luau"); s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
if MARCA not in s:
    assert s.count(A) == 1, s.count(A); s = s.replace(A, B)
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok VFXSombra")
SONS = open(os.path.join(CD, "SonsSombra.luau"), encoding="utf-8").read().replace("\r\n", "\n")
assert "]======]" not in SONS + A + B
L = ['-- patch_sons_sombra.luau (Studio, Edit) — audio do kit da Sombra (04/11). Gerado por sombrio/gerar_patch_sons_sombra.py.',
     '-- Cria ReplicatedStorage.Combate_Dragoes.SonsSombra e liga o VFXSombra; backup unico ServerStorage.Backup_Sons_Sombra_2026-11-04.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage"); local CD = game:GetService("ReplicatedStorage").Combate_Dragoes',
     'local V = CD.VFXSombra; local src = V.Source:gsub("\\r\\n", "\\n")',
     'if src:find("%s", 1, true) then return "ja aplicado" end' % MARCA,
     'local a, b = [======[' + A + ']======], [======[' + B + ']======]',
     'local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora VFXSombra")',
     'src = src:sub(1, i - 1) .. b .. src:sub(j + 1); assert(loadstring(src), "VFXSombra nao compila")',
     'local sons = [======[' + SONS + ']======]',
     'assert(loadstring(sons), "SonsSombra nao compila")',
     'if not SS:FindFirstChild("Backup_Sons_Sombra_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Sons_Sombra_2026-11-04"; V:Clone().Parent = f; f.Parent = SS end',
     'local M = CD:FindFirstChild("SonsSombra") or Instance.new("ModuleScript"); M.Name = "SonsSombra"; M.Source = sons; M.Parent = CD',
     'V.Source = src',
     'return "aplicado: SonsSombra (" .. #sons .. " bytes) + VFXSombra (" .. #src .. " bytes)"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_sons_sombra.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
