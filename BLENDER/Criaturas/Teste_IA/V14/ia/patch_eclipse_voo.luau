-- patch_eclipse_voo.luau (Studio, Edit) — Eclipse em voo: decola, ruge, solta, ruge pairando, pousa (04/11).
-- Gerado por sombrio/gerar_patch_eclipse_voo.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico
-- ServerStorage.Backup_Eclipse_Voo_2026-11-04.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage")
local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end
local novos = {}
do local s = game.ServerScriptService.Combate_Dragao.ConfigCombate; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_ECLIPSE_VOO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[			danoArea = 3, tickArea = 0.5, clipeLoop = "Eclipse_Rugido_Loop", clipeFim = "Eclipse_Rugido_Fim", fimRugido = 0.6},]==], [==[			danoArea = 3, tickArea = 0.5, clipeLoop = "Eclipse_Rugido_Loop", clipeFim = "Eclipse_Rugido_Fim", fimRugido = 0.6,
			-- PATCH_ECLIPSE_VOO (04/11, pedido do usuario): decola (altura), ruge (rugir s), solta no ar e pousa (descida s)
			altura = 24, subidaAr = 10, rugir = 1.2, descida = 1.1},]==])
  assert(loadstring(src), "ConfigCombate.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Combate_Dragao.Nucleo; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_ECLIPSE_VOO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[function N:_Eclipse(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "inicio", el = el, noAr = noAr, detona = def.detona, raio = def.raio})
	local tPrinc = self:tocar(def.clipe, noAr, {}, function() end)
	task.wait(def.detona)
	if not m.Parent or m:GetAttribute("Incapacitado") then FX:FireAllClients({d = m, hab = "Eclipse", fase = "fim", el = el}); return end
	local c = self:centroCorpo()
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "detonar", el = el, pos = c, raio = def.raio, duracao = def.escuro})
	local mult = ((m:GetAttribute("DominioAtivo") and Cfg.habilidades.Dominio.multiplicadorDano) or 1) * Passivas.multiplicadorOfensivo(m)
	local total, nAlvos = 0, 0
	for _, a in ipairs(self:alvosValidos()) do
		if naEsfera(c, def.raio, a) and self:visivel(c, a) then
			local n = Passivas.consumirMarcas(m, a)                         -- zera ANTES do dano: o multiplicador da Marca nao soma
			if n > 0 and N.ferir(m, a, def.danoPorMarca * n * mult, el, "Eclipse", def.intensidade, true) then   -- como tick: nao marca de novo
				FX:FireAllClients({d = m, fase = "reacao", alvo = a, intensidade = def.intensidade, el = el, tipo = "Eclipse"})
				FX:FireAllClients({d = m, hab = "Eclipse", fase = "marca", el = el, alvo = a, marcas = n})
				total += n; nAlvos += 1
			end
		end
	end
	m:SetAttribute("UltimoEclipse", ("alvos=%d marcas=%d raio=%d"):format(nAlvos, total, def.raio))
	-- PATCH_ECLIPSE_AREA: rugido sustentado (laco com a boca aberta) e dano continuo na area enquanto ela existe
	if not def.danoArea then local resto = def.duracao - def.detona; if resto > 0 then task.wait(resto) end; return end
	local tLaco
	task.delay(0.45, function()                                          -- entra no laco ainda com a boca aberta
		if not m.Parent then return end
		tLaco = self:tocar(def.clipeLoop, noAr, {}, function() end, true)
		if tLaco and tPrinc then tPrinc:Stop(0.3) end
	end)
	local t0, ticks, feridos = os.clock(), 0, {}
	while os.clock() - t0 < def.escuro do
		task.wait(def.tickArea)
		if not m.Parent or m:GetAttribute("Incapacitado") then break end            -- dragao derrubado: a area acaba
		ticks += 1
		for _, a in ipairs(self:alvosValidos()) do
			if naEsfera(c, def.raio, a) and self:visivel(c, a) and N.ferir(m, a, def.danoArea * mult, el, "Eclipse", "leve", true) then
				FX:FireAllClients({d = m, fase = "reacao", alvo = a, intensidade = "leve", el = el, tipo = "EclipseArea"})
				feridos[a.Name] = (feridos[a.Name] or 0) + 1
			end
		end
	end
	local fr = {}; for n, k in pairs(feridos) do table.insert(fr, n .. "=" .. k) end
	m:SetAttribute("UltimoEclipseArea", ("ticks=%d %s"):format(ticks, table.concat(fr, " ")))
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "fimRugido", el = el})
	if m.Parent then
		local tFim = self:tocar(def.clipeFim, noAr, {}, function() end)
		if tLaco then tLaco:Stop(0.25) end; if tPrinc then tPrinc:Stop(0.25) end
		task.wait(tFim and def.fimRugido or 0.1)
	end
end]==], [==[-- PATCH_ECLIPSE_VOO (04/11, pedido do usuario): o dragao LEVANTA VOO, ruge, SOLTA o poder no ar e segue rugindo
-- pairando enquanto a area dura; quando o poder comeca a cessar, fecha a boca e POUSA. O combate move o corpo
-- (CorpoElevado: montaria e IA nao disputam o pivo, como na Nevasca). No ar: ganha um pouco de altura e paira.
-- Detonacao das Marcas (danoPorMarca x marcas) e dano continuo da area (danoArea por tickArea) iguais; o centro da
-- area e o chao sob o dragao (o corpo esta no alto). Numeros NAO_APROVADO.
function N:_Eclipse(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "inicio", el = el, noAr = noAr, detona = def.detona, raio = def.raio})
	m:SetAttribute("CorpoElevado", true)
	local P = Enum.AnimationPriority
	local function trilha(nome, camada, laco, prio) local t = self:tocar(nome, camada, {}, function() end, laco); if t then t.Priority = prio end; return t end
	local tDec = not noAr and trilha("Decolagem", false, false, P.Action2) or nil
	local tPairar
	task.delay(noAr and 0 or 0.8, function() if m.Parent then tPairar = trilha("Pairar", false, true, P.Action2); if tDec then tDec:Stop(0.3) end end end)
	local tRugido; task.delay(def.rugir or 1.2, function() if m.Parent then tRugido = trilha("Rugido_Combate", true, false, P.Action3) end end)
	local H = noAr and (def.subidaAr or 10) or (def.altura or 24)
	local s0, s1 = noAr and 0 or 0.2, noAr and 1.0 or 1.5
	local yAtual = 0
	local function subir(k)                                           -- altura do corpo no instante k (decola, paira, pousa)
		local y
		if k < s0 then y = 0 elseif k < s1 then local x = (k - s0) / (s1 - s0); y = H * (1 - (1 - x) ^ 2) else y = H + 0.9 * math.sin((k - s1) * 2.0) end
		return y
	end
	local t0 = os.clock(); local morto = false
	local con = RunService.Heartbeat:Connect(function()
		if not m.Parent then return end
		local y = subir(os.clock() - t0)
		m:PivotTo(m:GetPivot() + Vector3.new(0, y - yAtual, 0)); yAtual = y
	end)
	local function encerrar()                                         -- desce e pousa (no chao) ou estabiliza (no ar)
		con:Disconnect()
		if m.Parent and not noAr then
			local y0 = yAtual; local d0 = os.clock(); local desce = def.descida or 1.1; local pousou = false
			while m.Parent and os.clock() - d0 < desce do
				RunService.Heartbeat:Wait()
				local x = math.min(1, (os.clock() - d0) / desce); local y = y0 * (1 - x * x * (3 - 2 * x))
				m:PivotTo(m:GetPivot() + Vector3.new(0, y - yAtual, 0)); yAtual = y
				if not pousou and x > 0.55 then pousou = true; local tp = trilha("Pouso", false, false, P.Action2); if tPairar then tPairar:Stop(0.25) end; if tp then task.delay(0.5, function() tp:Stop(0.3) end) end end
			end
			if m.Parent then m:PivotTo(m:GetPivot() - Vector3.new(0, yAtual, 0)); yAtual = 0 end   -- volta ao chao exato
		end
		if tPairar then tPairar:Stop(0.3) end
		m:SetAttribute("CorpoElevado", nil)
	end
	task.wait(def.detona)
	if not m.Parent or m:GetAttribute("Incapacitado") then FX:FireAllClients({d = m, hab = "Eclipse", fase = "fimRugido", el = el}); encerrar(); return end
	local c = self:centroCorpo() - Vector3.new(0, yAtual, 0)                 -- area no chao sob o dragao
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "detonar", el = el, pos = c, raio = def.raio, duracao = def.escuro})
	local mult = ((m:GetAttribute("DominioAtivo") and Cfg.habilidades.Dominio.multiplicadorDano) or 1) * Passivas.multiplicadorOfensivo(m)
	local total, nAlvos = 0, 0
	for _, a in ipairs(self:alvosValidos()) do
		if naEsfera(c, def.raio, a) and self:visivel(c, a) then
			local n = Passivas.consumirMarcas(m, a)                         -- zera ANTES do dano: o multiplicador da Marca nao soma
			if n > 0 and N.ferir(m, a, def.danoPorMarca * n * mult, el, "Eclipse", def.intensidade, true) then   -- como tick: nao marca de novo
				FX:FireAllClients({d = m, fase = "reacao", alvo = a, intensidade = def.intensidade, el = el, tipo = "Eclipse"})
				FX:FireAllClients({d = m, hab = "Eclipse", fase = "marca", el = el, alvo = a, marcas = n})
				total += n; nAlvos += 1
			end
		end
	end
	m:SetAttribute("UltimoEclipse", ("alvos=%d marcas=%d raio=%d"):format(nAlvos, total, def.raio))
	-- rugido sustentado (laco aereo com a boca aberta) e dano continuo na area enquanto ela existe
	local tLaco
	task.delay(0.45, function() if m.Parent then tLaco = trilha(def.clipeLoop, true, true, P.Action3); if tLaco and tRugido then tRugido:Stop(0.3) end end end)
	local ta, ticks, feridos = os.clock(), 0, {}
	while os.clock() - ta < def.escuro do
		task.wait(def.tickArea)
		if not m.Parent or m:GetAttribute("Incapacitado") then morto = true; break end   -- dragao derrubado: a area acaba
		ticks += 1
		for _, a in ipairs(self:alvosValidos()) do
			if naEsfera(c, def.raio, a) and self:visivel(c, a) and N.ferir(m, a, def.danoArea * mult, el, "Eclipse", "leve", true) then
				FX:FireAllClients({d = m, fase = "reacao", alvo = a, intensidade = "leve", el = el, tipo = "EclipseArea"})
				feridos[a.Name] = (feridos[a.Name] or 0) + 1
			end
		end
	end
	local fr = {}; for n, k in pairs(feridos) do table.insert(fr, n .. "=" .. k) end
	m:SetAttribute("UltimoEclipseArea", ("ticks=%d %s"):format(ticks, table.concat(fr, " ")))
	-- o poder comeca a cessar: fecha a boca e pousa
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "fimRugido", el = el})
	if m.Parent and not morto then
		local tFim = trilha(def.clipeFim, true, false, P.Action3)
		if tLaco then tLaco:Stop(0.25) end; if tRugido then tRugido:Stop(0.25) end
		if tFim then task.delay(def.fimRugido, function() tFim:Stop(0.3) end) end
	end
	encerrar()
end]==])
  assert(loadstring(src), "Nucleo.luau nao compila"); table.insert(novos, {s, src}) end
if not SS:FindFirstChild("Backup_Eclipse_Voo_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Eclipse_Voo_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f.Parent = SS end
for _, x in ipairs(novos) do x[1].Source = x[2] end
return "aplicado: ConfigCombate + Nucleo (" .. #novos .. "); backup ServerStorage.Backup_Eclipse_Voo_2026-11-04"
