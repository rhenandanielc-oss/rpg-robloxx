-- Controle_Cliente (Script com RunContext = Client, Workspace.Teste_LoboArtico) - controle de ENSAIO do Lobo Artico (16/11).
-- So manda a INTENCAO ao servidor (Controle_Servidor decide tudo): direcao no plano relativa a camera + marcha pedida.
-- PC: F assume/solta | WASD direcao | Shift (segurar) corre | Ctrl (segurar) anda | H Uivo.
-- Celular: botoes de toque do ContextActionService (Lobo / Correr / Uivo) + o direcional padrao (NAO testado em celular).
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local CAS = game:GetService("ContextActionService")
local UIS = game:GetService("UserInputService")
local jogador = Players.LocalPlayer
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local rede = pasta:WaitForChild("Rede_Controle")
local raiz = lobo:WaitForChild("RootPart")
-- r2: este place nao tem PlayerModule (PlayerScripts customizados) -> usa o PlayerModule se existir; senao WASD direto
-- e, para toque/controle, o Humanoid.MoveDirection (ja em espaco do mundo).
local pm = jogador:WaitForChild("PlayerScripts"):WaitForChild("PlayerModule", 2)
local controles = pm and require(pm):GetControls()
local function vetorTeclas()
	local x = (UIS:IsKeyDown(Enum.KeyCode.D) and 1 or 0) - (UIS:IsKeyDown(Enum.KeyCode.A) and 1 or 0)
	local z = (UIS:IsKeyDown(Enum.KeyCode.S) and 1 or 0) - (UIS:IsKeyDown(Enum.KeyCode.W) and 1 or 0)
	return Vector3.new(x, 0, z)
end

local ativo = false
local correrToque = false
local ultimoEnvio, ultimoDir, ultimaMarcha = 0, Vector3.zero, ""

-- HUD minimo de ensaio
local gui = Instance.new("ScreenGui"); gui.Name = "HUD_LoboArtico_Ensaio"; gui.ResetOnSpawn = false
local txt = Instance.new("TextLabel"); txt.Size = UDim2.fromOffset(330, 92); txt.Position = UDim2.fromOffset(12, 60)
txt.BackgroundTransparency = 0.35; txt.BackgroundColor3 = Color3.fromRGB(20, 24, 30); txt.TextColor3 = Color3.new(1, 1, 1)
txt.Font = Enum.Font.Code; txt.TextSize = 14; txt.TextXAlignment = Enum.TextXAlignment.Left; txt.TextYAlignment = Enum.TextYAlignment.Top
txt.Parent = gui; gui.Parent = jogador:WaitForChild("PlayerGui")

local function camera() return workspace.CurrentCamera end
local function assumir(_, estado)
	if estado ~= Enum.UserInputState.Begin then return Enum.ContextActionResult.Pass end
	if not ativo then
		rede:FireServer("assumir")
		task.delay(0.4, function()
			if lobo:GetAttribute("Controlador") == jogador.UserId then
				ativo = true; camera().CameraSubject = raiz
			end
		end)
	else
		rede:FireServer("soltar"); ativo = false
		local hum = jogador.Character and jogador.Character:FindFirstChildOfClass("Humanoid")
		if hum then camera().CameraSubject = hum end
	end
	return Enum.ContextActionResult.Sink
end
local function uivo(_, estado)
	if estado == Enum.UserInputState.Begin and ativo then rede:FireServer("uivo") end
	return ativo and Enum.ContextActionResult.Sink or Enum.ContextActionResult.Pass
end
local function correr(_, estado)
	if estado == Enum.UserInputState.Begin and ativo then correrToque = not correrToque end
	return Enum.ContextActionResult.Pass
end
CAS:BindAction("Lobo_Assumir", assumir, true, Enum.KeyCode.F)
CAS:BindAction("Lobo_Uivo", uivo, true, Enum.KeyCode.H)
CAS:BindAction("Lobo_CorrerToque", correr, true)          -- so botao de toque (Shift e lido direto)
CAS:SetTitle("Lobo_Assumir", "Lobo"); CAS:SetTitle("Lobo_Uivo", "Uivo"); CAS:SetTitle("Lobo_CorrerToque", "Correr")

-- se o servidor soltar (pacote velho, saiu, etc.), volta a camera
lobo:GetAttributeChangedSignal("Controlador"):Connect(function()
	if ativo and lobo:GetAttribute("Controlador") ~= jogador.UserId then
		ativo = false
		local hum = jogador.Character and jogador.Character:FindFirstChildOfClass("Humanoid")
		if hum then camera().CameraSubject = hum end
	end
end)

RunService.RenderStepped:Connect(function()
	local en = lobo:GetAttribute("Energia") or 0
	local rec = math.max(0, (lobo:GetAttribute("RecargaFim_Uivo") or 0) - workspace:GetServerTimeNow())
	txt.Text = string.format(" Lobo Artico (ensaio)  [F] %s\n marcha %s %s  vel %.1f\n energia %d  uivo %s  xVel %.2f\n %s",
		ativo and "solta" or "assume", lobo:GetAttribute("CtrlMarcha") or "", lobo:GetAttribute("CtrlClipe") or "",
		lobo:GetAttribute("VelAtual") or 0, en, rec > 0 and string.format("%.0fs", rec) or "pronto",
		lobo:GetAttribute("MultVelocidade") or 1, tostring(lobo:GetAttribute("UivoUltimaRecusa") or ""))
	if not ativo then return end
	local mv = controles and controles:GetMoveVector() or vetorTeclas()      -- local da camera: X direita, -Z frente
	local cf = camera().CFrame
	local fr = Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z); local di = Vector3.new(cf.RightVector.X, 0, cf.RightVector.Z)
	local dir = Vector3.zero
	if fr.Magnitude > 1e-3 then dir = di.Unit * mv.X + fr.Unit * (-mv.Z) end
	if dir.Magnitude < 0.1 and not controles then                          -- toque/controle sem PlayerModule
		local hum = jogador.Character and jogador.Character:FindFirstChildOfClass("Humanoid")
		if hum then dir = Vector3.new(hum.MoveDirection.X, 0, hum.MoveDirection.Z) end
	end
	if dir.Magnitude > 1 then dir = dir.Unit end
	local marcha = (UIS:IsKeyDown(Enum.KeyCode.LeftShift) or correrToque) and "correr"
		or UIS:IsKeyDown(Enum.KeyCode.LeftControl) and "andar" or "trote"
	local agora = os.clock()
	-- envia na mudanca ou a cada 0,2 s (o servidor solta o comando sem pacote por 0,6 s)
	if (dir - ultimoDir).Magnitude > 0.05 or marcha ~= ultimaMarcha or agora - ultimoEnvio > 0.2 then
		rede:FireServer("mover", dir, marcha)
		ultimoEnvio, ultimoDir, ultimaMarcha = agora, dir, marcha
	end
end)
