-- r8 (19/11): corpoSA acompanha a troca de malha por idade. Copia da r7: Uivo_Cliente_r7.client.luau.
-- r7 (19/11): efeitos na escala da idade. Copia da r6: Uivo_Cliente_r6.client.luau.
-- Uivo_Cliente (Script com RunContext = Client, Workspace.Teste_LoboArtico) - efeitos do UIVO BOREAL (r3, 16/11/2026).
-- So cosmetico: le os atributos do Uivo_Servidor e nunca decide nada.
-- r3 segue REFERENCIAS_PODERES_E_EFEITOS.md v5.2 §5.1/§5.3 (decisoes do usuario de 16/11):
--   * TUDO NO CORPO; fora do corpo SO neve levada pelo vento circulando (faixas finas em espiral, na frente e atras).
--   * Rosto limpo; olhos azul-gelo brilhando por conta propria.
--   * Duracao = duracao do buff (UivoAtivoFim), com fade-out no ultimo 1,5 s; pico no uivo.
--   * Som: uivo agudo + vento cortante + tilintar de gelo (sons Pro Sound Effects ja usados no kit Gelo do place).
--   * Alvos com lentidao (Lentidao_Boreal_Fim): geada no corpo do alvo enquanto durar.
-- r5 (16/11, pedido do usuario: "as linhas facam parte do corpo; nao flutuem ao redor; o poder do uivo implemente ao
-- corpo estes efeitos"): as LINHAS agora estao PINTADAS no corpo (mascara de emissao da SurfaceAppearance da LOW_Corpo,
-- rbxassetid 111250623946372, de boreal/tex/LoboArtico_Corpo_emissao_boreal.png r7b). Em repouso EmissiveStrength = 0
-- (nao ha linha); no Uivo a emissao acende, respira em 1,5 s e sobe no pico. Sairam: a neve em orbita (flutuava em
-- volta do corpo) e as fitas soltas do r4 (guardadas em ServerStorage.LoboArtico_Boreal_Retirados).
-- r4 (16/11): LINHAS azul-gelo continuas (FX_Boreal.Linhas_*, Neon, pele nos ossos; brilho percorre da cabeca para a
-- cauda, opacidade 35-55%, pico no uivo) e ESPINHOS de gelo (FX_Boreal.Espinho_*, crescem 0,6 s a partir da base no
-- inicio do efeito e recolhem 0,8 s no fim), vindos do Blender (boreal/boreal_fx.py r6 + montar_boreal.luau).
--   O Highlight dos cristais (r3) saiu: vazava pelos cartoes de pelo e manchava o peito.
-- r3: cristais do dorso acendem em azul-gelo (Highlight so no LOW_Cristais, sem contorno), olhos, neve em orbita,
-- sons e geada nos alvos. PENDENTE (precisa de textura/malha nova): linhas azul-gelo continuas pelo corpo ("capa de
-- efeito" com UV do pelo), espinhos de gelo que CRESCEM do pelo e a pelicula de geada no dorso.
-- r2 (neutro, 16/11) tinha nevoa saindo da boca e luz no ombro: removidas (ferem "nada sai do corpo"). Copia: Uivo_Cliente_r2_neutro.
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local function osso(n) return lobo:FindFirstChild(n, true) end
local cab = osso("Cabeca")
while not cab do task.wait(0.25); cab = osso("Cabeca") end     -- streaming: espera os ossos
local raiz = lobo:WaitForChild("RootPart")
local cristais = lobo:WaitForChild("LOW_Cristais", 10) or lobo:FindFirstChild("LOW_Cristais", true)

local GELO = Color3.fromRGB(165, 222, 255)
local NEVE = Color3.fromRGB(240, 248, 255)
local function id(n) return "rbxassetid://" .. n end
local SONS = {uivo = id(9120790529), vento = id(9125742111), tinido = id(9114590297), cristais = id(9114858178)}

-- pontos no corpo (Bone sem peso, so no cliente)
local function ponto(pai, nome, pos)
	local b = pai:FindFirstChild(nome) or Instance.new("Bone")
	b.Name = nome; b.CFrame = CFrame.new(pos); b.Parent = pai
	return b
end
-- r7/r5 (19/11, idades): efeitos acompanham Escala (Idade_Servidor). As pecas do FX_Boreal ja encolhem com Model:ScaleTo,
-- mas os atributos dos espinhos (OffsetOsso/BaseLocal/TamanhoCheio), olhos e particulas sao numeros fixos do Adulto.
local function escLobo() return lobo:GetAttribute("Escala") or 1 end
local function escCF(cf, e) if typeof(cf) == "Vector3" then return cf * e end; return CFrame.new(cf.Position * e) * cf.Rotation end   -- BaseLocal e Vector3
local pNariz = ponto(cab, "FX_Nariz", Vector3.new(0, 1.565, 0))
lobo:GetAttributeChangedSignal("Escala"):Connect(function() pNariz.CFrame = CFrame.new(0, 1.565 * escLobo(), 0) end)
pNariz.CFrame = CFrame.new(0, 1.565 * escLobo(), 0)
-- limpa o que a r2 deixou (nevoa da boca e luz do ombro) caso exista
for _, n in ipairs({"FX_Boca", "FX_Marca"}) do local b = lobo:FindFirstChild(n, true); if b then b:Destroy() end end

-- sons --------------------------------------------------------------------------------------------------------------
local function som(nome, sid, vol, tom, pai)
	local s = pai:FindFirstChild(nome) or Instance.new("Sound")
	s.Name = nome; s.SoundId = sid; s.Volume = vol; s.PlaybackSpeed = tom
	s.RollOffMode = Enum.RollOffMode.InverseTapered; s.RollOffMinDistance = 12; s.RollOffMaxDistance = 220
	s.Parent = pai
	return s
end
local sUivo = som("Som_Uivo", SONS.uivo, 0.8, 1.12, pNariz)            -- agudo
local sVento = som("Som_Vento", SONS.vento, 0, 1.25, raiz); sVento.Looped = true   -- vento cortante (mais agudo)
local sTinido = som("Som_Tinido", SONS.tinido, 0.35, 1.3, raiz)
local sCristais = som("Som_Cristais", SONS.cristais, 0.3, 1.1, raiz)

-- cristais do dorso: brilho azul-gelo (so a malha dos cristais; sem contorno = sem halo) -----------------------------
-- r4: sem Highlight nos cristais (vazava pelo pelo). Linhas e espinhos do FX_Boreal:
local fxPasta = lobo:WaitForChild("FX_Boreal", 10)
local ORDEM = {}   -- r5: fitas soltas retiradas (as linhas sao do corpo)
local linhasFx, espinhos = {}, {}
if fxPasta then
	for _, p in ipairs(fxPasta:GetChildren()) do
		if ORDEM[p.Name] then table.insert(linhasFx, {p = p, k = ORDEM[p.Name]}); p.Transparency = 1 end
		if p:GetAttribute("OssoEspinho") then
			table.insert(espinhos, {p = p, b = osso(p:GetAttribute("OssoEspinho")), off = p:GetAttribute("OffsetOsso"),
				base = p:GetAttribute("BaseLocal"), cheio = p:GetAttribute("TamanhoCheio") or p.Size})
			p.Transparency = 1
		end
	end
end
local hl = {Enabled = false}   -- (compatibilidade com o resto do script)

-- olhos azul-gelo (pequenos pontos Neon presos aos ossos das palpebras) ---------------------------------------------
local olhos = {}
for _, lado in ipairs({{"Palpebra_Sup_E", -0.07}, {"Palpebra_Sup_D", 0.07}}) do
	local b = osso(lado[1])
	if b then
		local p = Instance.new("Part")
		p.Name = "Olho_Boreal"; p.Shape = Enum.PartType.Ball; p.Size = Vector3.new(0.14, 0.14, 0.14)
		p.Material = Enum.Material.Neon; p.Color = GELO; p.Transparency = 1
		p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
		p.Parent = lobo
		table.insert(olhos, {p = p, b = b, dx = lado[2]})
	end
end

-- r5: corpo (emissao pintada) ------------------------------------------------------------------------------------------
local corpoSA = (lobo:FindFirstChild("LOW_Corpo", true) or Instance.new("Part")):FindFirstChildOfClass("SurfaceAppearance")
local TINTA = Color3.fromRGB(60, 160, 255)
if corpoSA then corpoSA.EmissiveStrength = 0; corpoSA.EmissiveTint = TINTA end
-- troca de malha por idade (Idade_Servidor r2): a LOW_Corpo nova traz outra SurfaceAppearance
lobo.ChildAdded:Connect(function(c)
	if c.Name ~= "LOW_Corpo" then return end
	local sa = c:FindFirstChildOfClass("SurfaceAppearance") or c:WaitForChild("SurfaceAppearance", 5)
	if sa then corpoSA = sa; corpoSA.EmissiveTint = TINTA; corpoSA.EmissiveStrength = 0; end
end)
local faixas = {}       -- (r5: sem neve em orbita)
local linhasFx = {}     -- (r5: sem fitas soltas)

-- geada nos alvos com lentidao -----------------------------------------------------------------------------------------
local geadas = {}
local function atualizarGeada()
	local centro = lobo:GetPivot().Position
	for m, h in pairs(geadas) do
		local fim = m.Parent and m:GetAttribute("Lentidao_Boreal_Fim")
		if not fim or fim <= workspace:GetServerTimeNow() then h:Destroy(); geadas[m] = nil end
	end
	for _, d in ipairs(workspace:GetChildren()) do
		local function olhar(m)
			if m:IsA("Model") and m ~= lobo and m:GetAttribute("Lentidao_Boreal_Fim") and not geadas[m] then
				local piv = m:GetPivot().Position
				if (piv - centro).Magnitude < 60 then
					local h = Instance.new("Highlight"); h.Name = "Geada_Boreal"; h.Adornee = m
					h.FillColor = GELO; h.FillTransparency = 0.72; h.OutlineTransparency = 1
					h.DepthMode = Enum.HighlightDepthMode.Occluded; h.Parent = m
					geadas[m] = h
				end
			end
		end
		olhar(d)
		if d:IsA("Folder") or (d:IsA("Model") and not d:FindFirstChildOfClass("Humanoid")) then
			for _, c in ipairs(d:GetChildren()) do olhar(c) end
		end
	end
end
task.spawn(function() while lobo.Parent do atualizarGeada(); task.wait(0.25) end end)

-- fases do uivo (som) ----------------------------------------------------------------------------------------------
local faseAtual = ""
local function fadeOut(s, t)
	if not s.IsPlaying then return end
	local tw = TweenService:Create(s, TweenInfo.new(t), {Volume = 0}); tw:Play()
	tw.Completed:Once(function(st) if st == Enum.PlaybackState.Completed then s:Stop() end end)
end
local tPico = -100
lobo:GetAttributeChangedSignal("UivoFase"):Connect(function()
	local f = lobo:GetAttribute("UivoFase") or ""
	if f == faseAtual then return end
	faseAtual = f
	if f == "Uivando" then
		local atraso = math.clamp(workspace:GetServerTimeNow() - (lobo:GetAttribute("UivoFaseT") or 0), 0, 1)
		sUivo.Volume = 0.8; sUivo.TimePosition = atraso; sUivo:Play()
		sTinido.TimePosition = 0; sTinido:Play()
		tPico = os.clock() - atraso
	elseif f == "Uivar" then
		sCristais.Volume = 0.3; sCristais.TimePosition = 0; sCristais:Play()      -- espinhos "acordando"
	elseif f == "PararUivar" then
		fadeOut(sUivo, 0.5)
	else
		fadeOut(sUivo, 0.25); fadeOut(sCristais, 0.25)
	end
end)

-- quadro a quadro: intensidade do efeito (fade-in 0,6 s, pico no uivo, fade-out no ultimo 1,5 s) ----------------------
local ligado = false
RunService.RenderStepped:Connect(function()
	local agora = workspace:GetServerTimeNow()
	local fim = lobo:GetAttribute("UivoAtivoFim") or 0
	local dur = lobo:GetAttribute("UivoDur") or 8
	local resta = fim - agora
	local ativo = resta > 0 and (lobo:GetAttribute("BonusVel_Uivo") or 0) > 0   -- r6: so o bonus do Uivo (a nevasca tambem mexe no MultVelocidade)
	if not ativo then
		if ligado then
			ligado = false
			for _, l in ipairs(linhasFx) do l.p.Transparency = 1 end
			for _, e in ipairs(espinhos) do e.p.Transparency = 1 end
			for _, o in ipairs(olhos) do o.p.Transparency = 1 end
			if corpoSA then corpoSA.EmissiveStrength = 0 end
			fadeOut(sVento, 0.3)
		end
		return
	end
	if not ligado then
		ligado = true
		sVento.Volume = 0; sVento:Play()
	end
	local decorrido = dur - resta
	local env = math.clamp(decorrido / 0.6, 0, 1) * math.clamp(resta / 1.5, 0, 1)
	local pico = math.max(0, 1 - math.abs(os.clock() - tPico - 0.4) / 0.9)       -- sobe por um instante no uivo
	local pulso = 0.5 + 0.5 * math.sin(os.clock() * math.pi * 2 / 1.5)          -- 1,5 s
	-- linhas: opacidade 35-55% com o brilho correndo da cabeca para a cauda (1,5 s), pico no uivo
	for _, l in ipairs(linhasFx) do
		local onda = 0.5 + 0.5 * math.sin(os.clock() * math.pi * 2 / 1.5 - l.k * 0.9)
		l.p.Transparency = 1 - env * (0.35 + 0.20 * onda + 0.30 * pico)
	end
	-- espinhos: crescem 0,6 s (saida suave) no inicio do efeito e recolhem 0,8 s no fim, a partir da base
	local s = math.clamp(decorrido / 0.6, 0, 1); s = 1 - (1 - s) ^ 3
	s = s * math.clamp(resta / 0.8, 0, 1)
	for _, e in ipairs(espinhos) do
		if s < 0.02 or not e.b then e.p.Transparency = 1 else
			local ee = escLobo()
			local cheio = e.b.TransformedWorldCFrame * escCF(e.off, ee)
			local base = cheio * escCF(e.base, ee)
			e.p.Size = e.cheio * ee * s
			e.p.CFrame = CFrame.new(base + (cheio.Position - base) * s) * cheio.Rotation
			e.p.Transparency = 0.18
		end
	end
	-- olhos
	for _, o in ipairs(olhos) do
		local cf = o.b.TransformedWorldCFrame
		local ee = escLobo(); o.p.Size = Vector3.new(0.14, 0.14, 0.14) * ee
		o.p.CFrame = cf * CFrame.new(o.dx * ee, 0, 0)
		o.p.Transparency = 1 - env * (0.55 + 0.35 * pico)
	end
	-- linhas do corpo: emissao respira (1,5 s) e sobe no pico do uivo; fade-in 0,6 s / fade-out 1,5 s
	if corpoSA then corpoSA.EmissiveStrength = env * (5 + 2.5 * pulso + 7 * pico) end
	sVento.Volume = 0.32 * env
end)
