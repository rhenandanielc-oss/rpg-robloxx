-- Instala a rodada r12 no rpg_roblox (Edit): Controle r12 (modelo selvagem + Teste_LoboArtico), IA r7b (so modelo selvagem),
-- Movimento_LoboArtico v48 e Cabeca_Cliente r1 (Script RunContext=Client, nos dois). Tudo-ou-nada: confere r11e / r7 / v47, compila,
-- backup em ServerStorage.LoboArtico_Backups.Antes_r12_26_11 e so entao troca. Clipes: montar_kfs_lobo_v48.luau (depois).
local HS = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local BASE = "http://127.0.0.1:8766/"
local function acha(raiz, nome) for _, d in ipairs(raiz:GetDescendants()) do if d:IsA("LuaSourceContainer") and d.Name == nome then return d end end end
local lib = game.ReplicatedStorage.Animacoes_LoboArtico
local mod, tl = SS.LoboArtico_Selvagem_Modelo, workspace.Teste_LoboArtico
local alvos = {
	{obj = acha(mod, "Controle_Servidor"), url = "Controle_Servidor_r11_proposta.server.luau", antes = "r11e 24/11", depois = "r12 26/11"},
	{obj = acha(tl, "Controle_Servidor"), url = "Controle_Servidor_r11_proposta.server.luau", antes = "r11e 24/11", depois = "r12 26/11"},
	{obj = acha(mod, "IA_LoboArtico"), url = "selvagem/IA_LoboArtico.server.luau", antes = "- r7 20/11/2026", depois = "r7b 26/11/2026"},
	{obj = lib:FindFirstChild("Movimento_LoboArtico"), url = "Movimento_LoboArtico_v48.lua", antes = "gerar_movimento_v47.py", depois = "gerar_movimento_v48.py"},
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
local cab = HS:GetAsync(BASE .. "Cabeca_Cliente.client.luau?t=" .. os.time(), true); assert(loadstring(cab), "Cabeca_Cliente nao compila")
local bk = SS.LoboArtico_Backups
if not bk:FindFirstChild("Antes_r12_26_11") then
	local p = Instance.new("Folder"); p.Name = "Antes_r12_26_11"
	for i, a in ipairs(alvos) do
		if novos[i] then local c = a.obj:Clone(); if c:IsA("BaseScript") then c.Disabled = true end; c.Name = a.obj.Name .. "_antes_" .. i; c.Parent = p end
	end
	p:SetAttribute("Origem", "antes da r12 (partida/parada, mira do peito, cabeca no cliente; instalar_r12.luau, 26/11)"); p.Parent = bk
end
for i, a in ipairs(alvos) do if novos[i] then a.obj.Source = novos[i]; table.insert(rel, a.obj:GetFullName() .. ": " .. a.antes .. " -> " .. a.depois) end end
for _, raiz in ipairs({mod, tl}) do
	local pasta = acha(raiz, "Controle_Servidor").Parent
	local s = pasta:FindFirstChild("Cabeca_Cliente") or Instance.new("Script")
	s.Name = "Cabeca_Cliente"; s.RunContext = Enum.RunContext.Client; s.Source = cab; s.Parent = pasta
	table.insert(rel, s:GetFullName() .. ": Cabeca_Cliente r1 (" .. #cab .. " bytes)")
end
return table.concat(rel, "\n")
