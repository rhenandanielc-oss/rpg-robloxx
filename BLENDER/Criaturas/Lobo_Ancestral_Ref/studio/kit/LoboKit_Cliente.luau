-- LoboKit_Cliente (LocalScript em StarterPlayer.StarterPlayerScripts) - entrada, HUD minima e efeitos do kit (v6.2; efeitos r3 17/11: so vento fora do corpo)
-- Natureza do Lobo Ancestral (prototipo, place isolado, 15/11/2026). Fonte: studio/kit/LoboKit_Cliente.luau.
-- O cliente so PEDE (PedidoKit) e mostra; dano, alvo, alcance, recarga e bonus sao decididos no servidor.
-- Teclas (prototipo): Z = Salto Predatorio (alvo sob o mouse; sem alvo = ponto do mouse no chao), X = Uivo Ancestral,
-- C = Investida (direcao do mouse no chao),
-- V = Mordida, B = Garra (basicos, fora dos slots). Sons: nao ha sons do lobo no projeto ainda (pendente).
local Players = game:GetService("Players")
local UIS = game:GetService("UserInputService")
local Debris = game:GetService("Debris")
local TweenService = game:GetService("TweenService")
local Rep = game:GetService("ReplicatedStorage")
local PASTA = Rep:WaitForChild("LoboAncestral")
local REM = PASTA:WaitForChild("Remotes")
local PEDIDO, EVENTO = REM:WaitForChild("PedidoKit"), REM:WaitForChild("EventoKit")
local eu = Players.LocalPlayer
local mouse = eu:GetMouse()
local AREA = workspace:WaitForChild("Teste_LoboAncestral")

local function meuLobo()
	for _, m in ipairs(AREA:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("DonoUserId") == eu.UserId then return m end
	end
end
-- HUD minima: estado, energia, bonus e ultima resposta
local gui = Instance.new("ScreenGui"); gui.Name = "LoboKitHUD"; gui.ResetOnSpawn = false; gui.Parent = eu:WaitForChild("PlayerGui")
local txt = Instance.new("TextLabel"); txt.Size = UDim2.new(0, 360, 0, 92); txt.Position = UDim2.new(0, 12, 1, -104)
txt.BackgroundTransparency = 0.45; txt.BackgroundColor3 = Color3.fromRGB(20, 26, 20); txt.TextColor3 = Color3.fromRGB(225, 235, 215)
txt.TextXAlignment = Enum.TextXAlignment.Left; txt.TextYAlignment = Enum.TextYAlignment.Top; txt.Font = Enum.Font.Gotham; txt.TextSize = 13
txt.Text = "Lobo Ancestral"; txt.Parent = gui
local ultima = ""
task.spawn(function()
	while true do
		local m = meuLobo()
		if m then
			txt.Text = string.format("Lobo Ancestral  Vida %s  Energia %s  %s\nT trava | Z Salto | X Uivo | C Investida | V/B basicos\nBonus: %s  (vel x%.2f, esquiva %.0f%%, dano x%.2f)\n%s",
				tostring(m:GetAttribute("Vida")), tostring(m:GetAttribute("Energia")), m:GetAttribute("Noite") and "NOITE" or "dia",
				(m:GetAttribute("Bonus") or "") ~= "" and m:GetAttribute("Bonus") or "-",
				m:GetAttribute("VelMult") or 1, (m:GetAttribute("Esquiva") or 0) * 100, m:GetAttribute("DanoMult") or 1, ultima)
		end
		task.wait(0.2)
	end
end)

local function alvoValidoCli(m)
	local pa = AREA:FindFirstChild("Alvos")
	local h = m and m:FindFirstChildOfClass("Humanoid")
	return m ~= nil and pa ~= nil and m:IsDescendantOf(pa) and h ~= nil and h.Health > 0
end
local function alvoSobMouse()
	local t = mouse.Target
	local m = t and t:FindFirstAncestorOfClass("Model")
	if alvoValidoCli(m) then return m end
	return nil
end
-- mira (§1 do documento de poderes): ALVO TRAVADO -> MOUSE -> CAMERA. T trava o alvo valido mais proximo num cone frontal
-- de 60 graus (da camera) ate 40 studs do lobo; T de novo destrava. O servidor valida tudo de novo (alcance, linha de visao).
local travado, marcaTrava = nil, nil
local function destravar() travado = nil; if marcaTrava then marcaTrava:Destroy(); marcaTrava = nil end end
local function travar(m)
	destravar()
	local cam = workspace.CurrentCamera; local frente = Vector3.new(cam.CFrame.LookVector.X, 0, cam.CFrame.LookVector.Z).Unit
	local p = m:GetPivot().Position; local melhor, md = nil, math.huge
	local pa = AREA:FindFirstChild("Alvos")
	for _, a in ipairs(pa and pa:GetChildren() or {}) do
		if alvoValidoCli(a) then
			local d = a:GetPivot().Position - p; local dh = Vector3.new(d.X, 0, d.Z)
			if dh.Magnitude <= 40 and dh.Magnitude > 0.1 and math.deg(math.acos(math.clamp(dh.Unit:Dot(frente), -1, 1))) <= 30 and dh.Magnitude < md then
				melhor, md = a, dh.Magnitude
			end
		end
	end
	if not melhor then ultima = "Trava: nenhum alvo a frente (40 studs, 60 graus)"; return end
	travado = melhor
	marcaTrava = Instance.new("Highlight"); marcaTrava.Name = "TravaLobo"; marcaTrava.FillTransparency = 1
	marcaTrava.OutlineColor = Color3.fromRGB(235, 235, 220); marcaTrava.OutlineTransparency = 0.35; marcaTrava.Parent = melhor
	ultima = "Alvo travado: " .. melhor.Name
end
local function pontoMira(m)
	if travado and alvoValidoCli(travado) then return travado end
	if travado then destravar() end
	if UIS.MouseEnabled then return alvoSobMouse() or mouse.Hit.Position end
	local cam = workspace.CurrentCamera                                       -- celular/controle: para onde a camera olha
	local f = Vector3.new(cam.CFrame.LookVector.X, 0, cam.CFrame.LookVector.Z)
	return m:GetPivot().Position + (f.Magnitude > 0.01 and f.Unit or m:GetPivot().LookVector) * 30
end
UIS.InputBegan:Connect(function(inp, gp)
	if gp then return end
	local m = meuLobo(); if not m then return end
	local k = inp.KeyCode
	if k == Enum.KeyCode.T then if travado then destravar(); ultima = "Alvo destravado" else travar(m) end
	elseif k == Enum.KeyCode.Z then PEDIDO:FireServer(m, "SaltoPredatorio", pontoMira(m))
	elseif k == Enum.KeyCode.X then PEDIDO:FireServer(m, "UivoAncestral")
	elseif k == Enum.KeyCode.C then
		local alvo = pontoMira(m)
		local pt = typeof(alvo) == "Instance" and alvo:GetPivot().Position or alvo
		local d = pt - m:GetPivot().Position
		PEDIDO:FireServer(m, "Investida", Vector3.new(d.X, 0, d.Z))
	elseif k == Enum.KeyCode.V then PEDIDO:FireServer(m, "Mordida")
	elseif k == Enum.KeyCode.B then PEDIDO:FireServer(m, "Garra") end
end)

-- ------------------------------------------------------------------ efeitos r3 (17/11/2026) [PROPOSTA] [A TESTAR]
-- REFERENCIAS_PODERES_E_EFEITOS v6.2 §5.1/§5.2/§5.6 + pedido do usuario de 17/11 (efeitos fracos no video v6.2):
--  * tudo NO CORPO: mascara emissiva fixa da propria pele (linhas, runas, olhos; rosto limpo) + luz verde curta presa aos
--    ossos do pescoco e das escapulas (destaque de ombros/pescoco no pico, sem halo); fora do corpo SO vento (Trails finas).
--  * cada habilidade tem preparacao, pico e dissipacao sincronizados aos marcadores do clipe:
--    Uivo (UivoInicio 0,55 / BuffInicio 0,6 / UivoFim 1,85), Salto (Mira 0,30 / Impulso 0,36 / Decolagem 0,42 / planeio /
--    Aterrissagem), Investida (Carga 0 / Arranque 0,22 / Contato 0,86 / Freia 0,96 / Fim 1,2).
--  * um RenderStepped para TODOS os lobos (mixer de brilho por camadas + vento); fora de 150 studs da camera nada e criado
--    (§5.10); celular = metade das faixas. Custo medido em atributos do jogador: LoboFxMs (ms/quadro) e LoboFxN (faixas+luzes).
-- O LocalScript nao troca a mascara (medido 16/11): so forca (EmissiveStrength) e tinta (EmissiveTint) sao animadas.
local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")
local VENTO = Color3.fromRGB(150, 235, 125)            -- 18/11 (referencia do usuario): ventania VERDE em volta do corpo (aura)
local VENTO_TEX = "rbxasset://textures/particles/smoke_main.dds"   -- textura macia do proprio Roblox (nenhum asset novo)
local VENTO_LARG = 3.0                                  -- faixas 3x mais largas e macias (antes 0,2-0,3 stud)
local VENTO_NUCLEO = Color3.fromRGB(205, 255, 185)      -- nucleo claro de cada rajada (brilho das faixas da referencia)
local IC_RASTRO = 8                                     -- = InstintoCaca.rastroSeg (pegadas somem em 8 s)
local TINTA_NAT = Color3.fromRGB(60, 210, 70)          -- verde (mascara r2 aprovada no pedido de 16/11)
local TINTA_AR = Color3.fromRGB(150, 245, 215)         -- salto encadeado: verde-agua claro (sinal proprio, sem mudar o dano)
local FORCA_MAX = 6.0                                  -- EmissiveStrength no pico (repouso do efeito ~ 40% disso) [A TESTAR]
local LUZ_MAX = 1.8                                    -- brilho das luzes do pescoco/ombros no pico (Range curto) [A TESTAR]
local CELULAR = UIS.TouchEnabled and not UIS.KeyboardEnabled
local function sm(x) x = math.clamp(x, 0, 1); return x * x * (3 - 2 * x) end
local function gauss(t, c, l) return math.exp(-((t - c) / l) ^ 2) end
local function perto(m) local cam = workspace.CurrentCamera; return cam and (m:GetPivot().Position - cam.CFrame.Position).Magnitude <= 150 end

-- ----- mixer: camadas de brilho por lobo -----
local fx = {}                                          -- [modelo] = {sa, luzes, camadas = {}, fitas = {}}
local function estadoFx(m)
	local e = fx[m]; if e then return e end
	local low = m:FindFirstChild("Lobo_Ancestral_LOW"); local sa = low and low:FindFirstChildOfClass("SurfaceAppearance")
	e = {sa = sa, camadas = {}, fitas = {}, luzes = {}}
	for _, n in ipairs({"Pescoco1", "EscapulaE", "EscapulaD"}) do
		local b = m:FindFirstChild(n, true)
		if b and b:IsA("Attachment") then
			local l = Instance.new("PointLight"); l.Name = "LuzFx_Lobo"; l.Color = Color3.fromRGB(90, 230, 110); l.Range = (n == "Pescoco1") and 3 or 2.6
			l.Brightness = 0; l.Shadows = false; l.Enabled = false; l.Parent = b; table.insert(e.luzes, l)
		end
	end
	local au = Instance.new("Highlight"); au.Name = "AuraLobo"; au.FillColor = Color3.fromRGB(120, 230, 100); au.OutlineColor = Color3.fromRGB(170, 255, 140)
	au.DepthMode = Enum.HighlightDepthMode.Occluded; au.FillTransparency = 1; au.OutlineTransparency = 1; au.Enabled = false; au.Adornee = m; au.Parent = m
	e.aura = au                                      -- 18/11: aura verde da referencia (contorno + tinta leve; nao esconde o lobo)
	fx[m] = e; return e
end
-- f(t) devolve forca (0..1), luz (0..1) e mistura de tinta Ar (0..1); dur = vida da camada
local function camada(m, nome, dur, f)
	if not perto(m) then return end
	local e = estadoFx(m); e.camadas[nome] = {t0 = os.clock(), dur = dur, f = f}
end
local function cortar(m, nome) local e = fx[m]; if e then e.camadas[nome] = nil end end

-- ----- vento: fitas (Trail) com trajetoria por funcao no espaco do RootPart (frente = -Z) -----
local function fita(m, dur, larg, transp, vida, pos)
	local e = estadoFx(m); local root = m:FindFirstChild("RootPart"); if not root then return end
	local a0 = Instance.new("Attachment"); local a1 = Instance.new("Attachment")
	local tr = Instance.new("Trail"); tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Lifetime = vida or 0.45; tr.MinLength = 0
	tr.Color = ColorSequence.new(VENTO); tr.LightEmission = 1; tr.LightInfluence = 0.15; tr.FaceCamera = true
	tr.Texture = VENTO_TEX; tr.TextureMode = Enum.TextureMode.Stretch; pcall(function() tr.Brightness = 2.5 end)
	local nucleo = Instance.new("Trail"); nucleo.Attachment0 = a0; nucleo.Attachment1 = a1; nucleo.Lifetime = (vida or 0.45) * 0.8; nucleo.MinLength = 0
	nucleo.Color = ColorSequence.new(VENTO_NUCLEO); nucleo.LightEmission = 1; nucleo.LightInfluence = 0; nucleo.FaceCamera = true
	nucleo.WidthScale = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.22), NumberSequenceKeypoint.new(1, 0.04)})
	tr.WidthScale = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(1, 0.15)})
	a0.Parent = root; a1.Parent = root; tr.Parent = root; nucleo.Parent = root
	local f = {a0 = a0, a1 = a1, tr = tr, nucleo = nucleo, t0 = os.clock(), dur = dur, larg = (larg or 0.32) * VENTO_LARG, transp = transp or 0.45, pos = pos, root = root}
	table.insert(e.fitas, f); return f
end
local function soltarFita(f) f.tr.Enabled = false; f.nucleo.Enabled = false; Debris:AddItem(f.nucleo, 0.7); Debris:AddItem(f.tr, 0.7); Debris:AddItem(f.a0, 0.7); Debris:AddItem(f.a1, 0.7) end
local function nFaixas(n) return CELULAR and math.max(1, math.floor(n / 2)) or n end
-- orbita em espiral (passa na frente e atras do corpo): raio/velocidade/visibilidade controlados por funcoes do tempo
local function orbita(m, dur, n, raioF, velF, visF, sobeF)
	local ang0 = {}
	for i = 1, nFaixas(n) do
		local fase = (i - 1) / n * math.pi * 2; local sentido = (i % 2 == 0) and 1 or -1; local alt = 1.4 + (i % 4) * 1.05
		local acum = 0; local ult = 0
		fita(m, dur, 0.2, 0.55, 0.55, function(t)
			local dt = t - ult; ult = t; acum += (velF and velF(t) or 2.6) * dt
			local r = raioF and raioF(t) or 1
			local a = fase + sentido * acum
			local y = alt + 0.45 * math.sin(t * 1.7 + fase) + (sobeF and sobeF(t) or 0)
			return Vector3.new(math.cos(a) * 3.0 * r, y, -2.2 + math.sin(a) * 6.2 * r), visF and visF(t) or 1
		end)
	end
end

-- 18/11 TESTE (pedido do usuario): giros de vento ESPONTANEOS - arcos curtos com raio, inclinacao, sentido, volta,
-- duracao e intervalo sorteados, surgindo e sumindo soltos em volta do corpo (em vez de orbitas seguidas).
-- r2 (18/11, "mais denso"): ~3x mais giros e inclinacao menor (arcos de lado viravam tracos retos).
-- VENTO_ESPONTANEO = false volta ao vento r4 (orbita + rajadas em sequencia).
local VENTO_ESPONTANEO = true
local function espontaneo(m, durTotal, densidade, visF, rente)
	task.spawn(function()
		local t0 = os.clock()
		while m.Parent and os.clock() - t0 < durTotal do
			local tg = os.clock() - t0
			local vg = visF and visF(tg) or 1
			if vg > 0.05 then
				local cz = -2.2 + (math.random() * 2 - 1) * 4.5
				local cy = 1.6 + math.random() * 3.8
				local r = (rente and 1.6 or 2.2) + math.random() * (rente and 1.2 or 2.0)
				local incl = CFrame.Angles(math.rad(math.random(-18, 18)), math.random() * 6.28, math.rad(math.random(-12, 12)))
				local a0 = math.random() * 6.28; local giro = math.rad(math.random(140, 320)) * (math.random() < 0.5 and -1 or 1)
				local d = 0.55 + math.random() * 0.6
				local alonga = 1.2 + math.random() * 0.9
				local sobe = (math.random() - 0.3) * 1.5
				fita(m, d, 0.24 + math.random() * 0.12, 0.45, 0.45, function(t)
					local u = t / d; local a = a0 + giro * u
					local q = incl:VectorToWorldSpace(Vector3.new(math.cos(a) * r, 0, math.sin(a) * r * alonga))
					return Vector3.new(q.X, cy + q.Y + sobe * u, cz + q.Z), math.sin(u * math.pi) * vg
				end)
			end
			local dens = type(densidade) == "function" and densidade(tg) or (densidade or 1)
			task.wait((0.06 + math.random() * 0.2) / (dens * (CELULAR and 0.5 or 1)))
		end
	end)
end

-- ----- laco unico -----
local custoAcum, quadros, ultimoRel = 0, 0, os.clock()
RunService.RenderStepped:Connect(function()
	local c0 = os.clock()
	local claro = Lighting.ClockTime >= 6 and Lighting.ClockTime < 18.5
	local fatorLuz = claro and 1.0 or 0.62                     -- noite: menos forca para nao estourar (mesma leitura) [A TESTAR]
	local nAtivos = 0
	for m, e in pairs(fx) do
		if not m.Parent then
			for _, f in ipairs(e.fitas) do soltarFita(f) end
			for _, l in ipairs(e.luzes) do l:Destroy() end
			if e.aura then e.aura:Destroy() end
			fx[m] = nil
		else
			local agora = os.clock()
			local forca, luz, ar = 0, 0, 0
			for nome, c in pairs(e.camadas) do
				local t = agora - c.t0
				if t > c.dur then e.camadas[nome] = nil
				else
					local f, l, a = c.f(t)
					if f > forca then forca = f; ar = a or 0 end
					luz = math.max(luz, l or 0)
				end
			end
			if e.sa then
				local s = FORCA_MAX * fatorLuz * forca
				if math.abs(e.sa.EmissiveStrength - s) > 0.01 then e.sa.EmissiveStrength = s end
				local tinta = TINTA_NAT:Lerp(TINTA_AR, ar)
				if e.sa.EmissiveTint ~= tinta then e.sa.EmissiveTint = tinta end
			end
			for _, l in ipairs(e.luzes) do
				local b = LUZ_MAX * luz * (claro and 1 or 0.7)
				l.Enabled = b > 0.02; l.Brightness = b; l.Color = Color3.fromRGB(90, 230, 110):Lerp(TINTA_AR, ar)
				if l.Enabled then nAtivos += 1 end
			end
			if e.aura then
				local a = math.min(1, forca * 1.4)
				e.aura.Enabled = a > 0.03
				if e.aura.Enabled then
					e.aura.OutlineTransparency = 1 - 0.55 * a; e.aura.FillTransparency = 1 - 0.05 * a   -- so contorno: o pelo continua o mesmo
					e.aura.OutlineColor = Color3.fromRGB(170, 255, 140):Lerp(TINTA_AR, ar)
				end
			end
			local i = 1
			while i <= #e.fitas do
				local f = e.fitas[i]; local t = agora - f.t0
				if t > f.dur or not f.root.Parent then soltarFita(f); table.remove(e.fitas, i)
				else
					local p, vis = f.pos(t)
					f.a0.Position = p; f.a1.Position = p + Vector3.new(0, f.larg, 0)
					local tv = 1 - (1 - f.transp) * math.clamp(vis or 1, 0, 1)
					if f.ultT ~= tv then f.ultT = tv; f.tr.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, tv), NumberSequenceKeypoint.new(1, 1)})
						f.nucleo.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, math.min(1, tv + 0.1)), NumberSequenceKeypoint.new(1, 1)}) end
					i += 1; nAtivos += 1
				end
			end
		end
	end
	custoAcum += os.clock() - c0; quadros += 1
	if os.clock() - ultimoRel >= 1 then
		eu:SetAttribute("LoboFxMs", math.floor(custoAcum / math.max(quadros, 1) * 1e5) / 100); eu:SetAttribute("LoboFxN", nAtivos)
		custoAcum, quadros, ultimoRel = 0, 0, os.clock()
	end
end)

-- ----- Uivo Ancestral: inspiracao -> nota (pico) -> bonus respirando -> termino -----
local function fxUivo(m, dur, buffIni)
	if not perto(m) then return end
	local fimB = buffIni + dur                                -- fim do bonus no relogio do clipe
	camada(m, "Uivo", fimB + 0.1, function(t)
		local f, l
		if t < 0.55 then f = 0.06 + 0.24 * sm(t / 0.55); l = 0                       -- inspiracao: as linhas acendem com o ar entrando
		elseif t < 1.85 then
			local g = gauss(t, 1.0, 0.38)                                               -- nota mais forte do uivo
			f = 0.36 + 0.64 * g; l = g
		else f = 0.62 * (0.88 + 0.12 * math.sin((t - 1.85) * math.pi * 2 / 2.2)); l = 0 -- bonus: discreto, respira com o lobo
		end
		local rest = fimB - t
		if rest < 1.5 then                                                            -- termino: um ultimo pulso e apaga em 1,5 s
			f = (0.62 + 0.3 * gauss(rest, 1.3, 0.15)) * sm(rest / 1.5); l = 0.35 * gauss(rest, 1.3, 0.15)
		end
		return f, l, 0
	end)
	if VENTO_ESPONTANEO then                                  -- TESTE 18/11: giros soltos; mais densos na nota do uivo
		espontaneo(m, fimB, function(t) return (t > 0.55 and t < 1.85) and 3.0 or 1.6 end,
			function(t) local rest = fimB - t; return sm(t / 0.4) * sm((rest + 0.2) / 1.6) end, false)
		return
	end
	-- vento: junta-se ao corpo na inspiracao, expande e acelera na nota, circula legivel durante o bonus e sobe ao terminar
	orbita(m, fimB + 0.4, 8,
		function(t) if t < 0.55 then return 1.55 - 0.55 * sm(t / 0.55) elseif t < 1.85 then return 1.0 + 0.3 * gauss(t, 1.05, 0.45) end return 1.0 end,
		function(t) if t < 0.55 then return 1.6 elseif t < 1.85 then return 2.6 + 3.2 * gauss(t, 1.0, 0.4) end return 2.4 end,
		function(t) local rest = fimB - t; return sm(t / 0.4) * (t < 0.55 and 0.6 or 1) * sm((rest + 0.4) / 1.9) end,
		function(t) local rest = fimB - t; return rest < 1.5 and (1.5 - rest) * 1.4 or 0 end)
	-- rajadas que correm da cabeca para a cauda, uma nova a cada 0,35 s enquanto dura o bonus (cada uma vive 1,1 s)
	task.spawn(function()
		local t0 = os.clock(); local k = 0
		while m.Parent and os.clock() - t0 < fimB - 1.2 do
			k += 1
			local lado = (k % 2 == 0) and 1 or -1; local alt = 3.0 + (k % 3) * 0.9
			fita(m, 1.1, 0.24, 0.5, 0.5, function(t)
				local u = t / 1.1
				return Vector3.new(lado * (1.7 + 1.1 * math.sin(u * math.pi)), alt + 0.7 * math.sin(u * 6.28 + k), -7 + u * 15), math.sin(u * math.pi)
			end)
			task.wait(0.35)
		end
	end)
end

-- ----- Salto Predatorio: impulso, voo/planeio e pouso distinguiveis; encadeado com sinal proprio -----
local function fxSalto(m, info, vooTotal)
	if not perto(m) then return end
	local dec = info.decolagem or 0.42
	local pouso = dec + (vooTotal or 1.04)
	local ar = info.cadeia and 1 or 0
	camada(m, "Salto", pouso + 0.6, function(t)
		local f, l
		if t < dec then f = 0.15 + 0.75 * sm((t - 0.18) / (dec - 0.18)); l = 0.5 * sm((t - 0.25) / (dec - 0.25))   -- impulso (Mira->Decolagem)
			if info.cadeia then f = math.max(f, 0.55 * gauss(t, 0.12, 0.06), 0.7 * gauss(t, 0.3, 0.06)) end           -- encadeado: duplo lampejo
		elseif t < pouso then f = 0.34 + 0.12 * math.sin((t - dec) / (pouso - dec) * math.pi); l = 0.15             -- voo/planeio: brilho firme
		else local u = (t - pouso); f = 0.95 * math.exp(-u / 0.18); l = 0.8 * math.exp(-u / 0.2) end              -- pouso: lampejo curto
		return f, l, ar
	end)
	-- impulso: 3 faixas rente as patas, apertando (o ar puxado para o salto)
	for i = 1, nFaixas(3) do
		local fase = i * 2.1
		fita(m, dec + 0.1, 0.22, 0.4, 0.3, function(t)
			local r = 1.6 - 1.0 * sm(t / dec); local a = fase + t * 9
			return Vector3.new(math.cos(a) * 2.6 * r, 0.6 + 0.3 * i, -2.2 + math.sin(a) * 4.6 * r), sm(t / 0.12)
		end)
	end
	task.delay(dec, function()
		if not m.Parent then return end
		local dur = (vooTotal or 1.04) + 0.05
		if info.cadeia then                                      -- encadeado: helice girando em volta do corpo (sinal proprio)
			for i = 1, nFaixas(4) do
				local fase = (i - 1) * math.pi / 2
				fita(m, dur, 0.3, 0.38, 0.4, function(t)
					local a = fase + t * 11
					return Vector3.new(math.cos(a) * 2.4, 3.4 + math.sin(a) * 2.0, -2.2 + (i - 2.5) * 1.6), 1
				end)
			end
		elseif VENTO_ESPONTANEO then espontaneo(m, dur, 3.2, nil, true)   -- TESTE 18/11: giros soltos durante o voo
		else                                                     -- normal: vento rente ao corpo que fica para tras (rastro do movimento)
			local pontos = {Vector3.new(-1.9, 3.6, -4.5), Vector3.new(1.9, 3.6, -4.5), Vector3.new(-1.7, 4.2, 1.2), Vector3.new(1.7, 4.2, 1.2)}
			for i = 1, nFaixas(4) do
				local p0 = pontos[i]
				fita(m, dur, 0.28, 0.4, 0.32, function(t) return p0 + Vector3.new(0, 0.25 * math.sin(t * 7 + i), 0), sm(t / 0.1) end)
			end
		end
	end)
end
local function fxSaltoPouso(m, r)
	if not perto(m) then return end
	-- pouso: anel de ar saindo das patas rente ao chao (6 faixas curtas); acerto = mais forte
	for i = 1, nFaixas(6) do
		local a = (i - 1) / 6 * math.pi * 2
		fita(m, 0.4, 0.2, r.acertou and 0.3 or 0.45, 0.25, function(t)
			local raio = 1.5 + 9 * sm(t / 0.35)
			return Vector3.new(math.cos(a) * raio * 0.6, 0.4 + t * 0.8, -2.2 + math.sin(a) * raio), 1 - sm((t - 0.15) / 0.25)
		end)
	end
end

-- ----- Investida: carga -> aceleracao (linhas acompanham a velocidade) -> contato ou interrupcao -----
local VEL_G = 21.43
local function velI(t)
	if t < 0.22 then return 0 elseif t < 0.36 then return sm((t - 0.22) / 0.14) elseif t < 0.78 then return 1 elseif t < 0.96 then return 1 - sm((t - 0.78) / 0.18) end
	return 0
end
local function fxInvestida(m)
	if not perto(m) then return end
	camada(m, "Investida", 1.3, function(t)
		if t < 0.22 then return 0.12 + 0.4 * sm(t / 0.22), 0.25 * sm(t / 0.22), 0 end   -- carga: tensao nas linhas
		return 0.32 + 0.4 * velI(t), 0.3 * velI(t), 0                                  -- arranque/galope: acompanha a velocidade
	end)
	-- carga: 2 faixas apertando nos flancos; depois 4 faixas RENTES ao corpo (patas/flancos) que ficam para tras na corrida
	for i = 1, nFaixas(2) do
		local s = i == 1 and -1 or 1
		fita(m, 0.24, 0.24, 0.42, 0.25, function(t) return Vector3.new(s * (2.6 - 1.0 * sm(t / 0.22)), 2.2, -3.5 + t * 6), sm(t / 0.08) end)
	end
	if VENTO_ESPONTANEO then task.delay(0.22, function() if m.Parent then espontaneo(m, 0.74, 3.6, function(t) return velI(t + 0.22) end, true) end end) return end
	task.delay(0.22, function()
		if not m.Parent then return end
		local pontos = {Vector3.new(-1.5, 1.3, -3.6), Vector3.new(1.5, 1.3, -3.6), Vector3.new(-1.6, 3.4, -1.0), Vector3.new(1.6, 3.4, -1.0)}
		for i = 1, nFaixas(4) do
			local p0 = pontos[i]
			fita(m, 0.78, 0.26, 0.38, 0.28, function(t) return p0, velI(t + 0.22) end)
		end
	end)
end
local function fxInvestidaFim(m, tipo, pos)
	if not perto(m) then return end
	local root = m:FindFirstChild("RootPart"); if not root or not pos then return end
	local loc = root.CFrame:PointToObjectSpace(pos)
	if tipo == "alvo" then
		camada(m, "InvestidaFim", 0.5, function(t) return 1.0 * math.exp(-t / 0.14), 1.0 * math.exp(-t / 0.16), 0 end)   -- contato: lampejo
		for i = 1, nFaixas(6) do                                -- ar empurrado para a frente no ponto do contato
			local a = (i - 1) / 6 * math.pi * 2
			fita(m, 0.35, 0.22, 0.32, 0.22, function(t)
				local r = 0.5 + 4.5 * sm(t / 0.3)
				return loc + Vector3.new(math.cos(a) * r, 0.6 + math.sin(a) * r * 0.6, -t * 4), 1 - sm((t - 0.15) / 0.2)
			end)
		end
	elseif tipo == "obstaculo" then
		camada(m, "InvestidaFim", 0.6, function(t) return 0.3 * (1 - gauss(t, 0.12, 0.05)) * (1 - gauss(t, 0.32, 0.05)) * math.exp(-t / 0.4), 0, 0 end)  -- linhas falham 2x e apagam
		for i = 1, nFaixas(3) do                                -- ar desviado para cima e para os lados na parede
			local s = (i - 2)
			fita(m, 0.45, 0.22, 0.4, 0.3, function(t)
				return loc + Vector3.new(s * 3 * sm(t / 0.35), 1 + 4 * sm(t / 0.4), 1.5 * sm(t / 0.35)), 1 - sm((t - 0.2) / 0.25)
			end)
		end
	end
end

-- ----- Instinto de Caca: marca e pegadas faceis de seguir, nunca atraves de paredes (§5.6) -----
local function vegetacao(inst) return inst:GetAttribute("Vegetacao") == true end
local function visivelDaCamera(alvo)                           -- parede entre a camera e o alvo = esconde (vegetacao nao conta)
	local cam = workspace.CurrentCamera; local r = alvo.PrimaryPart or alvo:FindFirstChild("HumanoidRootPart"); if not r then return false end
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude
	local ign = {alvo}; if eu.Character then table.insert(ign, eu.Character) end
	for m in pairs(fx) do table.insert(ign, m) end
	local ml = meuLobo(); if ml then table.insert(ign, ml) end
	for _ = 1, 4 do
		p.FilterDescendantsInstances = ign
		local h = workspace:Raycast(cam.CFrame.Position, r.Position - cam.CFrame.Position, p)
		if not h then return true end
		if vegetacao(h.Instance) or h.Instance:IsDescendantOf(alvo) then table.insert(ign, h.Instance) else return false end
	end
	return true
end
local vigiados = {}                                             -- [Highlight/Billboard] = alvo; checados a cada 0,1 s
task.spawn(function()
	while true do
		task.wait(0.1)
		for obj, alvo in pairs(vigiados) do
			if not obj.Parent then vigiados[obj] = nil
			else
				local ok = alvo.Parent and visivelDaCamera(alvo)
				if obj:IsA("Highlight") then obj.Enabled = ok else obj.Enabled = ok end
			end
		end
	end
end)
local function marcarPresa(alvo, dur)
	local old = alvo:FindFirstChild("MarcaPresa_Lobo"); if old then old:Destroy() end
	local oldb = alvo:FindFirstChild("SetaPresa_Lobo"); if oldb then oldb:Destroy() end
	local h = Instance.new("Highlight"); h.Name = "MarcaPresa_Lobo"; h.FillColor = Color3.fromRGB(120, 210, 90); h.FillTransparency = 0.88
	h.OutlineColor = Color3.fromRGB(140, 230, 100); h.OutlineTransparency = 0.1; h.DepthMode = Enum.HighlightDepthMode.Occluded; h.Parent = alvo
	local r = alvo.PrimaryPart or alvo:FindFirstChild("HumanoidRootPart")
	local bb, seta
	if r then
		bb = Instance.new("BillboardGui"); bb.Name = "SetaPresa_Lobo"; bb.Size = UDim2.new(0, 34, 0, 34); bb.StudsOffset = Vector3.new(0, 4.4, 0)
		bb.Adornee = r; bb.AlwaysOnTop = false; bb.LightInfluence = 0
		seta = Instance.new("TextLabel", bb); seta.Size = UDim2.fromScale(1, 1); seta.BackgroundTransparency = 1; seta.Text = "▼"; seta.Font = Enum.Font.GothamBold
		seta.TextScaled = true; seta.TextColor3 = Color3.fromRGB(150, 235, 105); seta.TextStrokeTransparency = 0.4; seta.TextStrokeColor3 = Color3.fromRGB(20, 50, 15)
		bb.Parent = alvo
	end
	vigiados[h] = alvo; if bb then vigiados[bb] = alvo end
	local t0 = os.clock()
	local con; con = RunService.RenderStepped:Connect(function()
		local t = os.clock() - t0
		if t > dur or not h.Parent then con:Disconnect(); h:Destroy(); if bb then bb:Destroy() end return end
		local fade = sm((dur - t) / 1.5)
		local pulso = t < 1.2 and (0.5 + 0.5 * math.cos(t * math.pi * 2 / 0.4)) or 0       -- 3 pulsos ao marcar
		h.OutlineTransparency = 1 - (0.75 + 0.25 * pulso) * fade
		if bb then bb.StudsOffset = Vector3.new(0, 4.4 + 0.35 * math.sin(t * 4), 0); seta.TextTransparency = 1 - fade end
	end)
end
-- pegadas: pares de almofadas orientadas no sentido do movimento; a mais nova e a mais forte; somem pela idade (8 s)
local pegadas = {}
local ultimaPeg = {}
local function pegada(pp, idade, id)
	local p = pp
	local k = string.format("%s_%d_%d", id or "", math.floor(p.X / 1.6), math.floor(p.Z / 1.6))
	if pegadas[k] then return end
	local resta = (IC_RASTRO or 8) - (idade or 1)
	if resta <= 0.2 then return end
	local ant = ultimaPeg[id or ""]; ultimaPeg[id or ""] = p
	local dir = (ant and (p - ant).Magnitude > 0.3) and (p - ant).Unit or Vector3.new(0, 0, -1)
	local cf = CFrame.lookAt(p, p + dir)
	local grupo = {}
	for _, lado in ipairs({-0.45, 0.45}) do
		local d = Instance.new("Part"); d.Anchored = true; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.CastShadow = false
		d.Shape = Enum.PartType.Cylinder; d.Size = Vector3.new(0.05, 0.62, 0.62); d.Material = Enum.Material.Neon; d.Color = Color3.fromRGB(120, 200, 85)
		d.CFrame = cf * CFrame.new(lado, 0.04, lado * 0.5) * CFrame.Angles(0, 0, math.rad(90))
		d.Transparency = 0.25 + 0.5 * math.clamp((idade or 1) / 8, 0, 1); d.Name = "PegadaInstinto"; d.Parent = workspace.Terrain
		table.insert(grupo, d)
		TweenService:Create(d, TweenInfo.new(resta, Enum.EasingStyle.Linear), {Transparency = 1}):Play()
	end
	pegadas[k] = true
	task.delay(resta, function() pegadas[k] = nil; for _, d in ipairs(grupo) do d:Destroy() end end)
end
local function revelar(alvo, dur)
	if not alvo.Parent then return end
	local h = alvo:FindFirstChild("RevelaInstinto")
	if not h then
		h = Instance.new("Highlight"); h.Name = "RevelaInstinto"; h.FillColor = Color3.fromRGB(120, 200, 90)
		h.FillTransparency = 0.8; h.OutlineColor = Color3.fromRGB(150, 220, 110); h.OutlineTransparency = 0.3
		h.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop; h.Parent = alvo   -- atravessa so a vegetacao: parede esconde (vigiados)
		vigiados[h] = alvo; h.Enabled = visivelDaCamera(alvo)
	end
	h:SetAttribute("Ate", os.clock() + dur)
	task.delay(dur + 0.05, function() if h.Parent and os.clock() >= (h:GetAttribute("Ate") or 0) then h:Destroy() end end)
end
-- rajada de vento curta numa direcao (pista de ninho): faixas saindo do corpo, sem particulas
local function rajada(m, dir)
	local root = m:FindFirstChild("RootPart"); if not root then return end
	local loc = root.CFrame:VectorToObjectSpace(dir)
	for i = 1, nFaixas(3) do
		local base = Vector3.new((i - 2) * 0.8, 3 + i * 0.6, -2)
		fita(m, 0.8, 0.26, 0.42, 0.5, function(t) local u = t / 0.8; return base + loc * (u * 9) + Vector3.new(0, math.sin(u * math.pi) * 0.8, 0), 1 - sm((u - 0.7) / 0.3) end)
	end
end

local uivoClipe = {}                                             -- lobos cujo Uivo ja veio pelo UivoInicio (evita efeito dobrado)
EVENTO.OnClientEvent:Connect(function(tipo, m, a, b, c, d)
	if tipo == "Resposta" then ultima = string.format("%s: %s %s", tostring(a), b and "ok" or "recusado", c or "")
	elseif tipo == "Pegadas" then for _, x in ipairs(a) do if typeof(x) == "table" then pegada(x.p, x.idade, x.id) else pegada(x, 1, "") end end
	elseif tipo == "PistaNinho" then rajada(m, a)
	elseif tipo == "Marca" then if a and a.Parent then marcarPresa(a, b or 8) end
	elseif tipo == "Revelar" then for _, alvo in ipairs(a or {}) do revelar(alvo, b or 1.3) end
	elseif tipo == "UivoInicio" then uivoClipe[m] = os.clock(); fxUivo(m, a or 8, b or 0.6)
	elseif tipo == "Uivo" then if not (uivoClipe[m] and os.clock() - uivoClipe[m] < 2) then fxUivo(m, a or 8, 0) end
	elseif tipo == "UivoFim" then uivoClipe[m] = nil
	elseif tipo == "Salto" then fxSalto(m, d or {}, c)
	elseif tipo == "SaltoPouso" then fxSaltoPouso(m, a or {})
	elseif tipo == "Investida" then fxInvestida(m)
	elseif tipo == "InvestidaFim" then fxInvestidaFim(m, a, b)
	elseif tipo == "Noite" then ultima = a and "Cacador Noturno ativo (noite)" or "Cacador Noturno inativo (dia)" end
end)
