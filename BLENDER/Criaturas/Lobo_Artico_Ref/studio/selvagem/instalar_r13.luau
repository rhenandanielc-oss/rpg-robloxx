-- Instala a rodada r13 no rpg_roblox (Edit): Controle r13 (modelo selvagem + Teste_LoboArtico) e Movimento_LoboArtico v49 (curvas de
-- trote e corrida). Tudo-ou-nada: confere r12 / v48, compila, backup em ServerStorage.LoboArtico_Backups.Antes_r13_26_11.
-- Clipes: montar_kfs_lobo_v49.luau (depois, em lotes).
local HS = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local BASE = "http://127.0.0.1:8766/"
local function acha(raiz, nome) for _, d in ipairs(raiz:GetDescendants()) do if d:IsA("LuaSourceContainer") and d.Name == nome then return d end end end
local lib = game.ReplicatedStorage.Animacoes_LoboArtico
local mod, tl = SS.LoboArtico_Selvagem_Modelo, workspace.Teste_LoboArtico
local alvos = {
	{obj = acha(mod, "Controle_Servidor"), url = "Controle_Servidor_r11_proposta.server.luau", antes = "r12 26/11", depois = "r13 26/11"},
	{obj = acha(tl, "Controle_Servidor"), url = "Controle_Servidor_r11_proposta.server.luau", antes = "r12 26/11", depois = "r13 26/11"},
	{obj = lib:FindFirstChild("Movimento_LoboArtico"), url = "Movimento_LoboArtico_v49.lua", antes = "gerar_movimento_v48.py", depois = "gerar_movimento_v49.py"},
}
local novos, rel = {}, {}
for i, a in ipairs(alvos) do
	assert(a.obj, "nao achado: " .. a.url)
	if a.obj.Source:sub(1, 600):find(a.depois, 1, true) then table.insert(rel, a.obj:GetFullName() .. ": ja em " .. a.depois); continue end
	assert(a.obj.Source:sub(1, 600):find(a.antes, 1, true), "fonte inesperada em " .. a.obj:GetFullName())
	local novo = HS:GetAsync(BASE .. a.url .. "?t=" .. os.time(), true)
	local f, err = loadstring(novo); assert(f, "nao compila " .. a.url .. ": " .. tostring(err))
	assert(novo:sub(1, 600):find(a.depois, 1, true), "baixado sem a marca " .. a.depois)
	novos[i] = novo
end
local bk = SS.LoboArtico_Backups
if not bk:FindFirstChild("Antes_r13_26_11") then
	local p = Instance.new("Folder"); p.Name = "Antes_r13_26_11"
	for i, a in ipairs(alvos) do
		if novos[i] then local c = a.obj:Clone(); if c:IsA("BaseScript") then c.Disabled = true end; c.Name = a.obj.Name .. "_antes_" .. i; c.Parent = p end
	end
	p:SetAttribute("Origem", "antes da r13 (curvas de trote/corrida; instalar_r13.luau, 26/11)"); p.Parent = bk
end
for i, a in ipairs(alvos) do if novos[i] then a.obj.Source = novos[i]; table.insert(rel, a.obj:GetFullName() .. ": " .. a.antes .. " -> " .. a.depois) end end
return table.concat(rel, "\n")
