-- r5 (19/11): efeitos na escala da idade. Copia da r4: Kit_Cliente_r4.client.luau.
-- Kit_Cliente r4 (18/11: som e impacto da mordida; r3 ataque basico andando; r2 E4) (Script com RunContext = Client, Workspace.Teste_LoboArtico) - comandos e efeitos do KIT do Lobo Artico.
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
local SONS = {voo = id(9125648149), impacto = id(9114591164), ronco = id(9125443744), neve = id(9119316414), tinido = id(9114590297),
	-- r4 (18/11): mordida = "Creature Bite Pterodactyl Crunch" (ja usado nos dragoes do projeto), mais agudo para o lobo
	mordida = {id(9125467298), id(9125466463)}, acerto = id(9113445183)}
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
-- r3 (17/11): ATAQUE BASICO andando - clique esquerdo ataca (mordidas e garras em sequencia; segurar repete) e, se o
-- clique cair num inimigo, tambem trava o alvo. Celular: botao "Atacar" (segurar repete). O servidor decide tudo.
local segurando = false
local function atacar()
	if not souDono() then return end
	rede:FireServer("basico", direcao(), alvoTravado)
end
local function inimigoSobMouse()
	local m = UIS:GetMouseLocation(); local raio = camera:ViewportPointToRay(m.X, m.Y)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {lobo, jogador.Character}
	local r = workspace:Raycast(raio.Origin, raio.Direction * 300, rp)
	local alvo = r and r.Instance and r.Instance:FindFirstAncestorOfClass("Model")
	if alvo and (alvo:FindFirstChildOfClass("Humanoid") or alvo:GetAttribute("Criatura")) then return alvo end
end
local function comecarAtaque()
	if segurando then return end
	segurando = true
	task.spawn(function()
		while segurando and lobo.Parent do atacar(); task.wait(0.5) end
	end)
end
UIS.InputBegan:Connect(function(i, gp)
	if gp or i.UserInputType ~= Enum.UserInputType.MouseButton1 or not souDono() then return end
	local alvo = inimigoSobMouse()
	if alvo then alvoTravado = alvo; rede:FireServer("travar", alvo) end
	comecarAtaque()
end)
UIS.InputEnded:Connect(function(i) if i.UserInputType == Enum.UserInputType.MouseButton1 then segurando = false end end)
CAS:BindAction("Lobo_Ataque", function(_, e)
	if e == Enum.UserInputState.Begin then comecarAtaque() elseif e == Enum.UserInputState.End or e == Enum.UserInputState.Cancel then segurando = false end
	return Enum.ContextActionResult.Pass
end, true, Enum.KeyCode.ButtonR2)
CAS:SetTitle("Lobo_Ataque", "Atacar")
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
-- E4 (17/11): efeitos 100% pela referencia PREPARO/VOO/POUSO (mesmo efeito em todos os poderes) -----------------------------
--   casca do voo = malha Casca_Gelo (pele nos ossos) | rastro = particulas de lascas | pouso = coroa de cristais cravados,
--   lascas no ar e crosta rachada (moldes em FX_Boreal.Moldes) | olhos azul-gelo nos dois poderes.
local cascaMalha = fxPasta and fxPasta:FindFirstChild("Casca_Gelo")
local moldes = fxPasta and fxPasta:FindFirstChild("Moldes")
local SPRITE = id(89705690599635)   -- lasca enviada 17/11 (boreal/tex/LoboArtico_LascaGelo_sprite.png)
local olhos = {}
for _, lado in ipairs({{"Palpebra_Sup_E", -0.07}, {"Palpebra_Sup_D", 0.07}}) do
	local b = lobo:FindFirstChild(lado[1], true)
	if b then
		local p = Instance.new("Part"); p.Name = "Olho_Kit"; p.Shape = Enum.PartType.Ball; p.Size = Vector3.new(0.14, 0.14, 0.14)
		p.Material = Enum.Material.Neon; p.Color = GELO; p.Transparency = 1
		p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false; p.Parent = lobo
		table.insert(olhos, {p = p, b = b, dx = lado[2]})
	end
end
-- rastro: lascas e po saindo da anca durante o voo
-- preso no osso Quadril (Bone e um Attachment): as particulas ficam para tras sozinhas porque o lobo voa rapido
local atRastro = lobo:FindFirstChild("Quadril", true) or raiz
local function emissor(tam, vida, taxa, tex)
	local pe = Instance.new("ParticleEmitter"); pe.Texture = tex; pe.Color = ColorSequence.new(GELO, Color3.fromRGB(230, 248, 255))
	pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, tam), NumberSequenceKeypoint.new(1, tam * 0.15)})
	pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.05), NumberSequenceKeypoint.new(0.7, 0.3), NumberSequenceKeypoint.new(1, 1)})
	pe.Lifetime = NumberRange.new(vida * 0.6, vida); pe.Speed = NumberRange.new(1.5, 5); pe.SpreadAngle = Vector2.new(180, 180)
	pe.Rotation = NumberRange.new(0, 360); pe.RotSpeed = NumberRange.new(-180, 180); pe.Drag = 2; pe.LightEmission = 0.5
	pe.Acceleration = Vector3.new(0, -4, 0); pe.Rate = taxa; pe.Enabled = false; pe.Name = "Rastro_Gelo_Kit"; pe.Parent = atRastro
	return pe
end
local rastroLascas = emissor(0.8, 1.2, 160, SPRITE)          -- r2 (teste E4 no Studio): rastro estava ralo
local rastroPo = emissor(0.25, 1.0, 300, "rbxasset://textures/particles/sparkles_main.dds")
-- r7/r5 (19/11, idades): efeitos acompanham Escala (Idade_Servidor). As pecas do FX_Boreal ja encolhem com Model:ScaleTo,
-- mas os atributos dos espinhos (OffsetOsso/BaseLocal/TamanhoCheio), olhos e particulas sao numeros fixos do Adulto.
local function escLobo() return lobo:GetAttribute("Escala") or 1 end
local function escCF(cf, e) if typeof(cf) == "Vector3" then return cf * e end; return CFrame.new(cf.Position * e) * cf.Rotation end   -- BaseLocal e Vector3
local function escalarRastro()
	local e = escLobo()
	for _, par in ipairs({{rastroLascas, 0.8}, {rastroPo, 0.25}}) do
		par[1].Size = NumberSequence.new({NumberSequenceKeypoint.new(0, par[2] * e), NumberSequenceKeypoint.new(1, par[2] * 0.15 * e)})
		par[1].Speed = NumberRange.new(1.5 * e, 5 * e)
	end
end
lobo:GetAttributeChangedSignal("Escala"):Connect(escalarRastro); escalarRastro()
local function rastro(on) rastroLascas.Enabled = on; rastroPo.Enabled = on end
-- pouso: coroa + lascas + crosta (tudo local e curto; some sozinho)
local rpPouso = RaycastParams.new(); rpPouso.FilterType = Enum.RaycastFilterType.Exclude
local function chao(p)
	rpPouso.FilterDescendantsInstances = {lobo, jogador.Character}
	local r = workspace:Raycast(p + Vector3.new(0, 6, 0), Vector3.new(0, -20, 0), rpPouso)
	return r and r.Position or p
end
local function estilhacos(centro, raio, frente, escala)
	if not moldes then return end
	escala = escala or 1
	local ee = escLobo()          -- r5: distancias e particulas na escala da idade (os moldes ja encolhem com o modelo)
	local fx = Instance.new("Folder"); fx.Name = "Estilhacos_Gelo_Cliente"; fx.Parent = workspace
	local up = Vector3.yAxis
	frente = (frente and frente.Magnitude > 0.1) and Vector3.new(frente.X, 0, frente.Z).Unit or Vector3.zAxis
	local lado = frente:Cross(up)
	local c0 = chao(centro)
	local pecas = {}
	-- coroa cravada: 2 aneis elipticos alongados no sentido do lobo, inclinados para fora, maiores perto
	local aneis = {{2.0, 4.2, 20, 2.7}, {3.2, 5.6, 26, 1.6}}
	for ia, an in ipairs(aneis) do
		local n = math.floor(an[3] * escala + 0.5)
		for k = 1, n do
			local ang = 2 * math.pi * (k + (math.random() - 0.5) * 0.6) / n
			local d = (lado * math.cos(ang) * an[1] + frente * math.sin(ang) * an[2]) * escala * ee * (0.92 + math.random() * 0.2)
			local fora = d.Unit
			local h = an[4] * escala * (0.55 + math.random() * 0.45)
			local inc = (0.45 + math.random() * 0.4 + 0.25 * (ia - 1)) * 0.6
			local m = moldes:FindFirstChild("Molde_Coroa_" .. math.random(1, 3)):Clone()
			local base = chao(c0 + d) - up * 0.15
			local rot = CFrame.fromAxisAngle(up:Cross(fora), inc) * CFrame.Angles(0, math.random() * 6.28, 0)
			table.insert(pecas, {m = m, base = base, rot = rot, cheio = m.Size * h, atraso = (d.Magnitude / 6) * 0.08})
			m.Size = m.Size * 0.01; m.Transparency = 0.15; m.CFrame = CFrame.new(base); m.Parent = fx
		end
	end
	-- crosta rachada
	local cr = moldes:FindFirstChild("Molde_Crosta"):Clone()
	local esc = escala * 0.9
	cr.Size = Vector3.new(cr.Size.X * esc, math.max(cr.Size.Y, 0.05), cr.Size.Z * esc)
	cr.CFrame = CFrame.lookAt(c0 + up * 0.03, c0 + up * 0.03 + frente); cr.Transparency = 0.35; cr.Parent = fx
	-- lascas no ar
	local voando = {}
	for i = 1, math.floor(28 * escala + 0.5) do
		local m = moldes:FindFirstChild("Molde_Lasca_" .. math.random(1, 2)):Clone()
		local ang = math.random() * 6.28
		local dir = (lado * math.cos(ang) + frente * math.sin(ang) * 1.3).Unit
		local s = 0.15 + math.random() * 0.3
		m.Size = m.Size * s * escala; m.Transparency = 0.1
		m.CFrame = CFrame.new(c0 + (dir * (1 + math.random() * 1.5) + up * 0.6) * ee) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)
		m.Parent = fx
		table.insert(voando, {m = m, v = (dir * (9 + math.random() * 10) + up * (6 + math.random() * 9)) * math.sqrt(ee), w = Vector3.new(math.random() * 8 - 4, math.random() * 8 - 4, 0)})
	end
	local at = Instance.new("Attachment"); at.WorldPosition = c0 + up * 0.5; at.Parent = workspace.Terrain
	local po = Instance.new("ParticleEmitter"); po.Texture = "rbxasset://textures/particles/sparkles_main.dds"; po.Color = ColorSequence.new(GELO)
	po.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.3 * ee), NumberSequenceKeypoint.new(1, 0)}); po.Lifetime = NumberRange.new(0.4, 0.9)
	po.Speed = NumberRange.new(8 * ee, 18 * ee); po.SpreadAngle = Vector2.new(80, 80); po.EmissionDirection = Enum.NormalId.Top; po.Drag = 3
	po.Acceleration = Vector3.new(0, -20, 0); po.LightEmission = 0.6; po.Rate = 0; po.Parent = at; po:Emit(math.floor(90 * escala))
	local t0 = os.clock()
	local con; con = RunService.Heartbeat:Connect(function(dt)
		local t = os.clock() - t0
		for _, p in ipairs(pecas) do       -- cresce 0,12 s (saida rapida), fica, afunda e some 0,6 s
			local g = math.clamp((t - p.atraso) / 0.12, 0, 1); g = 1 - (1 - g) ^ 3
			local sai = math.clamp((t - 1.1) / 0.6, 0, 1)
			local tam = p.cheio * math.max(g, 0.01)
			p.m.Size = tam
			p.m.CFrame = CFrame.new(p.base) * p.rot * CFrame.new(0, tam.Y / 2 - sai * tam.Y * 0.6, 0)
			p.m.Transparency = 0.15 + 0.85 * sai
		end
		for _, l in ipairs(voando) do
			l.v += Vector3.new(0, -45, 0) * dt
			l.m.CFrame = (l.m.CFrame + l.v * dt) * CFrame.Angles(l.w.X * dt, l.w.Y * dt, 0)
			l.m.Transparency = math.clamp((t - 0.35) / 0.4, 0.1, 1)
		end
		cr.Transparency = 0.35 + 0.65 * math.clamp((t - 0.8) / 1.6, 0, 1)
		if t > 2.5 then con:Disconnect(); fx:Destroy(); at:Destroy() end
	end)
end

local function uivoAtivo() return (lobo:GetAttribute("BonusVel_Uivo") or 0) > 0 end
local estado = {poder = nil, t0 = 0, fimEspinho = nil, flash = 0}
local fovBase = nil
lobo:GetAttributeChangedSignal("PoderAtivo"):Connect(function()
	local p = lobo:GetAttribute("PoderAtivo")
	if p then
		estado.poder = p; estado.t0 = os.clock(); estado.fimEspinho = nil
		if p == "Cometa" then
			if not cascaMalha then casca.FillColor = GELO; casca.FillTransparency = 1; casca.Enabled = true end   -- E4: malha real se houver
			som(SONS.voo, 0.7, 1.15, raiz, 2)
		elseif p == "Avalanche" then
			casca.FillColor = Color3.fromRGB(245, 248, 255); casca.FillTransparency = 1; casca.Enabled = true
			estado.ronco = som(SONS.ronco, 0.45, 1.25, raiz, 4)
		end
	else
		if estado.poder then estado.fimEspinho = os.clock() end        -- E4: espinhos/linhas/olhos recolhem nos dois poderes
		rastro(false)
		if cascaMalha then cascaMalha.Transparency = 1 end
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
		if cascaMalha then
			-- E4: casca de gelo vitreo so no VOO (forma em 0,15 s); no pouso ela "vira" os estilhacos
			if fase == "Voo" then
				estado.tVoo = estado.tVoo or os.clock()
				cascaMalha.Transparency = 1 - 0.62 * math.clamp((os.clock() - estado.tVoo) / 0.15, 0, 1)
				rastro(true)
			else
				estado.tVoo = nil; cascaMalha.Transparency = 1; rastro(false)
			end
		else
			casca.FillTransparency = (fase == "Voo") and 0.45 or (fase == "Preparo" and 0.8 or 0.45)
		end
	elseif estado.poder == "Avalanche" then
		casca.FillTransparency = 1 - math.clamp(t / 0.25, 0, 1) * 0.5
	end
	-- linhas do corpo e espinhos no Cometa (se o Uivo nao estiver cuidando deles)
	if not uivoAtivo() then
		local s = 0
		if estado.poder then s = math.clamp(t / 0.25, 0, 1)
		elseif estado.fimEspinho then s = 1 - math.clamp((os.clock() - estado.fimEspinho) / 0.8, 0, 1); if s <= 0 then estado.fimEspinho = nil end end
		if corpoSA and (s > 0 or estado.poder) then corpoSA.EmissiveStrength = 12 * s end
		for _, o in ipairs(olhos) do
			if s < 0.02 then o.p.Transparency = 1 else local ee = escLobo(); o.p.Size = Vector3.new(0.14, 0.14, 0.14) * ee; o.p.CFrame = o.b.TransformedWorldCFrame * CFrame.new(o.dx * ee, 0, 0); o.p.Transparency = 1 - 0.9 * s end
		end
		for _, e in ipairs(espinhos) do
			if s < 0.02 or not e.b then
				if e.p.Transparency ~= 1 and not uivoAtivo() then e.p.Transparency = 1 end
			else
				local ee = escLobo()
				local cheio = e.b.TransformedWorldCFrame * escCF(e.off, ee)
				local base = cheio * escCF(e.base, ee)
				e.p.Size = e.cheio * ee * s; e.p.CFrame = CFrame.new(base + (cheio.Position - base) * s) * cheio.Rotation
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
local function escLobo() return lobo:GetAttribute("Escala") or 1 end
fxRede.OnClientEvent:Connect(function(tipo, a, b, c, d)
	if tipo == "basico" then
		-- r4: estalo da mordida saindo da cabeca, no tempo do fechamento da boca (contato q6 = 0,2 s)
		task.delay(0.16, function()
			local s = SONS.mordida[math.random(1, #SONS.mordida)]
			som(s, 0.55, (1.35 + math.random() * 0.15) / math.sqrt(escLobo()), raiz, 2)
		end)
		return
	elseif tipo == "basico_acerto" then
		-- r4: impacto no ALVO: pancada surda + pequena nuvem de neve/geada no ponto da mordida (regra: so neve fora do corpo)
		if typeof(a) ~= "Vector3" then return end
		local p = typeof(b) == "Vector3" and (a:Lerp(b, 0.55) + Vector3.new(0, 0.6, 0)) or a
		local base = Instance.new("Part"); base.Anchored = true; base.CanCollide = false; base.CanQuery = false; base.CanTouch = false
		base.Transparency = 1; base.Size = Vector3.new(0.2, 0.2, 0.2); base.Position = p; base.Parent = workspace
		local pe = Instance.new("ParticleEmitter")
		pe.Texture = "rbxasset://textures/particles/smoke_main.dds"; pe.Color = ColorSequence.new(Color3.fromRGB(235, 245, 255))
		local ee = escLobo()
		pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.5 * ee), NumberSequenceKeypoint.new(1, 1.6 * ee)})
		pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.35), NumberSequenceKeypoint.new(1, 1)})
		pe.Lifetime = NumberRange.new(0.35, 0.6); pe.Speed = NumberRange.new(3, 6); pe.SpreadAngle = Vector2.new(70, 70)
		pe.Drag = 5; pe.Rate = 0; pe.Parent = base
		local pg = Instance.new("ParticleEmitter")
		pg.Texture = "rbxasset://textures/particles/sparkles_main.dds"; pg.Color = ColorSequence.new(GELO)
		pg.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.12), NumberSequenceKeypoint.new(1, 0)})
		pg.Lifetime = NumberRange.new(0.15, 0.3); pg.Speed = NumberRange.new(6, 10); pg.SpreadAngle = Vector2.new(120, 120)
		pg.Drag = 8; pg.Rate = 0; pg.LightEmission = 0.5; pg.Parent = base
		pe:Emit(10); pg:Emit(14)
		som(SONS.acerto, 0.5, 1.25, base, 2)
		if souDono() then tremer(0.35, 0.12) end
		task.delay(1.2, function() base:Destroy() end)
		return
	elseif tipo == "cometa_impacto" then
		-- casca estoura: flash rapido no corpo + estilhacos finos curtos (0,3 s) + vidro
		rastro(false); if cascaMalha then cascaMalha.Transparency = 1 end
		if moldes then
			estilhacos(a, b, lobo:GetPivot().LookVector, 1)          -- E4: coroa + lascas + crosta (referencia POUSO)
			som(SONS.impacto, 0.8, 0.9, raiz, 3); som(SONS.tinido, 0.6, 0.8, raiz, 2)
			tremer(1.6, 0.25)
			return
		end
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
		if moldes and typeof(a) == "Vector3" then estilhacos(a + (typeof(b) == "Vector3" and b * 3 or Vector3.zero), 4, b, 0.6) end   -- E4: mesmo estouro, menor
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
