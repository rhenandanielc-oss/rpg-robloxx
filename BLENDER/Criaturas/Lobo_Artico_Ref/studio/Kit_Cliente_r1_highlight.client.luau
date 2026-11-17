-- Kit_Cliente (Script com RunContext = Client, Workspace.Teste_LoboArtico) - comandos e efeitos do KIT do Lobo Artico (16/11).
-- So manda pedidos (o Kit_Servidor decide tudo) e desenha efeitos. Regra do usuario: efeitos NO CORPO, nada flutuando
-- em volta do lobo. Fora do corpo so o que e do ALVO (marca, pegadas, deteccao) e o estouro curto do impacto.
-- PC: Q Cometa Glacial | E Avalanche | clique num inimigo = travar alvo | T solta o alvo. Celular: botoes de toque.
-- Mira (§1): alvo travado -> mouse (PC, cursor livre) -> camera. Durante a Avalanche manda a direcao a 10 Hz.
-- Efeitos (§5.4-5.7):
--   Cometa: preparo = linhas do corpo acendem forte + espinhos crescem; voo = CASCA DE GELO translucida colada ao corpo
--     (Highlight azul-gelo no proprio lobo), FOV +8; impacto = casca estoura (flash e some), tremor curto, vidro.
--   Avalanche: corpo coberto de NEVE COMPACTADA (Highlight branco no lobo); rugido de neve; onda = baque de neve.
--   Instinto Boreal: marca da presa 8 s (contorno azul-gelo + seta) e pegadas com cristais (8 s) SO para o dono;
--     brilho azul onde ha inimigo sob a neve (SO para o dono).
--   Pelagem Polar: camuflagem (contraste cai em 1 s, volta em 0,3 s ao atacar/mover).
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local CAS = game:GetService("ContextActionService")
local UIS = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local jogador = Players.LocalPlayer
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local rede = pasta:WaitForChild("Rede_Kit")
local fxRede = pasta:WaitForChild("Kit_FX")
local raiz = lobo:WaitForChild("RootPart")
local GELO = Color3.fromRGB(165, 222, 255)
local function id(n) return "rbxassetid://" .. n end
local SONS = {voo = id(9125648149), impacto = id(9114591164), ronco = id(9125443744), neve = id(9119316414), tinido = id(9114590297)}
local function souDono() return lobo:GetAttribute("Controlador") == jogador.UserId end
local camera = workspace.CurrentCamera

-- mira --------------------------------------------------------------------------------------------------------------------
local function direcao()
	local cam = workspace.CurrentCamera
	local base = lobo:GetPivot().Position
	if UIS.MouseEnabled and UIS.MouseBehavior ~= Enum.MouseBehavior.LockCenter then
		local m = UIS:GetMouseLocation()
		local raio = cam:ViewportPointToRay(m.X, m.Y)
		local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {lobo, jogador.Character}
		local r = workspace:Raycast(raio.Origin, raio.Direction * 500, rp)
		local p = r and r.Position or (raio.Origin + raio.Direction * 60)
		local d = Vector3.new(p.X - base.X, 0, p.Z - base.Z)
		if d.Magnitude > 0.5 then return d.Unit end
	end
	local l = cam.CFrame.LookVector
	return Vector3.new(l.X, 0, l.Z).Unit
end
local alvoTravado = nil
local function pedir(poder)
	if not souDono() then return end
	rede:FireServer(poder, direcao(), alvoTravado)
end
CAS:BindAction("Lobo_Cometa", function(_, e) if e == Enum.UserInputState.Begin then pedir("cometa") end return Enum.ContextActionResult.Pass end, true, Enum.KeyCode.Q)
CAS:BindAction("Lobo_Avalanche", function(_, e) if e == Enum.UserInputState.Begin then pedir("avalanche") end return Enum.ContextActionResult.Pass end, true, Enum.KeyCode.E)
CAS:BindAction("Lobo_SoltarAlvo", function(_, e) if e == Enum.UserInputState.Begin then alvoTravado = nil; rede:FireServer("travar", nil) end return Enum.ContextActionResult.Pass end, false, Enum.KeyCode.T)
CAS:SetTitle("Lobo_Cometa", "Cometa"); CAS:SetTitle("Lobo_Avalanche", "Avalanche")
UIS.InputBegan:Connect(function(i, gp)
	if gp or i.UserInputType ~= Enum.UserInputType.MouseButton1 or not souDono() then return end
	local m = UIS:GetMouseLocation(); local raio = camera:ViewportPointToRay(m.X, m.Y)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {lobo, jogador.Character}
	local r = workspace:Raycast(raio.Origin, raio.Direction * 300, rp)
	local alvo = r and r.Instance and r.Instance:FindFirstAncestorOfClass("Model")
	if alvo and (alvo:FindFirstChildOfClass("Humanoid") or alvo:GetAttribute("Criatura")) then alvoTravado = alvo; rede:FireServer("travar", alvo) end
end)
-- direcao continua durante a Avalanche (segue mouse/camera sem alvo)
task.spawn(function()
	while lobo.Parent do
		task.wait(0.1)
		if souDono() and lobo:GetAttribute("PoderAtivo") == "Avalanche" then rede:FireServer("dir", direcao()) end
	end
end)

-- sons ----------------------------------------------------------------------------------------------------------------------
local function som(sid, vol, tom, pai, dur)
	local s = Instance.new("Sound"); s.SoundId = sid; s.Volume = vol; s.PlaybackSpeed = tom or 1
	s.RollOffMode = Enum.RollOffMode.InverseTapered; s.RollOffMinDistance = 12; s.RollOffMaxDistance = 220
	s.Parent = pai; s:Play()
	task.delay(dur or 4, function() s:Destroy() end)
	return s
end

-- efeitos NO CORPO: casca/neve (Highlight no proprio lobo), linhas e espinhos ------------------------------------------------
local casca = Instance.new("Highlight"); casca.Name = "Casca_Kit"; casca.Adornee = lobo; casca.Enabled = false
casca.DepthMode = Enum.HighlightDepthMode.Occluded; casca.OutlineTransparency = 1; casca.Parent = lobo
local corpoSA = (lobo:FindFirstChild("LOW_Corpo", true) or Instance.new("Part")):FindFirstChildOfClass("SurfaceAppearance")
local fxPasta = lobo:WaitForChild("FX_Boreal", 10)
local espinhos = {}
if fxPasta then
	for _, p in ipairs(fxPasta:GetChildren()) do
		if p:GetAttribute("OssoEspinho") then
			table.insert(espinhos, {p = p, b = lobo:FindFirstChild(p:GetAttribute("OssoEspinho"), true), off = p:GetAttribute("OffsetOsso"),
				base = p:GetAttribute("BaseLocal"), cheio = p:GetAttribute("TamanhoCheio") or p.Size})
		end
	end
end
local function uivoAtivo() return (lobo:GetAttribute("BonusVel_Uivo") or 0) > 0 end
local estado = {poder = nil, t0 = 0, fimEspinho = nil, flash = 0}
local fovBase = nil
lobo:GetAttributeChangedSignal("PoderAtivo"):Connect(function()
	local p = lobo:GetAttribute("PoderAtivo")
	if p then
		estado.poder = p; estado.t0 = os.clock(); estado.fimEspinho = nil
		if p == "Cometa" then
			casca.FillColor = GELO; casca.FillTransparency = 1; casca.Enabled = true
			som(SONS.voo, 0.7, 1.15, raiz, 2)
		elseif p == "Avalanche" then
			casca.FillColor = Color3.fromRGB(245, 248, 255); casca.FillTransparency = 1; casca.Enabled = true
			estado.ronco = som(SONS.ronco, 0.45, 1.25, raiz, 4)
		end
	else
		if estado.poder == "Cometa" then estado.fimEspinho = os.clock() end
		if estado.ronco then TweenService:Create(estado.ronco, TweenInfo.new(0.4), {Volume = 0}):Play() end
		estado.poder = nil
		TweenService:Create(casca, TweenInfo.new(0.3), {FillTransparency = 1}):Play()
		task.delay(0.35, function() if not estado.poder then casca.Enabled = false end end)
	end
end)

RunService:BindToRenderStep("Kit_Lobo_Efeitos", Enum.RenderPriority.Last.Value, function()
	local t = os.clock() - estado.t0
	-- casca de gelo (Cometa: aparece no voo) / neve compactada (Avalanche)
	if estado.poder == "Cometa" then
		local fase = lobo:GetAttribute("CometaFase")
		casca.FillTransparency = (fase == "Voo") and 0.45 or (fase == "Preparo" and 0.8 or 0.45)
	elseif estado.poder == "Avalanche" then
		casca.FillTransparency = 1 - math.clamp(t / 0.25, 0, 1) * 0.5
	end
	-- linhas do corpo e espinhos no Cometa (se o Uivo nao estiver cuidando deles)
	if not uivoAtivo() then
		local s = 0
		if estado.poder == "Cometa" then s = math.clamp(t / 0.25, 0, 1)
		elseif estado.fimEspinho then s = 1 - math.clamp((os.clock() - estado.fimEspinho) / 0.8, 0, 1); if s <= 0 then estado.fimEspinho = nil end end
		if corpoSA and (s > 0 or estado.poder == "Cometa") then corpoSA.EmissiveStrength = 12 * s end
		for _, e in ipairs(espinhos) do
			if s < 0.02 or not e.b then
				if e.p.Transparency ~= 1 and not uivoAtivo() then e.p.Transparency = 1 end
			else
				local cheio = e.b.TransformedWorldCFrame * e.off
				local base = cheio * e.base
				e.p.Size = e.cheio * s; e.p.CFrame = CFrame.new(base + (cheio.Position - base) * s) * cheio.Rotation
				e.p.Transparency = 0.18
			end
		end
		if s <= 0 and corpoSA and not estado.poder and corpoSA.EmissiveStrength ~= 0 and estado.fimEspinho == nil and not uivoAtivo() then
			corpoSA.EmissiveStrength = 0
		end
	end
	-- FOV +8 no voo do Cometa (so a camera do dono)
	if souDono() then
		local cam = workspace.CurrentCamera
		if estado.poder == "Cometa" and lobo:GetAttribute("CometaFase") == "Voo" then
			fovBase = fovBase or cam.FieldOfView; cam.FieldOfView = fovBase + 8
		elseif fovBase then cam.FieldOfView = fovBase; fovBase = nil end
	end
end)

-- eventos do servidor: impacto, onda, dano ---------------------------------------------------------------------------------
local function tremer(intens, dur)
	if not souDono() then return end
	local t0 = os.clock()
	local con; con = RunService.RenderStepped:Connect(function()
		local k = 1 - (os.clock() - t0) / dur
		if k <= 0 then con:Disconnect(); return end
		local cam = workspace.CurrentCamera
		cam.CFrame = cam.CFrame * CFrame.Angles(math.rad((math.random() - 0.5) * intens * k), math.rad((math.random() - 0.5) * intens * k), 0)
	end)
end
fxRede.OnClientEvent:Connect(function(tipo, a, b, c, d)
	if tipo == "cometa_impacto" then
		-- casca estoura: flash rapido no corpo + estilhacos finos curtos (0,3 s) + vidro
		casca.FillTransparency = 0.1; TweenService:Create(casca, TweenInfo.new(0.3), {FillTransparency = 1}):Play()
		local at = Instance.new("Attachment"); at.Parent = raiz; at.Position = Vector3.new(0, 3, 0)
		local pe = Instance.new("ParticleEmitter")
		pe.Texture = "rbxasset://textures/particles/sparkles_main.dds"; pe.Color = ColorSequence.new(GELO)
		pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.18), NumberSequenceKeypoint.new(1, 0)})
		pe.Lifetime = NumberRange.new(0.2, 0.35); pe.Speed = NumberRange.new(8, 14); pe.SpreadAngle = Vector2.new(180, 180)
		pe.Drag = 6; pe.Rate = 0; pe.LightEmission = 0.6; pe.Parent = at
		pe:Emit(40); task.delay(0.6, function() at:Destroy() end)
		som(SONS.impacto, 0.8, 0.9, raiz, 3)
		tremer(1.6, 0.25)
	elseif tipo == "avalanche_onda" then
		som(SONS.neve, 0.8, 1.0, raiz, 3)
		tremer(0.8, 0.2)
	elseif tipo == "gelo_desviado" then
		som(SONS.tinido, 0.4, 1.4, raiz, 2)
	end
end)

-- Instinto Boreal (so para o dono): marca da presa, pegadas e deteccao sob a neve -------------------------------------------
local marcas = {}
local pegadasPasta = Instance.new("Folder"); pegadasPasta.Name = "Pegadas_Boreal_Cliente"; pegadasPasta.Parent = workspace
local ultimoPasso = {}
local function inimigoVisivel(m)
	if m == lobo or m == jogador.Character then return false end
	local hum = m:FindFirstChildOfClass("Humanoid")
	return (hum and hum.Health > 0) or m:GetAttribute("Criatura") == true
end
local function pegada(pos)
	local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Size = Vector3.new(0.7, 0.05, 0.9); p.Material = Enum.Material.Neon; p.Color = GELO; p.Transparency = 0.35
	p.CFrame = CFrame.new(pos + Vector3.new(0, 0.03, 0)); p.Parent = pegadasPasta
	TweenService:Create(p, TweenInfo.new(8, Enum.EasingStyle.Linear), {Transparency = 1}):Play()
	task.delay(8.1, function() p:Destroy() end)
end
local rpChao = RaycastParams.new(); rpChao.FilterType = Enum.RaycastFilterType.Exclude
task.spawn(function()
	while lobo.Parent do
		task.wait(0.2)
		local t = workspace:GetServerTimeNow()
		local dono = souDono()
		local centro = lobo:GetPivot().Position
		local vistos = {}
		-- consulta espacial no raio do Instinto (90): o place tem milhoes de instancias, nunca varrer o Workspace inteiro
		local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Exclude; op.FilterDescendantsInstances = {lobo, pegadasPasta}
		local cand = {}
		for _, parte in ipairs(workspace:GetPartBoundsInRadius(centro, 90, op)) do
			local m = parte:FindFirstAncestorOfClass("Model")
			while m and not (m:FindFirstChildOfClass("Humanoid") or m:GetAttribute("Criatura")) do m = m:FindFirstAncestorOfClass("Model") end
			if m and not cand[m] then cand[m] = true end
		end
		for m in pairs(cand) do
			if inimigoVisivel(m) then
				vistos[m] = true
				local pos = (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart or {Position = m:GetPivot().Position}).Position
				-- marca 8 s: contorno + seta (so o dono que marcou)
				local marcado = dono and (m:GetAttribute("MarcaBoreal_Fim") or 0) > t and m:GetAttribute("MarcaBoreal_Dono") == jogador.UserId
				if marcado and not marcas[m] then
					local h = Instance.new("Highlight"); h.Adornee = m; h.FillTransparency = 1; h.OutlineColor = GELO; h.OutlineTransparency = 0.1
					h.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop; h.Parent = m
					local bb = Instance.new("BillboardGui"); bb.Size = UDim2.fromOffset(28, 28); bb.StudsOffsetWorldSpace = Vector3.new(0, 4.5, 0)
					bb.AlwaysOnTop = true; bb.Adornee = m:FindFirstChild("Head") or m.PrimaryPart
					local tx = Instance.new("TextLabel"); tx.Size = UDim2.fromScale(1, 1); tx.BackgroundTransparency = 1; tx.Text = "▼"
					tx.TextColor3 = GELO; tx.TextScaled = true; tx.Font = Enum.Font.GothamBold; tx.Parent = bb; bb.Parent = m
					marcas[m] = {h = h, bb = bb}
				elseif not marcado and marcas[m] then marcas[m].h:Destroy(); marcas[m].bb:Destroy(); marcas[m] = nil end
				-- pegadas dos inimigos a ate 90 studs (so o dono)
				if dono and (pos - centro).Magnitude <= 90 then
					local u = ultimoPasso[m]
					if not u or (Vector3.new(pos.X, 0, pos.Z) - Vector3.new(u.X, 0, u.Z)).Magnitude >= 2.5 then
						rpChao.FilterDescendantsInstances = {m, lobo, pegadasPasta}
						local r = workspace:Raycast(pos + Vector3.new(0, 2, 0), Vector3.new(0, -10, 0), rpChao)
						if r and u then pegada(r.Position) end
						ultimoPasso[m] = pos
					end
				end
				-- deteccao sob a neve: brilho azul no chao (so o dono)
				local det = dono and (m:GetAttribute("DetectadoBoreal_Fim") or 0) > t and m:GetAttribute("DetectadoBoreal_Dono") == jogador.UserId
				local luz = m:FindFirstChild("Deteccao_Boreal", true)
				if det and not luz then
					local at = Instance.new("Attachment"); at.Name = "Deteccao_Boreal"; at.Parent = m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart
					local pl = Instance.new("PointLight"); pl.Color = GELO; pl.Range = 6; pl.Brightness = 2; pl.Parent = at
				elseif not det and luz then luz:Destroy() end
			end
		end
		for m, mk in pairs(marcas) do if not vistos[m] then mk.h:Destroy(); mk.bb:Destroy(); marcas[m] = nil end end
	end
end)

-- Pelagem Polar: camuflagem (contraste cai em 1 s; volta em 0,3 s) -----------------------------------------------------------
local camuf = Instance.new("Highlight"); camuf.Name = "Camuflagem_Polar"; camuf.Adornee = lobo; camuf.FillColor = Color3.fromRGB(246, 249, 255)
camuf.FillTransparency = 1; camuf.OutlineTransparency = 1; camuf.DepthMode = Enum.HighlightDepthMode.Occluded; camuf.Enabled = false; camuf.Parent = lobo
lobo:GetAttributeChangedSignal("Camuflado"):Connect(function()
	if lobo:GetAttribute("Camuflado") then
		camuf.Enabled = true; TweenService:Create(camuf, TweenInfo.new(1), {FillTransparency = 0.55}):Play()
	else
		local tw = TweenService:Create(camuf, TweenInfo.new(0.3), {FillTransparency = 1}); tw:Play()
		tw.Completed:Once(function() if not lobo:GetAttribute("Camuflado") then camuf.Enabled = false end end)
	end
end)
