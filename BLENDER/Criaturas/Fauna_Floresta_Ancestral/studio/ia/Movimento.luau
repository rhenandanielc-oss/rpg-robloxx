-- IA_FaunaFloresta/Movimento - deslocamento do piloto (modelo ancorado, pivo = chao sob a Raiz, frente = LookVector).
-- O deslocamento e aplicado UMA vez por quadro, so aqui (passo/passoVoo). Chao por raycast; obstaculo por spherecast;
-- area de teste por caixa; retorno por PathfindingService (recalculo com frequencia limitada).
local Players = game:GetService("Players")
local CS = game:GetService("CollectionService")
local PFS = game:GetService("PathfindingService")
local Config = require(script.Parent:WaitForChild("Config"))

local M = {}
M.__index = M

local function plano(v) return Vector3.new(v.X, 0, v.Z) end
M.plano = plano
function M.angulo(a, b)   -- angulo assinado de a para b no plano XZ (positivo = esquerda)
	return math.atan2(a.Z * b.X - a.X * b.Z, a.X * b.X + a.Z * b.Z)
end

-- area = {centro = Vector3, tamanho = Vector3}; ignorar = lista extra de instancias que nao contam como obstaculo
function M.novo(modelo, area, ignorar, corpo)
	local self = setmetatable({}, M)
	self.m, self.area, self.ignorarExtra = modelo, area, ignorar or {}
	self.rp = RaycastParams.new(); self.rp.FilterType = Enum.RaycastFilterType.Exclude; self.rp.RespectCanCollide = true
	self.caminhos = 0
	self.hPeito = (corpo and corpo.peito or 0.6) * modelo:GetScale(); self.raio = corpo and corpo.raio or 1.5
	self.raioGiro, self.tauGiro = corpo and corpo.raioGiro, corpo and corpo.tauGiro or 0   -- curva limitada pela velocidade
	self.raioVoo = nil                                                                    -- idem no ar (definido pelo Controlador)
	return self
end

-- comPersonagens = true: jogadores (e alvos de teste) contam como obstaculo (17/11: o corpo do animal nao atravessa ninguem)
function M:_filtro(extra, comPersonagens)
	local l = { self.m }
	if not comPersonagens then
		for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(l, p.Character) end end
		if Config.DEBUG then for _, t in ipairs(CS:GetTagged(Config.TAG_ALVO_TESTE)) do table.insert(l, t) end end
	end
	for _, x in ipairs(self.ignorarExtra) do table.insert(l, x) end
	if extra then for _, x in ipairs(extra) do table.insert(l, x) end end
	self.rp.FilterDescendantsInstances = l
	return self.rp
end

function M:pivo() return self.m:GetPivot() end
function M:pos() return self.m:GetPivot().Position end
function M:frente() return plano(self.m:GetPivot().LookVector).Unit end
function M:escala() return self.m:GetScale() end

function M:chao(p)
	local rp = self:_filtro()
	local r = workspace:Raycast(p + Vector3.new(0, 6, 0), Vector3.new(0, -30, 0), rp)
	return r and r.Position.Y or nil
end

function M:dentroArea(p, margem)
	local a = self.area; if not a then return true end
	local d = p - a.centro; local h = a.tamanho / 2 - Vector3.new(margem or 0, 0, margem or 0)
	return math.abs(d.X) <= h.X and math.abs(d.Z) <= h.Z
end

-- distancia livre a partir de 'origem' na direcao 'dir' ate 'dist' (spherecast raio r). nil = livre
function M:obstaculo(origem, dir, dist, r, extra, comPersonagens)
	if dir.Magnitude < 1e-4 then return nil end
	local rp = self:_filtro(extra, comPersonagens)
	local res = workspace:Spherecast(origem, r, dir.Unit * dist, rp)
	return res and res.Distance or nil
end

-- altura do peito (para os testes de obstaculo terrestres)
function M:peito(p, h) return (p or self:pos()) + Vector3.new(0, h or self.hPeito, 0) end

-- um passo terrestre: gira ate 'dirDesejada' com giro maximo (rad/s), avanca v*dt, assenta no chao.
-- devolve false se o passo sairia da area ou do chao (nao move).
function M:passo(dt, v, dirDesejada, giro)
	local pv = self.m:GetPivot()
	local f = plano(pv.LookVector).Unit
	if dirDesejada and plano(dirDesejada).Magnitude > 1e-3 then
		local d = plano(dirDesejada).Unit
		local a = M.angulo(f, d)
		local w = giro or math.huge
		-- 17/11: o giro sai da passada. Raio minimo de curva = raioGiro (ou v*tauGiro, se maior): parado nao gira
		if self.raioGiro then w = math.min(w, v / math.max(self.raioGiro, v * self.tauGiro)) end
		local lim = w * dt
		a = math.clamp(a, -lim, lim)
		f = (CFrame.Angles(0, a, 0) * CFrame.new(Vector3.zero, f)).LookVector
		f = plano(f).Unit
	end
	-- 16/11: nao atravessa obstaculo (o teste do muro mostrou o cervo passando entre dois recalculos de rota)
	if v > 1e-3 and self:obstaculo(pv.Position + Vector3.new(0, self.hPeito, 0), f, v * dt + 0.3, self.raio, nil, true) then
		self.m:PivotTo(CFrame.lookAt(pv.Position, pv.Position + f)); return false
	end
	local alvo = pv.Position + f * (v * dt)
	if not self:dentroArea(alvo, 2) then
		self.m:PivotTo(CFrame.lookAt(pv.Position, pv.Position + f)); return false
	end
	local y = self:chao(alvo)
	if not y then self.m:PivotTo(CFrame.lookAt(pv.Position, pv.Position + f)); return false end
	local np = Vector3.new(alvo.X, y, alvo.Z)
	self.m:PivotTo(CFrame.lookAt(np, np + f))
	return true
end

-- passo de voo 3D: segue 'alvo' (Vector3), horizontal v, vertical limitado (subida/descida), giro limitado
function M:passoVoo(dt, v, alvo, giro, subida, descida)
	local pv = self.m:GetPivot(); local p = pv.Position
	local f = plano(pv.LookVector).Unit
	local dh = plano(alvo - p)
	if dh.Magnitude > 0.05 then
		local w = giro; if self.raioVoo then w = math.min(w, v / self.raioVoo) end   -- 17/11: sem velocidade nao gira no ar
		local a = math.clamp(M.angulo(f, dh.Unit), -w * dt, w * dt)
		f = plano((CFrame.Angles(0, a, 0) * CFrame.new(Vector3.zero, f)).LookVector).Unit
	end
	local passoH = math.min(v * dt, dh.Magnitude)
	local dy = math.clamp(alvo.Y - p.Y, -descida * dt, subida * dt)
	local np = p + f * passoH + Vector3.new(0, dy, 0)
	self.m:PivotTo(CFrame.lookAt(np, np + f))
	return (plano(alvo - np)).Magnitude, alvo.Y - np.Y
end

-- passo com desvio: se a direcao desejada estiver bloqueada a 2,5 studs, tenta +-30/60/90 graus (a primeira livre)
function M:passoDesvio(dt, v, dir, giro)
	local d = plano(dir); if d.Magnitude < 1e-3 then return self:passo(dt, v, nil, giro) end
	d = d.Unit
	local o = self:pos() + Vector3.new(0, self.hPeito, 0)
	for _, a in ipairs({ 0, 30, -30, 60, -60, 90, -90 }) do
		local c = (CFrame.Angles(0, math.rad(a), 0) * CFrame.new(Vector3.zero, d)).LookVector
		if not self:obstaculo(o, c, 2.5, self.raio, nil, true) then return self:passo(dt, v, c, giro) end
	end
	return false
end

-- 17/11: primeira direcao livre (a 'dist' studs, personagens contam) a partir de 'pref', abrindo em leque ate 150 graus
function M:direcaoLivre(pref, dist)
	local d = plano(pref); if d.Magnitude < 1e-3 then d = self:frente() else d = d.Unit end
	local o = self:pos() + Vector3.new(0, self.hPeito, 0)
	for _, a in ipairs({ 0, 30, -30, 60, -60, 90, -90, 120, -120, 150, -150 }) do
		local c = (CFrame.Angles(0, math.rad(a), 0) * CFrame.new(Vector3.zero, d)).LookVector
		if not self:obstaculo(o, c, dist, self.raio, nil, true) then return c end
	end
	return nil
end

-- 17/11: gira no lugar ate 'dir' a 'w' rad/s (so na manobra, com clipe de curva tocando: as patas dao os passos)
function M:girar(dt, dir, w)
	local p = self:pos(); local f = self:frente(); local d = plano(dir)
	if d.Magnitude < 1e-3 then return end
	local a = math.clamp(M.angulo(f, d.Unit), -w * dt, w * dt)
	f = plano((CFrame.Angles(0, a, 0) * CFrame.new(Vector3.zero, f)).LookVector).Unit
	self.m:PivotTo(CFrame.lookAt(p, p + f))
end

function M:olharPara(dir)
	local p = self:pos(); local d = plano(dir)
	if d.Magnitude > 1e-3 then self.m:PivotTo(CFrame.lookAt(p, p + d.Unit)) end
end

-- caminho terrestre ate 'destino'; devolve lista de Vector3 ou nil
function M:caminho(destino, raioAgente)
	self.caminhos += 1
	local path = PFS:CreatePath({ AgentRadius = raioAgente or 2, AgentHeight = 5, AgentCanJump = false, WaypointSpacing = 6 })
	local ok = pcall(function() path:ComputeAsync(self:pos(), destino) end)
	if not ok or path.Status ~= Enum.PathStatus.Success then return nil end
	local r = {}
	for i, w in ipairs(path:GetWaypoints()) do if i > 1 then table.insert(r, w.Position) end end
	return r
end

return M
