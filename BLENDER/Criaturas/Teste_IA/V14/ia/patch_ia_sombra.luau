-- patch_ia_sombra.luau (Studio, Edit) — IA selvagem com o kit da Sombra + PassoBonus no Locomotor (04/11).
-- Gerado por sombrio/gerar_patch_ia_sombra.py; backup unico ServerStorage.Backup_IA_Sombra_2026-11-04.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage")
local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end
local novos = {}
do local s = game.ServerScriptService.Combate_Dragao_Servidor; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_IA_KIT_SOMBRA", 1, true) then return "ja aplicado" end
  src = troca(src, [=====[local function alcSopro(c)
	local e = Cfg.habilidades.Sopro.porElemento[c.m:GetAttribute("ElementoAtivo") or ""]; return e and e.alcance or 100
end
]=====], [=====[local function alcSopro(c)
	if c:real("Coracao") == "Eclipse" then                             -- PATCH_IA_KIT_SOMBRA: Sopro Umbral tem alcance proprio
		local e = Cfg.habilidades.SoproUmbral.porElemento.Sombra; return e and e.alcance or 95
	end
	local e = Cfg.habilidades.Sopro.porElemento[c.m:GetAttribute("ElementoAtivo") or ""]; return e and e.alcance or 100
end
]=====])
  src = troca(src, [=====[	local noAr = c.m:GetAttribute("NoAr") == true
	local perto, atrasN = 0, 0
]=====], [=====[	local noAr = c.m:GetAttribute("NoAr") == true
	local kitS = c:real("Coracao") == "Eclipse"                             -- PATCH_IA_KIT_SOMBRA
	local perto, atrasN = 0, 0
]=====])
  src = troca(src, [=====[	if c:temHabilidade("Coracao") and os.clock() - (ultimoCoracao[c.m] or -99) > CI.recarga * 1.5 then
]=====], [=====[	if not kitS and c:temHabilidade("Coracao") and os.clock() - (ultimoCoracao[c.m] or -99) > CI.recarga * 1.5 then
]=====])
  src = troca(src, [=====[	if perto >= 3 or (perto >= 2 and (atrasN >= 1 or math.random() < 0.35)) then
]=====], [=====[	if not kitS and (perto >= 3 or (perto >= 2 and (atrasN >= 1 or math.random() < 0.35))) then
]=====])
  src = troca(src, [=====[	if d >= 50 and d < 170 then
]=====], [=====[	if not kitS and d >= 50 and d < 170 then
]=====])
  src = troca(src, [=====[	-- PATCH_RUGIDOS_FOGO: rugido de combate ocasional]=====], [=====[	-- PATCH_IA_KIT_SOMBRA (04/11): kit do Sombrio com tatica propria (slots: Arremetida = Correntes, Tempestade = Passo,
	-- Coracao = Eclipse). NAO_APROVADO
	if kitS then
		local CO, EC = Cfg.habilidades.Correntes, Cfg.habilidades.Eclipse
		-- Correntes: media/longa distancia, com linha de visao; vem do chao, entao serve contra alvo no ar (prioridade
		-- maior se ele voa acima ou esta alem do sopro)
		if d >= 22 and d < CO.alcance then
			if not c:visivel(b, alvo) then table.insert(bloqueio, "Correntes: sem linha de visao")
			else add("Arremetida", (acima > 15 or d > alcSopro(c)) and 1.05 or 0.8) end
		end
		-- Eclipse: alvos dentro da area; grupo (2+) ou um alvo com 3+ marcas desta origem (mais marcas, mais vontade)
		if os.clock() - (ultimoCoracao[c.m] or -99) > EC.recarga * 1.5 then
			local naArea, marcas = 0, 0
			for _, a in ipairs(c:alvosValidos()) do
				if (raiz(a).Position - p).Magnitude < EC.raio * 0.8 then naArea += 1; marcas += a:GetAttribute("MarcaSombria_" .. c.m.Name) or 0 end
			end
			if naArea >= 2 or (naArea == 1 and marcas >= 3) then add("Coracao", 1.15 + math.min(marcas, 5) * 0.03)
			elseif naArea == 1 then table.insert(bloqueio, "Eclipse: poucas marcas (" .. marcas .. ")") end
		end
		-- Passo Sombrio: some e acelera para escapar ferido ou para encurtar a distancia de um alvo longe
		local vida, vmax = c.m:GetAttribute("Vida"), c.m:GetAttribute("VidaMax")
		local ferido = vida and vmax and vmax > 0 and vida / vmax < 0.35
		if not c.m:GetAttribute("PassoInvisivel") and (ferido or d > 110) then add("Tempestade", ferido and 1.3 or 0.7) end
	end
	-- PATCH_RUGIDOS_FOGO: rugido de combate ocasional]=====])
  assert(loadstring(src), "Combate_Dragao_Servidor.server.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.IA_Dragao.Locomotor; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_IA_KIT_SOMBRA", 1, true) then return "ja aplicado" end
  src = troca(src, [=====[		or (self.m:GetAttribute("RitmoAndarBase") or cfg.andarVel * cfg.andarRitmo)
]=====], [=====[		or (self.m:GetAttribute("RitmoAndarBase") or cfg.andarVel * cfg.andarRitmo)
	vel *= 1 + (self.m:GetAttribute("PassoBonus") or 0)                  -- PATCH_IA_KIT_SOMBRA: Passo Sombrio da IA
]=====])
  src = troca(src, [=====[		local vel = rapido and cfg.vooRapidoVel or cfg.vooVel
]=====], [=====[		local vel = (rapido and cfg.vooRapidoVel or cfg.vooVel) * (1 + (self.m:GetAttribute("PassoBonus") or 0))   -- PATCH_IA_KIT_SOMBRA
]=====])
  assert(loadstring(src), "Locomotor.luau nao compila"); table.insert(novos, {s, src}) end
if not SS:FindFirstChild("Backup_IA_Sombra_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_IA_Sombra_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f.Parent = SS end
for _, x in ipairs(novos) do x[1].Source = x[2] end
return "aplicado: " .. #novos .. " scripts; backup ServerStorage.Backup_IA_Sombra_2026-11-04"
