-- Instala a AMEACA visivel e sonora no rpg_roblox (Edit): IA r5 no modelo selvagem + 4 clipes (montar_kfs_lobo_v45).
-- Tudo-ou-nada: confere a IA r4 no place, compila a r5, backup em ServerStorage.LoboArtico_Backups.Antes_r5_20_11.
local HS = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local BASE = "http://127.0.0.1:8766/"
local mod = SS:FindFirstChild("LoboArtico_Selvagem_Modelo"); assert(mod, "sem modelo selvagem")
local ia; for _, d in ipairs(mod:GetDescendants()) do if d:IsA("LuaSourceContainer") and d.Name == "IA_LoboArtico" then ia = d end end
assert(ia, "sem IA_LoboArtico no modelo")
local rel = {}
if ia.Source:sub(1, 200):find("r5 20/11", 1, true) then
	table.insert(rel, "IA ja em r5")
else
	assert(ia.Source:sub(1, 200):find("r4 20/11", 1, true), "IA do place nao e a r4")
	local novo = HS:GetAsync(BASE .. "selvagem/IA_LoboArtico.server.luau?t=" .. os.time(), true)
	local f, err = loadstring(novo); assert(f, "IA r5 nao compila: " .. tostring(err))
	assert(novo:sub(1, 200):find("r5 20/11", 1, true), "baixado sem a marca r5")
	local bk = SS:FindFirstChild("LoboArtico_Backups") or Instance.new("Folder"); bk.Name = "LoboArtico_Backups"; bk.Parent = SS
	if not bk:FindFirstChild("Antes_r5_20_11") then
		local p = Instance.new("Folder"); p.Name = "Antes_r5_20_11"; local c = ia:Clone(); c.Disabled = true; c.Name = "IA_LoboArtico_r4"; c.Parent = p; p.Parent = bk
	end
	ia.Source = novo; table.insert(rel, "IA r4 -> r5 (" .. #novo .. " bytes)")
end
local m = HS:GetAsync(BASE .. "montar_kfs_lobo_v45.luau?t=" .. os.time(), true)
local fm, err = loadstring(m); assert(fm, err)
table.insert(rel, fm().montar({"AmeacaEntrar", "Ameaca", "AmeacaSair", "InvestidaAviso"}))
return table.concat(rel, "\n")
