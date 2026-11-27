-- Mordida_Servidor (Script em ServerScriptService) - PROTOTIPO da mordida basica do Cerbero (27/11).
-- Clique (validado aqui): escolhe a cabeca cuja boca esta mais perto do alvo, toca o clipe em camada (MordidaC/E/D, Action2,
-- nao para a locomocao) e, no instante do contato, testa uma esfera na frente da boca: 17 x MultDano (Furia +20%), um acerto
-- por mordida. Intervalo 0,8 s. Bloqueada pelo atributo MordidaBloqueada (carga do Sol, salto/impacto da Investida, rugido).
-- Furia sustentada (atributo FuriaSustentada): cada cabeca morde sozinha o alvo mais perto dela, 15% mais rapido.
-- Obs.: no servidor os ossos ficam na pose de repouso (a animacao so aparece no cliente); o contato usa a boca em repouso + alcance.
-- Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/mordida/Mordida_Servidor.server.luau
local RS = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local pasta = RS:WaitForChild("MordidaCerbero")
local C = require(pasta:WaitForChild("Mordida_Config"))
local Pedido = pasta:WaitForChild("PedidoMordida")
local Efeito = pasta:WaitForChild("Efeito")

local cerbero = workspace:WaitForChild("Teste_Cerbero"):WaitForChild("Cerbero_Sombrio")
local okT, T = pcall(require, game.ServerStorage:WaitForChild("Cerbero_Piloto"):WaitForChild("TestePlayCerbero"))
if not okT then T = nil; warn("[MOR] sem TestePlayCerbero: clipes nao tocam") end
local function log(...) print("[MOR]", ...) end

local mand = {}
for _, k in ipairs(C.Cabecas) do mand[k] = cerbero:FindFirstChild("Mandibula" .. k, true) end

local function modeloComHumanoid(inst)
	local m = inst and inst:FindFirstAncestorOfClass("Model")
	while m do
		local h = m:FindFirstChildOfClass("Humanoid")
		if h then return m, h end
		m = m.Parent and m.Parent:FindFirstAncestorOfClass("Model")
	end
	return nil
end

local function dono()
	local id = cerbero:GetAttribute("DonoId")
	return id and Players:GetPlayerByUserId(id) or Players:GetPlayers()[1]
end

local function pontoBoca(k)
	local cf = cerbero:GetPivot()
	return mand[k].WorldPosition + cf.LookVector * C.Alcance
end

-- inimigos (modelos com Humanoid vivos), sem o Cerbero e sem o dono
local function inimigos()
	local d = dono()
	local t = {}
	for _, x in ipairs(workspace:GetDescendants()) do
		if x:IsA("Humanoid") and x.Health > 0 and x.Parent:IsA("Model") and x.Parent ~= cerbero and not (d and d.Character == x.Parent) then
			table.insert(t, x.Parent)
		end
	end
	return t
end

-- distancia do ponto ate a caixa do modelo (0 se dentro)
local function distCaixa(m, p)
	local cf, s = m:GetBoundingBox()
	local l = cf:PointToObjectSpace(p)
	local q = Vector3.new(math.max(math.abs(l.X) - s.X / 2, 0), math.max(math.abs(l.Y) - s.Y / 2, 0), math.max(math.abs(l.Z) - s.Z / 2, 0))
	return q.Magnitude
end

local proxima = {C = 0, E = 0, D = 0}
local globalProxima = 0

local function morder(k, alvoPedido, vel)
	vel = vel or 1
	if T then pcall(function() T.faixa("Cerbero_Mordida" .. k):Play(0.05, 1, vel) end) end
	Efeito:FireAllClients("mordida", k)
	task.delay(C.TempoContato / vel, function()
		if cerbero:GetAttribute("MordidaBloqueada") then return end
		local p = pontoBoca(k)
		local d0 = dono()
		local op = OverlapParams.new()
		op.FilterType = Enum.RaycastFilterType.Exclude
		op.FilterDescendantsInstances = {cerbero, d0 and d0.Character or nil}
		local acertado
		for _, parte in ipairs(workspace:GetPartBoundsInRadius(p, C.RaioContato, op)) do
			local m, h = modeloComHumanoid(parte)
			if m and h.Health > 0 then
				if m == alvoPedido then acertado = m; break end
				acertado = acertado or m
			end
		end
		if acertado then
			local h = acertado:FindFirstChildOfClass("Humanoid")
			local md = cerbero:GetAttribute("MultDano") or 1
			local v = C.Dano * md
			h:TakeDamage(v)
			Efeito:FireAllClients("acerto", p, cerbero:GetAttribute("Furia") == true)
			log(string.format("mordida %s acertou %s: %.1f%s -> vida %.1f/%.0f", k, acertado.Name, v, md ~= 1 and string.format(" (x%.1f Furia)", md) or "", h.Health, h.MaxHealth))
		else
			log("mordida " .. k .. " no ar (nada ao alcance da boca)")
		end
	end)
end

-- clique: cabeca mais perto do alvo
local function pedido(plr, alvoInst, ponto)
	if cerbero:GetAttribute("MordidaBloqueada") then log("mordida recusada: bloqueada (" .. tostring(cerbero:GetAttribute("PoderAtivo")) .. ")") return end
	if cerbero:GetAttribute("FuriaSustentada") then log("mordida manual ignorada: na Furia as cabecas mordem sozinhas") return end
	local agora = os.clock()
	if agora < globalProxima then return end
	local alvo, tp
	if typeof(alvoInst) == "Instance" then
		local m = modeloComHumanoid(alvoInst)
		if m and m ~= cerbero and not (plr and plr.Character == m) then alvo = m end
	end
	if not alvo then   -- sem alvo sob o mouse: inimigo mais perto das bocas
		local melhor
		for _, m in ipairs(inimigos()) do
			for _, k in ipairs(C.Cabecas) do
				local d = distCaixa(m, pontoBoca(k))
				if d <= C.BuscaAlvo and (not melhor or d < melhor) then melhor, alvo = d, m end
			end
		end
	end
	if alvo then tp = alvo:GetBoundingBox().Position elseif typeof(ponto) == "Vector3" then tp = ponto end
	local k = "C"
	if tp then
		local melhor
		for _, kk in ipairs(C.Cabecas) do
			local d = (pontoBoca(kk) - tp).Magnitude
			if not melhor or d < melhor then melhor, k = d, kk end
		end
	end
	globalProxima = agora + C.Intervalo
	log(string.format("clique: cabeca %s morde (alvo %s)", k, alvo and alvo.Name or "nenhum"))
	morder(k, alvo, 1)
end

Pedido.OnServerEvent:Connect(function(plr, alvoInst, ponto)
	local raiz = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart")
	if not raiz or (raiz.Position - cerbero:GetPivot().Position).Magnitude > C.AlcanceComando then return end
	pedido(plr, alvoInst, ponto)
end)

-- Furia sustentada: as 3 cabecas mordem sozinhas, cada uma o alvo mais perto da sua boca, 15% mais rapido
task.spawn(function()
	while cerbero.Parent do
		task.wait(0.1)
		if cerbero:GetAttribute("FuriaSustentada") and not cerbero:GetAttribute("MordidaBloqueada") then
			local agora = os.clock()
			local lista = inimigos()
			for _, k in ipairs(C.Cabecas) do
				if agora >= proxima[k] then
					local p, alvo, melhor = pontoBoca(k), nil, nil
					for _, m in ipairs(lista) do
						local d = distCaixa(m, p)
						if d <= C.BuscaFuria and (not melhor or d < melhor) then melhor, alvo = d, m end
					end
					if alvo then
						proxima[k] = agora + C.Intervalo / C.VelAtaqueFuria
						log(string.format("Furia: cabeca %s morde sozinha %s", k, alvo.Name))
						morder(k, alvo, C.VelAtaqueFuria)
					end
				end
			end
		end
	end
end)

-- ensaio: workspace.Treino_Mordida atributo "Morder" (contador) -> um clique sem alvo
local treino = workspace:FindFirstChild("Treino_Mordida")
if treino then
	treino:GetAttributeChangedSignal("Morder"):Connect(function() pedido(nil, nil, nil) end)
end
log("pronto (intervalo " .. C.Intervalo .. " s)")
