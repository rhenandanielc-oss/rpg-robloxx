-- LaminaVento (ModuleScript, ServerScriptService.Combate_Wyvern) — ativa LAMINA DE VENTO da Wyvern (vaga 3). AUTORIDADE DO
-- SERVIDOR: o cliente so pede (tecla 3 / botao 3); o Nucleo valida recarga/energia/ocupado/transicao antes de chamar.
-- Regra (kit aprovado; ATUALIZADA pelo usuario em 14/11): recolhe as asas a frente do peito e abre ambas de uma vez; cada asa
-- emite um corte diagonal que cruza o outro logo a frente, formando um X largo. O X viaja como UM projetil TELEGUIADO de
-- media distancia e ajusta a trajetoria em voo para perseguir o ALVO DO DISPARO, como um missil. Cada alvo pode ser
-- atingido uma vez por disparo. Terra e ar.
-- Clipes (Blender, Wyvern_E7_clipes_L8): LaminaVento (chao, 1,6 s, emissao 0,49 s) e LaminaVento_Ar (voo, 1,3 s, emissao
-- 0,40 s). No ar o voo continua (o Locomotor so para o corpo com EmAtaque = "Arremetida").
-- Alvo do disparo: alvo travado (op.alvo, ja validado) > o alvo valido mais perto da linha de mira dentro do cone de
-- aquisicao (op.direcao = camera/mira) > nenhum (voa reto na mira).
-- Voo: posicao/direcao no servidor a cada Heartbeat; a direcao gira para o ponto do alvo no maximo def.taxaCurva graus/s;
-- persegue ate def.duracao s ou def.alcance studs. Acertos: hitbox em X no plano perpendicular ao voo (duas diagonais com
-- espessura, meia-largura do X), 1 por alvo (tabela do disparo); o X segue ate acertar o ALVO DO DISPARO (fim, como missil),
-- bater em terreno/estrutura ou acabar o tempo. Outros alvos no caminho tomam 1 acerto e o X continua.
-- Custo: 1 projetil por disparo; lista de alvos refeita a cada 0,2 s (nao a cada quadro); efeito: estado a cada 0,1 s.
-- Numeros (dano, velocidade, curva, duracao, alcance, largura) PROVISORIOS = balanceamento.
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local L = {}
L.EMISSAO = {chao = 0.49, ar = 0.40}                 -- s do clipe: asas no meio da abertura (manifesto_L8)
L.DURACAO_CLIPE = {chao = 1.6, ar = 1.3}

local Y = Vector3.yAxis
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end
local function raiz(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end
-- gira o vetor a em direcao a b no maximo ang (radianos)
local function girarPara(a, b, ang)
	local c = math.clamp(a:Dot(b), -1, 1); local th = math.acos(c)
	if th <= ang or th < 1e-4 then return b end
	local eixo = a:Cross(b); if eixo.Magnitude < 1e-5 then eixo = a:Cross(Y); if eixo.Magnitude < 1e-5 then eixo = a:Cross(Vector3.xAxis) end end
	return CFrame.fromAxisAngle(eixo.Unit, ang):VectorToWorldSpace(a).Unit
end
-- mundo: terreno e estruturas; sem personagens/criaturas (sao alvos, tratados a parte) nem a propria Wyvern
local function filtroMundo(m)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude
	local ex = {m}
	for _, pl in ipairs(Players:GetPlayers()) do if pl.Character then table.insert(ex, pl.Character) end end
	for _, d in ipairs(workspace:GetChildren()) do
		if d:IsA("Model") and (d:GetAttribute("FormaRegional") or d:GetAttribute("GuardiaoNinho") or d:FindFirstChildOfClass("Humanoid")) then table.insert(ex, d) end
	end
	local lab = workspace:FindFirstChild("Laboratorio_IA"); if lab then table.insert(ex, lab) end   -- alvos de teste (NPCs)
	local fx = workspace:FindFirstChild("VFX_Temporarios"); if fx then table.insert(ex, fx) end
	p.FilterDescendantsInstances = ex; return p
end
-- hitbox em X: ponto relativo ao centro do X, no plano perpendicular ao voo (eixos u = lado, v = cima do X)
local function noX(rel, dir, def, extra)
	local lado = dir:Cross(Y); if lado.Magnitude < 1e-3 then lado = dir:Cross(Vector3.xAxis) end; lado = lado.Unit
	local cima = lado:Cross(dir).Unit
	local u, v, w = rel:Dot(lado), rel:Dot(cima), rel:Dot(dir)
	if math.abs(w) > def.profundidade + extra then return false end
	if math.max(math.abs(u), math.abs(v)) > def.meiaLargura + extra then return false end
	local d1, d2 = math.abs(u - v) / math.sqrt(2), math.abs(u + v) / math.sqrt(2)     -- distancia as duas diagonais
	return math.min(d1, d2) <= def.espessura + extra
end

-- self = registro do Nucleo (metatabela N)
function L.executar(self, def, el, noAr, op)
	local N = getmetatable(self)
	local m = self.m
	-- so montado nesta etapa (como o Rasante): no 1o Play da E3 o guardiao selvagem (IA ChaseIntruder, que age mesmo com
	-- IA_Ativa=false) passou a disparar a Lamina no jogador assim que a vaga 3 entrou em habilidadesForma. IA selvagem usando
	-- o kit = pendente de decisao do usuario. (Recarga/energia ja foram cobradas pelo Nucleo; IA nao paga custo real.)
	if m:GetAttribute("Controlador") ~= "Montaria" then return end
	local modo = noAr and "ar" or "chao"
	op = op or {}
	self.pontaE = self.pontaE or osso(m, "strut_b_02_L"); self.pontaD = self.pontaD or osso(m, "strut_b_02_R")
	N.FX:FireAllClients({d = m, hab = "LaminaVento", fase = "preparo", noAr = noAr})
	local t0 = os.clock()
	local trilha = self:clipe(noAr and "LaminaVento_Ar" or "LaminaVento", false)
	if trilha then trilha.Looped = false; trilha:Play(0.12) end
	task.wait(L.EMISSAO[modo])
	if not m.Parent or m:GetAttribute("Incapacitado") then if trilha then trilha:Stop(0.2) end; return end
	-- ---- emissao: pontas das asas (pose animada) -> o X nasce a frente, no meio delas
	local f = self:frente()
	local pe = self.pontaE and self.pontaE.TransformedWorldCFrame.Position
	local pd = self.pontaD and self.pontaD.TransformedWorldCFrame.Position
	local b = self:boca()
	local meio = (pe and pd) and (pe + pd) / 2 or b
	local centro = Vector3.new(meio.X, (meio.Y + b.Y) / 2, meio.Z) + f * def.cruzaFrente
	-- ---- alvo do disparo
	local alvo = op.alvo and op.alvo.Parent and op.alvo or nil
	local mira = (typeof(op.direcao) == "Vector3" and op.direcao.Magnitude > 0.1) and op.direcao.Unit or f
	if not alvo then
		local melhor, mAng = nil, math.rad(def.coneAquisicao)
		for _, a in ipairs(self:alvosValidos()) do
			local v = N.pontoAlvo(a) - centro; local d = v.Magnitude
			if d > 1 and d <= def.alcance then
				local ang = math.acos(math.clamp(v.Unit:Dot(mira), -1, 1))
				if ang < mAng then melhor, mAng = a, ang end
			end
		end
		alvo = melhor
	end
	local dir = alvo and (N.pontoAlvo(alvo) - centro).Unit or mira
	-- no chao a mira inicial nao aponta para dentro do solo nem para o ceu (a perseguicao corrige depois)
	if not noAr and not alvo then dir = Vector3.new(dir.X, math.clamp(dir.Y, -0.25, 0.35), dir.Z).Unit end
	local id = tostring(m:GetAttribute("LaminaN") or 0) .. "_" .. tostring(math.floor(os.clock() * 1000))
	m:SetAttribute("LaminaN", (m:GetAttribute("LaminaN") or 0) + 1)
	m:SetAttribute("LaminaAlvo", alvo and alvo.Name or "-")                               -- depuracao/teste
	N.FX:FireAllClients({d = m, hab = "LaminaVento", fase = "emissao", id = id, pe = pe, pd = pd, centro = centro, dir = dir,
		vel = def.velocidade, alvo = alvo, noAr = noAr, meia = def.meiaLargura})
	task.spawn(L.voar, self, def, el, id, centro, dir, alvo)
	-- termina o clipe (ocupado ate o fim do gesto; o projetil segue sozinho)
	local resto = L.DURACAO_CLIPE[modo] - (os.clock() - t0) - 0.1
	if resto > 0 then task.wait(resto) end
end

function L.voar(self, def, el, id, pos, dir, alvo)
	local N = getmetatable(self)
	local m = self.m
	local fm = filtroMundo(m)
	local atingidos = {}
	local alvos, tLista = {}, -1
	local t, perc, tEnvio = 0, 0, 0
	local taxa = math.rad(def.taxaCurva)
	local acertos = 0
	local function fim(fase, p, normal)
		N.FX:FireAllClients({d = m, hab = "LaminaVento", fase = fase, id = id, pos = p, normal = normal})
		m:SetAttribute("LaminaAcertos", acertos); m:SetAttribute("LaminaFim", fase)
	end
	while m.Parent do
		local dt = RunService.Heartbeat:Wait()
		t += dt
		if t - tLista > 0.2 then alvos = self:alvosValidos(); tLista = t end
		-- persegue o alvo do disparo (missil): gira no maximo taxaCurva graus/s
		if alvo and alvo.Parent and not atingidos[alvo] and t <= def.duracao then
			local destino = N.pontoAlvo(alvo) - pos
			if destino.Magnitude > 0.5 then dir = girarPara(dir, destino.Unit, taxa * dt) end
		end
		local passo = def.velocidade * dt
		-- mundo: para no terreno/estrutura (esfera fina do miolo do X)
		local h = workspace:Spherecast(pos, def.raioMundo, dir * passo, fm)
		-- alvos ao longo do passo: subdivide para o X nao pular um alvo (passo ~1,3 studs a 80 studs/s)
		local sub = math.max(1, math.ceil(passo / 2))
		local fimAlvo = false
		for k = 1, sub do
			local c = pos + dir * (passo * k / sub)
			for _, a in ipairs(alvos) do
				if not atingidos[a] and a.Parent then
					local grande = a:GetAttribute("GuardiaoNinho") ~= nil
					local extra = grande and (a:GetAttribute("CorpoRaio") or 8) or 1.5
					-- testa a ALTURA do corpo (pes, centro, cabeca), nao so o centro: no 1o Play um alvo em pe na faixa ficava no
					-- "vao" abaixo do cruzamento do X (5,5 studs abaixo do centro) e o X passava por cima sem acertar
					local pa = N.pontoAlvo(a); local meiaAlt = grande and 4 or 2.5
					local dentro = false
					for _, k in ipairs({0, -meiaAlt, meiaAlt}) do
						if noX(pa + Y * k - c, dir, def, extra) then dentro = true; break end
					end
					if dentro then
						atingidos[a] = true; acertos += 1
						self:aplicar({a}, def.dano, "LaminaVento", def.intensidade, el)
						N.FX:FireAllClients({d = m, hab = "LaminaVento", fase = "impacto", id = id, pos = N.pontoAlvo(a), acertou = true})
						if a == alvo then fimAlvo = true end
					end
				end
			end
			if fimAlvo then break end
		end
		if fimAlvo then fim("acertou", N.pontoAlvo(alvo)); return end
		if h then fim("bateu", h.Position, h.Normal); return end
		pos += dir * passo; perc += passo
		if t >= def.duracao or perc >= def.alcance then fim("dissipa", pos); return end
		tEnvio += dt
		if tEnvio >= 0.1 then tEnvio = 0; N.FX:FireAllClients({d = m, hab = "LaminaVento", fase = "voo", id = id, pos = pos, dir = dir}) end
	end
end

return L
