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
local function profMin() return C_.topo + CFG.Submersao.folga_topo + CFG.Submersao.folga_fundo end
local function yEspreita(sup) return sup - C_.olhos + C_.pivo end            -- olhos/narinas na superficie
local function ySubmerso(sup) return sup - CFG.Submersao.folga_topo - C_.topo + C_.pivo end
local function naAltura(cf, y) return CFrame.new(cf.X, y, cf.Z) * cf.Rotation end
local function centro(a) local r = a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart; return r and r.Position end

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
	est.poder = nil; est.fase = nil
	modelo:SetAttribute("Submerso", false); modelo:SetAttribute("Movendo", false)
	if modelo:IsDescendantOf(workspace) then T.tocar(est.naAgua and "Crocodilo_Espreita" or "Crocodilo_Repouso", 0.2) end
	return motivo
end

local function iniciar(poder, manterPivo)
	if est.poder then return false end
	if est.mov then est.mov += 1 end                          -- para uma volta suave pendente
	if not manterPivo and (modelo:GetPivot().Position - BASE.Position).Magnitude > 0.001 then modelo:PivotTo(BASE) end
	est.poder = poder; est.fase = nil; est.gen += 1; est.t0 = os.clock(); M.log = {}
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
function M.agarrao(alvo, cena)
	local g = iniciar("Agarrao"); if not g then return "ocupado" end
	if not alvoValido(alvo) then M.cancelar("alvo_invalido"); return "alvo_invalido" end
	local clipe
	if cena == "agua" then
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
		if resultado ~= "acerto" then M.cancelar(resultado); return end
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
	est.alvo = alvoAntes; if est.alvo then vigiaAlvo(g) end
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
				local passo = math.min(C.velocidade * dt, C.distancia - andou)
				cf = naAltura(cf + cf.LookVector * passo, ySubmerso(s2)); modelo:PivotTo(cf); andou += passo
				BASE = naAltura(cf, yEspreita(s2))                   -- cancelar aqui = sobe no lugar, sem voltar
				if andou >= C.distancia then break end
			end
			if est.gen ~= g then return end
			modelo:SetAttribute("Movendo", false)
			log("DESLOCAMENTO: %.1f studs em %.2f s (%.1f studs/s), energia %.0f -> %.0f, parou por %s", andou, t, andou / math.max(t, 0.01), C.energia_teste, energia, motivo)
		end,
		function()                                                   -- emersao adiante
			local cf = modelo:GetPivot(); local s3 = medirAgua(cf.Position) or sup
			T.tocar("Crocodilo_Emersao", 0.2); moverPivo(naAltura(cf, yEspreita(s3)), C.subida)
			task.wait(C.subida * 0.5); modelo:SetAttribute("Submerso", false)
			fx("ondulacao", Vector3.new(cf.X, s3, cf.Z) + cf.LookVector * 10, 1.0)
			BASE = naAltura(cf, yEspreita(s3))
			log("EMERSAO adiante (%.1f studs do inicio)", (Vector3.new(cf.X, 0, cf.Z) - Vector3.new(cf0.X, 0, cf0.Z)).Magnitude)
			task.wait(C.subida * 0.5 + 0.6)
		end})
	return "iniciado"
end

-- ================================================================ Cauda de Mare
-- antecipacao -> varredura (evento impacto_cauda: bonecos no raio da ponta da cauda sao empurrados) -> recuperacao
function M.caudaDeMare()
	local g = iniciar("CaudaDeMare"); if not g then return "ocupado" end
	local f = T.tocar("Crocodilo_CaudaDeMare", 0.1)
	table.insert(est.cons, f:GetMarkerReachedSignal("impacto_cauda"):Connect(function()
		if est.gen ~= g then return end
		local ponta = osso("Cauda6").TransformedWorldCFrame.Position
		anelAgua(Vector3.new(ponta.X, CFG.AlturaAgua, ponta.Z), Color3.fromRGB(120, 190, 220))
		local acertos = 0
		for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
			if alvoValido(a) and not a:GetAttribute("Agarrado") then
				local d = (centro(a) - ponta) * Vector3.new(1, 0, 1)
				if d.Magnitude <= CFG.Cauda.raio then
					local dir = d.Magnitude > 0.1 and d.Unit or Vector3.new(-1, 0, 0)
					a:PivotTo(a:GetPivot() + dir * CFG.Cauda.empurrao)
					a:FindFirstChildOfClass("Humanoid"):TakeDamage(CFG.Cauda.dano); acertos += 1
					log("IMPACTO: %s a %.1f da ponta, empurrado %.0f", a.Name, d.Magnitude, CFG.Cauda.empurrao)
				end
			end
		end
		if acertos == 0 then log("IMPACTO: nenhum boneco no raio %.0f", CFG.Cauda.raio) end
	end))
	table.insert(est.cons, f.Stopped:Connect(function() if est.gen == g then M.cancelar("fim_cauda") end end))
	return "iniciado"
end

function M.estado() return {poder = est.poder, fase = est.fase, alvo = est.alvo and est.alvo.Name or nil, naAgua = est.naAgua} end
return M
