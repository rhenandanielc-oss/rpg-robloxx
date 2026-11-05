-- PATCH_IA_CORRIDA_TAREFA: lacos conferem vivo() apos cada quadro
-- IA_Dragao/Locomotor — move o dragao (modelo ancorado, PivotTo) casando velocidade e giro com os clipes aprovados.
-- Chao: segue o terreno por raycast, inclina pela rampa, para diante de parede/rampa ingreme; caminho por
-- PathfindingService. Ar: Decolagem -> Voo/Voo_Rapido/Planeio/Subida/Descida/Curva_Aerea -> Pouso, altitude acima
-- do relevo da rota e desvio por spherecast; nunca voa onde nao ha ceu livre (cavernas).
-- Todas as funcoes de movimento recebem 'vivo' (function -> bool): quando a tarefa e cancelada, param na hora.
local RunService = game:GetService("RunService")
local PathfindingService = game:GetService("PathfindingService")
local Players = game:GetService("Players")
local L = {}
L.__index = L

local function yawDe(v) return math.atan2(v.X, v.Z) end
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function difAng(a, b) local d = (b - a) % (2 * math.pi); if d > math.pi then d -= 2 * math.pi end; return d end

function L.novo(modelo, estados, cfg)
	local self = setmetatable({}, L)
	self.m, self.E, self.cfg = modelo, estados, cfg
	local root = modelo.PrimaryPart
	local cab = root:FindFirstChild("Cabeca", true); local quad = root:FindFirstChild("Quadril", true)
	local piv = modelo:GetPivot()
	self.f0 = plano(cab.WorldPosition - quad.WorldPosition).Unit
	self.R0 = piv.Rotation
	self.psi, self.pitch = 0, 0
	self.params = RaycastParams.new(); self.params.FilterType = Enum.RaycastFilterType.Exclude
	self:_filtro()
	local chao = self:chaoLocal(piv.Position) or (piv.Position.Y - 26)
	self.alturaPivo = piv.Position.Y - chao
	self.distBoca = (cab.WorldPosition - piv.Position):Dot(self.f0) + 6
	self.noAr, self.alturaVoo = false, 0
	self.atual = nil
	return self
end

function L:_filtro()
	local lista = {self.m}
	for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(lista, p.Character) end end
	for _, m in ipairs(game:GetService("CollectionService"):GetTagged("Invasor_Teste")) do table.insert(lista, m) end
	-- outros dragoes nao sao "terreno" (chao/parede/obstaculo de voo); a convivencia cuida da distancia entre eles
	for _, d in ipairs(workspace:GetChildren()) do if d ~= self.m and d:IsA("Model") and d:GetAttribute("FormaRegional") then table.insert(lista, d) end end
	self.params.FilterDescendantsInstances = lista
end
function L:chaoEm(p)
	local r = workspace:Raycast(Vector3.new(p.X, p.Y + 250, p.Z), Vector3.new(0, -800, 0), self.params)
	return r and r.Position.Y or nil
end
-- chao proximo do corpo (funciona sob tetos de caverna): raio parte 45 studs acima do pivo atual
function L:chaoLocal(p)
	local r = workspace:Raycast(Vector3.new(p.X, p.Y + 45, p.Z), Vector3.new(0, -260, 0), self.params)
	return r and r.Position.Y or nil
end
function L:pos() return self.m:GetPivot().Position end
function L:frente() return CFrame.Angles(0, self.psi, 0):VectorToWorldSpace(self.f0) end
function L:_aplicar(pos)
	if self.m:GetAttribute("EmAtaque") == "Arremetida" or self.m:GetAttribute("CorpoElevado") then return end   -- o combate move o corpo
	local pf = self.m:GetAttribute("PresoFator")                           -- PATCH_CORRENTES_AR: preso pelas Correntes da Noite
	if pf then local atual = self:pos(); pos = atual + (pos - atual) * math.clamp(pf, 0, 1) end
	local giro = CFrame.Angles(0, self.psi, 0)
	local dir = giro:VectorToWorldSpace(self.f0); local direita = dir:Cross(Vector3.yAxis).Unit
	self.m:PivotTo(CFrame.new(pos) * CFrame.fromAxisAngle(direita, self.pitch) * giro * self.R0)
end
function L:_girarPara(dir, taxaGraus, dt)
	-- direcao nula/NaN (ex.: ja exatamente sobre o destino, ainda subindo): mantem o rumo. Sem isto o psi virava NaN e
	-- o PivotTo jogava o modelo para y = -1e6.
	if dir.X ~= dir.X or dir.Z ~= dir.Z or Vector3.new(dir.X, 0, dir.Z).Magnitude < 1e-3 then return 0 end
	local alvo = yawDe(dir) - yawDe(self.f0)
	local d = difAng(self.psi, alvo); local passo = math.rad(taxaGraus) * dt
	self.psi += math.clamp(d, -passo, passo)
	return math.abs(d)
end

-- animacao: assume o controle das trilhas do EstadosDragao (cancela as tarefas dele)
function L:clipe(nome, loop, ritmo, fade)
	if self.atual ~= nome then
		self.E.geracao += 1; self.E.estado = nil; self.E.postura = "pe"
		local t = self.E:_tocar(nome, loop ~= false, fade or 0.3)
		self.trilha = t; self.atual = nome
	end
	if ritmo and self.trilha then self.trilha:AdjustSpeed(ritmo) end
	return self.trilha
end
function L:soltar() self.atual = nil end      -- a proxima animacao vem do EstadosDragao (comportamentos)

local function esperarClipe(self, nome, vivo, ritmo)
	local t = self:clipe(nome, false, ritmo, 0.25)
	local lim = os.clock() + 5
	while t.Length <= 0 and os.clock() < lim do task.wait(0.05) end
	local fim = os.clock() + t.Length / (ritmo or 1) - 0.25
	while os.clock() < fim do if not vivo() then return false end; task.wait(0.05) end
	return true
end

-- ===== chao ===================================================================================================
function L:podePassar(dir)
	local p = self:pos(); local g0 = self:chaoLocal(p)
	local frente = p + dir * 28
	local g1 = self:chaoLocal(frente)
	if not (g0 and g1) then return false, "sem chao" end
	if (g1 - g0) / 28 > self.cfg.inclinacaoMax then return false, "rampa" end
	if g0 - g1 > 40 then return false, "queda" end
	-- corpo largo: raio central + dois nas laterais (largura do corpo com asas recolhidas) + um baixo (rochas no peito)
	local lado = dir:Cross(Vector3.yAxis).Unit * ((self.m:GetAttribute("CorpoRaio") or 8) + 4)
	for _, o in ipairs({Vector3.zero, lado, -lado, Vector3.new(0, -12, 0)}) do
		local r = workspace:Raycast(Vector3.new(p.X, g0 + 22, p.Z) + o, dir * 40, self.params)
		if r and r.Normal.Y < 0.5 then return false, "parede" end
	end
	return true
end

-- anda/corre em linha reta ate 'alvo' (Vector3, no plano). Retorna true (chegou), false+motivo (bloqueado/cancelado)
function L:passoChao(alvo, correr, vivo, tol)
	tol = tol or 6
	local cfg = self.cfg
	-- outro rig informa as proprias velocidades: anda no ritmo natural do clipe (RitmoAndarBase), corre em VelCorrer
	local vel = correr and (self.m:GetAttribute("VelCorrer") or cfg.correrVel * cfg.correrRitmo)
		or (self.m:GetAttribute("RitmoAndarBase") or cfg.andarVel * cfg.andarRitmo)
	vel *= 1 + (self.m:GetAttribute("PassoBonus") or 0)                  -- PATCH_IA_KIT_SOMBRA: Passo Sombrio da IA
	local giro = correr and cfg.giroCorrer or cfg.giroAndar
	local ultimoTeste = 0
	while vivo() do
		local dt = RunService.Heartbeat:Wait(); if not vivo() then break end
		local p = self:pos(); local d = plano(alvo - p)
		if d.Magnitude <= tol then return true end
		local erro = self:_girarPara(d.Unit, giro, dt)
		if erro > math.rad(70) and not correr then                        -- muito fora: gira no lugar com passos
			self:clipe(difAng(self.psi, yawDe(d) - yawDe(self.f0)) > 0 and "Giro_E" or "Giro_D", true)
			self:_girarPara(d.Unit, cfg.giroParado, dt)
		else
			-- ritmo do clipe casado com a velocidade; outro rig informa a velocidade do proprio clipe (RitmoAndarBase)
			local base = self.m:GetAttribute(correr and "RitmoCorrerBase" or "RitmoAndarBase")
			self:clipe(correr and "Correr" or "Andar", true, base and vel / base or (correr and cfg.correrRitmo or cfg.andarRitmo))
			local f = self:frente()
			if os.clock() - ultimoTeste > 0.15 then
				ultimoTeste = os.clock()
				local ok, motivo = self:podePassar(f)
				if not ok then return false, motivo end
			end
			local passo = math.min(vel * dt * math.clamp(1 - erro / math.rad(90), 0.3, 1), d.Magnitude)
			local np = p + f * passo
			local g = self:chaoLocal(np)
			if not g then return false, "sem chao" end
			local gF = self:chaoLocal(np + f * 20) or g; local gT = self:chaoLocal(np - f * 20) or g
			self.pitch = math.clamp(math.atan2(gF - gT, 40), math.rad(-14), math.rad(14)) * -1
			self:_aplicar(Vector3.new(np.X, g + self.alturaPivo, np.Z))
		end
	end
	return false, "cancelado"
end

function L:caminho(destino)
	local p = self:pos(); local g = self:chaoLocal(p) or p.Y
	local path = PathfindingService:CreatePath({AgentRadius = 16, AgentHeight = 40, AgentCanJump = false, AgentCanClimb = false, WaypointSpacing = 16})
	local ok = pcall(function() path:ComputeAsync(Vector3.new(p.X, g + 3, p.Z), destino) end)
	if not ok or path.Status ~= Enum.PathStatus.Success then return nil end
	return path:GetWaypoints()
end

-- a pe por caminho calculado; retorna true, ou false+motivo (sem caminho / bloqueado / cancelado)
function L:irAPe(destino, correr, vivo, tol)
	if self.noAr then                                                     -- nunca anda no ar: pousa onde houver ceu livre
		if not self:ceuLivre() then return false, "no ar sem ceu livre" end
		if not self:pousar(vivo, correr) then return false, "cancelado" end
	end
	local wps = self:caminho(destino)
	if not wps then                                                       -- navmesh nao cobre (ex.: tunel p/ agente grande):
		return self:passoChao(destino, correr, vivo, tol)                 -- linha reta, checando parede/rampa a cada passo
	end
	for i = 2, #wps do
		local ok, motivo = self:passoChao(wps[i].Position, correr, vivo, i == #wps and (tol or 6) or 8)
		if not ok then return false, motivo end
	end
	return true
end

function L:virarPara(alvo, vivo)
	while vivo() do
		local dt = RunService.Heartbeat:Wait(); if not vivo() then break end
		local d = plano(alvo - self:pos()); if d.Magnitude < 1 then return true end
		local alvoPsi = yawDe(d) - yawDe(self.f0); local erro = difAng(self.psi, alvoPsi)
		if math.abs(erro) < math.rad(6) then return true end
		self:clipe(erro > 0 and "Giro_E" or "Giro_D", true)
		self:_girarPara(d.Unit, self.cfg.giroParado, dt); self:_aplicar(self:pos())
	end
	return false
end

-- ===== ar =====================================================================================================
function L:ceuLivre(p)
	p = p or self:pos()
	local r = workspace:Raycast(p + Vector3.new(0, 30, 0), Vector3.new(0, self.cfg.tetoMinVoo, 0), self.params)
	return r == nil
end

function L:decolar(vivo)
	if self.noAr then return true end
	if not self:ceuLivre() then return false, "sem ceu" end
	self.pitch = 0; self:_aplicar(self:pos())
	if not esperarClipe(self, "Decolagem", vivo) then return false, "cancelado" end
	self.noAr, self.alturaVoo = true, 0; self.m:SetAttribute("NoAr", true)
	self:clipe("Voo", true)
	return true
end

-- desce o pivo ate o chao (altura 0) e pousa
function L:pousar(vivo, rapido)
	if not self.noAr then return true end
	while vivo() do
		local dt = RunService.Heartbeat:Wait(); if not vivo() then break end
		local p = self:pos(); local g = (self:ceuLivre(p) and self:chaoEm(p) or self:chaoLocal(p)) or (p.Y - self.alturaPivo)
		local alvoY = g + self.alturaPivo
		if p.Y - alvoY <= 0.5 then break end
		self:clipe("Descida", true)
		self:_aplicar(Vector3.new(p.X, math.max(alvoY, p.Y - (rapido and 20 or 12) * dt), p.Z))
	end
	if not vivo() then return false end
	local ok = esperarClipe(self, "Pouso", vivo)
	self.noAr = false; self.m:SetAttribute("NoAr", false)
	return ok
end

-- voa ate ficar sobre 'destino' (plano). Altitude: relevo da rota + cruzeiro; sobe se o spherecast acusar obstaculo.
function L:voarAte(destino, rapido, vivo, tol)
	tol = tol or 10
	local cfg = self.cfg
	local ok, motivo = self:decolar(vivo); if not ok then return false, motivo end
	local ultimoTeste, extra = 0, 0
	while vivo() do
		local dt = RunService.Heartbeat:Wait(); if not vivo() then break end
		local p = self:pos(); local d = plano(destino - p); local dist = d.Magnitude
		if dist <= tol and p.Y >= (self.altAlvo or p.Y) - 10 then return true end      -- so chega acima do relevo do destino
		local erro = self:_girarPara(d.Unit, cfg.giroVoo, dt)
		local f = self:frente()
		-- altitude desejada: maior chao entre aqui, 60/140 studs a frente e o destino
		if os.clock() - ultimoTeste > 0.25 then
			ultimoTeste = os.clock()
			local gmax = -math.huge
			for _, k in ipairs({0, 60, 140}) do local g = self:chaoEm(p + f * math.min(k, dist)); if g then gmax = math.max(gmax, g) end end
			local gd = self:chaoEm(destino); if gd and dist < 200 then gmax = math.max(gmax, gd) end
			local corpo = p + Vector3.new(0, 14 + 20, 0)
			local hit = workspace:Spherecast(corpo, 26, f * 90, self.params)
			extra = hit and math.min(extra + 25, 150) or math.max(extra - 5, 0); self.bloqueadoVoo = hit ~= nil
			self.altAlvo = gmax + self.alturaPivo + (dist < 120 and cfg.folgaVoo or cfg.alturaCruzeiro) + extra
		end
		local dy = math.clamp((self.altAlvo or p.Y) - p.Y, -cfg.vSubida * dt, cfg.vSubida * dt)
		local vel = (rapido and cfg.vooRapidoVel or cfg.vooVel) * (1 + (self.m:GetAttribute("PassoBonus") or 0))   -- PATCH_IA_KIT_SOMBRA
		local falta = (self.altAlvo or p.Y) - p.Y
		if self.bloqueadoVoo or falta > 40 then vel *= 0.25 end                 -- rocha a frente ou muito abaixo: sobe antes de avancar
		if erro > math.rad(35) then self:clipe(difAng(self.psi, yawDe(d) - yawDe(self.f0)) > 0 and "Curva_Aerea_E" or "Curva_Aerea_D", true); vel *= 0.7
		elseif dy > cfg.vSubida * dt * 0.6 then self:clipe("Subida", true)
		elseif dy < -cfg.vSubida * dt * 0.6 then self:clipe(self.planar and "Planeio" or "Descida", true)
		elseif self.planar then self:clipe("Planeio", true)
		else self:clipe(rapido and "Voo_Rapido" or "Voo", true) end
		self.pitch = 0
		self:_aplicar(Vector3.new(p.X, p.Y + dy, p.Z) + f * math.min(vel * dt, dist))
	end
	return false, "cancelado"
end

-- COMBATE AEREO (30/10): persegue um alvo no ar mantendo 'distIdeal' (plano) e a altura dele (nunca abaixo da folga
-- sobre o relevo); paira quando esta na distancia; obstaculo a frente -> sobe em vez de avancar. Roda enquanto vivo().
function L:perseguirAr(alvoPos, vivo, distIdeal)
	local cfg = self.cfg
	if not self.noAr then local ok, m = self:decolar(vivo); if not ok then return false, m end end
	while vivo() do
		local dt = RunService.Heartbeat:Wait(); if not vivo() then break end
		local alvo = alvoPos(); if not alvo then return false, "sem alvo" end
		local p = self:pos(); local d = plano(alvo - p); local dist = d.Magnitude
		local erro = dist > 1 and self:_girarPara(d.Unit, cfg.giroVoo * 1.4, dt) or 0
		local f = self:frente()
		local g = self:chaoEm(p) or (p.Y - 200)
		local alvoY = math.max(alvo.Y + 4, g + self.alturaPivo + cfg.folgaVoo * 0.6)
		local dy = math.clamp(alvoY - p.Y, -cfg.vSubida * dt, cfg.vSubida * dt)
		local avanco = 0
		if dist > distIdeal + 10 then avanco = math.min(cfg.vooVel * dt, dist - distIdeal)
		elseif dist < distIdeal - 12 then avanco = -cfg.vooVel * 0.4 * dt end
		if avanco > 0 and workspace:Spherecast(p + Vector3.new(0, 20, 0), 22, f * 60, self.params) then avanco = 0; dy = cfg.vSubida * dt end
		if math.abs(avanco) < 1e-3 and math.abs(dy) < cfg.vSubida * dt * 0.5 then self:clipe("Pairar", true)
		elseif erro > math.rad(35) then self:clipe(difAng(self.psi, yawDe(d) - yawDe(self.f0)) > 0 and "Curva_Aerea_E" or "Curva_Aerea_D", true)
		elseif dy > cfg.vSubida * dt * 0.6 then self:clipe("Subida", true)
		elseif dy < -cfg.vSubida * dt * 0.6 then self:clipe("Descida", true)
		else self:clipe("Voo", true) end
		self.pitch = 0
		self:_aplicar(Vector3.new(p.X, p.Y + dy, p.Z) + f * avanco)
	end
	return true
end

-- melhor meio para chegar: a pe se houver caminho e nao for longe; senao voando (se houver ceu)
function L:irPara(destino, urgente, vivo, tol)
	local p = self:pos(); local dist = plano(destino - p).Magnitude
	local podeVoar = self:ceuLivre() and self:ceuLivre(destino)
	if self.noAr then
		local ok, m = self:voarAte(self:ultimoCeuLivre(destino), urgente, vivo, tol); if not ok then return false, m end
		if not self:pousar(vivo, urgente) then return false, "cancelado" end
		if plano(destino - self:pos()).Magnitude > (tol or 6) then return self:irAPe(destino, urgente, vivo, tol) end
		return true
	end
	if not (dist > self.cfg.distPreferirVoo and podeVoar) then
		local ok, m = self:irAPe(destino, urgente, vivo, tol)
		if ok then return true end
		if m == "cancelado" then return false, m end
		if not (self:ceuLivre() and self:ceuLivre(destino)) then return false, m end
	end
	local pouso = self:ultimoCeuLivre(destino)
	local ok, m = self:voarAte(pouso, urgente, vivo, tol); if not ok then return false, m end
	if not self:pousar(vivo, urgente) then return false, "cancelado" end
	if plano(destino - self:pos()).Magnitude > (tol or 6) then return self:irAPe(destino, urgente, vivo, tol) end
	return true
end

-- ponto mais proximo do destino, na linha vinda do dragao, que ainda tem ceu livre (ex.: antes da borda da caverna)
function L:ultimoCeuLivre(destino)
	if self:ceuLivre(destino) then return destino end
	local p = self:pos(); local d = plano(destino - p); local n = math.ceil(d.Magnitude / 15)
	for i = 1, n do
		local q = destino - d.Unit * (15 * i)
		if self:ceuLivre(q) then return q - d.Unit * 25 end            -- margem para as asas
	end
	return p
end
return L
