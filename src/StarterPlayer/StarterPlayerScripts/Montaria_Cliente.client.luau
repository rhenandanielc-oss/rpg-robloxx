-- Montaria_Cliente (LocalScript, StarterPlayerScripts) — entrada, camera, HUD e visual do cavaleiro.
-- Envia so INTENCAO ao servidor (acelerador/giro/subida, direcao da camera, botoes). Movimento vem do PlayerModule
-- (WASD, analogico do gamepad, joystick de toque); acoes por ContextActionService (teclado, gamepad e botoes de toque).
-- Camera: segue um alvo suavizado no pivo do dragao (nao nos ossos), entao a batida das asas nao sacode a imagem.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local CAS = game:GetService("ContextActionService")
local TweenService = game:GetService("TweenService")

local lp = Players.LocalPlayer
local pasta = RS:WaitForChild("Montaria_Dragoes")
local Cfg = require(pasta:WaitForChild("ConfigMontaria"))
local Comando, Entrada, Aviso = pasta:WaitForChild("Comando"), pasta:WaitForChild("Entrada"), pasta:WaitForChild("Aviso")
local Pedido = RS:WaitForChild("Combate_Dragoes"):WaitForChild("Pedido", 30)
local UIS = game:GetService("UserInputService")
local controles                                                   -- PlayerModule (se existir) cobre teclado, gamepad e toque
task.spawn(function()
	local pm = lp:WaitForChild("PlayerScripts"):WaitForChild("PlayerModule", 8)
	if pm then local ok, c = pcall(function() return require(pm):GetControls() end); if ok then controles = c end end
end)
local function vetorMovimento()
	if controles then local ok, v = pcall(function() return controles:GetMoveVector() end); if ok and v then return v end end
	-- reserva: teclado + analogico esquerdo
	local x, z = 0, 0
	if UIS:IsKeyDown(Enum.KeyCode.W) or UIS:IsKeyDown(Enum.KeyCode.Up) then z -= 1 end
	if UIS:IsKeyDown(Enum.KeyCode.S) or UIS:IsKeyDown(Enum.KeyCode.Down) then z += 1 end
	if UIS:IsKeyDown(Enum.KeyCode.A) or UIS:IsKeyDown(Enum.KeyCode.Left) then x -= 1 end
	if UIS:IsKeyDown(Enum.KeyCode.D) or UIS:IsKeyDown(Enum.KeyCode.Right) then x += 1 end
	for _, st in ipairs(UIS:GetGamepadState(Enum.UserInputType.Gamepad1)) do
		if st.KeyCode == Enum.KeyCode.Thumbstick1 and st.Position.Magnitude > 0.15 then x, z = st.Position.X, -st.Position.Y end
	end
	return Vector3.new(x, 0, z)
end
local C = Cfg.controles

-- ===== prompts: so o dono ve o "Montar" ==========================================================================
local function ajustarPrompt(pp)
	if not (pp:IsA("ProximityPrompt") and pp.Name == "Montar") then return end
	local m = pp:FindFirstAncestorWhichIsA("Model")
	local function upd() pp.Enabled = m and m:GetAttribute("DonoUserId") == lp.UserId and not m:GetAttribute("Cavaleiro") or false end
	upd(); if m then m:GetAttributeChangedSignal("Cavaleiro"):Connect(upd); m:GetAttributeChangedSignal("DonoUserId"):Connect(upd) end
	pp:GetPropertyChangedSignal("Enabled"):Connect(function() if pp.Enabled and m and m:GetAttribute("DonoUserId") ~= lp.UserId then pp.Enabled = false end end)
end
for _, d in ipairs(workspace:GetDescendants()) do ajustarPrompt(d) end
workspace.DescendantAdded:Connect(ajustarPrompt)

-- ===== cavaleiros (todos, inclusive de outros jogadores): seguem o osso do dorso so no visual ======================
local seguir = {}                                                   -- [weld] = {root, osso, offset, c0}
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end
local function vincular(w)
	if not (w:IsA("Weld") and w.Name == "SelaWeld") then return end
	task.defer(function()
		local root = w.Part0; local m = root and root:FindFirstAncestorWhichIsA("Model"); local b = m and osso(m, Cfg.assento.osso)
		if not b then return end
		local c0 = w.C0
		local cf = b.CFrame; local p = b.Parent                     -- pose de repouso do osso (independe da animacao atual)
		while p and p:IsA("Bone") do cf = p.CFrame * cf; p = p.Parent end
		seguir[w] = {root = root, osso = b, offset = ((p and p:IsA("BasePart") and p.CFrame or CFrame.new()) * cf):ToObjectSpace(root.CFrame * c0), c0 = c0}
		w.AncestryChanged:Connect(function(_, p) if not p then seguir[w] = nil end end)
	end)
end
for _, d in ipairs(workspace:GetDescendants()) do vincular(d) end
workspace.DescendantAdded:Connect(vincular)
RunService.RenderStepped:Connect(function()
	for w, s in pairs(seguir) do
		if w.Parent and s.root.Parent then
			local animado = s.root.CFrame:ToObjectSpace(s.osso.TransformedWorldCFrame * s.offset)
			w.C0 = s.c0:Lerp(animado, Cfg.assento.seguirOsso)
		end
	end
end)

-- ===== HUD =======================================================================================================
local gui = Instance.new("ScreenGui"); gui.Name = "MontariaHUD"; gui.ResetOnSpawn = false; gui.Enabled = false; gui.Parent = lp:WaitForChild("PlayerGui")
local function rotulo(pai, props)
	local t = Instance.new("TextLabel"); t.BackgroundTransparency = 1; t.Font = Enum.Font.GothamMedium; t.TextColor3 = Color3.fromRGB(245, 235, 220)
	t.TextStrokeTransparency = 0.6; t.TextXAlignment = Enum.TextXAlignment.Left; t.TextScaled = false; t.TextSize = 15
	for k, v in pairs(props) do t[k] = v end; t.Parent = pai; return t
end
local painel = Instance.new("Frame"); painel.Size = UDim2.fromOffset(250, 96); painel.Position = UDim2.new(0, 16, 1, -250)
painel.BackgroundColor3 = Color3.fromRGB(20, 16, 14); painel.BackgroundTransparency = 0.35; painel.Parent = gui
Instance.new("UICorner", painel).CornerRadius = UDim.new(0, 8)
local tEstado = rotulo(painel, {Position = UDim2.fromOffset(12, 6), Size = UDim2.new(1, -24, 0, 20), TextSize = 17, Font = Enum.Font.GothamBold})
local tVoo = rotulo(painel, {Position = UDim2.fromOffset(12, 28), Size = UDim2.new(1, -24, 0, 18)})
local tElem = rotulo(painel, {Position = UDim2.fromOffset(12, 48), Size = UDim2.new(1, -24, 0, 18)})
local barra = Instance.new("Frame"); barra.Position = UDim2.fromOffset(12, 74); barra.Size = UDim2.new(1, -24, 0, 10); barra.BackgroundColor3 = Color3.fromRGB(60, 50, 45); barra.Parent = painel
local energia = Instance.new("Frame"); energia.Size = UDim2.fromScale(1, 1); energia.BackgroundColor3 = Color3.fromRGB(255, 150, 60); energia.BorderSizePixel = 0; energia.Parent = barra
local slots = {}
local linha = Instance.new("Frame"); linha.BackgroundTransparency = 1; linha.Size = UDim2.fromOffset(4 * 74, 70); linha.Position = UDim2.new(0.5, -148, 1, -96); linha.Parent = gui
for i, h in ipairs(C.habilidades) do
	local f = Instance.new("Frame"); f.Size = UDim2.fromOffset(68, 64); f.Position = UDim2.fromOffset((i - 1) * 74, 0)
	f.BackgroundColor3 = Color3.fromRGB(28, 22, 20); f.BackgroundTransparency = 0.25; f.Parent = linha
	Instance.new("UICorner", f).CornerRadius = UDim.new(0, 8)
	local cob = Instance.new("Frame"); cob.BackgroundColor3 = Color3.new(0, 0, 0); cob.BackgroundTransparency = 0.45; cob.BorderSizePixel = 0
	cob.AnchorPoint = Vector2.new(0, 1); cob.Position = UDim2.fromScale(0, 1); cob.Size = UDim2.fromScale(1, 0); cob.Parent = f
	rotulo(f, {Text = tostring(i), Position = UDim2.fromOffset(6, 2), Size = UDim2.fromOffset(20, 16), TextSize = 13})
	local nm = rotulo(f, {Text = h[4] or h[1], Position = UDim2.fromOffset(0, 24), Size = UDim2.new(1, 0, 0, 18), TextXAlignment = Enum.TextXAlignment.Center, TextSize = 12})
	local tr = rotulo(f, {Text = "", Position = UDim2.fromOffset(0, 42), Size = UDim2.new(1, 0, 0, 18), TextXAlignment = Enum.TextXAlignment.Center, TextSize = 13})
	slots[h[1]] = {cob = cob, txt = tr, nome = nm, padrao = h[4] or h[1]}
end
-- slot extra da Mordida Aerea (so aparece em dragao com VooLivre; mesma regra de recarga por atributo)
local slotMordida = Instance.new("Frame"); slotMordida.Size = UDim2.fromOffset(68, 64); slotMordida.Position = UDim2.fromOffset(4 * 74 + 12, 0)
slotMordida.BackgroundColor3 = Color3.fromRGB(34, 22, 26); slotMordida.BackgroundTransparency = 0.25; slotMordida.Visible = false; slotMordida.Parent = linha
Instance.new("UICorner", slotMordida).CornerRadius = UDim.new(0, 8)
do
	local cob = Instance.new("Frame"); cob.BackgroundColor3 = Color3.new(0, 0, 0); cob.BackgroundTransparency = 0.45; cob.BorderSizePixel = 0
	cob.AnchorPoint = Vector2.new(0, 1); cob.Position = UDim2.fromScale(0, 1); cob.Size = UDim2.fromScale(1, 0); cob.Parent = slotMordida
	rotulo(slotMordida, {Text = "M1", Position = UDim2.fromOffset(6, 2), Size = UDim2.fromOffset(50, 16), TextSize = 12})
	rotulo(slotMordida, {Text = "Mordida", Position = UDim2.fromOffset(0, 24), Size = UDim2.new(1, 0, 0, 18), TextXAlignment = Enum.TextXAlignment.Center, TextSize = 12})
	local tr = rotulo(slotMordida, {Text = "", Position = UDim2.fromOffset(0, 42), Size = UDim2.new(1, 0, 0, 18), TextXAlignment = Enum.TextXAlignment.Center, TextSize = 13})
	slots.MordidaAerea = {cob = cob, txt = tr}
end
local dica = rotulo(gui, {Position = UDim2.new(0, 16, 1, -148), Size = UDim2.fromOffset(560, 40), TextSize = 12, TextWrapped = true, TextYAlignment = Enum.TextYAlignment.Top,
	Text = "Mouse: direcao (no ar: sobe/desce/vira para onde a camera olha) | W acelera, S desacelera | Espaco decolar | G planar | F pousar | X desmontar | 1-4 habilidades | Alt solta o mouse"})
-- avisos ficam numa tela SEMPRE ligada: recusas de montaria (longe, nao e seu...) chegam antes de montar
local guiAviso = Instance.new("ScreenGui"); guiAviso.Name = "MontariaAvisos"; guiAviso.ResetOnSpawn = false; guiAviso.Parent = lp.PlayerGui
local toast = rotulo(guiAviso, {AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 90), Size = UDim2.fromOffset(520, 30), TextXAlignment = Enum.TextXAlignment.Center,
	TextSize = 18, Font = Enum.Font.GothamBold, TextColor3 = Color3.fromRGB(255, 200, 150), TextTransparency = 1, TextStrokeTransparency = 1})
Aviso.OnClientEvent:Connect(function(txt)
	toast.Text = tostring(txt); toast.TextTransparency = 0; toast.TextStrokeTransparency = 0.5
	TweenService:Create(toast, TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.In, 0, false, 2.2), {TextTransparency = 1, TextStrokeTransparency = 1}):Play()
end)
local NOMES = {chao = "No chao", decolando = "Decolando", voo = "Em voo", pousando = "Pousando", transicao = "Montando..."}

-- ===== estado montado ============================================================================================
local m = nil                                                        -- dragao montado
-- PATCH_HUD_FORMA (01/11): habilidades que ESTE dragao tem (atributo HabilidadesForma; sem ele = todas, como antes)
local function habPermitida(nome)
	local lista = m and m:GetAttribute("HabilidadesForma")
	if lista == nil then return true end
	return table.find(string.split(lista, ","), nome) ~= nil
end
local seg = {subir = false, descer = false, correr = false}
local alvoCam, camAntes
local soproSegurado = false                                           -- sopro com a tecla segurada (mira viva)
local miraAte = 0                                                      -- PATCH_KIT_GELO: habilidade com mira viva (Rajadas)
local function cyCp()
	-- a camera fica acima do dragao olhando um pouco para baixo: esse angulo (pitchNeutro) conta como voo horizontal
	local lv = workspace.CurrentCamera.CFrame.LookVector
	return math.atan2(lv.X, lv.Z), math.asin(math.clamp(lv.Y, -1, 1)) + (Cfg.camera.pitchNeutro or 0)
end
local function juntar(a, b) local t = table.clone(a or {}); for _, x in ipairs(b or {}) do table.insert(t, x) end; return t end
local function acao(nome, fn, teclas, titulo)
	CAS:BindActionAtPriority(nome, function(_, st, obj) return fn(st, obj) end, true, Enum.ContextActionPriority.High.Value + 10, table.unpack(teclas))
	CAS:SetTitle(nome, titulo)
end
local function ligarAcoes()
	acao("Mont_Subir", function(st)
		seg.subir = st == Enum.UserInputState.Begin
		if st == Enum.UserInputState.Begin and m and m:GetAttribute("MontariaModo") == "chao" then Comando:FireServer("decolar") end
		return Enum.ContextActionResult.Sink                                         -- engole o pulo do personagem
	end, juntar(C.decolar, C.subirAr), "Voar")
	acao("Mont_Descer", function(st) seg.descer = st == Enum.UserInputState.Begin; return Enum.ContextActionResult.Sink end, juntar(C.descer, C.descerAr), "Descer")
	acao("Mont_Correr", function(st) seg.correr = st == Enum.UserInputState.Begin; return Enum.ContextActionResult.Sink end, C.correr, "Correr")
	acao("Mont_Planar", function(st) if st == Enum.UserInputState.Begin then Comando:FireServer("planar") end; return Enum.ContextActionResult.Sink end, C.planar, "Planar")
	if m and m:GetAttribute("VooLivre") and C.mordida then
		acao("Mont_Mordida", function(st)
			if st == Enum.UserInputState.Begin and m then
				if m:GetAttribute("MontariaModo") == "voo" then Comando:FireServer("mordida")
				elseif m:GetAttribute("MontariaModo") == "chao" and Pedido then Pedido:FireServer(m, "usar", "Mordida", workspace.CurrentCamera.CFrame.LookVector) end
			end
			return (m and m:GetAttribute("MontariaModo") == "voo") and Enum.ContextActionResult.Sink or Enum.ContextActionResult.Pass
		end, C.mordida, "Mordida")
		if C.garra then
			acao("Mont_Garra", function(st)
				if st == Enum.UserInputState.Begin and m and m:GetAttribute("MontariaModo") == "chao" and Pedido then
					Pedido:FireServer(m, "usar", "Garra", workspace.CurrentCamera.CFrame.LookVector)
				end
				return Enum.ContextActionResult.Sink
			end, C.garra, "Garra")
		end
	end
	acao("Mont_Pousar", function(st) if st == Enum.UserInputState.Begin then Comando:FireServer("pousar") end; return Enum.ContextActionResult.Sink end, C.pousar, "Pousar")
	acao("Mont_Desmontar", function(st) if st == Enum.UserInputState.Begin then Comando:FireServer("desmontar") end; return Enum.ContextActionResult.Sink end, C.desmontar, "Sair")
	-- troca de elemento: so em forma com MAIS de um elemento (oficial 30/10: o Montanhas e so Fogo, sem troca)
	local varios = #string.split(m and m:GetAttribute("ElementosValidos") or "", ",") > 1
	if varios then acao("Mont_Elemento", function(st)
		if st == Enum.UserInputState.Begin and m and Pedido then
			local lista = string.split(m:GetAttribute("ElementosValidos") or "", ","); local at = m:GetAttribute("ElementoAtivo")
			local i = table.find(lista, at) or 0; local prox = lista[i % #lista + 1]
			if prox and prox ~= "" then Pedido:FireServer(m, "elemento", prox) end
		end
		return Enum.ContextActionResult.Sink
	end, C.elemento, "Elem.") end
	for _, h in ipairs(C.habilidades) do
		if not habPermitida(h[1]) then continue end
		acao("Mont_" .. h[1], function(st)
			if not (m and Pedido) then return Enum.ContextActionResult.Sink end
			if st == Enum.UserInputState.Begin then
				Pedido:FireServer(m, "usar", h[1], dirMira())                     -- direcao da BOCA ate o ponto do cursor
				if h[1] == "Sopro" then soproSegurado = true end
				local mv = C.miraVivaForma and C.miraVivaForma[m:GetAttribute("FormaRegional") or ""]
				if mv and mv[h[1]] then miraAte = os.clock() + mv[h[1]] end
			elseif st == Enum.UserInputState.End and h[1] == "Sopro" and soproSegurado then
				soproSegurado = false; Pedido:FireServer(m, "soltar")
			end
			return Enum.ContextActionResult.Sink
		end, {h[2], h[3]}, h[1])
	end
end
local function desligarAcoes()
	for _, n in ipairs({"Mont_Subir", "Mont_Descer", "Mont_Correr", "Mont_Planar", "Mont_Pousar", "Mont_Desmontar", "Mont_Elemento", "Mont_Mordida", "Mont_Garra"}) do CAS:UnbindAction(n) end
	for _, h in ipairs(C.habilidades) do CAS:UnbindAction("Mont_" .. h[1]) end
end

-- ===== camera orbital da montaria ================================================================================
-- Rotacao: imediata (mouse/analogico direito) => resposta instantanea ao apontar. Posicao: alvo suavizado no pivo
-- (nao nos ossos) => batidas de asa nao sacodem a imagem. Distancia cresce com a velocidade. Colisao: raio do alvo
-- ate a camera; se bater (montanha, arvore), a camera entra antes do obstaculo. O dragao segue para onde ela olha.
local orbita, mouseLivre = false, false
-- ===== mira pelo cursor (mouse livre) =============================================================================
-- O cursor NAO fica preso: aponta os poderes. Raio da camera pelo ponto do cursor (ignora o proprio dragao, o
-- cavaleiro e os efeitos); a direcao final sai da BOCA ate esse ponto (o servidor valida o cone do pescoco).
local rpMira = RaycastParams.new(); rpMira.FilterType = Enum.RaycastFilterType.Exclude
function pontoMira()
	local cam = workspace.CurrentCamera
	local p = UIS:GetMouseLocation()
	local raio = cam:ViewportPointToRay(p.X, p.Y)
	local ex = {}
	if m then table.insert(ex, m) end
	if lp.Character then table.insert(ex, lp.Character) end
	if alvoCam then table.insert(ex, alvoCam) end
	local fx = workspace:FindFirstChild("VFX_Temporarios"); if fx then table.insert(ex, fx) end
	rpMira.FilterDescendantsInstances = ex
	local h = workspace:Raycast(raio.Origin, raio.Direction * 700, rpMira)
	return h and h.Position or (raio.Origin + raio.Direction * 400), h
end
local function bocaPos()
	if not m then return Vector3.zero end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == "mouth_upper_tip" then return d.TransformedWorldCFrame.Position end end
	return m:GetPivot().Position
end
function dirMira()
	local alvo = pontoMira(); local v = alvo - bocaPos()
	return v.Magnitude > 1 and v.Unit or workspace.CurrentCamera.CFrame.LookVector
end
local orb = {yaw = 0, pitch = -0.28, dist = 70, zoom = nil}
local orbAtivo = false           -- zoom: escolhido pela roda do mouse (entre distMin e distMax)
local rpCam = RaycastParams.new(); rpCam.FilterType = Enum.RaycastFilterType.Exclude
-- camera por dragao: atributo Camera_<campo> no modelo sobrepoe ConfigMontaria.camera (dragoes de portes diferentes)
local function camCfg(campo) return (m and m:GetAttribute("Camera_" .. campo)) or Cfg.camera[campo] end
UIS.InputChanged:Connect(function(inp, processado)
	if processado or not (m and orbita) or inp.UserInputType ~= Enum.UserInputType.MouseWheel then return end
	orb.zoom = math.clamp((orb.zoom or camCfg("distancia")) * (1 - inp.Position.Z * 0.12), camCfg("distMin"), camCfg("distMax"))
end)
local function cameraOrbital(dt)
	if not m or not m.Parent or not alvoCam then return end
	local cam = workspace.CurrentCamera
	cam.CameraType = Enum.CameraType.Scriptable
	-- MOUSE LIVRE (oficial 29/10): o cursor fica solto para mirar; a camera so gira com o BOTAO DIREITO segurado.
	-- Sem girar, a camera volta suave para tras do dragao (nada de curva involuntaria a cada movimento do mouse).
	local orbitando = UIS:IsMouseButtonPressed(Enum.UserInputType.MouseButton2)
	UIS.MouseBehavior = orbitando and Enum.MouseBehavior.LockCurrentPosition or Enum.MouseBehavior.Default
	UIS.MouseIconEnabled = false                                              -- a reticula pequena faz o papel do cursor
	if orbitando then
		local d = UIS:GetMouseDelta()
		local sens = 0.0042 * UserSettings():GetService("UserGameSettings").MouseSensitivity
		orb.yaw -= d.X * sens; orb.pitch -= d.Y * sens
	elseif (m:GetAttribute("Velocidade") or 0) > 2 or m:GetAttribute("NoAr") then
		local lv = m:GetPivot().LookVector
		local alvoYaw = math.atan2(-lv.X, -lv.Z)
		local dif = (alvoYaw - orb.yaw + math.pi) % (2 * math.pi) - math.pi
		orb.yaw += dif * math.min(1, 2.2 * dt)
	end
	orbAtivo = orbitando
	for _, st in ipairs(UIS:GetGamepadState(Enum.UserInputType.Gamepad1)) do
		if st.KeyCode == Enum.KeyCode.Thumbstick2 and st.Position.Magnitude > 0.15 then
			orb.yaw -= st.Position.X * 2.6 * dt; orb.pitch += st.Position.Y * 1.8 * dt
		end
	end
	orb.pitch = math.clamp(orb.pitch, -1.25, 1.05)
	local v = m:GetAttribute("Velocidade") or 0
	-- distancia: zoom do jogador (padrao = distancia) + um pouco com a velocidade, sempre dentro de [distMin, distMax]
	local alvoD = math.clamp((orb.zoom or camCfg("distancia")) + v * (camCfg("porVel") or 0.45), camCfg("distMin"), camCfg("distMax"))
	orb.dist += (alvoD - orb.dist) * math.min(1, 4 * dt)
	local alvo = alvoCam.Position
	local rot = CFrame.fromEulerAnglesYXZ(orb.pitch, orb.yaw, 0)
	local desejado = alvo + rot:VectorToWorldSpace(Vector3.new(0, 0, orb.dist))
	local ex = {m, alvoCam}; if lp.Character then table.insert(ex, lp.Character) end
	local fx = workspace:FindFirstChild("VFX_Temporarios"); if fx then table.insert(ex, fx) end
	rpCam.FilterDescendantsInstances = ex
	local h = workspace:Raycast(alvo, desejado - alvo, rpCam)
	local pos = h and (h.Position + (alvo - h.Position).Unit * 2) or desejado
	-- tranco curto quando a mordida acerta (amortece em 0,25 s; sem tremor continuo)
	local hit = m:GetAttribute("MordidaAcertou")
	local k = hit and math.clamp(1 - (workspace:GetServerTimeNow() - hit) / 0.25, 0, 1) or 0
	local tranco = k > 0 and Vector3.new(math.sin(os.clock() * 70), math.cos(os.clock() * 55), 0) * 0.6 * k or Vector3.zero
	cam.CFrame = CFrame.lookAt(pos, alvo) * CFrame.new(tranco)
end

-- reticula pequena e discreta no cursor: branca; vermelha sobre um alvo com Humanoid (nao garante acerto)
local reticula = Instance.new("Frame"); reticula.Name = "Reticula"; reticula.Size = UDim2.fromOffset(14, 14); reticula.AnchorPoint = Vector2.new(0.5, 0.5)
reticula.BackgroundTransparency = 1; reticula.Visible = false; reticula.ZIndex = 50; reticula.Parent = gui
local anelR = Instance.new("UIStroke"); anelR.Thickness = 1.6; anelR.Color = Color3.fromRGB(240, 240, 240); anelR.Transparency = 0.15; anelR.Parent = reticula
Instance.new("UICorner", reticula).CornerRadius = UDim.new(1, 0)
local pontoR = Instance.new("Frame"); pontoR.Size = UDim2.fromOffset(2, 2); pontoR.AnchorPoint = Vector2.new(0.5, 0.5); pontoR.Position = UDim2.fromScale(0.5, 0.5)
pontoR.BackgroundColor3 = Color3.fromRGB(240, 240, 240); pontoR.BorderSizePixel = 0; pontoR.Parent = reticula
RunService.RenderStepped:Connect(function()
	if not (m and reticula.Visible) then return end
	local p = UIS:GetMouseLocation(); local ins = game:GetService("GuiService"):GetGuiInset()
	reticula.Position = UDim2.fromOffset(p.X - ins.X, p.Y - ins.Y)
	local _, h = pontoMira()
	local alvo = h and h.Instance and h.Instance:FindFirstAncestorWhichIsA("Model")
	local valido = alvo and alvo:FindFirstChildOfClass("Humanoid") ~= nil
	anelR.Color = valido and Color3.fromRGB(255, 90, 80) or Color3.fromRGB(240, 240, 240); pontoR.BackgroundColor3 = anelR.Color
end)
local function entrar(dragao)
	m = dragao
	local hum = lp.Character and lp.Character:FindFirstChildOfClass("Humanoid")
	if hum then hum:SetStateEnabled(Enum.HumanoidStateType.Jumping, false) end
	local cam = workspace.CurrentCamera
	camAntes = {subj = cam.CameraSubject, min = lp.CameraMinZoomDistance, max = lp.CameraMaxZoomDistance, fov = cam.FieldOfView}
	alvoCam = Instance.new("Part"); alvoCam.Name = "AlvoCameraMontaria"; alvoCam.Anchored = true; alvoCam.CanCollide = false; alvoCam.CanQuery = false
	alvoCam.Transparency = 1; alvoCam.Size = Vector3.one; alvoCam.CFrame = m:GetPivot() + Vector3.yAxis * camCfg("alturaAlvo"); alvoCam.Parent = workspace
	-- mouse/gamepad: camera orbital propria (mouse preso no centro, sem segurar botao); toque: camera padrao do Roblox
	orbita = UIS.MouseEnabled or UIS.GamepadEnabled
	if orbita then
		cam.CameraType = Enum.CameraType.Scriptable
		local lv = cam.CFrame.LookVector; orb.yaw = math.atan2(-lv.X, -lv.Z); orb.pitch = -0.28; orb.dist = camCfg("distancia"); orb.zoom = camCfg("distancia")
		mouseLivre = false
		CAS:BindActionAtPriority("Mont_Mouse", function(_, st)
			if st == Enum.UserInputState.Begin then mouseLivre = not mouseLivre end
			return Enum.ContextActionResult.Sink
		end, false, Enum.ContextActionPriority.High.Value + 10, Enum.KeyCode.LeftAlt)
		RunService:BindToRenderStep("CameraMontaria", Enum.RenderPriority.Camera.Value + 1, cameraOrbital)
	else
		cam.CameraSubject = alvoCam
		lp.CameraMinZoomDistance = camCfg("distancia"); lp.CameraMaxZoomDistance = camCfg("distancia")                 -- abre na distancia certa
		task.delay(0.2, function() lp.CameraMinZoomDistance = camCfg("distMin"); lp.CameraMaxZoomDistance = camCfg("distMax") end)
	end
	dica.Text = m:GetAttribute("VooLivre") and
		"Botao direito: girar a camera (o dragao segue) | Cursor: mira | W acelera | solte W: para no ar | E sobe / Q desce | Espaco: decolar | segure 1: sopro continuo (mira no cursor) | 2 Arremetida | 3 Tempestade | 4 Coracao Infernal | R: garra (no chao) | M1: mordida (no chao: terrestre; no ar: mordida aerea | G planar | X desmontar | Roda: zoom | Alt solta o mouse"
		or "Mouse: direcao (no ar: sobe/desce/vira para onde a camera olha) | W acelera, S desacelera | Espaco decolar | G planar | F pousar | X desmontar | 1-4 habilidades | Alt solta o mouse"
	slotMordida.Visible = m:GetAttribute("VooLivre") == true
	for _, h in ipairs(C.habilidades) do slots[h[1]].cob.Parent.Visible = habPermitida(h[1]) end
	if m:GetAttribute("HabilidadesForma") ~= nil then
		dica.Text = dica.Text:gsub(" | segure 1: sopro continuo %(mira no cursor%) | 2 Arremetida | 3 Tempestade | 4 Coracao Infernal", ""):gsub(" | 1%-4 habilidades", "")
	end
	-- PATCH_KIT_GELO: nomes dos slots, dica e cor da energia da forma
	local fr = m:GetAttribute("FormaRegional") or ""
	local rf = C.rotulosForma and C.rotulosForma[fr]
	for id, s in pairs(slots) do if s.nome then s.nome.Text = (rf and rf[id]) or s.padrao end end
	if C.dicaForma and C.dicaForma[fr] then dica.Text ..= C.dicaForma[fr] end
	energia.BackgroundColor3 = (C.corEnergiaForma and C.corEnergiaForma[fr]) or Color3.fromRGB(255, 150, 60)
	gui.Enabled = true; if reticula then reticula.Visible = UIS.MouseEnabled end
	ligarAcoes()
end
local function sair()
	desligarAcoes()
	local hum = lp.Character and lp.Character:FindFirstChildOfClass("Humanoid")
	if hum then hum:SetStateEnabled(Enum.HumanoidStateType.Jumping, true) end
	local cam = workspace.CurrentCamera
	if orbita then
		RunService:UnbindFromRenderStep("CameraMontaria"); CAS:UnbindAction("Mont_Mouse")
		cam.CameraType = Enum.CameraType.Custom; UIS.MouseBehavior = Enum.MouseBehavior.Default; UIS.MouseIconEnabled = true
		orbita = false
	end
	if camAntes then
		cam.CameraSubject = hum or camAntes.subj; lp.CameraMinZoomDistance = camAntes.min; lp.CameraMaxZoomDistance = camAntes.max; cam.FieldOfView = camAntes.fov
	end
	if alvoCam then alvoCam:Destroy(); alvoCam = nil end
	gui.Enabled = false; if reticula then reticula.Visible = false end; soproSegurado = false; m = nil
end
local function observarMontaria(ov)
	if not (ov:IsA("ObjectValue") and ov.Name == "MontariaAtual") then return end
	if ov.Value then entrar(ov.Value) end
	ov.AncestryChanged:Connect(function(_, p) if not p then sair() end end)
end
for _, c in ipairs(lp:GetChildren()) do observarMontaria(c) end
lp.ChildAdded:Connect(observarMontaria)

-- ===== laco: entrada (15 Hz), camera e HUD =======================================================================
local acum = 0
RunService.RenderStepped:Connect(function(dt)
	if not m or not m.Parent then return end
	-- entrada
	acum += dt
	if acum >= 1 / Cfg.entradaHz then
		acum = 0
		local mv = vetorMovimento()
		local cy, cp = cyCp()
		-- a camera so comanda o rumo/pitch do voo enquanto o jogador a GIRA (botao direito ou analogico direito);
		-- fora disso o dragao segue reto/A-D e o cursor serve so para mirar
		local stick = false
		for _, st in ipairs(UIS:GetGamepadState(Enum.UserInputType.Gamepad1)) do if st.KeyCode == Enum.KeyCode.Thumbstick2 and st.Position.Magnitude > 0.15 then stick = true end end
		if not (orbAtivo or stick or not UIS.MouseEnabled) then cy, cp = nil, 0 end
		Entrada:FireServer({f = -mv.Z, t = mv.X, up = (seg.subir and 1 or 0) - (seg.descer and 1 or 0), c = seg.correr, cy = cy, cp = cp})
		local dm = dirMira(); m:SetAttribute("MiraLocal", dm)                   -- cabeca do dragao olha a mira (MovimentoVivo)
		if (soproSegurado or os.clock() < miraAte) and Pedido then Pedido:FireServer(m, "mira", nil, dm) end
	end
	-- camera: alvo suavizado no pivo (sem tremer com as asas); FOV abre um pouco com a velocidade
	local alvo = m:GetPivot().Position + Vector3.yAxis * (camCfg("alturaAlvo") + (m:GetAttribute("NoAr") and camCfg("alturaVoo") or 0))
	alvoCam.CFrame = CFrame.new(alvoCam.Position:Lerp(alvo, math.min(1, Cfg.camera.suav * dt)))
	local v = m:GetAttribute("Velocidade") or 0
	local cam = workspace.CurrentCamera
	cam.FieldOfView += ((Cfg.camera.fovBase + Cfg.camera.fovVel * math.clamp(v / Cfg.vooRapidoVel, 0, 1)) - cam.FieldOfView) * math.min(1, 2 * dt)
	-- HUD
	local modo = m:GetAttribute("MontariaModo") or "transicao"
	tEstado.Text = (NOMES[modo] or modo) .. (modo == "voo" and m:GetAttribute("VooEstado") and (" (" .. m:GetAttribute("VooEstado") .. ", " .. math.floor(m:GetAttribute("Velocidade") or 0) .. ")") or "") .. (m:GetAttribute("EmAtaque") and ("  |  " .. m:GetAttribute("EmAtaque")) or "")
	local adulto = table.find({"Adulto", "Anciao"}, m:GetAttribute("Estagio"))
	local voo = adulto and (m:GetAttribute("VooDesbloqueado") == true or m:GetAttribute("VooDev") == true)
	tVoo.Text = not voo and "Voo montado: bloqueado (missao de voo)"
		or (m:GetAttribute("VooDesbloqueado") == true and "Voo montado: liberado" or "Voo montado: liberado (DEV - teste)")
	tVoo.TextColor3 = voo and Color3.fromRGB(190, 230, 170) or Color3.fromRGB(240, 170, 140)
	-- elemento unico + passivas (Sangue de Magma mostra o reforco ativo)
	local pas = {}
	for _, id in ipairs(string.split(m:GetAttribute("Passivas") or "", ",")) do
		if id ~= "" then
			local nome = (C.passivas and C.passivas[id]) or id
			if id == "SangueDeMagma" and (m:GetAttribute("SangueMagmaFim") or 0) > workspace:GetServerTimeNow() then nome ..= " (ativo)" end
			table.insert(pas, nome)
		end
	end
	tElem.Text = "Elemento: " .. tostring(m:GetAttribute("ElementoAtivo") or "-") .. (#pas > 0 and ("  |  Passivas: " .. table.concat(pas, ", ")) or "")
	energia.Size = UDim2.fromScale(math.clamp((m:GetAttribute("Energia") or 0) / 100, 0, 1), 1)
	local agora = workspace:GetServerTimeNow()
	for hab, s in pairs(slots) do
		local fim = m:GetAttribute("RecargaFim_" .. hab); local dur = m:GetAttribute("RecargaDur_" .. hab)
		local resta = fim and math.max(0, fim - agora) or 0
		s.cob.Size = UDim2.fromScale(1, (resta > 0 and dur) and resta / dur or 0)
		s.txt.Text = resta > 0 and ("%.1f"):format(resta) or ""
	end
end)
