-- patch_mix_vertical_parado.luau (Studio, modo Edit) — certificacao do Dragao Glacial (02/11): parado no ar, segurando
-- E (sobe) ou Q (desce), o misturador de voo so tocava o Pairar (a Subida/Descida so entravam com o dragao andando para
-- frente). Agora, num dragao com o atributo MixVerticalParado = true, a subida/descida vertical mistura o clipe de
-- Subida (cabeca para cima, batidas de esforco) ou de Descida ao Pairar, na proporcao da velocidade vertical (ate 70%).
-- Sem o atributo (Dragao das Montanhas) nada muda. So animacao: velocidades e controles intactos.
local SSS, SS = game:GetService("ServerScriptService"), game:GetService("ServerStorage")
local alvos = {MS = SSS.Montaria_Dragao_Servidor}
if alvos.MS.Source:find("PATCH_MIX_VERTICAL", 1, true) then return "ja aplicado" end
local novo = {}; for k, s in pairs(alvos) do novo[k] = s.Source:gsub("\r\n", "\n") end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true); assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end
troca("MS", [=[	w[esq and "Curva_Aerea_E_AFK" or "Curva_Aerea_D_AFK"] = pl * curva + ba * (1 - pairar) * curva * 0.35
	pesos(M, w)
	local ritmo = 0.9 + 0.45 * k + (gd > 8 and 0.25 or 0) + (f > 0.1 and 0.1 or 0)]=], [=[	w[esq and "Curva_Aerea_E_AFK" or "Curva_Aerea_D_AFK"] = pl * curva + ba * (1 - pairar) * curva * 0.35
	-- PATCH_MIX_VERTICAL (02/11): parado no ar subindo (E) ou descendo (Q): Subida/Descida entram sobre o Pairar
	if m:GetAttribute("MixVerticalParado") and M.vyH ~= 0 then
		local hp = ba * pairar
		local sv = math.clamp(M.vyH / math.max(1, VL.vSubidaParado), 0, 1) * 0.7
		local dv = math.clamp(-M.vyH / math.max(1, VL.vDescidaParado), 0, 1) * 0.7
		w.Pairar_AFK = hp * (1 - sv - dv); w.Subida_AFK += hp * sv; w.Descida_AFK += hp * dv
	end
	pesos(M, w)
	local ritmo = 0.9 + 0.45 * k + (gd > 8 and 0.25 or 0) + (f > 0.1 and 0.1 or 0)]=])
for k in pairs(alvos) do local f, e = loadstring(novo[k]); assert(f, k .. " nao compila: " .. tostring(e)) end
local bk = SS:FindFirstChild("Backup_Mix_Vertical_2026-11-02")
if not bk then
	bk = Instance.new("Folder"); bk.Name = "Backup_Mix_Vertical_2026-11-02"
	for k, s in pairs(alvos) do local c = s:Clone(); c.Name = k .. "__" .. s.Name; c.Enabled = false; c.Parent = bk end
	bk.Parent = SS
end
for k, s in pairs(alvos) do s.Source = novo[k] end
for _, n in ipairs({"Glacial", "Glacial_Guardiao"}) do local g = workspace:FindFirstChild(n); if g then g:SetAttribute("MixVerticalParado", true) end end
return "aplicado"
