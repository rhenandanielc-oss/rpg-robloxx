-- studio_combate_silverwing.luau (rodar no Studio, modo Edit, DEPOIS de trocar o modelo pelo Silverwing_Drake3c)
-- Ataques fisicos e cauda viva do Silverwing: liga os clipes proprios de combate, versoes no ar (_Camada), garra e
-- mordida terrestres para o cavaleiro, sons dos golpes (so com acerto o impacto forte), respiracao ocasional e
-- batidas de asa casadas com os clipes de 4 batidas. Cada troca confere o trecho original (assert) antes de editar.
local SSS, RS, SP = game:GetService("ServerScriptService"), game:GetService("ReplicatedStorage"), game:GetService("StarterPlayer")
local log = {}
-- tudo ou nada: as trocas acontecem numa copia do texto; so no fim (todas conferidas) os scripts sao gravados
local copia, ordem = {}, {}
local function trocar(script, velho, novo, rotulo)
	if not copia[script] then copia[script] = script.Source; table.insert(ordem, script) end
	local src = copia[script]
	local a, b = src:find(velho, 1, true)
	assert(a, "NADA FOI ALTERADO - trecho nao encontrado em " .. script:GetFullName() .. ": " .. rotulo)
	copia[script] = src:sub(1, a - 1) .. novo .. src:sub(b + 1)
	table.insert(log, script.Name .. ": " .. rotulo)
end

-- 1) Nucleo: clipe "_Camada" proprio (versao no ar) antes do clipe de solo; FX com 'acertou' e preparo dos golpes
local N = SSS.Combate_Dragao.Nucleo
trocar(N, [[		local a = self.apelidos[nome]
		kfs = pasta:FindFirstChild((self.apelidos.prefixo or "") .. nome) or (a and pasta:FindFirstChild(a))]],
[[		-- ordem: clipe proprio da camada (no ar) -> apelido da camada -> clipe proprio -> apelido
		local px = self.apelidos.prefixo or ""
		local ac, a = self.apelidos[chave], self.apelidos[nome]
		kfs = (chave ~= nome and (pasta:FindFirstChild(px .. chave) or (ac and pasta:FindFirstChild(ac))))
			or pasta:FindFirstChild(px .. nome) or (a and pasta:FindFirstChild(a))]], "clipe da camada no ar")
trocar(N, [[			self:aplicar(alvos, def.dano, "Mordida", def.intensidade, el)
			FX:FireAllClients({d = self.m, hab = "Mordida", fase = "impacto", pos = b, el = el})]],
[[			self:aplicar(alvos, def.dano, "Mordida", def.intensidade, el)
			FX:FireAllClients({d = self.m, hab = "Mordida", fase = "impacto", pos = b, el = el, acertou = #alvos > 0})]], "mordida acertou")
trocar(N, [[	local esquerda = math.random() < 0.5
	local t = self:tocar(esquerda and def.clipe or def.clipeD, false, {Impacto = 0.72}, function(n)]],
[[	local esquerda = math.random() < 0.5
	FX:FireAllClients({d = self.m, hab = "Garra", fase = "preparo", el = el})
	local t = self:tocar(esquerda and def.clipe or def.clipeD, false, {Impacto = 0.72}, function(n)]], "garra preparo")
trocar(N, [[			self:aplicar(alvos, def.dano, "Garra", def.intensidade, el)
			FX:FireAllClients({d = self.m, hab = "Garra", fase = "impacto", pos = pe, el = el})]],
[[			self:aplicar(alvos, def.dano, "Garra", def.intensidade, el)
			FX:FireAllClients({d = self.m, hab = "Garra", fase = "impacto", pos = pe, el = el, acertou = #alvos > 0})]], "garra acertou")
trocar(N, [[	local fim = false
	local t = self:tocar("Ataque_Mordida", noAr, {Impacto = 0.74}, function(n)]],
[[	FX:FireAllClients({d = self.m, hab = "Mordida", fase = "preparo", el = el})
	local t = self:tocar("Ataque_Mordida", noAr, {Impacto = 0.74}, function(n)]], "mordida preparo")

-- 2) Montaria (servidor): durante garra/mordida/cauda o dragao freia (patas do golpe nao patinam)
local MS = SSS.Montaria_Dragao_Servidor
trocar(MS, [[	local fixo = ataque == "Ruptura" or ataque == "Tempestade" or m:GetAttribute("Incapacitado")]],
[[	local fixo = ataque == "Ruptura" or ataque == "Tempestade" or ataque == "Garra" or ataque == "Mordida" or ataque == "Cauda"
		or m:GetAttribute("Incapacitado")]], "freia nos golpes fisicos")

-- 3) Controles: M1 no chao = mordida terrestre (no ar continua a Mordida Aerea); R = garra (alterna lados no servidor)
local CM = RS.Montaria_Dragoes.ConfigMontaria
trocar(CM, [[mordida = {Enum.UserInputType.MouseButton1, Enum.KeyCode.ButtonL1}]],
[[mordida = {Enum.UserInputType.MouseButton1, Enum.KeyCode.ButtonL1}, garra = {Enum.KeyCode.R, Enum.KeyCode.ButtonR1}]], "tecla da garra")
local MC = SP.StarterPlayerScripts.Montaria_Cliente
trocar(MC, [[			if st == Enum.UserInputState.Begin and m and m:GetAttribute("MontariaModo") == "voo" then Comando:FireServer("mordida") end]],
[[			if st == Enum.UserInputState.Begin and m then
				if m:GetAttribute("MontariaModo") == "voo" then Comando:FireServer("mordida")
				elseif m:GetAttribute("MontariaModo") == "chao" and Pedido then Pedido:FireServer(m, "usar", "Mordida", workspace.CurrentCamera.CFrame.LookVector) end
			end]], "M1 no chao = mordida")
trocar(MC, [[		end, C.mordida, "Mordida")]],
[[		end, C.mordida, "Mordida")
		if C.garra then
			acao("Mont_Garra", function(st)
				if st == Enum.UserInputState.Begin and m and m:GetAttribute("MontariaModo") == "chao" and Pedido then
					Pedido:FireServer(m, "usar", "Garra", workspace.CurrentCamera.CFrame.LookVector)
				end
				return Enum.ContextActionResult.Sink
			end, C.garra, "Garra")
		end]], "acao da garra")
trocar(MC, [["Mont_Elemento", "Mont_Mordida"}]], [["Mont_Elemento", "Mont_Mordida", "Mont_Garra"}]], "desligar garra")
trocar(MC, [[M1 (clique): mordida aer]], [[R: garra (no chao) | M1: mordida (no chao: terrestre; no ar: mordida aer]], "dica M1/R")

-- 4) Sons: novos arquivos (Pro Sound Effects) e volumes moderados
local SC = RS.Montaria_Dragoes.SonsConfig
trocar(SC, [[	rugido = id(9113985445),                         -- Creature Roar Deep Throaty Growls 2 (SFX)]],
[[	rugido = id(9113985445),                         -- Creature Roar Deep Throaty Growls 2 (SFX)
	respiro = id(9113971531), respiroVolume = 0.35, respiroTom = {0.55, 0.7},   -- Creature Growls Lion 4: Deep Quiet Breathy (SFX)
	respiroIntervalo = {7, 15},                      -- segundos entre respiracoes audiveis (parado/andando), nunca regular
	esforco = id(9125467848), esforcoVolume = 0.55,  -- Creature Growls Lion Deep Guttural Rumbling (SFX): esforco curto
	garra = id(9119228132), garraVolume = 0.9,       -- Slow Whoosh Beefy Airy Pass By 5 (SFX): deslocamento do golpe
	impacto = id(9118633669), impactoCorte = 0.3,    -- Rock Impacts Deep Crunchy: so quando ACERTA
	maxSimultaneos = 6,                              -- por dragao (evita sobreposicao)]], "sons novos")

local SD = SP.StarterPlayerScripts.SonsDragao_Cliente
-- clipes de voo com 4 batidas por laco (cauda/patas lentas): batida em (i + 0,55) / 4
trocar(SD, [[local ASAS = {Voo = {0.55}, Voo_AFK = {0.55}, Pairar = {0.55}, Pairar_AFK = {0.55}, Subida = {0.5}, Subida_AFK = {0.5},]],
[[local Q4 = {0.1375, 0.3875, 0.6375, 0.8875}; local Q4s = {0.125, 0.375, 0.625, 0.875}
local ASAS = {Voo = Q4, Voo_AFK = Q4, Pairar = Q4, Pairar_AFK = Q4, Subida = Q4s, Subida_AFK = Q4s,]], "batidas 4 por clipe")
-- limite de sons simultaneos por dragao
trocar(SD, [[local function tocar(pai, sid, vol, tom, corte)
	if not (pai and pai.Parent) then return end]],
[[local ativos = {}
local function tocar(pai, sid, vol, tom, corte)
	if not (pai and pai.Parent) then return end
	if (ativos[pai] or 0) >= (Cfg.maxSimultaneos or 6) then return end
	ativos[pai] = (ativos[pai] or 0) + 1
	task.delay(corte or 2.5, function() ativos[pai] = math.max(0, (ativos[pai] or 1) - 1) end)]], "limite simultaneos")
-- golpes fisicos: preparo (deslocamento/esforco), fechamento da boca sempre, impacto forte so com acerto
trocar(SD, [[		elseif h == "Mordida" and f == "impacto" then tocar(pp, sorteia(Cfg.mordida), 1.4, faixa(Cfg.mordidaTom))]],
[[		elseif h == "Mordida" and f == "preparo" then
			task.delay(0.5, function() tocar(pp, Cfg.garra, 0.5, 1.2) end)
		elseif h == "Mordida" and f == "impacto" then
			tocar(pp, sorteia(Cfg.mordida), e.acertou and 1.2 or 0.7, faixa(Cfg.mordidaTom))
			if e.acertou then tocar(pp, Cfg.impacto, 0.7, 0.8, Cfg.impactoCorte) end
		elseif h == "Garra" and f == "preparo" then
			if math.random() < 0.35 then tocar(pp, Cfg.esforco, Cfg.esforcoVolume, 0.8 + math.random() * 0.15, 1.0) end
			task.delay(0.45, function() tocar(pp, Cfg.garra, Cfg.garraVolume, 0.85 + math.random() * 0.1) end)
		elseif h == "Garra" and f == "impacto" and e.acertou then tocar(pp, Cfg.impacto, 0.8, 0.9, Cfg.impactoCorte)
		elseif h == "Cauda" and f == "impacto" then tocar(pp, Cfg.garra, 1.0, 0.7)]], "sons garra/mordida")
-- respiracao: so parado/andando no chao, perto da camera, intervalo irregular; mais frequente logo apos correr/voar
trocar(SD, [[-- Mordida Aerea: avanco (whoosh) no inicio, mordida no fechar da boca, estalo forte se acertar]],
[[-- respiracao grave e discreta (intervalos irregulares); depois de correr/voar fica mais frequente por ~20 s
local esforcoAte, proxRespiro = {}, {}
task.spawn(function()
	while true do
		task.wait(1)
		for _, m in ipairs(dragoes()) do
			local pp = m.PrimaryPart
			if (pp.Position - cam.CFrame.Position).Magnitude > 120 then continue end
			local modo = m:GetAttribute("MontariaModo")
			if modo == "voo" or m:GetAttribute("NoAr") or m:GetAttribute("EmAtaque") then esforcoAte[m] = os.clock() + 20; continue end
			local cansado = (esforcoAte[m] or 0) > os.clock()
			local prox = proxRespiro[m]
			if not prox then
				local a, b = Cfg.respiroIntervalo[1], Cfg.respiroIntervalo[2]
				proxRespiro[m] = os.clock() + (cansado and a * 0.5 or a) + math.random() * (b - a)
			elseif os.clock() >= prox then
				proxRespiro[m] = nil
				tocar(pp, Cfg.respiro, Cfg.respiroVolume * (cansado and 1.4 or 1), faixa(Cfg.respiroTom), 1.8)
			end
		end
	end
end)

-- Mordida Aerea: avanco (whoosh) no inicio, mordida no fechar da boca, estalo forte se acertar]], "respiracao")

-- 5) Apelidos: os clipes de combate agora sao proprios (achados pelo prefixo); no ar a mordida basica usa a aerea
local AP = RS.Animacoes_Silverwing.Apelidos
trocar(AP, [[	-- habilidades do combate (TEMPORARIO, sem clipes proprios ainda): poses mais proximas do gesto]],
[[	-- combate: clipes PROPRIOS (Silverwing_Ataque_*, Sopro_*, Arremetida, Tempestade_*, Ruptura_Vulcanica, Rugido_Combate
	-- e versoes _Camada no ar) sao achados pelo prefixo; os apelidos abaixo so valem se faltar um clipe
	Ataque_Mordida_Camada = c("Mordida_Aerea"),]], "apelidos combate")
-- copia de seguranca dos fontes originais (1 versao recuperavel) e gravacao
local bk = game:GetService("ServerStorage"):FindFirstChild("Backup_Scripts_Combate_Silverwing") or Instance.new("Folder")
bk.Name = "Backup_Scripts_Combate_Silverwing"; bk.Parent = game:GetService("ServerStorage")
for _, s in ipairs(ordem) do
	local v = bk:FindFirstChild(s.Name) or Instance.new("StringValue"); v.Name = s.Name; v.Value = s.Source; v.Parent = bk
	s.Source = copia[s]
end
return table.concat(log, "\n")
