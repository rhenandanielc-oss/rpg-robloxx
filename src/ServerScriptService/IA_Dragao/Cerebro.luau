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
-- PATCH_IA_SELVAGEM (30/10): investigar, espaco pessoal, LOD, convivencia entre dragoes, zonas seguras, ataque a distancia
local okN, Nucleo = pcall(function() return require(game:GetService("ServerScriptService"):WaitForChild("Combate_Dragao", 5):WaitForChild("Nucleo", 5)) end)
-- PATCH_IA_AJUSTES: postura de combate sem entrada (o rugido de ameaca fica so na 1a vez do confronto)
EstadosDragao.ESTADOS.PosturaCombate = EstadosDragao.ESTADOS.PosturaCombate or {postura = "pe", loop = {"Preparar_Combate"}}
-- PATCH_IA_DERROTA_AR: derrotavel (Vida/Incapacitado) e combate no ar (decisao do usuario 30/10)
local function zonaSegura(pos) return okN and type(Nucleo) == "table" and Nucleo.emZonaSegura and Nucleo.emZonaSegura(pos) or false end

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
	self.proximoDesde = {}
	if not modelo:GetAttribute("VidaMax") then modelo:SetAttribute("VidaMax", self.cfg.vidaGuardiao) end
	modelo:SetAttribute("Vida", modelo:GetAttribute("VidaMax")); modelo:SetAttribute("Incapacitado", nil)
	self.cxAlerta = self.T.Alerta.Event:Connect(function(alvo, motivo) self:ameaca(alvo, 2, motivo); self.urgente = true end)
	self.cxAtacado = Territorio.Eventos.GuardiaoAtacado.Event:Connect(function(guardiao, atacante)
		if guardiao == modelo and atacante then self:ameaca(atacante, 2, "ataque"); self.urgente = true end
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
	a.inicio = a.inicio or os.clock()
	if motivo == "coletou" or motivo == "ataque" or motivo == "invasao" then a.persegue = true end
	-- ameaca PESSOAL (ao dragao, nao ao ninho): o limite da perseguicao passa a ser o territorio inteiro
	if motivo == "ataque" or motivo == "invasao" or motivo == "proximo" then a.pessoal = true end
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
	local perto = false; local minDist = math.huge
	for _, alvo in ipairs(self:alvos()) do
		local r = raizDe(alvo); local dN = plano(r.Position - self.casa).Magnitude
		local dD = plano(r.Position - self.L:pos()).Magnitude; minDist = math.min(minDist, dD, dN)
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
		-- ESPACO PESSOAL (tambem longe do ninho): perto do dragao e visivel -> alerta (encara, asas meio abertas);
		-- muito perto por toleranciaProximo s -> defesa propria. Dentro de zona segura: so observa.
		local hab = self.habituado and self.habituado[alvo]
		local habituado = hab and agora - hab < 90 and dD > cfg.espacoCritico and not self.ameacas[alvo]
		if dD <= cfg.espacoPessoal and not habituado and not zonaSegura(r.Position) then
			local vis = dD < cfg.espacoCritico or not workspace:Raycast(cab, r.Position - cab, self.L.params)
			if vis then
				if dD <= cfg.espacoCritico then
					self.proximoDesde[alvo] = self.proximoDesde[alvo] or agora
					if agora - self.proximoDesde[alvo] >= cfg.toleranciaProximo then self:ameaca(alvo, 2, "invasao")
					else self:ameaca(alvo, 1, (self.ameacas[alvo] and self.ameacas[alvo].motivo) or "proximo") end
				else
					self.proximoDesde[alvo] = nil
					self:ameaca(alvo, 1, (self.ameacas[alvo] and self.ameacas[alvo].motivo) or "proximo")
				end
			end
		else
			self.proximoDesde[alvo] = nil
		end
		a = self.ameacas[alvo]
		local lim = a and a.pessoal and cfg.territorio or cfg.perseguicaoMax
		if a and (dN <= raioV or (a.persegue and dN <= lim) or (a.pessoal and dD <= cfg.espacoPessoal * 1.3)) then a.t = agora; a.ultimaPos = r.Position end
	end
	-- expirar ameacas (fora da vigilancia ha 'lembrarAmeaca' s, alvo sumiu, ou passou do limite da perseguicao)
	for alvo, a in pairs(self.ameacas) do
		local r = raizDe(alvo)
		local longe = r and plano(r.Position - self.casa).Magnitude > (a.pessoal and cfg.territorio or cfg.perseguicaoMax)
		local cansou = a.motivo == "proximo" and a.nivel < 2 and agora - (a.inicio or agora) > 25     -- parado perto sem avancar
		if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) or (r and zonaSegura(r.Position)) or cansou then
			if a.motivo == "proximo" then self.habituado = self.habituado or {}; self.habituado[alvo] = agora end
			self.ameacas[alvo] = nil; self:registrar("ameaca encerrada: " .. alvo.Name); self.proximoDesde[alvo] = nil
			-- presenca que sumiu sem confronto: vai conferir a ultima posicao conhecida (por tempo limitado)
			if a.nivel < 2 and a.ultimaPos and r and alvo.Parent and not cansou and plano(r.Position - self.L:pos()).Magnitude > cfg.observarDist then
				self.investigar = {pos = a.ultimaPos, t = agora}                -- so se o alvo sumiu de vista
			end
			if a.nivel >= 2 then self.aposConfronto = agora end
		end
	end
	self.longe = minDist > cfg.distJogadorLonge; self.dormente = self.longe
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
	if self.investigar and os.clock() - self.investigar.t < self.cfg.investigarJanela then return "Investigate" end
	if self.aposConfronto and os.clock() - self.aposConfronto < 60 and not self.recuperado then return "Recover" end
	if self.sede > self.cfg.limiarNecessidade and self:poi("Agua") then return "SearchWater" end
	if self.fome > self.cfg.limiarNecessidade and self:poi("Comida") then return "SearchFood" end
	if self.sono > 0.85 then return "Sleep" end
	if self.observado and os.clock() - self.ultimaObs > 25 then return "Observation" end
	if plano(self.L:pos() - self.casa).Magnitude > self.cfg.territorio * 0.85 then return "ReturnHome" end
	return nil                                                      -- rotina livre: escolhida quando a tarefa acaba
end
function C:rotina()
	-- LOD: longe de todos os jogadores so rotinas paradas (sem locomocao por quadro); perto, rotina completa
	local opcoes = self.dormente and {{"Rest", 2}, {"Idle", 1}} or {{"Wander", 4}, {"Patrol", 3}, {"Rest", 2}, {"Idle", 1}}
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
		if self.m:GetAttribute("Controlador") then self.L:soltar(); task.wait(0.5); continue end   -- montado: nunca disputa o controle
		local perto = self:perceber()
		local agora = os.clock(); local dt = agora - ultimo; ultimo = agora
		self.sede = math.min(1, self.sede + self.cfg.sedeTaxa * dt)
		self.fome = math.min(1, self.fome + self.cfg.fomeTaxa * dt)
		if self.estado ~= "Sleep" then self.sono = math.min(1, self.sono + self.cfg.sonoTaxa * dt) end
		-- vida: regenera fora de combate; a barra so aparece em combate/derrotado
		local vmax, vida = self.m:GetAttribute("VidaMax"), self.m:GetAttribute("Vida")
		local ud = self.m:GetAttribute("UltimoDano")
		if vmax and vida and vida < vmax and not self.m:GetAttribute("Incapacitado") and (not ud or workspace:GetServerTimeNow() - ud > self.cfg.regenApos) then
			self.m:SetAttribute("Vida", math.min(vmax, vida + self.cfg.regenVida * dt))
		end
		self:barraVida()
		local d = self:desejo()
		local atual = self.tarefa
		if d then
			local p = PRIO[d]
			local podeTrocar = not atual or (p > atual.prio and (p >= 80 or agora - atual.t >= self.cfg.tempoMinEstado))
			if podeTrocar and (not atual or atual.nome ~= d) then self:iniciar(d) end
		elseif not atual then
			self:iniciar(self:rotina())
		end
		-- LOD comportamental + reacao imediata a eventos (Alerta do ninho / ataque marcam 'urgente')
		local espera = perto and self.cfg.tickAtivo or (self.longe and self.cfg.tickDormente or self.cfg.tickCalmo)
		local fimE = os.clock() + espera
		while os.clock() < fimE and not self.urgente and self.m.Parent do task.wait(0.1) end
		self.urgente = false
	end
	self.T:liberar(self.id)
	if self.cxAlerta then self.cxAlerta:Disconnect() end; if self.cxAtacado then self.cxAtacado:Disconnect() end
	self.ameacas, self.proximoDesde = {}, {}
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
local function _pontoSorteado(self)
	local a = math.random() * 2 * math.pi; local r = self.cfg.territorio * (0.3 + 0.5 * math.random())
	return self.casa + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r)
end

-- convivencia entre dragoes: ponto livre = longe da posicao e do destino atual dos outros guardioes
function C:pontoLivre(p)
	for m, outro in pairs(_G.IA_DRAGOES or {}) do
		if outro ~= self and m.Parent and outro.L then
			if plano(outro.L:pos() - p).Magnitude < self.cfg.distEntreDragoes then return false end
			if outro.destino and plano(outro.destino - p).Magnitude < self.cfg.distEntreDragoes then return false end
		end
	end
	return true
end
function C:poleiroLivre()
	local _, ps = self:poi("Poleiro"); if not ps then return nil end
	local livres = {}
	for _, p in ipairs(ps) do if self:pontoLivre(p.Position) then table.insert(livres, p.Position) end end
	return #livres > 0 and livres[math.random(#livres)] or nil
end
local function aleatorioNoTerritorio(self)
	local p
	for _ = 1, 6 do p = _pontoSorteado(self); if self:pontoLivre(p) then return p end end
	return p
end
-- ataque: perto sempre; a distancia (sopro/arremetida) so com linha de visao; nunca em zona segura
function C:podeAtacar(alvo)
	local r = raizDe(alvo); if not r or zonaSegura(r.Position) then return false end
	local d = plano(self.L:pos() - r.Position).Magnitude
	local dy = math.abs(r.Position.Y - (self.L:pos().Y - self.L.alturaPivo))
	if d <= self.cfg.distAtaque and dy < 25 then return true end           -- perto e no mesmo nivel
	if d > self.cfg.distAtaqueMax then return false end
	local cab = self.m.PrimaryPart:FindFirstChild("Cabeca", true).WorldPosition
	return workspace:Raycast(cab, r.Position - cab, self.L.params) == nil
end
-- encara so se estiver bem fora (evita girar no lugar a toa e reiniciar o clipe de alerta)
function C:encarar(pos, vivo)
	local d = plano(pos - self.L:pos())
	if d.Magnitude > 1 and self.L:frente():Dot(d.Unit) < 0.9 and not self.L.noAr then self.L:virarPara(pos, vivo) end
end
function C:barraVida()
	local b = self.barra
	if not b then
		b = Instance.new("BillboardGui"); b.Name = "BarraVida"; b.Size = UDim2.fromOffset(170, 12); b.StudsOffset = Vector3.new(0, 16, 0)
		b.MaxDistance = 320; b.Enabled = false
		local fundo = Instance.new("Frame"); fundo.Name = "Fundo"; fundo.Size = UDim2.fromScale(1, 1); fundo.BorderSizePixel = 0
		fundo.BackgroundColor3 = Color3.fromRGB(25, 20, 20); fundo.BackgroundTransparency = 0.2; fundo.Parent = b
		local v = Instance.new("Frame"); v.Name = "V"; v.Size = UDim2.fromScale(1, 1); v.BorderSizePixel = 0; v.BackgroundColor3 = Color3.fromRGB(185, 45, 35); v.Parent = fundo
		b.Adornee = self.m.PrimaryPart; b.Parent = self.m.PrimaryPart; self.barra = b
	end
	local max = self.m:GetAttribute("VidaMax") or 1; local v = self.m:GetAttribute("Vida") or max
	local ud = self.m:GetAttribute("UltimoDano")
	b.Enabled = (ud ~= nil and workspace:GetServerTimeNow() - ud < 20) or self.m:GetAttribute("Incapacitado") == true
	b.Fundo.V.Size = UDim2.fromScale(math.clamp(v / max, 0, 1), 1)
end
function C:alvoNoAr(alvo)
	local r = raizDe(alvo); if not r then return false end
	local g = self.L:chaoEm(r.Position)
	return g ~= nil and r.Position.Y - g > self.cfg.alturaAlvoNoAr
end
function C:_Investigate(vivo)
	local inv = self.investigar; self.investigar = nil
	if not inv or not self:emPe(vivo) then return end
	local d = plano(inv.pos - self.L:pos())
	if d.Magnitude > 30 and plano(inv.pos - self.casa).Magnitude <= self.cfg.territorio then
		self.destino = inv.pos
		local ok = self:ir(inv.pos - d.Unit * 28, false, vivo, 14)
		if not ok or not vivo() then return end
	end
	self:encarar(inv.pos, vivo)
	self:definir("Investigate"); self:comportamento("Observacao", self.cfg.investigarTempo, vivo)   -- fareja e olha em volta
end

-- ===== tarefas ================================================================================================
function C:_Idle(vivo) self:emPe(vivo); self:comportamento("Idle", 6 + math.random() * 6, vivo) end
function C:_Rest(vivo)
	if not self:emPe(vivo) then return end
	if self.T:ovoPresente() then
		local ok = self:irAoNinho(false, vivo, 40); if not ok or not vivo() then return end
		self:definir("Rest"); self:comportamento("ProtecaoNinho", 25 + math.random() * 15, vivo)
	else
		-- descanso acordado: senta (nobre, atento) ou deita, alternando para nao repetir sempre o mesmo
		self:comportamento(math.random() < 0.5 and "Sentado" or "Descanso", 20 + math.random() * 10, vivo)
	end
end
function C:_Sleep(vivo)
	if self.E.postura == "deitado" and plano(self.L:pos() - self.casa).Magnitude < 60 then
		self:definir("Sleep"); if self:comportamento("Sono", 45, vivo) then self.sono = 0; self:comportamento("Despertar", 5, vivo) end
		return
	end
	if not self:emPe(vivo) then return end
	self:irAoNinho(false, vivo, 45); if not vivo() then return end
	self:definir("Sleep"); if self:comportamento("Sono", 45, vivo) then self.sono = 0; self:comportamento("Despertar", 5, vivo) end
end
function C:_Wander(vivo)
	if not self:emPe(vivo) then return end
	local poi = self:poi("Observacao"); local alvo = (poi and self:pontoLivre(poi.Position)) and poi.Position or aleatorioNoTerritorio(self)
	self.destino = alvo
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
	for i = 1, 3 do local pl = math.random() < 0.4 and self:poleiroLivre(); table.insert(rota, pl or aleatorioNoTerritorio(self)) end
	for i, ponto in ipairs(rota) do
		self:definir(i == 2 and "Glide" or "Fly"); self.L.planar = (i == 2); self.destino = ponto
		local ok = self.L:voarAte(ponto, false, vivo, 40)
		self.L.planar = false
		if not ok or not vivo() then return end
	end
	self:definir("Fly")
	local _, ps = self:poi("Poleiro")
	local pl = math.random() < 0.5 and self:poleiroLivre()
	local pouso = pl or (self.T:ovoPresente() and self.casa or aleatorioNoTerritorio(self)); self.destino = pouso
	if pouso == self.casa then self:irAoNinho(false, vivo, 40) else self:ir(pouso, false, vivo, 12) end
end
function C:_ReturnHome(vivo) if self:emPe(vivo) then self:irAoNinho(false, vivo, 60) end end
function C:_SearchWater_antigo(vivo)          -- substituida (PATCH_IA_MARGEM)
	if not self:emPe(vivo) then return end
	local poi = self:poi("Agua"); if not poi then return end
	local f = plano(poi.Position - self.L:pos()).Unit
	local ok = self:ir(poi.Position - f * self.L.distBoca, false, vivo, 8); if not ok or not vivo() then return end
	self.L:virarPara(poi.Position, vivo)
	self:definir("Drink"); if self:comportamento("BeberAgua", 9.5, vivo) then self.sede = 0 end
end
-- PATCH_IA_MARGEM: BEBER NA MARGEM — acha a agua real (voxels Water) perto do ponto, fica em terra firme de FRENTE
-- para a agua, boca na beira (antes parava no ponto vindo do lado do lago: cauda na agua, de costas para ela).
-- Sem agua perto do ponto: fonte inacessivel, registra e desiste (sem ficar tentando).
function C:margem(poi)
	self.margens = self.margens or {}
	if self.margens[poi] ~= nil then return self.margens[poi] or nil end
	local T = workspace.Terrain; local c = poi.Position; local achou
	for r = 4, 96, 6 do
		for k = 0, 23 do
			local a = k / 24 * 2 * math.pi
			local p = c + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r)
			local m = T:ReadVoxels(Region3.new(p - Vector3.new(2, 6, 2), p + Vector3.new(2, 14, 2)):ExpandToGrid(4), 4)
			for y = 1, m.Size.Y do if m[1][y][1] == Enum.Material.Water then achou = p; break end end
			if achou then break end
		end
		if achou then break end
	end
	self.margens[poi] = achou or false
	return achou
end
function C:_SearchWater(vivo)
	if not self:emPe(vivo) then return end
	local poi = self:poi("Agua"); if not poi then return end
	local agua = self:margem(poi)
	if not agua then self:registrar("agua inacessivel perto de " .. poi.Name); self.sede = 0.5; return end
	local w = plano(agua - poi.Position); w = w.Magnitude > 0.5 and w.Unit or plano(agua - self.L:pos()).Unit
	local beira = agua - w * 3                                         -- ultimo trecho seco antes da agua
	local destino = beira - w * (self.L.distBoca - 4)                  -- corpo em terra, boca na beira
	self.destino = destino
	local ok = self:ir(destino, false, vivo, 6); if not ok or not vivo() then return end
	self.L:virarPara(agua + w * 20, vivo)
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
	if self.L.noAr then
		if a.pessoal then self.L:pousar(vivo)                              -- alerta pessoal: pousa ali e encara
		else self:irAoNinho(false, vivo, 60); return end
	end
	self.L:virarPara(a.ultimaPos, vivo)
	self:comportamento("Alerta", 3, vivo)
	-- longe do ninho: aproxima-se andando para estar pronto (sem abandonar o alerta)
	-- alerta PESSOAL (alguem perto do dragao, fora do ninho): fica onde esta, encarando
	if not a.pessoal and plano(self.L:pos() - self.casa).Magnitude > self.cfg.vigilancia then
		if vivo() then self:definir("ReturnHome"); self:irAoNinho(false, vivo, 60) end
	end
	while vivo() and self:maiorAmeaca() do
		local _, a2 = self:maiorAmeaca(); if a2 and a2.ultimaPos then self:encarar(a2.ultimaPos, vivo) end
		self:comportamento("Alerta", 2, vivo)
	end
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
	self.ameacas = {}                                                  -- derrotado: esquece o confronto
	local fimInc = os.clock() + self.cfg.tempoRecuperacao
	while vivo() and self.m:GetAttribute("Incapacitado") and os.clock() < fimInc do task.wait(0.5) end
	if vivo() and self.m:GetAttribute("Incapacitado") then              -- recupera sozinho (metade da vida)
		self.m:SetAttribute("Incapacitado", nil); self.m:SetAttribute("Vida", math.floor((self.m:GetAttribute("VidaMax") or 600) * 0.5))
		self:registrar("recuperado da derrota")
	end
	if vivo() then self.aposConfronto = os.clock(); self.recuperado = false end
end

-- RETORNO URGENTE + DEFESA + PERSEGUICAO LIMITADA + ATAQUE
function C:_DefendNest(vivo)
	local ultimoAtaque, ameacou, falhas = 0, false, 0
	while vivo() do
		local alvo, a = self:maiorAmeaca()
		if not alvo or a.nivel < 2 then break end
		if self.m:GetAttribute("EmAtaque") then
			if self.L.noAr and self.m:GetAttribute("EmAtaque") ~= "Arremetida" then self.L:clipe("Pairar", true) end   -- golpe no ar: paira
			task.wait(0.1); continue
		end
		local r = raizDe(alvo); if not r then break end
		local pI = r.Position; local dIN = plano(pI - self.casa).Magnitude
		local dDN = plano(self.L:pos() - self.casa).Magnitude
		-- COMBATE AEREO: alvo voando -> persegue no ar e ataca no ar; alvo no chao -> segue a defesa em terra (abaixo)
		if self:alvoNoAr(alvo) and (self.L.noAr or self.L:ceuLivre()) then
			local lim = a.pessoal and self.cfg.territorio or self.cfg.perseguicaoMax
			if dIN > lim + 60 or zonaSegura(pI) then self.ameacas[alvo] = nil; self:registrar("combate aereo interrompido (limite)"); break end
			self:definir("AirCombat")
			local t0 = os.clock()
			self.L:perseguirAr(function() local rr = raizDe(alvo); return rr and rr.Position end,
				function() return vivo() and os.clock() - t0 < 0.5 and not self.m:GetAttribute("EmAtaque") end, ((self.m:GetAttribute("RecargaFim_Sopro") or 0) > workspace:GetServerTimeNow()) and 20 or self.cfg.distCombateAr)
			if vivo() and self:podeAtacar(alvo) and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then
				ultimoAtaque = os.clock(); self:definir("Attack"); Territorio.Eventos.AtaqueSolicitado:Fire(self.m, alvo)
			end
			task.wait(); continue
		end
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
			if dIN > (a.pessoal and self.cfg.territorio or self.cfg.perseguicaoMax) or zonaSegura(pI) then self.ameacas[alvo] = nil; self:registrar("perseguicao interrompida (limite)"); break end
			self:definir("ChaseIntruder")
			if self.L.noAr then self.L:pousar(vivo, true) end   -- PATCH_IA_POUSO_PERSEGUICAO: alvo no chao, persegue a pe
			if self.E.postura ~= "pe" then self:emPe(vivo) end
			local t0 = os.clock()                                       -- corre por 0,5 s e reavalia o alvo
			local ok, m = self.L:passoChao(pI, true, function() return vivo() and os.clock() - t0 < 0.5 end, self.cfg.distAtaque * 0.8)
			if not ok and m ~= "cancelado" and plano(self.L:pos() - pI).Magnitude > self.cfg.distAtaque then
				-- bloqueado a pe: se puder, segue voando
				if self.L:ceuLivre() then self.L:voarAte(pI, true, function() return vivo() and plano(self.L:pos() - pI).Magnitude > 50 end, 50) end
			end
			if self.L.noAr then self.L:pousar(vivo, true) end
			if self:podeAtacar(alvo) and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then
				ultimoAtaque = os.clock(); self:definir("Attack"); Territorio.Eventos.AtaqueSolicitado:Fire(self.m, alvo)
				self:comportamento("AmeacaNinho", 1.5, vivo)
			end
		-- 3) no ninho: fica entre o ovo e o invasor, ameaca, ataca quem chega perto
		else
			if self.L.noAr then self.L:pousar(vivo, true) end            -- alvo voltou ao chao: pousa para lutar em terra
			self:definir("DefendNest")
			local dir = plano(pI - self.casa); dir = dir.Magnitude > 1 and dir.Unit or self.L:frente()
			local cabP = self.m.PrimaryPart:FindFirstChild("Cabeca", true).WorldPosition
			local semVisao = workspace:Raycast(cabP, pI - cabP, self.L.params) ~= nil
			-- invasor perto do ovo: o dragao se poe sobre o ovo com a BOCA voltada ao invasor (alcance de mordida);
			-- invasor mais longe: fica entre o ovo e ele
			local guarda = (plano(pI - self.casa).Magnitude < self.cfg.distGuarda + self.L.distBoca)
				and (Vector3.new(pI.X, self.casa.Y, pI.Z) - dir * (self.L.distBoca + 12)) or (self.casa + dir * self.cfg.distGuarda)
			-- sem visao (invasor na encosta/atras da borda): avanca ate a borda para enxergar, sem sair da zona critica
			if semVisao and dIN > self.cfg.distGuarda + 12 then guarda = self.casa + dir * math.min(dIN - 18, self.cfg.critica) end
			if plano(self.L:pos() - guarda).Magnitude > 10 then
				self:emPe(vivo); self.L:passoChao(guarda, true, function() return vivo() and plano(self.L:pos() - guarda).Magnitude > 8 end, 8)
			end
			self.L:virarPara(pI, function() return vivo() end)
			if not ameacou then ameacou = true; self:comportamento("AmeacaNinho", 4.6, vivo)
			else self:comportamento("PosturaCombate", 1.0, vivo) end
			if self:podeAtacar(alvo) and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then
				ultimoAtaque = os.clock(); self:definir("Attack"); Territorio.Eventos.AtaqueSolicitado:Fire(self.m, alvo)
			end
		end
		task.wait()
	end
	self.aposConfronto = os.clock(); self.recuperado = false
end
return C
