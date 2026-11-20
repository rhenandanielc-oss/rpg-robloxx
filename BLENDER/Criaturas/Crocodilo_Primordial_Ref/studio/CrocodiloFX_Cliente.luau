-- CrocodiloFX_Cliente (LocalScript em StarterPlayer.StarterPlayerScripts do place de TESTE RBX Crocodilo) - P4 16/11
-- PREVIA DE TESTE dos efeitos do Crocodilo Primordial. So visual: o servidor (PoderesTeste) decide agua, alcance, alvo,
-- energia, dano, estados e soltura; aqui so se desenha o que ele anuncia (RemoteEvent Crocodilo_FX e atributos no modelo).
-- So reacao FISICA da agua e da lama (ondulacao, rastro, bolhas, respingos): elemento Agua, visual natural sem brilho (20/11). Tudo
-- temporario, limpo ao fim/cancelamento. Orcamento (ref. 5.10): so ate 150 studs; poucas pecas; metade no celular.
local RS = game:GetService("RunService"); local TS = game:GetService("TweenService")
local UIS = game:GetService("UserInputService"); local Debris = game:GetService("Debris")
local T = workspace:WaitForChild("Teste_Crocodilo"); local croc = T:WaitForChild("Crocodilo_Primordial")
local ev = game:GetService("ReplicatedStorage"):WaitForChild("Crocodilo_FX")
local CELULAR = UIS.TouchEnabled and not UIS.KeyboardEnabled
local ESCALA = CELULAR and 0.5 or 1
local pasta = Instance.new("Folder"); pasta.Name = "FX_Cliente_Crocodilo"; pasta.Parent = workspace
local cam = workspace.CurrentCamera
local function perto(pos) return (cam.CFrame.Position - pos).Magnitude <= 150 end
local function osso(n) return croc:FindFirstChild(n, true) end

-- anel fino na superficie (SurfaceGui com UIStroke = traco constante enquanto cresce)
local function anel(pos, r0, r1, dur, alfa, espessura)
	if not perto(pos) then return end
	local p = Instance.new("Part"); p.Name = "FX_Anel"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Transparency = 1; p.Size = Vector3.new(r0 * 2, 0.05, r0 * 2); p.CFrame = CFrame.new(pos + Vector3.new(0, 0.06, 0))
	local sg = Instance.new("SurfaceGui"); sg.Face = Enum.NormalId.Top; sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 24; sg.LightInfluence = 1; sg.Parent = p
	local f = Instance.new("Frame"); f.Size = UDim2.fromScale(1, 1); f.BackgroundTransparency = 1; f.Parent = sg
	Instance.new("UICorner", f).CornerRadius = UDim.new(0.5, 0)
	local st = Instance.new("UIStroke"); st.Color = Color3.fromRGB(214, 226, 214); st.Thickness = espessura or 5; st.Transparency = alfa; st.Parent = f
	p.Parent = pasta
	local ti = TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	TS:Create(p, ti, {Size = Vector3.new(r1 * 2, 0.05, r1 * 2)}):Play(); TS:Create(st, ti, {Transparency = 1}):Play()
	Debris:AddItem(p, dur + 0.1)
end
local function ondulacao(pos, forca)
	forca = forca or 1
	for k = 0, 2 do
		task.delay(k * 0.18, function() anel(pos, 1.5 + k, (7 + 4 * k) * forca, 1.3 + 0.2 * k, 0.25 + 0.15 * k, 6 - k) end)
	end
end
-- poucas bolhas: esferas pequenas que sobem e somem na superficie
local function bolha(pos, sup)
	if not perto(pos) then return end
	local b = Instance.new("Part"); b.Name = "FX_Bolha"; b.Shape = Enum.PartType.Ball; b.Anchored = true; b.CanCollide = false
	b.CanQuery = false; b.CanTouch = false; b.CastShadow = false; b.Material = Enum.Material.Glass; b.Color = Color3.fromRGB(230, 240, 235)
	b.Transparency = 0.45; local r = 0.18 + math.random() * 0.22; b.Size = Vector3.new(r, r, r); b.Position = pos; b.Parent = pasta
	local subida = math.max(0.2, sup - pos.Y); local dur = subida / 3.2
	TS:Create(b, TweenInfo.new(dur, Enum.EasingStyle.Linear), {Position = Vector3.new(pos.X + (math.random() - 0.5), sup, pos.Z + (math.random() - 0.5))}):Play()
	task.delay(dur, function() if b.Parent then anel(Vector3.new(b.Position.X, sup, b.Position.Z), 0.2, 1.2, 0.6, 0.5, 3); b:Destroy() end end)
end
-- 20/11 KIT OFICIAL (usuario): elemento AGUA com visual NATURAL, SEM BRILHO. Respingo = gotas de agua de verdade jogadas
-- para cima que caem pela gravidade (LightEmission 0, cor de agua turva do pantano); espuma = respingo claro e baixo.
local function respingo(pos, n, forca, cor)
	if not perto(pos) then return end
	forca = forca or 1
	local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain
	local e = Instance.new("ParticleEmitter"); e.Name = "FX_Respingo"; e.Texture = "rbxasset://textures/particles/smoke_main.dds"
	e.Color = ColorSequence.new(cor or Color3.fromRGB(196, 210, 200)); e.LightEmission = 0; e.LightInfluence = 1
	e.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.25), NumberSequenceKeypoint.new(0.7, 0.5), NumberSequenceKeypoint.new(1, 1)})
	e.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.6 * forca), NumberSequenceKeypoint.new(1, 1.4 * forca)})   -- r2: 0,25-0,6 sumia na tela
	e.Lifetime = NumberRange.new(0.6, 1.0); e.Speed = NumberRange.new(10 * forca, 18 * forca); e.SpreadAngle = Vector2.new(35, 35)
	e.EmissionDirection = Enum.NormalId.Top; e.Acceleration = Vector3.new(0, -workspace.Gravity * 0.35, 0); e.Drag = 0.6
	e.Rotation = NumberRange.new(0, 360); e.Enabled = false; e.Parent = a
	e:Emit(math.max(1, math.floor(n * ESCALA))); Debris:AddItem(a, 1.2)
end
-- aviso de recusa (raso / sem agua): texto curto sobre a cabeca por 1,8 s
local function recusa(pos, texto)
	local cab = osso("Cabeca"); if not cab then return end
	local bb = Instance.new("BillboardGui"); bb.Name = "FX_Recusa"; bb.Size = UDim2.fromOffset(260, 40); bb.StudsOffsetWorldSpace = Vector3.new(0, 5, 0)
	bb.Adornee = croc.PrimaryPart or croc:FindFirstChildWhichIsA("BasePart", true); bb.AlwaysOnTop = true
	local t = Instance.new("TextLabel"); t.Size = UDim2.fromScale(1, 1); t.BackgroundColor3 = Color3.fromRGB(120, 30, 20); t.BackgroundTransparency = 0.2
	t.TextColor3 = Color3.new(1, 1, 1); t.Font = Enum.Font.GothamBold; t.TextScaled = true; t.Text = "✕ " .. texto; t.Parent = bb
	Instance.new("UICorner", t).CornerRadius = UDim.new(0, 8); bb.Parent = pasta
	Debris:AddItem(bb, 1.8)
end

-- laco: bolhas e rastro enquanto o servidor marca Submerso/Movendo
local acc, accR = 0, 0
RS.Heartbeat:Connect(function(dt)
	if not croc:GetAttribute("Submerso") then return end
	local sup = croc:GetAttribute("Superficie"); if not sup then return end
	local cab = osso("Cabeca"); local cauda = osso("Cauda5"); if not cab then return end
	local movendo = croc:GetAttribute("Movendo")
	acc += dt * (movendo and 5 or 1.5) * ESCALA
	while acc >= 1 do
		acc -= 1
		local fonte = (math.random() < 0.6 or not cauda) and cab or cauda
		bolha(fonte.TransformedWorldCFrame.Position + Vector3.new(0, 1, 0), sup)
	end
	if movendo then                                            -- rastro: aneis rasos acima da cabeca, ficando para tras
		accR += dt
		if accR >= 0.3 / ESCALA then
			accR = 0; local p = cab.TransformedWorldCFrame.Position
			anel(Vector3.new(p.X, sup, p.Z), 1.0, 5.5, 1.6, 0.55, 4)
		end
	end
end)

-- ---------------------------------------------------------------- ONDA 3D (20/11, usuario: "onda 3D + espuma")
-- Parede de agua REAL em anel: segmentos 3D (vidro esverdeado do pantano; em terra, lama) que nascem abaixo da superficie,
-- sobem rapido, avancam ate o raio e desabam para a frente, com crista de espuma branca e borrifos saindo da crista.
-- Sem aneis desenhados e sem brilho (LightEmission 0). O raio/duracao vem do servidor (mesma frente que da o dano).
local function onda3D(c0, R, dur, naAgua)
	if not perto(c0) then return end
	local N = CELULAR and 14 or 26
	local corA = naAgua and Color3.fromRGB(104, 146, 140) or Color3.fromRGB(92, 72, 50)   -- r2: agua turva clara (o vidro sumia na agua)
	local corE = naAgua and Color3.fromRGB(232, 238, 234) or Color3.fromRGB(128, 106, 78)
	local hMax = naAgua and math.clamp(R * 0.22, 1.2, 4.6) or math.clamp(R * 0.14, 0.6, 1.6)   -- r2 usuario: 'a agua subir mais'
	local transpA = naAgua and 0.35 or 0.02
	local transpE = naAgua and 0.25 or 0.05
	local segs = {}
	for i = 1, N do
		local a = Instance.new("Part"); a.Name = "FX_Onda"; a.Anchored = true; a.CanCollide = false; a.CanQuery = false; a.CanTouch = false
		a.CastShadow = false; a.Material = naAgua and Enum.Material.SmoothPlastic or Enum.Material.Mud; a.Color = corA
		a.Transparency = transpA; a.Reflectance = naAgua and 0.12 or 0; a.Size = Vector3.new(0.2, 0.2, 0.2); a.CFrame = CFrame.new(c0)
		local e = Instance.new("Part"); e.Name = "FX_Espuma"; e.Anchored = true; e.CanCollide = false; e.CanQuery = false; e.CanTouch = false
		e.CastShadow = false; e.Material = naAgua and Enum.Material.SmoothPlastic or Enum.Material.Mud; e.Color = corE
		e.Transparency = transpE; e.Size = Vector3.new(0.2, 0.2, 0.2); e.CFrame = CFrame.new(c0)
		a.Parent = pasta; e.Parent = pasta
		local em
		if i % (CELULAR and 4 or 3) == 0 then                                        -- borrifo da crista (gotas que caem)
			em = Instance.new("ParticleEmitter"); em.Texture = "rbxasset://textures/particles/smoke_main.dds"; em.Color = ColorSequence.new(corE)
			em.LightEmission = 0; em.LightInfluence = 1; em.Transparency = NumberSequence.new(0.3, 1)
			em.Size = NumberSequence.new(naAgua and 0.35 or 0.25, naAgua and 0.9 or 0.5); em.Lifetime = NumberRange.new(0.35, 0.65)
			em.Speed = NumberRange.new(3, 7); em.SpreadAngle = Vector2.new(30, 30); em.EmissionDirection = Enum.NormalId.Front
			em.Acceleration = Vector3.new(0, -workspace.Gravity * 0.35, 0); em.Rate = (naAgua and 30 or 14) * ESCALA; em.Parent = e
		end
		segs[i] = {a, e, 2 * math.pi * (i - 0.5) / N, em}
	end
	local t = 0
	local con; con = RS.RenderStepped:Connect(function(dt)
		t += dt; local u = math.min(1, t / dur)
		local r = 0.8 + (R - 0.8) * (1 - (1 - u) * (1 - u))                         -- mesma frente que o servidor usa
		local sobe = math.sin(math.pi * math.min(1, u * 1.1)) ^ 0.7 * (1 - 0.3 * u)   -- sobe rapido, desaba no fim
		local h = math.max(0.05, hMax * sobe)
		local arco = 2 * math.pi * r / N * 1.14; local esp = 0.6 + 0.7 * (1 - u)
		local inc = math.rad(18 + 32 * u)                                            -- a crista tomba para a frente
		local fade = u > 0.7 and (u - 0.7) / 0.3 or 0
		for _, sg in ipairs(segs) do
			local dir = Vector3.new(math.cos(sg[3]), 0, math.sin(sg[3])); local base = c0 + dir * r - Vector3.new(0, 0.35, 0)
			local cf = CFrame.lookAt(base, base + dir) * CFrame.Angles(-inc, 0, 0)
			sg[1].Size = Vector3.new(arco, h, esp); sg[1].CFrame = cf * CFrame.new(0, h / 2, 0)
			sg[1].Transparency = transpA + (1 - transpA) * fade
			sg[2].Size = Vector3.new(arco * 1.02, 0.12 + 0.14 * (1 - u), esp * 0.55); sg[2].CFrame = cf * CFrame.new(0, h, -esp * 0.2)   -- r2: espuma fina so na crista
			sg[2].Transparency = transpE + (1 - transpE) * fade
			if sg[4] then sg[4].Enabled = u < 0.65 end
		end
		if u >= 1 then
			con:Disconnect()
			for _, sg in ipairs(segs) do sg[1]:Destroy(); sg[2]:Destroy() end
		end
	end)
end
local function lamaBaixa(pos, n, forca)                                              -- po/lama baixa (pouso em terra)
	if not perto(pos) then return end
	local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain
	local e = Instance.new("ParticleEmitter"); e.Texture = "rbxasset://textures/particles/smoke_main.dds"; e.Color = ColorSequence.new(Color3.fromRGB(120, 104, 78))
	e.LightEmission = 0; e.Transparency = NumberSequence.new(0.4, 1); e.Size = NumberSequence.new(1.5 * forca, 4 * forca); e.Lifetime = NumberRange.new(0.6, 1.0)
	e.Speed = NumberRange.new(5 * forca, 10 * forca); e.SpreadAngle = Vector2.new(80, 10); e.Rotation = NumberRange.new(0, 360)
	e.Acceleration = Vector3.new(0, -4, 0); e.Drag = 3; e.Enabled = false; e.Parent = a
	e:Emit(math.floor(n * ESCALA)); Debris:AddItem(a, 1.3)
end

-- ---------------------------------------------------------------- EMBOSCADA (sem giro, 20/11)
-- antes: agua escurece em volta e poucas bolhas sobem (silencioso); saida: a agua EXPLODE (respingo alto + onda pequena);
-- no ar: agua escorrendo do corpo; pouso: na agua respingo + onda, em terra lama baixa. Nada brilha.
local function discoEscuro(pos, raio, dur)
	if not perto(pos) then return end
	local p = Instance.new("Part"); p.Name = "FX_AguaEscura"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Shape = Enum.PartType.Cylinder; p.Material = Enum.Material.SmoothPlastic; p.Color = Color3.fromRGB(18, 26, 18)
	p.Transparency = 1; p.Size = Vector3.new(0.05, raio * 2, raio * 2); p.CFrame = CFrame.new(pos + Vector3.new(0, 0.04, 0)) * CFrame.Angles(0, 0, math.rad(90)); p.Parent = pasta
	TS:Create(p, TweenInfo.new(dur * 0.4), {Transparency = 0.55}):Play()
	task.delay(dur * 0.5, function() if p.Parent then TS:Create(p, TweenInfo.new(dur * 0.5), {Transparency = 1}):Play() end end)
	Debris:AddItem(p, dur + 0.1)
end
local escorreFX = {}
local function escorrer(on)                                                          -- agua escorrendo do corpo no ar
	for _, o in ipairs(escorreFX) do if o.Parent then o.Enabled = false; Debris:AddItem(o, 1.2) end end
	escorreFX = {}
	if not on then return end
	for _, n in ipairs({"Coluna1", "Coluna2", "Pelve", "Cauda3", "Pescoco", "Cabeca"}) do
		local b = osso(n); if b then
			local e = Instance.new("ParticleEmitter"); e.Name = "FX_Escorre"; e.Texture = "rbxasset://textures/particles/smoke_main.dds"
			e.Color = ColorSequence.new(Color3.fromRGB(196, 210, 200)); e.LightEmission = 0; e.LightInfluence = 1; e.Transparency = NumberSequence.new(0.3, 1)
			e.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.4), NumberSequenceKeypoint.new(1, 0.15)})
			e.Lifetime = NumberRange.new(0.4, 0.7); e.Rate = 30 * ESCALA; e.Speed = NumberRange.new(1, 3); e.SpreadAngle = Vector2.new(180, 180)
			e.Acceleration = Vector3.new(0, -60, 0); e.Drag = 1; e.Parent = b; table.insert(escorreFX, e)
		end
	end
end
croc:GetAttributeChangedSignal("NoAr"):Connect(function() escorrer(croc:GetAttribute("NoAr") == true) end)
local function embAntes(pos)
	discoEscuro(pos, 10, 1.0)
	for k = 1, math.floor(6 * ESCALA) do task.delay(k * 0.06, function() bolha(pos + Vector3.new(math.random() * 6 - 3, -3 - math.random() * 2, math.random() * 6 - 3), pos.Y) end) end
end
local function embSaida(pos, look, naAgua)
	if not naAgua then return end
	respingo(pos, 60, 1.8); onda3D(pos, 7, 0.8, true)
end
local function embPouso(pos, raio, naAgua)
	if naAgua then respingo(pos, 44, 1.6); onda3D(pos, 6, 0.6, true)
	else lamaBaixa(pos, 22, 1.0); onda3D(pos, 3.5, 0.45, false) end
end

-- ---------------------------------------------------------------- Cauda de Mare e Escamas Grossas
-- cauda: durante a varrida a ponta da cauda levanta agua (ou lama) de verdade; no impacto o servidor manda a ONDA REAL
-- (mesmo raio/duracao do dano): onda 3D + respingo alto no centro. Escamas: borrifo curto de agua no ponto do golpe.
local caudaCon
croc:GetAttributeChangedSignal("CaudaVarre"):Connect(function()
	local modo = croc:GetAttribute("CaudaVarre")
	if caudaCon then caudaCon:Disconnect(); caudaCon = nil end
	if not modo then return end
	local nivel = croc:GetAttribute("Nivel") or 0; local acc = 0
	caudaCon = RS.Heartbeat:Connect(function(dt)
		acc += dt; if acc < 0.07 / ESCALA then return end; acc = 0
		local b = osso("Cauda8"); if not b then return end
		local p = b.TransformedWorldCFrame.Position
		if modo == "agua" then respingo(Vector3.new(p.X, nivel, p.Z), 5, 0.7)
		else respingo(Vector3.new(p.X, nivel, p.Z), 3, 0.5, Color3.fromRGB(120, 100, 72)) end
	end)
end)
local function ondaCauda(pos, raio, dur, naAgua)
	onda3D(pos, raio, dur, naAgua)
	if naAgua then respingo(pos, 70, 2.3) else respingo(pos, 18, 0.9, Color3.fromRGB(110, 90, 64)); lamaBaixa(pos, 10, 0.7) end
end
local function escamasPulso(pos)
	if not perto(pos) then return end
	respingo(pos, 18, 0.8)                                                           -- borrifo da couraca molhada
end

ev.OnClientEvent:Connect(function(tipo, a, b, c, d)
	if tipo == "ondulacao" then ondulacao(a, b)
	elseif tipo == "recusa" then recusa(a, b)
	elseif tipo == "giro_antes" then embAntes(a)
	elseif tipo == "emb_saida" then embSaida(a, b, c)
	elseif tipo == "giro_pouso" then embPouso(a, b, c)
	elseif tipo == "onda" then ondaCauda(a, b, c, d)
	elseif tipo == "escamas_pulso" then escamasPulso(a)
	elseif tipo == "limpar" then pasta:ClearAllChildren()
	end
end)
