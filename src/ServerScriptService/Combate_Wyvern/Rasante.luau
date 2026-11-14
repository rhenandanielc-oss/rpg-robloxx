-- Rasante (ModuleScript, ServerScriptService.Combate_Wyvern) — ativa RASANTE PREDATORIO da Wyvern (kit aprovado 13/11/2026).
-- AUTORIDADE DO SERVIDOR. Vaga 2 (tecla 2) via kitForma (Arremetida -> Rasante).
-- Comportamento aprovado:
--  * EM VOO: preparacao legivel (asas recolhem, corpo vira ate a mira), mergulho rapido numa faixa ESTREITA na direcao da
--    mira travada na arrancada; atinge o PRIMEIRO alvo da trajetoria e sai subindo; se errar, recuperacao breve antes de
--    devolver o controle.
--  * NO CHAO: agacha, batida curta de asas e salto RENTE ao solo, alcance menor, direcao fixada na arrancada; atinge o
--    primeiro alvo e volta a apoiar as patas; se errar, recuperacao breve antes de virar.
-- Duas metades que compartilham o estado S[modelo]:
--  * R.executar (Nucleo, N:_Rasante): fases, animacoes, deteccao do acerto (faixa estreita varrida pela boca) e dano.
--  * R.passo (Montaria_Dragao_Servidor, PATCH_RASANTE, inicio do passo de chao / voo livre): move o corpo.
-- So montado nesta etapa (a IA selvagem nao usa). Numeros em ConfigCombate.habilidades.Rasante (PROVISORIOS).
--
-- r2 AEREO (13/11, pedido do usuario: "curvas estranhas"; telemetria do Studio): a r1 trocava o vetor de velocidade por
-- fase (nivelado -> picada -55 graus -> subida +25 num quadro cada), somava a inclinacao do corpo a do clipe Mergulho
-- (o clipe ja traz o tronco a -40 graus: o corpo chegava a -84, quase vertical, e ficava congelado) e a do Subida (+27:
-- saida a +46 graus, "angulo quebrado"), e trocava os clipes com corte seco. Agora o voo e CONTINUO:
--  ENTRADA: parte da velocidade, rumo e trajetoria atuais; vira para a mira no ritmo que a velocidade permite (se a
--    virada nao couber, ABORTA antes de comprometer e devolve recarga e energia); inclina a trajetoria aos poucos ate a
--    picada; so compromete com corredor livre (spherecast) e altura para o arco de recuperacao (senao a picada fica mais
--    rasa; sem espaco nenhum, aborta).
--  PASSAGEM: rumo e picada fixos (alvo que sai da faixa escapa); acelera; o focinho lidera (a inclinacao do corpo segue a
--    trajetoria) e a cauda reage pelo MovimentoVivo do cliente.
--  SAIDA: arco progressivo de raio fixo (def.raioArco) mantendo a velocidade da passagem; comeca na altura que deixa o
--    fundo do arco rente ao chao (ou antes de obstaculo/apos o acerto); asas abrem (Planeio) e batem (VooBatido) para
--    recuperar sustentacao; devolve o voo com rumo, trajetoria e velocidade do fim do arco.
--  CORPO: L.pitch = trajetoria - (soma dos pesos x inclinacao embutida de cada clipe) -> o tronco VISIVEL segue a
--    trajetoria; taxa de giro limitada. CLIPES: tres trilhas em laco misturadas por peso a cada quadro (sem corte).
local RunService = game:GetService("RunService")
local R = {}
local S = {}                                  -- [modelo] = estado do rasante em andamento
R.estado = S
local Y = Vector3.yAxis
-- inclinacao do tronco embutida em cada clipe (graus; medido no Blender, L7: pelvis -> neck_01)
local PITCH_CLIPE = {Rasante_Ar = -40, Rasante_Recup = 5, Rasante_Batida = 0}
-- parametros do voo continuo (r2); ConfigCombate.habilidades.Rasante sobrepoe se tiver o campo. PROVISORIOS
local AR = {velMinAr = 18, giroEntrada = 110, folgaGiro = 8, entradaAr = 0.45, raioArco = 34, corredor = 90, corredorMin = 22,
	margemObstaculo = 8, gravidade = 30, acelAr = 90, gamaSaida = 8, gamaFinal = 3, planeioAcerto = 0.15, planeioErro = 0.4,
	taxaPitch = 160, inclinacaoGiro = 28, folgaAlvo = 6, acelArco = 115, correcaoPassagem = 8,
	folgaCorpo = 3, antecipa = 0.45, raioMinimo = 20, gamaFuga = 55, duracaoMax = 4.5, gamaFreio = 10}
local function comPadrao(def) return setmetatable({}, {__index = function(_, k) local v = def[k]; if v == nil then v = AR[k] end; return v end}) end

local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function angY(a, b)                     -- angulo assinado de a para b em torno de +Y (anti-horario visto de cima)
	a, b = plano(a), plano(b)
	if a.Magnitude < 1e-3 or b.Magnitude < 1e-3 then return 0 end
	a, b = a.Unit, b.Unit
	return math.atan2(a:Cross(b).Y, a:Dot(b))
end
local function distSeg(p, a, b)
	local ab = b - a; local l2 = ab:Dot(ab)
	local t = l2 > 1e-6 and math.clamp((p - a):Dot(ab) / l2, 0, 1) or 0
	return (p - (a + ab * t)).Magnitude, t
end
-- criatura = o modelo MAIS ALTO na hierarquia com Humanoid, FormaRegional ou GuardiaoNinho (r2c: o guardiao tem modelos
-- internos - sela, arreio - e olhar so o ancestral mais proximo deixava a sela passar como cenario)
local function criatura(inst)
	local achou
	local a = inst and inst.Parent
	while a and a ~= workspace do
		if a:IsA("Model") and (a:FindFirstChildOfClass("Humanoid") or a:GetAttribute("FormaRegional") ~= nil or a:GetAttribute("GuardiaoNinho") ~= nil) then achou = a end
		a = a.Parent
	end
	return achou
end
local function grande(mod) return mod ~= nil and (mod:GetAttribute("FormaRegional") ~= nil or mod:GetAttribute("GuardiaoNinho") ~= nil) end
-- obstaculo de verdade: parede/pilar (normal pouco vertical) e criatura GRANDE (dragao, wyvern, guardiao) que nao e o alvo
-- travado. Personagens/NPCs pequenos e o proprio alvo nao bloqueiam (o arco passa por cima deles). O chao a frente da
-- picada NAO e obstaculo (a altura do arco cuida dele): no 1o teste da r2 o corredor batia no chao a 42 studs
local function obstaculo(hit, alvo)
	if not hit then return false end
	local cri = criatura(hit.Instance)
	if cri then return cri ~= alvo and grande(cri) end
	if hit.Normal.Y > 0.7 then return false end
	return true
end
-- sonda propria de CRIATURAS GRANDES: o L.params do Locomotor exclui de proposito todos os dragoes ("convivencia cuida da
-- distancia") e o rasante herdava isso - no teste r2c a Wyvern atravessou um Silverwing parado no corredor. Lista Include
-- (sem a propria Wyvern e sem o alvo travado), refeita a cada 0,5 s. Colisao = malha na pose de repouso (aproximada).
local function sondaCriaturas(st, m, origem, raio, vetor)
	if not st.rpCri or (st.t or 0) - (st.tCri or -1) > 0.5 then
		local l = {}
		for _, d in ipairs(workspace:GetChildren()) do
			if d ~= m and d ~= st.alvoMod and d:IsA("Model") and grande(d) then table.insert(l, d) end
		end
		st.rpCri = st.rpCri or RaycastParams.new(); st.rpCri.FilterType = Enum.RaycastFilterType.Include
		st.rpCri.FilterDescendantsInstances = l; st.tCri = st.t or 0
	end
	return workspace:Spherecast(origem, raio, vetor, st.rpCri)
end
local function maisPerto(a, b) if a and b then return (a.Distance <= b.Distance) and a or b end return a or b end
-- chao do TERRENO sob o corpo: ignora criaturas/personagens (r2b: o raio batia no proprio alvo sob o fundo do arco) e
-- parte LOGO ACIMA do corpo (r2c: partindo 250 acima, encostado num pilar o "chao" virava o TOPO do pilar e o corpo
-- saltava 52 studs num quadro)
local function chaoTerreno(L, p)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
	local lista = table.clone(L.params.FilterDescendantsInstances)
	for _ = 1, 4 do
		rp.FilterDescendantsInstances = lista
		local r = workspace:Raycast(Vector3.new(p.X, p.Y + 8, p.Z), Vector3.new(0, -400, 0), rp)
		if not r then return nil end
		local cri = criatura(r.Instance)
		if cri then table.insert(lista, cri) else return r.Position.Y end
	end
	return nil
end
-- topo do CORPO VISIVEL do alvo (criaturas grandes): CorpoAltura/CorpoRaio dos dragoes sao pequenos (6/8) e nao servem
-- para a folga; mede pelas pecas visiveis (sem RootPart) com 5 raios em volta do pivo. Personagens: nil (folgaAlvo basta)
local function topoCorpo(alvo)
	if not alvo or not alvo.Parent or alvo:FindFirstChildOfClass("Humanoid") then return nil end
	local lista = {}
	for _, b in ipairs(alvo:GetDescendants()) do
		if b:IsA("BasePart") and b.Transparency < 1 and b.Name ~= "RootPart" then table.insert(lista, b) end
	end
	if #lista == 0 then return nil end
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = lista
	local c = alvo:GetPivot().Position; local topo
	for _, d in ipairs({Vector3.zero, Vector3.new(5, 0, 0), Vector3.new(-5, 0, 0), Vector3.new(0, 0, 5), Vector3.new(0, 0, -5)}) do
		local r = workspace:Raycast(c + d + Y * 200, Vector3.new(0, -400, 0), rp)
		if r then topo = math.max(topo or -math.huge, r.Position.Y) end
	end
	-- a colisao da malha com pele fica na pose de repouso; a pose ANIMADA vem dos ossos (sem as asas, que sobem e descem)
	for _, b in ipairs(alvo:GetDescendants()) do
		if b:IsA("Bone") then
			local n = b.Name:lower()
			if not (n:find("wing") or n:find("asa") or n:find("feather") or n:find("strut") or n:find("finger") or n:find("thumb")
				or n:find("upperarm") or n:find("forearm") or n:find("hand")) then
				topo = math.max(topo or -math.huge, b.TransformedWorldCFrame.Position.Y + 1.5)   -- +1,5 = espessura da pele
			end
		end
	end
	return topo
end
R._topoCorpo = topoCorpo                       -- teste
local function suave(k) k = math.clamp(k, 0, 1); return k * k * (3 - 2 * k) end
function R.ativo(m) return S[m] ~= nil end

-- varredura da faixa estreita pela boca (comum ao chao e ao ar): o PRIMEIRO alvo do segmento varrido neste quadro
local function varrer(self, N, def, a, b)
	local melhor, tMin = nil, math.huge
	for _, alvo in ipairs(self:alvosValidos()) do
		local extra = alvo:GetAttribute("GuardiaoNinho") and (alvo:GetAttribute("CorpoRaio") or 8) or 0
		local pa = N.pontoAlvo(alvo)
		local d, tt = distSeg(plano(pa), plano(a), plano(b))
		local yOk = pa.Y <= math.max(b.Y, a.Y) + 4 and pa.Y >= math.min(b.Y, a.Y) - def.alcanceBaixo - extra
		if yOk and d <= def.raio + extra and tt < tMin then melhor, tMin = alvo, tt end
	end
	return melhor
end

-- ===== metade do combate (Nucleo) =================================================================================
local executarChao
function R.executar(self, def, el, noAr, op)
	local N = getmetatable(self)
	local m = self.m
	if m:GetAttribute("Controlador") ~= "Montaria" then return end          -- so montado nesta etapa
	-- direcao da mira: alvo travado > direcao pedida > frente; desvio limitado a def.giroMax a partir da frente atual
	local frente = self:frente()
	local origem = noAr and m:GetPivot().Position or self:boca()            -- no ar: na picada a boca fica no nivel do pivo
	local mira = (op and op.alvo and op.alvo.Parent and (N.pontoAlvo(op.alvo) - origem))
		or (op and typeof(op.direcao) == "Vector3" and op.direcao) or frente
	if not noAr then return executarChao(self, N, def, el, mira, frente) end
	-- ---------------------------------------------------------------- AR (r2)
	local a = angY(frente, mira)
	local dirH = CFrame.fromAxisAngle(Y, math.clamp(a, -math.rad(def.giroMax), math.rad(def.giroMax))):VectorToWorldSpace(frente)
	local h = plano(mira).Magnitude
	local picada = math.clamp(-math.atan2(mira.Y, math.max(h, 1e-3)), math.rad(def.picadaMin), math.rad(def.picadaMax))
	def = comPadrao(def)
	-- ponto mirado no COMPROMISSO (fixo: alvo que se mexe depois pode escapar); a picada e refeita a partir dele ao fim da entrada
	local miraPonto = origem + (op and op.alvo and op.alvo.Parent and mira or mira.Unit * 120)
	local st = {modo = "ar", fase = "entrada", dirH = dirH, giroPedido = a, miraVec = mira, picada = picada, miraPonto = miraPonto, t = 0, acertou = false, def = comPadrao(def),
		travado = (op and op.alvo and op.alvo.Parent) ~= nil, alvoMod = op and op.alvo,
		w = {Rasante_Ar = 0, Rasante_Recup = 1, Rasante_Batida = 0}}
	S[m] = st
	m:SetAttribute("RasanteFase", "entrada"); m:SetAttribute("RasanteModo", "ar"); m:SetAttribute("RasanteAbortado", nil); m:SetAttribute("RasanteFreio", nil)
	m:SetAttribute("RasanteMira", ("alvo=%s giro=%.1f picada=%.1f"):format(tostring(op and op.alvo and op.alvo.Name), math.deg(a), math.deg(picada)))   -- depuracao
	-- o primeiro passo da montaria planeja (precisa do Locomotor: chao, obstaculos, velocidade atual)
	local t0 = os.clock()
	while not st.plano and os.clock() - t0 < 0.5 and S[m] == st do RunService.Heartbeat:Wait() end
	if st.abortar or not st.plano then                                       -- nada comprometido: devolve recarga e energia
		self.recargas["Arremetida"] = os.clock(); self.energia = math.min(self.energia + (def.energia or 0), 100)
		m:SetAttribute("RecargaFim_Arremetida", workspace:GetServerTimeNow()); m:SetAttribute("Energia", self.energia)
		m:SetAttribute("RasanteAbortado", st.abortar or "sem plano"); m:SetAttribute("RasanteAcertos", nil)
		if S[m] == st then S[m] = nil end
		m:SetAttribute("RasanteFase", nil); m:SetAttribute("RasanteModo", nil)
		return
	end
	N.FX:FireAllClients({d = m, hab = "Rasante", fase = "preparo", el = el, noAr = true})
	-- tres trilhas em laco, misturadas por peso (st.w, calculado no passo)
	local trilhas = {}
	for nome in pairs(PITCH_CLIPE) do
		local t = self:clipe(nome, false)
		if t then t.Looped = true; t:Play(0.2, math.max(st.w[nome], 0.001)); trilhas[nome] = t end
	end
	local bocaAnt = self:boca(); local avisou = false
	while S[m] == st and not st.fim and m.Parent and not m:GetAttribute("Incapacitado") and os.clock() - t0 < 5 do
		RunService.Heartbeat:Wait()
		for nome, t in pairs(trilhas) do t:AdjustWeight(math.max(st.w[nome] or 0, 0.001), 0.08) end
		if st.fase == "passagem" and not avisou then
			avisou = true; m:SetAttribute("RasanteFase", "passagem")
			N.FX:FireAllClients({d = m, hab = "Rasante", fase = "emissao", el = el, noAr = true})
		elseif st.fase ~= "passagem" then m:SetAttribute("RasanteFase", st.fase) end
		local b = self:boca()
		-- acerto: na passagem e no fundo do arco (a boca ainda varre o caminho)
		if not st.acertou and (st.fase == "passagem" or (st.fase == "saida" and (st.u or 1) < 0.6)) then   -- ate o fundo do arco
			local alvo = varrer(self, N, def, bocaAnt, b)
			if alvo then
				st.acertou = true
				self:aplicar({alvo}, def.dano, "Rasante", def.intensidade, el)
				m:SetAttribute("RasanteAcertos", 1)
				N.FX:FireAllClients({d = m, hab = "Rasante", fase = "impacto", pos = N.pontoAlvo(alvo), el = el, acertou = true})
			end
		end
		bocaAnt = b
	end
	if not st.acertou then m:SetAttribute("RasanteAcertos", 0) end
	for _, t in pairs(trilhas) do t:Stop(0.45) end                          -- o misturador da montaria assume aos poucos
	if S[m] == st then S[m] = nil end
	m:SetAttribute("RasanteFase", nil); m:SetAttribute("RasanteModo", nil)
end

-- chao: inalterado desde a r1 aprovada (salto rente; acerto do 1o alvo; parede para rente)
function executarChao(self, N, def, el, mira, frente)
	local m = self.m
	local a = math.clamp(angY(frente, mira), -math.rad(def.giroMax), math.rad(def.giroMax))
	local dirH = CFrame.fromAxisAngle(Y, a):VectorToWorldSpace(frente)
	local st = {modo = "chao", fase = "prep", dirH = dirH, giro = a, t = 0, acertou = false, def = def}
	S[m] = st
	m:SetAttribute("RasanteFase", "prep"); m:SetAttribute("RasanteModo", "chao")
	N.FX:FireAllClients({d = m, hab = "Rasante", fase = "preparo", el = el, noAr = false})
	local trilhas = {}
	local function tocar(nome, ritmo, loop)
		local t = self:clipe(nome, false)
		if t then t.Looped = loop == true; t:Play(0.15); if ritmo then t:AdjustSpeed(ritmo) end; table.insert(trilhas, t) end
		return t
	end
	local function parar() for _, t in ipairs(trilhas) do t:Stop(0.25) end; trilhas = {} end
	tocar("Rasante_Chao", def.ritmoSaltoChao, false)
	local function esperar(seg, cada)
		local t0 = os.clock()
		while os.clock() - t0 < seg and S[m] == st and m.Parent and not m:GetAttribute("Incapacitado") do
			RunService.Heartbeat:Wait(); if cada and cada() then return true end
		end
		return false
	end
	esperar(def.prepChao)
	if S[m] ~= st then return end
	st.fase = "investida"; m:SetAttribute("RasanteFase", "investida")
	N.FX:FireAllClients({d = m, hab = "Rasante", fase = "emissao", el = el, noAr = false})
	local bocaAnt = self:boca()
	local atingido = nil
	esperar(def.durChao, function()
		local b = self:boca()
		local alvo = varrer(self, N, def, bocaAnt, b)
		bocaAnt = b
		if alvo then atingido = alvo; return true end
		return st.bateu == true
	end)
	if atingido then
		st.acertou = true
		self:aplicar({atingido}, def.dano, "Rasante", def.intensidade, el)
		m:SetAttribute("RasanteAcertos", 1)
		N.FX:FireAllClients({d = m, hab = "Rasante", fase = "impacto", pos = N.pontoAlvo(atingido), el = el, acertou = true})
		st.fase = "saida"; m:SetAttribute("RasanteFase", "saida")
		parar(); tocar("Rasante_Pouso", nil, false)
		esperar(def.saida)
	else
		m:SetAttribute("RasanteAcertos", 0)
		st.fase = "recup"; m:SetAttribute("RasanteFase", "recup")
		parar(); tocar("Rasante_Pouso", nil, false)
		esperar(def.recup)
	end
	parar()
	if S[m] == st then S[m] = nil end
	m:SetAttribute("RasanteFase", nil); m:SetAttribute("RasanteModo", nil)
end

-- ===== metade do movimento (montaria) =============================================================================
local passoAr
-- devolve true se moveu o corpo neste quadro (o controlador da montaria pula o proprio passo)
function R.passo(M, dt, modo, aplicar)
	local m, L = M.m, M.L
	local st = S[m]
	if not st then return false end
	if st.modo == "ar" then
		if modo ~= "ar" then return false end
		return passoAr(M, dt, st, aplicar)
	end
	local def = st.def
	st.t += dt
	local p = L:pos()
	if st.fase == "prep" then
		local falta = angY(L:frente(), st.dirH)
		L.psi += math.clamp(falta, -math.rad(def.giroPrep) * dt, math.rad(def.giroPrep) * dt)
	end
	-- chao: salto rente ao solo (r1)
	local alvoV, freio = 0, 150
	if st.fase == "investida" then alvoV = def.velChao; freio = 300 end
	M.vel += math.clamp(alvoV - M.vel, -freio * dt, freio * dt)
	local dir = st.fase == "prep" and L:frente() or st.dirH
	if st.fase == "investida" then
		local hC, rC = m:GetAttribute("CorpoAltura") or 34, m:GetAttribute("CorpoRaio") or 22
		if workspace:Spherecast(p + Y * hC * 0.6, rC * 0.7, dir * (M.vel * dt + rC), L.params) then st.bateu = true; M.vel = 0 end
	end
	local np = p + dir * M.vel * dt
	local g = L:chaoLocal(np)
	if not g then M.vel = 0; np = p; g = L:chaoLocal(p) or (p.Y - L.alturaPivo); st.bateu = st.fase == "investida" or st.bateu end
	local h = 0
	if st.fase == "investida" then
		st.tI = (st.tI or 0) + dt
		h = def.alturaSalto * math.sin(math.pi * math.clamp(st.tI / def.durChao, 0, 1))
	end
	L.pitch += ((st.fase == "prep" and -math.rad(6) or 0) - L.pitch) * math.min(1, 8 * dt)
	M.roll += (0 - M.roll) * math.min(1, 6 * dt)
	aplicar(M, Vector3.new(np.X, g + L.alturaPivo + h, np.Z))
	m:SetAttribute("Velocidade", math.floor(M.vel))
	return true
end

-- ---------------------------------------------------------------- AR (r2): voo continuo
local function planejar(M, st, L)
	local m, def = M.m, st.def
	local p = L:pos()
	local hC, rC = m:GetAttribute("CorpoAltura") or 34, m:GetAttribute("CorpoRaio") or 22
	st.s = math.max(M.vel or 0, def.velMinAr)                                -- parte da velocidade atual
	st.gama = M.gama or 0                                                    -- e da trajetoria atual
	st.pitchVis = st.gama
	-- virada: o que cabe na entrada com a velocidade atual (mais rapido = vira menos)
	local taxa = math.rad(def.giroEntrada) * (1 - math.clamp(st.s / def.velAr, 0, 1) * 0.55)
	-- direcao comprometida medida do RUMO REAL do corpo (L:frente, o que move o voo). N:frente usa cabeca-quadril ANIMADOS
	-- e oscila ~8-10 graus com o clipe de voo: no teste r2b um alvo a 32 graus virou "virada de 49 graus" e abortou
	local fr = L:frente()
	local aR = math.clamp(angY(fr, st.miraVec), -math.rad(def.giroMax), math.rad(def.giroMax))
	st.dirH = CFrame.fromAxisAngle(Y, aR):VectorToWorldSpace(fr)
	local falta = aR
	if math.abs(falta) > taxa * def.entradaAr + math.rad(def.folgaGiro) then
		st.abortar = ("virada de %.0f graus nao cabe a %.0f studs/s"):format(math.deg(math.abs(falta)), st.s); return
	end
	st.taxaGiro = taxa
	-- altura: o arco de raio R precisa de R(1-cos picada) + folga abaixo do inicio da saida; a entrada tambem desce
	-- sem chao embaixo (fora do mapa / vao): usa o ultimo chao conhecido, a MESMA regra da montaria (M.ultimoChao); com
	-- p.Y-200 o rasante soltava a 12 e a montaria puxava para o seu piso, degrau de 7 studs na devolucao (teste r2b)
	local g = chaoTerreno(L, p); if g then st.ultChao = g end; g = g or st.ultChao or M.ultimoChao
	local chao = g and (g + L.alturaPivo) or (p.Y - 200)
	local altura = p.Y - chao
	-- raio do arco pela velocidade da passagem (aceleracao centripeta maxima acelArco): a 75 studs/s o raio fixo de 34 dava
	-- ~2,2 rad/s de subida e o tronco virava ~23 graus em 0,1 s no fundo (teste r2b); agora ~49 studs, ~1,5 rad/s
	st.R = math.max(def.raioArco, def.velAr * def.velAr / def.acelArco)
	local Rr = st.R
	local function cabe(pc)
		local desceEntrada = st.s * def.entradaAr * math.sin(pc) * 0.5
		return Rr * (1 - math.cos(pc)) + def.folgaRasante + 2 + desceEntrada <= altura
	end
	local pc = st.picada
	-- criatura grande como alvo: o fundo do arco passa por CIMA do corpo (r2c: o fundo cortava o dorso do dragao)
	st.topoAlvo = st.travado and topoCorpo(st.alvoMod) or nil
	if st.travado then
		-- alvo travado: geometria do arco tangente JA no compromisso. Preve onde a entrada termina (avanca ~0,9*s*T e desce
		-- metade de s*T*sin) e acha a picada cuja reta, de la, chega ao ponto recuado X0 (fundo do arco sobre o alvo). Mais
		-- ingreme que picadaMax = alvo perto demais para a picada: aborta e devolve (r2b; teste a 33 studs saia sem acertar)
		local alvoPt = st.miraPonto
		local yb = math.max(alvoPt.Y + def.folgaAlvo, chao + def.folgaRasante, (st.topoAlvo or -math.huge) + def.folgaCorpo)
		local hAlvo = plano(alvoPt - p):Dot(st.dirH.Unit)
		local T = def.entradaAr
		local q = pc
		for _ = 1, 6 do
			local dh = hAlvo - st.s * T * 0.9 - Rr * math.tan(q / 2)
			local dy = (p.Y - st.s * T * math.sin(q) * 0.5) - yb
			if dh <= 1 then q = math.huge; break end
			q = math.max(math.atan2(dy, dh), math.rad(def.picadaMin))
		end
		if q > math.rad(def.picadaMax) then
			st.abortar = ("alvo perto demais para a picada (%.0f studs a frente, %.0f acima)"):format(hAlvo, p.Y - yb); return
		end
		pc = q
	end
	-- (travado: o fundo do arco ja fica em yb >= chao + folgaRasante pela construcao; nao reduz a picada aqui)
	while not st.travado and pc > math.rad(def.picadaMin) and not cabe(pc) do pc -= math.rad(2) end
	if not st.travado and not cabe(pc) then st.abortar = ("sem altura para recuperar (%.0f studs)"):format(altura); return end
	st.picada = pc
	local pmax = math.rad(def.picadaMax)                                     -- maior picada que a altura ainda permite
	while not st.travado and pmax > pc and not cabe(pmax) do pmax -= math.rad(2) end
	st.picadaMaxPlano = math.max(pmax, pc)
	-- corredor: varre o caminho comprometido com o corpo + asas + cavaleiro (raio do corpo)
	local dir3 = (st.dirH.Unit * math.cos(pc) - Y * math.sin(pc)).Unit
	-- r2b (teste do pilar): obstaculo no corredor = NAO compromete (aborta e devolve). Antes a picada era encurtada (limite)
	-- e a saida comecava diante do pilar mais alto que o voo: o corpo parava 0,15 s e a montaria o jogava 37 studs acima.
	-- Com alvo travado o corredor vai ate o fundo do arco e continua RENTE depois dele (o arco sobe so ate gamaSaida).
	local compr = def.corredor
	if st.travado then compr = math.min(def.corredor * 1.5, plano(st.miraPonto - p).Magnitude / math.cos(pc) + rC) end
	local hit = workspace:Spherecast(p + Y * hC * 0.5, rC * 0.8, dir3 * compr, L.params)
	if not obstaculo(hit, st.alvoMod) then hit = nil end
	hit = maisPerto(hit, sondaCriaturas(st, m, p + Y * hC * 0.5, rC * 0.8, dir3 * compr))
	if not hit and st.travado then                                           -- trecho rente depois do fundo do arco
		local yb = math.max(st.miraPonto.Y + def.folgaAlvo, chao + def.folgaRasante, (st.topoAlvo or -math.huge) + def.folgaCorpo)
		local fundo = Vector3.new(st.miraPonto.X, yb + hC * 0.5, st.miraPonto.Z)
		hit = workspace:Spherecast(fundo, rC * 0.8, st.dirH.Unit * (Rr + def.margemObstaculo + rC), L.params)
		if not obstaculo(hit, st.alvoMod) then hit = nil end
		hit = maisPerto(hit, sondaCriaturas(st, m, fundo, rC * 0.8, st.dirH.Unit * (Rr + def.margemObstaculo + rC)))
		if hit then st.abortar = ("obstaculo logo depois do alvo (%.0f studs alem)"):format(hit.Distance); return end
	end
	if hit then st.abortar = ("obstaculo no trajeto a %.0f studs"):format(hit.Distance); return end
	st.limite = math.huge
	m:SetAttribute("RasantePlano", ("falta=%.1f taxa=%.0f/s picada=%.1f max=%.1f limite=%s"):format(math.deg(falta), math.deg(taxa), math.deg(pc), math.deg(st.picadaMaxPlano), tostring(hit and math.floor(hit.Distance))))   -- depuracao
	st.percorrido = 0
	st.plano = true
end

function passoAr(M, dt, st, aplicar)
	local m, L, def = M.m, M.L, st.def
	if not st.plano then planejar(M, st, L); if not st.plano then return false end end
	st.t += dt
	local p = L:pos()
	local hC, rC = m:GetAttribute("CorpoAltura") or 34, m:GetAttribute("CorpoRaio") or 22
	-- sem chao embaixo (fora do mapa / vao): usa o ultimo chao conhecido, a MESMA regra da montaria (M.ultimoChao); com
	-- p.Y-200 o rasante soltava a 12 e a montaria puxava para o seu piso, degrau de 7 studs na devolucao (teste r2b)
	local g = chaoTerreno(L, p); if g then st.ultChao = g end; g = g or st.ultChao or M.ultimoChao
	local chao = g and (g + L.alturaPivo) or (p.Y - 200)
	local Rr = st.R or def.raioArco
	local giroRate = 0
	-- ---- fases
	if st.fase == "entrada" then
		local tau = math.clamp(st.t / def.entradaAr, 0, 1)
		local falta = angY(L:frente(), st.dirH)                                -- vira no ritmo permitido
		st.faltaIni = st.faltaIni or math.deg(falta)
		giroRate = math.clamp(falta / math.max(dt, 1e-3), -st.taxaGiro, st.taxaGiro)
		L.psi += giroRate * dt
		st.gama0 = st.gama0 or st.gama
		st.gama = st.gama0 + (-st.picada - st.gama0) * suave(tau)              -- inclina a trajetoria aos poucos
		st.s += (def.gravidade * math.sin(-st.gama) - 2) * dt
		if tau >= 1 then
			st.fase = "passagem"
			-- refaz a picada a partir de onde a entrada terminou (a entrada avanca quase nivelada; sem isto a linha real ficava
			-- ACIMA da mira; teste r2). Geometria do arco tangente: a reta mira um ponto X0 RECUADO R*tan(picada/2) antes do
			-- alvo, na altura do alvo; a saida comeca no ponto de tangencia e o FUNDO do arco passa sobre o alvo (com a saida
			-- iniciada so pela altura, o fundo ficava ~24 studs depois do alvo e a boca passava acima da faixa)
			local alvoPt = st.miraPonto
			-- re-mira o PONTO COMPROMETIDO (nao o alvo atual) a partir de onde a curva da entrada deixou o corpo: virar durante a
			-- entrada desloca o corpo para o lado da reta original (teste r2b: alvo a 32 graus, fundo do arco 4,4 studs ao lado)
			local vH = plano(alvoPt - p)
			if vH.Magnitude > 5 then
				local corr = math.clamp(angY(st.dirH, vH), -math.rad(def.correcaoPassagem), math.rad(def.correcaoPassagem))
				st.dirH = CFrame.fromAxisAngle(Y, corr):VectorToWorldSpace(st.dirH)
			end
			local yb = math.max(alvoPt.Y + def.folgaAlvo, chao + def.folgaRasante, (st.topoAlvo or -math.huge) + def.folgaCorpo)
			local function ponto(pc) return Vector3.new(alvoPt.X, yb, alvoPt.Z) - st.dirH.Unit * (Rr * math.tan(pc / 2)) end
			local pc = st.picada
			for _ = 1, 3 do                                                     -- converge a picada com o recuo
				local v = ponto(pc) - p
				pc = math.clamp(-math.atan2(v.Y, math.max(plano(v).Magnitude, 1e-3)), math.rad(def.picadaMin), math.rad(def.picadaMax))
			end
			-- ainda respeita a altura para o arco (planejada) e muda no maximo 15 graus (sem quebra)
			st.picada = math.clamp(pc, st.picada - math.rad(15), math.min(st.picada + math.rad(15), st.picadaMaxPlano))
			st.X0 = ponto(st.picada)
		end
	elseif st.fase == "passagem" then
		local faltaP = angY(L:frente(), st.dirH)                               -- alinha a correcao pequena, giro suave
		giroRate = math.clamp(faltaP / math.max(dt, 1e-3), -st.taxaGiro * 0.5, st.taxaGiro * 0.5)
		L.psi += giroRate * dt
		st.gama += (-st.picada - st.gama) * math.min(1, 6 * dt)                -- ajusta suave para a picada refeita
		st.s = math.min(def.velAr, st.s + (def.acelAr + def.gravidade * math.sin(st.picada)) * dt)
		local altura = p.Y - chao
		local precisa = Rr * (1 - math.cos(st.picada)) + def.folgaRasante
		-- ponto de tangencia: distancia restante ao longo da reta ate X0 <= R*tan(picada/2)
		local dir3 = (st.dirH.Unit * math.cos(st.picada) - Y * math.sin(st.picada))
		local tangente = st.X0 and (st.X0 - p):Dot(dir3) <= Rr * math.tan(st.picada / 2)
		if tangente or altura <= precisa or st.percorrido >= st.limite or st.acertou or st.t > def.entradaAr + def.durAr then
			st.fase = "saida"; st.gamaIni = st.gama
		end
	end
	if st.fase == "saida" then
		local w = st.s / (st.raioSaida or Rr)                                  -- arco progressivo: dgama/dt = v / R
		local bloq = st.tBloq ~= nil and st.t - st.tBloq < 0.25
		local teto = bloq and math.rad(def.gamaFuga) or math.max(math.rad(def.gamaSaida), st.gama)
		st.gama = math.min(st.gama + w * dt, teto)
		st.s = math.max(def.velMinAr, st.s - (def.gravidade * math.max(math.sin(st.gama), 0) + 4) * dt)
		st.u = (st.gama - st.gamaIni) / (math.rad(def.gamaSaida) - st.gamaIni)
		if st.gama >= math.rad(def.gamaSaida) - 1e-3 and not bloq then
			st.fase = "planeio"; st.tPlaneio = 0
		end
	elseif st.fase == "planeio" then
		st.tPlaneio += dt
		st.gama += (math.rad(def.gamaFinal) - st.gama) * math.min(1, 3 * dt)
		-- so devolve acima da folga normal do voo (senao a montaria puxa o corpo de uma vez: degrau de 0,4 no teste r2)
		local folgaNormal = chao + (m:GetAttribute("FolgaChao") or 12)
		if p.Y < folgaNormal then st.gama = math.max(st.gama, math.rad(def.gamaFinal + 4)) end
		if (st.tPlaneio >= (st.acertou and def.planeioAcerto or def.planeioErro) and p.Y >= folgaNormal) or st.tPlaneio > 2 then st.fim = true end
	end
	if st.fase == "freio" then
		st.tFreio += dt
		st.gama += (math.rad(def.gamaFreio) - st.gama) * math.min(1, 5 * dt)
		-- devolve PARADO (pairando): devolvendo a 17 studs/s a montaria ainda deslizava 14 studs e a cabeca entrava no pilar
		if st.s <= 2 or st.tFreio > 1.2 then st.fim = true end
	end
	if st.t > def.duracaoMax then st.fim = true end                          -- seguranca: nunca prende o controle
	-- ---- movimento (vetor de velocidade continuo)
	local dir = (L:frente() * math.cos(st.gama) + Y * math.sin(st.gama)).Unit
	local passo = st.s * dt
	-- obstaculo que APARECE durante o rasante (fora do corredor planejado, em movimento, criatura que se levanta): olha
	-- ~0,45 s a frente e entra em FREIO - "flare" de ave: nariz um pouco acima, asas batendo, desaceleracao pela distancia
	-- livre - e devolve o voo a montaria devagar diante do obstaculo. r2c: antes parava 0,2 s e saltava 52 studs; depois
	-- subia a face em pe por 2 s. Deslize pela face so como garantia no contato.
	-- alcance da CABECA a frente do pivo (osso animado): o pescoco/cabeca vao ~13 studs a frente; medindo so do corpo a
	-- Wyvern parava a 4 studs da face com a cabeca DENTRO do pilar (r2c, quadros do perfil)
	if st.osCabeca == nil then st.osCabeca = false; for _, b in ipairs(m:GetDescendants()) do if b:IsA("Bone") and b.Name == "Cabeca" then st.osCabeca = b; break end end end
	local alc = st.osCabeca and math.max(0, (st.osCabeca.TransformedWorldCFrame.Position - p):Dot(dir)) or 0
	local olhar = st.s * def.antecipa + rC + alc
	local hit = workspace:Spherecast(p + Y * hC * 0.5, rC * 0.8, dir * olhar, L.params)
	if not obstaculo(hit, st.alvoMod) then hit = nil end
	hit = maisPerto(hit, sondaCriaturas(st, m, p + Y * hC * 0.5, rC * 0.8, dir * olhar))
	if hit and st.fase ~= "freio" then st.fase = "freio"; st.tFreio = 0; st.wAFreio = st.w.Rasante_Ar or 0; m:SetAttribute("RasanteFreio", math.floor(hit.Distance)) end
	if st.fase == "freio" then
		local livre = hit and math.max(hit.Distance - rC - alc - 2, 1) or math.huge          -- folga medida da CABECA
		local a = math.clamp(st.s * st.s / (2 * math.max(livre - 2, 1)), 60, 260)       -- para antes da face
		st.s = math.max(0, st.s - a * dt)
		passo = st.s * dt
		if hit and hit.Distance < passo + rC * 0.3 + alc and dir:Dot(hit.Normal) < 0 then          -- garantia: nunca atravessa
			dir = dir - hit.Normal * dir:Dot(hit.Normal); if dir.Magnitude > 1e-3 then dir = dir.Unit end
		end
	end
	st.percorrido = (st.percorrido or 0) + passo
	local np = p + dir * passo
	if np.Y < chao + def.folgaRasante then np = Vector3.new(np.X, chao + def.folgaRasante, np.Z); st.gama = math.max(st.gama, 0) end
	-- ---- pesos dos clipes: asas recolhem na picada, abrem no arco, batem no fim do arco
	local kTuck = math.clamp(st.picada / math.rad(40), 0.45, 1)
	local wA, wB = 0, 0
	if st.fase == "entrada" then wA = kTuck * suave(st.t / def.entradaAr)
	elseif st.fase == "passagem" then wA = kTuck
	elseif st.fase == "saida" then local u = math.clamp(st.u or 0, 0, 1); wA = kTuck * (1 - suave(u * 1.5)); wB = 0.6 * suave((u - 0.45) / 0.55)
	elseif st.fase == "freio" then wA = (st.wAFreio or 0) * (1 - suave((st.tFreio or 0) / 0.3)); wB = 0.6 * suave((st.tFreio or 0) / 0.25)
	else wB = 0.6 * (1 - suave((st.tPlaneio or 0) / 0.4)) end
	local wP = math.max(0, 1 - wA - wB)
	st.w.Rasante_Ar, st.w.Rasante_Batida, st.w.Rasante_Recup = wA, wB, wP
	-- ---- corpo: tronco visivel = trajetoria (+ focinho lidera); desconta a inclinacao embutida nos clipes
	local lead = (st.fase == "entrada" and -math.rad(6) * math.sin(math.pi * math.clamp(st.t / def.entradaAr, 0, 1)))
		or (st.fase == "saida" and math.rad(6) * suave((st.u or 0) * 3)) or 0      -- r2b: entra aos poucos (degrau de ~8 graus no grafico)
	local embut = math.rad(wA * PITCH_CLIPE.Rasante_Ar + wP * PITCH_CLIPE.Rasante_Recup + wB * PITCH_CLIPE.Rasante_Batida)
	local alvoPitch = math.clamp(st.gama + lead - embut, -math.rad(60), math.rad(45))
	local maxP = math.rad(def.taxaPitch) * dt
	L.pitch += math.clamp(alvoPitch - L.pitch, -maxP, maxP)
	local alvoRoll = -math.clamp(giroRate / math.max(st.taxaGiro or 1, 1e-3), -1, 1) * math.rad(def.inclinacaoGiro)
	M.roll += (alvoRoll - M.roll) * math.min(1, 6 * dt)
	aplicar(M, np)
	M.vel = st.s
	m:SetAttribute("Velocidade", math.floor(st.s))
	if st.fim then                                                            -- devolve o voo continuo para a montaria
		M.gama = st.gama; M.vyH = 0; M.yawRate = 0; M.planar = false
	end
	return true
end
return R
