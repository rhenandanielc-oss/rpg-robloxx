-- SolInfernal_Servidor (Script em ServerScriptService) - PROTOTIPO do Sol Infernal do Cerbero Sombrio, so no Cerbero-testes (26/11).
-- Autoridade no servidor: recarga, mira (alvo travado -> ponto do mouse -> frente), voo teleguiado, colisao com obstaculos,
-- acerto, explosao e queimadura. O cliente so pede (tecla de teste) e desenha (SolInfernal_Cliente).
-- Regras aprovadas (19/11): carga 3,35 s; 30 studs/s; curva 130 graus/s; alcance 50; acerto 8; alvo 1,8x;
-- explosao raio 12 com 1,0x nos demais (sem acumular no alvo); queimadura leve 3 s (0,1x/s, 26/11); recarga 14 s; energia 35.
-- Nao atravessa obstaculos (spherecast). Uma bola so. Furia (atributo Furia no Cerbero) = bola roxa, mesmos numeros.
-- Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/sol/SolInfernal_Servidor.server.luau
local RS = game:GetService("ReplicatedStorage")
local Run = game:GetService("RunService")
local Players = game:GetService("Players")

local pasta = RS:WaitForChild("SolInfernal")
local C = require(pasta:WaitForChild("SolInfernal_Config"))
local Pedido = pasta:WaitForChild("Pedido")
local Explodiu = pasta:WaitForChild("Explodiu")
local Queima = pasta:WaitForChild("Queima")

local cerbero = workspace:WaitForChild("Teste_Cerbero"):WaitForChild("Cerbero_Sombrio")
local okT, T = pcall(require, game.ServerStorage:WaitForChild("Cerbero_Piloto"):WaitForChild("TestePlayCerbero"))
if not okT then T = nil; warn("[SOL] sem TestePlayCerbero: clipe nao toca", T) end

local vfx = workspace:FindFirstChild("VFX_SolInfernal") or Instance.new("Folder")
vfx.Name = "VFX_SolInfernal"; vfx.Parent = workspace

local estado = {ocupado = false, prontoEm = 0}
local function log(...) print("[SOL]", ...) end

local function modeloComHumanoid(inst)
	local m = inst and inst:FindFirstAncestorOfClass("Model")
	while m do
		local h = m:FindFirstChildOfClass("Humanoid")
		if h then return m, h end
		m = m.Parent and m.Parent:FindFirstAncestorOfClass("Model")
	end
	return nil
end

local function centro(m)
	local r = m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart
	return r and r.Position
end

local function aplicarDano(m, h, valor, tipo)
	if not h or h.Health <= 0 then return end
	local md = cerbero:GetAttribute("MultDano") or 1      -- Furia: +20% (VigiliaFuria_Servidor)
	if md ~= 1 then valor = valor * md; tipo = tipo .. string.format(" x%.1f Furia", md) end
	h:TakeDamage(valor)
	log(string.format("%s recebeu %.1f (%s) -> vida %.1f/%.0f", m.Name, valor, tipo, h.Health, h.MaxHealth))
end

local function queimar(m, h, roxo)
	Queima:FireAllClients(m, C.QueimaDuracao, roxo)
	task.spawn(function()
		for i = 1, C.QueimaDuracao do
			task.wait(1)
			if not m.Parent then return end
			aplicarDano(m, h, C.DanoBase * C.QueimaPorSegundo, "queimadura " .. i .. "/" .. C.QueimaDuracao)
		end
	end)
end

local function explodir(pos, principal, roxo, motivo, dono, dir)
	Explodiu:FireAllClients(pos, roxo, C.RaioExplosao)
	log(string.format("explodiu (%s) em %.1f, %.1f, %.1f", motivo, pos.X, pos.Y, pos.Z))
	local atingidos = {}
	if principal then
		local h = principal:FindFirstChildOfClass("Humanoid")
		atingidos[principal] = true
		aplicarDano(principal, h, C.DanoBase * C.MultAlvo, "alvo atingido 1,8x")
		queimar(principal, h, roxo)
	end
	-- explosao: 1,0x nos demais dentro do raio (o dono e o proprio Cerbero ficam de fora)
	local op = OverlapParams.new()
	op.FilterType = Enum.RaycastFilterType.Exclude
	op.FilterDescendantsInstances = {cerbero, vfx, dono and dono.Character or nil}
	-- a explosao tambem nao passa por paredes: linha de visada do ponto (recuado 1,5 stud) ate o centro de cada vitima
	local origem = dir and (pos - dir * 1.5) or pos
	for _, parte in ipairs(workspace:GetPartBoundsInRadius(pos, C.RaioExplosao, op)) do
		local m, h = modeloComHumanoid(parte)
		if m and not atingidos[m] then
			atingidos[m] = true
			local c = centro(m)
			local rp = RaycastParams.new()
			rp.FilterType = Enum.RaycastFilterType.Exclude
			rp.FilterDescendantsInstances = {cerbero, vfx, m, dono and dono.Character or nil}
			local bloq = c and workspace:Raycast(origem, c - origem, rp)
			if bloq and not modeloComHumanoid(bloq.Instance) then
				log(m.Name .. " protegido pela parede (" .. bloq.Instance.Name .. ")")
			else
				aplicarDano(m, h, C.DanoBase * C.MultExplosao, "explosao 1,0x")
			end
		end
	end
end

local function lancar(dono, alvo, pontoMira)
	if estado.ocupado then log("recusado: ja carregando") return end
	local agora = os.clock()
	if agora < estado.prontoEm then log(string.format("recusado: recarga (faltam %.1f s)", estado.prontoEm - agora)) return end
	estado.ocupado = true
	local roxo = cerbero:GetAttribute("Furia") == true
	log(string.format("lancando: alvo=%s ponto=%s energia=%d%s", alvo and alvo.Name or "nenhum", tostring(pontoMira), C.Energia, roxo and " FURIA(roxo)" or ""))

	-- vira para o alvo (ou para o ponto do mouse)
	local p0 = cerbero:GetPivot().Position
	local mira = (alvo and centro(alvo)) or pontoMira
	if mira then
		local d = Vector3.new(mira.X - p0.X, 0, mira.Z - p0.Z)
		if d.Magnitude > 1 then cerbero:PivotTo(CFrame.lookAt(p0, p0 + d)) end
	end
	if T then pcall(T.tocar, "Cerbero_BolaInfernalR2", 0.15) end

	local rp = cerbero.PrimaryPart
	local bola = Instance.new("Part")
	bola.Name = "SolInfernal_Bola"; bola.Shape = Enum.PartType.Ball; bola.Size = Vector3.one
	bola.Anchored = true; bola.CanCollide = false; bola.CanQuery = false; bola.CanTouch = false
	bola.Transparency = 1; bola.CastShadow = false
	bola:SetAttribute("Escala", 0); bola:SetAttribute("Roxo", roxo); bola:SetAttribute("Raio", C.RaioVisual)
	bola.CFrame = rp.CFrame * CFrame.new(C.OrigemLocal)
	bola.Parent = vfx

	-- CARGA (telegrafada): a bola cresce entre carga_inicio e carga_max, presa diante das cabecas
	local t0 = os.clock()
	local ultimaEscala = -1
	while os.clock() - t0 < C.Carga do
		Run.Heartbeat:Wait()
		if cerbero:GetAttribute("Atordoado") or not cerbero.Parent then
			log("carga INTERROMPIDA: bola desfeita, recarga pela metade")
			bola:Destroy()
			estado.prontoEm = os.clock() + C.Recarga * C.RecargaInterrompida
			estado.ocupado = false
			return
		end
		local t = os.clock() - t0
		local esc = math.clamp((t - C.CargaInicio) / (C.CargaMax - C.CargaInicio), 0, 1)
		if math.abs(esc - ultimaEscala) >= 0.04 then bola:SetAttribute("Escala", esc); ultimaEscala = esc end
		bola.CFrame = rp.CFrame * CFrame.new(C.OrigemLocal)
	end
	bola:SetAttribute("Escala", 1); bola:SetAttribute("Voando", true)
	task.delay(C.DuracaoClipe - C.Carga, function() if T then pcall(T.tocar, "Cerbero_Repouso", 0.3) end end)

	-- VOO teleguiado
	local pos = bola.Position
	local frente = rp.CFrame.LookVector
	local destino = (alvo and centro(alvo)) or pontoMira or (pos + frente * 10)
	local dir = (destino - pos).Magnitude > 0.1 and (destino - pos).Unit or frente
	local percorrido = 0
	local rparams = RaycastParams.new()
	rparams.FilterType = Enum.RaycastFilterType.Exclude
	rparams.FilterDescendantsInstances = {cerbero, vfx, dono and dono.Character or nil}
	local op = OverlapParams.new()
	op.FilterType = Enum.RaycastFilterType.Exclude
	op.FilterDescendantsInstances = {cerbero, vfx, dono and dono.Character or nil}
	local maxCurva = math.rad(C.CurvaGrausPorSeg)

	while true do
		local dt = Run.Heartbeat:Wait()
		if alvo and alvo.Parent then
			local tp = centro(alvo)
			if tp then
				local quer = (tp - pos).Unit
				local ang = math.acos(math.clamp(dir:Dot(quer), -1, 1))
				if ang > 1e-4 then dir = dir:Lerp(quer, math.min(1, (maxCurva * dt) / ang)).Unit end
			end
		elseif alvo then
			alvo = nil      -- alvo sumiu/morreu: segue reto
		end
		local passo = dir * math.min(C.Velocidade * dt, C.Alcance - percorrido)
		-- 1) obstaculo no caminho (nao atravessa paredes nem terreno)
		local hit = workspace:Spherecast(pos, C.RaioColisao, passo, rparams)
		local novo = hit and hit.Position or (pos + passo)
		-- 2) criatura/jogador ao alcance do acerto (raio 8) - a bola so explode uma vez
		local principal
		for _, parte in ipairs(workspace:GetPartBoundsInRadius(novo, C.RaioAcerto, op)) do
			local m = modeloComHumanoid(parte)
			if m then
				if m == alvo then principal = m; break end
				principal = principal or m
			end
		end
		pos = novo; bola.Position = pos
		percorrido += passo.Magnitude
		if principal then explodir(pos, principal, roxo, "acerto em " .. principal.Name, dono, dir) break end
		if hit then
			local m = modeloComHumanoid(hit.Instance)
			explodir(pos, m, roxo, m and ("acerto em " .. m.Name) or ("obstaculo " .. hit.Instance:GetFullName()), dono, dir)
			break
		end
		if percorrido >= C.Alcance - 1e-3 then explodir(pos, nil, roxo, "fim do alcance", dono, dir) break end
	end
	bola:Destroy()
	estado.prontoEm = os.clock() + C.Recarga
	estado.ocupado = false
end

-- Tecla de teste do jogador (validada aqui: distancia ao Cerbero, alvo valido e ao alcance)
Pedido.OnServerEvent:Connect(function(plr, alvoInst, ponto)
	local ch = plr.Character
	local raiz = ch and ch:FindFirstChild("HumanoidRootPart")
	if not raiz then return end
	local pc = cerbero:GetPivot().Position
	if (raiz.Position - pc).Magnitude > C.AlcanceComando then log(plr.Name, "recusado: longe do Cerbero") return end
	local alvo
	if typeof(alvoInst) == "Instance" then
		local m = modeloComHumanoid(alvoInst)
		if m and m ~= ch and m ~= cerbero and centro(m) and (centro(m) - pc).Magnitude <= C.AlcanceMira then alvo = m end
	end
	if typeof(ponto) ~= "Vector3" or (ponto - pc).Magnitude > 500 then ponto = nil end
	task.spawn(lancar, plr, alvo, ponto)
end)

-- Ensaio automatico: workspace.Treino_SolInfernal com atributo "Disparar" = nome do boneco (ou "frente")
local treino = workspace:FindFirstChild("Treino_SolInfernal")
if treino then
	treino:GetAttributeChangedSignal("Disparar"):Connect(function()
		local nome = treino:GetAttribute("Disparar")
		if not nome or nome == "" then return end
		local alvo = treino:FindFirstChild(nome)
		task.spawn(lancar, nil, alvo, nil)
	end)
	-- boneco que anda de um lado para o outro
	local andando = treino:FindFirstChild("Boneco_Andando")
	if andando then
		local base = andando:GetPivot()
		task.spawn(function()
			local t = 0
			while andando.Parent do
				t += Run.Heartbeat:Wait()
				andando:PivotTo(base * CFrame.new(math.sin(t * 0.5) * 12, 0, 0))
			end
		end)
	end
	-- leva o jogador para perto do Cerbero (o SpawnLocation do place fica longe)
	local function levar(chr)
		if treino:GetAttribute("LevarJogador") then
			task.wait(0.5)
			chr:PivotTo(CFrame.new(32, 4, 74) * CFrame.Angles(0, math.rad(35), 0))
		end
	end
	local function ligar(plr)
		plr.CharacterAdded:Connect(levar)
		if plr.Character then task.spawn(levar, plr.Character) end
	end
	Players.PlayerAdded:Connect(ligar)
	for _, plr in ipairs(Players:GetPlayers()) do ligar(plr) end
end
log("pronto (recarga " .. C.Recarga .. " s, energia " .. C.Energia .. ")")
