-- patch_hud_habilidades_forma.luau (Studio, modo Edit) — achado no teste do Dragao Glacial (01/11): o HUD da montaria
-- mostrava e ligava as 4 habilidades de FOGO (Sopro, Arremetida, Tempestade, Coracao) em qualquer dragao. Agora o
-- dragao pode declarar o atributo HabilidadesForma ("" = nenhuma; "Sopro,Arremetida" = so essas): slots e teclas
-- seguem essa lista. Sem o atributo (Dragao das Montanhas) nada muda. O servidor ja recusava (ConfigCombate.
-- habilidadesForma), entao isto so corrige o que o jogador ve e as teclas. Kit de gelo segue PENDENTE.
local SP, SS = game:GetService("StarterPlayer"), game:GetService("ServerStorage")
local alvos = {MC = SP.StarterPlayerScripts.Montaria_Cliente}
if alvos.MC.Source:find("PATCH_HUD_FORMA", 1, true) then return "ja aplicado" end
local novo = {}; for k, s in pairs(alvos) do novo[k] = s.Source:gsub("\r\n", "\n") end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true); assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end
troca("MC", [=[local m = nil                                                        -- dragao montado]=],
[=[local m = nil                                                        -- dragao montado
-- PATCH_HUD_FORMA (01/11): habilidades que ESTE dragao tem (atributo HabilidadesForma; sem ele = todas, como antes)
local function habPermitida(nome)
	local lista = m and m:GetAttribute("HabilidadesForma")
	if lista == nil then return true end
	return table.find(string.split(lista, ","), nome) ~= nil
end]=])
troca("MC", [=[	for _, h in ipairs(C.habilidades) do
		acao("Mont_" .. h[1], function(st)]=], [=[	for _, h in ipairs(C.habilidades) do
		if not habPermitida(h[1]) then continue end
		acao("Mont_" .. h[1], function(st)]=])
troca("MC", [=[	slotMordida.Visible = m:GetAttribute("VooLivre") == true]=], [=[	slotMordida.Visible = m:GetAttribute("VooLivre") == true
	for _, h in ipairs(C.habilidades) do slots[h[1]].cob.Parent.Visible = habPermitida(h[1]) end
	if m:GetAttribute("HabilidadesForma") ~= nil then
		dica.Text = dica.Text:gsub(" | segure 1: sopro continuo %(mira no cursor%) | 2 Arremetida | 3 Tempestade | 4 Coracao Infernal", ""):gsub(" | 1%-4 habilidades", "")
	end]=])
for k in pairs(alvos) do local f, e = loadstring(novo[k]); assert(f, k .. " nao compila: " .. tostring(e)) end
local bk = SS:FindFirstChild("Backup_HUD_Forma_2026-11-01")
if not bk then
	bk = Instance.new("Folder"); bk.Name = "Backup_HUD_Forma_2026-11-01"
	for k, s in pairs(alvos) do local c = s:Clone(); c.Name = k .. "__" .. s.Name; c.Enabled = false; c.Parent = bk end
	bk.Parent = SS
end
for k, s in pairs(alvos) do s.Source = novo[k] end
workspace:FindFirstChild("Glacial"):SetAttribute("HabilidadesForma", "")     -- kit de gelo pendente: nenhuma habilidade
return "aplicado"
