-- patch_kit_gelo.luau (Studio, modo Edit) — KIT OFICIAL DO DRAGAO GLACIAL (usuario 02/11): passivas Sangue Glacial e
-- Frostbite; ativas Sopro Glacial (slot 1), Rajadas de Gelo (slot 2, no lugar da investida), Zero Absoluto (slot 3) e
-- Nevasca Ancestral (slot 4, ultimate). Os slots/teclas/HUD/IA continuam os mesmos ids (Sopro, Arremetida, Tempestade,
-- Coracao); ConfigCombate.kitForma traduz o slot para a habilidade real da forma. O Dragao das Montanhas nao muda.
-- Numeros PROVISORIOS (NAO_APROVADO). Tudo-ou-nada: confere todos os trechos, compila e guarda backup antes de gravar.
-- O modulo de efeitos (VFXGelo) vem de vfx_gelo.luau (servido no mesmo endereco).
local RS, SS, SSS, SP = game:GetService("ReplicatedStorage"), game:GetService("ServerStorage"), game:GetService("ServerScriptService"), game:GetService("StarterPlayer")
local H = game:GetService("HttpService")
local alvos = {
	CC = SSS.Combate_Dragao.ConfigCombate, PA = SSS.Combate_Dragao.Passivas, NU = SSS.Combate_Dragao.Nucleo,
	MS = SSS.Montaria_Dragao_Servidor, MC = SP.StarterPlayerScripts.Montaria_Cliente, CM = RS.Montaria_Dragoes.ConfigMontaria,
	VF = RS.Combate_Dragoes.VFXCombate, SC = SP.StarterPlayerScripts.SonsDragao_Cliente,
}
if alvos.NU.Source:find("PATCH_KIT_GELO", 1, true) then return "ja aplicado" end
local novo = {}; for k, s in pairs(alvos) do novo[k] = s.Source:gsub("\r\n", "\n") end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true); assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end

-- ===== ConfigCombate ==============================================================================================
troca("CC", [=[	elementosForma = {Montanhas = {"Fogo"}},
	habilidadesForma = {Montanhas = {"Sopro", "Arremetida", "Tempestade", "Coracao"}},
	passivasForma = {Montanhas = {"SangueDeMagma", "Burning"}},]=], [=[	elementosForma = {Montanhas = {"Fogo"}, Glacial = {"Gelo"}},
	habilidadesForma = {Montanhas = {"Sopro", "Arremetida", "Tempestade", "Coracao"}, Glacial = {"Sopro", "Arremetida", "Tempestade", "Coracao"}},
	passivasForma = {Montanhas = {"SangueDeMagma", "Burning"}, Glacial = {"SangueGlacial", "Frostbite"}},
	-- PATCH_KIT_GELO (oficial 02/11): o slot (tecla/HUD/IA) continua com o mesmo id; a forma decide a habilidade real
	kitForma = {Glacial = {Sopro = "SoproGlacial", Arremetida = "Rajadas", Tempestade = "ZeroAbsoluto", Coracao = "Nevasca"}},]=])
troca("CC", [=[		Dominio = {recarga = 30, energia = 35, duracao = 12, multiplicadorDano = 1.0},]=], [=[		Dominio = {recarga = 30, energia = 35, duracao = 12, multiplicadorDano = 1.0},
		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) =====
		-- Sopro Glacial: jato continuo de frio (mesma mecanica do sopro segurado), dano por tick + Frostbite por tick
		SoproGlacial = {recarga = 10, energia = 25, emissao = 1.8, tick = 0.3, elemental = true, emissaoMax = 5, energiaSeg = 8,
			emAtaque = "Sopro", clipes = "Sopro_Glacial", frost = 6,
			porElemento = {Gelo = {forma = "cone", alcance = 105, angulo = 11, dano = 6}}},
		-- Rajadas de Gelo: 4 lancas rapidas pela boca, cada uma com mira propria (cursor do cavaleiro ou alvo da IA com
		-- antecipacao); hitbox FINA (mais dificil de acertar), mais dano e muito Frostbite por acerto
		Rajadas = {recarga = 11, energia = 30, elemental = true, intensidade = "moderado", clipe = "Rajadas_Gelo", duracao = 2.4,
			disparos = {0.72, 1.08, 1.44, 1.80}, velocidade = 240, alcance = 230, raio = 3.2, dano = 22, frost = 24, coneMin = 0.25},
		-- Zero Absoluto: tensao e descarga; onda circular que se expande pelo chao (1 acerto por alvo) e deixa uma zona
		-- congelada que segue acumulando Frostbite em quem fica dentro
		ZeroAbsoluto = {recarga = 15, energia = 35, elemental = true, intensidade = "pesado", clipe = "Zero_Absoluto", duracao = 2.8,
			emissao = 1.06, raio = 64, velOnda = 95, alturaFaixa = 18, alturaMaxAr = 45, dano = 24, frost = 50,
			zona = 4.0, zonaRaio = 52, zonaTick = 0.5, zonaFrost = 6},
		-- Nevasca Ancestral (ultimate): sobe (solo) ou ganha altitude (ar), ruge, corpo inteiro brilha, tempestade de
		-- fragmentos em ondas ao redor; no solo desce e pousa no fim
		Nevasca = {recarga = 28, energia = 55, elemental = true, intensidade = "pesado", clipe = "Nevasca_Ancestral", duracao = 5.6,
			elevacaoSolo = 26, subidaAr = 14, subida = {0.5, 1.6}, descida = {4.7, 5.4}, rugido = 1.75,
			ondas = {2.2, 2.9, 3.6, 4.3}, raio = 95, dano = 30, fatorOnda = 0.55, frost = 30},]=])
troca("CC", [=[			imuneAtributo = "ImuneQueimadura"},                -- alvo com este atributo = true nao queima
	},]=], [=[			imuneAtributo = "ImuneQueimadura"},                -- alvo com este atributo = true nao queima
		-- Sangue Glacial (Glacial): frio constante — resistencia a Gelo, imune ao proprio Frostbite; em combate os olhos
		-- e o interior da boca brilham (atributo SangueGlacialFim, so visual)
		SangueGlacial = {resistenciaGelo = 0.3, combateJanela = 6},
		-- Frostbite (Glacial): acumulo 0..100 por alvo; lentidao e vulnerabilidade crescem com o acumulo; em 100 o alvo
		-- CONGELA por instantes e volta a 45 (com janela em que acumula mais devagar, sem travar em cadeia); sem novos
		-- acertos o acumulo cai. basico = acumulo dos ataques basicos (mordida/garra/cauda/mordida aerea)
		Frostbite = {max = 100, basico = 10, decaiApos = 2.0, decaiPorSeg = 12, lentidaoMax = 0.55, vulnerabMax = 0.25,
			congelaDur = 1.4, aposCongelar = 45, imuneCongelarPor = 4, imuneAtributo = "ImuneFrostbite"},
	},]=])

-- ===== Passivas ===================================================================================================
troca("PA", [=[		end
	end
end)
return P]=], [=[		end
	end
end)

-- ===== PATCH_KIT_GELO: Sangue Glacial e Frostbite (Dragao Glacial, oficial 02/11) ==================================
function P.resistenciaGelo(alvo)
	if P.tem(alvo, "SangueGlacial") then return Cfg.passivas.SangueGlacial.resistenciaGelo end
	return math.clamp(alvo:GetAttribute("ResistenciaGelo") or 0, 0, 1)
end
function P.marcarCombate(m)                                          -- Sangue Glacial: brilho frio em combate (visual)
	if m and P.tem(m, "SangueGlacial") then m:SetAttribute("SangueGlacialFim", agora() + Cfg.passivas.SangueGlacial.combateJanela) end
end
local frost = {}                                                    -- [alvo] = {v, ultimo, congeladoAte, imuneAte, ws, pulo}
P.frost = frost
function P.vulnerabilidade(alvo)
	local f = frost[alvo]; if not f then return 1 end
	local F = Cfg.passivas.Frostbite; return 1 + F.vulnerabMax * f.v / F.max
end
local function aplicarLentidao(alvo, f)
	local h = alvo:FindFirstChildOfClass("Humanoid"); if not h then return end
	local F = Cfg.passivas.Frostbite
	if not f.ws then f.ws = h.WalkSpeed; f.pulo = h.UseJumpPower and h.JumpPower or h.JumpHeight end
	local congelado = (f.congeladoAte or 0) > os.clock()
	h.WalkSpeed = congelado and 0 or f.ws * (1 - F.lentidaoMax * f.v / F.max)
	if h.UseJumpPower then h.JumpPower = congelado and 0 or f.pulo else h.JumpHeight = congelado and 0 or f.pulo end
end
local function soltarFrost(alvo)
	local f = frost[alvo]; frost[alvo] = nil; if not f then return end
	local h = alvo.Parent and alvo:FindFirstChildOfClass("Humanoid")
	if h and f.ws then h.WalkSpeed = f.ws; if h.UseJumpPower then h.JumpPower = f.pulo else h.JumpHeight = f.pulo end end
	if alvo.Parent then alvo:SetAttribute("Frostbite", nil); alvo:SetAttribute("Congelado", nil) end
end
function P.aplicarFrostbite(fonte, alvo, qtd)
	if not (fonte and alvo and alvo.Parent) or not qtd or qtd <= 0 or not P.tem(fonte, "Frostbite") then return false end
	local F = Cfg.passivas.Frostbite
	if alvo:GetAttribute(F.imuneAtributo) or P.tem(alvo, "SangueGlacial") then return false end
	local f = frost[alvo]; if not f then f = {v = 0}; frost[alvo] = f end
	if (f.imuneAte or 0) > os.clock() then qtd *= 0.4 end            -- logo apos descongelar acumula mais devagar
	f.v = math.min(F.max, f.v + qtd); f.ultimo = os.clock()
	if f.v >= F.max and (f.imuneAte or 0) <= os.clock() then
		f.congeladoAte = os.clock() + F.congelaDur; f.imuneAte = f.congeladoAte + F.imuneCongelarPor
		alvo:SetAttribute("Congelado", agora() + F.congelaDur)
		if N then N.FX:FireAllClients({d = fonte, hab = "Frostbite", fase = "congelar", alvo = alvo, duracao = F.congelaDur, el = "Gelo"}) end
	end
	alvo:SetAttribute("Frostbite", math.floor(f.v))
	aplicarLentidao(alvo, f)
	return true
end
task.spawn(function()
	while true do
		local dt = task.wait(0.2)
		local F = Cfg.passivas.Frostbite; local t = os.clock()
		for alvo, f in pairs(frost) do
			if not alvo.Parent then frost[alvo] = nil
			else
				if f.congeladoAte and t >= f.congeladoAte then              -- descongela: volta a um acumulo medio
					f.congeladoAte = nil; f.v = math.min(f.v, F.aposCongelar); f.ultimo = t; alvo:SetAttribute("Congelado", nil)
				end
				if not f.congeladoAte and t - (f.ultimo or 0) > F.decaiApos then f.v -= F.decaiPorSeg * dt end
				local h = alvo:FindFirstChildOfClass("Humanoid")
				if f.v <= 0 or (h and h.Health <= 0) then soltarFrost(alvo)
				else alvo:SetAttribute("Frostbite", math.floor(f.v)); aplicarLentidao(alvo, f) end
			end
		end
	end
end)
return P]=])

-- ===== Nucleo =====================================================================================================
troca("NU", [=[function N:temHabilidade(hab)]=], [=[-- PATCH_KIT_GELO: slot (tecla/HUD/IA) -> habilidade real da forma (Glacial: Sopro Glacial, Rajadas, Zero Absoluto, Nevasca)
function N:real(hab) local k = Cfg.kitForma and Cfg.kitForma[self.forma]; return (k and k[hab]) or hab end
function N:temHabilidade(hab)]=])
troca("NU", [=[	local def = Cfg.habilidades[hab] or Cfg.basicos[hab]; if not def then return false, "habilidade inexistente" end]=],
	[=[	local def = Cfg.habilidades[self:real(hab)] or Cfg.basicos[hab]; if not def then return false, "habilidade inexistente" end]=])
troca("NU", [=[	self.m:SetAttribute("EmAtaque", hab)
	task.spawn(function()
		local okE, err = pcall(self["_" .. hab], self, def, el, noAr, op)]=], [=[	self.m:SetAttribute("EmAtaque", def.emAtaque or self:real(hab))
	Passivas.marcarCombate(self.m)
	task.spawn(function()
		local okE, err = pcall(self["_" .. self:real(hab)], self, def, el, noAr, op)]=])
troca("NU", [=[		if el == "Fogo" then dano *= (1 - Passivas.resistenciaFogo(a)) end
		if dano > 0 then h:TakeDamage(dano); ok = true end
	end
	if ok and not ehTick then
		FX:FireAllClients({d = fonte, fase = "reacao", alvo = a, intensidade = intensidade, el = el, tipo = tipo})
		Passivas.aplicarBurning(fonte, a)
	end
	return ok
end
function N:aplicar(alvos, dano, tipo, intensidade, el)]=], [=[		if el == "Fogo" then dano *= (1 - Passivas.resistenciaFogo(a)) end
		if el == "Gelo" then dano *= (1 - Passivas.resistenciaGelo(a)) end
		dano *= Passivas.vulnerabilidade(a)                             -- Frostbite: alvo muito congelado sofre mais
		if dano > 0 then h:TakeDamage(dano); ok = true end
	end
	if ok and not ehTick then
		FX:FireAllClients({d = fonte, fase = "reacao", alvo = a, intensidade = intensidade, el = el, tipo = tipo})
		Passivas.aplicarBurning(fonte, a)
		Passivas.aplicarFrostbite(fonte, a, frost or Cfg.passivas.Frostbite.basico)   -- Glacial: todo acerto acumula
		Passivas.marcarCombate(fonte)
	end
	return ok
end
function N:aplicar(alvos, dano, tipo, intensidade, el, frost)]=])
troca("NU", [=[function N.ferir(fonte, a, dano, el, tipo, intensidade, ehTick)]=], [=[function N.ferir(fonte, a, dano, el, tipo, intensidade, ehTick, frost)]=])
troca("NU", [=[		if N.ferir(self.m, a, dano * mult, el, tipo, intensidade) then n += 1 end]=], [=[		if N.ferir(self.m, a, dano * mult, el, tipo, intensidade, nil, frost) then n += 1 end]=])
troca("NU", [=[	elseif el == "Fogo" then dano *= (1 - Passivas.resistenciaFogo(g)) end
	if dano <= 0 then return false end]=], [=[	elseif el == "Fogo" then dano *= (1 - Passivas.resistenciaFogo(g)) end
	if el == "Gelo" then dano *= (1 - Passivas.resistenciaGelo(g)) end
	dano *= Passivas.vulnerabilidade(g)
	if dano <= 0 then return false end]=])
-- Sopro: clipes por forma (Sopro_Glacial_*) e Frostbite por tick
troca("NU", [=[	local t0 = self:tocar("Sopro_Inicio", noAr, {Emissao = 1.05}, function() end)
	task.wait(1.05)
	local loop = self:clipe("Sopro_Loop", noAr); if loop then loop.Looped = true; loop:Play(0.1) end]=], [=[	local px = def.clipes or "Sopro"
	local t0 = self:tocar(px .. "_Inicio", noAr, {Emissao = 1.05}, function() end)
	task.wait(1.05)
	local loop = self:clipe(px .. "_Loop", noAr); if loop then loop.Looped = true; loop:Play(0.1) end]=])
troca("NU", [=[			if #alvos > 0 then self:aplicar(alvos, e.dano, "Sopro", "leve", el) end]=], [=[			if #alvos > 0 then self:aplicar(alvos, e.dano, "Sopro", "leve", el, def.frost) end]=])
troca("NU", [=[	local tf = self:tocar("Sopro_Fim", noAr, {}, function() end); task.wait(0.8)]=], [=[	local tf = self:tocar(px .. "_Fim", noAr, {}, function() end); task.wait(0.8)]=])
troca("NU", [=[-- energia
task.spawn(function()]=], [=[-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11) ===============================================================
function N:_SoproGlacial(def, el, noAr, op) return self:_Sopro(def, "Gelo", noAr, op) end

-- Rajadas de Gelo: 4 lancas, cada uma com a mira do momento do disparo (cursor do cavaleiro, que o cliente segue
-- enviando, ou alvo da IA com antecipacao), dentro do cone do pescoco. Voo simulado no servidor quadro a quadro:
-- segmento percorrido x alvos (hitbox fina) e x mundo (impacto no chao/parede). 1 acerto por lanca.
function N:voarLanca(def, el, de, dir, i)
	local pos, perc = de, 0
	local fm = filtroMundo(self)
	while perc < def.alcance and self.m.Parent do
		local dt = RunService.Heartbeat:Wait()
		local passo = math.min(def.velocidade * dt, def.alcance - perc)
		for _, a in ipairs(self:alvosValidos()) do
			local p = raiz(a).Position
			local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) * 1.4 or 2.2
			local s = math.clamp((p - pos):Dot(dir), 0, passo)
			if (pos + dir * s - p).Magnitude <= def.raio + extra then
				self:aplicar({a}, def.dano, "Rajadas", def.intensidade, el, def.frost)
				FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "impacto", el = el, pos = pos + dir * s, indice = i, acertou = true})
				return
			end
		end
		local h = workspace:Raycast(pos, dir * passo, fm)
		if h then FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "impacto", el = el, pos = h.Position, normal = h.Normal, indice = i, acertou = false}); return end
		pos += dir * passo; perc += passo
	end
	FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "dissipa", el = el, pos = pos, indice = i})
end
function N:_Rajadas(def, el, noAr, op)
	FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "preparo", el = el})
	self.miraDir = nil
	self:tocar(def.clipe, noAr, {}, function() end)
	local t0 = os.clock()
	for i, ts in ipairs(def.disparos) do
		local espera = ts - (os.clock() - t0); if espera > 0 then task.wait(espera) end
		if not self.m.Parent or self.m:GetAttribute("Incapacitado") then return end
		local b = self:boca(); local f = self:frente()
		local dir
		local md = self.miraDir or op.direcao
		if typeof(md) == "Vector3" and md.Magnitude > 0.1 then dir = md.Unit end
		if op.alvo and raiz(op.alvo) then                                      -- IA: mira com antecipacao do movimento
			local r = raiz(op.alvo); local tv = (r.Position - b).Magnitude / def.velocidade
			dir = ((r.Position + r.AssemblyLinearVelocity * tv) - b).Unit
		end
		dir = dir or f
		local pd = plano(dir)
		if pd.Magnitude < 0.1 or pd.Unit:Dot(f) < def.coneMin then dir = (f + Vector3.new(0, math.clamp(dir.Y, -0.5, 0.4), 0)).Unit end
		dir = Vector3.new(dir.X, math.clamp(dir.Y, -0.8, 0.6), dir.Z).Unit
		FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "disparo", el = el, de = b, dir = dir, vel = def.velocidade, alcance = def.alcance, indice = i})
		task.spawn(function() self:voarLanca(def, el, b, dir, i) end)
	end
	local resto = def.duracao - (os.clock() - t0); if resto > 0.1 then task.wait(resto - 0.1) end
	self.miraDir = nil
end

-- Zero Absoluto: descarga em def.emissao; a onda nasce no chao sob o corpo (no ar, se houver chao ate alturaMaxAr;
-- senao na altura do corpo) e se expande a velOnda ate o raio: 1 acerto por alvo quando a frente da onda passa.
-- Depois a zona congelada segue acumulando Frostbite (sem dano) por def.zona segundos.
function N:_ZeroAbsoluto(def, el, noAr, op)
	FX:FireAllClients({d = self.m, hab = "ZeroAbsoluto", fase = "preparo", el = el, noAr = noAr, emissao = def.emissao})
	self:tocar(def.clipe, noAr, {}, function() end)
	task.wait(def.emissao)
	if not self.m.Parent or self.m:GetAttribute("Incapacitado") then return end
	local c = self:centroCorpo()
	local h = workspace:Raycast(c + Vector3.new(0, 5, 0), Vector3.new(0, -(def.alturaMaxAr + 25), 0), filtroMundo(self))
	local centro = h and h.Position or c
	FX:FireAllClients({d = self.m, hab = "ZeroAbsoluto", fase = "onda", el = el, centro = centro, normal = h and h.Normal, noChao = h ~= nil,
		raio = def.raio, vel = def.velOnda, zona = def.zona, zonaRaio = def.zonaRaio})
	local atingidos, r = {}, 0
	while r < def.raio and self.m.Parent do
		local dt = RunService.Heartbeat:Wait()
		r = math.min(def.raio, r + def.velOnda * dt)
		for _, a in ipairs(self:alvosValidos()) do
			if not atingidos[a] then
				local p = raiz(a).Position
				local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) * 1.6 or 2
				if plano(p - centro).Magnitude <= r + extra and math.abs(p.Y - centro.Y) <= def.alturaFaixa + extra then
					atingidos[a] = true
					self:aplicar({a}, def.dano, "ZeroAbsoluto", def.intensidade, el, def.frost)
				end
			end
		end
	end
	if h then
		local m = self.m
		task.spawn(function()
			local fim = os.clock() + def.zona
			while os.clock() < fim and m.Parent do
				task.wait(def.zonaTick)
				for _, a in ipairs(self:alvosValidos()) do
					local p = raiz(a).Position
					if plano(p - centro).Magnitude <= def.zonaRaio and math.abs(p.Y - centro.Y) <= 14 then Passivas.aplicarFrostbite(m, a, def.zonaFrost) end
				end
			end
		end)
	end
	local resto = def.duracao - def.emissao - def.raio / def.velOnda; if resto > 0.05 then task.wait(resto) end
end

-- Nevasca Ancestral (ultimate): o combate move o corpo (CorpoElevado: montaria e IA nao disputam o pivo). Solo: sobe
-- elevacaoSolo e no fim desce de volta; ar: ganha subidaAr e estabiliza. Ondas de fragmentos em def.ondas (1a cheia,
-- seguintes x fatorOnda), esfera em volta do tronco com linha de visao.
function N:_Nevasca(def, el, noAr, op)
	FX:FireAllClients({d = self.m, hab = "Nevasca", fase = "inicio", el = el, noAr = noAr, duracao = def.duracao, rugido = def.rugido,
		ondas = def.ondas, raio = def.raio, subida = def.subida})
	self:tocar(def.clipe, noAr, {}, function() end)
	self.m:SetAttribute("CorpoElevado", true)
	local t0 = os.clock()
	local H = noAr and def.subidaAr or def.elevacaoSolo
	local s0, s1, d0, d1 = def.subida[1], def.subida[2], def.descida[1], def.descida[2]
	local feitas, yAtual = {}, 0
	local function onda(i)
		local c = self:centroCorpo(); local lista = {}
		for _, a in ipairs(self:alvosValidos()) do if naEsfera(c, def.raio, a) and self:visivel(c, a) then table.insert(lista, a) end end
		self:aplicar(lista, def.dano * (i == 1 and 1 or def.fatorOnda), "Nevasca", def.intensidade, el, def.frost)
		FX:FireAllClients({d = self.m, hab = "Nevasca", fase = "onda", el = el, indice = i, pos = c, raio = def.raio})
	end
	while self.m.Parent and not self.m:GetAttribute("Incapacitado") do
		RunService.Heartbeat:Wait()
		local k = os.clock() - t0
		if k >= def.duracao then break end
		local y
		if k < s0 then y = 0
		elseif k < s1 then local x = (k - s0) / (s1 - s0); y = H * (1 - (1 - x) ^ 2)
		elseif noAr or k < d0 then y = H + 0.8 * math.sin((k - s1) * 2.2)
		elseif k < d1 then local x = (k - d0) / (d1 - d0); y = (H + 0.8 * math.sin((d0 - s1) * 2.2)) * (1 - x * x * (3 - 2 * x))
		else y = 0 end
		self.m:PivotTo(self.m:GetPivot() + Vector3.new(0, y - yAtual, 0)); yAtual = y
		for i, to in ipairs(def.ondas) do if not feitas[i] and k >= to then feitas[i] = true; onda(i) end end
	end
	if not noAr and self.m.Parent then self.m:PivotTo(self.m:GetPivot() - Vector3.new(0, yAtual, 0)) end   -- volta ao chao exato
	self.m:SetAttribute("CorpoElevado", nil)
	FX:FireAllClients({d = self.m, hab = "Nevasca", fase = "fim", el = el})
end

-- energia
task.spawn(function()]=])
troca("NU", [=[-- Nucleo (ModuleScript, ServerScriptService.Combate_Dragao) — combate do Dragao das Montanhas, AUTORIDADE DO SERVIDOR.]=],
	[=[-- Nucleo (ModuleScript, ServerScriptService.Combate_Dragao) — combate do Dragao das Montanhas, AUTORIDADE DO SERVIDOR.
-- PATCH_KIT_GELO (02/11): kit oficial do Dragao Glacial (Sopro Glacial, Rajadas, Zero Absoluto, Nevasca; Frostbite).]=])

-- ===== Montaria (servidor): poderes do Glacial seguram o corpo; Nevasca no ar estabiliza o voo =====================
troca("MS", [=[	local fixo = ataque == "Ruptura" or ataque == "Coracao" or ataque == "Tempestade" or ataque == "Garra" or ataque == "Mordida" or ataque == "Cauda"]=],
	[=[	local fixo = ataque == "Ruptura" or ataque == "Coracao" or ataque == "Tempestade" or ataque == "Garra" or ataque == "Mordida" or ataque == "Cauda"
		or ataque == "Rajadas" or ataque == "ZeroAbsoluto" or ataque == "Nevasca"            -- PATCH_KIT_GELO]=])
troca("MS", [=[	if ataque == "Arremetida" then M.vel = m:GetAttribute("VelArremetida") or M.vel; return end    -- o Nucleo move; a velocidade volta no fim]=],
	[=[	if ataque == "Arremetida" then M.vel = m:GetAttribute("VelArremetida") or M.vel; return end    -- o Nucleo move; a velocidade volta no fim
	if m:GetAttribute("CorpoElevado") then M.vel = 0; M.vyH = 0; return end                   -- PATCH_KIT_GELO: Nevasca no ar (o Nucleo move)]=])

-- ===== ConfigMontaria: rotulos/passivas/mira viva por forma =========================================================
troca("CM", [=[		passivas = {SangueDeMagma = "Sangue de Magma", Burning = "Burning"},   -- exibicao no HUD (lista vem do atributo Passivas)]=],
	[=[		passivas = {SangueDeMagma = "Sangue de Magma", Burning = "Burning", SangueGlacial = "Sangue Glacial", Frostbite = "Frostbite"},   -- exibicao no HUD (lista vem do atributo Passivas)
		-- PATCH_KIT_GELO: rotulo de cada slot por forma, e slots que seguem mandando a mira enquanto a habilidade roda (s)
		rotulosForma = {Glacial = {Sopro = "Sopro Glacial", Arremetida = "Rajadas", Tempestade = "Zero Absol.", Coracao = "Nevasca"}},
		dicaForma = {Glacial = " | segure 1: Sopro Glacial | 2 Rajadas de Gelo (mire) | 3 Zero Absoluto | 4 Nevasca Ancestral"},
		miraVivaForma = {Glacial = {Arremetida = 2.6}},
		corEnergiaForma = {Glacial = Color3.fromRGB(150, 215, 255)},]=])

-- ===== Montaria (cliente): rotulos e mira viva =======================================================================
troca("MC", [=[	rotulo(f, {Text = h[4] or h[1], Position = UDim2.fromOffset(0, 24), Size = UDim2.new(1, 0, 0, 18), TextXAlignment = Enum.TextXAlignment.Center, TextSize = 12})
	local tr = rotulo(f, {Text = "", Position = UDim2.fromOffset(0, 42), Size = UDim2.new(1, 0, 0, 18), TextXAlignment = Enum.TextXAlignment.Center, TextSize = 13})
	slots[h[1]] = {cob = cob, txt = tr}]=], [=[	local nm = rotulo(f, {Text = h[4] or h[1], Position = UDim2.fromOffset(0, 24), Size = UDim2.new(1, 0, 0, 18), TextXAlignment = Enum.TextXAlignment.Center, TextSize = 12})
	local tr = rotulo(f, {Text = "", Position = UDim2.fromOffset(0, 42), Size = UDim2.new(1, 0, 0, 18), TextXAlignment = Enum.TextXAlignment.Center, TextSize = 13})
	slots[h[1]] = {cob = cob, txt = tr, nome = nm, padrao = h[4] or h[1]}]=])
troca("MC", [=[local soproSegurado = false                                           -- sopro com a tecla segurada (mira viva)]=],
	[=[local soproSegurado = false                                           -- sopro com a tecla segurada (mira viva)
local miraAte = 0                                                      -- PATCH_KIT_GELO: habilidade com mira viva (Rajadas)]=])
troca("MC", [=[				Pedido:FireServer(m, "usar", h[1], dirMira())                     -- direcao da BOCA ate o ponto do cursor
				if h[1] == "Sopro" then soproSegurado = true end]=], [=[				Pedido:FireServer(m, "usar", h[1], dirMira())                     -- direcao da BOCA ate o ponto do cursor
				if h[1] == "Sopro" then soproSegurado = true end
				local mv = C.miraVivaForma and C.miraVivaForma[m:GetAttribute("FormaRegional") or ""]
				if mv and mv[h[1]] then miraAte = os.clock() + mv[h[1]] end]=])
troca("MC", [=[		if soproSegurado and Pedido then Pedido:FireServer(m, "mira", nil, dm) end]=],
	[=[		if (soproSegurado or os.clock() < miraAte) and Pedido then Pedido:FireServer(m, "mira", nil, dm) end]=])
troca("MC", [=[	if m:GetAttribute("HabilidadesForma") ~= nil then
		dica.Text = dica.Text:gsub(" | segure 1: sopro continuo %(mira no cursor%) | 2 Arremetida | 3 Tempestade | 4 Coracao Infernal", ""):gsub(" | 1%-4 habilidades", "")
	end]=], [=[	if m:GetAttribute("HabilidadesForma") ~= nil then
		dica.Text = dica.Text:gsub(" | segure 1: sopro continuo %(mira no cursor%) | 2 Arremetida | 3 Tempestade | 4 Coracao Infernal", ""):gsub(" | 1%-4 habilidades", "")
	end
	-- PATCH_KIT_GELO: nomes dos slots, dica e cor da energia da forma
	local fr = m:GetAttribute("FormaRegional") or ""
	local rf = C.rotulosForma and C.rotulosForma[fr]
	for id, s in pairs(slots) do if s.nome then s.nome.Text = (rf and rf[id]) or s.padrao end end
	if C.dicaForma and C.dicaForma[fr] then dica.Text ..= C.dicaForma[fr] end
	energia.BackgroundColor3 = (C.corEnergiaForma and C.corEnergiaForma[fr]) or Color3.fromRGB(255, 150, 60)]=])

-- ===== VFXCombate: tudo que e Gelo vai para o VFXGelo ===============================================================
troca("VF", [=[	if d.fase == "reacao" then reacao(d.alvo, el, d.intensidade); return end
	if d.fase == "lancamento" then lancamento(d); return end              -- empurrao (Tempestade/Ruptura): so o personagem atingido]=],
	[=[	-- PATCH_KIT_GELO: efeitos do Gelo (kit do Glacial, reacoes, Frostbite) no modulo proprio
	if el == "Gelo" or d.hab == "Frostbite" then
		local G = script.Parent:FindFirstChild("VFXGelo")
		if G then return require(G).evento(d, fatorLOD(m:GetPivot().Position)) end
	end
	if d.fase == "reacao" then reacao(d.alvo, el, d.intensidade); return end
	if d.fase == "lancamento" then lancamento(d); return end              -- empurrao (Tempestade/Ruptura): so o personagem atingido]=])

-- ===== Sons: o jato de Gelo tem som proprio no VFXGelo (nao tocar o "ar" generico por cima) ===========================
troca("SC", [=[			else tocar(pp, Cfg.ar, 1.3, 0.8) end]=], [=[			elseif el ~= "Gelo" then tocar(pp, Cfg.ar, 1.3, 0.8) end              -- PATCH_KIT_GELO: Gelo toca no VFXGelo]=])

-- ===== compila tudo, backup, grava =================================================================================
for k in pairs(alvos) do local f, e = loadstring(novo[k]); assert(f, k .. " nao compila: " .. tostring(e)) end
local srcG = H:GetAsync("http://127.0.0.1:8766/vfx_gelo.luau?x=" .. os.clock())
local fG, eG = loadstring(srcG); assert(fG, "VFXGelo nao compila: " .. tostring(eG))
local bk = SS:FindFirstChild("Backup_Kit_Gelo_2026-11-02")
if not bk then
	bk = Instance.new("Folder"); bk.Name = "Backup_Kit_Gelo_2026-11-02"
	for k, s in pairs(alvos) do local c = s:Clone(); c.Name = k .. "__" .. s.Name; if c:IsA("BaseScript") then c.Enabled = false end; c.Parent = bk end
	bk.Parent = SS
end
for k, s in pairs(alvos) do s.Source = novo[k] end
local g = RS.Combate_Dragoes:FindFirstChild("VFXGelo") or Instance.new("ModuleScript"); g.Name = "VFXGelo"; g.Source = srcG; g.Parent = RS.Combate_Dragoes
-- modelos: kit ativo (slots visiveis), elemento Gelo
for _, n in ipairs({"Glacial", "Glacial_Guardiao"}) do
	local m = workspace:FindFirstChild(n)
	if m then m:SetAttribute("HabilidadesForma", "Sopro,Arremetida,Tempestade,Coracao"); m:SetAttribute("ElementoNato", "Gelo"); m:SetAttribute("ElementoAtivo", "Gelo") end
end
return "aplicado"
