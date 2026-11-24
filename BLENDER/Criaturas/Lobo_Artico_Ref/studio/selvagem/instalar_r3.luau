-- Instala a IA r3 + Kit r15 (so no modelo selvagem) + spawner r3 no rpg_roblox (Edit). Tudo-ou-nada:
-- 1) confere que as fontes do place sao as esperadas (r2j / r14 / r2); 2) baixa as novas de http://127.0.0.1:8766 e
-- compila com loadstring; 3) backup em ServerStorage.LoboArtico_Backups.Antes_IA_r3_20_11; 4) troca o Source.
-- Servidor HTTP: python -m http.server 8766 a partir de BLENDER/Criaturas/Lobo_Artico_Ref/studio.
local HS = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local SSS = game:GetService("ServerScriptService")
local BASE = "http://127.0.0.1:8766/"
local modelo = SS:FindFirstChild("LoboArtico_Selvagem_Modelo"); assert(modelo, "sem LoboArtico_Selvagem_Modelo")
local function acha(raiz, nome)
	for _, d in ipairs(raiz:GetDescendants()) do if d:IsA("LuaSourceContainer") and d.Name == nome then return d end end
end
local alvos = {
	{obj = acha(modelo, "IA_LoboArtico"), url = "selvagem/IA_LoboArtico.server.luau", antes = _G.R3_ANTES_IA or "r2j 20/11", depois = _G.R3_DEPOIS_IA or "r3 20/11"},
	{obj = acha(modelo, "Kit_Servidor"), url = "Kit_Servidor.server.luau", antes = "r14 19/11", depois = "r15 20/11"},
	{obj = SSS:FindFirstChild("IA_LoboArtico_Servidor"), url = "selvagem/IA_LoboArtico_Servidor.server.luau", antes = "r2 19/11", depois = "r3 20/11"},
}
local novos, rel = {}, {}
for i, a in ipairs(alvos) do
	assert(a.obj, "script nao achado: " .. a.url)
	local src = a.obj.Source
	if src:sub(1, 400):find(a.depois, 1, true) then table.insert(rel, a.obj:GetFullName() .. ": ja estava em " .. a.depois); continue end
	assert(src:sub(1, 600):find(a.antes, 1, true), "fonte inesperada em " .. a.obj:GetFullName() .. " (esperava " .. a.antes .. ")")
	local novo = HS:GetAsync(BASE .. a.url .. "?t=" .. os.time(), true)
	local f, err = loadstring(novo); assert(f, "nao compila " .. a.url .. ": " .. tostring(err))
	assert(novo:sub(1, 400):find(a.depois, 1, true), "baixado sem a marca " .. a.depois)
	novos[i] = novo
end
local bk = SS:FindFirstChild("LoboArtico_Backups") or Instance.new("Folder"); bk.Name = "LoboArtico_Backups"; bk.Parent = SS
local pasta = bk:FindFirstChild("Antes_IA_r3_20_11")
if not pasta then
	pasta = Instance.new("Folder"); pasta.Name = "Antes_IA_r3_20_11"
	for i, a in ipairs(alvos) do
		if novos[i] then local c = a.obj:Clone(); c.Disabled = true; c.Name = a.obj.Name .. "_" .. a.antes:gsub("[^%w]", ""); c.Parent = pasta end
	end
	pasta:SetAttribute("Origem", "fontes do place antes da r3 (instalar_r3.luau)"); pasta.Parent = bk
end
for i, a in ipairs(alvos) do
	if novos[i] then a.obj.Source = novos[i]; table.insert(rel, a.obj:GetFullName() .. ": " .. a.antes .. " -> " .. a.depois .. " (" .. #novos[i] .. " bytes)") end
end
return table.concat(rel, "\n")
