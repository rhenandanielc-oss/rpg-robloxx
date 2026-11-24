-- Instala no rpg_roblox (Edit) a rodada "lobo solitario + viradas naturais": IA r4 e Controle r8 SO no modelo selvagem,
-- spawner r4, Movimento_LoboArtico com as curvas VirarCurto (v44; demais curvas identicas) e os 2 clipes VirarCurto (montar_kfs v44).
-- Tudo-ou-nada: confere as fontes atuais (r3i / r7 / r3 / Movimento v41), compila as novas, faz backup em
-- ServerStorage.LoboArtico_Backups.Antes_r4_20_11 e so entao troca. O lobo de ensaio (Teste_LoboArtico) mantem o Controle r7.
local HS = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local BASE = "http://127.0.0.1:8766/"
local mod = SS:FindFirstChild("LoboArtico_Selvagem_Modelo"); assert(mod, "sem modelo selvagem")
local lib = game.ReplicatedStorage:FindFirstChild("Animacoes_LoboArtico"); assert(lib, "sem Animacoes_LoboArtico")
local function acha(raiz, nome) for _, d in ipairs(raiz:GetDescendants()) do if d:IsA("LuaSourceContainer") and d.Name == nome then return d end end end
local alvos = {
	{obj = acha(mod, "IA_LoboArtico"), url = "selvagem/IA_LoboArtico.server.luau", antes = "r3i 20/11", depois = "r4 20/11"},
	{obj = acha(mod, "Controle_Servidor"), url = "Controle_Servidor.server.luau", antes = "r7 19/11", depois = "r8 20/11"},
	{obj = game.ServerScriptService:FindFirstChild("IA_LoboArtico_Servidor"), url = "selvagem/IA_LoboArtico_Servidor.server.luau", antes = "r3 20/11", depois = "r4 20/11"},
	{obj = lib:FindFirstChild("Movimento_LoboArtico"), url = "Movimento_LoboArtico_v44.lua", antes = "gerar_movimento_v41.py", depois = "gerar_movimento_v44.py"},
}
local novos, rel = {}, {}
for i, a in ipairs(alvos) do
	assert(a.obj, "nao achado: " .. a.url)
	local cab = a.obj.Source:sub(1, 400)
	if cab:find(a.depois, 1, true) then table.insert(rel, a.obj:GetFullName() .. ": ja em " .. a.depois); continue end
	assert(cab:find(a.antes, 1, true), "fonte inesperada em " .. a.obj:GetFullName() .. " (esperava " .. a.antes .. ")")
	local novo = HS:GetAsync(BASE .. a.url .. "?t=" .. os.time(), true)
	local f, err = loadstring(novo); assert(f, "nao compila " .. a.url .. ": " .. tostring(err))
	assert(novo:sub(1, 400):find(a.depois, 1, true), "baixado sem a marca " .. a.depois)
	novos[i] = novo
end
local bk = SS:FindFirstChild("LoboArtico_Backups") or Instance.new("Folder"); bk.Name = "LoboArtico_Backups"; bk.Parent = SS
local pasta = bk:FindFirstChild("Antes_r4_20_11")
if not pasta then
	pasta = Instance.new("Folder"); pasta.Name = "Antes_r4_20_11"
	for i, a in ipairs(alvos) do
		if novos[i] then local c = a.obj:Clone(); if c:IsA("BaseScript") then c.Disabled = true end; c.Name = a.obj.Name .. "_antes"; c.Parent = pasta end
	end
	pasta:SetAttribute("Origem", "antes do lobo solitario/viradas (instalar_r4.luau, 20/11)"); pasta.Parent = bk
end
for i, a in ipairs(alvos) do
	if novos[i] then a.obj.Source = novos[i]; table.insert(rel, a.obj:GetFullName() .. ": " .. a.antes .. " -> " .. a.depois) end
end
-- clipes VirarCurto (KeyframeSequence; nao existiam)
local m = HS:GetAsync(BASE .. "montar_kfs_lobo_v44.luau?t=" .. os.time(), true)
local fm, err = loadstring(m); assert(fm, err)
table.insert(rel, fm().montar({"VirarCurtoEsquerda", "VirarCurtoDireita"}))
return table.concat(rel, "\n")
