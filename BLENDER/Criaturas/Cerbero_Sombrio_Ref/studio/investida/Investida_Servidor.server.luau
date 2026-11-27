-- Investida_Servidor (Script em ServerScriptService) - PROTOTIPO da Investida Sombria do Cerbero, so no Cerbero-testes (26/11).
-- Autoridade no servidor: recarga, deslocamento (impulso 12 studs/0,5 s + boost +40% por 4 s), deteccao a frente,
-- porte do alvo (altura vs cernelha), passagem por cima (1,0x) ou parada com impacto + 3 mordidas (2,7x), parede, rastro
-- de 3 s que deixa 15% mais lento quem pisa. Um contato por Investida. O cliente so pede (tecla E) e desenha.
-- Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/investida/Investida_Servidor.server.luau
local RS = game:GetService("ReplicatedStorage")
local Run = game:GetService("RunService")
local Players = game:GetService("Players")

local pasta = RS:WaitForChild("InvestidaSombria")
local C = require(pasta:WaitForChild("Investida_Config"))
local Pedido = pasta:WaitForChild("Pedido")
local Direcao = pasta:WaitForChild("Direcao")
local Efeito = pasta:WaitForChild("Efeito")

local cerbero = workspace:WaitForChild("Teste_Cerbero"):WaitForChild("Cerbero_Sombrio")
local okT, T = pcall(require, game.ServerStorage:WaitForChild("Cerbero_Piloto"):WaitForChild("TestePlayCerbero"))
if not okT then T = nil; warn("[INV] sem TestePlayCerbero: clipes nao tocam") end
local function tocar(nome, fade) if T then pcall(T.tocar, nome, fade) end end

local estado = {ocupado = false, prontoEm = 0, dono = nil, dirAlvo = nil}
local function log(...) print("[INV]", ...) end

local function modeloComHumanoid(inst)
	local m = inst and inst:FindFirstAncestorOfClass("Model")
	while m do
		local h = m:FindFirstChildOfClass("Humanoid")
		if h then return m, h end
		m = m.Parent and m.Parent:FindFirstAncestorOfClass("Model")
	end
	return nil
end

local function aplicarDano(m, h, mult, tipo)
	if not h or h.Health <= 0 then return end
	local v = C.DanoBase * mult
	h:TakeDamage(v)
	log(string.format("%s recebeu %.1f (%s) -> vida %.1f/%.0f", m.Name, v, tipo, h.Health, h.MaxHealth))
end

-- porte = altura do corpo (caixa do modelo; bonecos e jogadores nao tem efeitos de particula na caixa)
local function porte(m) local _, s = m:GetBoundingBox(); return s.Y end

local function yawDe(look) return math.atan2(-look.X, -look.Z) end

local function virarPara(ponto, maxAng)
	local cf = cerbero:GetPivot(); local p = cf.Position
	local d = Vector3.new(ponto.X - p.X, 0, ponto.Z - p.Z)
	if d.Magnitude < 1 then return end
	local atual = Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z).Unit
	local alvo = d.Unit
	local ang = math.acos(math.clamp(atual:Dot(alvo), -1, 1))
	if ang < 1e-3 then return end
	local giro = math.min(ang, maxAng) * (atual:Cross(alvo).Y >= 0 and 1 or -1)
	cerbero:PivotTo(CFrame.new(p) * CFrame.Angles(0, yawDe(atual) + giro, 0))
end

-- alvo mais proximo no corredor a frente: devolve modelo, humanoid e distancia do pivo ate a face proxima do alvo
local function procurarFrente(excluir)
	local cf = cerbero:GetPivot()
	local comp = C.GatilhoSobre + 4
	local op = OverlapParams.new()
	op.FilterType = Enum.RaycastFilterType.Exclude
	op.FilterDescendantsInstances = excluir
	local melhor, melhorH, melhorD
	local vistos = {}
	for _, parte in ipairs(workspace:GetPartBoundsInBox(cf * CFrame.new(0, 9, -comp / 2), Vector3.new(C.LarguraBusca * 2, 18, comp), op)) do
		local m, h = modeloComHumanoid(parte)
		if m and not vistos[m] and h.Health > 0 then
			vistos[m] = true
			local bcf, bs = m:GetBoundingBox()
			local meia = (bs.X * math.abs(bcf.RightVector:Dot(cf.LookVector)) + bs.Z * math.abs(bcf.LookVector:Dot(cf.LookVector))) / 2
			local d = (bcf.Position - cf.Position):Dot(cf.LookVector) - meia
			if d > -2 and (not melhorD or d < melhorD) then melhor, melhorH, melhorD = m, h, d end
		end
	end
	return melhor, melhorH, melhorD
end

local function paredeFrente(excluir, passo)
	local cf = cerbero:GetPivot()
	local rp = RaycastParams.new()
	rp.FilterType = Enum.RaycastFilterType.Exclude
	rp.FilterDescendantsInstances = excluir
	local r = workspace:Blockcast(cf * CFrame.new(0, 9, -2), Vector3.new(8, 10, 1), cf.LookVector * (C.GatilhoParede + passo), rp)
	if r and r.Instance.CanCollide and not modeloComHumanoid(r.Instance) then return r end
	return nil
end

-- ===== rastro (3 s, -15% de velocidade para quem pisa; o dono fica de fora) =====
local rastro = {}
local donoRastro = nil
local function marcarRastro(pos, yaw, roxo)
	table.insert(rastro, {pos = pos, expira = os.clock() + C.RastroDuracao})
	Efeito:FireAllClients("rastro", pos, yaw, roxo, C.RastroDuracao)
end
local lentos = {}   -- [humanoid] = {velocidadeOriginal, modelo}
task.spawn(function()
	while true do
		task.wait(0.2)
		local agora = os.clock()
		for i = #rastro, 1, -1 do if rastro[i].expira < agora then table.remove(rastro, i) end end
		local candidatos = {}
		for _, plr in ipairs(Players:GetPlayers()) do if plr.Character and plr ~= donoRastro then table.insert(candidatos, plr.Character) end end
		local treino = workspace:FindFirstChild("Treino_Investida")
		if treino then for _, m in ipairs(treino:GetChildren()) do if m:IsA("Model") then table.insert(candidatos, m) end end end
		for _, m in ipairs(candidatos) do
			local h = m:FindFirstChildOfClass("Humanoid")
			local raiz = m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart
			if h and raiz then
				local pisando = false
				for _, r in ipairs(rastro) do
					local d = Vector3.new(raiz.Position.X - r.pos.X, 0, raiz.Position.Z - r.pos.Z).Magnitude
					if d <= C.RastroRaio and raiz.Position.Y - r.pos.Y < 12 then pisando = true; break end
				end
				if pisando and not lentos[h] then
					lentos[h] = {h.WalkSpeed, m}
					h.WalkSpeed = h.WalkSpeed * (1 - C.RastroLentidao)
					m:SetAttribute("NoRastro", true)
					log(string.format("%s pisou no rastro: velocidade %.1f -> %.1f (-15%%)", m.Name, lentos[h][1], h.WalkSpeed))
				elseif not pisando and lentos[h] then
					h.WalkSpeed = lentos[h][1]; m:SetAttribute("NoRastro", nil)
					log(m.Name .. " saiu do rastro: velocidade restaurada " .. h.WalkSpeed)
					lentos[h] = nil
				end
			end
		end
	end
end)

-- ===== a investida =====
local function investir(dono, ponto)
	if estado.ocupado then log("recusado: ja em uso") return end
	local agora = os.clock()
	if agora < estado.prontoEm then log(string.format("recusado: recarga (faltam %.1f s)", estado.prontoEm - agora)) return end
	estado.ocupado = true; estado.dono = dono; estado.dirAlvo = nil; donoRastro = dono
	local roxo = cerbero:GetAttribute("Furia") == true
	log(string.format("investida: energia %d%s", C.Energia, roxo and " FURIA(roxo)" or ""))
	if ponto then virarPara(ponto, math.pi) end
	local excl = {cerbero, workspace:FindFirstChild("VFX_SolInfernal"), dono and dono.Character or nil}

	tocar("Cerbero_InvestidaR3", 0.1)
	Efeito:FireAllClients("inicio", cerbero, roxo)
	local t0 = os.clock()
	local fimBoost = C.ImpulsoInicio + C.ImpulsoDuracao + C.BoostDuracao
	local ultimoRastro = cerbero:GetPivot().Position
	local acertou, correndo = false, false
	local sobre = nil          -- {modelo, h, inicio, danoFeito}
	local motivo = "fim do boost"

	while true do
		local dt = Run.Heartbeat:Wait()
		local t = os.clock() - t0
		if t >= fimBoost and not sobre then break end
		local v
		if sobre then
			v = C.VelocidadeSobre
			local ts = os.clock() - sobre.inicio
			if not sobre.danoFeito and ts >= C.TempoApiceSobre then
				sobre.danoFeito = true
				aplicarDano(sobre.modelo, sobre.h, C.MultPassagem, "passagem por cima 1,0x")
				Efeito:FireAllClients("passagem", sobre.modelo, roxo)
			end
			if ts >= C.DuracaoSobre then
				sobre = nil
				if t < fimBoost then tocar("Cerbero_Corrida", 0.2) end
			end
		elseif t < C.ImpulsoInicio then
			v = 0
		elseif t < C.ImpulsoInicio + C.ImpulsoDuracao then
			v = C.ImpulsoDistancia / C.ImpulsoDuracao
		else
			v = C.VelocidadeBase * C.BoostMult
			if not correndo then correndo = true; tocar("Cerbero_Corrida", 0.25) end
			if estado.dirAlvo then virarPara(estado.dirAlvo, math.rad(C.CurvaGrausPorSeg) * dt) end
		end

		if v > 0 then
			local passo = v * dt
			local parede = paredeFrente(excl, passo)
			if parede then
				motivo = "parede (" .. parede.Instance.Name .. ")"
				Efeito:FireAllClients("parede", parede.Position, roxo)
				break
			end
			if not acertou and not sobre then
				local m, h, d = procurarFrente(excl)
				if m then
					local alt = porte(m)
					local pequeno = alt <= C.Cernelha * C.LimitePequeno
					if pequeno and d <= C.GatilhoSobre then
						acertou = true
						log(string.format("%s: altura %.2f (<= %.2f) -> PASSA POR CIMA", m.Name, alt, C.Cernelha * C.LimitePequeno))
						sobre = {modelo = m, h = h, inicio = os.clock(), danoFeito = false}
						tocar("Cerbero_InvestidaSobre", 0.1)
					elseif not pequeno and d <= C.GatilhoImpacto then
						acertou = true
						log(string.format("%s: altura %.2f (> %.2f) -> PARA E MORDE", m.Name, alt, C.Cernelha * C.LimitePequeno))
						motivo = "impacto em " .. m.Name
						tocar("Cerbero_InvestidaImpacto", 0.08)
						Efeito:FireAllClients("impacto", m, roxo)
						local ti = os.clock()
						local feitos = {false, false, false, false}
						while os.clock() - ti < C.DuracaoImpacto do
							Run.Heartbeat:Wait()
							local ts = os.clock() - ti
							if not feitos[1] and ts >= C.TempoImpacto then feitos[1] = true; aplicarDano(m, h, C.MultImpacto, "impacto 0,6x") end
							for i, tm in ipairs(C.TemposMordida) do
								if not feitos[i + 1] and ts >= tm then
									feitos[i + 1] = true
									aplicarDano(m, h, C.MultMordida, "mordida " .. ({"C", "E", "D"})[i] .. " 0,7x")
									Efeito:FireAllClients("mordida", m, roxo, i)
								end
							end
						end
						break
					end
				end
			end
			local cf = cerbero:GetPivot()
			cerbero:PivotTo(cf + cf.LookVector * passo)
			local p = cerbero:GetPivot().Position
			if (p - ultimoRastro).Magnitude >= C.RastroPasso then
				ultimoRastro = p
				marcarRastro(p, yawDe(cerbero:GetPivot().LookVector), roxo)
			end
		end
	end
	if not motivo:find("^impacto") then tocar("Cerbero_Repouso", 0.35) else tocar("Cerbero_Repouso", 0.2) end
	log(string.format("investida terminou: %s (%.1f s)", motivo, os.clock() - t0))
	Efeito:FireAllClients("fim", cerbero)
	estado.prontoEm = os.clock() + C.Recarga
	estado.ocupado = false; estado.dono = nil
	task.delay(C.RastroDuracao, function() if not estado.ocupado then donoRastro = nil end end)
end

-- Tecla de teste (validada aqui) e direcao livre durante o boost
Pedido.OnServerEvent:Connect(function(plr, ponto)
	local raiz = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart")
	if not raiz then return end
	if (raiz.Position - cerbero:GetPivot().Position).Magnitude > C.AlcanceComando then log(plr.Name, "recusado: longe do Cerbero") return end
	if typeof(ponto) ~= "Vector3" then ponto = nil end
	task.spawn(investir, plr, ponto)
end)
Direcao.OnServerEvent:Connect(function(plr, ponto)
	if estado.ocupado and estado.dono == plr and typeof(ponto) == "Vector3" then estado.dirAlvo = ponto end
end)

-- Ensaio automatico: workspace.Treino_Investida, atributo "Investir" muda -> investe para a frente
local treino = workspace:FindFirstChild("Treino_Investida")
if treino then
	treino:GetAttributeChangedSignal("Investir"):Connect(function()
		local v = treino:GetAttribute("Investir")
		if not v or v == "" then return end
		local cf = cerbero:GetPivot()
		task.spawn(investir, nil, cf.Position + cf.LookVector * 30)
	end)
	-- o boneco Boneco_CruzaRastro e levado para cima do rastro pelo script de ensaio (depois que o Cerbero passa)
end
log("pronto (recarga " .. C.Recarga .. " s, energia " .. C.Energia .. ")")
