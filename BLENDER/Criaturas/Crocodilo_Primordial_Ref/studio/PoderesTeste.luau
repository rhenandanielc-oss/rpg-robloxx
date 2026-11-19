-- PoderesTeste (ModuleScript em ServerStorage.Crocodilo_Piloto) - PROTOTIPOS [PROPOSTA] dos 4 poderes historicos do
-- Crocodilo Primordial (Mordida de Agarrao, Giro Predatorio, Submersao, Cauda de Mare), SO NA ARENA DE TESTE.
-- Kit oficial, elemento, passiva e regra do agarrao PvP: PENDENTES. Tudo roda no SERVIDOR (alvo, alcance, estado,
-- efeitos e cancelamento); o agarrao so aceita bonecos com o atributo BonecoTeste. Um poder por vez (estado unico).
-- Saida limpa em: fim normal, cancelar(), alvo removido/morto, crocodilo removido. M.log guarda os eventos (evidencia).
local RS = game:GetService("RunService")
local PASTA = game.ServerStorage.Crocodilo_Piloto
local CFG = require(PASTA.ConfigPoderes_Teste)
local T = require(PASTA.TestePlayCrocodilo)
local M = {log = {}}
local modelo = workspace.Teste_Crocodilo.Crocodilo_Primordial
local PIVO0 = modelo:GetPivot()
local BASE = PIVO0                     -- P4: posicao/altura de repouso atual (M.posicionar e o fim da Submersao mudam)
local RepS = game:GetService("ReplicatedStorage")
local FX = RepS:FindFirstChild("Crocodilo_FX") or Instance.new("RemoteEvent")      -- efeitos SO visuais no cliente
FX.Name = "Crocodilo_FX"; FX.Parent = RepS
local function fx(tipo, ...) FX:FireAllClients(tipo, ...) end
local est = {poder = nil, alvo = nil, cons = {}, gen = 0, t0 = 0}

local function log(...)
	local s = string.format("%.2f ", os.clock() - est.t0) .. string.format(...)
	table.insert(M.log, s); print("[PoderesTeste] " .. s)
end
local function osso(n) return modelo:FindFirstChild(n, true) end
local function limparCons() for _, c in ipairs(est.cons) do c:Disconnect() end; est.cons = {} end
local function alvoValido(a)
	if not a or not a.Parent or not a:IsDescendantOf(workspace) then return false end
	if CFG.SoBonecos and not a:GetAttribute("BonecoTeste") then return false end
	local h = a:FindFirstChildOfClass("Humanoid"); return h ~= nil and h.Health > 0
end
-- 16/11 (P3): o pivo do crocodilo muda de altura sempre por transicao suave (antes: PivotTo direto = salto de 2,4)
local function moverPivo(destino, dur)
	est.mov = (est.mov or 0) + 1; local tok = est.mov
	if dur <= 0 or not modelo:IsDescendantOf(workspace) then modelo:PivotTo(destino); return end
	local ini = modelo:GetPivot(); local t0 = os.clock()
	task.spawn(function()
		while est.mov == tok do
			local u = math.min(1, (os.clock() - t0) / dur); u = u * u * (3 - 2 * u)
			modelo:PivotTo(ini:Lerp(destino, u))
			if u >= 1 then break end
			RS.Heartbeat:Wait()
		end
	end)
end
-- ================================================================ P4: agua REAL (Terrain Water) medida no servidor
-- superficie = 1o impacto com agua; fundo = 1o solido ignorando a agua. A placa Agua_Teste (vidro) nao conta como agua.
local function medirAgua(pos)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude
	p.FilterDescendantsInstances = {modelo, workspace.Teste_Crocodilo:FindFirstChild("Arena")}
	local o = Vector3.new(pos.X, pos.Y + 60, pos.Z); local d = Vector3.new(0, -240, 0)
	local r1 = workspace:Raycast(o, d, p); p.IgnoreWater = true; local r2 = workspace:Raycast(o, d, p)
	local fundo = r2 and r2.Position.Y or -math.huge
	if r1 and r1.Material == Enum.Material.Water then return r1.Position.Y, fundo end
	return nil, fundo
end
local C_ = CFG.Corpo
local function montado() return modelo:GetAttribute("Montado") == true end      -- P4b: com cavaleiro afunda mais
local function extraMont() return montado() and CFG.Submersao.extra_montado or 0 end
local function profMin() return C_.topo + CFG.Submersao.folga_topo + extraMont() + CFG.Submersao.folga_fundo end
local function yEspreita(sup) return sup - C_.olhos + C_.pivo end            -- olhos/narinas na superficie
local function ySubmerso(sup) return sup - CFG.Submersao.folga_topo - extraMont() - C_.topo + C_.pivo end
-- P4b: presa a frente (so bonecos de teste): distancia da cabeca e angulo com a direcao do crocodilo
local function presaAFrente(cf)
	local cab = cf.Position + cf.LookVector * C_.cabeca
	local melhor, dm = nil, CFG.Submersao.deteccao
	for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
		if a:GetAttribute("BonecoTeste") and a.Parent and a:FindFirstChildOfClass("Humanoid") and a:FindFirstChildOfClass("Humanoid").Health > 0 then
			local c = (a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart); local v = c and (c.Position - cab)
			if v then
				local plano = Vector3.new(v.X, 0, v.Z)
				local ang = plano.Magnitude > 0.1 and math.deg(math.acos(math.clamp(plano.Unit:Dot(Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z).Unit), -1, 1))) or 0
				if plano.Magnitude <= dm and ang <= CFG.Submersao.cone then melhor, dm = a, plano.Magnitude end
			end
		end
	end
	return melhor, dm
end
local function naAltura(cf, y) return CFrame.new(cf.X, y, cf.Z) * cf.Rotation end
local function centro(a) local r = a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart; return r and r.Position end

-- O2 (17/11): o SERVIDOR diz para onde os olhos olham (atributo AlvoOlhar, Vector3; nil = o cliente escolhe sozinho).
-- So visual: o OlhosCrocodilo_Cliente gira os globos. Atualiza a 10 Hz (nao a cada quadro) para poupar rede.
-- Emboscada = presa detectada; Agarrao = alvo ate o contato e o alvo preso; Giro = alvo preso; Giro de Emboscada = pouso.
local function olharPara(p) modelo:SetAttribute("AlvoOlhar", p) end
local function seguirOlhar(g, fonte)                   -- fonte() -> Vector3 ou nil; para sozinho no fim do poder
	local acum = 1
	olharPara(fonte())
	table.insert(est.cons, RS.Heartbeat:Connect(function(dt)
		if est.gen ~= g then return end
		acum += dt; if acum < 0.1 then return end; acum = 0
		olharPara(fonte())
	end))
end
local function olharAlvo(a) return function() local p = a and a.Parent and centro(a); return p and p + Vector3.new(0, 1, 0) end end

-- solta o alvo (sempre seguro de chamar): volta ao chao no ponto atual, marca liberado
local function soltar(motivo)
	local a = est.alvo; est.alvo = nil
	if a and a.Parent then
		local p = centro(a)
		if p then a:PivotTo(CFrame.new(Vector3.new(p.X, 2.5, p.Z))) end
		a:SetAttribute("Agarrado", false)
		log("alvo %s solto (%s)", a.Name, motivo)
	end
end

-- P4: coloca o crocodilo num ponto (cf = posicao e direcao); na agua flutua na altura de espreita (se couber), senao apoia no fundo
function M.posicionar(cf)
	if est.poder then M.cancelar("reposicionado") end
	local sup, fundo = medirAgua(cf.Position)
	local y = fundo + C_.pivo
	if sup and sup - fundo >= C_.olhos then y = yEspreita(sup) end
	est.naAgua = sup ~= nil and (sup - fundo) > 1
	BASE = naAltura(cf, y); modelo:PivotTo(BASE)
	T.tocar(est.naAgua and "Crocodilo_Espreita" or "Crocodilo_Repouso", 0.2)
	return string.format("%s prof %.1f", est.naAgua and "agua" or "terra", sup and (sup - fundo) or 0)
end
function M.medir(pos) return medirAgua(pos or modelo:GetPivot().Position) end

function M.cancelar(motivo)
	motivo = motivo or "cancelado"
	if not est.poder then return "nada ativo" end
	log("FIM %s: %s", est.poder, motivo)
	est.gen += 1; limparCons(); soltar(motivo)
	T.parar()
	local dy = (modelo:GetPivot().Position - BASE.Position).Magnitude
	moverPivo(BASE, dy > 0.05 and 0.4 or 0)               -- volta a altura normal sem salto
	--                                   -- profundidade/posicao de teste voltam ao normal
	est.poder = nil; est.fase = nil
	modelo:SetAttribute("Submerso", false); modelo:SetAttribute("Movendo", false); modelo:SetAttribute("Giro", false); modelo:SetAttribute("CaudaVarre", nil)
	olharPara(nil)                                        -- O2: devolve o olhar ao cliente
	if modelo:IsDescendantOf(workspace) then T.tocar(est.naAgua and "Crocodilo_Espreita" or "Crocodilo_Repouso", 0.2) end
	return motivo
end

local function iniciar(poder, manterPivo)
	if est.poder then return false end
	if est.mov then est.mov += 1 end                          -- para uma volta suave pendente
	if not manterPivo and (modelo:GetPivot().Position - BASE.Position).Magnitude > 0.001 then modelo:PivotTo(BASE) end
	est.poder = poder; est.fase = nil; est.gen += 1
	if not manterPivo then est.t0 = os.clock(); M.log = {} end     -- encadeado: o log continua
	log("INICIO %s", poder)
	-- crocodilo removido: solta tudo
	table.insert(est.cons, modelo.AncestryChanged:Connect(function()
		if not modelo:IsDescendantOf(workspace) then M.cancelar("crocodilo_removido") end
	end))
	return est.gen
end
local function vigiaAlvo(g)
	table.insert(est.cons, RS.Heartbeat:Connect(function()
		if est.gen ~= g or not est.alvo then return end
		if not alvoValido(est.alvo) then M.cancelar("alvo_removido_ou_derrotado"); return end
		-- o alvo acompanha a mandibula no encaixe medido no contato (gira junto no Giro)
		est.alvo:PivotTo(osso("Mandibula").TransformedWorldCFrame * est.rel)
	end))
end

-- ================================================================ Mordida de Agarrao
-- aproximacao (terra: MordidaLateral do lado do alvo; agua: desce a profundidade de teste e da o BoteAquatico; a Mordida
-- basica fica separada) -> contato no evento fecha_boca (alcance medido no servidor da PONTA DOS DENTES ao centro do
-- alvo) -> sustentacao (SegurarPresa / SegurarPresaAgua) -> SoltarPresa (marcador solta libera; cancelamento/remocao soltam na hora)
local function nadarAdiante(g, v0, dur, motivo)       -- P4b: errou o bote = continua nadando e desacelera, sem travar
	local atual
	local function tocarSe(nome) if atual ~= nome then atual = nome; T.tocar(nome, 0.3) end end
	tocarSe("Crocodilo_Nado")
	local t = 0
	while est.gen == g and t < dur do
		local dt = RS.Heartbeat:Wait(); if est.gen ~= g then return end; t += dt
		local cf = modelo:GetPivot()
		local function fundoOk(dir) local s2, f2 = medirAgua(cf.Position + dir * CFG.Submersao.olhar_frente); return s2 and s2 - f2 >= C_.olhos, s2 end
		local okF, s2 = fundoOk(cf.LookVector)
		local v = v0 * math.max(0, 1 - t / dur) ^ 1.5                    -- max(0): base negativa ^1,5 = NaN (jogava o modelo no infinito)
		if not okF then                                                       -- beira a frente: vira para o lado com agua
			local okE = fundoOk((cf * CFrame.Angles(0, math.rad(60), 0)).LookVector)
			cf = cf * CFrame.Angles(0, math.rad((okE and 1 or -1) * 75) * dt, 0); v = v * 0.35
			tocarSe(okE and "Crocodilo_CurvaAquaticaEsquerda" or "Crocodilo_CurvaAquaticaDireita")
		else tocarSe("Crocodilo_Nado") end
		local sAqui = medirAgua(cf.Position) or s2 or cf.Y
		local alvoY = yEspreita(sAqui); local yy = cf.Y + (alvoY - cf.Y) * math.min(1, dt * 3)      -- assenta na espreita sem salto
		cf = naAltura(cf + cf.LookVector * v * dt, yy); modelo:PivotTo(cf); BASE = naAltura(cf, alvoY)
	end
	if est.gen == g then M.cancelar(motivo) end
end
function M.agarrao(alvo, cena, opcoes)
	opcoes = opcoes or {}
	local g = iniciar("Agarrao", opcoes.emboscada); if not g then return "ocupado" end
	if not alvoValido(alvo) then M.cancelar("alvo_invalido"); return "alvo_invalido" end
	seguirOlhar(g, function() return olharAlvo(est.alvo or alvo)() end)   -- O2: olha o alvo do bote e, depois, o preso
	local clipe
	if cena == "agua" and opcoes.emboscada then
		-- P4b: vem SUBMERSO da Submersao: sobe rapido ate a espreita e continua avancando (impulso que se apaga no bote)
		local cf = modelo:GetPivot(); local sup = medirAgua(cf.Position) or cf.Y
		local yBote = math.max(yEspreita(sup) - CFG.Submersao.bote_abaixo, (select(2, medirAgua(cf.Position)) or -math.huge) + C_.pivo)
		BASE = naAltura(cf, yBote); moverPivo(BASE, CFG.Submersao.subida_bote); clipe = "Crocodilo_BoteAquatico"
		fx("ondulacao", Vector3.new(cf.X, sup, cf.Z) + cf.LookVector * C_.cabeca, 1.3)
		-- investida: avanca ate parar a ~3 da presa (max 9), desacelerando ate o fecha_boca (0,62 s); sobe com o fundo na beira
		local frente = (centro(alvo) - cf.Position); frente = Vector3.new(frente.X, 0, frente.Z):Dot(Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z).Unit)
		local L = math.clamp(frente - C_.ponta_bote - CFG.Submersao.parar_antes, 0, CFG.Submersao.investida_max)   -- pela ponta dos dentes
		local ini = modelo:GetPivot()
		task.spawn(function()
			local t, D = 0, 0.6
			while est.gen == g and t < D do
				local dt = RS.Heartbeat:Wait(); if est.gen ~= g then return end; t = math.min(D, t + dt)
				local u = 1 - (1 - t / D) ^ 2                                 -- ease-out
				local alvoXZ = ini.Position + ini.LookVector * (L * u)
				local s2, f2 = medirAgua(alvoXZ); s2 = s2 or sup
				local yy = math.max(modelo:GetPivot().Y, f2 + C_.pivo)          -- nunca abaixo do fundo
				modelo:PivotTo(naAltura(ini.Rotation + alvoXZ, yy)); BASE = naAltura(ini.Rotation + alvoXZ, math.max(yEspreita(s2), f2 + C_.pivo))
				est.yBote = yy
			end
		end)
	elseif cena == "agua" then
		-- espreita: so olhos/narinas/cristas fora (0,85 abaixo do nado de teste), afunda na antecipacao do bote
		moverPivo(BASE * CFrame.new(0, -(est.naAgua and 0 or CFG.Agarrao.profundidade_agua), 0), 0.3); clipe = "Crocodilo_BoteAquatico"
	else
		clipe = (BASE:PointToObjectSpace(centro(alvo)).X < 0) and "Crocodilo_MordidaLateralEsquerda" or "Crocodilo_MordidaLateralDireita"
	end
	log("aproximacao: %s (%s)", clipe:sub(11), cena or "terra")
	local f = T.tocar(clipe, 0.1)
	local resultado = "andamento"
	table.insert(est.cons, f:GetMarkerReachedSignal("fecha_boca"):Connect(function()
		if est.gen ~= g then return end
		local ponta = osso("Mandibula").TransformedWorldCFrame * Vector3.new(0, CFG.Agarrao.ponta, 0)   -- +Y do osso = frente
		local d = (ponta - centro(alvo)).Magnitude
		if d <= CFG.Agarrao.alcance and alvoValido(alvo) then
			est.alvo = alvo; alvo:SetAttribute("Agarrado", true)
			est.rel = osso("Mandibula").TransformedWorldCFrame:Inverse() * alvo:GetPivot()
			local h = alvo:FindFirstChildOfClass("Humanoid"); h:TakeDamage(CFG.Agarrao.dano_contato)
			log("CONTATO: agarrou %s (distancia %.2f <= %.2f)", alvo.Name, d, CFG.Agarrao.alcance)
			resultado = "acerto"; vigiaAlvo(g)
		else
			log("ERROU: %s a %.2f (alcance %.2f)", alvo.Name, d, CFG.Agarrao.alcance); resultado = "erro_alcance"
		end
	end))
	table.insert(est.cons, f.Stopped:Connect(function()
		if est.gen ~= g then return end
		if resultado ~= "acerto" then
			if opcoes.emboscada then log("errou: segue nadando"); nadarAdiante(g, CFG.Submersao.velocidade * 0.7, CFG.Submersao.deriva, resultado .. "_seguiu_nadando"); return end
			M.cancelar(resultado); return
		end
		-- 16/11 (P2): sustentacao com clipe proprio (terra SegurarPresa, agua SegurarPresaAgua) no lugar de ArrastarPresa
		local nomeSeg = (cena == "agua") and "Crocodilo_SegurarPresaAgua" or "Crocodilo_SegurarPresa"
		T.tocar(nomeSeg, 0.2); est.fase = "segurando"
		log("SUSTENTACAO: %s", nomeSeg:sub(11))
		local t = 0
		table.insert(est.cons, RS.Heartbeat:Connect(function(dt)
			if est.gen ~= g or not est.alvo or est.fase ~= "segurando" then return end
			if not alvoValido(est.alvo) then M.cancelar("alvo_removido_ou_derrotado"); return end
			t += dt; est.alvo:FindFirstChildOfClass("Humanoid"):TakeDamage(CFG.Agarrao.dano_por_segundo * dt)
			if t < CFG.Agarrao.sustentacao then return end
			-- fim normal: o dano para; SoltarPresa abre a boca e o marcador "solta" libera o boneco
			est.fase = "soltando"
			local fs = T.tocar("Crocodilo_SoltarPresa", 0.15)
			if cena == "agua" then moverPivo(BASE, 0.8) end        -- sobe a superficie enquanto solta
			log("FIM DA SUSTENTACAO (%.2f s): SoltarPresa", t)
			table.insert(est.cons, fs:GetMarkerReachedSignal("solta"):Connect(function()
				if est.gen ~= g then return end
				soltar("marcador_solta"); est.fase = "solto"
			end))
			table.insert(est.cons, fs.Stopped:Connect(function()
				if est.gen == g then M.cancelar("fim_agarrao") end
			end))
		end))
	end))
	return "iniciado"
end

-- ================================================================ Giro Predatorio
-- RolarDaMorte em laco; cada volta (DidLoop) = efeito de teste (anel de agua) + dano no alvo preso, se houver
local function anelAgua(pos, cor)
	local p = Instance.new("Part"); p.Name = "Efeito_Teste_Croc"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false
	p.Shape = Enum.PartType.Cylinder; p.Material = Enum.Material.Neon; p.Color = cor or Color3.fromRGB(150, 210, 230)
	p.Transparency = 0.35; p.Size = Vector3.new(0.2, 3, 3)
	p.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90)); p.Parent = workspace.Teste_Crocodilo
	local ts = game:GetService("TweenService")
	ts:Create(p, TweenInfo.new(0.8), {Size = Vector3.new(0.2, 16, 16), Transparency = 1}):Play()
	game:GetService("Debris"):AddItem(p, 0.9)
end
function M.giro()
	local preso = est.poder == "Agarrao" and est.fase == "segurando" and est.alvo or nil
	if est.poder and not preso then return "ocupado" end
	local alvoAntes = preso
	if preso then est.gen += 1; limparCons(); est.poder = nil end   -- encadeia: o alvo continua preso
	local g = iniciar("Giro", preso ~= nil); if not g then return "ocupado" end   -- encadeado: fica na altura da pegada
	est.alvo = alvoAntes; if est.alvo then vigiaAlvo(g); seguirOlhar(g, function() return olharAlvo(est.alvo)() end) end   -- O2
	local f = T.tocar("Crocodilo_RolarDaMorte", 0.15); local voltas = 0
	log("GIRO comeca (alvo preso: %s)", est.alvo and est.alvo.Name or "nenhum")
	table.insert(est.cons, f.DidLoop:Connect(function()
		if est.gen ~= g then return end
		voltas += 1
		local c = osso("Coluna1").TransformedWorldCFrame.Position
		anelAgua(Vector3.new(c.X, CFG.AlturaAgua, c.Z))
		if est.alvo and alvoValido(est.alvo) then est.alvo:FindFirstChildOfClass("Humanoid"):TakeDamage(CFG.Giro.dano_por_volta) end
		log("volta %d completa (efeito sincronizado no DidLoop)", voltas)
		if voltas >= CFG.Giro.voltas then M.cancelar("fim_giro") end
	end))
	return "iniciado"
end

-- ================================================================ Submersao (P4, 16/11)
-- AGUA REAL (servidor mede superficie e fundo): espreita com olhos/narinas na superficie -> Mergulho (afunda em 0,5 s ate
-- o topo do corpo ficar abaixo da superficie) -> AproximacaoSubmersa deslocando o crocodilo no MUNDO (velocidade de teste,
-- energia por segundo), sempre conferindo a profundidade a frente -> Emersao adiante, de volta a espreita.
-- Raso demais (prof < topo do corpo + folgas): RECUSA clara (nao afunda atravessando o fundo); fica em espreita de
-- superficie. Sem agua real: recusa. TERRA: variante separada de postura baixa (Deitar -> DescansoDeitado -> Levantar).
-- Efeitos (ondulacao, rastro, bolhas) sao so visuais, no cliente (Crocodilo_FX / atributos Submerso e Movendo).
function M.submersao(meio)
	local g = iniciar("Submersao"); if not g then return "ocupado" end
	local C = CFG.Submersao
	local function seq(passos)
		task.spawn(function()
			for _, p in ipairs(passos) do
				if est.gen ~= g then return end
				p()
			end
			if est.gen == g then M.cancelar("fim_submersao") end
		end)
	end
	if meio == "terra" then
		seq({function() local f = T.tocar("Crocodilo_Deitar", 0.2); log("TERRA: deitar (postura baixa)"); f.Stopped:Wait() end,
			function() T.tocar("Crocodilo_DescansoDeitado", 0.2); log("escondido em cobertura (visivel)"); task.wait(C.tempo_terra) end,
			function() if est.gen ~= g then return end local f = T.tocar("Crocodilo_Levantar", 0.2); log("levanta"); f.Stopped:Wait() end})
		return "iniciado"
	end
	local cf0 = modelo:GetPivot()
	local sup, fundo = medirAgua(cf0.Position)
	if not sup then log("RECUSADA: sem agua real aqui"); fx("recusa", cf0.Position, "Sem água"); M.cancelar("sem_agua"); return "sem_agua" end
	local prof = sup - fundo
	if prof < profMin() then
		log("RECUSADA: raso (profundidade %.1f < %.1f necessaria)", prof, profMin())
		fx("recusa", cf0.Position, string.format("Raso demais: %.1f de %.1f", prof, profMin()))
		seq({function() T.tocar("Crocodilo_Espreita", 0.3); task.wait(1.5) end})     -- provisorio: espreita de superficie
		return "raso_insuficiente"
	end
	local energia = C.energia_teste
	seq({
		function()                                                   -- espreita: olhos e narinas na superficie
			T.tocar("Crocodilo_Espreita", 0.3); moverPivo(naAltura(cf0, yEspreita(sup)), 0.4)
			log("ESPREITA (prof %.1f; superficie %.2f, fundo %.2f)", prof, sup, fundo); task.wait(C.espreita)
		end,
		function()                                                   -- mergulho real
			T.tocar("Crocodilo_Mergulho", 0.2); fx("ondulacao", Vector3.new(cf0.X, sup, cf0.Z), 1.0)
			moverPivo(naAltura(modelo:GetPivot(), ySubmerso(sup)), C.descida)
			task.wait(C.descida * 0.6); modelo:SetAttribute("Superficie", sup); modelo:SetAttribute("Submerso", true)
			log("MERGULHO: topo do corpo %.1f abaixo da superficie", C.folga_topo); task.wait(C.descida * 0.6)
		end,
		function()                                                   -- deslocamento submerso no mundo
			T.tocar("Crocodilo_AproximacaoSubmersa", 0.3, C.vel_clipe); modelo:SetAttribute("Movendo", true)
			local andou, t = 0, 0; local motivo = "distancia"
			while est.gen == g do
				local dt = RS.Heartbeat:Wait(); if est.gen ~= g then break end; t += dt   -- cancelado durante a espera: nao move mais
				local cf = modelo:GetPivot(); local frente = cf.Position + cf.LookVector * C.olhar_frente
				local s2, f2 = medirAgua(frente)
				if not s2 or s2 - f2 < profMin() then motivo = "fundo_acaba_a_frente"; break end
				energia -= C.energia_s * dt
				if energia <= 0 then motivo = "sem_energia"; break end
				local presa = presaAFrente(cf)
				if presa then motivo = "presa_detectada"; est.presa = presa; est.presaDist = select(2, presaAFrente(cf)); olharPara(olharAlvo(presa)()); break end   -- O2: fixa a presa
				local passo = math.min(C.velocidade * dt, C.distancia - andou)
				cf = naAltura(cf + cf.LookVector * passo, ySubmerso(s2)); modelo:PivotTo(cf); andou += passo
				BASE = naAltura(cf, yEspreita(s2))                   -- cancelar aqui = sobe no lugar, sem voltar
				if andou >= C.distancia then break end
			end
			if est.gen ~= g then return end
			modelo:SetAttribute("Movendo", false)
			log("DESLOCAMENTO: %.1f studs em %.2f s (%.1f studs/s), energia %.0f -> %.0f, parou por %s%s", andou, t, andou / math.max(t, 0.01), C.energia_teste, energia, motivo, montado() and " (MONTADO, +" .. C.extra_montado .. " de fundo)" or "")
			if motivo == "presa_detectada" then                   -- emboscada: sobe rapido e da o bote (encadeia o Agarrao)
				local presa = est.presa; est.presa = nil
				modelo:SetAttribute("Submerso", false)
				est.gen += 1; limparCons(); est.poder = nil; est.fase = nil
				log("EMBOSCADA: %s a frente -> bote", presa.Name)
				M.agarrao(presa, "agua", {emboscada = true, vel = C.velocidade, dist = est.presaDist})
				return
			end
		end,
		function()                                                   -- emersao adiante
			local cf = modelo:GetPivot(); local s3 = medirAgua(cf.Position) or sup
			T.tocar("Crocodilo_Emersao", 0.2); moverPivo(naAltura(cf, yEspreita(s3)), C.subida)
			task.wait(C.subida * 0.5); modelo:SetAttribute("Submerso", false)
			fx("ondulacao", Vector3.new(cf.X, s3, cf.Z) + cf.LookVector * 10, 1.0)
			BASE = naAltura(cf, yEspreita(s3))
			log("EMERSAO adiante (%.1f studs do inicio)", (Vector3.new(cf.X, 0, cf.Z) - Vector3.new(cf0.X, 0, cf0.Z)).Magnitude)
			task.wait(C.subida * 0.5 + 0.6)
			est.emergiuEm = os.clock()                            -- abre a janela do Giro de Emboscada
		end})
	return "iniciado"
end

-- ================================================================ Giro Predatorio de Emboscada (P4, 16/11) [PROPOSTA]
-- Ref. secao 4 / 5.8: sai da agua GIRANDO e cai em terra, dano em area, derruba, silencioso. Janela: ate 1,5 s depois de
-- emergir da Submersao (dano cheio + bonus em alvo distraido); em agua rasa sem Submersao: dano 1,2x sem bonus; fora
-- disso: recusa. Clipes: GiroSaida (impulso) -> RolarDaMorte r2 em laco no ar -> GiroPouso (impacto). Servidor decide
-- janela, trajetoria, area, dano, derrubada e limpeza; o cliente so desenha (agua escorrendo, linhas, impacto).
local function chaoEm(pos)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude; p.IgnoreWater = true
	p.FilterDescendantsInstances = {modelo, workspace.Teste_Crocodilo:FindFirstChild("Arena"), workspace.Teste_Crocodilo:FindFirstChild("Cavaleiro_Teste")}
	local r = workspace:Raycast(Vector3.new(pos.X, pos.Y + 80, pos.Z), Vector3.new(0, -300, 0), p)
	return r and r.Position.Y or 0
end
function M.giroEmboscada()
	if est.poder then return "ocupado" end
	local G = CFG.GiroEmboscada
	local cf0 = modelo:GetPivot(); local sup, fundo = medirAgua(cf0.Position)
	local janela = est.emergiuEm and (os.clock() - est.emergiuEm) <= G.janela
	local modo, mult, bonus
	if janela then modo, mult, bonus = "emboscada", G.mult, G.bonus_distraido
	elseif sup and (sup - fundo) < profMin() then modo, mult, bonus = "raso", G.mult_raso, 1.0
	else
		local motivo = sup and "fora_da_janela" or "fora_da_agua"
		fx("recusa", cf0.Position, sup and "Giro: só até 1,5 s após emergir (ou no raso)" or "Giro: precisa sair da água")
		log("GIRO RECUSADO: %s", motivo); return motivo
	end
	local g = iniciar("GiroEmboscada", true)
	if not janela then est.t0 = os.clock(); M.log = {}; log("INICIO GiroEmboscada (raso)") end
	est.emergiuEm = nil
	-- destino: a frente, pousando onde o chao (com a frente do corpo) estiver; nunca abaixo do chao
	local dist = G.distancia; local alvoXZ = cf0.Position + Vector3.new(cf0.LookVector.X, 0, cf0.LookVector.Z).Unit * dist
	local yPouso = math.max(chaoEm(alvoXZ), chaoEm(alvoXZ + cf0.LookVector * C_.cabeca * 0.6) - 0.6) + C_.pivo
	local destino = naAltura(cf0.Rotation + alvoXZ, yPouso)
	do local cen = destino.Position + destino.LookVector * G.centro_frente; olharPara(Vector3.new(cen.X, chaoEm(cen) + 1, cen.Z)) end   -- O2: olha o pouso
	log("GIRO %s (x%.1f%s): de y %.2f ate (%.1f, %.2f, %.1f), %.0f studs", modo, mult, bonus > 1 and ", +50% em distraido" or "", cf0.Y, destino.X, destino.Y, destino.Z, dist)
	task.spawn(function()
		-- antes: agua ondula e escurece, bolhas sobem (silencioso)
		fx("giro_antes", Vector3.new(cf0.X, sup or cf0.Y, cf0.Z), cf0.LookVector)
		local fs = T.tocar("Crocodilo_GiroSaida", 0.15)
		local tImp = 0; local c1 = fs:GetMarkerReachedSignal("impulso"):Connect(function() tImp = os.clock() end)
		local t0 = os.clock(); while est.gen == g and tImp == 0 and os.clock() - t0 < 1 do RS.Heartbeat:Wait() end
		c1:Disconnect(); if est.gen ~= g then return end
		-- voo girando: RolarDaMorte em laco (1 volta por voo), parabola ate o destino
		modelo:SetAttribute("Giro", true); modelo:SetAttribute("Submerso", false)
		BASE = destino                                        -- cancelado no ar = termina no pouso, nao volta para a agua
		T.tocar("Crocodilo_RolarDaMorte", 0.08, 1.2 / G.voo)
		fx("ondulacao", Vector3.new(cf0.X, sup or cf0.Y, cf0.Z), 1.2)
		local ini = modelo:GetPivot(); local t = 0
		while est.gen == g and t < G.voo do
			local dt = RS.Heartbeat:Wait(); if est.gen ~= g then return end; t = math.min(G.voo, t + dt)
			local u = t / G.voo
			local pos = ini.Position:Lerp(destino.Position, u) + Vector3.new(0, 4 * G.altura * u * (1 - u), 0)
			modelo:PivotTo(ini.Rotation + pos)
		end
		if est.gen ~= g then return end
		-- pouso com peso: impacto em area (servidor), derruba; o cliente mostra o impacto
		BASE = destino; est.naAgua = medirAgua(destino.Position) ~= nil
		local fp = T.tocar("Crocodilo_GiroPouso", 0.05)
		local cen = destino.Position + destino.LookVector * G.centro_frente
		fx("giro_pouso", Vector3.new(cen.X, chaoEm(cen), cen.Z), G.raio, est.naAgua)
		local acertos = 0
		for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
			if alvoValido(a) and not a:GetAttribute("Agarrado") then
				local d = (centro(a) - cen) * Vector3.new(1, 0, 1)
				if d.Magnitude <= G.raio then
					local b = a:GetAttribute("Distraido") and bonus or 1.0
					local dano = G.dano_base * mult * b
					a:FindFirstChildOfClass("Humanoid"):TakeDamage(dano); acertos += 1
					local orig = a:GetPivot(); a:SetAttribute("Derrubado", true)
					a:PivotTo(orig * CFrame.Angles(math.rad(80), 0, 0) - Vector3.new(0, 1.5, 0))
					task.delay(G.derruba, function() if a.Parent then a:PivotTo(orig); a:SetAttribute("Derrubado", false) end end)
					log("IMPACTO: %s a %.1f -> dano %.0f%s, derrubado %.1f s", a.Name, d.Magnitude, dano, b > 1 and " (distraido +50%)" or "", G.derruba)
				end
			end
		end
		if acertos == 0 then log("IMPACTO: ninguem no raio %.0f", G.raio) end
		task.delay(0.6, function() modelo:SetAttribute("Giro", false) end)
		fp.Stopped:Wait()
		if est.gen == g then M.cancelar("fim_giro_emboscada") end
	end)
	return "iniciado"
end

-- ================================================================ Cauda de Mare (P4, 16/11) [PROPOSTA]
-- Agua (CaudaDeMare, boiando) ou terra (CaudaDeMareTerra, patas plantadas). O ACERTO segue a TRAJETORIA REAL da cauda:
-- durante a varredura (0,42-0,75 s do clipe) o servidor amostra os ossos Cauda3..Cauda8 a cada quadro e atinge quem
-- estiver a ate `largura` da linha da cauda (cada boneco uma vez), empurrando no sentido da varredura. Nada e atingido
-- atras/fora do arco percorrido. A cobertura medida (graus do arco da ponta) e comparada com os 360 propostos (ref. 4).
local OSSOS_CAUDA = {"Cauda3", "Cauda4", "Cauda5", "Cauda6", "Cauda7", "Cauda8"}
local function distSeg(p, a, b)
	local ab = b - a; local t = ab.Magnitude > 1e-4 and math.clamp((p - a):Dot(ab) / ab:Dot(ab), 0, 1) or 0
	return (p - (a + ab * t)).Magnitude
end
function M.caudaDeMare()
	local g = iniciar("CaudaDeMare"); if not g then return "ocupado" end
	local K = CFG.Cauda
	local cf0 = modelo:GetPivot(); local sup, fundo = medirAgua(cf0.Position)
	local naAgua = sup ~= nil and (sup - fundo) > 1
	local nivel = naAgua and sup or chaoEm(cf0.Position)
	local f = T.tocar(naAgua and "Crocodilo_CaudaDeMare" or "Crocodilo_CaudaDeMareTerra", 0.1)
	log("CAUDA DE MARE em %s", naAgua and "AGUA (onda maior, empurra mais)" or "TERRA (lama, empurra menos)")
	modelo:SetAttribute("Nivel", nivel); modelo:SetAttribute("CaudaVarre", naAgua and "agua" or "terra")
	local atingidos, angs = {}, {}
	local antPonta
	table.insert(est.cons, RS.Heartbeat:Connect(function()
		if est.gen ~= g then return end
		local tp = f.TimePosition
		if tp < 0.42 or tp > 0.75 then return end
		local pts = {}; for _, n in ipairs(OSSOS_CAUDA) do local b = osso(n); if b then table.insert(pts, b.TransformedWorldCFrame.Position) end end
		local ponta = pts[#pts]; local l = modelo:GetPivot():PointToObjectSpace(ponta)
		table.insert(angs, math.deg(math.atan2(l.X, l.Z)))                   -- 0 = cauda reta para tras
		local dirV = antPonta and (ponta - antPonta) * Vector3.new(1, 0, 1) or Vector3.zero; antPonta = ponta
		for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
			if not atingidos[a] and alvoValido(a) and not a:GetAttribute("Agarrado") then
				local c = centro(a); local c2 = Vector3.new(c.X, 0, c.Z); local d = math.huge
				for i = 1, #pts - 1 do d = math.min(d, distSeg(c2, pts[i] * Vector3.new(1, 0, 1), pts[i + 1] * Vector3.new(1, 0, 1))) end
				if d <= K.largura then
					atingidos[a] = true
					local emp = naAgua and K.empurrao_agua or K.empurrao_terra
					local dir = dirV.Magnitude > 0.01 and dirV.Unit or (c2 - Vector3.new(cf0.X, 0, cf0.Z)).Unit
					a:PivotTo(a:GetPivot() + dir * emp)
					a:FindFirstChildOfClass("Humanoid"):TakeDamage(K.dano)
					log("ACERTO na trajetoria: %s a %.1f da cauda (t=%.2f), dano %d, empurrado %.0f", a.Name, d, tp, K.dano, emp)
				end
			end
		end
	end))
	table.insert(est.cons, f:GetMarkerReachedSignal("impacto_cauda"):Connect(function()
		if est.gen ~= g then return end
		local p = osso("Cauda7").TransformedWorldCFrame.Position
		fx("cauda_impacto", Vector3.new(p.X, nivel, p.Z), naAgua and K.onda_agua or K.onda_terra, naAgua)
	end))
	table.insert(est.cons, f.Stopped:Connect(function()
		if est.gen ~= g then return end
		local a0, a1 = angs[1] or 0, angs[#angs] or 0
		local n = 0; for a in pairs(atingidos) do n += 1 end
		log("COBERTURA REAL: ponta de %.0f a %.0f graus = arco de %.0f graus (proposto: %d); atingidos %d", a0, a1, math.abs(a1 - a0), K.proposto_graus, n)
		M.cancelar("fim_cauda")
	end))
	return "iniciado"
end

-- ================================================================ Escamas Grossas (passiva, P4) [PROPOSTA]
-- Ref. secao 4: -15% de dano fisico. Teste: dois golpes fisicos equivalentes, com e sem a passiva, em terra e na agua.
-- O recuo (empurrao do golpe) e o mesmo com e sem a passiva; muda so com o meio (agua empurra mais). Pulso curto nas
-- escamas no ponto do impacto (cliente), sem escudo permanente.
function M.receberGolpe(dano, ponto, passiva)
	local E = CFG.Escamas
	local final = passiva and dano * (1 - E.reducao) or dano
	local cf = modelo:GetPivot(); local sup, fundo = medirAgua(cf.Position); local naAgua = sup ~= nil and (sup - fundo) > 1
	local recuo = naAgua and E.recuo_agua or E.recuo_terra
	local dir = (cf.Position - ponto) * Vector3.new(1, 0, 1); dir = dir.Magnitude > 0.1 and dir.Unit or -cf.LookVector
	local novo = cf + dir * recuo
	if not est.poder then BASE = novo; moverPivo(novo, 0.22) end
	local vida = (modelo:GetAttribute("VidaTeste") or E.vida) - final; modelo:SetAttribute("VidaTeste", vida)
	if passiva then fx("escamas_pulso", ponto) end
	table.insert(M.log, string.format("GOLPE %s em %s: %.0f -> %.0f de dano (%s), recuo %.1f, vida %.0f", passiva and "COM Escamas" or "SEM Escamas", naAgua and "agua" or "terra", dano, final, passiva and "-15%" or "cheio", recuo, vida))
	print("[PoderesTeste] " .. M.log[#M.log])
	return final, recuo
end

function M.estado() return {poder = est.poder, fase = est.fase, alvo = est.alvo and est.alvo.Name or nil, naAgua = est.naAgua} end
return M
