-- IA_LoboArtico (Script dentro da pasta de UM lobo selvagem, criada pelo IA_LoboArtico_Servidor) - r3d 20/11/2026
-- (r3d, 3o Play: o relogio do aviso e a referencia da insistencia so comecam quando o intruso esta a <= avisoVisivel x Escala
-- do focinho de algum lobo -- o aviso precisa ser VISTO; no tunel o lobo escalava com o jogador a 160 studs. Copia: _r3c.)
-- (r3c, 2o Play: a zona critica, a insistencia e o recuo contam ate o NUCLEO da toca (descanso -> abrigo), nao ate o
-- tunel inteiro (o tunel da Floresta tem 180 studs: tudo nele virava "zona critica"); longe da toca o lobo firma posicao
-- onde esta em vez de ir ate a entrada. Copia da r3b: IA_LoboArtico_r3b.server.luau.)
-- (r3b, achado no 1o Play: membros da alcateia sao Folders, nao Models -> sem coordenador; e os raios do territorio passam
-- a ser medidos ate a TOCA inteira (entrada, tunel e abrigo; a toca da Floresta tem 272 studs da entrada ao ovo), nao so
-- ate o abrigo. Copia da r3: IA_LoboArtico_r3.server.luau.) Copia da r2j: IA_LoboArtico_r2j.server.luau (r2j = contato/caminho/toca, testada
-- em Play 20/11 salvo o rotulo IA_Contato).
-- Pedido 20/11 ("ameaca antes do ataque e distancia de confronto"): o lobo chegava perto demais e passava direto ao ataque.
--   1. Estados EXPLICITOS da alcateia (atributo Tensao na pasta da alcateia): Calmo -> Atencao -> Ameaca -> Defesa, com
--      histerese nos raios e prazos minimos; descer de nivel so depois de CFG.ameaca.calma s sem gatilho (Desengajar).
--      Um COORDENADOR por alcateia (Lider; se incapacitado, Membro; depois Guardiao) decide o nivel e e o UNICO que limpa o
--      alvo compartilhado (achado 4: na r2j qualquer lobo limpava AlvoJogador e a defesa alternava com a rotina).
--   2. Aproximacao da toca: primeiro Atencao (para, encara, a distancia visivel); depois Ameaca: cada papel vai a um posto
--      ENTRE o intruso e a toca (Lider na frente, Membro no flanco, Guardiao junto ao ovo), para, encara e mantem
--      distancia de confronto (focinho a >= distConfronto x Escala da superficie do intruso). Escala para Defesa se, depois
--      de avisoMin s de aviso, o intruso AVANCA (insistencia), FICA na zona critica avisoCritico s ou encosta num lobo.
--      Recuar baixa a tensao. Coleta do ovo e dano com autoria validada = Defesa imediata (regras ja existentes).
--   3. O aviso NAO e o Uivo Boreal (poder com bonus). Sinal corporal usa os clipes "Alerta"/"Ameaca" SE existirem em
--      Animacoes_LoboArtico (hoje NAO existem: ver contrato em lobo-artico-ia-plano.md §9); vocal = atributo IA_Vocal para o
--      som futuro (nao ha som de rosnado/latido aprovado). O Uivo Boreal so pode sair ja em Defesa e de longe (r2h).
--   4. Contato: alcance e cone do Kit inalterados; a parada considera o VOLUME do alvo e a FRENAGEM (velocidade medida do
--      pivo), nunca mais perto que o alcance do Kit permite morder.
--   5. Percepcao: linha de visao (raycast olhos -> cabeca) e memoria da ultima posicao (CFG.ameaca.memoria). Alvo morto,
--      desconectado ou fora de vista alem da memoria e reavaliado; o alvo expira sem limpeza manual.
--   6. Dano: autoria SO pelo evento IA_DanoRecebido do Kit r15 (ReceberDano com origem validada). Dano sem autoria = Atencao
--      na direcao de onde veio (investigar), nunca o jogador mais proximo (achado 2).
-- Raios, prazos e distancias = [PROPOSTA][A TESTAR]. Dano, alcance, cone e recarga continuam os do Kit (nao mudam aqui).
local Players = game:GetService("Players")
local PFS = game:GetService("PathfindingService")
local KSP = game:GetService("KeyframeSequenceProvider")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local lib = game:GetService("ReplicatedStorage"):WaitForChild("Animacoes_LoboArtico")
local habitat = workspace.Tundra_Congelada.Habitats.Ecologia_Fauna.Lobo_Artico:FindFirstChild(pasta:GetAttribute("AlcateiaPasta") or "")
assert(habitat, "habitat da alcateia nao achado")

local CFG = {
	raioColeira = 75,                                         -- do abrigo: alem disso a defesa termina (+ ameaca.defesaSai)
	raioDormente = 600,
	tick = 0.3, tickDormente = 2,
	pesos = {Dormir = 2, Patrulhar = 3, Cacar = 2, Guardar = 2},
	patrulhaPasso = 4,
	chegada = 5, repath = 2.5,
	durDormir = {60, 140}, durGuardar = {30, 70}, durCacar = {25, 50},
	nocauteSeg = 60,
	-- r2: geometria do contato (x Escala da idade). Focinho/alcance/cone = valores do Kit_Servidor (CFG.focinho, basico).
	focinho = 6.2, alcanceKit = 3.5, folgaKit = 1.5, coneMordida = 30,
	contatoEntra = 3.2, contatoSai = 4.6, aproxima = 8, perseguirCorrendo = 25,
	raioAlvo = 1.0, estacaoFolga = 0.8, separacao = 3.5,
	troncoLado = 1.8, troncoAtras = 1.0,
	intervaloMordida = 0.5,                                   -- = Kit basico.intervalo (o Kit recusa antes disso)
	corpoLargura = 2.0, alturaCabeca = 6.0,                   -- caixa do Blockcast da toca (x Escala); cabeca do Adulto ~6,05 acima do chao
	desacel = 12,                                             -- r3: studs/s2 da frenagem (transicoes reais sao clipes; mesmo valor da simulacao)
	-- r3: ameaca antes do ataque. Raios em studs a partir do ABRIGO do ovo (territorio, nao escalam com o lobo); distancias
	-- ate o lobo x Escala da idade. Tudo [PROPOSTA][A TESTAR].
	ameaca = {
		raioAtencao = 48, raioAviso = 34, raioCritico = 20, histerese = 6,
		atencaoLobo = 30, avisoLobo = 16, encostar = 2.5,     -- longe da toca: distancia focinho -> superficie do intruso (x Escala)
		atencaoMin = 1.0,                                     -- s de Atencao antes de Ameaca (salvo se ja entrou na zona critica)
		avisoMin = 2.0,                                       -- s de aviso garantidos antes de escalar por aproximacao
		avisoCritico = 3.0,                                   -- s parado na zona critica (depois do aviso) -> Defesa
		insistencia = 5,                                      -- studs de avanco para a toca desde o ponto mais distante do aviso
		recuo = 3,                                            -- studs de recuo que zeram o tempo na zona critica
		calma = 4,                                            -- s sem gatilho para descer um nivel
		memoria = 8,                                          -- s lembrando a ultima posicao vista
		memoriaDefesa = 20,                                   -- s de validade do alvo da alcateia (renovado enquanto visto no territorio)
		defesaSai = 8,                                        -- studs alem da coleira para encerrar a defesa (histerese)
		foraSeg = 3,                                          -- s fora da coleira para o coordenador encerrar a defesa
		distConfronto = 11,                                   -- x Escala: focinho -> superficie do intruso durante a ameaca
		postoFracao = 0.45, postoMax = 16,                    -- posto na linha ancora -> intruso
		flanco = 7, flancoAtras = 2,                          -- x Escala: Membro ao lado do Lider
		guardiaoPosto = 4,                                    -- studs do abrigo para o Guardiao (responsavel pelo ovo)
		guardiaoDefende = 26,                                 -- o Guardiao so sai do ovo para alvo a menos disso do abrigo
		cone = 125,                                           -- meia abertura da visao (graus); atras dela nao ve
		avisoVisivel = 35,                                    -- r3d: x Escala; o aviso so "conta" com o intruso a essa distancia de um focinho
	},
}
local evMover = pasta:WaitForChild("IA_Mover")
local evAcao = pasta:WaitForChild("IA_Acao")
local evUivo = pasta:WaitForChild("IA_PedirUivo")
local evOlhar = pasta:WaitForChild("IA_Olhar", 10)               -- Controle r7; sem ele cai no comportamento antigo (parar)
local function P(nome) local p = habitat:FindFirstChild(nome, true); return p and p.Position end
local pontoDescanso, pontoAbrigo, pontoEntrada = P("Descanso_Toca"), P("Abrigo_Filhotes"), P("Entrada_Toca")
local zonas = {}; for _, z in ipairs(habitat.Zonas_Caca:GetChildren()) do table.insert(zonas, z.Position) end
local rota = {}
do
	local ok, pts = pcall(function() return game:GetService("HttpService"):JSONDecode(habitat.Rotas_Patrulha.Rota_Patrulha:GetAttribute("Pontos")) end)
	if ok and pts then for i = 1, #pts, CFG.patrulhaPasso do table.insert(rota, Vector3.new(pts[i][1], pts[i][2], pts[i][3])) end end
end
local papel = pasta:GetAttribute("Papel") or "Membro"           -- Lider / Guardiao / Membro
local pastaAlcateia = pasta.Parent
local function esc() return lobo:GetAttribute("Escala") or 1 end

-- animacoes de vida -------------------------------------------------------------------------------------------------------
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
local poseAtual, poseGen = nil, 0                               -- r2 E: geracao invalida callbacks atrasados
local function pose(n, fade)
	if poseAtual == n then return end
	poseGen += 1
	for nome, f in pairs(faixas) do if f and nome ~= n and f.IsPlaying then f:Stop(fade or 0.4) end end
	poseAtual = n
	if n then local f = faixa(n); if f then f:Play(fade or 0.4) end end
end
local function tocarUmaVez(n, depois)
	local f = faixa(n); if not f then return 0 end
	poseGen += 1; local g = poseGen
	for nome, h in pairs(faixas) do if h and h ~= f and h.IsPlaying then h:Stop(0.3) end end
	f.Looped = false; f:Play(0.3); poseAtual = depois
	if depois then
		task.delay(f.Length - 0.1, function()
			if g ~= poseGen or not lobo.Parent or poseAtual ~= depois then return end
			local h = faixa(depois); if h then h:Play(0.3) end
		end)
	end
	return f.Length
end

-- movimento -----------------------------------------------------------------------------------------------------------------
local function pos() return lobo:GetPivot().Position end
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function parar() evMover:Fire(Vector3.zero, "andar") end
local function olhar(d) if evOlhar then evOlhar:Fire(d) else parar() end end
local rpLivre = RaycastParams.new(); rpLivre.FilterType = Enum.RaycastFilterType.Exclude
local function filtrosLivres()
	local lista = {habitat}
	local ia = workspace:FindFirstChild("Criaturas_IA"); if ia then table.insert(lista, ia) end
	for _, j in ipairs(Players:GetPlayers()) do if j.Character then table.insert(lista, j.Character) end end
	rpLivre.FilterDescendantsInstances = lista
end
local function linhaLivre(a, b)                                  -- r2 C: o corpo do lobo passa de a ate b?
	filtrosLivres()
	local e = esc(); local h = Vector3.new(0, 2.2 * e, 0); local d = (b + h) - (a + h)
	if d.Magnitude < 0.5 then return true end
	return workspace:Spherecast(a + h, 0.9 * e, d, rpLivre) == nil
end
local caminho, idx, alvoCaminho, ultimoPath = nil, 1, nil, 0
local travaRef, travaT, falhas, travaLook = nil, 0, 0, nil
local ultimaFalha = ""
local function falhar(motivo) ultimaFalha = motivo; pasta:SetAttribute("IA_Falha", motivo .. string.format(" @(%d,%d,%d)", pos().X, pos().Y, pos().Z)); return "falhou" end
local function irParaFora(destino, marcha)
	local agora = os.clock()
	if not alvoCaminho or (alvoCaminho - destino).Magnitude > 4 or agora - ultimoPath > CFG.repath then
		alvoCaminho, ultimoPath = destino, agora
		local path = PFS:CreatePath({AgentRadius = 3, AgentHeight = 7, AgentCanJump = false, WaypointSpacing = 8})
		local ok = pcall(function() path:ComputeAsync(pos(), destino) end)
		if ok and path.Status == Enum.PathStatus.Success then caminho = path:GetWaypoints(); idx = math.min(2, #caminho)
		elseif linhaLivre(pos(), destino) then caminho = {{Position = destino}}; idx = 1        -- NoPath, mas a linha esta livre
		else caminho = nil; return falhar("NoPath e linha bloqueada") end
	end
	if not caminho then return falhar("sem caminho") end
	local p = pos()
	if plano(destino - p).Magnitude < CFG.chegada then travaRef = nil; falhas = 0; parar(); return "chegou" end
	-- r2e: girar no lugar (clipe Virar ~3,1 s por 90 graus, ou giro do IA_Olhar) NAO e travamento
	local look = lobo:GetPivot().LookVector
	local virando = (lobo:GetAttribute("CtrlClipe") or ""):find("Virar") ~= nil
	if not travaRef or (p - travaRef).Magnitude > 1 or virando or (travaLook and look:Dot(travaLook) < 0.985) then
		travaRef, travaT, travaLook = p, os.clock(), look
	elseif os.clock() - travaT > 4 then
		travaRef, travaT = p, os.clock(); falhas += 1; ultimoPath = 0
		if caminho and idx < #caminho then idx += 1 end
		if falhas >= 3 then falhas = 0; parar(); return falhar("travado 3x") end   -- r2 C: falha explicita, nao chegada
	end
	while caminho[idx] and plano(caminho[idx].Position - p).Magnitude < CFG.chegada and idx < #caminho do idx += 1 end
	local wp = caminho[idx] and caminho[idx].Position or destino
	pose(nil); evMover:Fire(plano(wp - p), marcha)
	return "andando"
end

-- toca: cadeia (agente pequeno) + conferencia do volume do lobo da idade -----------------------------------------------------
local cadeia, limiteCadeia
local iNucleo = 1                                                -- r3c: indice do Descanso_Toca na cadeia (nucleo = descanso -> abrigo)
local function construirCadeia()
	local c = {pontoEntrada}
	local path = PFS:CreatePath({AgentRadius = 1, AgentHeight = 3, AgentCanJump = true, WaypointSpacing = 6})
	pcall(function() path:ComputeAsync(pontoEntrada, pontoDescanso) end)
	if path.Status == Enum.PathStatus.Success then for _, w in ipairs(path:GetWaypoints()) do table.insert(c, w.Position) end end
	table.insert(c, pontoDescanso); iNucleo = #c
	local n = math.max(1, math.floor((pontoAbrigo - pontoDescanso).Magnitude / 6))
	for k = 1, n do table.insert(c, pontoDescanso:Lerp(pontoAbrigo, k / n)) end
	-- r2 D/r2d: o lobo desta idade cabe? Cada ponto vai para o CHAO real (r2c usava a altura dos marcadores e batia em
	-- degrau); a caixa vai de chao+1,0 (degrau tolerado) ate a altura da cabeca (6,0 x Escala), largura 2,0 x Escala.
	filtrosLivres()
	local e = esc()
	local function chaoDe(q)
		local r = workspace:Raycast(q + Vector3.new(0, 6, 0), Vector3.new(0, -20, 0), rpLivre)
		return r and r.Position or q
	end
	for i = 1, #c do c[i] = chaoDe(c[i]) end
	local alt = CFG.alturaCabeca * e - 1.0
	local caixa = Vector3.new(CFG.corpoLargura * e, alt, 0.5)
	limiteCadeia = #c
	for i = 1, #c - 1 do
		local a = c[i] + Vector3.new(0, 1.0 + alt / 2, 0); local b = c[i + 1] + Vector3.new(0, 1.0 + alt / 2, 0)
		local d = b - a
		if d.Magnitude > 0.2 then
			local r = workspace:Blockcast(CFrame.lookAt(a, b), caixa, d, rpLivre)
			if r then
				limiteCadeia = i
				pasta:SetAttribute("IA_CadeiaBloqueio", string.format("trecho %d->%d: nao cabe em (%d,%d,%d), %s (escala %.2f, cabeca %.1f)", i, i + 1, r.Position.X, r.Position.Y, r.Position.Z, r.Instance.Name, e, CFG.alturaCabeca * e))
				break
			end
		end
	end
	pasta:SetAttribute("IA_CadeiaToca", #c); pasta:SetAttribute("IA_CadeiaLimite", limiteCadeia)
	return c
end
local function prox(p)
	local bi, bd = 1, math.huge
	for i, q in ipairs(cadeia) do local d = (q - p).Magnitude; if d < bd then bi, bd = i, d end end
	return bi, bd
end
-- r2f: "dentro da toca" exige TETO de rocha acima (perto da boca da toca os pontos da cadeia estao a ceu aberto e o
-- lobo seguia a cadeia para longe do alvo)
local function coberto(p)
	filtrosLivres()
	return workspace:Raycast(p + Vector3.new(0, 1, 0), Vector3.new(0, 25, 0), rpLivre) ~= nil
end
local function andarReto(ponto, marcha)
	local d = plano(ponto - pos())
	if d.Magnitude < CFG.chegada then return "chegou" end
	pose(nil); evMover:Fire(d, marcha); return "andando"
end
local function irPara(destino, marcha)
	cadeia = cadeia or construirCadeia()
	local ip, dp = prox(pos()); local it, dt = prox(destino)
	-- r2i: alem do teto, precisa estar alem do 1o trecho do tunel (indice > 3); na boca da toca ha beiral de rocha
	local loboDentro = ip > 3 and dp < 15 and coberto(pos())
	local destDentro = it > 3 and dt < 15 and coberto(destino)
	if destDentro and it > limiteCadeia then destino = cadeia[limiteCadeia]; it = limiteCadeia end   -- r2 D: nao passa do limite
	if not loboDentro and not destDentro then return irParaFora(destino, marcha) end
	if not loboDentro then
		local s = irParaFora(pontoEntrada, marcha)
		if s == "falhou" then return s end
		if (pontoEntrada - pos()).Magnitude > CFG.chegada + 2 then return "andando" end
		ip = 1
	end
	local alvoI = destDentro and it or 1
	if ip == alvoI then
		if destDentro then return andarReto(destino, "andar") end
		return irParaFora(destino, marcha)
	end
	local passo = alvoI > ip and 1 or -1
	local proxI = ip
	if (cadeia[ip] - pos()).Magnitude <= 6 then
		proxI = ip + passo
		while proxI ~= alvoI and plano(cadeia[proxI] - pos()).Magnitude < CFG.chegada do proxI += passo end
	end
	if proxI == alvoI and plano(cadeia[alvoI] - pos()).Magnitude < CFG.chegada then
		if destDentro then return andarReto(destino, "andar") end
		return irParaFora(destino, marcha)
	end
	andarReto(cadeia[proxI], "andar")
	return "andando"
end

-- percepcao (r3: linha de visao + memoria) -----------------------------------------------------------------------------------
local A = CFG.ameaca
local function dToca(p)                                           -- r3b: distancia ate a toca inteira (cadeia: entrada -> tunel -> abrigo)
	cadeia = cadeia or construirCadeia()
	local _, d = prox(p); return d
end
local function dNucleo(p)                                         -- r3c: distancia ate o nucleo da toca (descanso -> abrigo)
	cadeia = cadeia or construirCadeia()
	local d = math.huge
	for i = iNucleo, #cadeia do d = math.min(d, (cadeia[i] - p).Magnitude) end
	return d
end
local function personagemValido(c)                               -- vivo e conectado
	if not c or not c.Parent then return nil end
	local j = Players:GetPlayerFromCharacter(c); if not j or j.Parent ~= Players then return nil end
	local h = c:FindFirstChildOfClass("Humanoid"); local r = c:FindFirstChild("HumanoidRootPart")
	if not (h and r and h.Health > 0) then return nil end
	return j, r
end
local function personagemDe(uid)
	local j = uid and Players:GetPlayerByUserId(uid)
	local c = j and j.Character
	if personagemValido(c) then return c end
	return nil
end
local function jogadorMaisPerto()
	local dm = math.huge
	for _, j in ipairs(Players:GetPlayers()) do
		local r = j.Character and j.Character:FindFirstChild("HumanoidRootPart")
		if r then dm = math.min(dm, (r.Position - pos()).Magnitude) end
	end
	return dm
end
local rpVisao = RaycastParams.new(); rpVisao.FilterType = Enum.RaycastFilterType.Exclude
local function olhos()
	local e = esc(); local pv = lobo:GetPivot()
	local fr = plano(pv.LookVector); fr = fr.Magnitude > 0 and fr.Unit or Vector3.new(0, 0, -1)
	return pv.Position + fr * (CFG.focinho - 1.2) * e + Vector3.new(0, 4.6 * e, 0), fr
end
local function visivel(c)                                         -- cone largo a frente + nada entre os olhos e a cabeca
	local cab = c:FindFirstChild("Head") or c:FindFirstChild("HumanoidRootPart"); if not cab then return false end
	local o, fr = olhos()
	local d = cab.Position - o
	local dp = plano(d)
	if dp.Magnitude > 1 and math.deg(math.acos(math.clamp(dp.Unit:Dot(fr), -1, 1))) > A.cone then return false end
	local ia = workspace:FindFirstChild("Criaturas_IA")
	rpVisao.FilterDescendantsInstances = {c, ia or lobo, habitat}
	return workspace:Raycast(o, d, rpVisao) == nil
end
local function raioDoAlvo(c)                                       -- r3: volume do alvo no plano (jogador ~1)
	local ok, s = pcall(function() return c:GetExtentsSize() end)
	if not ok or not s then return CFG.raioAlvo end
	return math.clamp(math.min(s.X, s.Z) * 0.5, 0.8, 6)
end
-- memoria propria (por UserId) e avistamento publicado para o coordenador (atributos da pasta deste lobo)
local memoria = {}
local function perceber()
	local agora = os.clock(); local melhorUid, melhorD, melhorPos
	for _, j in ipairs(Players:GetPlayers()) do
		local c = j.Character; local _, r = personagemValido(c)
		if r then
			local dA = dToca(r.Position); local dL = (r.Position - pos()).Magnitude
			if (dA <= A.raioAtencao + A.histerese + 20 or dL <= A.atencaoLobo * esc() + 20) and visivel(c) then
				memoria[j.UserId] = {pos = r.Position, t = agora}
			end
		end
	end
	for uid, m in pairs(memoria) do
		if agora - m.t > A.memoria or not personagemDe(uid) then memoria[uid] = nil      -- morto/desconectado sai da memoria
		else
			local d = dToca(m.pos)
			if not melhorD or d < melhorD then melhorUid, melhorD, melhorPos = uid, d, m.pos end
		end
	end
	pasta:SetAttribute("Visao_Id", melhorUid); pasta:SetAttribute("Visao_Pos", melhorPos)
	pasta:SetAttribute("Visao_T", melhorUid and memoria[melhorUid].t or nil)
end
local function viuRecente(uid)                                     -- este lobo viu o jogador ha pouco?
	local m = memoria[uid]; return m and os.clock() - m.t <= A.memoria, m
end

-- alcateia: estado compartilhado ---------------------------------------------------------------------------------------------
-- Atributos na pasta da alcateia: Tensao (Calmo/Atencao/Ameaca/Defesa), TensaoId, TensaoPos, AvisoDesde, Motivo;
-- AlvoId/AlvoMotivo/AlvoAte (Defesa); InvestigarPos/InvestigarAte (dano sem autoria). AlvoJogador (nome) = r2, ainda lido.
local function membros()
	local l = {}
	for _, f in ipairs(pastaAlcateia:GetChildren()) do
		local o = (f:IsA("Folder") or f:IsA("Model")) and f:FindFirstChild("LoboArtico_LOW")   -- r3b: as pastas dos lobos sao Folders
		if o then table.insert(l, {pasta = f, lobo = o}) end
	end
	return l
end
local ORDEM_COORD = {Lider = 1, Membro = 2, Guardiao = 3}
local function souCoordenador()
	local melhor, pm
	for _, m in ipairs(membros()) do
		local ok = (m.lobo:GetAttribute("Vida") or 1) > 0 and not m.lobo:GetAttribute("Incapacitado")
		local p = ORDEM_COORD[m.pasta:GetAttribute("Papel") or "Membro"] or 9
		if ok and (not pm or p < pm or (p == pm and m.pasta.Name < melhor.Name)) then melhor, pm = m.pasta, p end
	end
	return melhor == pasta
end
local function definirAlvo(uid, motivo, seg)                       -- qualquer lobo/sistema pode DEFINIR; so o coordenador limpa
	pastaAlcateia:SetAttribute("AlvoId", uid); pastaAlcateia:SetAttribute("AlvoMotivo", motivo)
	pastaAlcateia:SetAttribute("AlvoAte", os.clock() + (seg or A.memoriaDefesa))
	pastaAlcateia:SetAttribute("Tensao", "Defesa"); pastaAlcateia:SetAttribute("Motivo", motivo)
	pastaAlcateia:SetAttribute("TensaoId", uid)
end
local function alvoAlcateia()                                      -- personagem do alvo valido ou nil
	local uid = pastaAlcateia:GetAttribute("AlvoId")
	if not uid then                                                -- compatibilidade: spawner r2 grava o NOME
		local nome = pastaAlcateia:GetAttribute("AlvoJogador")
		local j = nome and Players:FindFirstChild(nome)
		if j and os.clock() <= (pastaAlcateia:GetAttribute("AlvoAte") or 0) then definirAlvo(j.UserId, "coleta", A.memoriaDefesa) end
		pastaAlcateia:SetAttribute("AlvoJogador", nil)
		uid = pastaAlcateia:GetAttribute("AlvoId")
	end
	if not uid or os.clock() > (pastaAlcateia:GetAttribute("AlvoAte") or 0) then return nil, uid end
	return personagemDe(uid), uid
end
-- dano: autoria so pelo evento do Kit r15 (origem validada no servidor do Kit) ------------------------------------------------
local ultimoDanoEvento = 0
local evDano = pasta:FindFirstChild("IA_DanoRecebido")
local function investigar(p)
	if not p then local pv = lobo:GetPivot(); p = pv.Position + pv.LookVector * 15 end
	pastaAlcateia:SetAttribute("InvestigarPos", p); pastaAlcateia:SetAttribute("InvestigarAte", os.clock() + A.memoria)
end
if evDano then
	evDano.Event:Connect(function(valor, uid, origemPos)
		ultimoDanoEvento = os.clock()
		if type(valor) ~= "number" or valor <= 0 then return end
		if uid and personagemDe(uid) then definirAlvo(uid, "dano", A.memoriaDefesa); pasta:SetAttribute("IA_Motivo", "dano validado")
		else investigar(typeof(origemPos) == "Vector3" and origemPos or nil); pasta:SetAttribute("IA_Motivo", "dano sem autoria: investigar") end
	end)
end
local vidaAnt = lobo:GetAttribute("Vida") or 400
lobo:GetAttributeChangedSignal("Vida"):Connect(function()
	local v = lobo:GetAttribute("Vida") or 0
	if v < vidaAnt then
		task.delay(0.15, function()                                -- o evento do Kit chega no mesmo quadro; sem ele = sem autoria
			if os.clock() - ultimoDanoEvento > 0.3 then investigar(nil); pasta:SetAttribute("IA_Motivo", "dano sem autoria: investigar") end
		end)
	end
	vidaAnt = v
end)

-- coordenador: nivel da alcateia com histerese e prazos ------------------------------------------------------------------------
local C = {dRef = nil, criticoDesde = nil, foraDesde = nil, gatilhoT = 0, nivelDesde = os.clock()}
local NIVEL = {Calmo = 0, Atencao = 1, Ameaca = 2, Defesa = 3}
local function tensao() return pastaAlcateia:GetAttribute("Tensao") or "Calmo" end
local function mudarNivel(n, motivo)
	if tensao() == n then return end
	pastaAlcateia:SetAttribute("Tensao", n); pastaAlcateia:SetAttribute("Motivo", motivo)
	C.nivelDesde = os.clock()
	if n == "Ameaca" then pastaAlcateia:SetAttribute("AvisoDesde", os.clock()); C.dRef = nil; C.criticoDesde = nil; C.visivelDesde = nil end
	if NIVEL[n] < 2 then pastaAlcateia:SetAttribute("AvisoDesde", nil) end
	if n == "Calmo" then pastaAlcateia:SetAttribute("TensaoId", nil); pastaAlcateia:SetAttribute("TensaoPos", nil) end
end
local function limparAlvo(motivo)                                   -- SO o coordenador chama
	pastaAlcateia:SetAttribute("AlvoId", nil); pastaAlcateia:SetAttribute("AlvoMotivo", nil); pastaAlcateia:SetAttribute("AlvoAte", nil)
	pastaAlcateia:SetAttribute("AlvoJogador", nil)
	C.foraDesde = nil; C.gatilhoT = os.clock()
	mudarNivel("Atencao", motivo)                                   -- desengaja passando por Atencao (encara, depois acalma)
end
local function avistamentos()                                       -- o mais perto do abrigo visto por qualquer membro
	local agora = os.clock(); local uid, p, dm
	for _, m in ipairs(membros()) do
		local id, vp, vt = m.pasta:GetAttribute("Visao_Id"), m.pasta:GetAttribute("Visao_Pos"), m.pasta:GetAttribute("Visao_T")
		if id and vp and vt and agora - vt <= A.memoria and personagemDe(id) then
			local d = dToca(vp)
			if not dm or d < dm then uid, p, dm = id, vp, d end
		end
	end
	return uid, p, dm
end
local function distAoBando(p, raio)                                 -- menor distancia focinho -> superficie, em unidades de Escala
	local melhor = math.huge
	for _, m in ipairs(membros()) do
		local e = m.lobo:GetAttribute("Escala") or 1; local pv = m.lobo:GetPivot()
		local fr = plano(pv.LookVector); fr = fr.Magnitude > 0 and fr.Unit or Vector3.new(0, 0, -1)
		local f = pv.Position + fr * CFG.focinho * e
		local d = math.min(plano(p - f).Magnitude, plano(p - pv.Position).Magnitude) - raio
		melhor = math.min(melhor, d / e)
	end
	return melhor
end
local function vistoPorAlguem(uid)
	for _, m in ipairs(membros()) do
		if m.pasta:GetAttribute("Visao_Id") == uid and os.clock() - (m.pasta:GetAttribute("Visao_T") or -99) <= 2 then return true end
	end
	return false
end
local function coordenar()
	local agora = os.clock()
	-- 1. defesa em curso: valida o alvo; renova enquanto visto no territorio; encerra com histerese
	local c, uidAlvo = alvoAlcateia()
	if uidAlvo then
		if not c then
			local motivo = Players:GetPlayerByUserId(uidAlvo) and "alvo morto ou fora do tempo" or "alvo desconectado"
			if agora > (pastaAlcateia:GetAttribute("AlvoAte") or 0) then motivo = "memoria do alvo expirou" end
			limparAlvo(motivo); return
		end
		local r = c.HumanoidRootPart
		local dA = dToca(r.Position)
		if dA > CFG.raioColeira + A.defesaSai then
			C.foraDesde = C.foraDesde or agora
			if agora - C.foraDesde >= A.foraSeg then limparAlvo("alvo saiu do territorio"); return end
		else
			C.foraDesde = nil
			local coleta = pastaAlcateia:GetAttribute("AlvoMotivo") == "coleta"   -- oficial: a coleta e sempre percebida
			if vistoPorAlguem(uidAlvo) or (coleta and agora - C.nivelDesde < A.memoriaDefesa) then
				pastaAlcateia:SetAttribute("AlvoAte", agora + A.memoriaDefesa)
			end
		end
		pastaAlcateia:SetAttribute("TensaoPos", r.Position)
		if tensao() ~= "Defesa" then mudarNivel("Defesa", pastaAlcateia:GetAttribute("AlvoMotivo") or "defesa") end
		return
	end
	if tensao() == "Defesa" then limparAlvo("sem alvo") return end
	-- 2. intruso percebido (visto por algum membro, dentro da memoria)
	local uid, p, dA = avistamentos()                                -- dA = distancia ate a toca (r3b)
	local inv = pastaAlcateia:GetAttribute("InvestigarPos")
	if not uid then
		if inv and agora <= (pastaAlcateia:GetAttribute("InvestigarAte") or 0) then
			pastaAlcateia:SetAttribute("TensaoPos", inv); C.gatilhoT = agora
			if tensao() == "Calmo" then mudarNivel("Atencao", "investigar dano sem autoria") end
			return
		end
		if tensao() ~= "Calmo" and agora - C.gatilhoT >= A.calma then
			mudarNivel(NIVEL[tensao()] >= 2 and "Atencao" or "Calmo", "sem intruso a vista: acalma")
			C.gatilhoT = agora
		end
		return
	end
	if pastaAlcateia:GetAttribute("TensaoId") ~= uid then
		pastaAlcateia:SetAttribute("TensaoId", uid); C.dRef = nil; C.criticoDesde = nil; C.visivelDesde = nil
	end
	pastaAlcateia:SetAttribute("TensaoPos", p)
	local nivel = tensao()
	local dL = distAoBando(p, CFG.raioAlvo)
	local rAv = A.raioAviso + (nivel == "Ameaca" and A.histerese or 0)
	local rAt = A.raioAtencao + (nivel ~= "Calmo" and A.histerese or 0)
	local lAv = A.avisoLobo + (nivel == "Ameaca" and A.histerese or 0)
	local lAt = A.atencaoLobo + (nivel ~= "Calmo" and A.histerese or 0)
	local quer = (dA <= rAv or dL <= lAv) and "Ameaca" or ((dA <= rAt or dL <= lAt) and "Atencao" or "Calmo")
	if NIVEL[quer] >= NIVEL[nivel] then C.gatilhoT = agora end
	-- subir: Atencao antes de Ameaca (atencaoMin), salvo intruso ja na zona critica; descer: so apos `calma` s
	if NIVEL[quer] > NIVEL[nivel] then
		local dNc = dNucleo(p)
		local esperaAtencao = quer == "Ameaca" and nivel == "Atencao" and agora - C.nivelDesde < A.atencaoMin and dNc > A.raioCritico
		if quer == "Ameaca" and nivel == "Calmo" and dNc > A.raioCritico then mudarNivel("Atencao", "intruso a vista")
		elseif not esperaAtencao then mudarNivel(quer, quer == "Ameaca" and "intruso perto da toca: aviso" or "intruso a vista") end
	elseif NIVEL[quer] < NIVEL[nivel] and agora - C.gatilhoT >= A.calma then
		mudarNivel(nivel == "Ameaca" and "Atencao" or "Calmo", "intruso recuou: acalma")
		C.gatilhoT = agora
	end
	-- 3. durante o aviso: insistencia, zona critica, encostar -> Defesa (so depois de avisoMin)
	if tensao() == "Ameaca" then
		-- r3d: o aviso so conta depois que o intruso ficou ao alcance de VER o lobo ameacando (dL em unidades de Escala)
		if dL <= A.avisoVisivel then C.visivelDesde = C.visivelDesde or agora end
		local tAv = C.visivelDesde and (agora - C.visivelDesde) or 0
		-- referencia da insistencia: so conta o avanco DEPOIS de avisoMin (o jogador que vinha andando precisa de tempo
		-- para ver o aviso e parar; simulacao r3: sem isso quem parava logo depois do aviso era atacado)
		local dN = dNucleo(p)                                            -- r3c: avanco/recuo/zona critica medidos ate o nucleo
		if tAv < A.avisoMin then C.dRef = dN else C.dRef = math.max(C.dRef or dN, dN) end
		local recuando = dN > (C.dMin or dN) + A.recuo
		C.dMin = math.min(C.dMin or dN, dN); if recuando then C.dMin = dN; C.criticoDesde = nil end
		pastaAlcateia:SetAttribute("Recuando", recuando)
		if dN <= A.raioCritico and C.visivelDesde then C.criticoDesde = C.criticoDesde or agora elseif dN > A.raioCritico then C.criticoDesde = nil end
		pastaAlcateia:SetAttribute("AvisoSeg", math.floor(tAv * 10) / 10)
		pastaAlcateia:SetAttribute("DistNucleo", math.floor(dN))
		if tAv >= A.avisoMin then
			if C.dRef - dN >= A.insistencia and not recuando and dA <= A.raioAviso then definirAlvo(uid, "insistiu apos o aviso")
			elseif dL <= A.encostar then definirAlvo(uid, "encostou no lobo apos o aviso")
			elseif C.criticoDesde and agora - C.criticoDesde >= A.avisoCritico then definirAlvo(uid, "ficou na zona critica") end
		end
	else
		C.dMin = nil
	end
end

-- rotinas -------------------------------------------------------------------------------------------------------------------
local estado, alvoRotina, estadoAte = nil, nil, 0
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
local chegouEm
local function iniciar(n)
	estado = n; alvoRotina = nil; chegouEm = nil
	if n == "Dormir" then estadoAte = os.clock() + rand(CFG.durDormir); alvoRotina = pontoDescanso + Vector3.new(math.random(-4, 4), 0, math.random(-4, 4))
	elseif n == "Guardar" then estadoAte = os.clock() + rand(CFG.durGuardar); alvoRotina = pontoAbrigo + Vector3.new(math.random(-5, 5), 0, math.random(-5, 5))
	elseif n == "Cacar" then estadoAte = os.clock() + rand(CFG.durCacar) + 60; alvoRotina = zonas[math.random(1, math.max(1, #zonas))]
	elseif n == "Patrulhar" then estadoAte = os.clock() + 240; alvoRotina = 1 end
	pasta:SetAttribute("IA_Estado", n)
end
local function rotina()
	if not estado or os.clock() > estadoAte then iniciar(escolherRotina()) end
	if estado == "Patrulhar" then
		if #rota == 0 then estado = nil; return end
		local s = irPara(rota[alvoRotina], "andar")
		if s == "chegou" then alvoRotina += 1; if alvoRotina > #rota then estado = nil end
		elseif s == "falhou" then alvoRotina += 1; if alvoRotina > #rota then estado = nil end end   -- pula o ponto inviavel
		return
	end
	local alvo = alvoRotina or pontoDescanso
	if not chegouEm then
		local marcha = (plano(alvo - pos()).Magnitude > 60) and "trote" or "andar"
		local s = irPara(alvo, marcha)
		if s == "falhou" then estado = nil; return end                                          -- r2 C: abandono controlado
		if s == "chegou" then chegouEm = os.clock()
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

-- defesa: aproximacao, contato e mordida (r2 A/B) ----------------------------------------------------------------------------
local ultimaMordida, uivou, uivandoAte, contato = 0, 0, 0, false
local est = {}                                                                     -- estacao de reposicionamento
local function companheiros()
	local l = {}
	for _, f in ipairs(pastaAlcateia:GetChildren()) do
		local o = f ~= pasta and f:FindFirstChild("LoboArtico_LOW")
		if o then table.insert(l, o:GetPivot().Position) end
	end
	return l
end
local function separar(d)
	local e = esc(); local p = pos(); local rep = Vector3.zero
	for _, q in ipairs(companheiros()) do
		local v = plano(p - q); local m = v.Magnitude
		if m > 0.05 and m < CFG.separacao * e then rep += v.Unit * (1 - m / (CFG.separacao * e)) end
	end
	if d.Magnitude < 1e-3 then return rep end
	return d.Unit + rep * 0.8
end
local function geometria(alvoPos)
	local e = esc(); local pv = lobo:GetPivot()
	local fr = plano(pv.LookVector); fr = fr.Magnitude > 0 and fr.Unit or Vector3.new(0, 0, -1)
	local rel = plano(alvoPos - pv.Position)
	local focinho = pv.Position + fr * CFG.focinho * e
	local dF = plano(alvoPos - focinho).Magnitude                                -- = medida de alcance do Kit
	local along = rel:Dot(fr)
	local lado = math.abs(rel:Dot(Vector3.new(-fr.Z, 0, fr.X)))
	local ang = rel.Magnitude > 0.05 and math.deg(math.acos(math.clamp(rel.Unit:Dot(fr), -1, 1))) or 180
	local sobTronco = along > -CFG.troncoAtras * e and along < (CFG.focinho - 0.8) * e and lado < CFG.troncoLado * e
	local colado = along >= (CFG.focinho - 0.8) * e and dF < 0.7 * e         -- alvo dentro do focinho
	return {e = e, fr = fr, rel = rel, dF = dF, ang = ang, sob = sobTronco or colado}
end
local function estacao(alvoPos, e)
	-- r2 B: entre 8 pontos a D do alvo, o de menor custo (virar agora + andar + virar no fim para o alvo); rota que passa
	-- por cima do alvo e penalizada. (Espelhado e conferido em simular_contato_r2.py.)
	local D = CFG.focinho * e + CFG.raioAlvo + CFG.estacaoFolga * e
	local pv = lobo:GetPivot(); local p = plano(pv.Position); local fr = plano(pv.LookVector).Unit
	local a2 = plano(alvoPos)
	local melhor, cm
	for k = 0, 7 do
		local u = CFrame.Angles(0, k * math.pi / 4, 0):VectorToWorldSpace(Vector3.new(0, 0, 1))
		local S = a2 + u * D; local ida = S - p
		if ida.Magnitude < 0.5 then return Vector3.new(S.X, alvoPos.Y, S.Z) end
		local function giro(x, y) return math.acos(math.clamp(x.Unit:Dot(y.Unit), -1, 1)) end
		local c = giro(fr, ida) / math.rad(45) + ida.Magnitude / (3.0 * e) + giro(ida, -u) / math.rad(45)
		local w = a2 - p; local t = math.clamp(w:Dot(ida) / math.max(ida:Dot(ida), 1e-6), 0, 1)
		if t > 0.15 and (a2 - (p + ida * t)).Magnitude < 2.0 * e then c += 6 end
		if not cm or c < cm then melhor, cm = S, c end
	end
	return Vector3.new(melhor.X, alvoPos.Y, melhor.Z)
end
local function morderSePuder(c, g)
	local alcance = CFG.alcanceKit * g.e + CFG.folgaKit
	if g.dF <= alcance and g.ang <= CFG.coneMordida and os.clock() - ultimaMordida >= CFG.intervaloMordida then
		ultimaMordida = os.clock(); evAcao:Fire("basico", c)
	end
end
-- r3: velocidade do pivo (para a frenagem; o Controle move por PivotTo, a fisica nao tem velocidade)
local pAnt, tAnt, velLobo = nil, os.clock(), 0
local function medirVel()
	local p, t = pos(), os.clock()
	if pAnt and t > tAnt then velLobo = plano(p - pAnt).Magnitude / (t - tAnt) end
	pAnt, tAnt = p, t
end
local function frenagem() return velLobo * velLobo / (2 * CFG.desacel) end
local function sinal(n)                                            -- sinal corporal (clipe so se existir) + rotulo
	pasta:SetAttribute("IA_Sinal", n)
	if n and faixa(n) then pose(n, 0.3) elseif poseAtual == "Alerta" or poseAtual == "Ameaca" then pose(nil) end
end

-- Atencao: para e encara a distancia (sem andar para o intruso) ----------------------------------------------------------------
local function atencao(alvoP)
	if poseAtual == "Dormindo" or poseAtual == "Farejando" then sairDaPose() end
	estado = nil; contato = false
	pasta:SetAttribute("IA_Estado", "Atencao"); pasta:SetAttribute("IA_Contato", nil)
	local d = plano(alvoP - pos())
	-- o Guardiao volta ao lado do ovo se estiver longe; os outros param onde estao
	if papel == "Guardiao" and plano(pontoAbrigo - pos()).Magnitude > A.guardiaoPosto + CFG.chegada + 4 then
		if irPara(pontoAbrigo, "andar") == "andando" then return end
	end
	if d.Magnitude > 0.5 then olhar(d) else parar() end
	sinal("Alerta")
end

-- Ameaca: posto entre o intruso e o recurso, parado, de frente, a distancia de confronto -----------------------------------------
local ladoFlanco = (pasta.Name:byte(#pasta.Name) or 0) % 2 == 0 and 1 or -1
local function postoAmeaca(intrP)
	local e = esc(); local raio = CFG.raioAlvo
	-- ancora: o abrigo se o intruso esta dentro da toca; senao a entrada (os postos ficam do lado de fora da rocha)
	cadeia = cadeia or construirCadeia()
	local it, dt = prox(intrP)
	local dentro = it > 3 and dt < 15 and coberto(intrP)
	local ancora = pontoEntrada                                         -- fora da toca: a entrada
	if dentro then                                                      -- r3c: dentro: o ponto do NUCLEO (descanso -> abrigo) mais perto
		local dm = math.huge
		for i = iNucleo, #cadeia do local d = (cadeia[i] - intrP).Magnitude; if d < dm then dm, ancora = d, cadeia[i] end end
	end
	-- r3c: intruso longe da toca (encontro em patrulha/caca): firma posicao onde esta, sem ir ate a entrada
	if dt > A.raioAtencao + A.histerese and papel ~= "Guardiao" then return pos() end
	if papel == "Guardiao" then
		local dir = plano(intrP - pontoAbrigo); dir = dir.Magnitude > 0.1 and dir.Unit or Vector3.new(0, 0, 1)
		return pontoAbrigo + dir * A.guardiaoPosto
	end
	local v = plano(intrP - ancora); local dist = v.Magnitude
	local dir = dist > 0.1 and v.Unit or Vector3.new(0, 0, 1)
	local minIntr = (A.distConfronto + CFG.focinho) * e + raio          -- pivo -> intruso para o focinho ficar a distConfronto
	local k = math.clamp(dist * A.postoFracao, 0, A.postoMax)
	k = math.min(k, math.max(0, dist - minIntr))                       -- nunca mais perto do intruso que a distancia de confronto
	local posto = ancora + dir * k
	if papel ~= "Lider" then                                           -- Membro: flanco, um pouco atras do Lider
		local perp = Vector3.new(-dir.Z, 0, dir.X)
		posto = posto + perp * (A.flanco * e * ladoFlanco) - dir * (A.flancoAtras * e)
	end
	return Vector3.new(posto.X, ancora.Y, posto.Z)
end
local function ameacar(intrP)
	if poseAtual == "Dormindo" or poseAtual == "Farejando" then sairDaPose() end
	estado = nil; contato = false
	pasta:SetAttribute("IA_Estado", "Ameacar")
	local e = esc()
	local posto = postoAmeaca(intrP)
	local dF = plano(intrP - (pos() + plano(lobo:GetPivot().LookVector).Unit * CFG.focinho * e)).Magnitude - CFG.raioAlvo
	pasta:SetAttribute("IA_DistFocinho", math.floor(dF * 10) / 10)
	-- ja esta perto demais do intruso (ele veio ate o lobo): nao avanca; encara (recuar = clipe ausente)
	if dF < A.distConfronto * e then
		pasta:SetAttribute("IA_Contato", "confronto: segura a posicao")
		olhar(plano(intrP - pos())); sinal("Ameaca"); return
	end
	if plano(posto - pos()).Magnitude > CFG.chegada then
		pasta:SetAttribute("IA_Contato", "indo ao posto")
		sinal(nil)
		local marcha = plano(posto - pos()).Magnitude > 25 and "trote" or "andar"
		local s = irPara(posto, marcha)
		if s == "andando" then return end
		if s == "falhou" then pasta:SetAttribute("IA_Contato", "posto inviavel: encara daqui") end
	else
		pasta:SetAttribute("IA_Contato", "no posto")
	end
	olhar(plano(intrP - pos())); sinal("Ameaca")
	if papel == "Lider" then pasta:SetAttribute("IA_Vocal", "rosnado")   -- gancho do som futuro (nao ha som aprovado)
	end
end

-- Defesa: aproximacao, contato e mordida (r2 A/B + r3 volume do alvo, frenagem, visao, Guardiao no ovo) -------------------------
local function defender(c)
	local r = c:FindFirstChild("HumanoidRootPart"); if not r then return end
	if poseAtual then sairDaPose() end
	estado = nil; pasta:SetAttribute("IA_Estado", "Defender"); pasta:SetAttribute("IA_Sinal", nil)
	pasta:SetAttribute("IA_Motivo", pastaAlcateia:GetAttribute("AlvoMotivo"))
	if os.clock() < uivandoAte then parar(); return end                           -- r2 E: uivo sem travar a IA
	-- r3: posicao usada = real se este lobo o viu ha pouco (ou e a coleta, sempre percebida); senao a ultima vista
	local uid = Players:GetPlayerFromCharacter(c) and Players:GetPlayerFromCharacter(c).UserId
	local visto, m = viuRecente(uid)
	local coleta = pastaAlcateia:GetAttribute("AlvoMotivo") == "coleta"
	local alvoPos = r.Position
	if not coleta and not (visto and os.clock() - m.t <= 2) then
		local tp = pastaAlcateia:GetAttribute("TensaoPos"); alvoPos = (m and m.pos) or tp or r.Position
		pasta:SetAttribute("IA_Contato", "procura onde viu o alvo")
		if plano(alvoPos - pos()).Magnitude > CFG.chegada + 3 then irPara(alvoPos, "trote") else olhar(plano(alvoPos - pos())) end
		return
	end
	-- r3: o Guardiao (responsavel pelo ovo) so deixa o ovo para alvo perto do abrigo
	if papel == "Guardiao" and (alvoPos - pontoAbrigo).Magnitude > A.guardiaoDefende then
		pasta:SetAttribute("IA_Contato", "guarda o ovo")
		local posto = pontoAbrigo + plano(alvoPos - pontoAbrigo).Unit * A.guardiaoPosto
		if plano(posto - pos()).Magnitude > CFG.chegada and irPara(posto, "trote") == "andando" then return end
		olhar(plano(alvoPos - pos())); return
	end
	local g = geometria(alvoPos)
	-- r2h: Uivo Boreal (PODER, com bonus) so ja em Defesa e de LONGE; nao e o aviso
	if papel == "Lider" and os.clock() - uivou > 40 and g.dF > 25 * g.e then
		uivou = os.clock(); uivandoAte = os.clock() + 6.9; parar(); evUivo:Fire(); return
	end
	-- r3: parada pelo volume do alvo e pela frenagem; nunca alem do alcance de mordida do Kit
	local raio = raioDoAlvo(c)
	local alcance = CFG.alcanceKit * g.e + CFG.folgaKit
	local entra = math.min(alcance - 0.3, math.max(CFG.contatoEntra * g.e, raio + 1.2 * g.e))
	local sai = math.max(entra + 1.0, math.min(alcance + 1.0, CFG.contatoSai * g.e))
	local dPar = g.dF - frenagem()
	contato = (contato and g.dF <= sai) or (dPar <= entra)                       -- histerese
	pasta:SetAttribute("IA_DistFocinho", math.floor(g.dF * 10) / 10)
	pasta:SetAttribute("IA_Frenagem", math.floor(frenagem() * 10) / 10)
	if est.ponto and ((alvoPos - est.alvo).Magnitude > 3 or os.clock() > est.ate) then est.ponto = nil end
	if g.sob or est.ponto then
		contato = false; pasta:SetAttribute("IA_Contato", "reposicionar")
		if not est.ponto then est.ponto, est.alvo, est.ate = estacao(alvoPos, g.e), alvoPos, os.clock() + 8 end
		if plano(est.ponto - pos()).Magnitude < 1.0 then est.ponto = nil; olhar(g.rel); return end
		pose(nil); evMover:Fire(separar(plano(est.ponto - pos())), "andar")
		return
	end
	if not contato and g.dF <= 15 * g.e and g.ang > 50 then
		pasta:SetAttribute("IA_Contato", "virando para o alvo")
		olhar(g.rel); return
	end
	if contato then
		pasta:SetAttribute("IA_Contato", "contato")
		olhar(g.rel)
		morderSePuder(c, g)
	elseif g.dF <= CFG.aproxima * g.e then
		pasta:SetAttribute("IA_Contato", "aproximando")
		local vAlvo = plano(r.AssemblyLinearVelocity).Magnitude
		pose(nil); evMover:Fire(separar(g.rel), vAlvo > 2.5 * g.e and "trote" or "andar")
		morderSePuder(c, g)
	else
		pasta:SetAttribute("IA_Contato", "perseguindo")
		local fuga = plano(r.AssemblyLinearVelocity):Dot(plano(alvoPos - pos()).Unit)
		local marchaP = (g.dF > CFG.perseguirCorrendo * g.e or fuga > 5 * g.e) and "correr" or "trote"
		local s
		cadeia = cadeia or construirCadeia()
		local ipL, dpL = prox(pos()); local ipA, dpA = prox(alvoPos)
		local dentroL = ipL > 3 and dpL < 15 and coberto(pos())
		local dentroA = ipA > 3 and dpA < 15 and coberto(alvoPos)
		if not dentroL and not dentroA and (linhaLivre(pos(), alvoPos) or g.dF < 20 * g.e) then
			pose(nil); evMover:Fire(separar(plano(alvoPos - pos())), marchaP); s = "andando"
		else
			s = irPara(alvoPos, marchaP)
		end
		if s == "chegou" then
			pasta:SetAttribute("IA_Contato", "limite da toca: encara")
			olhar(plano(alvoPos - pos()))
		elseif s == "falhou" then
			pasta:SetAttribute("IA_Contato", "sem caminho: volta ao posto")
			local postoOvo = pontoAbrigo + plano(alvoPos - pontoAbrigo).Unit * 6
			if irPara(postoOvo, "trote") ~= "andando" then olhar(plano(alvoPos - pos())) end
		end
	end
end

-- nocaute (igual a r1e; no plano) ---------------------------------------------------------------------------------------------
local function nocaute()
	pasta:SetAttribute("IA_Estado", "Nocaute"); parar(); tocarUmaVez("Deitar", "Dormindo"); lobo:SetAttribute("Incapacitado", true)
	task.wait(CFG.nocauteSeg)
	if not lobo.Parent then return end
	lobo:SetAttribute("Vida", lobo:GetAttribute("VidaMax") or 400); lobo:SetAttribute("Incapacitado", nil)
	sairDaPose(); estado = nil
end

lobo:SetAttribute("Selvagem", true)
script:SetAttribute("Versao", "r3d 20/11 (aviso conta so quando visivel) | r3c 20/11 (nucleo da toca; firma posicao longe da toca) | r3b 20/11 (Folders; raios ate a toca inteira) | r3 20/11 (Atencao/Ameaca/Defesa/Desengajar; coordenador; visao; autoria do dano) | r2j 20/11 (contato, caminho, toca)")
task.wait(math.random() * 2)
local nivelAnt = "Calmo"
while lobo.Parent do
	if workspace:GetAttribute("IA_LoboArtico_Ativa") == false then parar(); task.wait(2); continue end
	if (lobo:GetAttribute("Vida") or 1) <= 0 then nocaute(); continue end
	if jogadorMaisPerto() > CFG.raioDormente then
		if estado ~= "Dormir" or not chegouEm then parar() end
		task.wait(CFG.tickDormente); continue
	end
	medirVel()
	perceber()
	if souCoordenador() then coordenar() end
	local nivel = tensao()
	local alvoP = pastaAlcateia:GetAttribute("TensaoPos")
	if nivel == "Defesa" then
		local c = alvoAlcateia()
		if c then defender(c) else atencao(alvoP or pos()) end
	elseif nivel == "Ameaca" and alvoP then
		ameacar(alvoP)
	elseif nivel == "Atencao" and alvoP then
		atencao(alvoP)
	else
		contato = false
		if pasta:GetAttribute("IA_Contato") then pasta:SetAttribute("IA_Contato", nil) end
		if pasta:GetAttribute("IA_Sinal") then sinal(nil) end
		pasta:SetAttribute("IA_Vocal", nil)
		-- Desengajar: ao voltar da tensao, a rotina recomeca por Guardar (volta ao posto perto do ovo, andando)
		if nivelAnt ~= "Calmo" then iniciar("Guardar"); pasta:SetAttribute("IA_Motivo", "desengajou: volta ao posto") end
		rotina()
	end
	nivelAnt = nivel
	task.wait(CFG.tick)
end
