-- Instala a rodada "andar em curva com passos" no rpg_roblox (Edit), PARTE 1 (scripts): Controle r11 no modelo selvagem E no
-- Teste_LoboArtico, Movimento_LoboArtico v46b (acrescenta as 16 curvas; as anteriores iguais). Tudo-ou-nada: confere r10e / v44,
-- compila as novas, backup em ServerStorage.LoboArtico_Backups.Antes_r11_20_11 e so entao troca. Os clipes (KFS) vem na PARTE 2
-- (montar_kfs_lobo_v46b.luau, em lotes). O r11 so liga as curvas se os 16 clipes E as curvas existirem (TEM_CURVAS).
local HS = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local BASE = "http://127.0.0.1:8766/"
local function acha(raiz, nome) for _, d in ipairs(raiz:GetDescendants()) do if d:IsA("LuaSourceContainer") and d.Name == nome then return d end end end
local lib = game.ReplicatedStorage.Animacoes_LoboArtico
local alvos = {
	{obj = acha(SS.LoboArtico_Selvagem_Modelo, "Controle_Servidor"), url = "Controle_Servidor_r11_proposta.server.luau", antes = "r10e 20/11 (ponto de passagem", depois = "r11 PROPOSTA 20/11"},
	{obj = acha(workspace.Teste_LoboArtico, "Controle_Servidor"), url = "Controle_Servidor_r11_proposta.server.luau", antes = "r10e 20/11 (ponto de passagem", depois = "r11 PROPOSTA 20/11"},
	{obj = lib:FindFirstChild("Movimento_LoboArtico"), url = "Movimento_LoboArtico_v46b.lua", antes = "gerar_movimento_v44.py", depois = "gerar_movimento_v46b.py"},
}
local novos, rel = {}, {}
for i, a in ipairs(alvos) do
	assert(a.obj, "nao achado: " .. a.url)
	if a.obj.Source:sub(1, 600):find(a.depois, 1, true) then table.insert(rel, a.obj:GetFullName() .. ": ja em " .. a.depois); continue end
	assert(a.obj.Source:find(a.antes, 1, true), "fonte inesperada em " .. a.obj:GetFullName())
	local novo = HS:GetAsync(BASE .. a.url .. "?t=" .. os.time(), true)
	local f, err = loadstring(novo); assert(f, "nao compila " .. a.url .. ": " .. tostring(err))
	assert(novo:sub(1, 600):find(a.depois, 1, true), "baixado sem a marca " .. a.depois)
	novos[i] = novo
end
local bk = SS.LoboArtico_Backups
if not bk:FindFirstChild("Antes_r11_20_11") then
	local p = Instance.new("Folder"); p.Name = "Antes_r11_20_11"
	for i, a in ipairs(alvos) do
		if novos[i] then local c = a.obj:Clone(); if c:IsA("BaseScript") then c.Disabled = true end; c.Name = a.obj.Name .. "_antes_" .. i; c.Parent = p end
	end
	p:SetAttribute("Origem", "antes das curvas andando (instalar_r11.luau, 20/11)"); p.Parent = bk
end
for i, a in ipairs(alvos) do if novos[i] then a.obj.Source = novos[i]; table.insert(rel, a.obj:GetFullName() .. ": " .. a.antes .. " -> " .. a.depois .. " (" .. #novos[i] .. " bytes)") end end
return table.concat(rel, "\n")
