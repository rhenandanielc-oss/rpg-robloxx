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

function M.cancelar(motivo)
	motivo = motivo or "cancelado"
	if not est.poder then return "nada ativo" end
	log("FIM %s: %s", est.poder, motivo)
	est.gen += 1; limparCons(); soltar(motivo)
	T.parar()
	modelo:PivotTo(PIVO0)                                   -- profundidade/posicao de teste voltam ao normal
	est.poder = nil; est.fase = nil
	if modelo:IsDescendantOf(workspace) then T.tocar("Crocodilo_Repouso", 0.2) end
	return motivo
end

local function iniciar(poder)
	if est.poder then return false end
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
		modelo:PivotTo(PIVO0 * CFrame.new(0, -CFG.Submersao.profundidade, 0)); clipe = "Crocodilo_BoteAquatico"
	else
		clipe = (PIVO0:PointToObjectSpace(centro(alvo)).X < 0) and "Crocodilo_MordidaLateralEsquerda" or "Crocodilo_MordidaLateralDireita"
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
	local g = iniciar("Giro"); if not g then return "ocupado" end
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

-- ================================================================ Submersao
-- agua: Mergulho (desce a profundidade de teste) -> Espreita/AproximacaoSubmersa (laco) -> Emersao (sobe). Terra:
-- Deitar -> DescansoDeitado (postura baixa em cobertura) -> Levantar. Sempre visivel (sem transparencia).
function M.submersao(meio, mover)
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
	local function descer(dy, dur)
		local t0 = os.clock(); local base = modelo:GetPivot()
		while os.clock() - t0 < dur do
			if est.gen ~= g then return end
			local u = (os.clock() - t0) / dur; modelo:PivotTo(base * CFrame.new(0, -dy * (u * u * (3 - 2 * u)), 0)); RS.Heartbeat:Wait()
		end
		if est.gen == g then modelo:PivotTo(base * CFrame.new(0, -dy, 0)) end
	end
	if meio == "terra" then
		seq({function() local f = T.tocar("Crocodilo_Deitar", 0.2); log("TERRA: deitar (postura baixa)"); f.Stopped:Wait() end,
			function() T.tocar("Crocodilo_DescansoDeitado", 0.2); log("escondido em cobertura (visivel)"); task.wait(C.tempo) end,
			function() if est.gen ~= g then return end local f = T.tocar("Crocodilo_Levantar", 0.2); log("levanta"); f.Stopped:Wait() end})
	else
		seq({function() T.tocar("Crocodilo_Mergulho", 0.2); log("AGUA: mergulho (profundidade de teste %.1f)", C.profundidade); descer(C.profundidade, C.descida) end,
			function() T.tocar(mover and "Crocodilo_AproximacaoSubmersa" or "Crocodilo_Espreita", 0.3); log("submerso: %s", mover and "aproximacao" or "espreita"); task.wait(C.tempo) end,
			function() if est.gen ~= g then return end T.tocar("Crocodilo_Emersao", 0.2); log("emersao"); descer(-C.profundidade, C.descida) end})
	end
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

function M.estado() return {poder = est.poder, fase = est.fase, alvo = est.alvo and est.alvo.Name or nil} end
return M
