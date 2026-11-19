-- Kit_Servidor (Script, Workspace.Teste_LoboArtico) - KIT COMPLETO do Lobo Artico / "Lobo Glacial" (16/11/2026).
-- Usuario: "Prossiga com os poderes, seguindo o documento de poderes, ja faca todos os poderes de uma vez."
-- Fonte: REFERENCIAS_PODERES_E_EFEITOS.md v5.2 §1 (mira), §3 (kit), §0b (balanceamento), §5.4-5.7 (efeitos).
-- ENSAIO no place Teste-animacoes. AUTORIDADE DO SERVIDOR: o cliente so manda pedido + vetor de direcao + alvo
-- selecionado; o servidor valida dono, estado, recarga, energia, alcance, linha de visao, curva e aplica dano/estado.
--   Uivo Boreal  -> Uivo_Servidor (ja aprovado). Este script:
--   * Cometa Glacial (ativa): voa ate 35 studs, explode ao pousar: dano 0,8x mordida (8), raio 8, lentidao 30% 2 s;
--     energia 22, recarga 9 s; mira alvo -> mouse -> camera; curva max 120 graus/s; obstaculo explode no ponto.
--   * Avalanche (ativa): corrida teleguiada ate 30 studs, termina em onda conica: dano 1,2x mordida (12), lentidao 30%;
--     trilha de gelo 3 s que escorrega; energia 15, recarga 6 s; segue o alvo, sem alvo segue mouse/camera; curva 90/s.
--   * Instinto Boreal (passiva): raio 90, marca 8 s (dono ve contorno e seta), pegadas dos inimigos (no cliente do
--     dono), detecta inimigos sob neve/gelo (atributo SobNeve); em nevasca +12% vel. e +10% esquiva.
--   * Pelagem Polar (passiva): imune a frio ambiental e lentidao de neve profunda; -20% dano de gelo; parado >= 2 s
--     na neve: -40% do alcance em que inimigos o notam (some ao atacar).
--   * Esquiva = chance sorteada no servidor a cada golpe (SortearEsquiva), base 5%, teto 35%; bonus somados aqui.
-- Numeros [PROPOSTA][A TESTAR] do documento. PROVISORIOS deste ensaio (nao estao no documento) marcados [ENSAIO].
-- r4 (17/11): Cometa e Avalanche usam os clipes proprios v42 (anim_v42 -> json_v42). Texto antigo:
-- Animacoes: o documento marca as do Cometa e da Avalanche como [PENDENTE]; aqui usam os clipes aprovados como
-- substitutos (Arrancada = preparo, quadro da Corrida congelado = voo, Frenagem = pouso/fim) ate existirem clipes proprios.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local KSP = game:GetService("KeyframeSequenceProvider")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local lib = game:GetService("ReplicatedStorage"):WaitForChild("Animacoes_LoboArtico")

local CFG = {
	mordida = 10, vida = 400,                                   -- base dos lobos (§0b)
	-- r8 (pedido 17/11: atacar ANDANDO, PvP): ataque basico fora dos slots, sequencia variada de mordidas e garras;
	-- clipes PARCIAIS v43 (so pescoco/cabeca/boca/orelhas e, na garra, uma pata dianteira) por cima da locomocao.
	-- NAO marca PoderAtivo: o Controle_Servidor continua movendo o lobo. Valores [ENSAIO].
	basico = {seq = {"Mordida1", "GarraE", "Mordida2", "GarraD"}, danoMordida = 1.0, danoGarra = 0.8,   -- x mordida (10)
		-- r11 (decisao do usuario 17/11: "sem garras ... somente para animais pequenos de caca, como javali, coruja, etc...
		-- No combate nao"): combate = so mordidas; garras so contra presa pequena de caca.
		seqCombate = {"Mordida1", "Mordida2"},
		presaAtributo = "PresaPequena", presaNomes = {"Javali", "Coruja"},     -- [PROVISORIO] contrato com a fauna; outras especies = decisao do usuario
		intervalo = 0.5, reinicio = 1.2, alcance = 3.5, cone = 75, contato = {Mordida1 = 0.2, Mordida2 = 0.2, GarraE = 0.233, GarraD = 0.233}},   -- r11b: reinicio 1,0 -> 1,2 (segurar o botao repete a cada 0,5 s)
	esquivaBase = 0.05, tetoEsquiva = 0.35,
	mira = {cone = 60, dist = 65, perdaVisao = 0.5},      -- r7: trava/escolhe alvo ate 65 (Cometa de longo alcance) [ENSAIO]
	cometa = {custo = 22, recarga = 9, alcance = 60, mult = 0.8, raio = 8, lent = 0.30, lentDur = 2, giro = 240, prep = 0.25,
		vel = 40, altura = 10, alcanceMin = 8},                 -- r7 (pedido 17/11 "segue o alvo, longo alcance"): alcance 35->60, giro 120->240, vel 34->40 [ENSAIO]                 -- vel/altura/alcanceMin [ENSAIO]; r6: altura 5.5 -> 10 (pedido 17/11: pular mais alto)
	focinho = 6.2, folgaAlvo = 1.2,                            -- r5: pivo -> focinho (o pivo fica nas ancas; na r4 o peito entrava no alvo)
	avalanche = {custo = 15, recarga = 6, alcance = 30, mult = 1.2, lent = 0.30, lentDur = 2, trilhaDur = 3, giro = 90,
		vel = 24, coneDist = 10, coneAng = 35, trilhaRaio = 2.5},   -- vel, cone e lentDur [ENSAIO]
	instinto = {raio = 90, marca = 8, nevVel = 0.12, nevEsq = 0.10},
	pelagem = {resistGelo = 0.20, paradoSeg = 2, alcanceNotar = 0.6},
	pacotesPorSeg = 20,
}

local rede = pasta:FindFirstChild("Rede_Kit") or Instance.new("RemoteEvent"); rede.Name = "Rede_Kit"; rede.Parent = pasta
local fx = pasta:FindFirstChild("Kit_FX") or Instance.new("RemoteEvent"); fx.Name = "Kit_FX"; fx.Parent = pasta
local function agora() return workspace:GetServerTimeNow() end
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function angulo(a, b) return math.atan2(a.Z * b.X - a.X * b.Z, a.X * b.X + a.Z * b.Z) end   -- + = esquerda

-- estado base --------------------------------------------------------------------------------------------------------
if not lobo:GetAttribute("VidaMax") then lobo:SetAttribute("VidaMax", CFG.vida); lobo:SetAttribute("Vida", CFG.vida) end
lobo:SetAttribute("ImuneFrio", true); lobo:SetAttribute("ImuneNeveProfunda", true)
lobo:SetAttribute("ResistGelo", CFG.pelagem.resistGelo); lobo:SetAttribute("AlcanceNotarMult", 1); lobo:SetAttribute("Camuflado", false)
lobo:SetAttribute("PoderAtivo", nil); lobo:SetAttribute("VelPoder", 0)
lobo:SetAttribute("RecargaFim_Cometa", 0); lobo:SetAttribute("RecargaDur_Cometa", CFG.cometa.recarga)
lobo:SetAttribute("RecargaFim_Avalanche", 0); lobo:SetAttribute("RecargaDur_Avalanche", CFG.avalanche.recarga)

-- bonus somados (Uivo, nevasca, ...) -> MultVelocidade e ChanceEsquiva --------------------------------------------------
local function recomputar()
	local vel, esq = 1, CFG.esquivaBase
	for k, v in pairs(lobo:GetAttributes()) do
		if type(v) == "number" then
			if k:sub(1, 9) == "BonusVel_" then vel += v elseif k:sub(1, 13) == "BonusEsquiva_" then esq += v end
		end
	end
	lobo:SetAttribute("MultVelocidade", vel); lobo:SetAttribute("ChanceEsquiva", math.min(CFG.tetoEsquiva, esq))
end
lobo.AttributeChanged:Connect(function(k) if k:sub(1, 9) == "BonusVel_" or k:sub(1, 13) == "BonusEsquiva_" then recomputar() end end)
-- Instinto Boreal: nevasca (atributo Nevasca no Workspace no ensaio; no jogo vem do clima da Tundra)
local function nevasca()
	local on = workspace:GetAttribute("Nevasca") == true
	lobo:SetAttribute("BonusVel_Nevasca", on and CFG.instinto.nevVel or 0)
	lobo:SetAttribute("BonusEsquiva_Nevasca", on and CFG.instinto.nevEsq or 0)
end
workspace:GetAttributeChangedSignal("Nevasca"):Connect(nevasca); nevasca(); recomputar()

-- faixas substitutas -----------------------------------------------------------------------------------------------------
local animator = lobo.AnimationController:FindFirstChildOfClass("Animator") or Instance.new("Animator", lobo.AnimationController)
local faixas = {}
local function faixa(n)
	if not faixas[n] then
		local a = Instance.new("Animation"); a.AnimationId = KSP:RegisterKeyframeSequence(lib["LoboArtico_" .. n])
		faixas[n] = animator:LoadAnimation(a); faixas[n].Priority = Enum.AnimationPriority.Action
	end
	return faixas[n]
end
for _, n in ipairs({"CometaPreparar", "CometaVoo", "CometaPouso", "AvalancheCorrida", "AvalancheOnda", "Repouso"}) do faixa(n) end
-- r8: faixas do ataque basico (parciais) ficam FORA de `faixas` para o so()/pararTodas() dos poderes nao as tocarem
local golpes = {}
local function golpe(n)
	if not golpes[n] then
		local a = Instance.new("Animation"); a.AnimationId = KSP:RegisterKeyframeSequence(lib["LoboArtico_" .. n])
		golpes[n] = animator:LoadAnimation(a); golpes[n].Priority = Enum.AnimationPriority.Action2; golpes[n].Looped = false
	end
	return golpes[n]
end
for _, n in ipairs(CFG.basico.seq) do if lib:FindFirstChild("LoboArtico_" .. n) then golpe(n) end end
-- r10 (v43 r5, aprovado 17/11 "Aprovar e integrar"): garras SINCRONIZADAS por marcha (comecam no quadro em que aquela pata
-- DESCOLA na passada e devolvem a pata onde a passada a apoia) + mordidas com variante de Corrida (corpo baixo do galope).
for _, n in ipairs({"GarraE_Andar", "GarraD_Andar", "GarraE_Trote", "GarraD_Trote", "GarraE_Corrida", "GarraD_Corrida",
	"Mordida1_Corrida", "Mordida2_Corrida"}) do if lib:FindFirstChild("LoboArtico_" .. n) then golpe(n) end end
local LOCO_LEN = {Andar = 36 / 30, Trote = 18 / 30, Corrida = 14 / 30}             -- ciclo dos clipes de locomocao (s)
local DESCOLA = {Andar = {E = 32 / 30, D = 14 / 30}, Trote = {E = 8 / 30, D = 17 / 30}, Corrida = {E = 10 / 30, D = 9 / 30}}  -- gen_garra_v43r5
local golpeAte = 0                                                                  -- r10: sem Piscar durante golpe (+0,2 s)
local function faixaMarcha()
	if lobo:GetAttribute("CtrlModo") ~= "Laco" then return nil end
	local m = lobo:GetAttribute("CtrlMarcha"); local L = LOCO_LEN[m]; if not L then return nil end
	for _, tr in ipairs(animator:GetPlayingAnimationTracks()) do
		if tr.Looped and math.abs(tr.Length - L) < 0.02 and tr.WeightCurrent > 0.5 and tr.Priority ~= Enum.AnimationPriority.Action then return m, tr end
	end
	return nil
end
-- r9 (usuario 17/11 "quero animacao nos olhos"): os golpes ja animam as palpebras (estreitam mirando, fecham no contato);
-- alem disso o lobo PISCA de tempos em tempos (clipe parcial so das 4 palpebras, Action3) andando, correndo ou parado.
if lib:FindFirstChild("LoboArtico_Piscar") then
	task.spawn(function()
		local a = Instance.new("Animation"); a.AnimationId = KSP:RegisterKeyframeSequence(lib.LoboArtico_Piscar)
		local f = animator:LoadAnimation(a); f.Priority = Enum.AnimationPriority.Action3; f.Looped = false
		while lobo.Parent do
			task.wait(2.5 + math.random() * 4)
			if not f.IsPlaying and os.clock() > golpeAte then f:Play(0.03) end      -- r10: nao mascara a expressao do golpe
		end
	end)
end
local function so(n, t, ritmo, fade)
	for nome, f in pairs(faixas) do if nome ~= n and f.IsPlaying then f:Stop(fade or 0.12) end end
	local f = faixa(n)
	if not f.IsPlaying then f:Play(fade or 0.12) end
	if t then f.TimePosition = t end
	f:AdjustSpeed(ritmo or 1)
	return f
end
local function pararTodas(fade) for _, f in pairs(faixas) do if f.IsPlaying then f:Stop(fade or 0.2) end end end

-- consulta de chao / obstaculo -------------------------------------------------------------------------------------------
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.IgnoreWater = true
local function filtro(extra)
	local l = {lobo}
	for _, j in ipairs(Players:GetPlayers()) do if j.Character then table.insert(l, j.Character) end end
	if extra then for _, e in ipairs(extra) do table.insert(l, e) end end
	rp.FilterDescendantsInstances = l
end
local function chao(p)
	filtro()
	local r = workspace:Raycast(p + Vector3.new(0, 8, 0), Vector3.new(0, -20, 0), rp)
	return r and r.Position.Y or nil, r
end

-- inimigos ----------------------------------------------------------------------------------------------------------------
local function dono() return lobo:GetAttribute("Controlador") end
local function modeloAlvo(inst)
	local m = inst and (inst:IsA("Model") and inst or inst:FindFirstAncestorOfClass("Model"))
	while m do
		if m:FindFirstChildOfClass("Humanoid") or m:GetAttribute("Criatura") then return m end
		m = m:FindFirstAncestorOfClass("Model")
	end
end
local function ehInimigo(m)
	if not m or m == lobo or not m:IsDescendantOf(workspace) then return false end
	local j = Players:GetPlayerFromCharacter(m)
	if j and (j.UserId == dono() or j.UserId == lobo:GetAttribute("DonoUserId")) then return false end
	if j then return false end                                       -- PvP [A CONFIRMAR]: jogadores fora no ensaio
	local hum = m:FindFirstChildOfClass("Humanoid")
	return (hum and hum.Health > 0) or (m:GetAttribute("Criatura") == true and (m:GetAttribute("Vida") or 1) > 0)
end
local function posDe(m) local r = m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart; return r and r.Position or m:GetPivot().Position end
local function inimigosEm(centro, raio)
	local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Exclude; op.FilterDescendantsInstances = {lobo}
	local vistos, l = {}, {}
	for _, p in ipairs(workspace:GetPartBoundsInRadius(centro, raio, op)) do
		local m = modeloAlvo(p)
		if m and not vistos[m] then vistos[m] = true; if ehInimigo(m) then table.insert(l, m) end end
	end
	return l
end
local function cabeca() return lobo:GetPivot().Position + Vector3.new(0, 4.5, 0) end
local function visivel(m)
	filtro({m})
	local d = posDe(m) - cabeca()
	return workspace:Raycast(cabeca(), d, rp) == nil
end

-- Instinto Boreal: marca da presa ------------------------------------------------------------------------------------
local function marcar(m)
	if not ehInimigo(m) then return end
	m:SetAttribute("MarcaBoreal_Fim", agora() + CFG.instinto.marca); m:SetAttribute("MarcaBoreal_Dono", dono())
end

-- dano causado (aplicacao no servidor) e camuflagem ------------------------------------------------------------------
local function revelar() lobo:SetAttribute("Camuflado", false); lobo:SetAttribute("AlcanceNotarMult", 1); lobo:SetAttribute("CamufladoDesde", nil) end
local function causarDano(m, valor, elemento)
	local hum = m:FindFirstChildOfClass("Humanoid")
	if hum then hum:TakeDamage(valor) else m:SetAttribute("Vida", (m:GetAttribute("Vida") or 0) - valor) end
	marcar(m)
	fx:FireAllClients("dano", m, valor, elemento)
end
local evLent = pasta:WaitForChild("AplicarLentidao", 10)
local function lentidao(m, v, d) if evLent then evLent:Fire(m, v, d) end end

-- dano recebido pelo lobo: esquiva (chance) -> Pelagem Polar (-20% gelo) ---------------------------------------------
local fnDano = pasta:FindFirstChild("ReceberDano") or Instance.new("BindableFunction"); fnDano.Name = "ReceberDano"; fnDano.Parent = pasta
fnDano.OnInvoke = function(valor, elemento)
	if type(valor) ~= "number" or valor <= 0 then return 0, "invalido" end
	local sortear = pasta:FindFirstChild("SortearEsquiva")
	if sortear and sortear:Invoke() then fx:FireAllClients("esquiva", lobo); return 0, "esquivou" end
	local v = valor
	if elemento == "Gelo" then v *= (1 - CFG.pelagem.resistGelo); fx:FireAllClients("gelo_desviado", lobo) end
	lobo:SetAttribute("Vida", math.max(0, (lobo:GetAttribute("Vida") or CFG.vida) - v))
	return v, "acertou"
end

-- mira: alvo travado -> mais proximo no cone 60/40 -> direcao do cliente (mouse/camera) -----------------------------
local travado, travadoInvisivelDesde = nil, nil
local function alvoValido(m)
	return m and ehInimigo(m) and (plano(posDe(m) - lobo:GetPivot().Position)).Magnitude <= CFG.mira.dist
end
local function escolherAlvo()
	if alvoValido(travado) then
		if visivel(travado) then travadoInvisivelDesde = nil; return travado end
		travadoInvisivelDesde = travadoInvisivelDesde or os.clock()
		if os.clock() - travadoInvisivelDesde <= CFG.mira.perdaVisao then return travado end
	end
	local pv = lobo:GetPivot(); local fr = plano(pv.LookVector).Unit
	local melhor, dm = nil, math.huge
	for _, m in ipairs(inimigosEm(pv.Position, CFG.mira.dist)) do
		local d = plano(posDe(m) - pv.Position)
		if d.Magnitude > 0.1 and math.abs(math.deg(angulo(fr, d.Unit))) <= CFG.mira.cone / 2 and d.Magnitude < dm and visivel(m) then
			melhor, dm = m, d.Magnitude
		end
	end
	return melhor
end

-- pedido e validacao comuns -------------------------------------------------------------------------------------------
local dirCliente, dirT = nil, 0
local function recusar(poder, motivo) lobo:SetAttribute("KitUltimaRecusa", poder .. ": " .. motivo .. " @" .. string.format("%.2f", agora())); return false end
local function podeUsar(nome, cfg)
	local t = agora()
	if lobo:GetAttribute("PoderAtivo") then return recusar(nome, "outro poder ativo") end
	if (lobo:GetAttribute("UivoFase") or "") ~= "" or lobo:GetAttribute("Parado") then return recusar(nome, "uivando") end
	if lobo:GetAttribute("Incapacitado") then return recusar(nome, "incapacitado") end
	if t < (lobo:GetAttribute("RecargaFim_" .. nome) or 0) then return recusar(nome, string.format("recarga %.1f s", lobo:GetAttribute("RecargaFim_" .. nome) - t)) end
	local gastar = pasta:FindFirstChild("GastarEnergia")
	if not (gastar and gastar:Invoke(cfg.custo)) then return recusar(nome, "energia < " .. cfg.custo) end
	lobo:SetAttribute("RecargaFim_" .. nome, t + cfg.recarga)
	lobo:SetAttribute(nome .. "N", (lobo:GetAttribute(nome .. "N") or 0) + 1)
	revelar()                                             -- Pelagem Polar: some ao atacar
	return true
end
local function direcaoDesejada(alvo, padrao)
	if alvo and alvo.Parent then return plano(posDe(alvo) - lobo:GetPivot().Position) end
	if dirCliente and os.clock() - dirT < 0.6 then return dirCliente end
	return padrao
end
local function girar(atual, desejada, maxGraus, dt)
	if desejada.Magnitude < 1e-3 then return atual end
	local a = angulo(atual, desejada.Unit)
	local passo = math.clamp(a, -math.rad(maxGraus) * dt, math.rad(maxGraus) * dt)
	return (CFrame.Angles(0, passo, 0) * CFrame.lookAt(Vector3.zero, atual)).LookVector
end

-- COMETA GLACIAL --------------------------------------------------------------------------------------------------------
local function cometa()
	local C = CFG.cometa
	if not podeUsar("Cometa", C) then return end
	local alvo = escolherAlvo()
	local pv0 = lobo:GetPivot()
	local fr = plano(pv0.LookVector).Unit
	local d0 = direcaoDesejada(alvo, fr); if d0.Magnitude < 1e-3 then d0 = fr end
	-- r3: com alvo, pousa 2,5 studs antes (na r2 pousava em cima do inimigo)
	local dist = math.clamp(alvo and (d0.Magnitude - CFG.focinho - CFG.folgaAlvo) or C.alcance, C.alcanceMin, C.alcance)
	lobo:SetAttribute("PoderAtivo", "Cometa"); lobo:SetAttribute("CometaFase", "Preparo"); lobo:SetAttribute("CometaAlvo", alvo and alvo.Name or "")
	-- preparo 0,25 s: vira para a direcao e agacha (inicio do impulso da Arrancada)
	so("CometaPreparar", 0, (8 / 30) / C.prep)                 -- r4: clipe proprio v42 (8 q esticados para 0,25 s)
	local t0 = os.clock(); local frente = fr
	while os.clock() - t0 < C.prep do
		local dt = RunService.Heartbeat:Wait()
		frente = girar(frente, plano(direcaoDesejada(alvo, d0)), C.giro * 2, dt)
		local p = lobo:GetPivot().Position; lobo:PivotTo(CFrame.lookAt(p, p + frente))
	end
	-- voo: arco parabolico, curva limitada, obstaculo/inimigo no caminho explode no ponto
	lobo:SetAttribute("CometaFase", "Voo")
	local voo = so("CometaVoo", nil, 1)                    -- r4: clipe proprio v42 (laco, corpo esticado)
	local base = lobo:GetPivot().Position
	local yBase = base.Y
	local percorrido, ultimoChao, pos = 0, base, base
	local fim, motivo = nil, "pousou"
	local arco = math.min(C.altura, dist * 0.32)              -- r7: altura do arco fixada na partida
	while percorrido < dist do
		local dt = RunService.Heartbeat:Wait()
		frente = girar(frente, plano(direcaoDesejada(alvo, frente)), C.giro, dt)
		-- r7: SEGUE O ALVO - o ponto de pouso acompanha o alvo durante o voo (suavizado; teto = alcance)
		if alvo and alvo.Parent then
			local resta = (plano(posDe(alvo) - pos)).Magnitude - CFG.focinho - CFG.folgaAlvo
			local novo = math.clamp(percorrido + math.max(resta, 0), C.alcanceMin, C.alcance)
			dist += (novo - dist) * math.min(1, dt * 6)
			if percorrido >= dist then break end
		end
		local passo = math.min(C.vel * dt, dist - percorrido)
		local u = (percorrido + passo) / dist
		local horiz = Vector3.new(pos.X, 0, pos.Z) + frente * passo
		local yc = chao(Vector3.new(horiz.X, pos.Y, horiz.Z))     -- r2: o raio tem de partir da altura do lobo (Y=0 achava o mapa la embaixo)
		if yc then ultimoChao = Vector3.new(horiz.X, yc, horiz.Z) end
		local yRef = yc or yBase
		local alvoY = yRef + 4 * arco * u * (1 - u)                -- r6: arco proporcional a distancia (teto 10); r7: arco da partida
		local nova = Vector3.new(horiz.X, alvoY, horiz.Z)
		-- obstaculo: raio do peito do lobo na direcao do movimento
		filtro()
		local de = pos + Vector3.new(0, 3, 0)
		local hit = workspace:Raycast(de, (nova + Vector3.new(0, 3, 0)) - de + frente * (CFG.focinho + 0.5), rp)
		if hit and not (hit.Instance and hit.Normal.Y > 0.7 and u > 0.6) then
			fim = Vector3.new(pos.X, (chao(pos) or yRef), pos.Z); motivo = "obstaculo: " .. hit.Instance.Name; break
		end
		lobo:PivotTo(CFrame.lookAt(nova, nova + frente))
		lobo:SetAttribute("VelPoder", passo / math.max(dt, 1e-3))
		pos = nova; percorrido += passo
	end
	fim = fim or ultimoChao
	lobo:PivotTo(CFrame.lookAt(fim, fim + frente))
	-- explosao ao pousar
	lobo:SetAttribute("CometaFase", "Impacto"); lobo:SetAttribute("CometaMotivo", motivo)
	local atingidos = {}
	local centro = fim + frente * 3                            -- r5: explosao no peito, nao nas ancas
	for _, m in ipairs(inimigosEm(centro, C.raio)) do
		if (plano(posDe(m) - centro)).Magnitude <= C.raio then
			causarDano(m, CFG.mordida * C.mult, "Gelo"); lentidao(m, C.lent, C.lentDur); table.insert(atingidos, m.Name)
		end
	end
	lobo:SetAttribute("CometaAtingidos", table.concat(atingidos, ","))
	fx:FireAllClients("cometa_impacto", centro, C.raio)
	so("CometaPouso", 0, 1, 0.06)                          -- r4: toque -> amortece -> Repouso (0,8 s)
	task.wait(0.75)
	pararTodas(0.25); lobo:SetAttribute("VelPoder", 0)
	lobo:SetAttribute("CometaFase", ""); lobo:SetAttribute("PoderAtivo", nil)
end

-- AVALANCHE ------------------------------------------------------------------------------------------------------------
local trilha = {}                                          -- {pos, fim}
local function avalanche()
	local C = CFG.avalanche
	if not podeUsar("Avalanche", C) then return end
	local alvo = escolherAlvo()
	lobo:SetAttribute("PoderAtivo", "Avalanche"); lobo:SetAttribute("AvalancheAlvo", alvo and alvo.Name or "")
	local pv = lobo:GetPivot(); local frente = plano(pv.LookVector).Unit
	local corrida = so("AvalancheCorrida", nil, C.vel / 20.357)   -- r4: Corrida com cabeca de investida (v42)
	local percorrido, ultimo = 0, pv.Position
	local motivo = "alcance"
	local giroAnt = 0
	while percorrido < C.alcance do
		local dt = RunService.Heartbeat:Wait()
		local antes = frente
		frente = girar(frente, plano(direcaoDesejada(alvo, frente)), C.giro, dt)
		local w = angulo(antes, frente) / math.max(dt, 1e-3)               -- rad/s (inclina nas curvas)
		giroAnt = giroAnt + (w - giroAnt) * math.min(1, dt * 8)
		local p = lobo:GetPivot().Position + frente * C.vel * dt
		local y = chao(p)
		local yF = chao(p + frente * 4.5)
		if not y or not yF then motivo = "sem chao"; break end
		filtro()
		if workspace:Raycast(lobo:GetPivot().Position + Vector3.new(0, 3, 0), frente * (CFG.focinho + 0.5), rp) then motivo = "obstaculo"; break end
		local inclina = math.clamp(-giroAnt * 0.12, -0.18, 0.18)
		local np = Vector3.new(p.X, y, p.Z)
		lobo:PivotTo(CFrame.lookAt(np, np + frente) * CFrame.Angles(0, 0, inclina))
		lobo:SetAttribute("VelPoder", C.vel)
		percorrido += C.vel * dt
		if (np - ultimo).Magnitude >= 1 then table.insert(trilha, {np, agora() + C.trilhaDur}); ultimo = np end
		if alvo and alvo.Parent and (plano(posDe(alvo) - np)).Magnitude < CFG.focinho + CFG.folgaAlvo + 0.5 then motivo = "chegou no alvo"; break end
	end
	-- onda conica a frente
	local pvF = lobo:GetPivot(); local frF = plano(pvF.LookVector).Unit
	lobo:PivotTo(CFrame.lookAt(pvF.Position, pvF.Position + frF))
	local atingidos = {}
	for _, m in ipairs(inimigosEm(pvF.Position, C.coneDist + 2)) do
		local d = plano(posDe(m) - pvF.Position)
		if d.Magnitude <= C.coneDist and (d.Magnitude < 1 or math.abs(math.deg(angulo(frF, d.Unit))) <= C.coneAng) then
			causarDano(m, CFG.mordida * C.mult, "Gelo"); lentidao(m, C.lent, C.lentDur); table.insert(atingidos, m.Name)
		end
	end
	lobo:SetAttribute("AvalancheMotivo", motivo); lobo:SetAttribute("AvalancheAtingidos", table.concat(atingidos, ","))
	lobo:SetAttribute("AvalanchePercorrido", math.floor(percorrido * 10) / 10)
	fx:FireAllClients("avalanche_onda", pvF.Position, frF, C.coneDist, C.coneAng)
	so("AvalancheOnda", 0, 1, 0.08)                       -- r4: onda em 0,2 s, volta ao Repouso em 1 s
	task.wait(0.9)
	pararTodas(0.25); lobo:SetAttribute("VelPoder", 0); lobo:SetAttribute("PoderAtivo", nil)
end

-- trilha de gelo (3 s): inimigos que pisam ganham Escorregando (os controladores deles leem) -------------------------
task.spawn(function()
	while lobo.Parent do
		task.wait(0.2)
		local t = agora()
		for i = #trilha, 1, -1 do if trilha[i][2] <= t then table.remove(trilha, i) end end
		if #trilha > 0 then
			for _, m in ipairs(inimigosEm(trilha[#trilha][1], CFG.avalanche.alcance + 5)) do
				local p = posDe(m)
				for _, tp in ipairs(trilha) do
					if (plano(p - tp[1])).Magnitude <= CFG.avalanche.trilhaRaio then m:SetAttribute("Escorregando", t + 0.6); break end
				end
			end
		end
	end
end)

-- Pelagem Polar: camuflagem parado na neve ----------------------------------------------------------------------------
task.spawn(function()
	local paradoDesde = nil
	while lobo.Parent do
		task.wait(0.25)
		local parado = (lobo:GetAttribute("VelAtual") or 0) < 0.1 and not lobo:GetAttribute("PoderAtivo")
		local _, r = chao(lobo:GetPivot().Position)
		local naNeve = r and (r.Material == Enum.Material.Snow or r.Material == Enum.Material.Glacier or r.Material == Enum.Material.Ice
			or (r.Instance and r.Instance:GetAttribute("Neve") == true))
		if parado and naNeve then
			paradoDesde = paradoDesde or os.clock()
			if not lobo:GetAttribute("Camuflado") and os.clock() - paradoDesde >= CFG.pelagem.paradoSeg then
				lobo:SetAttribute("Camuflado", true); lobo:SetAttribute("AlcanceNotarMult", CFG.pelagem.alcanceNotar)
			end
		else
			paradoDesde = nil
			if lobo:GetAttribute("Camuflado") then revelar() end
		end
		lobo:SetAttribute("NaNeve", naNeve and true or false)
	end
end)

-- Instinto Boreal: deteccao sob neve/gelo (raio 90) ------------------------------------------------------------------
task.spawn(function()
	while lobo.Parent do
		task.wait(0.5)
		local t = agora()
		if dono() and dono() ~= 0 then
			for _, m in ipairs(inimigosEm(lobo:GetPivot().Position, CFG.instinto.raio)) do
				if m:GetAttribute("SobNeve") then m:SetAttribute("DetectadoBoreal_Fim", t + 1.0); m:SetAttribute("DetectadoBoreal_Dono", dono()) end
			end
		end
	end
end)

-- ATAQUE BASICO (r8) ---------------------------------------------------------------------------------------------------
-- O servidor decide: intervalo, sequencia, alvo no cone a frente do focinho NO INSTANTE DO CONTATO (o lobo e o alvo podem
-- estar se movendo), dano. Nada de PoderAtivo: andar/trotar/correr/virar continuam.
local basicoProx, basicoIdx, basicoUlt, basicoSeq = 0, 0, 0, nil
local function ehPresaPequena(m)
	if not m then return false end
	if m:GetAttribute(CFG.basico.presaAtributo) == true then return true end
	local esp = tostring(m:GetAttribute("Especie") or "") .. " " .. m.Name
	for _, n in ipairs(CFG.basico.presaNomes) do if esp:find(n, 1, true) then return true end end
	return false
end
local function basico()
	local B = CFG.basico; local t = os.clock()
	if lobo:GetAttribute("PoderAtivo") or lobo:GetAttribute("UivoFase") == "Uivar" then return recusar("Basico", "ocupado") end
	if t < basicoProx - 0.05 then return false end                          -- r11b: tolerancia de 0,05 s (pedido que chegava um pouco cedo era recusado e reiniciava a sequencia)
	local alvoAtk = escolherAlvo()
	-- r12 (usuario 17/11: "esqueca da garra, nao e necessario"): ataque basico = SO mordidas, em combate e na caca.
	-- Os clipes de garra ficam no place sem uso (B.seq e ehPresaPequena mantidos so como historico).
	local seq = B.seqCombate
	if t - basicoUlt > B.reinicio or seq ~= basicoSeq then basicoIdx = 0 end
	basicoSeq = seq
	basicoIdx = basicoIdx % #seq + 1; basicoUlt = t
	local nome = seq[basicoIdx]
	lobo:SetAttribute("BasicoModo", "mordidas")
	-- r10: escolhe a versao pela marcha; garra andando espera o descolamento da pata que descola primeiro
	local marcha, ft = faixaMarcha()
	local atraso, ritmo = 0, 1
	if nome:sub(1, 5) == "Garra" then
		if marcha then
			local tp, sp, L = ft.TimePosition, math.max(ft.Speed, 0.05), LOCO_LEN[marcha]
			local lado, w = nil, math.huge
			for l, t0 in pairs(DESCOLA[marcha]) do local esp = ((t0 - tp) % L) / sp; if esp < w then lado, w = l, esp end end
			nome = "Garra" .. lado .. "_" .. marcha; atraso = w; ritmo = sp
		end
	elseif marcha == "Corrida" and golpes[nome .. "_Corrida"] then nome = nome .. "_Corrida" end
	local contato = (nome:sub(1, 5) == "Garra" and 7 / 30 or 6 / 30) / ritmo
	basicoProx = t + atraso + B.intervalo
	basicoUlt = t + atraso                       -- r10b: o reinicio da sequencia conta do golpe tocado (a espera da garra o fazia voltar a Mordida1)
	golpeAte = t + atraso + 0.5 / ritmo + 0.2
	local function tocar()
		local f = golpes[nome] or golpe(nome)
		for _, g in pairs(golpes) do if g ~= f and g.IsPlaying then g:Stop(0.08) end end
		f:Play(0.06, 1, ritmo); f.TimePosition = 0
		lobo:SetAttribute("BasicoAtual", nome); lobo:SetAttribute("BasicoN", (lobo:GetAttribute("BasicoN") or 0) + 1)
		lobo:SetAttribute("BasicoEspera", math.floor(atraso * 1000 + 0.5) / 1000)
		fx:FireAllClients("basico", nome)
	end
	revelar()
	if atraso > 0.005 then task.delay(atraso, tocar) else tocar() end
	task.delay(atraso + contato, function()
		if lobo:GetAttribute("PoderAtivo") then return end
		local pv = lobo:GetPivot(); local fr = plano(pv.LookVector).Unit
		local focinho = pv.Position + fr * CFG.focinho
		local melhor, dm = nil, math.huge
		for _, m in ipairs(inimigosEm(focinho, B.alcance + 4)) do
			local d = plano(posDe(m) - focinho)
			local ang = math.abs(math.deg(angulo(fr, plano(posDe(m) - pv.Position).Unit)))
			if d.Magnitude <= B.alcance + 1.5 and ang <= B.cone / 2 and d.Magnitude < dm then melhor, dm = m, d.Magnitude end
		end
		if melhor then
			local mult = nome:sub(1, 5) == "Garra" and B.danoGarra or B.danoMordida
			causarDano(melhor, CFG.mordida * mult, "Fisico")
			lobo:SetAttribute("BasicoAcertou", melhor.Name .. string.format(" %.1f", dm))
		else lobo:SetAttribute("BasicoAcertou", "") end
	end)
	return true
end

-- rede -------------------------------------------------------------------------------------------------------------------
local janela, n = 0, 0
rede.OnServerEvent:Connect(function(j, acao, a1, a2)
	if j.UserId ~= dono() then return end                         -- so quem controla o lobo
	local c = os.clock(); if c - janela > 1 then janela = c; n = 0 end
	n += 1; if n > CFG.pacotesPorSeg then return end
	local function dirValida(v)
		if typeof(v) ~= "Vector3" or v ~= v then return nil end
		local d = plano(v); if d.X ~= d.X or d.Z ~= d.Z or d.Magnitude < 1e-3 or d.Magnitude > 1e4 then return nil end
		return d.Unit
	end
	if acao == "dir" then
		local d = dirValida(a1); if d then dirCliente, dirT = d, c end
	elseif acao == "travar" then
		local m = typeof(a1) == "Instance" and modeloAlvo(a1) or nil
		if m and alvoValido(m) and visivel(m) then travado = m; marcar(m); lobo:SetAttribute("AlvoTravado", m.Name)
		else travado = nil; lobo:SetAttribute("AlvoTravado", "") end
	elseif acao == "basico" then
		local d = dirValida(a1); if d then dirCliente, dirT = d, c end
		if typeof(a2) == "Instance" then local m = modeloAlvo(a2); if m and alvoValido(m) then travado = m; marcar(m) end end
		basico()
	elseif acao == "cometa" or acao == "avalanche" then
		local d = dirValida(a1); if d then dirCliente, dirT = d, c end
		if typeof(a2) == "Instance" then local m = modeloAlvo(a2); if m and alvoValido(m) then travado = m end end
		task.spawn(acao == "cometa" and cometa or avalanche)
	end
end)
Players.PlayerRemoving:Connect(function(j) if j.UserId == dono() then travado = nil end end)
pasta:SetAttribute("Kit_Versao", "r12 17/11 (ataque basico so mordidas, sem garras; garras sincronizadas por marcha v43r5, sem piscar no golpe; piscar + ataque basico andando + Cometa r7 segue o alvo, Avalanche, Instinto Boreal, Pelagem Polar)")
