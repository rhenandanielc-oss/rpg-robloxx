-- IA_FaunaFloresta/Controlador - controlador COMPARTILHADO do piloto (16/11/2026). Um fio por animal; o servidor decide
-- alvo, estado e deslocamento. Fluxos por especie [PROPOSTA]:
--   Cervo : Repouso -> Alerta -> Fuga -> (Desacelerar) -> Retorno -> Repouso
--   Javali: Repouso -> Alerta -> Ameaca -> Investida curta -> Recuperacao -> Retorno -> Repouso (desiste se recuar/bloqueado)
--   Coruja: Pousada -> Alerta -> Decolagem -> Voo (waypoints) -> Pouso -> Pousada (poleiro alternativo ou seguro)
-- mudar() troca de estado e cancela a acao anterior (token). O deslocamento e aplicado so em Movimento:passo/passoVoo.
local RunService = game:GetService("RunService")
local Config = require(script.Parent:WaitForChild("Config"))
local Anim = require(script.Parent:WaitForChild("Anim"))
local Percepcao = require(script.Parent:WaitForChild("Percepcao"))
local Movimento = require(script.Parent:WaitForChild("Movimento"))
local okSons, Sons = pcall(require, script.Parent:WaitForChild("Sons", 5))   -- 17/11: sons (falha nao derruba a IA)
if not okSons then warn("[FaunaIA] Sons indisponivel:", Sons); Sons = nil end
local plano, angulo = Movimento.plano, Movimento.angulo

local K = {}
K.__index = K
K.todos = {}

local function suave(x) x = math.clamp(x, 0, 1); return x * x * (3 - 2 * x) end

-- opts: area {centro,tamanho}; casa CFrame; poleiros {nome={topo=Vector3, inst=Model}}; rotas {"A_B"={Vector3...}}; poleiro
function K.novo(modelo, especie, opts)
	local self = setmetatable({}, K)
	self.m, self.especie, self.cfg = modelo, especie, Config.especies[especie]
	self.esc = modelo:GetScale()
	self.anim = Anim.novo(modelo, especie)
	self.perc = Percepcao.novo(modelo, self.cfg)
	local ign = {}
	for _, p in pairs(opts.poleiros or {}) do table.insert(ign, p.inst) end
	self.mov = Movimento.novo(modelo, opts.area, {}, self.cfg.corpo)
	if self.cfg.voo then self.mov.raioVoo = self.cfg.voo.raioGiro end
	self.poleiros, self.rotas, self.poleiro = opts.poleiros, opts.rotas, opts.poleiro
	self.casa = opts.casa or modelo:GetPivot()
	self.tok, self.estado, self.log, self.ativo = 0, "Iniciando", {}, true
	self.t0 = os.clock()
	if Config.DEBUG then self:_placa() end
	table.insert(K.todos, self)
	return self
end

function K:_placa()
	local rp = self.m:FindFirstChild("RootPart") or self.m.PrimaryPart
	local bb = Instance.new("BillboardGui"); bb.Name = "DebugFauna"; bb.Size = UDim2.fromOffset(170, 34)
	bb.StudsOffsetWorldSpace = Vector3.new(0, 4 * self.esc, 0); bb.AlwaysOnTop = true; bb.MaxDistance = 250
	local tl = Instance.new("TextLabel"); tl.Size = UDim2.fromScale(1, 1); tl.BackgroundTransparency = 0.35
	tl.BackgroundColor3 = Color3.new(0, 0, 0); tl.TextColor3 = Color3.new(1, 1, 1); tl.TextScaled = true; tl.Font = Enum.Font.GothamBold
	tl.Parent = bb; bb.Parent = rp; self.placa = tl
end

function K:registrar(txt)
	local e = string.format("%6.2f %s %s", os.clock() - self.t0, self.estado, txt or "")
	table.insert(self.log, e); if #self.log > 200 then table.remove(self.log, 1) end
	if Config.DEBUG then print("[FaunaIA:" .. self.especie .. "] " .. e) end
end

function K:mudar(estado, info)
	self.tok += 1
	self.anim:pararAcao(0.2)
	self.estado = estado
	self.m:SetAttribute("Estado", estado)
	if self.placa then self.placa.Text = self.especie .. ": " .. estado end
	self:registrar(info)
	if Sons then pcall(Sons.estado, self, estado) end
	return self.tok
end

function K:vivo() return self.ativo and self.m.Parent ~= nil and self.m:IsDescendantOf(workspace) end
function K:quadro()
	local dt = RunService.Heartbeat:Wait()
	self.alvo, self.dist = self.perc:atualizar(os.clock())
	return dt
end
function K:aguardar(s, cond) local t = 0; while t < s and self:vivo() do t += self:quadro(); if cond and cond() then return true end end; return false end
function K:v(nome) return (self.cfg.vClipe[nome] or 0) * self.esc end
function K:pos() return self.mov:pos() end

-- velocidade de avanco (studs/s) de um clipe de transicao no tempo t
function K:vPerfil(nome, t, dur)
	local v = self.anim:perfil(nome, t)
	if v then return v * self.esc end
	local pp = self.cfg.perfilProprio and self.cfg.perfilProprio[nome]
	if pp then
		local function val(x) return type(x) == "number" and x or (self.cfg.vClipe[x] or 0) end
		local t0 = pp.inicio or 0
		local s = t < t0 and 0 or suave((t - t0) / math.max(dur - t0, 1e-3))
		return (val(pp.de) + (val(pp.para) - val(pp.de)) * s) * self.esc
	end
	return 0
end

-- toca 'nome' (acao) e desloca com o perfil. opts: dir()=direcao desejada, giro, parar()=motivo p/ encerrar antes,
-- voo=true + alvoPt() (passo 3D sem chao), proxima={base, vel} (laco que assume no fim), fade
function K:transicao(nome, opts)
	opts = opts or {}
	local dur = self.anim:duracao(nome)
	local tok = self.tok
	if not self.anim:acao(nome, opts.fade or 0.15) then self:registrar("clipe ausente " .. nome) end
	local t, motivo = 0, "fim"
	while t < dur do
		if not self:vivo() then return "removido" end
		if self.tok ~= tok then return "cancelado" end
		local dt = self:quadro(); t += dt
		local v = self:vPerfil(nome, math.min(t, dur), dur)
		if opts.voo then
			self.mov:passoVoo(dt, v, opts.alvoPt(), opts.giro or 0, opts.subida or 0, opts.descida or 0)
		elseif v > 1e-3 or opts.dir then
			local okp = opts.semDesvio and self.mov:passo(dt, v, opts.dir and opts.dir(), opts.giro)
				or self.mov:passoDesvio(dt, v, opts.dir and opts.dir() or self.mov:frente(), opts.giro)
			if not okp and v > 1e-3 then motivo = "bloqueado" end
		end
		if opts.parar then local r = opts.parar(); if r then motivo = r; break end end
	end
	if opts.proxima then self.anim:base(opts.proxima[1], 0.12, opts.proxima[2] or 1) end
	self.anim:pararAcao(0.12)
	return motivo
end

------------------------------------------------------------------ terrestre
function K:escolherFuga(ameaca, dirAtual)
	local F = self.cfg.fuga
	local p = self:pos()
	local away = plano(p - ameaca); away = away.Magnitude > 0.1 and away.Unit or -self.mov:frente()
	local alcance = F.lookahead * 2.5
	local melhor, nota = nil, -math.huge
	for i = 0, 15 do
		local a = i * math.pi / 8
		local d = Vector3.new(math.sin(a), 0, math.cos(a))
		local dot = d:Dot(away)
		if dot > -0.1 then
			local livre = self.mov:obstaculo(self.mov:peito(p), d, alcance, F.raioCorpo) or alcance
			local area = 0
			while area < alcance and self.mov:dentroArea(p + d * (area + 4), 6) do area += 4 end
			local espaco = math.min(livre, area)
			if espaco >= 10 then
				local n = dot * 2 + espaco / alcance * 1.5 + (dirAtual and d:Dot(dirAtual) * 0.6 or 0)
				if n > nota then melhor, nota = d, n end
			end
		end
	end
	return melhor
end

-- volta para a casa andando (Pathfinding so quando a linha direta esta bloqueada). perigo() interrompe -> "ameaca"
-- 17/11: curva SEMPRE andando: VirarE/VirarD (clipe de curva aprovado, 25 graus/s) quando a curva pedida e grande, Andar no
-- reto (correcao lenta). O raio de curva vem da passada (Movimento.passo), entao o animal nunca gira parado.
function K:retorno(clipeAndar, clipeParado, perigo)
	self:mudar("Retorno")
	local R, Cv, C = self.cfg.retorno, self.cfg.curva, self.cfg.clipes
	local destino = self.casa.Position
	local pts, ultimo = nil, -1e9
	local rg = self.cfg.corpo.raioGiro or 0
	local clipeAtual = clipeAndar
	self.anim:base(clipeAndar, 0.3, 1)
	local parado, preso, esperaAte, manobra = false, 0, 0, 0
	local function angPara(v) return v.Magnitude > 0.05 and angulo(self.mov:frente(), v.Unit) or 0 end
	while self:vivo() do
		local dt = self:quadro()
		if perigo and perigo() then return "ameaca" end
		local p = self:pos()
		local resto = plano(destino - p)
		-- chegou: dentro do raio, ou tao perto que so alcancaria a casa girando em volta dela
		if resto.Magnitude <= R.raioChegada or (resto.Magnitude <= 2.2 * rg and math.abs(angPara(resto)) > math.rad(70)) then break end
		local alvoPt
		local bloq = self.mov:obstaculo(self.mov:peito(p), resto, math.min(resto.Magnitude, 12), 1.2)
		if not bloq then pts = nil; alvoPt = destino
		else
			if (not pts or #pts == 0) and os.clock() - ultimo >= R.recalcCaminho then
				ultimo = os.clock(); pts = self.mov:caminho(destino, math.max(2.5, rg * 0.7))   -- caminho largo: cabe a curva
				self:registrar(pts and ("caminho " .. #pts .. " pts") or "caminho falhou")
			end
			if pts and #pts > 0 then
				local w = plano(pts[1] - p)
				if w.Magnitude < 2.5 then table.remove(pts, 1) end
				alvoPt = pts[1]
			end
		end
		if alvoPt and os.clock() >= esperaAte then
			local a = angPara(plano(alvoPt - p))
			local quer = clipeAtual
			if Cv and C.virarE then
				if math.abs(a) >= Cv.entra then quer = a > 0 and C.virarE or C.virarD
				elseif math.abs(a) <= Cv.sai or quer == clipeParado then quer = clipeAndar end
			else quer = clipeAndar end
			if parado or quer ~= clipeAtual then self.anim:base(quer, 0.3, 1); clipeAtual = quer; parado = false end
			local giro = Cv and (clipeAtual == clipeAndar and Cv.giroReto or Cv.giroClipe) or R.giro
			if self.mov:passoDesvio(dt, self:v(clipeAtual), alvoPt - p, giro) then preso = 0; manobra = 0
			else
				preso += dt
				local livre = C.virarE and manobra < (R.manobraMax or 4) and self.mov:direcaoLivre(alvoPt - p, 3)
				if livre then
					-- 17/11: frente travada (quina/muro) e o raio de curva nao cabe: vira dando passos com o clipe de curva ate
					-- a frente livrar (nao fica parado nem gira sem mexer as patas). Limitado a manobraMax s.
					local lado = angPara(livre) >= 0 and C.virarE or C.virarD
					if clipeAtual ~= lado then self.anim:base(lado, 0.25, 1); clipeAtual = lado; parado = false end
					if manobra == 0 then self:registrar("manobra: vira dando passos") end
					manobra += dt
					self.mov:girar(dt, livre, Cv.giroClipe * 1.6)
				elseif preso > 0.3 then        -- nao anda no lugar: para, recalcula e tenta de novo em 1 s
					preso = 0; manobra = 0; esperaAte = os.clock() + 1.0; pts = nil; ultimo = -1e9
					self.anim:base(clipeParado, 0.3, 1); parado = true; clipeAtual = clipeParado; self:registrar("bloqueado: espera e recalcula")
				end
			end
		elseif not alvoPt and not parado then
			self.anim:base(clipeParado, 0.3, 1); parado = true; clipeAtual = clipeParado     -- sem rota: espera parado (estado seguro)
		end
	end
	return "casa"
end

------------------------------------------------------------------ CERVO
local Fluxos = {}

function K:fugaCervo()
	local c, C, F = self.cfg, self.cfg.clipes, self.cfg.fuga
	while self:vivo() do
		local ameaca = self.alvo and self.alvo.parte.Position or (self:pos() - self.mov:frente() * 10)
		local inicio = self:pos()
		local dir = self:escolherFuga(ameaca)
		if not dir then self:mudar("SemRota", "fica em alerta"); return "semrota" end
		self:mudar("Fuga", self.alvo and self.alvo.nome or "?")
		local ultimoCalc = os.clock()
		local function dirFn()
			if self.alvo then ameaca = self.alvo.parte.Position end
			if self.mov:obstaculo(self.mov:peito(), self.mov:frente(), F.lookahead, F.raioCorpo) then ultimoCalc = -1e9 end
			if os.clock() - ultimoCalc >= F.recalc then
				ultimoCalc = os.clock(); dir = self:escolherFuga(ameaca, dir) or dir
			end
			return dir
		end
		self:transicao(C.arrancada, { dir = dirFn, giro = F.giro, proxima = { C.corrida, 1 } })
		local t, presos = 0, 0
		while self:vivo() do
			local dt = self:quadro(); t += dt
			local ok = self.mov:passo(dt, self:v("Corrida"), dirFn(), F.giro)
			if ok then presos = 0 else presos += dt; ultimoCalc = -1e9 end
			if presos > 0.4 then break end                                  -- nao corre no lugar
			if (self:pos() - ameaca).Magnitude >= F.distSegura or t >= F.tempoMax or (not self.alvo and t > 2.5) then break end
		end
		self:mudar("Desacelerar", string.format("fugiu %.0f studs em %.1fs", plano(self:pos() - inicio).Magnitude, t))
		local function perto() return self.alvo and self.dist <= c.percepcao.raioFuga and "ameaca" or nil end
		local r = self:transicao(C.corridaTrote, { dir = dirFn, giro = F.giro, proxima = { C.trote, 1 }, parar = perto })
		if r ~= "ameaca" then r = self:transicao(C.troteAndar, { dir = dirFn, giro = F.giro, proxima = { C.andar, 1 }, parar = perto }) end
		if r ~= "ameaca" then
			r = self:retorno(C.andar, C.repouso, function() return self.alvo and self.dist <= c.percepcao.raioFuga end)
		end
		if r ~= "ameaca" then return "casa" end
		self:registrar("ameaca de novo: foge outra vez")
	end
end

function Fluxos.Cervo(self)
	local c, C = self.cfg, self.cfg.clipes
	while self:vivo() do
		self:mudar("Repouso"); self.anim:base(C.repouso, 0.3)
		repeat self:quadro() until not self:vivo() or self.alvo
		if not self:vivo() then break end
		self:mudar("Alerta", self.alvo.nome .. string.format(" a %.0f", self.dist))
		self.anim:acao(C.alerta, 0.2)
		local t, fora, fugir = 0, 0, false
		while self:vivo() do
			local dt = self:quadro(); t += dt
			if self.alvo then fora = 0 else fora += dt end
			if self.alvo and self.dist <= c.percepcao.raioFuga and t >= c.alertaMin then fugir = true; break end
			if fora >= c.calma then break end
		end
		if fugir then self:fugaCervo() else self:registrar("alvo recuou: volta ao repouso") end
	end
end

------------------------------------------------------------------ JAVALI
-- 17/11: vira para o alvo ANDANDO em arco (VirarE/VirarD acelerado por encarar.vel: giro e passada sobem juntos, entao
-- as patas casam com o deslocamento). Antes girava parado a 110 graus/s ("um 180 sem se mexer").
function K:encarar(alvoFn, tempoMax)
	local E, C, Cv = self.cfg.encarar, self.cfg.clipes, self.cfg.curva
	local alvo = alvoFn(); if not alvo then return false end
	local d = plano(alvo - self:pos()); if d.Magnitude < 0.1 then return false end
	local a = angulo(self.mov:frente(), d.Unit)
	if math.abs(a) < E.tolerancia then return false end
	local clipe = a > 0 and C.virarE or C.virarD
	self.anim:base(clipe, 0.25, E.vel)
	local t = 0
	while self:vivo() and t < (tempoMax or E.tempoMax) do
		local dt = self:quadro(); t += dt
		local p = alvoFn(); if not p then break end
		d = plano(p - self:pos()); if d.Magnitude < 0.1 then break end
		a = angulo(self.mov:frente(), d.Unit)
		if math.abs(a) < math.rad(5) then break end
		local novo = a > 0 and C.virarE or C.virarD
		if novo ~= clipe then clipe = novo; self.anim:base(clipe, 0.25, E.vel) end
		self.mov:passo(dt, self:v(clipe) * E.vel, d, Cv.giroClipe * E.vel)
	end
	self.anim:base(C.repouso, 0.3)
	return true
end

function K:investida(dist, parteAlvo)
	local C, I = self.cfg.clipes, self.cfg.investida
	local dir = self.mov:frente()        -- a investida nao gira: segue a frente (ja alinhada ao alvo pelo encarar)
	self:mudar("Investida", string.format("alvo a %.1f", dist))
	local inicio = self:pos()
	local dMax = math.min(dist + I.alemDoAlvo, I.distMax)
	-- ponta do focinho a frente do pivo (cantos das malhas visiveis; a RootPart invisivel de 6 studs fica fora) e meia largura
	-- do alvo: o acerto e por CONTATO, nao por raio fixo
	local focinho = 0
	for _, pt in ipairs(self.m:GetDescendants()) do
		if pt:IsA("BasePart") and pt.Transparency < 1 then
			for _, k in ipairs({ Vector3.new(1, 1, 1), Vector3.new(1, 1, -1), Vector3.new(1, -1, 1), Vector3.new(-1, 1, 1),
				Vector3.new(-1, -1, 1), Vector3.new(-1, 1, -1), Vector3.new(1, -1, -1), Vector3.new(-1, -1, -1) }) do
				focinho = math.max(focinho, ((pt.CFrame * (pt.Size / 2 * k)) - self:pos()):Dot(dir))
			end
		end
	end
	local raioAlvo = parteAlvo and math.min(parteAlvo.Size.X, parteAlvo.Size.Z) / 2 or 1
	local function fim()
		local p = self:pos()
		if parteAlvo and parteAlvo.Parent then   -- acerto: o alvo esta a frente e a ponta do focinho quase encostando
			local ra = plano(parteAlvo.Position - p)
			if ra:Dot(dir) > 0 and ra.Magnitude - focinho - raioAlvo <= I.folgaGolpe then return "acerto" end
		end
		if plano(p - inicio).Magnitude >= dMax then return "distancia" end
		if self.mov:obstaculo(self.mov:peito(p), dir, I.lookahead, I.raioCorpo) then return "obstaculo" end
		if not self.mov:dentroArea(p + dir * 3, 3) then return "area" end
		return nil
	end
	local function d() return dir end
	local motivo = self:transicao(C.investida, { dir = d, giro = 0, semDesvio = true, parar = fim, proxima = { C.corrida, 1 } })
	local t = self.anim:duracao(C.investida)
	if motivo == "fim" then
		while self:vivo() do
			local dt = self:quadro(); t += dt
			motivo = fim() or (t >= I.tempoMax and "tempo") or nil
			if motivo then break end
			if not self.mov:passo(dt, self:v("Corrida"), dir, 0) then motivo = "bloqueado"; break end
		end
	end
	if motivo == "acerto" then
		-- 17/11: chifrada (parcial: pescoco/cabeca/orelhas, Action2) por cima da freada; so visual, sem dano
		self.anim:sobre(C.chifrada, 0.06, 1)
		self.m:SetAttribute("UltimaChifrada", os.clock())
		if Sons then pcall(Sons.evento, self, "chifrada") end
	end
	self:mudar("Recuperacao", string.format("%s apos %.1f studs", tostring(motivo), plano(self:pos() - inicio).Magnitude))
	local function freio() return self.mov:obstaculo(self.mov:peito(), dir, 1.5, I.raioCorpo) and "parede" or nil end
	self:transicao(C.recuperacao, { dir = d, giro = 0, semDesvio = true, parar = freio, proxima = { C.repouso, 1 } })
end

function Fluxos.Javali(self)
	local c, C = self.cfg, self.cfg.clipes
	local ultimaInv = -1e9
	local function dh() return self.alvo and plano(self.alvo.parte.Position - self:pos()).Magnitude or math.huge end
	while self:vivo() do
		self:mudar("Repouso"); self.anim:base(C.repouso, 0.3)
		repeat self:quadro() until not self:vivo() or self.alvo
		if not self:vivo() then break end
		self:mudar("Alerta", self.alvo.nome .. string.format(" a %.0f", dh()))
		self:transicao(C.alerta, { proxima = { C.repouso, 1 } })
		local fora, ameacou, proxCheque = 0, false, 0
		while self:vivo() do
			local dt = self:quadro()
			if not self.alvo then
				fora += dt
				if fora >= c.calma then
					self:mudar("Desiste", "alvo recuou"); self:transicao(C.alertaRepouso, { proxima = { C.repouso, 1 } }); break
				end
			else
				fora = 0
				local d = dh()
				local aAlvo = math.abs(angulo(self.mov:frente(), plano(self.alvo.parte.Position - self:pos()).Unit))
				if not ameacou and d <= c.ameaca.raioAmeaca then
					-- ameaca UMA vez por aproximacao; depois vigia
					local function pAlvo() return self.alvo and self.alvo.parte.Position or nil end
					self:mudar("Encarar", self.alvo.nome); self:encarar(pAlvo)
					self:mudar("Ameaca", string.format("a %.1f", dh()))
					self:transicao(C.ameaca, { proxima = { C.repouso, 1 } })
					ameacou = true
					self:mudar("Vigiar")
				elseif ameacou and aAlvo > math.max(c.investida.alinhamento, math.rad(20)) and os.clock() >= proxCheque then
					-- vigiando: acompanha o alvo virando ANDANDO em arco (curto), nunca girando parado
					local function pAlvo() return self.alvo and self.alvo.parte.Position or nil end
					self:encarar(pAlvo, 1.5); proxCheque = os.clock() + 0.5
				elseif ameacou and os.clock() >= proxCheque and os.clock() - ultimaInv >= c.recarga and d <= c.ameaca.raioInvestida
					and aAlvo <= c.investida.alinhamento then
					local dir = plano(self.alvo.parte.Position - self:pos()).Unit
					local bloq = self.mov:obstaculo(self.mov:peito(), dir, math.min(d, c.investida.distMax), c.investida.raioCorpo)
					if bloq and bloq < math.min(d - 1.5, c.investida.minLivre) then
						-- linha bloqueada: nao investe; vigia e rechecha a cada 1 s (sem repetir a ameaca)
						if self.estado ~= "Desiste" then self:mudar("Desiste", string.format("rota bloqueada a %.1f", bloq)) end
						proxCheque = os.clock() + 1.0
					else
						self:investida(d, self.alvo.parte); ultimaInv = os.clock()
						-- sai andando reto; a volta para casa e feita em arco no Retorno (antes girava 180 graus parado aqui)
						self:transicao(C.paradoAndar, { dir = function() return self.mov:frente() end, giro = 0, proxima = { C.andar, 1 } })
						self:retorno(C.andar, C.repouso, function()
							return self.alvo and os.clock() - ultimaInv >= c.recarga and dh() <= c.ameaca.raioAmeaca
						end)
						self:transicao(C.andarParado, { dir = function() return self.mov:frente() end, giro = 0, proxima = { C.repouso, 1 } })
						break
					end
				end
			end
		end
	end
end

------------------------------------------------------------------ CORUJA
function K:poleiroLivre(nome)
	local P = self.poleiros[nome]; if not P then return false, "sem poleiro" end
	for _, a in ipairs(Percepcao.alvos()) do
		if plano(a.parte.Position - P.topo).Magnitude < self.cfg.voo.poleiroLivre then return false, "alvo no poleiro" end
	end
	local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Exclude; op.FilterDescendantsInstances = { self.m, P.inst }
	for _, x in ipairs(workspace:GetPartBoundsInBox(CFrame.new(P.topo + Vector3.new(0, 2.6, 0)), Vector3.new(3, 4.6, 3), op)) do
		if x.CanCollide then return false, "bloqueio sobre o poleiro: " .. x.Name end
	end
	return true
end

function K:pontoPouso(destino, ultimo)
	local topo = self.poleiros[destino].topo
	local dir = plano(topo - ultimo).Unit
	local S = 0
	local p = require(script.Parent.Perfis).Coruja[self.cfg.clipes.pousar]
	for _, v in ipairs(p) do S += v / 30 end
	S *= self.esc
	return topo - dir * S, dir, S
end

-- pontos de voo completos (rota explicita + ponto de inicio do pouso) e checagem de rota livre
function K:planoVoo(destino)
	local rota = self.rotas[self.poleiro .. "_" .. destino]
	if not rota then return nil, "sem rota" end
	local pts = table.clone(rota)
	local L, dirPouso = self:pontoPouso(destino, rota[#rota])
	table.insert(pts, L)
	local ign = { self.poleiros[destino].inst, self.poleiros[self.poleiro].inst }
	local corpo = Vector3.new(0, 1.2, 0)
	local a = self:pos() + corpo
	for i, b in ipairs(pts) do
		local h = self.mov:obstaculo(a, b + corpo - a, (b + corpo - a).Magnitude, self.cfg.voo.raioCorpo, ign)
		if h then return nil, string.format("segmento %d bloqueado a %.1f", i, h) end
		if i < #pts then
			local yc = self.mov:chao(b)
			if yc and b.Y - yc < self.cfg.voo.folgaChao then return nil, "ponto " .. i .. " baixo demais" end
		end
		a = b + corpo
	end
	local livre, porque = self:poleiroLivre(destino)
	if not livre then return nil, porque end
	return pts, nil, dirPouso
end

function K:virarNoLugar(ponto)
	local d = plano(ponto - self:pos()); if d.Magnitude < 0.1 then return end
	local a = angulo(self.mov:frente(), d.Unit)
	if math.abs(a) < math.rad(10) then return end
	self.anim:base(a > 0 and "VirarNoLugarE" or "VirarNoLugarD", 0.2, 1)
	while self:vivo() do
		local dt = self:quadro()
		d = plano(ponto - self:pos())
		a = angulo(self.mov:frente(), d.Unit)
		if math.abs(a) < math.rad(4) then break end
		local passo = math.clamp(a, -math.rad(60) * dt, math.rad(60) * dt)     -- 60 graus/s do manifesto do clipe
		local p = self:pos(); local f = (CFrame.Angles(0, passo, 0) * CFrame.new(Vector3.zero, self.mov:frente())).LookVector
		self.m:PivotTo(CFrame.lookAt(p, p + plano(f)))
	end
end

function K:voar(destino, pts, dirPouso)
	local C, V = self.cfg.clipes, self.cfg.voo
	self:mudar("Decolagem", self.poleiro .. " -> " .. destino)
	self:virarNoLugar(pts[1])
	local p0 = self:pos()
	self:transicao(C.decolar, { voo = true, alvoPt = function() return Vector3.new(pts[1].X, p0.Y, pts[1].Z) end,
		giro = V.giro, proxima = { C.bater, 1 } })
	self:mudar("Voo", destino)
	local i, planando, desvios = 1, false, 0
	local ign = { self.poleiros[destino].inst }
	while self:vivo() and i <= #pts do
		local dt = self:quadro()
		local alvo = pts[i]
		local v = planando and self:v("Planar") or self:v("BaterAsas")
		local dH, dY = self.mov:passoVoo(dt, v, alvo, V.giro, V.subida, V.descida)
		if not planando and i >= 2 then
			self:transicao(C.bater2planar, { voo = true, alvoPt = function() return pts[i] end, giro = V.giro,
				subida = V.subida, descida = V.descida, proxima = { C.planar, 1 } })
			planando = true
		end
		local frente = plano(alvo - self:pos())
		if planando and C.curvaE then     -- 17/11: curva planando com o clipe de curva (asas inclinadas), nao de asas retas
			local ac = frente.Magnitude > 0.5 and angulo(self.mov:frente(), frente.Unit) or 0
			local quer = math.abs(ac) > V.curvaClipe and (ac > 0 and C.curvaE or C.curvaD) or C.planar
			if quer ~= self.anim.baseNome then self.anim:base(quer, 0.35, 1) end
		end
		if frente.Magnitude > 0.5 and self.mov:obstaculo(self:pos() + Vector3.new(0, 1.2, 0), frente, 6, V.raioCorpo, ign) and desvios < 3 then
			desvios += 1; pts[i] = alvo + Vector3.new(0, 4, 0); self:registrar("obstaculo em voo: sobe 4")
		end
		local ultimoPt = i == #pts      -- o inicio do pouso precisa ser exato: o clipe Pousar leva o pivo ate o topo
		if dH < (ultimoPt and 0.15 or V.chegada) and math.abs(dY) < (ultimoPt and 0.2 or 1.5) then i += 1 end
	end
	-- pouso: chega no ponto L alinhado; Pousar leva o pivo ate o topo pelo perfil do clipe
	self:mudar("Pouso", destino)
	local topo = self.poleiros[destino].topo
	local p = self:pos(); local ang = math.deg(math.abs(angulo(self.mov:frente(), dirPouso)))
	self.m:PivotTo(CFrame.lookAt(Vector3.new(p.X, topo.Y, p.Z), Vector3.new(p.X, topo.Y, p.Z) + dirPouso))
	if not planando then self.anim:base(C.planar, 0.1, 1) end
	self:transicao(C.pousar, { voo = true, alvoPt = function() return topo end, giro = V.giro, proxima = { C.repouso, 1 } })
	local erro = (self:pos() - topo).Magnitude
	self.m:PivotTo(CFrame.lookAt(topo, topo + dirPouso))
	self.poleiro = destino
	self:registrar(string.format("contato no poleiro: erro %.2f studs, alinhamento %.0f graus", erro, ang))
	self.ultimoPouso = { erro = erro, ang = ang }
end

function Fluxos.Coruja(self)
	local c, C = self.cfg, self.cfg.clipes
	while self:vivo() do
		self:mudar("Pousada", self.poleiro); self.anim:base(C.repouso, 0.3)
		repeat self:quadro() until not self:vivo() or self.alvo
		if not self:vivo() then break end
		self:mudar("Alerta", self.alvo.nome .. string.format(" a %.0f", self.dist))
		local lado = angulo(self.mov:frente(), plano(self.alvo.parte.Position - self:pos()).Unit) > 0 and C.alertaE or C.alertaD
		self.anim:acao(lado, 0.2)
		local t, fora, tentativas, proxTent = 0, 0, 0, 0
		while self:vivo() do
			local dt = self:quadro(); t += dt
			if self.alvo then fora = 0 else fora += dt end
			if fora >= c.calma then self:registrar("alvo recuou: volta a pousada"); break end
			if self.alvo and self.dist <= c.percepcao.raioFuga and t >= c.alertaMin and t >= proxTent then
				local escolhido, pts, dirP, motivos = nil, nil, nil, {}
				for _, nome in ipairs(self:candidatos()) do
					local r, porque, d = self:planoVoo(nome)
					if r then escolhido, pts, dirP = nome, r, d; break end
					table.insert(motivos, nome .. ": " .. tostring(porque))
				end
				if escolhido then self:voar(escolhido, pts, dirP); break end
				tentativas += 1; proxTent = t + c.voo.reavaliar
				self:registrar("sem rota livre (" .. table.concat(motivos, "; ") .. "), tentativa " .. tentativas)
				if tentativas >= c.voo.tentativas then self:mudar("AlertaPousada", "fica no poleiro, reavalia depois"); tentativas = 0 end
			end
		end
	end
end

-- ordem: poleiros alternativos (exceto o seguro), depois o seguro
function K:candidatos()
	local r, seguro = {}, nil
	for nome, P in pairs(self.poleiros) do
		if nome ~= self.poleiro then if P.seguro then seguro = nome else table.insert(r, nome) end end
	end
	table.sort(r)
	if seguro then table.insert(r, seguro) end
	return r
end

------------------------------------------------------------------
function K:iniciar()
	local lista = {}
	for _, n in pairs(self.cfg.clipes) do table.insert(lista, n) end
	for n in pairs(self.cfg.vClipe) do table.insert(lista, n) end
	if self.especie == "Coruja" then table.insert(lista, "VirarNoLugarE"); table.insert(lista, "VirarNoLugarD") end
	self.anim:preCarregar(lista)
	self.fio = task.spawn(function()
		local ok, err = pcall(Fluxos[self.especie], self)
		if not ok then self:registrar("ERRO " .. tostring(err)); warn("[FaunaIA] erro", self.especie, err) end
		self.ativo = false
	end)
	if Sons then pcall(Sons.iniciarVida, self) end
end

function K:parar()
	self.ativo = false
	self.tok += 1
	if self.fio and coroutine.status(self.fio) ~= "dead" then pcall(task.cancel, self.fio) end
	pcall(function() self.anim:pararTudo(0.1) end)
	if self.placa then self.placa.Parent:Destroy() end
end

return K
