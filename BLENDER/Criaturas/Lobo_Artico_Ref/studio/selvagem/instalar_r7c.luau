-- Instala a IA r7c (degrau da toca 1,8) no rpg_roblox (Edit). Tudo-ou-nada: troca TODA copia de IA_LoboArtico que esteja em r7b
-- (modelo em ServerStorage e lobos ja no Workspace), backup em ServerStorage.LoboArtico_Backups.Antes_r7c_26_11.
local HS = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local novo = HS:GetAsync("http://127.0.0.1:8766/selvagem/IA_LoboArtico.server.luau?t=" .. os.time(), true)
assert(loadstring(novo), "nao compila")
assert(novo:sub(1, 300):find("r7c 26/11/2026", 1, true), "baixado sem r7c")
local alvos, rel = {}, {}
for _, raiz in ipairs({SS, workspace}) do
	for _, d in ipairs(raiz:GetDescendants()) do
		if d:IsA("Script") and d.Name == "IA_LoboArtico" and not d:IsDescendantOf(SS.LoboArtico_Backups) then
			local h = d.Source:sub(1, 300)
			if h:find("r7c 26/11/2026", 1, true) then table.insert(rel, d:GetFullName() .. ": ja r7c")
			else assert(h:find("r7b 26/11/2026", 1, true), "fonte inesperada em " .. d:GetFullName()); table.insert(alvos, d) end
		end
	end
end
assert(#alvos + #rel > 0, "nenhum IA_LoboArtico achado")
local bk = SS.LoboArtico_Backups
if #alvos > 0 and not bk:FindFirstChild("Antes_r7c_26_11") then
	local p = Instance.new("Folder"); p.Name = "Antes_r7c_26_11"
	local c = alvos[1]:Clone(); c.Disabled = true; c.Name = "IA_LoboArtico_r7b"; c.Parent = p
	p:SetAttribute("Origem", "antes da IA r7c (instalar_r7c.luau, 26/11)"); p.Parent = bk
end
for _, d in ipairs(alvos) do d.Source = novo; table.insert(rel, d:GetFullName() .. ": r7b -> r7c") end
return table.concat(rel, "\n")
