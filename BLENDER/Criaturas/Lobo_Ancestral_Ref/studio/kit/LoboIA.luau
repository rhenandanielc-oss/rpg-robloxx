-- LoboIA (ModuleScript filho de ServerScriptService.LoboAncestral_Kit.LoboKit_Servidor) - IA ESTRATEGICA do Lobo Ancestral,
-- PROTOTIPO no place isolado Testes-loboancestral (19/11/2026). Fonte: BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/kit/LoboIA.luau.
-- NAO integrada ao jogo principal. Todos os numeros em ConfigKitLobo.IA_Lobo sao [PROPOSTA]/[A TESTAR].
--
-- Principios adaptados da IA dos dragoes (src/ServerScriptService/IA_Dragao/Cerebro, Locomotor; Combate_Dragao_Servidor;
-- duelo tatico de teste 09/11), SEM copiar voo, distancias nem regras de ninho:
--   * memoria de ameaca por alvo (nivel, motivo, ultima posicao, tempo) com esquecimento (lembrar) e investigacao da ultima
--     posicao de quem sumiu; troca de alvo so com vantagem clara (histerese);
--   * planos com tempo minimo (sem tremer entre planos); interrupcao imediata so por motivo urgente (ataque anunciado,
--     vida critica, alvo invalido/protegido);
--   * escolha de golpe por condicoes REAIS (alcance ate a superficie, cone, linha de visao, corredor livre, chao do pouso,
--     energia, recarga), com peso + pequena variacao REGISTRADA; todo bloqueio vai para o log com o motivo;
--   * locomocao ancorada por PivotTo na velocidade de cada clipe (sem patinar), sempre para a FRENTE com giro limitado por
--     marcha (sem deslizar de lado); giro grande parado = clipes VirarE/D; desvio de obstaculo por sondas;
--   * frequencia de decisao menor sem jogador por perto.
-- Separacao: PERCEPCAO/AMEACA -> PLANO -> LOCOMOCAO (Heartbeat) -> EXECUCAO (mesmas funcoes do jogador: K.acaoIA ->
-- ACOES do kit, com podeUsar/energia/recarga/alcance/protecoes validados no servidor, inclusive no impacto).
-- Lobo do DONO: nao usa esta IA (comportamento de seguir inalterado). Liga com L.ia = {v2 = true, posto = Vector3}.
local RS = game:GetService("RunService")
local Players = game:GetService("Players")

local M = {}
local A, CFG, P, G               -- api do kit, config, IA_Lobo, IA_Guardiao (gatilhos/coleira ja documentados)
local O_CURVA = CFrame.new(0, 0, -2.196)   -- gira em volta do meio do corpo (mesmo centro das curvas do Blender)

local function flat(v) return Vector3.new(v.X, 0, v.Z) end
local folgaCapsulas
local function angAssinado(de, para)      -- + = para a esquerda
	if de.Magnitude < 1e-3 or para.Magnitude < 1e-3 then return 0 end
	de, para = de.Unit, para.Unit
	return math.atan2(de:Cross(para).Y, de:Dot(para))
end
local function girar(v, ang) return CFrame.Angles(0, ang, 0):VectorToWorldSpace(v) end

-- ------------------------------------------------------------------ utilidades de log
local function rc(L, n) local r = L.recargas[n]; local s = r and (r - os.clock()) or 0; return s > 0 and string.format("%.1f", s) or "0" end
local function status(L)
	return string.format("vida %.0f en %.0f rc[S %s I %s U %s M %s G %s]", L.vida, L.energia, rc(L, "SaltoPredatorio"), rc(L, "Investida"),
		rc(L, "UivoAncestral"), rc(L, "Mordida"), rc(L, "Garra"))
end
local function logIA(L, s) A.logc("IA", L, s) end

-- ------------------------------------------------------------------ PERCEPCAO / AMEACA
-- Gatilhos = os do guardiao ja documentados (IA_Guardiao): perto (<= raioAmeaca), aproximando (>= aproximacao studs/s ate
-- raioAlerta) ou atacou o lobo. Percebido ate raioAlerta sem gatilho = so ALERTA (olha, rosna; nao ataca).
-- [PROPOSTA] lobo sem dono ignora outro lobo sem dono (mesma especie) a menos que seja atacado por ele: nao ha regra de
-- alcateia; evita agressao gratuita entre guardioes.
local function ehLoboSelvagem(m) local x = A.lobos[m]; return x ~= nil and x.dono == nil end
local function ameacaDe(L, I, a, agora, piv)
	if not A.alvoPermitido(L, a) then return nil end
	local atacou = L.atacadoPor and L.atacadoPor.alvo == a and agora < L.atacadoPor.ate
	-- ameaca PESSOAL (quem atacou o lobo): continua inimiga enquanto for vista e estiver no territorio (como "pessoal" no
	-- Cerebro dos dragoes); antes expirava 6 s apos o ultimo golpe e o lobo "esquecia" um rival a 4 studs (duelo 19/11)
	local pessoal = I.ameacas[a] and I.ameacas[a].pessoal
	if ehLoboSelvagem(a) and not L.dono and not atacou and not pessoal then return nil end
	if not A.visao(L, a) then return nil end
	local _, dPosto = A.pontoProximo(a, I.posto)
	if dPosto > G.coleira + G.raioAmeaca then return nil end          -- fora do territorio: nao vira ameaca (nem pisca no log)
	local c, dist = A.pontoProximo(a, piv)
	local aprox = dist > 0.1 and A.velAlvo(a):Dot(flat(piv - c).Unit) or 0
	if atacou then return 3, "atacou o lobo", c, dist, true end
	if pessoal then return 3, "rival em luta", c, dist, true end
	if dist <= G.raioAmeaca then return 2, string.format("perto %.1f", dist), c, dist end
	if dist <= G.raioAlerta and aprox >= G.aproximacao then return 2, string.format("aproximando %.1f studs/s a %.1f", aprox, dist), c, dist end
	if dist <= G.raioAlerta then return 1, string.format("observado a %.1f", dist), c, dist end
	return nil
end
local function atualizarAmeacas(L, I, agora, piv)
	-- atacante fora da percepcao (atras): vira ALERTA na posicao dele (investiga), nao ataque cego
	if L.atacadoPor and agora < L.atacadoPor.ate and L.atacadoPor.alvo and L.atacadoPor.alvo.Parent and not L.percebidos[L.atacadoPor.alvo] then
		local a = L.atacadoPor.alvo
		if A.alvoPermitido(L, a) then
			local c = A.centro(a)
			local e = I.ameacas[a] or {nivel = 0, inicio = agora}; I.ameacas[a] = e
			if c then e.ultimaPos = c end
			if e.nivel < 1 or agora - (e.t or 0) > 1 then e.nivel = math.max(e.nivel, 1); e.motivo = "atacou fora da visao"; e.t = agora end
		end
	end
	for a in pairs(L.percebidos) do
		local nivel, motivo, c, dist, pessoal = ameacaDe(L, I, a, agora, piv)
		if nivel then
			local e = I.ameacas[a]
			if not e then e = {nivel = 0, inicio = agora}; I.ameacas[a] = e end
			if pessoal then e.pessoal = true end
			if nivel > e.nivel then logIA(L, string.format("AMEACA %s nivel %d (%s)", a.Name, nivel, motivo)) end
			e.nivel = math.max(e.nivel, nivel); e.motivo = (nivel >= e.nivel) and motivo or e.motivo
			e.t = agora; e.ultimaPos = c; e.dist = dist
		end
	end
	-- esquecimento / invalidacao
	for a, e in pairs(I.ameacas) do
		local motivo = nil
		if not a.Parent or not A.alvoValido(a) then motivo = "morto/removido"
		else
			local pr = A.protegido(L, a); if pr then motivo = "protegido (" .. pr .. ")" end
			local _, dPosto = A.pontoProximo(a, I.posto)                 -- coleira medida ate a SUPERFICIE (alvo grande)
			if not motivo and dPosto > G.coleira + G.raioAmeaca then motivo = "saiu da coleira" end
			if not motivo and agora - (e.t or 0) > P.lembrarSeg then motivo = "sumiu (sem ver ha " .. P.lembrarSeg .. " s)" end
		end
		if motivo then
			I.ameacas[a] = nil
			logIA(L, string.format("esqueceu %s: %s", a.Name or "?", motivo))
			if motivo:find("sumiu") and e.ultimaPos and e.nivel >= 1 then I.investigar = {pos = e.ultimaPos, ate = agora + P.investigarJanela, nome = a.Name} end
			if I.alvo == a then I.alvo = nil; I.perdeuPor = motivo end
		end
	end
end
-- alvo = maior nivel; empate -> mais perto. Histerese: so troca com vantagem (nivel maior ou 6 studs mais perto).
local function escolherAlvo(L, I)
	local melhor, ms = nil, -math.huge
	for a, e in pairs(I.ameacas) do
		if e.nivel >= 2 then
			local s = e.nivel * 100 - (e.dist or 50)
			if a == I.alvo then s += 6 end
			if s > ms then melhor, ms = a, s end
		end
	end
	if melhor ~= I.alvo then
		logIA(L, melhor and string.format("alvo -> %s (%s)", melhor.Name, I.ameacas[melhor].motivo) or "sem alvo de combate")
		I.alvo = melhor; I.golpesTrocados = 0
	end
	return melhor
end

-- ------------------------------------------------------------------ ataque ANUNCIADO do alvo (para esquivar/recuar)
-- Fontes: (1) outro lobo do kit (estado do servidor); (2) atributo EmAtaque (convencao do combate dos dragoes; o kit do
-- Lobo tambem publica EmAtaque nos proprios golpes). So conta se o alvo estiver de frente para o lobo e perto.
local GOLPES = {Mordida = true, Garra = true, Investida = true, SaltoPredatorio = true}
local function ataqueAnunciado(L, a, dist)
	local x = A.lobos[a]
	local anun = nil
	if x then
		if GOLPES[x.estado] then anun = x.estado elseif x.basicoAte and os.clock() < x.basicoAte then anun = "golpe andando" end
	end
	local em = a:GetAttribute("EmAtaque"); if not anun and em and em ~= "" and em ~= false then anun = tostring(em) end
	if not anun then return nil end
	local cf = a:IsA("Model") and a:GetPivot(); if not cf then return nil end
	local paraMim = flat(L.modelo:GetPivot().Position - cf.Position)
	if paraMim.Magnitude < 0.1 then return anun end
	if flat(cf.LookVector).Unit:Dot(paraMim.Unit) < P.esquiva.frente then return nil end
	if dist > P.esquiva.dist then return nil end
	return anun
end

-- ------------------------------------------------------------------ LOCOMOCAO (Heartbeat; so vale com L.estado Livre)
-- I.mov = {marcha, ponto, parar, olhar?}. Anda sempre para a frente; giro limitado por marcha (P.giro, graus/s) em volta do
-- meio do corpo; Andar usa a mistura reta+curva aprovada (AndarCurvaE/D). Erro > P.virarParado com o lobo parado = VirarE/D.
-- Chao: raycast por quadro (altura do pivo mantida) com desnivel maximo por passo. Obstaculo: sondas a frente (+-35, +-70 graus).
-- capsula do corpo no plano: da anca (pivo - P.capsula.tras) ao focinho (pivo + P.capsula.frente), raio P.capsula.raio
local function segCorpo(cf) local f = flat(cf.LookVector).Unit; local o = flat(cf.Position); return o - f * P.capsula.tras, o + f * P.capsula.frente end
local function distPS(p, a, b) local ab = b - a; local t = math.clamp((p - a):Dot(ab) / math.max(ab:Dot(ab), 1e-6), 0, 1); return (p - (a + ab * t)).Magnitude end
folgaCapsulas = function(cfA, cfB)
	local a0, a1 = segCorpo(cfA); local b0, b1 = segCorpo(cfB); local m = math.huge
	for i = 0, 6 do local u = i / 6; m = math.min(m, distPS(a0:Lerp(a1, u), b0, b1), distPS(b0:Lerp(b1, u), a0, a1)) end
	return m - 2 * P.capsula.raio
end
local function bloqueado(L, pos, dir, alcance)
	local o = pos + Vector3.new(0, 3.2, 0)
	local hit = workspace:Raycast(o, dir * alcance, A.filtroMov(L, (L.ia and L.ia.alvo) and {L.ia.alvo} or nil))   -- o alvo nao e obstaculo
	if hit then return true, hit.Instance.Name end
	-- o proprio alvo tambem e obstaculo, mas so a curta distancia (sonda menor que distMin): o lobo encosta o focinho
	-- e nao atravessa o corpo ao contornar/flanquear
	local alvo = L.ia and L.ia.alvo
	-- 19/11: a sonda do corpo do alvo so vale indo NA DIRECAO dele (antes travava ate as saidas: impasse encostado)
	if alvo and alvo.Parent and dir:Dot(flat(alvo:GetPivot().Position - pos).Unit) > 0.2 then
		local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Include; p.FilterDescendantsInstances = {alvo}
		local h2 = workspace:Raycast(o, dir * math.min(alcance, P.sondaAlvo), p)
		if h2 then return true, "corpo do alvo" end
	end
	local p2 = pos + dir * math.min(alcance, 6)
	local y0 = A.chaoY(L, pos); local y1 = A.chaoY(L, p2)
	if not y1 then return true, "sem chao" end
	if y0 and ((y1 - y0) > P.degrauMax or (y0 - y1) > CFG.SaltoPredatorio.desnivelMax) then return true, string.format("desnivel %.1f", y1 - y0) end
	return false
end
local function direcaoLivre(L, I, pos, dir)
	local b, por = bloqueado(L, pos, dir, P.sonda)
	if not b then return dir, nil end
	local lado = I.ladoDesvio or 1
	for _, g in ipairs({35, -35, 70, -70, 105, -105}) do
		local d2 = girar(dir, math.rad(g * lado))
		if not bloqueado(L, pos, d2, P.sonda) then
			if g * lado < 0 then I.ladoDesvio = -lado end      -- mantem o lado que funcionou (nao oscila)
			return d2, por
		end
	end
	return nil, por
end
local function pararMov(L, I, base)
	if I.andando then I.andando = false end
	I.mov = nil
	A.pararCurvas(L, 0.3)
	L.C.base(base or "Repouso", 0.35)
end
M.pararMov = pararMov
local function passoMov(L, I, dt)
	local mov = I.mov
	if not mov or L.estado ~= "Livre" or L.virando or L.dashando then
		if I.andando and L.estado ~= "Livre" then I.andando = false end
		return
	end
	local piv = L.modelo:GetPivot(); local pos = piv.Position
	local d = flat(mov.ponto - pos); local dist = d.Magnitude
	if dist <= (mov.parar or 1.5) then
		if I.andando then I.andando = false; A.pararCurvas(L, 0.3); L.C.base(mov.base or "Repouso", 0.35) end
		mov.chegou = true
		return
	end
	mov.chegou = false
	local fr = flat(piv.LookVector).Unit
	local desejo = d.Unit
	-- separacao entre lobos com IA (nao se atravessam)
	local meu = pos + fr * 2.196                          -- meio do corpo (o pivo fica na traseira)
	for m, x in pairs(A.lobos) do
		if x ~= L and x.ia then
			local pm = m:GetPivot(); local o = flat(meu - (pm.Position + flat(pm.LookVector).Unit * 2.196))
			if o.Magnitude > 0.1 and o.Magnitude < P.separacao then desejo = (desejo + o.Unit * (P.separacao - o.Magnitude) / P.separacao * 1.2).Unit end
		end
	end
	local livre, por = direcaoLivre(L, I, pos, desejo)
	if not livre then
		I.travadoDesde = I.travadoDesde or os.clock()
		if not I.logTravado then I.logTravado = true; logIA(L, "caminho bloqueado (" .. tostring(por) .. ")") end
		if I.andando then I.andando = false; A.pararCurvas(L, 0.2); L.C.base("Repouso", 0.3) end
		return
	end
	I.travadoDesde = nil; I.logTravado = false
	local ang = angAssinado(fr, livre)
	local marcha = mov.marcha
	-- calmo/alerta: parado com o ponto atras = vira com o clipe (patas giram junto), nao gira deslizando.
	-- combate (mov.combate): vira EM MOVIMENTO (trote em arco fechado, passo reduzido), como o lobo real que gira sobre as patas
	if not mov.combate and not I.andando and math.abs(ang) > math.rad(P.virarParado) then
		A.virarNoLugar(L, ang > 0 and 1 or -1)
		return
	end
	-- curva fechada demais na corrida: cai para o trote (raio menor); no trote/andar segue com giro limitado
	if marcha == "Corrida" and math.abs(ang) > math.rad(60) then marcha = "Trote" end
	if mov.combate and marcha == "Andar" and math.abs(ang) > math.rad(45) then marcha = "Trote" end   -- Andar so gira 30 graus/s
	local vel = P.velocidades[marcha] * L.velMult
	-- chegada: nao passa do ponto (desacelera para a marcha de baixo quando perto)
	if marcha == "Corrida" and dist < P.corridaFreia then marcha = "Trote"; vel = P.velocidades.Trote * L.velMult end
	if marcha == "Trote" and dist < 3 and mov.parar < 3 then marcha = "Andar"; vel = P.velocidades.Andar * L.velMult end
	-- curva fechada = passo menor (como o Locomotor) e a passada do clipe desacelera junto (sem patinar)
	local fator = (marcha ~= "Andar") and math.clamp(1 - math.abs(ang) / math.rad(120), 0.45, 1) or 1
	L.C.base(marcha, 0.25, L.velMult * fator)
	I.andando = true; I.marcha = marcha
	local giroMax = math.rad(P.giro[marcha] or 60) * L.velMult
	local cf
	if marcha == "Andar" then
		local alvoPc = math.clamp(1.6 * ang / math.rad(30), -1, 1)
		L.pc = (L.pc or 0) + math.clamp(alvoPc - (L.pc or 0), -3 * dt, 3 * dt)
		A.misturarCurva(L, L.pc)
		cf = piv + fr * (vel * dt)
		cf = cf * O_CURVA * CFrame.Angles(0, L.pc * math.rad(30) * L.velMult * dt, 0) * O_CURVA:Inverse()
	else
		A.pararCurvas(L, 0.2)
		local passo = math.clamp(ang, -giroMax * dt, giroMax * dt)
		cf = piv * O_CURVA * CFrame.Angles(0, passo, 0) * O_CURVA:Inverse()
		cf = cf + flat(cf.LookVector).Unit * math.min(vel * fator * dt, dist)
	end
	-- chao: mantem a altura do pivo acima do chao (suave); nunca sobe/desce mais que degrauMax por passo
	local yc = A.chaoY(L, cf.Position)
	if yc and I.offPiv then
		local yAlvo = yc + I.offPiv
		-- 19/11: degrau maior que degrauMax NESTE passo = parede/borda: recusa o passo (antes a suavizacao por quadro
		-- deixava subir qualquer altura aos poucos - visto no ensaio 7, lobo em cima de parede de 20)
		-- subir: ate degrauMax; descer (pular de uma borda, ex.: depois de pousar do Salto num bloco): ate o desnivel do Salto
		local dy = yAlvo - piv.Position.Y
		if dy > P.degrauMax or -dy > CFG.SaltoPredatorio.desnivelMax then
			if not I.logDegrau then I.logDegrau = true; logIA(L, string.format("passo recusado: degrau %.1f", yAlvo - piv.Position.Y)) end
			if I.andando then I.andando = false; A.pararCurvas(L, 0.2); L.C.base("Repouso", 0.3) end
			return
		end
		I.logDegrau = nil
		local y = cf.Position.Y + math.clamp(yAlvo - cf.Position.Y, -CFG.SaltoPredatorio.desnivelMax, P.degrauMax) * math.min(1, dt * 10)
		cf = CFrame.lookAt(Vector3.new(cf.Position.X, y, cf.Position.Z), Vector3.new(cf.Position.X, y, cf.Position.Z) + flat(cf.LookVector))
	end
	-- 19/11 separacao DURA pela SILHUETA: cada lobo e uma capsula da anca ao focinho (P.capsula). Passo que deixa a folga
	-- entre as capsulas abaixo de P.folgaCorpo E menor que antes e cancelado: focinho, peito e patas nao entram no outro;
	-- passos que afastam (ou mantem) sempre podem. A medicao anterior (meio a meio) deixava o focinho atravessar.
	for m, x in pairs(A.lobos) do
		if x ~= L and m.Parent then
			local fAntes = folgaCapsulas(piv, m:GetPivot()); local fNovo = folgaCapsulas(cf, m:GetPivot())
			-- encostado, deslizar ao longo do rival (folga quase igual) e permitido; entrar nele (folga caindo) nao
			-- so cancela passo que PIORA a folga: dentro do limite, perder mais que folgaTol; abaixo do piso, qualquer piora
			-- r4: encostar (folga ate -folgaPiso, pelo de um no do outro) e permitido; abaixo disso, so passos que melhoram
			-- r6 (20/11): a capsula do CAIDO e a de um lobo em pe (pivo->focinho); o flanco real fica dentro dela. Abordando o
			-- flanco para finalizar, aceita sobrepor ate -1,2 dessa capsula (o encaixe real e medido pela boca no tronco)
			local abordando = I.plano == "Finalizar" and m:GetAttribute("Caido") and I.queda and I.queda.alvo == m
			local piso = abordando and -1.2 or (P.folgaCorpo - P.folgaPiso)
			if fNovo < piso and fNovo < fAntes then
				if not I.logCorpo then I.logCorpo = true; logIA(L, string.format("passo cancelado: silhueta entraria em %s (folga %.2f)", m.Name, fNovo)) end
				I.encostou = os.clock()                   -- a decisao abre espaco em vez de insistir
				-- saida do contato: o passo para a frente entraria no rival; vira NO LUGAR com o clipe (patas giram junto,
				-- sem patinar) para o lado que afasta o focinho do rival; depois o trote sai normalmente
				if not L.virando and not (L.basicoAte and os.clock() < L.basicoAte) and os.clock() - (I.ultimoVirarContato or 0) > P.virarContatoIntervalo then
					local rel = flat(m:GetPivot().Position - piv.Position)
					local lado = angAssinado(flat(piv.LookVector), rel) > 0 and -1 or 1      -- rival a esquerda -> vira a direita
					I.ultimoVirarContato = os.clock()
					logIA(L, "vira no lugar para sair do contato com " .. m.Name)
					A.virarNoLugar(L, lado)
				end
				return
			end
		end
	end
	I.logCorpo = nil
	L.modelo:PivotTo(cf)
end

local function irPara(L, I, ponto, marcha, parar, base, combate)
	local m = I.mov
	if m and m.marcha == marcha and m.parar == (parar or 1.5) and m.combate == combate then m.ponto = ponto; return end
	I.mov = {ponto = ponto, marcha = marcha, parar = parar or 1.5, base = base, combate = combate}
end
-- ponto limitado ao territorio (coleira + raioAmeaca em volta do posto): o lobo nunca sai dele
local function noTerritorio(I, p)
	local d = flat(p - I.posto); local lim = G.coleira + G.raioAmeaca - 2
	if d.Magnitude > lim then p = I.posto + d.Unit * lim end
	return Vector3.new(p.X, p.Y, p.Z)
end

-- ------------------------------------------------------------------ EXECUCAO de golpes (mesmo caminho do jogador)
local function corredorLivre(L, alvo, dist)
	local piv = L.modelo:GetPivot()
	local c = A.pontoProximo(alvo, piv.Position)
	local dir = flat(c - piv.Position); if dir.Magnitude < 0.5 then return false, "alvo colado" end
	local o = piv.Position + Vector3.new(0, 3.5, 0)
	local hit = workspace:Blockcast(CFrame.lookAt(o, o + dir.Unit), Vector3.new(CFG.Investida.largura, 4, 1), dir.Unit * (dist + 1), A.filtroMov(L, {alvo}))
	if hit then return false, "corredor bloqueado por " .. hit.Instance.Name end
	-- chao ao longo do corredor (sem buraco/degrau grande)
	local y0 = A.chaoY(L, piv.Position)
	for k = 3, math.floor(dist), 3 do
		local y = A.chaoY(L, piv.Position + dir.Unit * k)
		if not y or (y0 and math.abs(y - y0) > P.degrauMax) then return false, "corredor sem chao firme" end
	end
	return true
end
local function golpe(L, I, nome, dados, motivo)
	local ok, por = A.acao(L, nome, dados, motivo .. " | " .. status(L))
	I.ultimoGolpe = {nome = nome, t = os.clock(), ok = ok}
	table.insert(I.historico, 1, nome); if #I.historico > 4 then table.remove(I.historico) end
	-- "golpes trocados" (gatilho do flanco) = so golpes contra o alvo; Uivo e salto de esquiva (sem alvo) nao contam
	if ok then
		if nome ~= "UivoAncestral" and typeof(dados) ~= "Vector3" then I.golpesTrocados += 1 end
		I.seqBasicos = (nome == "Mordida" or nome == "Garra") and (I.seqBasicos or 0) + 1 or 0
		if nome == "Mordida" or nome == "Garra" then I.golpesEntrada = (I.golpesEntrada or 0) + 1 end
		I.contagem[nome] = (I.contagem[nome] or 0) + 1
		if nome == "UivoAncestral" then I.uivouAlvo = I.alvo end
		if nome == "Investida" then I.posHab = "investida" end
	else I.bloqueios[nome] = os.clock() + P.reTentar end
	return ok, por
end
-- candidatos por condicoes reais; devolve o melhor e a lista de descartes (motivo)
local function escolherGolpe(L, I, a, c, dist, angAlvo)
	local agora = os.clock()
	local E = L.energia
	local reserva = (L.vida / CFG.Vida < P.recuo.vida) and P.reservaEnergia or 0
	local cand, desc = {}, {}
	local function livre(n) local r = L.recargas[n]; if r and agora < r then return false, string.format("recarga %.1f", r - agora) end
		if I.bloqueios[n] and agora < I.bloqueios[n] then return false, "recusado ha pouco" end; return true end
	local function rep(n) return (I.historico[1] == n and P.repeticao or 0) + (I.historico[2] == n and P.repeticao / 2 or 0) end
	local function add(n, peso, dados, por)
		local j = math.random() * P.variacao
		table.insert(cand, {n = n, s = peso - rep(n) + j, dados = dados, por = string.format("%s (peso %.0f, rep -%.0f, var +%.1f)", por, peso, rep(n), j)})
	end
	local visto = A.linhaDeVisao(L, a)
	-- Mordida / Garra (andando quando em movimento: r7)
	local exigeAndar = (I.plano == "Pressionar" or I.plano == "Flanquear" or I.plano == "Perseguir") and not I.andando
	for _, n in ipairs({"Mordida", "Garra"}) do
		local b = CFG.Basico[n]; local ok, r = livre(n)
		if exigeAndar then desc[n] = "parado: golpe basico so andando na pressao"
		elseif dist > b.alcance + (I.andando and P.pressao.antecipa or 0) then desc[n] = string.format("alcance %.1f > %.1f", dist, b.alcance)
		elseif math.deg(math.abs(angAlvo)) > b.cone / 2 then desc[n] = string.format("fora do cone %.0f", math.deg(math.abs(angAlvo)))
		elseif A.contato and (function()
			-- r3 (20/11, hitbox de contato): so ataca se a BOCA/PATA vai tocar o corpo (bote do clipe + o que anda ate o contato)
			local HBc = CFG.Hitbox
			local pts = (n == "Garra") and A.patas(L) or {A.boca(L)}
			local dc = A.contato(a, pts)
			-- so o avanco EM DIRECAO ao alvo conta (arco lateral nao aproxima), menos o quanto o alvo se afasta
			local vel = I.andando and ((P.velocidades[I.marcha] or 0) * L.velMult) or 0
			local paraAlvo = flat(c - L.modelo:GetPivot().Position); paraAlvo = paraAlvo.Magnitude > 0.1 and paraAlvo.Unit or flat(L.modelo:GetPivot().LookVector).Unit
			local fecha = vel * math.max(0, math.cos(angAlvo)) - A.velAlvo(a):Dot(paraAlvo)
			local lim = ((n == "Garra") and HBc.preverGarra or HBc.preverMordida) + math.max(0, fecha) * HBc.tContato
			I.ultimoDc = dc
			if dc > lim then desc[n] = string.format("%s a %.1f do corpo > %.1f", n == "Garra" and "pata" or "focinho", dc, lim); return true end
			return false
		end)() then
		elseif not visto then desc[n] = "sem linha de visao"
		elseif not ok then desc[n] = r
		else add(n, n == "Mordida" and 60 or 52, nil, string.format("%s a %.1f (boca/pata a %.1f do corpo)", n == "Mordida" and "mordida" or "garra", dist, I.ultimoDc or -1)) end
	end
	-- Investida: distancia que o clipe cobre (~12,4 + mordida 1,5), de frente e com corredor livre
	do local IV = CFG.Investida; local ok, r = livre("Investida")
		if dist < P.investida.min or dist > P.investida.max then desc.Investida = string.format("distancia %.1f fora de %d-%d", dist, P.investida.min, P.investida.max)
		elseif math.deg(math.abs(angAlvo)) > P.investida.cone then desc.Investida = string.format("desalinhado %.0f", math.deg(math.abs(angAlvo)))
		elseif not ok then desc.Investida = r
		elseif E < IV.energia + reserva then desc.Investida = string.format("energia %.0f < %.0f", E, IV.energia + reserva)
		else
			local cl, por = corredorLivre(L, a, dist)
			if not cl then desc.Investida = por else add("Investida", 56, flat(c - L.modelo:GetPivot().Position), string.format("investida a %.1f, corredor livre", dist)) end
		end
	end
	-- Salto Predatorio: fecha distancia (o kit valida o chao firme do pouso; recusa vira bloqueio temporario)
	do local SP = CFG.SaltoPredatorio; local ok, r = livre("SaltoPredatorio")
		if dist < G.saltoDesde or dist > SP.alcanceMax then desc.SaltoPredatorio = string.format("distancia %.1f fora de %d-%d", dist, G.saltoDesde, SP.alcanceMax)
		elseif math.deg(math.abs(angAlvo)) > P.salto.cone then desc.SaltoPredatorio = string.format("desalinhado %.0f", math.deg(math.abs(angAlvo)))
		elseif not visto then desc.SaltoPredatorio = "sem linha de visao"
		elseif not ok then desc.SaltoPredatorio = r
		elseif E < SP.energia + reserva then desc.SaltoPredatorio = string.format("energia %.0f < %.0f", E, SP.energia + reserva)
		else
			local foge = A.velAlvo(a):Dot(flat(c - L.modelo:GetPivot().Position).Unit) > 2
			add("SaltoPredatorio", 48 + (foge and 18 or 0), a, string.format("salto a %.1f%s", dist, foge and ", alvo fugindo" or ""))
		end
	end
	-- Uivo: so quando o bonus serve (perseguir quem foge / esquiva com vida em queda), com energia sobrando para um golpe
	do local UV = CFG.UivoAncestral; local ok, r = livre("UivoAncestral")
		local vRel = A.velAlvo(a):Dot(flat(c - L.modelo:GetPivot().Position).Unit)    -- > 0: o alvo se afasta; < 0: avanca
		local foge = vRel > 2 and dist >= P.uivo.fugaDist
		local util = foge and "alvo fugindo (+velocidade)" or (L.vida / CFG.Vida < P.uivo.vida and "vida em queda (+esquiva)") or (dist >= P.uivo.distMin and I.golpesTrocados == 0 and "inicio do combate a distancia") or nil
		if L.mods.UivoAncestral then desc.UivoAncestral = "bonus ja ativo"
		elseif I.uivouAlvo == a then desc.UivoAncestral = "ja uivou para este alvo (um uivo parado por combate)"
		elseif not util then desc.UivoAncestral = "bonus sem utilidade agora"
		elseif dist < P.uivo.distSegura then desc.UivoAncestral = string.format("alvo perto demais (%.1f) para parar e uivar", dist)
		elseif vRel < -P.uivo.avancoMax then desc.UivoAncestral = string.format("alvo avancando %.1f studs/s: uivar parado seria pego", -vRel)
		elseif not ok then desc.UivoAncestral = r
		elseif E < UV.energia + P.uivo.sobra then desc.UivoAncestral = string.format("energia %.0f < %.0f", E, UV.energia + P.uivo.sobra)
		else add("UivoAncestral", 44, nil, util) end
	end
	table.sort(cand, function(x, y) return x.s > y.s end)
	return cand[1], desc
end

-- ------------------------------------------------------------------ PLANOS
-- Calmo, Alerta, Investigar, Perseguir, Pressionar, Flanquear, Esquivar, Recuar, Recuperar, Desistir (= retorno ao posto).
local function mudarPlano(L, I, plano, motivo, agora)
	if I.plano == plano then return end
	logIA(L, string.format("plano %s -> %s (%s) | %s", I.plano or "-", plano, motivo, status(L)))
	I.plano = plano; I.planoDesde = agora; I.planoMotivo = motivo
	I.contPlanos[plano] = (I.contPlanos[plano] or 0) + 1
	I.flanco = nil; I.repos = nil; I.fase = nil; I.abrir = nil; I.golpesEntrada = 0
	L.modelo:SetAttribute("PlanoIA", plano)
end
local URGENTES = {Esquivar = true, Desistir = true, Recuar = true}
local function podeTrocar(I, novo, agora)
	if URGENTES[novo] then return true end
	return agora - (I.planoDesde or 0) >= P.planoMin
end


-- ------------------------------------------------------------------ 19/11 alvo CAIDO: FINALIZAR ou POUPAR (uma decisao por queda)
-- Pesa: ameaca restante (vida x forca do alvo), outros inimigos, propria vida/energia, distancia, linha de visao, coleira,
-- protecao e tempo ate o alvo levantar. Lobo do dono nunca finaliza sozinho. Atributo DecisaoQueda = "finalizar"/"poupar"
-- forca a escolha nos testes (as condicoes duras continuam valendo dentro de A.finalizar).
local function decidirQueda(L, I, a, agora, piv, c, dist, angAlvo)
	local F = CFG.Controle.finalizar
	local caiAte = a:GetAttribute("CaidoAte") or 0
	local resta = caiAte - workspace:GetServerTimeNow()
	local Q = I.queda
	if not Q or Q.alvo ~= a then          -- r3: uma decisao por queda ate o alvo levantar (prolongar a queda nao gera outra)
		local por, fin = {}, true
		local forc = L.modelo:GetAttribute("DecisaoQueda")
		local vidaF = L.vida / CFG.Vida
		local outros = 0
		for b, e in pairs(I.ameacas) do if b ~= a and e.nivel >= 2 and (e.dist or 99) <= F.ameacaRaio then outros += 1 end end
		local pa, pb = A.classePorte(L.modelo), A.classePorte(a)
		local ameaca = ((a:GetAttribute("Vida") or 0) / math.max(a:GetAttribute("VidaMax") or CFG.Vida, 1)) * (pb.forca / math.max(pa.forca, 1))
		local tempoNec = math.max(0, dist - (F.alcance - 1)) / P.velocidades.Trote + F.anuncio + 0.5 + F.folgaTempo
		local e = I.ameacas[a]
		local function nao(m) fin = false; table.insert(por, m) end
		if L.dono then nao("lobo do dono: sem finalizacao automatica") end
		if not (e and e.pessoal) then nao("alvo nao lutou com o lobo: so afasta") end
		if outros > 0 then nao(outros .. " outro(s) inimigo(s) a menos de " .. F.ameacaRaio) end
		if vidaF < F.vidaMin then nao(string.format("propria vida %.0f%%", vidaF * 100)) end
		if L.energia < F.energiaMin then nao(string.format("energia %.0f", L.energia)) end
		local planoAlvo = a:GetAttribute("PlanoIA")
		if (planoAlvo == "Desistir" or planoAlvo == "Recuar") then nao("alvo ja estava fugindo (" .. planoAlvo .. "): deixa ir") end
		if dist > F.abordarAte then nao(string.format("longe %.1f", dist)) end
		if resta < tempoNec then nao(string.format("levanta em %.1f s (precisa %.1f)", resta, tempoNec)) end
		if not A.linhaDeVisao(L, a) then nao("sem linha de visao") end
		local pr = A.protegido(L, a); if pr then nao("protegido (" .. pr .. ")") end
		local _, dPosto = A.pontoProximo(a, I.posto); if dPosto > G.coleira + G.raioAmeaca then nao("fora da coleira") end
		local motivo
		if forc == "poupar" then fin = false; motivo = "forcado pelo teste: poupar"
		elseif forc == "finalizar" and not L.dono then fin = true; motivo = "forcado pelo teste: finalizar" .. (#por > 0 and (" (ignorando: " .. table.concat(por, "; ") .. ")") or "")
		else motivo = fin and string.format("ameaca restante %.2f, sozinho, vida %.0f%%, levanta em %.1f s", ameaca, vidaF * 100, resta) or table.concat(por, "; ") end
		Q = {alvo = a, caiAte = caiAte, fin = fin, motivo = motivo, t = agora}; I.queda = Q
		I.contDecisao = I.contDecisao or {finalizar = 0, poupar = 0}
		I.contDecisao[fin and "finalizar" or "poupar"] += 1
		logIA(L, string.format("QUEDA de %s (%s x %s) -> %s: %s | %s", a.Name, pa.nome, pb.nome, fin and "FINALIZAR" or "POUPAR", motivo, status(L)))
		mudarPlano(L, I, fin and "Finalizar" or "Vigiar", motivo, agora)
		if not fin and L.estado == "Livre" then pararMov(L, I, "Repouso"); L.C.acao("Rosnar", 0.15) end
	end
	if I.plano ~= "Finalizar" and I.plano ~= "Vigiar" then mudarPlano(L, I, Q.fin and "Finalizar" or "Vigiar", Q.motivo, agora) end
	if L.estado ~= "Livre" then return end
	if Q.fin and not Q.tentou then
		local tempoNec = math.max(0, dist - (F.alcance - 1)) / P.velocidades.Trote + F.anuncio + 0.5
		if resta < tempoNec then
			Q.fin = false; logIA(L, string.format("finalizacao abandonada: %s levanta em %.1f s (precisa %.1f; dist %.1f, angulo %.0f)", a.Name, resta, tempoNec, dist, math.deg(angAlvo)))
			mudarPlano(L, I, "Vigiar", "nao chega antes de levantar", agora); return
		end
		-- r4 (20/11, correcao do usuario): finalizacao no FLANCO/barriga. Ponto = meio do tronco (Pelve-Peito); lado = o da barriga
		-- (onde estao as patas) se estiver livre, senao o outro; nenhum livre = cancela com motivo. Contorna o corpo em arco
		-- (cabeca ou cauda) quando esta do outro lado; nunca passa por cima do caido.
		local Est = CFG.Controle.estilo
		if not Q.flanco then
			local pe, pv = a:FindFirstChild("Peito", true), a:FindFirstChild("Pelve", true)
			if not (pe and pv and pe:IsA("Bone") and pv:IsA("Bone")) then
				Q.fin = false; logIA(L, "finalizacao cancelada: alvo sem ossos de tronco (flanco desconhecido)"); mudarPlano(L, I, "Vigiar", "sem flanco", agora); return
			end
			local P1, P2 = pe.TransformedWorldCFrame.Position, pv.TransformedWorldCFrame.Position
			local meio = (P1 + P2) / 2; local eixo = flat(P1 - P2); local meia = eixo.Magnitude / 2; eixo = eixo.Unit
			local nrm = Vector3.new(-eixo.Z, 0, eixo.X)
			local patas = Vector3.zero; local np = 0
			for _, nm in ipairs({"MaoE", "MaoD", "PeE", "PeD"}) do local o = a:FindFirstChild(nm, true); if o and o:IsA("Bone") then patas += o.TransformedWorldCFrame.Position; np += 1 end end
			local ladoP = np > 0 and flat(patas / np - meio):Dot(nrm) or 0
			local ladoBarriga = (ladoP < 0) and -1 or 1
			-- r6: deitado sobre o peito (patas sob o corpo) os dois flancos valem: fica do lado em que o lobo ja esta
			if math.abs(ladoP) < 0.4 and not a:GetAttribute("CaidoLado") then ladoBarriga = (flat(piv.Position - meio):Dot(nrm) >= 0) and 1 or -1 end
			-- pontas reais do corpo (cabeca / cauda) para contornar sem encostar
			local extF, extT = meia, -meia
			for _, nm in ipairs({"Cabeca", "Mandibula", "Pescoco2"}) do local o = a:FindFirstChild(nm, true); if o and o:IsA("Bone") then extF = math.max(extF, flat(o.TransformedWorldCFrame.Position - meio):Dot(eixo)) end end
			for _, nm in ipairs({"Cauda1", "Cauda3", "PeE", "PeD"}) do local o = a:FindFirstChild(nm, true); if o and o:IsA("Bone") then extT = math.min(extT, flat(o.TransformedWorldCFrame.Position - meio):Dot(eixo)) end end
			local escolha, porque = nil, {}
			-- r3 20/11: alvo deitado DE LADO (CaidoLado): a barriga real fica a (ladoDesloc+ladoRaio) x comprimento do tronco da
			-- coluna, do lado das patas; as costas nao servem para a mordida na barriga (o lado oposto vira "costas" e e recusado)
			local deLado = a:GetAttribute("CaidoLado") ~= nil
			local lenT = (P1 - P2).Magnitude
			for _, s in ipairs({ladoBarriga, -ladoBarriga}) do
				local n = nrm * s
				local sup = meio + n * Est.raioTronco * ((a.GetScale and a:GetScale()) or 1)   -- r9: raio na escala do alvo
				local frente = Est.frenteBoca
				if deLado then sup = meio + n * (Est.ladoDesloc + Est.ladoRaio) * lenT; frente = Est.frenteBocaLado end
				local spot = Vector3.new(sup.X, piv.Position.Y, sup.Z) + n * (frente - 0.1)
				local motivo = nil
				if deLado and s ~= ladoBarriga then motivo = "costas (deitado de lado: a barriga fica do outro lado)" end
				local y = not motivo and A.chaoY(L, spot); if motivo then elseif not y or math.abs(y - (I.offPiv and (piv.Position.Y - I.offPiv) or y)) > 2.5 then motivo = "sem chao" end
				if not motivo then
					local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {L.modelo, a}
					local o0 = Vector3.new(sup.X, piv.Position.Y + 3, sup.Z)
					if workspace:Raycast(o0, (spot + Vector3.new(0, 3, 0)) - o0, rp) then motivo = "parede/obstaculo" end
				end
				if not motivo and not noTerritorio(I, spot):FuzzyEq(spot, 0.5) then motivo = "fora do territorio" end
				if not motivo then escolha = {n = n, spot = spot, meio = meio, eixo = eixo, meia = meia, extF = extF, extT = extT, barriga = (s == ladoBarriga), ambiguo = math.abs(ladoP) < 0.4 and not deLado, deLado = deLado,
					raioSup = deLado and (Est.ladoDesloc + Est.ladoRaio) * lenT or Est.raioTronco * ((a.GetScale and a:GetScale()) or 1), frente = frente}; break end
				table.insert(porque, (s == ladoBarriga and "lado da barriga: " or "outro lado: ") .. motivo)
			end
			if not escolha then
				Q.fin = false; logIA(L, "finalizacao cancelada: nenhum flanco livre (" .. table.concat(porque, "; ") .. ")")
				mudarPlano(L, I, "Vigiar", "sem flanco livre", agora); return
			end
			Q.flanco = escolha
			logIA(L, string.format("finalizacao: flanco %s de %s%s", escolha.ambiguo and "(deitado sobre o peito: lado onde o lobo esta)" or (escolha.barriga and "da barriga" or "oposto"), a.Name, #porque > 0 and (" (" .. porque[1] .. ")") or ""))
		end
		local Fl = Q.flanco
		local pp = piv.Position
		local dSpot = flat(Fl.spot - pp).Magnitude
		-- do outro lado do corpo: contorna pela ponta mais perto (cabeca ou cauda) antes de ir ao flanco
		local ladoAtual = flat(pp - Fl.meio):Dot(Fl.n)
		local alvoMov = Fl.spot
		if ladoAtual < (Fl.raioSup or Est.raioTronco * ((a.GetScale and a:GetScale()) or 1)) then
			local ponta = (flat(pp - Fl.meio):Dot(Fl.eixo) >= 0) and 1 or -1
			local alem = (ponta > 0) and (Fl.extF + Est.arcoFolga) or (Fl.extT - Est.arcoFolga)   -- r6: alem da cabeca/cauda reais
			alvoMov = Fl.meio + Fl.eixo * alem + Fl.n * ((Fl.raioSup or Est.raioTronco) + (Fl.frente or Est.frenteBoca))
			alvoMov = Vector3.new(alvoMov.X, pp.Y, alvoMov.Z)
		end
		local faceAlvo = -Fl.n
		local angF = math.deg(math.abs(angAssinado(flat(piv.LookVector), faceAlvo)))
		if alvoMov == Fl.spot and dSpot <= Est.ajusteMax and angF <= Est.giroMax and dist <= F.alcance + 1 and not L.virando then
			pararMov(L, I, "Repouso"); Q.tentou = true
			local enc = CFrame.lookAt(Vector3.new(Fl.spot.X, pp.Y, Fl.spot.Z), Vector3.new(Fl.spot.X, pp.Y, Fl.spot.Z) + faceAlvo)
			local ok, motivo = A.finalizar(L, a, Q.motivo, enc)
			if not ok then Q.fin = false; logIA(L, "finalizacao recusada: " .. tostring(motivo)); mudarPlano(L, I, "Vigiar", "recusada: " .. tostring(motivo), agora) end
		elseif alvoMov ~= Fl.spot then                                      -- contornando a cabeca/cauda
			Q.fase = "pre"
			irPara(L, I, noTerritorio(I, alvoMov), "Trote", 1.0, nil, true)       -- r6: contorna trotando (andando nao dava tempo)
		elseif alvoMov == Fl.spot and dSpot <= Est.ajusteMax and angF > Est.giroMax and not L.virando and resta > 2.6 + 1.5 then
			-- r9: no ponto mas de costas (> giroMax): para e vira no lugar com o clipe (com passos), para o lado do corpo
			pararMov(L, I, "Repouso")
			A.virarNoLugar(L, angAssinado(flat(piv.LookVector), faceAlvo) > 0 and 1 or -1)
			logIA(L, string.format("finalizacao: vira no lugar para o flanco (%.0f graus)", angF))
		elseif not L.virando then
			-- r8: vai DIRETO ao ponto do flanco (trota longe, anda perto); o encaixe do rosnado corrige ate 1,5 studs / 135 graus
			irPara(L, I, noTerritorio(I, Fl.spot), dSpot > 2.5 and "Trote" or "Andar", 0.25, nil, true)
		end
		return
	end
	-- POUPAR / VIGIAR: nao morde quem esta no chao; fica a distancia, de frente, e retoma a luta quando ele levantar
	if dist < F.vigiarDist - 1.5 then
		local fora = flat(piv.Position - c); fora = fora.Magnitude > 0.1 and fora.Unit or -flat(piv.LookVector).Unit
		irPara(L, I, noTerritorio(I, c + fora * F.vigiarDist), "Andar", 0.8, nil, true)
	elseif I.mov then pararMov(L, I, "Repouso") end
end
local function decidirCombate(L, I, a, agora, piv)
	local c, dist = A.pontoProximo(a, piv.Position)
	local fr = flat(piv.LookVector)
	local angAlvo = angAssinado(fr, flat(c - piv.Position))
	if a:GetAttribute("Caido") and (a:GetAttribute("CaidoAte") or 0) > workspace:GetServerTimeNow() then
		-- so decide finalizar/poupar com o alvo ENFRAQUECIDO; forte, a queda so abre vantagem (golpes normais, sem golpe final)
		local vA = (a:GetAttribute("Vida") or 0) / math.max(a:GetAttribute("VidaMax") or CFG.Vida, 1)
		local caiAte = a:GetAttribute("CaidoAte")
		if vA <= CFG.Controle.finalizar.vidaAlvoMax or L.modelo:GetAttribute("DecisaoQueda") or (I.queda and I.queda.alvo == a) then
			return decidirQueda(L, I, a, agora, piv, c, dist, angAlvo)
		elseif I.quedaAprov ~= caiAte then
			I.quedaAprov = caiAte; I.contDecisao = I.contDecisao or {finalizar = 0, poupar = 0}
			I.contDecisao.aproveitar = (I.contDecisao.aproveitar or 0) + 1
			logIA(L, string.format("QUEDA de %s -> APROVEITA: alvo ainda forte (vida %.0f%% > %.0f%%), golpes normais sem finalizar", a.Name, vA * 100, CFG.Controle.finalizar.vidaAlvoMax * 100))
		end
	elseif I.queda and I.queda.alvo == a then
		logIA(L, string.format("%s levantou: retoma a luta (%s)", a.Name, I.queda.fin and "finalizacao nao concluida" or "poupado")); I.queda = nil
	end
	local vidaF = L.vida / CFG.Vida
	local anun = ataqueAnunciado(L, a, dist)
	if I.vidaAnt and L.vida < I.vidaAnt then I.golpesTrocados += 1 end      -- golpe recebido tambem conta como troca
	I.vidaAnt = L.vida
	-- 1) escolha do PLANO (sobreposicoes duras primeiro, como no duelo tatico)
	local novo, motivo
	if vidaF <= P.desistirVida then novo, motivo = "Desistir", string.format("vida critica %.0f%%", vidaF * 100)
	elseif anun and (not I.esquivouAte or agora > I.esquivouAte) then novo, motivo = "Esquivar", "ataque anunciado: " .. anun
	elseif I.plano == "Esquivar" and agora - I.planoDesde < P.esquiva.duracao then novo = "Esquivar"
	elseif I.plano == "Recuperar" and (L.energia < P.recuo.recuperarAte or agora - I.planoDesde < P.recuo.minSeg) and dist > P.recuo.defenderDentro then novo = "Recuperar"
	elseif I.plano == "Recuar" and dist < P.recuo.dist and agora - I.planoDesde < P.recuo.maxSeg then novo = "Recuar"
	elseif I.plano == "Recuar" then novo, motivo = "Recuperar", string.format("abriu distancia %.1f em %.1f s; recupera folego", dist, agora - I.planoDesde); I.recuoPendente = nil
	elseif vidaF < P.recuo.vida and (not I.recuouVida or I.recuoPendente) then   -- recuo interrompido por esquiva continua pendente
		novo, motivo = "Recuar", string.format("vida baixa %.0f%%%s", vidaF * 100, I.recuoPendente and " (retoma o recuo)" or ""); I.recuouVida = true; I.recuoPendente = true
	elseif L.energia < P.recuo.energia then novo, motivo = "Recuar", string.format("energia baixa %.0f", L.energia)
	elseif dist > P.perseguirDesde then novo, motivo = "Perseguir", string.format("alvo a %.1f", dist)
	elseif I.plano == "Flanquear" and I.flanco and agora < I.flanco.ate then novo = "Flanquear"
	else
		-- flanquear quando o alvo encara o lobo e ja houve troca de golpes (o espaco do lado e checado ao iniciar)
		local cf = a:GetPivot(); local encarado = flat(cf.LookVector).Unit:Dot(flat(piv.Position - cf.Position).Unit) > math.cos(math.rad(P.flanco.encarado))
		if encarado and I.golpesTrocados >= P.flanco.aposGolpes and dist < P.pressaoAte and (agora - (I.ultimoFlanco or 0)) > P.flanco.intervalo then
			novo, motivo = "Flanquear", string.format("encarado apos %d golpes", I.golpesTrocados)
		else novo, motivo = "Pressionar", string.format("alvo a %.1f", dist) end
	end
	if novo ~= I.plano then
		if podeTrocar(I, novo, agora) or I.plano == "Recuperar" or I.plano == "Esquivar" or I.plano == "Recuar" or I.plano == "Vigiar" or I.plano == "Finalizar" then mudarPlano(L, I, novo, motivo or "continua", agora)
		else novo = I.plano end
	end
	-- 2) LOCOMOCAO do plano (combate: gira em movimento, nunca parado deslizando)
	local alvoCf = a:GetPivot()
	local vA = A.velAlvo(a)
	local plano = I.plano
	if plano == "Perseguir" then
		local t = math.min(dist / P.velocidades.Corrida, P.previsaoMax)       -- breve previsao do alvo
		local pred = c + vA * t
		irPara(L, I, noTerritorio(I, pred), dist > P.corridaDesde and "Corrida" or "Trote", P.distMin, nil, true)
	elseif plano == "Pressionar" then
		-- 19/11 (duelo "parado"): pressao em CICLOS de entrar e abrir, sem estacionar na faixa de alcance.
		--   ENTRAR: arco curto ate a distancia de contato, de um lado (P.pressao.arco), mordendo/arranhando ANDANDO (r7).
		--   ABRIR: depois de N golpes, ou colado sem golpe pronto, ou desalinhado, sai trotando em arco para o lado
		--   (P.pressao.abrirAng/abrirRaio) e reentra por outro angulo. Troca de lado quando o alvo encara o lado atual,
		--   quando o lado esta bloqueado ou a cada entrada alternada. O destino acompanha o alvo a cada decisao.
		local PP = P.pressao
		local ctr = alvoCf.Position
		local radial = flat(piv.Position - ctr); if radial.Magnitude < 0.1 then radial = -fr end; radial = radial.Unit
		local rSup = math.max(0.5, (flat(c - ctr)).Magnitude)          -- raio da superficie do alvo do lado do lobo
		I.fase = I.fase or "entrar"
		-- reentra so com espaco (>= reentrarMin) ou quando o tempo de abrir estoura de vez (evita abrir/reentrar colado)
		if I.fase == "abrir" and I.abrir and ((agora > I.abrir.ate or (I.mov and I.mov.chegou)) and dist >= PP.reentrarMin or agora > I.abrir.ate + 1.0) then
			I.fase = "entrar"; I.abrir = nil; I.golpesEntrada = 0
			logIA(L, string.format("reentra pela %s (alvo a %.1f)", (I.ladoFlanco or 1) > 0 and "esquerda" or "direita", dist))
		end
		if I.fase == "entrar" then
			local deFrente = math.deg(math.abs(angAlvo)) <= CFG.Basico.Mordida.cone / 2
			local ultimoT = I.ultimoGolpe and I.ultimoGolpe.t or 0
			local colado = dist <= P.distMin + 0.3
			local motivo = nil
			-- r7: golpe basico em curso (ate o contato) NAO e interrompido por abrir/virar: antes o lobo virava antes do dente chegar
			local golpeEmCurso = (L.basicoAte and agora < L.basicoAte) or (agora - ultimoT < PP.esperaContato)
			if I.posHab and L.estado == "Livre" then motivo = "saida apos " .. I.posHab; I.posHab = nil
			elseif I.encostou and agora - I.encostou < 0.4 and not golpeEmCurso then motivo = "silhueta encostada no rival"; I.encostou = nil
			elseif (I.golpesEntrada or 0) >= I.estilo.golpesPorEntrada and agora - ultimoT > PP.esperaContato then motivo = string.format("%d golpes na entrada", I.golpesEntrada)
			elseif colado and not deFrente and not golpeEmCurso then motivo = string.format("colado e desalinhado %.0f graus", math.deg(math.abs(angAlvo)))
			elseif colado and agora - ultimoT > PP.coladoMax and not (L.basicoAte and agora < L.basicoAte) then motivo = "colado sem golpe pronto" end
			if motivo then
				-- lado de saida: se o alvo encara o lado atual ou se o lado esta bloqueado, troca
				local lado = I.ladoFlanco or 1
				if flat(alvoCf.LookVector).Unit:Dot(radial) > 0.6 then lado = -lado end
				local p2 = ctr + girar(radial, math.rad(I.estilo.abrirAng * lado)) * (rSup + I.estilo.abrirRaio)
				local dp = flat(p2 - piv.Position)
				if dp.Magnitude > 0.5 and bloqueado(L, piv.Position, dp.Unit, math.min(P.sonda, dp.Magnitude)) then
					lado = -lado; p2 = ctr + girar(radial, math.rad(I.estilo.abrirAng * lado)) * (rSup + I.estilo.abrirRaio)
				end
				I.ladoFlanco = lado; I.fase = "abrir"
				I.abrir = {ate = agora + PP.abrirSeg, p = noTerritorio(I, p2)}
				logIA(L, string.format("abre espaco pela %s (%s)", lado > 0 and "esquerda" or "direita", motivo))
			else
				local lado = I.ladoFlanco or 1
				local pEnt
				if dist > PP.retaAte then
					pEnt = ctr + girar(radial, math.rad(I.estilo.arco * lado)) * (rSup + P.distMin) + vA * 0.4   -- longe: arco curto de um lado
				else
					-- reta final: chega de frente para o ALVO mas pelo lado dele (P.pressao.retaLado graus fora do focinho do
					-- rival), evitando o focinho-com-focinho que travava os dois e pedia giro no lugar
					local lr = I.ladoFlanco or 1
					if PP.retaLado > 0 and flat(alvoCf.LookVector).Unit:Dot(radial) > 0.5 then   -- r5: desligado (retaLado 0) - piorou a precisao
						pEnt = ctr + girar(radial, math.rad(PP.retaLado * lr)) * (rSup + P.distMin + 0.4) + vA * 0.4
					else
						pEnt = c + radial * (P.distMin + 0.4) + vA * 0.4                                    -- ja de lado/atras: reto
					end
				end
				irPara(L, I, noTerritorio(I, pEnt), dist > PP.andarAte and "Trote" or "Andar", 0.6, nil, true)
			end
		end
		if I.fase == "abrir" and I.abrir then
			-- o ponto de saida acompanha o alvo (mesmo angulo relativo)
			irPara(L, I, I.abrir.p + vA * 0.3, "Trote", 1.5, nil, true)
		end
	elseif plano == "Flanquear" and I.encostou and agora - I.encostou < 0.4 then
		mudarPlano(L, I, "Pressionar", "silhueta encostada no flanco: abre espaco", agora)
	elseif plano == "Flanquear" then
		if not I.flanco then
			local raio = flat(piv.Position - alvoCf.Position); local r = math.max(raio.Magnitude, dist + 4)
			local lado
			for _, s in ipairs({I.ladoFlanco or 1, -(I.ladoFlanco or 1)}) do
				local p2 = alvoCf.Position + girar(raio.Unit, math.rad(P.flanco.angulo * s)) * r
				local dp = flat(p2 - piv.Position)
				if dp.Magnitude > 0.5 and not bloqueado(L, piv.Position, dp.Unit, math.min(P.sonda, dp.Magnitude)) then lado = s; break end
			end
			if not lado then I.ultimoFlanco = agora; mudarPlano(L, I, "Pressionar", "sem espaco para flanquear", agora)
			else
				I.ladoFlanco = lado; I.ultimoFlanco = agora; I.golpesTrocados = 0
				I.flanco = {ate = agora + P.flanco.duracao, lado = lado, r = r}
				logIA(L, string.format("flanco pela %s (raio %.1f)", lado > 0 and "esquerda" or "direita", r))
			end
		end
		if I.flanco then
			local raio = flat(piv.Position - alvoCf.Position)
			local p2 = alvoCf.Position + girar(raio.Unit, math.rad(40 * I.flanco.lado)) * I.flanco.r
			irPara(L, I, noTerritorio(I, p2), "Trote", 1.5, nil, true)
			-- ao chegar no lado do alvo (fora do olhar dele), volta a pressionar
			local fa = flat(alvoCf.LookVector).Unit:Dot(flat(piv.Position - alvoCf.Position).Unit)
			if fa < math.cos(math.rad(70)) then I.flanco.ate = 0; mudarPlano(L, I, "Pressionar", "chegou ao flanco do alvo", agora) end
		end
	elseif plano == "Esquivar" then
		if not I.esquiva then
			-- sai da linha do golpe: perpendicular a linha alvo-lobo, no lado do flanco, um pouco para longe do alvo.
			-- Salto sem alvo so se essa direcao estiver ate P.esquiva.angulo da frente (o kit alinha o corpo na decolagem:
			-- giro maior seria um estalo); senao trota para o lado girando em movimento.
			local lado = I.ladoFlanco or 1
			local linha = flat(piv.Position - alvoCf.Position); if linha.Magnitude < 0.1 then linha = -fr end
			local rumo = girar(linha.Unit, math.rad((90 - 20) * lado))
			I.esquiva = true; I.esquivouAte = agora + P.esquiva.intervalo
			local angR = math.deg(math.abs(angAssinado(fr, rumo)))
			local feito = A.esquivaDesloc(L, a, "ativa")          -- 19/11: pequeno teleporte lateral (servidor valida)
			if feito then pararMov(L, I, nil); I.planoDesde = agora - P.esquiva.duracao + 0.2 end   -- retoma logo apos o deslocamento
			if not feito and angR <= P.esquiva.angulo and L.energia >= CFG.SaltoPredatorio.energiaSemAlvo + P.reservaEnergia then
				feito = golpe(L, I, "SaltoPredatorio", noTerritorio(I, piv.Position + rumo * P.esquiva.salto), string.format("esquiva lateral (salto sem alvo, %.0f graus da frente)", angR))
			end
			if not feito then
				-- a trote: mais para LONGE do alvo (40 graus da linha), girando em movimento
				local rumoT = girar(linha.Unit, math.rad(40 * lado))
				logIA(L, string.format("esquiva a trote para longe (%.0f graus da frente)", math.deg(math.abs(angAssinado(fr, rumoT)))))
				irPara(L, I, noTerritorio(I, piv.Position + rumoT * 10), "Trote", 1.5, nil, true)
			end
		end
	elseif plano == "Recuar" then
		local fora = flat(piv.Position - alvoCf.Position); if fora.Magnitude < 0.1 then fora = -fr end
		local p2 = noTerritorio(I, alvoCf.Position + fora.Unit * (P.recuo.dist + 4))
		if flat(p2 - piv.Position).Magnitude < 3 then          -- encurralado na coleira: recua contornando para o lado
			p2 = noTerritorio(I, piv.Position + girar(fora.Unit, math.rad(80 * (I.ladoFlanco or 1))) * 10)
		end
		irPara(L, I, p2, "Trote", 1.5, nil, true)
	elseif plano == "Recuperar" then
		-- ronda andando em arco a distancia (recupera energia; nao fica girando parado)
		local raio = flat(piv.Position - alvoCf.Position); if raio.Magnitude < 1 then raio = -fr end
		local p2 = alvoCf.Position + girar(raio.Unit, math.rad(25 * (I.ladoFlanco or 1))) * math.max(P.recuo.dist, raio.Magnitude)
		irPara(L, I, noTerritorio(I, p2), "Andar", 1.0, nil, true)
		if L.energia >= P.recuo.recuperarAte - 0.5 and agora - I.planoDesde >= P.recuo.minSeg then mudarPlano(L, I, "Pressionar", string.format("folego recuperado (energia %.0f)", L.energia), agora) end
	elseif plano == "Desistir" then
		-- vida critica: volta ao posto; so se defende se o alvo encostar
		irPara(L, I, I.posto, "Trote", G.voltaPostoDist, nil, true)
	end
	if I.plano ~= "Esquivar" then I.esquiva = nil end
	-- 3) GOLPE (planos ofensivos; recuperando/desistindo so se o alvo encostar)
	local defesa = (I.plano == "Recuperar" or I.plano == "Desistir") and dist <= P.recuo.defenderDentro
	if (I.plano == "Pressionar" or I.plano == "Perseguir" or I.plano == "Flanquear" or defesa)
		and L.estado == "Livre" and not (L.basicoAte and agora < L.basicoAte) and agora - (I.ultimoGolpe and I.ultimoGolpe.t or 0) >= P.intervaloGolpes then
		local melhor, desc = escolherGolpe(L, I, a, c, dist, angAlvo)
		if melhor then
			if melhor.n == "Investida" or melhor.n == "SaltoPredatorio" or melhor.n == "UivoAncestral" then pararMov(L, I, "Repouso") end
			golpe(L, I, melhor.n, melhor.dados, melhor.por)
		else
			-- registra o motivo de nao atacar (so quando muda, para nao inundar)
			local parts = {} for n, r in pairs(desc) do table.insert(parts, n .. ": " .. r) end; table.sort(parts)
			local s = table.concat(parts, "; ")
			if s ~= I.ultimoDesc and agora - (I.ultimoDescT or 0) > 1.5 then I.ultimoDesc = s; I.ultimoDescT = agora; A.logc("IA_BLOQUEIO", L, s) end
		end
	end
end

local function decidir(L, I, agora)
	if L.estado == "Caido" or L.estado == "Levantando" or L.estado == "Finalizando" or L.estado == "Retirado" then return end   -- 19/11
	local piv = L.modelo:GetPivot()
	if not I.offPiv then local y = A.chaoY(L, piv.Position); I.offPiv = y and (piv.Position.Y - y) or 0 end
	atualizarAmeacas(L, I, agora, piv.Position)
	local a = escolherAlvo(L, I)
	if a then
		I.combateAte = agora + P.recuperacaoApos
		decidirCombate(L, I, a, agora, piv)
		return
	end
	-- sem alvo de combate
	if I.plano and (I.plano == "Pressionar" or I.plano == "Perseguir" or I.plano == "Flanquear" or I.plano == "Recuar" or I.plano == "Recuperar" or I.plano == "Esquivar") then
		mudarPlano(L, I, I.investigar and "Investigar" or "Desistir", I.perdeuPor or "sem ameaca", agora)
	end
	local alerta = nil
	for x, e in pairs(I.ameacas) do if e.nivel == 1 and (not alerta or (e.dist or 99) < (I.ameacas[alerta].dist or 99)) then alerta = x end end
	if I.plano == "Investigar" or (I.investigar and agora < I.investigar.ate and I.plano ~= "Desistir") then
		if I.plano ~= "Investigar" then mudarPlano(L, I, "Investigar", "ultima posicao de " .. I.investigar.nome, agora) end
		local iv = I.investigar
		if not iv or agora > iv.ate then I.investigar = nil; mudarPlano(L, I, "Desistir", "investigacao sem rastro", agora)
		else
			irPara(L, I, noTerritorio(I, iv.pos), "FarejarAndando", 3, "Farejar")
			if I.mov and I.mov.chegou and not iv.farejou then iv.farejou = agora; logIA(L, "farejando a ultima posicao") end
			if iv.farejou and agora - iv.farejou > P.farejarSeg then I.investigar = nil; mudarPlano(L, I, "Desistir", "rastro frio", agora) end
		end
	elseif alerta then
		if I.plano ~= "Alerta" then mudarPlano(L, I, "Alerta", I.ameacas[alerta].motivo .. " (" .. alerta.Name .. ")", agora); I.alertaAvisou = nil end
		-- encara quem observa: giro grande com VirarE/D; aviso (rosnado) uma vez por intervalo; NAO ataca
		local c = A.centro(alerta); local fr = flat(piv.LookVector)
		local ang = c and angAssinado(fr, flat(c - piv.Position)) or 0
		if L.estado == "Livre" and not L.virando then
			if I.mov then pararMov(L, I, "Repouso") end
			if math.abs(ang) > math.rad(P.virarParado) then A.virarNoLugar(L, ang > 0 and 1 or -1)
			elseif not I.alertaAvisou or agora - I.alertaAvisou > P.avisoIntervalo then
				I.alertaAvisou = agora; L.C.acao(math.abs(ang) < math.rad(30) and "Rosnar" or "Alerta", 0.2)
				logIA(L, "aviso (" .. (math.abs(ang) < math.rad(30) and "rosnado" or "alerta") .. ") para " .. alerta.Name .. "; sem ataque")
			end
		end
	elseif I.plano == "Desistir" or (I.plano == "Alerta") then
		if I.plano == "Alerta" then mudarPlano(L, I, "Desistir", "observador foi embora", agora) end
		local d = flat(I.posto - piv.Position).Magnitude
		if d > G.voltaPostoDist then
			irPara(L, I, I.posto, d > 10 and "Trote" or "Andar", G.voltaPostoDist)
		else
			pararMov(L, I, "Repouso"); I.recuouVida = false
			mudarPlano(L, I, "Calmo", "de volta ao posto", agora)
			I.calmoDesde = agora
		end
	else
		if I.plano ~= "Calmo" then mudarPlano(L, I, "Calmo", "inicio", agora); I.calmoDesde = agora end
		-- calmo: repouso no posto; olha em volta de vez em quando (clipes existentes). Sem patrulha/caca/sono: sem regra.
		if L.estado == "Livre" and not L.virando and not I.mov and agora - (I.ultimoIdle or I.calmoDesde or agora) > P.idleIntervalo then
			I.ultimoIdle = agora
			local lista = {"Observar", "Farejar", "OlharTras"}
			local n = lista[(I.contIdle or 0) % #lista + 1]; I.contIdle = (I.contIdle or 0) + 1
			if n == "Farejar" then L.C.base("Farejar", 0.4); task.delay(4, function() if I.plano == "Calmo" and not I.mov and L.C.baseNome == "Farejar" then L.C.base("Repouso", 0.5) end end)
			else L.C.acao(n, 0.3) end
			logIA(L, "calmo: " .. n)
		end
	end
	if I.plano == "Calmo" and I.combateAte and agora < I.combateAte then
		-- logo apos o combate: recuperacao (sacode o corpo uma vez)
		if not I.sacudiu then I.sacudiu = true; L.C.acao("Sacudir", 0.2); logIA(L, "recuperacao apos combate (sacudir)") end
	else I.sacudiu = nil end
end

-- ------------------------------------------------------------------ ciclo
local function jogadorPerto(pos)
	for _, pl in ipairs(Players:GetPlayers()) do
		local r = pl.Character and pl.Character.PrimaryPart
		if r and (r.Position - pos).Magnitude <= P.raioJogadorPerto then return true end
	end
	return false
end
function M.ligar(L, posto)
	L.ia = {v2 = true, posto = posto, plano = nil, ameacas = {}, historico = {}, bloqueios = {}, contagem = {}, contPlanos = {},
		golpesTrocados = 0, proxima = 0, andando = false}
	-- 19/11: estilo proprio sorteado UMA vez por lobo (evita decisoes espelhadas entre dois lobos iguais) [A TESTAR]
	local PP, V = P.pressao, P.estiloVar
	local function var(x) return x * (1 + (math.random() * 2 - 1) * V) end
	L.ia.estilo = {arco = var(PP.arco), abrirAng = var(PP.abrirAng), abrirRaio = var(PP.abrirRaio),
		golpesPorEntrada = math.random() < 0.5 and PP.golpesPorEntrada or math.max(1, PP.golpesPorEntrada - 1)}
	L.ia.ladoFlanco = math.random() < 0.5 and 1 or -1
	L.modelo:SetAttribute("PlanoIA", "Calmo")
	local e = L.ia.estilo
	logIA(L, "IA estrategica ligada (posto " .. string.format("%.0f,%.0f", posto.X, posto.Z) .. string.format(") estilo: arco %.0f, saida %.0f graus/%.1f, %d golpes por entrada, lado %s",
		e.arco, e.abrirAng, e.abrirRaio, e.golpesPorEntrada, L.ia.ladoFlanco > 0 and "esquerdo" or "direito"))
	return L.ia
end
function M.info(L)
	local I = L.ia; if not I then return {} end
	return {plano = I.plano, motivo = I.planoMotivo, alvo = I.alvo and I.alvo.Name, vida = L.vida, energia = L.energia, estado = L.estado, virando = L.virando == true,
		marcha = I.andando and I.marcha or "parado", golpes = I.contagem, planos = I.contPlanos, pos = L.modelo:GetPivot().Position,
		decisoes = I.contDecisao, queda = I.queda and {alvo = I.queda.alvo.Name, fin = I.queda.fin, motivo = I.queda.motivo, fase = I.queda.fase,
			spot = I.queda.flanco and I.queda.flanco.spot, n = I.queda.flanco and I.queda.flanco.n, tentou = I.queda.tentou} or nil,
		movPonto = I.mov and I.mov.ponto}
end
function M.iniciar(api)
	A = api; CFG = api.CFG; P = CFG.IA_Lobo; G = CFG.IA_Guardiao
	RS.Heartbeat:Connect(function(dt)
		for _, L in pairs(A.lobos) do
			local I = L.ia
			if I and I.v2 and A.vivo(L) then
				local ok, err = pcall(passoMov, L, I, dt)
				if not ok then A.logc("IA_ERRO", L, "locomocao: " .. tostring(err)); I.mov = nil end
			end
		end
	end)
	task.spawn(function()
		while true do
			task.wait(P.tickCombate)
			local agora = os.clock()
			for _, L in pairs(A.lobos) do
				local I = L.ia
				if I and I.v2 and A.vivo(L) and agora >= I.proxima then
					local ok, err = pcall(decidir, L, I, agora)
					if not ok then A.logc("IA_ERRO", L, "decisao: " .. tostring(err)) end
					-- frequencia: combate/alerta 0,2 s; calmo 0,5 s; calmo sem jogador perto 1,5 s (varias copias, celular)
					local emAcao = I.plano and I.plano ~= "Calmo"
					I.proxima = agora + (emAcao and P.tickCombate or (jogadorPerto(L.modelo:GetPivot().Position) and P.tickCalmo or P.tickLonge))
				end
			end
		end
	end)
	-- quando o lobo morre: para a locomocao
	return M
end
return M
