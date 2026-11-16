-- LoboKit_Servidor (Script em ServerScriptService.LoboAncestral_Kit) - kit Natureza do Lobo Ancestral, PROTOTIPO no place
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
	if noiteGlobalRef and noiteGlobalRef() then setMod(L, "CacadorNoturno", {vel = CFG.CacadorNoturno.velocidade, esq = CFG.CacadorNoturno.esquiva, dano = CFG.CacadorNoturno.danoFisico}); modelo:SetAttribute("Noite", true) end
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
noiteGlobalRef = function() return noiteGlobal end
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
				K.ultimasPegadas = #pistas
				if #pistas > 0 then EVENTO:FireClient(L.dono, "Pegadas", L.modelo, pistas) end
				if t % IC.ninhoIntervalo < IC.intervalo then
					for _, n in ipairs(AREA:GetDescendants()) do
						if n:IsA("BasePart") and n:GetAttribute("PistaNinho") then
							local d = n.Position - L.modelo:GetPivot().Position
							if Vector3.new(d.X, 0, d.Z).Magnitude <= IC.ninhoRaio then
								local ang = math.atan2(d.X, d.Z) + math.rad((math.random() * 2 - 1) * IC.ninhoErroGraus)
								local dirN = Vector3.new(math.sin(ang), 0, math.cos(ang))
								K.ultimaPistaNinho = {dir = dirN, erroGraus = math.deg(math.acos(math.clamp(dirN:Dot(Vector3.new(d.X, 0, d.Z).Unit), -1, 1)))}
								EVENTO:FireClient(L.dono, "PistaNinho", L.modelo, dirN)
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
	EVENTO:FireAllClients("Salto", L.modelo, p0.Position, destino)
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
					if not acertou[alvo] and hit.Distance <= 6.5 + IV.alcanceMordida then
						acertou[alvo] = true; causarDano(L, alvo, CFG.Basico.Mordida.dano * IV.multDano, "Investida")
						parado = true; log("investida parou no primeiro alvo")
					end
				elseif hit and hit.Distance < passo.Magnitude + 6.0 then   -- focinho fica ~6 studs a frente do pivo
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

-- ------------------------------------------------------------------ gancho de TESTE (so Studio; ServerStorage nao replica)
-- usa exatamente K.pedido / K.receberDano / K.morrer; nao ha atalho que pule a validacao
if RS:IsStudio() then
	local bf = game.ServerStorage:FindFirstChild("LoboKitTeste") or Instance.new("BindableFunction")
	bf.Name = "LoboKitTeste"; bf.Parent = game.ServerStorage
	local function umLobo(m) if m then return K.lobos[m] end for _, x in pairs(K.lobos) do if x.modelo.Name == "Lobo_Ancestral" then return x end end end
	bf.OnInvoke = function(cmd, a, b, c)
		local jogador = Players:GetPlayers()[1]
		if cmd == "pedido" then local L = umLobo(c); return K.pedido(jogador, L and L.modelo, a, b)
		elseif cmd == "pedidoOutro" then local L = umLobo(); return K.pedido("outro", L and L.modelo, a, b)
		elseif cmd == "estado" then
			local L = umLobo(a); if not L then return {existe = false} end
			local fontes = {} for k in pairs(L.mods) do table.insert(fontes, k) end
			local lg = {} for i = math.max(1, #K.log - (b or 8) + 1), #K.log do table.insert(lg, K.log[i]) end
			return {existe = true, ativo = L.ativo, estado = L.estado, energia = L.energia, vida = L.vida, velMult = L.velMult, esquiva = L.esquiva,
				danoMult = L.danoMult, bonus = table.concat(fontes, ","), noite = K.ehNoite(), pos = L.modelo:GetPivot().Position,
				ultimoDano = K.ultimoDano, ultimaInvestida = K.ultimaInvestida, pegadas = K.ultimasPegadas, ninho = K.ultimaPistaNinho, log = lg}
		elseif cmd == "dano" then
			local L = umLobo(); local r = {acertou = 0, esquivou = 0, morto = 0}
			for _ = 1, b or 1 do local x = K.receberDano(L, a); r[x] += 1 end
			return r
		elseif cmd == "morrer" then K.morrer(umLobo(a)); return true
		elseif cmd == "reviver" then local L = umLobo(); L.vida = CFG.Vida; L.estado = "Livre"; L.modelo:SetAttribute("Estado", nil); L.C.pararTudo(0); L.C.base("Repouso", 0); recalcular(L)
			if K.ehNoite() then setMod(L, "CacadorNoturno", {vel = CN.velocidade, esq = CN.esquiva, dano = CN.danoFisico}) end; return true
		elseif cmd == "recargas" then local L = umLobo(); L.recargas = {}; L.energia = CFG.Energia.max; return true
		elseif cmd == "parado" then local L = umLobo(); L.parado = a; return true
		elseif cmd == "pivo" then local L = umLobo(); L.modelo:PivotTo(a); return true
		elseif cmd == "clonar" then local L0 = umLobo(); local m2 = L0.modelo:Clone(); m2.Name = "Lobo_Clone"; m2.Parent = AREA; m2:PivotTo(a or CFrame.new(-680, 0, -680)); local L2 = registrar(m2, jogador); L2.parado = true; return m2
		end
	end
end
