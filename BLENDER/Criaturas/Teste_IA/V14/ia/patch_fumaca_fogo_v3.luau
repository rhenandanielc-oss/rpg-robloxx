-- patch_fumaca_fogo_v3.luau (Studio, Edit) — fumaca residual do Fogo reforcada (05/11). Gerado por sombrio/gerar_patch_fumaca_fogo_v3.py.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage"); local V = game:GetService("ReplicatedStorage").Combate_Dragoes.VFXCombate
local src = V.Source:gsub("\r\n", "\n")
if src:find("PATCH_FUMACA_FOGO_V3", 1, true) then return "ja aplicado" end
if src:find("PATCH_FUMACA_FOGO_V2", 1, true) then local bk = SS:FindFirstChild("Backup_Fumaca_Fogo_v2_2026-11-05"); assert(bk, "sem backup do v2"); src = bk.VFXCombate.Source:gsub("\r\n", "\n") end   -- volta ao v1
assert(src:find("PATCH_FUMACA_RESIDUAL", 1, true), "aplique antes o patch_fumaca_residual.luau")
do local a, b = [======[	Fogo = {cor = {C3(96, 86, 80), C3(52, 49, 48)}, luzI = 1, sobe = 2.2, alfa = 0.55, tex = FB.fumaca, brasa = C3(255, 150, 60)},
]======], [======[	Fogo = {cor = {C3(104, 96, 90), C3(62, 59, 58)}, luzI = 1, sobe = 2.4, alfa = 0.45, tex = FB.fumaca, brasa = C3(255, 150, 60),   -- PATCH_FUMACA_FOGO_V3
		taxa = 1.4, tam = 1.1, vida = 2.2, brasas = 12},
]======]
	local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora 1")
	src = src:sub(1, i - 1) .. b .. src:sub(j + 1) end
do local a, b = [======[		local t = table.clone(base)
]======], [======[		local t = table.clone(base); tam = tam * (R.tam or 1); taxa = taxa * (R.taxa or 1)
]======]
	local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora 2")
	src = src:sub(1, i - 1) .. b .. src:sub(j + 1) end
do local a, b = [======[		t.Lifetime = NumberRange.new(1.1, 1.9);]======], [======[		t.Lifetime = NumberRange.new(1.1, R.vida or 1.9);]======]
	local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora 3")
	src = src:sub(1, i - 1) .. b .. src:sub(j + 1) end
do local a, b = [======[EmissionDirection = Enum.NormalId.Front, Rate = 7 * f}))
]======], [======[EmissionDirection = Enum.NormalId.Front, Rate = (R.brasas or 7) * f}))
]======]
	local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora 4")
	src = src:sub(1, i - 1) .. b .. src:sub(j + 1) end
assert(loadstring(src), "VFXCombate nao compila")
if not SS:FindFirstChild("Backup_Fumaca_Fogo_v3_2026-11-05") then local f = Instance.new("Folder"); f.Name = "Backup_Fumaca_Fogo_v3_2026-11-05"; V:Clone().Parent = f; f.Parent = SS end
V.Source = src
local _, n = src:gsub("\n", "")
return "aplicado: VFXCombate " .. #src .. " bytes / " .. n .. " linhas"
