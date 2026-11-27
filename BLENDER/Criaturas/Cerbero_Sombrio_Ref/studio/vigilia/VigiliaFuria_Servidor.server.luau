-- VigiliaFuria_Servidor (Script em ServerScriptService) - PROTOTIPO da Vigilia (passiva) e da Furia das Tres Cabecas (26/11).
-- Autoridade no servidor. FURIA (tecla F perto do Cerbero): recarga 30 s; clipe FuriaRugidoR4 (3 rugidos C/E/D); Rugido Infernal
-- no 1o rugido: inimigos a 25 studs -15% de velocidade e dano marcado -15% por 4 s; entra na Furia em 2,9 s: atributos Furia (cor roxa)
-- e MultDano 1,2 por 8 s (lidos pelo Sol Infernal e pela Investida); FuriaFade no ultimo 1,5 s; clipes FuriaLoop -> FuriaSaida.
-- VIGILIA (passiva): a cada 0,2 s procura modelos com atributo Invisivel a ate 15 studs da cabeca mais proxima; ao entrar:
-- pupilas das 3 cabecas brilham 1 s (todos veem) e o contorno aparece so para o dono; ao sair, o contorno some.
-- Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/vigilia/VigiliaFuria_Servidor.server.luau
local RS = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local pasta = RS:WaitForChild("VigiliaFuria")
local C = require(pasta:WaitForChild("VigiliaFuria_Config"))
local Pedido = pasta:WaitForChild("PedidoFuria")
local Efeito = pasta:WaitForChild("Efeito")

local cerbero = workspace:WaitForChild("Teste_Cerbero"):WaitForChild("Cerbero_Sombrio")
local okT, T = pcall(require, game.ServerStorage:WaitForChild("Cerbero_Piloto"):WaitForChild("TestePlayCerbero"))
if not okT then T = nil; warn("[VF] sem TestePlayCerbero: clipes nao tocam") end
local function tocar(nome, fade) if T then pcall(T.tocar, nome, fade) end end
local function log(...) print("[VF]", ...) end

cerbero:SetAttribute("ReducaoAtordoamento", C.ReducaoAtordoamento)
cerbero:SetAttribute("MultDano", 1)

local function dono()
	local id = cerbero:GetAttribute("DonoId")
	if id then return Players:GetPlayerByUserId(id) end
	local p = Players:GetPlayers()[1]
	if p then cerbero:SetAttribute("DonoId", p.UserId) end
	return p
end

local function modelosComHumanoid()
	local t = {}
	for _, d in ipairs(workspace:GetDescendants()) do
		if d:IsA("Humanoid") and d.Parent:IsA("Model") and d.Parent ~= cerbero then table.insert(t, d.Parent) end
	end
	return t
end

-- ===== FURIA =====
local estado = {ocupado = false, prontoEm = 0}
local function furia(quem)
	if estado.ocupado then log("Furia recusada: ja ativa") return end
	local agora = os.clock()
	if agora < estado.prontoEm then log(string.format("Furia recusada: recarga (faltam %.1f s)", estado.prontoEm - agora)) return end
	estado.ocupado = true
	log(string.format("FURIA: rugido + furia (energia %d)", C.Energia))
	tocar("Cerbero_FuriaRugidoR4", 0.15)
	local t0 = os.clock()
	local donoAtual = quem or dono()
	for i, r in ipairs(C.Rugidos) do
		task.delay(r[2], function()
			Efeito:FireAllClients("rugido", r[1])
			if i == 1 then
				cerbero:SetAttribute("Furia", true)          -- a cor muda no 1o rugido
				-- Rugido Infernal: inimigos a 25 studs (o dono fica de fora)
				local pc = cerbero:GetPivot().Position
				for _, m in ipairs(modelosComHumanoid()) do
					local raiz = m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart
					local eDono = donoAtual and donoAtual.Character == m
					if raiz and not eDono and (raiz.Position - pc).Magnitude <= C.RaioRugido then
						local h = m:FindFirstChildOfClass("Humanoid")
						local v0 = h.WalkSpeed
						h.WalkSpeed = v0 * (1 - C.RugidoLentidao)
						m:SetAttribute("MultDanoCausado", C.RugidoMultDano)
						m:SetAttribute("RugidoAte", workspace:GetServerTimeNow() + C.RugidoDuracao)
						Efeito:FireAllClients("debuff", m, C.RugidoDuracao)
						log(string.format("Rugido em %s (%.1f studs): velocidade %.1f -> %.1f, dano causado x%.2f por %d s",
							m.Name, (raiz.Position - pc).Magnitude, v0, h.WalkSpeed, C.RugidoMultDano, C.RugidoDuracao))
						task.delay(C.RugidoDuracao, function()
							if m.Parent then h.WalkSpeed = v0; m:SetAttribute("MultDanoCausado", nil); m:SetAttribute("RugidoAte", nil)
								log(m.Name .. ": efeito do Rugido terminou (velocidade " .. v0 .. ")") end
						end)
					end
				end
			end
		end)
	end
	task.delay(C.EntraFuria, function()
		cerbero:SetAttribute("MultDano", C.FuriaMultDano)
		log(string.format("entrou na Furia: dano x%.1f por %d s (velocidade de ataque x%.2f PENDENTE: sem mordida basica)", C.FuriaMultDano, C.FuriaDuracao, C.FuriaVelAtaque))
		tocar("Cerbero_FuriaLoop", 0.3)
	end)
	task.delay(C.EntraFuria + C.FuriaDuracao - C.FuriaFade, function() cerbero:SetAttribute("FuriaFade", true) end)
	task.delay(C.EntraFuria + C.FuriaDuracao, function()
		cerbero:SetAttribute("MultDano", 1); cerbero:SetAttribute("Furia", false); cerbero:SetAttribute("FuriaFade", nil)
		tocar("Cerbero_FuriaSaida", 0.2)
		task.delay(0.8, function() tocar("Cerbero_Repouso", 0.3) end)
		log(string.format("Furia terminou (%.1f s desde o rugido)", os.clock() - t0))
		estado.prontoEm = os.clock() + C.Recarga
		estado.ocupado = false
	end)
end

Pedido.OnServerEvent:Connect(function(plr)
	local raiz = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart")
	if not raiz or (raiz.Position - cerbero:GetPivot().Position).Magnitude > C.AlcanceComando then log(plr.Name, "Furia recusada: longe") return end
	task.spawn(furia, plr)
end)

-- ===== VIGILIA =====
local vistos = {}
local cabecas = {cerbero:FindFirstChild("CabecaC", true), cerbero:FindFirstChild("CabecaE", true), cerbero:FindFirstChild("CabecaD", true)}
task.spawn(function()
	while cerbero.Parent do
		task.wait(0.2)
		local d0 = dono()
		for _, m in ipairs(modelosComHumanoid()) do
			if m:GetAttribute("Invisivel") then
				local c = m:GetBoundingBox().Position
				local dmin = math.huge
				for _, b in ipairs(cabecas) do dmin = math.min(dmin, (b.WorldPosition - c).Magnitude) end
				local dentro = dmin <= C.RaioVigilia
				if dentro and not vistos[m] then
					vistos[m] = true
					log(string.format("Vigilia: %s (invisivel) detectado a %.1f studs da cabeca mais proxima", m.Name, dmin))
					Efeito:FireAllClients("pupilas", C.PupilasDuracao)
					if d0 then Efeito:FireClient(d0, "contorno", m, true) end
				elseif not dentro and vistos[m] then
					vistos[m] = nil
					log(string.format("Vigilia: %s saiu do alcance (%.1f studs)", m.Name, dmin))
					if d0 then Efeito:FireClient(d0, "contorno", m, false) end
				end
			end
		end
	end
end)

-- ensaio: workspace.Treino_Vigilia atributo "Furia" muda -> ativa a Furia sem jogador
local treino = workspace:FindFirstChild("Treino_Vigilia")
if treino then
	treino:GetAttributeChangedSignal("Furia"):Connect(function() if treino:GetAttribute("Furia") then task.spawn(furia, nil) end end)
	local inv = treino:FindFirstChild("Boneco_Invisivel")
	if inv then
		local base = inv:GetPivot()
		task.spawn(function()
			local t = 0
			while inv.Parent do
				t += task.wait()
				inv:PivotTo(base * CFrame.new(0, 0, math.sin(t * 0.55) * 13))   -- entra e sai do raio de 15 studs
			end
		end)
	end
end
log("pronto (Vigilia ativa; Furia na tecla F)")
