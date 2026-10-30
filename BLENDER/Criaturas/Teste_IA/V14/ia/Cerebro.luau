-- IA_Dragao/Cerebro — maquina de estados com prioridades para o guardiao selvagem (servidor).
-- Cada decisao vira UMA tarefa (coroutine) com geracao propria: uma tarefa de prioridade maior cancela a atual na
-- hora (defesa do ninho cancela qualquer rotina); rotinas trocam entre si so depois de 'tempoMinEstado'.
-- Estados expostos (atributo "EstadoIA" no modelo): Idle, Observation, Wander, Patrol, Fly, Glide, SearchFood, Eat,
-- SearchWater, Drink, Rest, Sleep, ReturnHome, Investigate, Alert, ReturnToNest, DefendNest, ChaseIntruder, Attack,
-- Recover, Incapacitated.
local Players = game:GetService("Players")
local CollectionService = game:GetService("CollectionService")
local pasta = script.Parent
local Config = require(pasta.Config)
local Territorio = require(pasta.Territorio)
local Locomotor = require(pasta.Locomotor)
local EstadosDragao = require(game:GetService("ReplicatedStorage").Comportamento_Dragoes.EstadosDragao)

local C = {}
C.__index = C
local PRIO = {Incapacitated = 100, DefendNest = 90, ReturnToNest = 90, ChaseIntruder = 90, Attack = 90, Alert = 60,
	Investigate = 55, Recover = 50, SearchWater = 40, SearchFood = 40, Sleep = 30, ReturnHome = 22, Observation = 18,
	Rest = 15, Patrol = 15, Wander = 15, Idle = 5}

local function plano(v) return Vector3.new(v.X, 0, v.Z) end

function C.novo(modelo, ninho, pois, cfg)
	local self = setmetatable({}, C)
	self.cfg = cfg or Config
	self.m, self.id = modelo, modelo:GetAttribute("GuardiaoId") or modelo.Name
	self.E = EstadosDragao.novo(modelo)
	self.L = Locomotor.novo(modelo, self.E, self.cfg)
	self.T = Territorio.novo(ninho, self.cfg)
	self.T:atribuir(self.id)
	self.casa = self.T.centro
	self.entrada = ninho:GetAttribute("Entrada")                    -- ninho em caverna: ponto de chegada externo
	self.pois = pois
	self.fome, self.sede, self.sono = 0.2, 0.2, 0.1
	self.ameacas = {}                                               -- [Model] = {nivel, ultimaPos, t, motivo}
	self.gen, self.tarefa = 0, nil
	self.log = {}
	self.ultimaObs = 0
	self.T.Alerta.Event:Connect(function(alvo, motivo) self:ameaca(alvo, 2, motivo) end)
	Territorio.Eventos.GuardiaoAtacado.Event:Connect(function(guardiao, atacante)
		if guardiao == modelo and atacante then self:ameaca(atacante, 2, "ataque") end
	end)
	self:registrar("criado; ninho=" .. self.T.id)
	task.spawn(function() self:_laco() end)
	return self
end

function C:registrar(msg)
	table.insert(self.log, string.format("%7.1f %-14s %s", os.clock(), self.estado or "-", msg))
	if #self.log > 300 then table.remove(self.log, 1) end
end
function C:definir(estado, vivo)
	if vivo and not vivo() then return end
	if self.estado ~= estado then self.estado = estado; self.m:SetAttribute("EstadoIA", estado); self:registrar("-> " .. estado) end
end

-- ===== percepcao ==============================================================================================
local function raizDe(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end
function C:alvos()
	local l = {}
	for _, p in ipairs(Players:GetPlayers()) do
		local ch = p.Character; local h = ch and ch:FindFirstChildOfClass("Humanoid")
		if ch and h and h.Health > 0 and raizDe(ch) then table.insert(l, ch) end
	end
	for _, m in ipairs(CollectionService:GetTagged("Invasor_Teste")) do if raizDe(m) then table.insert(l, m) end end
	return l
end
function C:ameaca(alvo, nivel, motivo)
	local r = raizDe(alvo); if not r then return end
	local a = self.ameacas[alvo] or {}
	local antes, motivoAntes = a.nivel or 0, a.motivo
	a.nivel = math.max(antes, nivel); a.ultimaPos = r.Position; a.t = os.clock()
	if motivo == "coletou" or motivo == "ataque" then a.persegue = true end
	if motivo then a.motivo = motivo end
	self.ameacas[alvo] = a
	if a.nivel > antes or a.motivo ~= motivoAntes then
		self:registrar(("AMEACA nivel %d (%s) %s"):format(a.nivel, a.motivo or (a.nivel >= 2 and "zona critica" or "vigilancia"), alvo.Name))
	end
end
function C:perceber()
	local cfg = self.cfg; local agora = os.clock()
	self.L:_filtro()
	local cab = self.m.PrimaryPart:FindFirstChild("Cabeca", true).WorldPosition
	local perto = false
	for _, alvo in ipairs(self:alvos()) do
		local r = raizDe(alvo); local dN = plano(r.Position - self.casa).Magnitude
		local dD = plano(r.Position - self.L:pos()).Magnitude
		if dD < cfg.distJogadorAtivo or dN < cfg.distJogadorAtivo then perto = true end
		local hum = alvo:FindFirstChildOfClass("Humanoid")
		local furtivo = alvo:GetAttribute("Furtivo") or (hum and hum.MoveDirection.Magnitude > 0 and hum.WalkSpeed <= cfg.velocidadeFurtiva)
		local raioV = cfg.vigilancia * (furtivo and cfg.furtivoFator or 1)
		if dN <= cfg.critica then
			self:ameaca(alvo, 2, nil)
		elseif dN <= raioV then
			local vis = workspace:Raycast(cab, r.Position - cab, self.L.params)
			if not vis or dN < raioV * 0.5 then self:ameaca(alvo, 1, nil) end
		elseif dD <= cfg.observarDist then
			self.observado = alvo
		end
		local a = self.ameacas[alvo]
		if a and (dN <= raioV or (a.persegue and dN <= cfg.perseguicaoMax)) then a.t = agora; a.ultimaPos = r.Position end
	end
	-- expirar ameacas (fora da vigilancia ha 'lembrarAmeaca' s, alvo sumiu, ou passou do limite da perseguicao)
	for alvo, a in pairs(self.ameacas) do
		local r = raizDe(alvo)
		local longe = r and plano(r.Position - self.casa).Magnitude > cfg.perseguicaoMax
		if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) then
			self.ameacas[alvo] = nil; self:registrar("ameaca encerrada: " .. alvo.Name)
			if a.nivel >= 2 then self.aposConfronto = agora end
		end
	end
	return perto
end
function C:maiorAmeaca()
	local melhor, pior = nil, -1
	for alvo, a in pairs(self.ameacas) do
		-- prioridade: quem coleta/coletou > nivel > mais perto do ovo
		local r = raizDe(alvo)
		local score = a.nivel * 1000 + ((a.motivo == "coleta" or a.motivo == "coletou") and 5000 or 0) - (r and (r.Position - self.casa).Magnitude or 999)
		if score > pior then pior, melhor = score, alvo end
	end
	return melhor, melhor and self.ameacas[melhor]
end

-- ===== decisao ================================================================================================
function C:desejo()
	if self.m:GetAttribute("Incapacitado") then return "Incapacitated" end
	local alvo, a = self:maiorAmeaca()
	if alvo and a.nivel >= 2 then return "DefendNest" end
	if alvo and a.nivel == 1 then return "Alert" end
	if self.aposConfronto and os.clock() - self.aposConfronto < 60 and not self.recuperado then return "Recover" end
	if self.sede > self.cfg.limiarNecessidade and self:poi("Agua") then return "SearchWater" end
	if self.fome > self.cfg.limiarNecessidade and self:poi("Comida") then return "SearchFood" end
	if self.sono > 0.85 then return "Sleep" end
	if self.observado and os.clock() - self.ultimaObs > 25 then return "Observation" end
	if plano(self.L:pos() - self.casa).Magnitude > self.cfg.territorio * 0.85 then return "ReturnHome" end
	return nil                                                      -- rotina livre: escolhida quando a tarefa acaba
end
function C:rotina()
	local opcoes = {{"Wander", 4}, {"Patrol", 3}, {"Rest", 2}, {"Idle", 1}}
	local soma = 0; for _, o in ipairs(opcoes) do soma += o[2] end
	local r = math.random() * soma
	for _, o in ipairs(opcoes) do r -= o[2]; if r <= 0 then return o[1] end end
	return "Idle"
end
function C:poi(tipo)
	local l = {}
	if self.pois then for _, p in ipairs(self.pois:GetChildren()) do if p:GetAttribute("Tipo") == tipo then table.insert(l, p) end end end
	if #l == 0 then return nil end
	return l[math.random(#l)], l
end

function C:iniciar(nome)
	self.gen += 1; local g = self.gen
	self.tarefa = {nome = nome, prio = PRIO[nome] or 10, t = os.clock(), gen = g}
	local vivo = function() return self.gen == g and self.m.Parent ~= nil end
	self:definir(nome)
	task.spawn(function()
		local t0 = os.clock()
		local ok, err = pcall(self["_" .. nome], self, vivo)
		if not ok then self:registrar("ERRO " .. nome .. ": " .. tostring(err)) end
		if vivo() and os.clock() - t0 < self.cfg.tempoMinEstado and nome ~= "Idle" then
			self:registrar(nome .. " terminou cedo; pausa"); self:definir("Idle", vivo)
			self:comportamento("Idle", self.cfg.tempoMinEstado + math.random() * 3, vivo)
		end
		if self.gen == g then self.tarefa = nil end
	end)
end

function C:_laco()
	local ultimo = os.clock()
	while self.m.Parent do
		local perto = self:perceber()
		local agora = os.clock(); local dt = agora - ultimo; ultimo = agora
		self.sede = math.min(1, self.sede + self.cfg.sedeTaxa * dt)
		self.fome = math.min(1, self.fome + self.cfg.fomeTaxa * dt)
		if self.estado ~= "Sleep" then self.sono = math.min(1, self.sono + self.cfg.sonoTaxa * dt) end
		local d = self:desejo()
		local atual = self.tarefa
		if d then
			local p = PRIO[d]
			local podeTrocar = not atual or (p > atual.prio and (p >= 80 or agora - atual.t >= self.cfg.tempoMinEstado))
			if podeTrocar and (not atual or atual.nome ~= d) then self:iniciar(d) end
		elseif not atual then
			self:iniciar(self:rotina())
		end
		task.wait(perto and self.cfg.tickAtivo or self.cfg.tickCalmo)
	end
	self.T:liberar(self.id)
end

-- ===== auxiliares de tarefa ===================================================================================
function C:comportamento(estado, segundos, vivo)
	if not vivo() then return false end
	self.L:soltar(); self.E:Mudar(estado)
	local fim = os.clock() + segundos
	while os.clock() < fim do if not vivo() then return false end; task.wait(0.1) end
	return true
end
function C:emPe(vivo)
	if self.E.postura == "pe" then return true end
	self.L:soltar(); self.E:Mudar("Idle")
	local lim = os.clock() + 8
	while self.E.postura ~= "pe" and os.clock() < lim do if not vivo() then return false end; task.wait(0.1) end
	return true
end
function C:irAoNinho(urgente, vivo, tol)
	if self.entrada and not self.L:ceuLivre(self.casa) then          -- caverna: pousa/chega na entrada e entra a pe
		local dentro = plano(self.L:pos() - self.casa).Magnitude < plano(self.entrada - self.casa).Magnitude
		if not dentro then
			local ok, m = self.L:irPara(self.entrada, urgente, vivo, 12); if not ok then return false, m end
		end
		return self.L:irAPe(self.casa, urgente, vivo, tol or 30)
	end
	return self.L:irPara(self.casa, urgente, vivo, tol or 30)
end
-- deslocamento geral: dentro de lugar fechado (caverna) e destino fora -> sai a pe pela entrada primeiro
function C:ir(destino, urgente, vivo, tol)
	if self.entrada and not self.L.noAr and not self.L:ceuLivre() and self.L:ceuLivre(destino) then
		local ok, m = self.L:irAPe(self.entrada, urgente, vivo, 14); if not ok then return false, m end
	end
	return self.L:irPara(destino, urgente, vivo, tol)
end
local function aleatorioNoTerritorio(self)
	local a = math.random() * 2 * math.pi; local r = self.cfg.territorio * (0.3 + 0.5 * math.random())
	return self.casa + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r)
end

-- ===== tarefas ================================================================================================
function C:_Idle(vivo) self:emPe(vivo); self:comportamento("Idle", 6 + math.random() * 6, vivo) end
function C:_Rest(vivo)
	if not self:emPe(vivo) then return end
	if self.T:ovoPresente() then
		local ok = self:irAoNinho(false, vivo, 40); if not ok or not vivo() then return end
		self:definir("Rest"); self:comportamento("ProtecaoNinho", 25 + math.random() * 15, vivo)
	else
		self:comportamento("Descanso", 20 + math.random() * 10, vivo)
	end
end
function C:_Sleep(vivo)
	if not self:emPe(vivo) then return end
	self:irAoNinho(false, vivo, 45); if not vivo() then return end
	self:definir("Sleep"); if self:comportamento("Sono", 45, vivo) then self.sono = 0; self:comportamento("Despertar", 5, vivo) end
end
function C:_Wander(vivo)
	if not self:emPe(vivo) then return end
	local poi = self:poi("Observacao"); local alvo = poi and poi.Position or aleatorioNoTerritorio(self)
	local ok = self:ir(alvo, false, vivo, 14)
	if not ok or not vivo() then return end
	self:definir("Observation"); self:comportamento("Observacao", 6 + math.random() * 4, vivo)
end
function C:_Observation(vivo)
	self.ultimaObs = os.clock()
	local alvo = self.observado; self.observado = nil
	local r = raizDe(alvo); if not r then return end
	if not self:emPe(vivo) then return end
	if not self.L.noAr then self.L:virarPara(r.Position, vivo) end
	self:comportamento("Observacao", 6, vivo)
end
function C:_Patrol(vivo)
	if not self:emPe(vivo) then return end
	if not self.L:ceuLivre() then
		if not (self.entrada and self.L:irAPe(self.entrada, false, vivo, 14)) then self:_Wander(vivo); return end
	end
	-- rota aerea: 3 pontos do territorio (preferindo poleiros) com trechos de planeio
	local rota = {}
	for i = 1, 3 do local _, ps = self:poi("Poleiro"); table.insert(rota, (ps and math.random() < 0.4) and ps[math.random(#ps)].Position or aleatorioNoTerritorio(self)) end
	for i, ponto in ipairs(rota) do
		self:definir(i == 2 and "Glide" or "Fly"); self.L.planar = (i == 2)
		local ok = self.L:voarAte(ponto, false, vivo, 40)
		self.L.planar = false
		if not ok or not vivo() then return end
	end
	self:definir("Fly")
	local _, ps = self:poi("Poleiro")
	local pouso = (ps and math.random() < 0.5) and ps[math.random(#ps)].Position or (self.T:ovoPresente() and self.casa or aleatorioNoTerritorio(self))
	if pouso == self.casa then self:irAoNinho(false, vivo, 40) else self:ir(pouso, false, vivo, 12) end
end
function C:_ReturnHome(vivo) if self:emPe(vivo) then self:irAoNinho(false, vivo, 60) end end
function C:_SearchWater(vivo)
	if not self:emPe(vivo) then return end
	local poi = self:poi("Agua"); if not poi then return end
	local f = plano(poi.Position - self.L:pos()).Unit
	local ok = self:ir(poi.Position - f * self.L.distBoca, false, vivo, 8); if not ok or not vivo() then return end
	self.L:virarPara(poi.Position, vivo)
	self:definir("Drink"); if self:comportamento("BeberAgua", 9.5, vivo) then self.sede = 0 end
end
function C:_SearchFood(vivo)
	if not self:emPe(vivo) then return end
	local poi = self:poi("Comida"); if not poi then return end
	local f = plano(poi.Position - self.L:pos()).Unit
	local ok = self:ir(poi.Position - f * self.L.distBoca, false, vivo, 8); if not ok or not vivo() then return end
	self.L:virarPara(poi.Position, vivo)
	self:comportamento("Observacao", 2, vivo)                        -- avalia o ambiente antes de comer
	self:definir("Eat"); if self:comportamento("Alimentacao", 8.5, vivo) then self.fome = 0 end
end
function C:_Alert(vivo)
	local alvo, a = self:maiorAmeaca(); if not alvo then return end
	if not self:emPe(vivo) then return end
	if self.L.noAr then self:irAoNinho(false, vivo, 60); return end
	self.L:virarPara(a.ultimaPos, vivo)
	self:comportamento("Alerta", 3, vivo)
	-- longe do ninho: aproxima-se andando para estar pronto (sem abandonar o alerta)
	if plano(self.L:pos() - self.casa).Magnitude > self.cfg.vigilancia then
		if vivo() then self:definir("ReturnHome"); self:irAoNinho(false, vivo, 60) end
	end
	while vivo() and self:maiorAmeaca() do self:comportamento("Alerta", 2, vivo) end
end
function C:_Recover(vivo)
	self.recuperado = true
	if not self:emPe(vivo) then return end
	self:irAoNinho(false, vivo, 40); if not vivo() then return end
	if self.T:ovoPresente() then self:comportamento("InspecaoNinho", 6.5, vivo)
	else self:comportamento("Observacao", 6, vivo) end              -- ovo coletado: nao finge que continua la
	self:comportamento("Alerta", 4, vivo)
	self:comportamento("Espreguicar", 5, vivo)
	self.aposConfronto = nil; self.recuperado = false
end
function C:_Incapacitated(vivo)
	if self.L.noAr then self.L:pousar(vivo, true) end
	self.L:soltar(); self.E:Mudar("Descanso")
	while vivo() and self.m:GetAttribute("Incapacitado") do task.wait(0.5) end
	if vivo() then self.aposConfronto = os.clock(); self.recuperado = false end
end

-- RETORNO URGENTE + DEFESA + PERSEGUICAO LIMITADA + ATAQUE
function C:_DefendNest(vivo)
	local ultimoAtaque, ameacou, falhas = 0, false, 0
	while vivo() do
		local alvo, a = self:maiorAmeaca()
		if not alvo or a.nivel < 2 then break end
		local r = raizDe(alvo); if not r then break end
		local pI = r.Position; local dIN = plano(pI - self.casa).Magnitude
		local dDN = plano(self.L:pos() - self.casa).Magnitude
		-- 1) longe do ninho: volta correndo ou voando
		if dDN > self.cfg.distGuarda + 30 and not (a.persegue and dIN > self.cfg.critica) then
			self:definir("ReturnToNest")
			if self.E.postura ~= "pe" then self:emPe(vivo) end
			local ok, m = self:irAoNinho(true, vivo, self.cfg.distGuarda + 10)
			if not ok and m ~= "cancelado" then
				falhas = (falhas or 0) + 1; self:registrar(("retorno falhou (%d): %s"):format(falhas, tostring(m)))
				if falhas >= 3 then                                     -- rota impossivel: defende de onde esta, sem repetir em loop
					self:registrar("ROTA IMPOSSIVEL ate o ninho; ameaca a distancia")
					if self.L.noAr and self.L:ceuLivre() then self.L:pousar(vivo, true) end
					if a.ultimaPos then self.L:virarPara(a.ultimaPos, vivo) end
					self:comportamento("AmeacaNinho", 5, vivo); falhas = 0
				end
				task.wait(0.5)
			end
		-- 2) quem coletou/atacou e fugiu: persegue dentro do limite territorial
		elseif a.persegue and dIN > self.cfg.critica then
			if dIN > self.cfg.perseguicaoMax then self.ameacas[alvo] = nil; self:registrar("perseguicao interrompida (limite)"); break end
			self:definir("ChaseIntruder")
			if self.E.postura ~= "pe" then self:emPe(vivo) end
			local t0 = os.clock()                                       -- corre por 0,5 s e reavalia o alvo
			local ok, m = self.L:passoChao(pI, true, function() return vivo() and os.clock() - t0 < 0.5 end, self.cfg.distAtaque * 0.8)
			if not ok and m ~= "cancelado" and plano(self.L:pos() - pI).Magnitude > self.cfg.distAtaque then
				-- bloqueado a pe: se puder, segue voando
				if self.L:ceuLivre() then self.L:voarAte(pI, true, function() return vivo() and plano(self.L:pos() - pI).Magnitude > 50 end, 50) end
			end
			if self.L.noAr then self.L:pousar(vivo, true) end
			if plano(self.L:pos() - raizDe(alvo).Position).Magnitude <= self.cfg.distAtaque and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then
				ultimoAtaque = os.clock(); self:definir("Attack"); Territorio.Eventos.AtaqueSolicitado:Fire(self.m, alvo)
				self:comportamento("AmeacaNinho", 1.5, vivo)
			end
		-- 3) no ninho: fica entre o ovo e o invasor, ameaca, ataca quem chega perto
		else
			self:definir("DefendNest")
			local dir = plano(pI - self.casa); dir = dir.Magnitude > 1 and dir.Unit or self.L:frente()
			-- invasor perto do ovo: o dragao se poe sobre o ovo com a BOCA voltada ao invasor (alcance de mordida);
			-- invasor mais longe: fica entre o ovo e ele
			local guarda = (plano(pI - self.casa).Magnitude < self.cfg.distGuarda + self.L.distBoca)
				and (Vector3.new(pI.X, self.casa.Y, pI.Z) - dir * (self.L.distBoca + 12)) or (self.casa + dir * self.cfg.distGuarda)
			if plano(self.L:pos() - guarda).Magnitude > 10 then
				self:emPe(vivo); self.L:passoChao(guarda, true, function() return vivo() and plano(self.L:pos() - guarda).Magnitude > 8 end, 8)
			end
			self.L:virarPara(pI, function() return vivo() end)
			if not ameacou then ameacou = true; self:comportamento("AmeacaNinho", 4.6, vivo)
			else self:comportamento("AmeacaNinho", 1.0, vivo) end
			if plano(self.L:pos() - pI).Magnitude <= self.cfg.distAtaque and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then
				ultimoAtaque = os.clock(); self:definir("Attack"); Territorio.Eventos.AtaqueSolicitado:Fire(self.m, alvo)
			end
		end
		task.wait()
	end
	self.aposConfronto = os.clock(); self.recuperado = false
end
return C
