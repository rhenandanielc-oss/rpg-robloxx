-- IA_LoboArtico (Script dentro da pasta de UM lobo selvagem, criada pelo IA_LoboArtico_Servidor) - r2c 19/11/2026 (LOCAL,
-- nao instalada/testada no Studio). Copia da r1e: IA_LoboArtico_r1e.server.luau.
-- Pedido 19/11 ("corrigir a IA e aproximar de lobos reais", 1a entrega): correcao PEQUENA de navegacao e contato de ataque.
--   A. Contato: distancia medida do FOCINHO (Kit: focinho 6,2 x Escala) ao centro do alvo, com o alcance do Kit
--      (3,5 x Escala + 1,5) e cone (75 graus -> mordida so ate 30 graus). Faixa de contato com HISTERESE (entra <= 3,2,
--      sai > 4,6, x Escala): no contato o lobo PARA e so se orienta (Controle r7 IA_Olhar, sem giro instantaneo);
--      entre o contato e 8 x Escala aproxima andando (pode morder andando); alem disso persegue (trote/correr).
--   B. Alvo sob o tronco (entre ancas e focinho) ou colado no focinho: REPOSICIONA para uma estacao a frente do alvo
--      (angulo proprio por membro) em vez de andar por cima dele. Repulsao de membros da alcateia a < 3,5 x Escala.
--   C. Caminho: irPara/irParaFora devolvem "chegou" | "andando" | "falhou". NoPath so vira linha reta se um Spherecast
--      do tamanho do lobo diz que a linha esta livre; 3 travamentos seguidos = "falhou" (antes devolvia true = chegada).
--      Falha numa rotina = abandono controlado (atributo IA_Falha, proxima rotina); na defesa = volta ao posto do ovo e
--      encara a ameaca.
--   D. Toca por porte: a cadeia (agente pequeno) e conferida com Blockcast do tamanho do lobo da idade; o 1o trecho
--      bloqueado vira limite (IA_CadeiaBloqueio) e destinos alem dele param no ultimo ponto valido.
--   E. Callbacks: token de geracao nas poses (pose antiga atrasada nao volta); o Uivo de aviso nao trava a IA 6,9 s.
-- O resto (percepcao, culpa do agressor, alerta escalonado, caca real, papeis) segue a r1e e esta no PLANO (§8.79).
-- Numeros e rotina = [PROPOSTA][A TESTAR]. Dano, recarga e alcance continuam os do Kit (nao mudam aqui).
local Players = game:GetService("Players")
local PFS = game:GetService("PathfindingService")
local KSP = game:GetService("KeyframeSequenceProvider")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local lib = game:GetService("ReplicatedStorage"):WaitForChild("Animacoes_LoboArtico")
local habitat = workspace.Tundra_Congelada.Habitats.Ecologia_Fauna.Lobo_Artico:FindFirstChild(pasta:GetAttribute("AlcateiaPasta") or "")
assert(habitat, "habitat da alcateia nao achado")

local CFG = {
	raioAlerta = 40, raioDefesa = 22, raioColeira = 75,      -- do ovo/abrigo (Urso usa 40/22/60) [PROPOSTA]
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
	corpoLargura = 2.0, corpoAltura = 4.0,                    -- caixa do Blockcast da toca (x Escala) [A TESTAR]
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
local travaRef, travaT, falhas = nil, 0, 0
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
	if not travaRef or (p - travaRef).Magnitude > 1 then travaRef, travaT = p, os.clock()
	elseif os.clock() - travaT > 3 then
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
local function construirCadeia()
	local c = {pontoEntrada}
	local path = PFS:CreatePath({AgentRadius = 1, AgentHeight = 3, AgentCanJump = true, WaypointSpacing = 6})
	pcall(function() path:ComputeAsync(pontoEntrada, pontoDescanso) end)
	if path.Status == Enum.PathStatus.Success then for _, w in ipairs(path:GetWaypoints()) do table.insert(c, w.Position) end end
	table.insert(c, pontoDescanso)
	local n = math.max(1, math.floor((pontoAbrigo - pontoDescanso).Magnitude / 6))
	for k = 1, n do table.insert(c, pontoDescanso:Lerp(pontoAbrigo, k / n)) end
	-- r2 D: o lobo desta idade cabe? Blockcast de uma caixa do corpo entre pontos seguidos (chao + folga)
	filtrosLivres()
	local e = esc(); local caixa = Vector3.new(CFG.corpoLargura * e, CFG.corpoAltura * e, 0.5)
	limiteCadeia = #c
	for i = 1, #c - 1 do
		local a = c[i] + Vector3.new(0, CFG.corpoAltura * e / 2 + 0.6, 0); local b = c[i + 1] + Vector3.new(0, CFG.corpoAltura * e / 2 + 0.6, 0)
		local d = b - a
		if d.Magnitude > 0.2 then
			local r = workspace:Blockcast(CFrame.lookAt(a, b), caixa, d, rpLivre)
			if r then
				limiteCadeia = i
				pasta:SetAttribute("IA_CadeiaBloqueio", string.format("trecho %d->%d bloqueado em (%d,%d,%d) por %s (escala %.2f)", i, i + 1, r.Position.X, r.Position.Y, r.Position.Z, r.Instance.Name, e))
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
local function andarReto(ponto, marcha)
	local d = plano(ponto - pos())
	if d.Magnitude < CFG.chegada then return "chegou" end
	pose(nil); evMover:Fire(d, marcha); return "andando"
end
local function irPara(destino, marcha)
	cadeia = cadeia or construirCadeia()
	local ip, dp = prox(pos()); local it, dt = prox(destino)
	local loboDentro = ip > 1 and dp < 15
	local destDentro = it > 1 and dt < 15
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

-- percepcao (igual a r1e; revisao no plano) ----------------------------------------------------------------------------------
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
local function alvoAlcateia()
	local nome = pastaAlcateia:GetAttribute("AlvoJogador")
	local ate = pastaAlcateia:GetAttribute("AlvoAte") or 0
	if not nome or os.clock() > ate then return nil end
	local j = Players:FindFirstChild(nome); return j and j.Character
end
local function avisar(c, seg) local j = Players:GetPlayerFromCharacter(c); if j then pastaAlcateia:SetAttribute("AlvoJogador", j.Name); pastaAlcateia:SetAttribute("AlvoAte", os.clock() + (seg or 12)) end end
local vidaAnt = lobo:GetAttribute("Vida") or 400
lobo:GetAttributeChangedSignal("Vida"):Connect(function()
	local v = lobo:GetAttribute("Vida") or 0
	if v < vidaAnt then local c = jogadoresPerto(pos(), 30); if c then avisar(c, 15) end end   -- (achado 2: no plano)
	vidaAnt = v
end)

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
local function defender(c)
	local r = c:FindFirstChild("HumanoidRootPart"); if not r then return end
	if poseAtual then sairDaPose() end
	estado = nil; pasta:SetAttribute("IA_Estado", "Defender")
	if os.clock() < uivandoAte then parar(); return end                           -- r2 E: uivo sem travar a IA
	local g = geometria(r.Position)
	if papel == "Lider" and os.clock() - uivou > 40 and g.dF > 14 then
		uivou = os.clock(); uivandoAte = os.clock() + 6.9; parar(); evUivo:Fire(); return
	end
	contato = (contato and g.dF <= CFG.contatoSai * g.e) or (g.dF <= CFG.contatoEntra * g.e)   -- histerese
	-- r2 B: alvo sob o tronco/colado -> vai para uma estacao (fixa por ate 8 s, refeita se o alvo andar > 3)
	if est.ponto and ((r.Position - est.alvo).Magnitude > 3 or os.clock() > est.ate) then est.ponto = nil end
	if g.sob or est.ponto then
		contato = false; pasta:SetAttribute("IA_Contato", "reposicionar")
		if not est.ponto then est.ponto, est.alvo, est.ate = estacao(r.Position, g.e), r.Position, os.clock() + 8 end
		if plano(est.ponto - pos()).Magnitude < 1.0 then est.ponto = nil; olhar(g.rel); return end
		pose(nil); evMover:Fire(separar(plano(est.ponto - pos())), "andar")
		return
	end
	if contato then
		pasta:SetAttribute("IA_Contato", "contato")
		olhar(g.rel)                                                                  -- para e mantem orientacao
		morderSePuder(c, g)
	elseif g.dF <= CFG.aproxima * g.e then
		pasta:SetAttribute("IA_Contato", "aproximando")
		local vAlvo = plano(r.AssemblyLinearVelocity).Magnitude                        -- alvo andando: acompanha em trote
		pose(nil); evMover:Fire(separar(g.rel), vAlvo > 2.5 * g.e and "trote" or "andar")   -- desacelera e pode morder andando
		morderSePuder(c, g)
	else
		pasta:SetAttribute("IA_Contato", "perseguindo")
		local s = irPara(r.Position, g.dF > CFG.perseguirCorrendo * g.e and "correr" or "trote")
		if s == "falhou" then                                                         -- r2 C: caminho inviavel -> posto do ovo
			pasta:SetAttribute("IA_Contato", "sem caminho: volta ao posto")
			local posto = pontoAbrigo + plano(r.Position - pontoAbrigo).Unit * 6
			if irPara(posto, "trote") ~= "andando" then olhar(plano(r.Position - pos())) end
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
task.wait(math.random() * 2)
while lobo.Parent do
	if workspace:GetAttribute("IA_LoboArtico_Ativa") == false then parar(); task.wait(2); continue end
	if (lobo:GetAttribute("Vida") or 1) <= 0 then nocaute(); continue end
	if jogadorMaisPerto() > CFG.raioDormente then
		if estado ~= "Dormir" or not chegouEm then parar() end
		task.wait(CFG.tickDormente); continue
	end
	local intruso = alvoAlcateia()
	local cAbr = jogadoresPerto(pontoAbrigo, CFG.raioAlerta)
	if cAbr then avisar(cAbr, 10); intruso = intruso or cAbr end
	if not intruso and papel ~= "Guardiao" then local c = jogadoresPerto(pos(), CFG.raioDefesa); if c then intruso = c end end
	if intruso then
		local r = intruso:FindFirstChild("HumanoidRootPart")
		if r and (r.Position - pontoAbrigo).Magnitude <= CFG.raioColeira or (r and (r.Position - pos()).Magnitude < CFG.raioDefesa) then
			defender(intruso)
		else
			pastaAlcateia:SetAttribute("AlvoJogador", nil); estado = nil; contato = false
		end
	else
		contato = false
		rotina()
	end
	task.wait(CFG.tick)
end
