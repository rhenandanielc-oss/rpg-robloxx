assert(game.PlaceId == 73543092389791)
local sss = game.ServerScriptService
local f = sss:FindFirstChild("LoboAncestral_Kit") or Instance.new("Folder", sss); f.Name = "LoboAncestral_Kit"
local s = f:FindFirstChild("LoboKit_Servidor") or Instance.new("Script"); s.Name = "LoboKit_Servidor"
s.Source = [==[-- LoboKit_Servidor (Script em ServerScriptService.LoboAncestral_Kit) - kit Natureza do Lobo Ancestral, PROTOTIPO no place
-- isolado Testes-loboancestral (15/11/2026). Fonte: BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/kit/LoboKit_Servidor.luau.
-- Servidor decide tudo: dono, estado, alvo, alcance, linha de visao, obstaculos, dano, energia, recarga, duracao, noite e
-- acumulo de bonus. O cliente so pede (RemoteEvent PedidoKit) e mostra efeitos (EventoKit). Numeros: ConfigKitLobo [PROPOSTA].
-- Montaria do lobo nao existe neste place: teste montado fica PENDENTE.
local Players = game:GetService("Players")
local RS = game:GetService("RunService")
local Lighting = game:GetService("Lighting")
local Rep = game:GetService("ReplicatedStorage")
local PASTA = Rep:WaitForChild("LoboAncestral")
local CFG = require(PASTA:WaitForChild("ConfigKitLobo"))
local LA = require(PASTA:WaitForChild("LoboAnimacao"))
local AREA = workspace:WaitForChild("Teste_LoboAncestral")

local remotes = PASTA:FindFirstChild("Remotes") or Instance.new("Folder", PASTA); remotes.Name = "Remotes"
local function remote(n) local r = remotes:FindFirstChild(n) or Instance.new("RemoteEvent", remotes); r.Name = n; return r end
local PEDIDO, EVENTO = remote("PedidoKit"), remote("EventoKit")

local K = {lobos = {}, log = {}}
_G.LoboKit = K
local function log(s) table.insert(K.log, string.format("%.2f %s", os.clock(), s)); if #K.log > 300 then table.remove(K.log, 1) end end

-- ------------------------------------------------------------------ alvos e geometria
local function alvosPasta() return AREA:FindFirstChild("Alvos") end
local function alvoValido(m)
	if typeof(m) ~= "Instance" or not m:IsA("Model") then return false end
	local pa = alvosPasta(); if not pa or not m:IsDescendantOf(pa) then return false end
	local h = m:FindFirstChildOfClass("Humanoid"); local r = m.PrimaryPart or m:FindFirstChild("HumanoidRootPart")
	return h ~= nil and h.Health > 0 and r ~= nil
end
local function centro(m) local r = m.PrimaryPart or m:FindFirstChild("HumanoidRootPart"); return r and r.Position end
local function filtro(L, extra)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude
	local lista = {L.modelo}
	for _, x in ipairs(extra or {}) do table.insert(lista, x) end
	for _, pl in ipairs(Players:GetPlayers()) do if pl.Character then table.insert(lista, pl.Character) end end
	p.FilterDescendantsInstances = lista; return p
end
local function peito(L) return L.modelo:GetPivot().Position + Vector3.new(0, 4.5, 0) end
-- linha de visao: raio do peito do lobo ao centro do alvo; so o proprio alvo pode ser atingido
local function linhaDeVisao(L, alvo)
	local a, b = peito(L), centro(alvo)
	local hit = workspace:Raycast(a, b - a, filtro(L))
	return hit == nil or hit.Instance:IsDescendantOf(alvo)
end

-- ------------------------------------------------------------------ modificadores (tabela unica, aditiva, com teto)
local function recalcular(L)
	local v, e, d = 0, 0, 0
	for _, mod in pairs(L.mods) do v += mod.vel or 0; e += mod.esq or 0; d += mod.dano or 0 end
	L.velMult = 1 + math.min(v, CFG.Acumulo.tetoVelocidade)
	L.esquiva = CFG.Esquiva.chanceBase + math.min(e, CFG.Acumulo.tetoEsquiva)
	L.danoMult = 1 + math.min(d, CFG.Acumulo.tetoDano)
	local m = L.modelo
	m:SetAttribute("VelMult", L.velMult); m:SetAttribute("Esquiva", L.esquiva); m:SetAttribute("DanoMult", L.danoMult)
	local fontes = {} for k in pairs(L.mods) do table.insert(fontes, k) end; table.sort(fontes)
	m:SetAttribute("Bonus", table.concat(fontes, ","))
end
local function setMod(L, nome, mod) L.mods[nome] = mod; recalcular(L) end

-- ------------------------------------------------------------------ lobo
local function vivo(L) return L.ativo and L.modelo.Parent ~= nil and L.vida > 0 end
local function registrar(modelo, dono)
	local L = {modelo = modelo, dono = dono, C = LA.preparar(modelo), mods = {}, recargas = {}, estado = "Livre",
		energia = CFG.Energia.max, vida = CFG.Vida, ativo = true, tarefas = {}, noite = false, rastros = {}}
	modelo:SetAttribute("DonoUserId", dono and dono.UserId or 0)
	K.lobos[modelo] = L
	recalcular(L)
	L.C.base("Repouso", 0)
	modelo.AncestryChanged:Connect(function(_, pai) if pai == nil then K.remover(L, "removido") end end)
	log("registrado " .. modelo:GetFullName() .. " dono=" .. tostring(dono))
	return L
end
function K.remover(L, motivo)
	if not L.ativo then return end
	L.ativo = false; L.estado = "Removido"
	for _, t in ipairs(L.tarefas) do pcall(task.cancel, t) end
	L.mods = {}; pcall(recalcular, L)
	K.lobos[L.modelo] = nil
	log("lobo encerrado: " .. motivo)
end
function K.morrer(L)
	L.vida = 0; L.estado = "Morto"; L.mods = {}; recalcular(L)
	for _, t in ipairs(L.tarefas) do pcall(task.cancel, t) end; L.tarefas = {}
	L.C.pararTudo(0.1); L.C.acao("Impacto", 0.05)
	L.modelo:SetAttribute("Estado", "Morto"); log("lobo morto")
end
-- dano recebido (para testar esquiva): rola a chance calculada no servidor
function K.receberDano(L, dano)
	if not vivo(L) then return "morto" end
	if math.random() < L.esquiva then log("esquivou"); return "esquivou" end
	L.vida -= dano; if L.vida <= 0 then K.morrer(L) end
	return "acertou"
end
local function tarefa(L, f) local t = task.spawn(f); table.insert(L.tarefas, t); return t end

-- ------------------------------------------------------------------ passiva: Cacador Noturno (estado unico no servidor)
local CN = CFG.CacadorNoturno
local noiteGlobal = nil
local function ehNoite(ct, anterior)
	local h = anterior and CN.histerese or -CN.histerese          -- histerese: para sair do estado precisa passar a borda
	if anterior then return ct >= CN.noiteInicio - h or ct < CN.noiteFim + h end
	return ct >= CN.noiteInicio - h or ct < CN.noiteFim + h
end
task.spawn(function()
	while true do
		local n = ehNoite(Lighting.ClockTime, noiteGlobal)
		if n ~= noiteGlobal then
			noiteGlobal = n; workspace:SetAttribute("LoboNoite", n)
			for _, L in pairs(K.lobos) do
				if vivo(L) then
					setMod(L, "CacadorNoturno", n and {vel = CN.velocidade, esq = CN.esquiva, dano = CN.danoFisico} or nil)
					L.modelo:SetAttribute("Noite", n)
					if L.dono then EVENTO:FireClient(L.dono, "Noite", L.modelo, n) end
				end
			end
			log("noite=" .. tostring(n) .. " ClockTime=" .. Lighting.ClockTime)
		end
		task.wait(CN.intervalo)
	end
end)
K.ehNoite = function() return noiteGlobal end

-- ------------------------------------------------------------------ passiva: Instinto de Caca
-- pegadas = posicoes ANTIGAS (>= atrasoMin s) de inimigos que o lobo viu (linha de visao) a <= raio; so para o dono.
-- pista de ninho = direcao aproximada (erro aleatorio +-ninhoErroGraus), sem distancia nem posicao.
local IC = CFG.InstintoCaca
task.spawn(function()
	local t = 0
	while true do
		task.wait(IC.intervalo); t += IC.intervalo
		for _, L in pairs(K.lobos) do
			if vivo(L) and L.dono then
				local pa = alvosPasta()
				local pistas = {}
				local agora = os.clock()
				for _, a in ipairs(pa and pa:GetChildren() or {}) do
					if alvoValido(a) then
						local c = centro(a)
						local hist = L.rastros[a] or {}; L.rastros[a] = hist
						local dist = (c - L.modelo:GetPivot().Position).Magnitude
						if dist <= IC.raio and linhaDeVisao(L, a) then
							table.insert(hist, {t = agora, p = Vector3.new(c.X, 0, c.Z)})
						end
						while hist[1] and agora - hist[1].t > IC.rastroSeg do table.remove(hist, 1) end
						for _, h in ipairs(hist) do
							if agora - h.t >= IC.atrasoMin then table.insert(pistas, h.p) end
						end
					end
				end
				if #pistas > 0 then EVENTO:FireClient(L.dono, "Pegadas", L.modelo, pistas) end
				if t % IC.ninhoIntervalo < IC.intervalo then
					for _, n in ipairs(AREA:GetDescendants()) do
						if n:GetAttribute("PistaNinho") then
							local d = n.Position - L.modelo:GetPivot().Position
							if Vector3.new(d.X, 0, d.Z).Magnitude <= IC.ninhoRaio then
								local ang = math.atan2(d.X, d.Z) + math.rad((math.random() * 2 - 1) * IC.ninhoErroGraus)
								EVENTO:FireClient(L.dono, "PistaNinho", L.modelo, Vector3.new(math.sin(ang), 0, math.cos(ang)))
								log("pista de ninho enviada (direcao com erro)")
							end
						end
					end
				end
			end
		end
	end
end)

-- ------------------------------------------------------------------ energia e recargas
task.spawn(function()
	while true do
		local dt = task.wait(0.25)
		for _, L in pairs(K.lobos) do
			if vivo(L) then
				L.energia = math.min(CFG.Energia.max, L.energia + CFG.Energia.regenPorS * dt)
				L.modelo:SetAttribute("Energia", math.floor(L.energia)); L.modelo:SetAttribute("Vida", L.vida)
			end
		end
	end
end)
local function podeUsar(L, nome, c)
	if not vivo(L) then return false, "lobo inativo" end
	if L.estado ~= "Livre" then return false, "ocupado (" .. L.estado .. ")" end
	local r = L.recargas[nome]; if r and os.clock() < r then return false, string.format("recarga %.1fs", r - os.clock()) end
	if c.energia and L.energia < c.energia then return false, "energia" end
	return true
end
local function gastar(L, nome, c)
	L.recargas[nome] = os.clock() + (c.recarga or 0)
	if c.energia then L.energia -= c.energia end
	L.modelo:SetAttribute("Recarga_" .. nome, L.recargas[nome])
end
local function causarDano(L, alvo, base, tipo)
	local h = alvo:FindFirstChildOfClass("Humanoid"); if not h then return 0 end
	local d = base * L.danoMult
	h:TakeDamage(d); log(string.format("%s acertou %s: %.1f (x%.2f)", tipo, alvo.Name, d, L.danoMult))
	K.ultimoDano = {tipo = tipo, alvo = alvo.Name, dano = d, mult = L.danoMult}
	return d
end
-- espera ate o tempo t do clipe (pelo relogio do servidor); cancela se o lobo deixar de existir
local function ate(L, t0, t) while vivo(L) and os.clock() - t0 < t do RS.Heartbeat:Wait() end return vivo(L) end

-- ------------------------------------------------------------------ basicos (fora dos slots)
local function basico(L, nome)
	local c = CFG.Basico[nome]
	local ok, por = podeUsar(L, nome, c); if not ok then return false, por end
	gastar(L, nome, c); L.estado = nome
	local cl = LA.clipe(c.clipe); local tC
	for _, mk in ipairs(cl.marcadores) do if mk.nome == c.marcador then tC = mk.t end end
	L.C.acao(c.clipe, 0.08)
	tarefa(L, function()
		local t0 = os.clock()
		if not ate(L, t0, tC or 0.5) then return end
		local piv = L.modelo:GetPivot(); local melhor, md = nil, math.huge
		for _, a in ipairs(alvosPasta() and alvosPasta():GetChildren() or {}) do
			if alvoValido(a) then
				local d = centro(a) - piv.Position; local dh = Vector3.new(d.X, 0, d.Z)
				local ang = math.deg(math.acos(math.clamp(dh.Unit:Dot(piv.LookVector), -1, 1)))
				if dh.Magnitude <= c.alcance + 2 and ang <= c.cone / 2 and dh.Magnitude < md and linhaDeVisao(L, a) then melhor, md = a, dh.Magnitude end
			end
		end
		if melhor then causarDano(L, melhor, c.dano, nome) else log(nome .. " sem alvo") end
		ate(L, t0, cl.quadros / cl.fps); if vivo(L) then L.estado = "Livre" end
	end)
	return true
end

-- ------------------------------------------------------------------ ATIVA 1: Salto Predatorio
local SP = CFG.SaltoPredatorio
local function salto(L, alvo)
	local ok, por = podeUsar(L, "SaltoPredatorio", SP); if not ok then return false, por end
	if not alvoValido(alvo) then return false, "alvo invalido" end
	local p0 = L.modelo:GetPivot(); local c = centro(alvo)
	local d = Vector3.new(c.X - p0.Position.X, 0, c.Z - p0.Position.Z)
	if d.Magnitude < SP.alcanceMin or d.Magnitude > SP.alcanceMax then return false, string.format("fora de alcance (%.1f)", d.Magnitude) end
	if not linhaDeVisao(L, alvo) then return false, "sem linha de visao" end
	gastar(L, "SaltoPredatorio", SP); L.estado = "SaltoPredatorio"
	local dir = d.Unit
	local destino = Vector3.new(c.X, p0.Position.Y, c.Z) - dir * 3      -- aterrissa diante do alvo (nunca dentro dele)
	L.modelo:PivotTo(CFrame.lookAt(p0.Position, p0.Position + dir))
	L.C.acao(SP.clipe, 0.06)
	if L.dono then EVENTO:FireAllClients("Salto", L.modelo, p0.Position, destino) end
	tarefa(L, function()
		local t0 = os.clock()
		if not ate(L, t0, SP.decolagem) then return end
		local ini = L.modelo:GetPivot().Position; local dist = (destino - ini).Magnitude
		local alt = SP.alturaArco * dist; local prev = ini; local parou = nil
		local fp = filtro(L, {alvo})
		while vivo(L) do
			local u = math.clamp((os.clock() - t0 - SP.decolagem) / SP.voo, 0, 1)
			local pos = ini:Lerp(destino, u) + Vector3.new(0, 4 * alt * u * (1 - u), 0)
			local hit = workspace:Raycast(prev + Vector3.new(0, 3, 0), pos - prev, fp)   -- trajeto bloqueado: para ali e cai
			if hit then
				parou = hit.Position - (pos - prev).Unit * 2.5
				L.modelo:PivotTo(CFrame.lookAt(Vector3.new(parou.X, p0.Position.Y, parou.Z), Vector3.new(parou.X, p0.Position.Y, parou.Z) + dir))
				log("salto interrompido por obstaculo: " .. hit.Instance.Name); break
			end
			L.modelo:PivotTo(CFrame.lookAt(pos, pos + dir)); prev = pos
			if u >= 1 then break end
			RS.Heartbeat:Wait()
		end
		if not vivo(L) then return end
		local fim = L.modelo:GetPivot().Position
		L.modelo:PivotTo(CFrame.lookAt(Vector3.new(fim.X, p0.Position.Y, fim.Z), Vector3.new(fim.X, p0.Position.Y, fim.Z) + dir))
		if not parou and alvoValido(alvo) and (Vector3.new(centro(alvo).X, 0, centro(alvo).Z) - Vector3.new(fim.X, 0, fim.Z)).Magnitude <= SP.raioAcerto then
			causarDano(L, alvo, CFG.Basico.Mordida.dano * SP.multDano, "SaltoPredatorio")
		else log("salto sem acerto" .. (parou and " (obstaculo)" or " (alvo saiu do raio)")) end
		ate(L, t0, SP.golpe + 0.49); if vivo(L) then L.estado = "Livre" end
	end)
	return true
end

-- ------------------------------------------------------------------ ATIVA 2: Uivo Ancestral (so o proprio lobo)
local UV = CFG.UivoAncestral
local function uivo(L)
	local ok, por = podeUsar(L, "UivoAncestral", UV); if not ok then return false, por end
	gastar(L, "UivoAncestral", UV); L.estado = "UivoAncestral"
	L.C.acao(UV.clipe, 0.1)
	tarefa(L, function()
		local t0 = os.clock()
		if not ate(L, t0, UV.buffInicio) then return end
		setMod(L, "UivoAncestral", {vel = UV.velocidade, esq = UV.esquiva})
		L.modelo:SetAttribute("UivoAte", os.clock() + UV.duracao)
		EVENTO:FireAllClients("Uivo", L.modelo, UV.duracao); log("uivo: bonus ligado")
		ate(L, t0, 2.6); if vivo(L) and L.estado == "UivoAncestral" then L.estado = "Livre" end
		if not ate(L, t0, UV.buffInicio + UV.duracao) then return end
		setMod(L, "UivoAncestral", nil); L.modelo:SetAttribute("UivoAte", nil); log("uivo: bonus desligado")
	end)
	return true
end

-- ------------------------------------------------------------------ ATIVA 3: Investida (direcao escolhida)
local IV = CFG.Investida
local VEL_GALOPE = 21.43
local function velInvestida(t)        -- = clipes_kit30/Investida_velocidade.json (sincronizado com as patas)
	local function s(x) x = math.clamp(x, 0, 1); return x * x * (3 - 2 * x) end
	if t < 0.22 then return 0 elseif t < 0.36 then return VEL_GALOPE * s((t - 0.22) / 0.14)
	elseif t < 0.78 then return VEL_GALOPE elseif t < 0.96 then return VEL_GALOPE * (1 - s((t - 0.78) / 0.18)) end
	return 0
end
local function investida(L, dir)
	local ok, por = podeUsar(L, "Investida", IV); if not ok then return false, por end
	if typeof(dir) ~= "Vector3" then return false, "direcao invalida" end
	dir = Vector3.new(dir.X, 0, dir.Z); if dir.Magnitude < 0.1 then return false, "direcao invalida" end
	dir = dir.Unit
	gastar(L, "Investida", IV); L.estado = "Investida"
	local p0 = L.modelo:GetPivot().Position
	L.modelo:PivotTo(CFrame.lookAt(p0, p0 + dir))
	L.C.acao(IV.clipe, 0.06)
	EVENTO:FireAllClients("Investida", L.modelo, dir)
	tarefa(L, function()
		local t0 = os.clock(); local acertou = {}; local parado = false
		local fp = filtro(L)
		local ultimo = 0
		while vivo(L) do
			local t = os.clock() - t0; if t >= 1.2 then break end
			local dt = t - ultimo; ultimo = t
			local v = parado and 0 or velInvestida(t)
			if v > 0 then
				local pos = L.modelo:GetPivot().Position; local passo = dir * v * dt
				-- obstaculo: caixa da largura do lobo a frente do peito (alvos validos contam como acerto, nao como parede)
				local cf = CFrame.lookAt(pos + Vector3.new(0, 3.5, 0), pos + Vector3.new(0, 3.5, 0) + dir)
				local hit = workspace:Blockcast(cf, Vector3.new(IV.largura, 4, 1), dir * (passo.Magnitude + 6.5), fp)
				local alvo = hit and hit.Instance:FindFirstAncestorOfClass("Model")
				if hit and alvo and alvoValido(alvo) then
					if not acertou[alvo] and (hit.Position - pos).Magnitude <= 6.5 + IV.alcanceMordida then
						acertou[alvo] = true; causarDano(L, alvo, CFG.Basico.Mordida.dano * IV.multDano, "Investida")
						parado = true; log("investida parou no primeiro alvo")
					end
				elseif hit and hit.Distance < passo.Magnitude + 0.5 then
					parado = true; log("investida parou em obstaculo: " .. hit.Instance.Name)
				end
				if not parado then L.modelo:PivotTo(CFrame.lookAt(pos + passo, pos + passo + dir)) end
			end
			RS.Heartbeat:Wait()
		end
		if vivo(L) then L.estado = "Livre" end
		K.ultimaInvestida = {dist = (L.modelo:GetPivot().Position - p0).Magnitude, acertos = (function() local n = 0 for _ in pairs(acertou) do n += 1 end return n end)()}
	end)
	return true
end

-- ------------------------------------------------------------------ pedidos (mesmo caminho para o remoto e os testes)
local ACOES = {SaltoPredatorio = function(L, d) return salto(L, d) end, UivoAncestral = function(L) return uivo(L) end,
	Investida = function(L, d) return investida(L, d) end, Mordida = function(L) return basico(L, "Mordida") end,
	Garra = function(L) return basico(L, "Garra") end}
function K.pedido(jogador, modelo, acao, dados)
	local L = K.lobos[modelo]
	if not L then return false, "lobo desconhecido" end
	if L.dono ~= jogador then return false, "nao e o dono" end
	local f = ACOES[acao]; if type(acao) ~= "string" or not f then return false, "acao invalida" end
	local ok, por = f(L, dados)
	log(string.format("pedido %s -> %s %s", acao, tostring(ok), por or ""))
	return ok, por
end
local ultimoPedido = {}
PEDIDO.OnServerEvent:Connect(function(jogador, modelo, acao, dados)
	local t = os.clock(); if ultimoPedido[jogador] and t - ultimoPedido[jogador] < 0.1 then return end   -- limite de spam
	ultimoPedido[jogador] = t
	local ok, por = K.pedido(jogador, modelo, acao, dados)
	EVENTO:FireClient(jogador, "Resposta", modelo, acao, ok, por)
end)

-- ------------------------------------------------------------------ seguir o dono a pe (andar/corrida nas velocidades dos clipes)
RS.Heartbeat:Connect(function(dt)
	for _, L in pairs(K.lobos) do
		if vivo(L) and L.estado == "Livre" and L.dono and L.dono.Character and L.dono.Character.PrimaryPart and not L.parado then
			local piv = L.modelo:GetPivot(); local alvo = L.dono.Character.PrimaryPart.Position
			local d = Vector3.new(alvo.X - piv.Position.X, 0, alvo.Z - piv.Position.Z)
			local dist = d.Magnitude
			local mv = CFG.Movimento
			if dist > mv.distSeguir or (L.seguindo and dist > mv.distParar) then
				L.seguindo = true
				local corre = dist > 25
				local v = (corre and mv.corrida or mv.andar) * L.velMult
				L.C.base(corre and "Corrida" or "Andar", 0.25, L.velMult)      -- a passada acelera junto: sem patinar
				local dir = d.Unit; local yaw = piv.LookVector:Lerp(dir, math.min(1, dt * 6))
				local novo = piv.Position + dir * math.min(v * dt, dist)
				L.modelo:PivotTo(CFrame.lookAt(novo, novo + Vector3.new(yaw.X, 0, yaw.Z)))
			elseif L.seguindo then
				L.seguindo = false; L.C.base("Repouso", 0.3)
			end
		end
	end
end)

-- lobo do teste: dono = primeiro jogador que entrar
local function iniciar(jogador)
	local m = AREA:FindFirstChild("Lobo_Ancestral")
	if m and not K.lobos[m] then registrar(m, jogador) end
end
Players.PlayerAdded:Connect(iniciar)
for _, p in ipairs(Players:GetPlayers()) do iniciar(p) end
K.registrar = registrar
]==]
s.Parent = f
local sps = game.StarterPlayer.StarterPlayerScripts
local c = sps:FindFirstChild("LoboKit_Cliente") or Instance.new("LocalScript"); c.Name = "LoboKit_Cliente"
c.Source = [==[-- LoboKit_Cliente (LocalScript em StarterPlayer.StarterPlayerScripts) - entrada, HUD minima e efeitos discretos do kit
-- Natureza do Lobo Ancestral (prototipo, place isolado, 15/11/2026). Fonte: studio/kit/LoboKit_Cliente.luau.
-- O cliente so PEDE (PedidoKit) e mostra; dano, alvo, alcance, recarga e bonus sao decididos no servidor.
-- Teclas (prototipo): Z = Salto Predatorio (alvo sob o mouse), X = Uivo Ancestral, C = Investida (direcao do mouse no chao),
-- V = Mordida, B = Garra (basicos, fora dos slots). Sons: nao ha sons do lobo no projeto ainda (pendente).
local Players = game:GetService("Players")
local UIS = game:GetService("UserInputService")
local Debris = game:GetService("Debris")
local TweenService = game:GetService("TweenService")
local Rep = game:GetService("ReplicatedStorage")
local PASTA = Rep:WaitForChild("LoboAncestral")
local REM = PASTA:WaitForChild("Remotes")
local PEDIDO, EVENTO = REM:WaitForChild("PedidoKit"), REM:WaitForChild("EventoKit")
local eu = Players.LocalPlayer
local mouse = eu:GetMouse()
local AREA = workspace:WaitForChild("Teste_LoboAncestral")

local function meuLobo()
	for _, m in ipairs(AREA:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("DonoUserId") == eu.UserId then return m end
	end
end
-- HUD minima: estado, energia, bonus e ultima resposta
local gui = Instance.new("ScreenGui"); gui.Name = "LoboKitHUD"; gui.ResetOnSpawn = false; gui.Parent = eu:WaitForChild("PlayerGui")
local txt = Instance.new("TextLabel"); txt.Size = UDim2.new(0, 360, 0, 92); txt.Position = UDim2.new(0, 12, 1, -104)
txt.BackgroundTransparency = 0.45; txt.BackgroundColor3 = Color3.fromRGB(20, 26, 20); txt.TextColor3 = Color3.fromRGB(225, 235, 215)
txt.TextXAlignment = Enum.TextXAlignment.Left; txt.TextYAlignment = Enum.TextYAlignment.Top; txt.Font = Enum.Font.Gotham; txt.TextSize = 13
txt.Text = "Lobo Ancestral"; txt.Parent = gui
local ultima = ""
task.spawn(function()
	while true do
		local m = meuLobo()
		if m then
			local function rec(n) local r = m:GetAttribute("Recarga_" .. n); local s = r and (r - os.clock()) or 0; return s > 0 and string.format("%.0f", s) or "ok" end
			txt.Text = string.format("Lobo Ancestral  Vida %s  Energia %s  %s\nZ Salto %s | X Uivo %s | C Investida %s | V/B basicos\nBonus: %s  (vel x%.2f, esquiva %.0f%%, dano x%.2f)\n%s",
				tostring(m:GetAttribute("Vida")), tostring(m:GetAttribute("Energia")), m:GetAttribute("Noite") and "NOITE" or "dia",
				rec("SaltoPredatorio"), rec("UivoAncestral"), rec("Investida"), m:GetAttribute("Bonus") ~= "" and m:GetAttribute("Bonus") or "-",
				m:GetAttribute("VelMult") or 1, (m:GetAttribute("Esquiva") or 0) * 100, m:GetAttribute("DanoMult") or 1, ultima)
		end
		task.wait(0.2)
	end
end)

local function alvoSobMouse()
	local t = mouse.Target
	local m = t and t:FindFirstAncestorOfClass("Model")
	return m
end
UIS.InputBegan:Connect(function(inp, gp)
	if gp then return end
	local m = meuLobo(); if not m then return end
	local k = inp.KeyCode
	if k == Enum.KeyCode.Z then PEDIDO:FireServer(m, "SaltoPredatorio", alvoSobMouse())
	elseif k == Enum.KeyCode.X then PEDIDO:FireServer(m, "UivoAncestral")
	elseif k == Enum.KeyCode.C then
		local d = mouse.Hit.Position - m:GetPivot().Position
		PEDIDO:FireServer(m, "Investida", Vector3.new(d.X, 0, d.Z))
	elseif k == Enum.KeyCode.V then PEDIDO:FireServer(m, "Mordida")
	elseif k == Enum.KeyCode.B then PEDIDO:FireServer(m, "Garra") end
end)

-- ------------------------------------------------------------------ efeitos discretos (folhas/vento, sem brilho constante)
local VERDE = Color3.fromRGB(96, 128, 64)
local function folhas(cf, qtd, vel, vida)
	local a = Instance.new("Attachment"); a.WorldCFrame = cf; a.Parent = workspace.Terrain
	local pe = Instance.new("ParticleEmitter")
	pe.Texture = "rbxasset://textures/particles/sparkles_main.dds"
	pe.Color = ColorSequence.new(VERDE, Color3.fromRGB(150, 140, 80)); pe.LightEmission = 0; pe.LightInfluence = 1
	pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.25), NumberSequenceKeypoint.new(1, 0.05)})
	pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1)})
	pe.Lifetime = NumberRange.new(vida * 0.6, vida); pe.Speed = NumberRange.new(vel * 0.5, vel); pe.SpreadAngle = Vector2.new(40, 40)
	pe.Rotation = NumberRange.new(0, 360); pe.RotSpeed = NumberRange.new(-180, 180); pe.Drag = 2; pe.Acceleration = Vector3.new(0, -3, 0)
	pe.Enabled = false; pe.Parent = a; pe:Emit(qtd)
	Debris:AddItem(a, vida + 0.5)
end
local function rastroVento(m, dur)
	local root = m:FindFirstChild("RootPart"); if not root then return end
	local a0 = Instance.new("Attachment", root); a0.Position = Vector3.new(0.9, 4.2, 2)
	local a1 = Instance.new("Attachment", root); a1.Position = Vector3.new(-0.9, 4.2, 2)
	local tr = Instance.new("Trail"); tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Lifetime = 0.25
	tr.Color = ColorSequence.new(Color3.fromRGB(205, 215, 190)); tr.LightEmission = 0
	tr.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.75), NumberSequenceKeypoint.new(1, 1)})
	tr.WidthScale = NumberSequence.new(1, 0.2); tr.Parent = root
	task.delay(dur, function() tr.Enabled = false; Debris:AddItem(tr, 0.4); Debris:AddItem(a0, 0.4); Debris:AddItem(a1, 0.4) end)
end
local pegadas = {}
local function pegada(p)
	local k = string.format("%d_%d", math.floor(p.X / 2), math.floor(p.Z / 2))
	if pegadas[k] then return end
	local d = Instance.new("Part"); d.Anchored = true; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.CastShadow = false
	d.Size = Vector3.new(0.7, 0.05, 0.9); d.Color = Color3.fromRGB(70, 60, 45); d.Material = Enum.Material.SmoothPlastic; d.Transparency = 0.45
	d.CFrame = CFrame.new(p + Vector3.new(math.random() - 0.5, 0.03, math.random() - 0.5)) * CFrame.Angles(0, math.random() * 6.28, 0)
	d.Name = "PegadaInstinto"; d.Parent = workspace.Terrain; pegadas[k] = d
	TweenService:Create(d, TweenInfo.new(6), {Transparency = 1}):Play()
	task.delay(6, function() pegadas[k] = nil; d:Destroy() end)
end
EVENTO.OnClientEvent:Connect(function(tipo, m, a, b, c, d)
	if tipo == "Resposta" then ultima = string.format("%s: %s %s", tostring(a), b and "ok" or "recusado", c or "")
	elseif tipo == "Pegadas" then for _, p in ipairs(a) do pegada(p) end
	elseif tipo == "PistaNinho" then
		local base = m:GetPivot().Position + Vector3.new(0, 3, 0)
		folhas(CFrame.lookAt(base, base + a) * CFrame.Angles(0, 0, 0), 12, 14, 1.4)  -- rajada curta de folhas na direcao aproximada
	elseif tipo == "Salto" then folhas(CFrame.new(a + Vector3.new(0, 1, 0)), 10, 6, 1.0); task.delay(0.86, function() folhas(CFrame.new(b + Vector3.new(0, 0.5, 0)), 14, 8, 1.0) end)
	elseif tipo == "Uivo" then
		local root = m:FindFirstChild("RootPart")
		for i = 0, 2 do task.delay(i * 0.5, function() if m.Parent then folhas(m:GetPivot() * CFrame.new(0, 6, -3), 8, 5, 1.6) end end) end
	elseif tipo == "Investida" then task.delay(0.22, function() rastroVento(m, 0.74) end)
	elseif tipo == "Noite" then ultima = a and "Cacador Noturno ativo (noite)" or "Cacador Noturno inativo (dia)" end
end)
]==]
c.Parent = sps
return "ok " .. #s.Source .. " " .. #c.Source
