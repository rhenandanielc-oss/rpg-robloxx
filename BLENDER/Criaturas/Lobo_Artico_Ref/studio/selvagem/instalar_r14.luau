-- Instala o Controle r14 no rpg_roblox (Edit; usuario 27/11 "Ajustar o controle"): partida em curva so com desvio >= 75 graus e
-- decisao imediata depois dela. Modelo selvagem + Teste_LoboArtico. Tudo-ou-nada: confere r13, compila, backup Antes_r14_27_11.
local HS = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local BASE = "http://127.0.0.1:8766/"
local function acha(raiz, nome) for _, d in ipairs(raiz:GetDescendants()) do if d:IsA("LuaSourceContainer") and d.Name == nome then return d end end end
local lib = game.ReplicatedStorage.Animacoes_LoboArtico
local mod, tl = SS.LoboArtico_Selvagem_Modelo, workspace.Teste_LoboArtico
local alvos = {
	{obj = acha(mod, "Controle_Servidor"), url = "Controle_Servidor_r11_proposta.server.luau", antes = "r13 26/11", depois = "r14 27/11"},
	{obj = acha(tl, "Controle_Servidor"), url = "Controle_Servidor_r11_proposta.server.luau", antes = "r13 26/11", depois = "r14 27/11"},
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
if not bk:FindFirstChild("Antes_r14_27_11") then
	local p = Instance.new("Folder"); p.Name = "Antes_r14_27_11"
	for i, a in ipairs(alvos) do
		if novos[i] then local c = a.obj:Clone(); if c:IsA("BaseScript") then c.Disabled = true end; c.Name = a.obj.Name .. "_antes_" .. i; c.Parent = p end
	end
	p:SetAttribute("Origem", "antes do Controle r14 (instalar_r14.luau, 27/11)"); p.Parent = bk
end
for i, a in ipairs(alvos) do if novos[i] then a.obj.Source = novos[i]; table.insert(rel, a.obj:GetFullName() .. ": " .. a.antes .. " -> " .. a.depois) end end
return table.concat(rel, "\n")
