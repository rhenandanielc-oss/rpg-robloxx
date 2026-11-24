-- IA_LoboArtico (Script dentro da pasta de UM lobo selvagem, criada pelo IA_LoboArtico_Servidor) - r1e 19/11/2026 (destrava; cadeia da toca completa ate o Abrigo).
-- Pedido do usuario 19/11: "prossiga com a ida, ninhos, spawn no habitat, IA selvagem" + "o lobo ja tem cavernas para
-- esconder seus ovos e dormir la". Numeros e rotina = [PROPOSTA][A TESTAR]; nada aqui e regra oficial nova.
-- O cerebro so decide; quem move e o Controle_Servidor (r6, IA_Mover: direcao + marcha, mesmos clipes/transicoes),
-- quem ataca e o Kit_Servidor (r14, IA_Acao) e quem uiva e o Uivo_Servidor (r7, via IA_PedirUivo).
-- Rotinas (pesos em CFG): dormir/descansar na camara de Descanso da toca, patrulhar a Rota_Patrulha, cacar (farejar) nas
-- Zonas_Caca, guardar o ovo (Abrigo_Filhotes). Defesa: jogador perto do ovo/toca (ou que ataca o lobo) vira alvo;
-- o lider uiva (aviso) e a alcateia persegue mordendo; desiste fora da coleira (RaioColeira do ovo) e volta.
-- Desempenho: tick 0,3 s com jogador perto, 2 s sem jogador a menos de CFG.raioDormente (so rotinas paradas).
local Players = game:GetService("Players")
local PFS = game:GetService("PathfindingService")
local KSP = game:GetService("KeyframeSequenceProvider")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local lib = game:GetService("ReplicatedStorage"):WaitForChild("Animacoes_LoboArtico")
local A = pasta:GetAttribute("Alcateia")
local habitat = workspace.Tundra_Congelada.Habitats.Ecologia_Fauna.Lobo_Artico:FindFirstChild(pasta:GetAttribute("AlcateiaPasta") or "")
assert(habitat, "habitat da alcateia nao achado")

local CFG = {
	raioAlerta = 40, raioDefesa = 22, raioColeira = 75,      -- do ovo/abrigo (Urso usa 40/22/60) [PROPOSTA]
	raioPercepcao = 60, raioDormente = 600,
	tick = 0.3, tickDormente = 2,
	distMordida = 9.5, intervaloMordida = 0.55,
	pesos = {Dormir = 2, Patrulhar = 3, Cacar = 2, Guardar = 2},
	patrulhaPasso = 4,                                         -- usa 1 de cada 4 pontos da rota
	chegada = 5, repath = 2.5,
	durDormir = {60, 140}, durGuardar = {30, 70}, durCacar = {25, 50},
	nocauteSeg = 60,
}
local evMover = pasta:WaitForChild("IA_Mover")
local evAcao = pasta:WaitForChild("IA_Acao")
local evUivo = pasta:WaitForChild("IA_PedirUivo")
local function P(nome) local p = habitat:FindFirstChild(nome, true); return p and p.Position end
local pontoDescanso, pontoAbrigo, pontoEntrada = P("Descanso_Toca"), P("Abrigo_Filhotes"), P("Entrada_Toca")
local zonas = {}; for _, z in ipairs(habitat.Zonas_Caca:GetChildren()) do table.insert(zonas, z.Position) end
local rota = {}
do
	local ok, pts = pcall(function() return game:GetService("HttpService"):JSONDecode(habitat.Rotas_Patrulha.Rota_Patrulha:GetAttribute("Pontos")) end)
	if ok and pts then for i = 1, #pts, CFG.patrulhaPasso do table.insert(rota, Vector3.new(pts[i][1], pts[i][2], pts[i][3])) end end
end
local papel = pasta:GetAttribute("Papel") or "Membro"           -- Lider / Guardiao / Membro

-- animacoes de vida (o Controle toca Repouso/locomocao; estas ficam por cima com prioridade Action, so parado)
local animator = lobo.AnimationController:FindFirstChildOfClass("Animator") or Instance.new("Animator", lobo.AnimationController)
local faixas = {}
local function faixa(n)
	if faixas[n] == nil then
		local k = lib:FindFirstChild("LoboArtico_" .. n)
		if not k then faixas[n] = false; return nil end
		local a = Instance.new("Animation"); a.AnimationId = KSP:RegisterKeyframeSequence(k)
		faixas[n] = animator:LoadAnimation(a); faixas[n].Priority = Enum.AnimationPriority.Action
	end
	return faixas[n] or nil
end
local poseAtual
local function pose(n, fade)
	if poseAtual == n then return end
	for nome, f in pairs(faixas) do if f and nome ~= n and f.IsPlaying then f:Stop(fade or 0.4) end end
	poseAtual = n
	if n then local f = faixa(n); if f then f:Play(fade or 0.4) end end
end
local function tocarUmaVez(n, depois)
	local f = faixa(n); if not f then return 0 end
	for nome, g in pairs(faixas) do if g and g ~= f and g.IsPlaying then g:Stop(0.3) end end
	f.Looped = false; f:Play(0.3); poseAtual = depois
	if depois then task.delay(f.Length - 0.1, function() if poseAtual == depois then local g = faixa(depois); if g then g:Play(0.3) end end end) end
	return f.Length
end

-- movimento por caminho (Pathfinding) -> direcao para o Controle
local caminho, idx, alvoCaminho, ultimoPath = nil, 1, nil, 0
local travaRef, travaT, falhas = nil, 0, 0
local estadoAte                                                  -- (declarado aqui para o irPara poder desistir da rotina)
local function parar() evMover:Fire(Vector3.zero, "andar") end
local function pos() return lobo:GetPivot().Position end
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function irParaFora(destino, marcha)
	local agora = os.clock()
	if not alvoCaminho or (alvoCaminho - destino).Magnitude > 4 or agora - ultimoPath > CFG.repath then
		alvoCaminho, ultimoPath = destino, agora
		local path = PFS:CreatePath({AgentRadius = 3, AgentHeight = 7, AgentCanJump = false, WaypointSpacing = 8})
		local ok = pcall(function() path:ComputeAsync(pos(), destino) end)
		if ok and path.Status == Enum.PathStatus.Success then caminho = path:GetWaypoints(); idx = math.min(2, #caminho)
		else caminho = {{Position = destino}}; idx = 1 end
	end
	local p = pos()
	if plano(destino - p).Magnitude < CFG.chegada then travaRef = nil; falhas = 0; parar(); return true end
	-- r1b: travado (mexeu < 1 stud em 3 s querendo andar) -> pula para o proximo ponto e recalcula; 3 falhas = desiste
	if not travaRef or (p - travaRef).Magnitude > 1 then travaRef, travaT = p, os.clock()
	elseif os.clock() - travaT > 3 then
		travaRef, travaT = p, os.clock(); falhas += 1; ultimoPath = 0
		if caminho and idx < #caminho then idx += 1 end
		if falhas >= 3 then falhas = 0; estadoAte = 0; parar(); return true end
	end
	while caminho and caminho[idx] and plano(caminho[idx].Position - p).Magnitude < CFG.chegada and idx < #caminho do idx += 1 end
	local wp = caminho and caminho[idx] and caminho[idx].Position or destino
	local d = plano(wp - p)
	if plano(destino - p).Magnitude < CFG.chegada then parar(); return true end
	pose(nil); evMover:Fire(d, marcha)
	return false
end

-- r1c: a toca e estreita demais para o Pathfinding com o tamanho do lobo (NoPath dentro dela). Na 1a vez, calcula a
-- "cadeia da toca" (Entrada -> Descanso -> Abrigo) com um agente pequeno; dentro da toca o lobo segue a cadeia em linha
-- reta ponto a ponto, fora dela usa o Pathfinding normal.
local cadeia
local function construirCadeia()
	local c = {pontoEntrada}
	local path = PFS:CreatePath({AgentRadius = 1, AgentHeight = 3, AgentCanJump = true, WaypointSpacing = 6})
	pcall(function() path:ComputeAsync(pontoEntrada, pontoDescanso) end)
	if path.Status == Enum.PathStatus.Success then for _, w in ipairs(path:GetWaypoints()) do table.insert(c, w.Position) end end
	table.insert(c, pontoDescanso)
	local n = math.max(1, math.floor((pontoAbrigo - pontoDescanso).Magnitude / 6))   -- r1e: trecho Descanso->Abrigo em pontos de 6
	for k = 1, n do table.insert(c, pontoDescanso:Lerp(pontoAbrigo, k / n)) end
	pasta:SetAttribute("IA_CadeiaToca", #c)
	return c
end
local function prox(p)
	local bi, bd = 1, math.huge
	for i, q in ipairs(cadeia) do local d = (q - p).Magnitude; if d < bd then bi, bd = i, d end end
	return bi, bd
end
local function andarReto(ponto, marcha)
	local d = plano(ponto - pos())
	if d.Magnitude < CFG.chegada then return true end
	pose(nil); evMover:Fire(d, marcha); return false
end
local function irPara(destino, marcha)
	cadeia = cadeia or construirCadeia()
	local ip, dp = prox(pos()); local it, dt = prox(destino)
	local loboDentro = ip > 1 and dp < 15
	local destDentro = it > 1 and dt < 15
	if not loboDentro and not destDentro then return irParaFora(destino, marcha) end
	if not loboDentro then irParaFora(pontoEntrada, marcha); if (pontoEntrada - pos()).Magnitude > CFG.chegada + 2 then return false end; ip = 1 end
	local alvoI = destDentro and it or 1
	if ip == alvoI then
		if destDentro then return andarReto(destino, "andar") end
		return irParaFora(destino, marcha)                               -- saiu pela entrada
	end
	local passo = alvoI > ip and 1 or -1
	local prox_i = ip
	if (cadeia[ip] - pos()).Magnitude <= 6 then                          -- ja na linha: proximo ponto que ainda esta longe
		prox_i = ip + passo
		while prox_i ~= alvoI and plano(cadeia[prox_i] - pos()).Magnitude < CFG.chegada do prox_i += passo end
	end
	if prox_i == alvoI and plano(cadeia[alvoI] - pos()).Magnitude < CFG.chegada then
		if destDentro then return andarReto(destino, "andar") end
		return irParaFora(destino, marcha)
	end
	andarReto(cadeia[prox_i], "andar")
	return false
end

-- percepcao
local function jogadoresPerto(centro, raio)
	local melhor, dm
	for _, j in ipairs(Players:GetPlayers()) do
		local c = j.Character; local h = c and c:FindFirstChildOfClass("Humanoid"); local r = c and c:FindFirstChild("HumanoidRootPart")
		if h and r and h.Health > 0 then
			local d = (r.Position - centro).Magnitude
			if d <= raio and math.abs(r.Position.Y - centro.Y) < 30 and (not dm or d < dm) then melhor, dm = c, d end
		end
	end
	return melhor, dm
end
local function jogadorMaisPerto()
	local dm = math.huge
	for _, j in ipairs(Players:GetPlayers()) do
		local r = j.Character and j.Character:FindFirstChild("HumanoidRootPart")
		if r then dm = math.min(dm, (r.Position - pos()).Magnitude) end
	end
	return dm
end
-- alerta compartilhado pela alcateia (atributo na pasta da alcateia, escrito pelo servidor do ovo ou por um membro)
local pastaAlcateia = pasta.Parent
local function alvoAlcateia()
	local nome = pastaAlcateia:GetAttribute("AlvoJogador")
	local ate = pastaAlcateia:GetAttribute("AlvoAte") or 0
	if not nome or os.clock() > ate then return nil end
	local j = Players:FindFirstChild(nome); return j and j.Character
end
local function avisar(c, seg) local j = Players:GetPlayerFromCharacter(c); if j then pastaAlcateia:SetAttribute("AlvoJogador", j.Name); pastaAlcateia:SetAttribute("AlvoAte", os.clock() + (seg or 12)) end end
-- dano recebido -> o atacante vira alvo (o Kit_Servidor.ReceberDano so desconta vida; quem bate e outro sistema)
local vidaAnt = lobo:GetAttribute("Vida") or 400
lobo:GetAttributeChangedSignal("Vida"):Connect(function()
	local v = lobo:GetAttribute("Vida") or 0
	if v < vidaAnt then local c = jogadoresPerto(pos(), 30); if c then avisar(c, 15) end end
	vidaAnt = v
end)

-- rotinas
local estado, alvoRotina = nil, nil
estadoAte = 0
local function rand(a) return a[1] + math.random() * (a[2] - a[1]) end
local function escolherRotina()
	local soma, lista = 0, {}
	for n, w in pairs(CFG.pesos) do
		if papel == "Guardiao" and n == "Patrulhar" then w = 0 end
		if papel == "Guardiao" and n == "Guardar" then w = w * 3 end
		local noite = game.Lighting.ClockTime < 6 or game.Lighting.ClockTime > 19
		if n == "Dormir" and noite then w = w * 3 end
		soma += w; table.insert(lista, {n, w})
	end
	local r = math.random() * soma
	for _, e in ipairs(lista) do r -= e[2]; if r <= 0 then return e[1] end end
	return "Guardar"
end
local function iniciar(n)
	estado = n; alvoRotina = nil
	if n == "Dormir" then estadoAte = os.clock() + rand(CFG.durDormir); alvoRotina = pontoDescanso + Vector3.new(math.random(-4, 4), 0, math.random(-4, 4))
	elseif n == "Guardar" then estadoAte = os.clock() + rand(CFG.durGuardar); alvoRotina = pontoAbrigo + Vector3.new(math.random(-5, 5), 0, math.random(-5, 5))
	elseif n == "Cacar" then estadoAte = os.clock() + rand(CFG.durCacar) + 60; alvoRotina = zonas[math.random(1, math.max(1, #zonas))]
	elseif n == "Patrulhar" then estadoAte = os.clock() + 240; alvoRotina = 1 end
	pasta:SetAttribute("IA_Estado", n)
end
local chegouEm
local function rotina()
	if not estado or os.clock() > estadoAte then iniciar(escolherRotina()); chegouEm = nil end
	if estado == "Patrulhar" then
		if #rota == 0 then estadoAte = 0; return end
		if irPara(rota[alvoRotina], "andar") then alvoRotina += 1; if alvoRotina > #rota then estadoAte = 0 end end
		return
	end
	local alvo = alvoRotina or pontoDescanso
	if not chegouEm then
		local marcha = (plano(alvo - pos()).Magnitude > 60) and "trote" or "andar"
		if irPara(alvo, marcha) then chegouEm = os.clock()
			if estado == "Dormir" then tocarUmaVez("Deitar", "Dormindo")
			elseif estado == "Cacar" then tocarUmaVez("Farejar", "Farejando"); estadoAte = os.clock() + rand(CFG.durCacar)
			elseif estado == "Guardar" then pose(nil) end
		end
	elseif estado == "Guardar" and math.random() < 0.02 then tocarUmaVez(math.random() < 0.5 and "Sacudir" or "Farejar", nil)
	end
end
local function sairDaPose()
	if poseAtual == "Dormindo" then tocarUmaVez("Despertar", nil); task.wait(1.2); tocarUmaVez("LevantarDeitado", nil); task.wait(1.6)
	elseif poseAtual == "Farejando" then tocarUmaVez("PararFarejar", nil); task.wait(0.6) end
	pose(nil)
end

-- defesa
local ultimaMordida, uivou = 0, 0
local function defender(c)
	local r = c:FindFirstChild("HumanoidRootPart"); if not r then return end
	if poseAtual then sairDaPose() end
	estado = nil; pasta:SetAttribute("IA_Estado", "Defender")
	local d = plano(r.Position - pos()).Magnitude
	if papel == "Lider" and os.clock() - uivou > 40 and d > 14 then          -- aviso: para e uiva (Uivo Boreal com bonus)
		uivou = os.clock(); parar(); task.wait(0.4); evUivo:Fire(); task.wait(6.5); return
	end
	if d > CFG.distMordida then irPara(r.Position, d > 25 and "correr" or "trote")
	else
		evMover:Fire(plano(r.Position - pos()), "andar")                  -- continua andando para o alvo e morde
		if os.clock() - ultimaMordida > CFG.intervaloMordida then ultimaMordida = os.clock(); evAcao:Fire("basico", c) end
	end
end

-- nocaute (vida 0): deita e se recupera [PROPOSTA]; nao morre nem e capturavel (guardiao selvagem, regra oficial)
local function nocaute()
	pasta:SetAttribute("IA_Estado", "Nocaute"); parar(); tocarUmaVez("Deitar", "Dormindo"); lobo:SetAttribute("Incapacitado", true)
	task.wait(CFG.nocauteSeg)
	lobo:SetAttribute("Vida", lobo:GetAttribute("VidaMax") or 400); lobo:SetAttribute("Incapacitado", nil)
	sairDaPose(); estado = nil
end

lobo:SetAttribute("Selvagem", true)
task.wait(math.random() * 2)
while lobo.Parent do
	if workspace:GetAttribute("IA_LoboArtico_Ativa") == false then parar(); task.wait(2); continue end
	if (lobo:GetAttribute("Vida") or 1) <= 0 then nocaute(); continue end
	local dormente = jogadorMaisPerto() > CFG.raioDormente
	if dormente then
		if estado ~= "Dormir" or not chegouEm then parar() end
		task.wait(CFG.tickDormente); continue
	end
	-- intrusos: perto do ovo/abrigo (alerta) ou do proprio lobo (percepcao), ou alvo avisado pela alcateia
	local intruso = alvoAlcateia()
	local cAbr = jogadoresPerto(pontoAbrigo, CFG.raioAlerta)
	if cAbr then avisar(cAbr, 10); intruso = intruso or cAbr end
	if not intruso and papel ~= "Guardiao" then local c = jogadoresPerto(pos(), CFG.raioDefesa); if c then intruso = c end end
	if intruso then
		local r = intruso:FindFirstChild("HumanoidRootPart")
		if r and (r.Position - pontoAbrigo).Magnitude <= CFG.raioColeira or (r and (r.Position - pos()).Magnitude < CFG.raioDefesa) then
			defender(intruso)
		else
			pastaAlcateia:SetAttribute("AlvoJogador", nil); estado = nil      -- fora da coleira: desiste e volta
		end
	else
		rotina()
	end
	task.wait(CFG.tick)
end
