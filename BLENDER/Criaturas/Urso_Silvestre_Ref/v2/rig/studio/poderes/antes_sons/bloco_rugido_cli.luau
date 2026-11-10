-- ================================================================== Rugido Protetor (Etapa 2, 04/11) - so visual
-- [historico] v2 (04/11, pedido do usuario: "algo envolvendo particulas ... que sai do treinador e do urso, e efeito especial na
-- hora do rugido"). Cores ambar/douradas NEUTRAS (o elemento do urso continua PENDENTE: nada de folhas/raizes).
--   * RUGIDO: da boca saem ONDAS DE SOM (aneis translucidos que avancam e crescem, um a cada ~0,16 s enquanto ruge),
--     um sopro de particulas para a frente, um clarao curto na cabeca e poeira levantando em volta das patas;
--   * EFEITO (pico): onda no chao + coluna de particulas douradas que SOBE de cada alvo (urso e treinador);
--   * BONUS ATIVO: de cada alvo saem continuamente brasas douradas subindo em espiral, um brilho fraco e um anel
--     fino nos pes. Nada esconde os personagens (sem Highlight/neblina; transparencia alta). Sai no "fim" do bonus.
-- Qualidade grafica baixa: metade das particulas e menos ondas (so visual).
-- v3 (04/11, pedido do usuario: "aura saindo do rugido ... e quando estiver com a protecao, uma aura AZUL em volta dos
--   dois, nao um redondo em volta deles"): tudo em AZUL; sem anel nem disco no chao. A aura da protecao CONTORNA o
--   corpo (Highlight com contorno azul e preenchimento quase invisivel, so onde o alvo esta a vista: nao atravessa
--   paredes) + chamas de energia azul subindo em volta do corpo. No rugido, a aura sai da boca: ondas azuis, sopro de
--   energia e uma nuvem de energia que se espalha a partir do urso.
M.SOM_RUGIDO_PROTETOR = nil      -- rbxassetid do rugido protetor quando existir (PENDENTE)
M.VIS_RP = {cor = Color3.fromRGB(70, 160, 255), cor2 = Color3.fromRGB(175, 225, 255), raioOnda = 40, durOnda = 0.9,
	ondasSom = 9, intervaloSom = 0.16, alcanceSom = 16, brasas = 14, duracaoRugido = 1.5, focos = 6}   -- focos: pontos em volta do corpo de onde as particulas sobem
local auras = {}                 -- [alvo] = {pecas, at, emissores, luz, con}
local function baixaQ() local q = settings().Rendering.QualityLevel.Value; return q > 0 and q <= 3 end
local function pecaRP(nome)
	local p = Instance.new("Part"); p.Name = nome; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Material = Enum.Material.Neon; p.Color = M.VIS_RP.cor; p.Shape = Enum.PartType.Cylinder; return p
end
local function chaoSob(pos, ex)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = ex
	local h = workspace:Raycast(pos + Vector3.new(0, 1, 0), Vector3.new(0, -12, 0), rp); return h and h.Position or pos
end
local function emissor(pai, t)
	local pe = Instance.new("ParticleEmitter")
	for k, v in pairs(t) do pe[k] = v end
	pe.Parent = pai; return pe
end
local function tirarAura(alvo)
	local a = auras[alvo]; if not a then return end; auras[alvo] = nil
	if a.con then a.con:Disconnect() end
	for _, p in ipairs(a.pecas) do if p.Parent then TS:Create(p, TweenInfo.new(0.4), {Transparency = 1}):Play(); task.delay(0.45, function() p:Destroy() end) end end
	for _, e in ipairs(a.emissores) do e.Enabled = false end
	if a.luz then TS:Create(a.luz, TweenInfo.new(0.5), {Brightness = 0}):Play() end
	if a.hl then TS:Create(a.hl, TweenInfo.new(0.5), {OutlineTransparency = 1, FillTransparency = 1}):Play(); local h = a.hl; task.delay(0.55, function() h:Destroy() end) end
	task.delay(2.0, function() if a.at then a.at:Destroy() end; for _, f in ipairs(a.focos or {}) do f:Destroy() end end)
end
local function porAura(alvo, dur)
	tirarAura(alvo)
	local base = alvo:FindFirstChild("HumanoidRootPart") or alvo:FindFirstChild("Pelve", true) or alvo.PrimaryPart or alvo:FindFirstChildWhichIsA("BasePart", true)
	if not base then return end
	local V = M.VIS_RP; local baixa = baixaQ()
	local ext = alvo:GetExtentsSize(); local r = math.clamp(math.max(ext.X, ext.Z) * 0.55, 2.0, 6)
	local hl = Instance.new("Highlight"); hl.Adornee = alvo; hl.FillColor = V.cor; hl.FillTransparency = 0.76; hl.OutlineColor = V.cor
	hl.OutlineTransparency = 1; hl.DepthMode = Enum.HighlightDepthMode.Occluded; hl.Parent = pasta
	TS:Create(hl, TweenInfo.new(0.35), {OutlineTransparency = 0.15}):Play()
	-- focos de particulas em VOLTA do corpo (fora da malha: de dentro do urso nada apareceria), na altura dos pes
	local baixaF = baixa and math.ceil(V.focos / 2) or V.focos
	local ks = function(a, b) return NumberSequence.new({NumberSequenceKeypoint.new(0, a), NumberSequenceKeypoint.new(1, b)}) end
	local focos, emissores = {}, {}
	for i = 1, baixaF do
		local at = Instance.new("Attachment"); at.Parent = workspace.Terrain; focos[i] = at
		table.insert(emissores, emissor(at, {Texture = "rbxasset://textures/particles/sparkles_main.dds", Color = ColorSequence.new(V.cor2, V.cor),
			LightEmission = 1, LightInfluence = 0, Size = ks(0.7, 0.1), Transparency = ks(0, 1), Lifetime = NumberRange.new(1.0, 1.8),
			Rate = baixa and 6 or 10, Speed = NumberRange.new(3, 6), SpreadAngle = Vector2.new(12, 12), EmissionDirection = Enum.NormalId.Top,
			Acceleration = Vector3.new(0, 2, 0), RotSpeed = NumberRange.new(-180, 180)}))
		table.insert(emissores, emissor(at, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(V.cor),
			LightEmission = 0.8, LightInfluence = 0, Size = ks(1.0, 2.6), Transparency = ks(0.6, 1), Lifetime = NumberRange.new(0.9, 1.4),
			Rate = baixa and 3 or 6, Speed = NumberRange.new(2, 4), EmissionDirection = Enum.NormalId.Top}))
	end
	local altura = math.max(ext.Y, 4)
	local luzAt = Instance.new("Attachment"); luzAt.Parent = workspace.Terrain
	local luz = Instance.new("PointLight"); luz.Color = V.cor; luz.Range = r * 3; luz.Brightness = 1.4; luz.Shadows = false; luz.Parent = luzAt
	local a = {pecas = {}, at = luzAt, focos = focos, emissores = emissores, luz = luz, hl = hl}
	local t0 = os.clock()
	a.con = RS.RenderStepped:Connect(function()
		if not alvo.Parent then tirarAura(alvo); return end
		local piv = alvo:GetPivot(); local pos = chaoSob(piv.Position, {alvo, pasta})
		hl.OutlineTransparency = 0.15 + 0.25 * (0.5 + 0.5 * math.sin((os.clock() - t0) * 5))   -- aura pulsando
		local giro = (os.clock() - t0) * 1.2                                  -- os focos giram devagar em volta (espiral)
		for i, at in ipairs(focos) do
			local ang = giro + (i / #focos) * math.pi * 2
			at.WorldPosition = pos + Vector3.new(math.cos(ang) * r * 0.7, 0.3 + (i % 3) * altura * 0.3, math.sin(ang) * r * 0.7)
		end
		luzAt.WorldPosition = pos + Vector3.new(0, altura * 0.5, 0)
	end)
	auras[alvo] = a
	task.delay(dur + 2, function() if auras[alvo] == a then tirarAura(alvo) end end)        -- seguranca: nunca fica para sempre
end
-- explosao de particulas que sobe de um alvo no pico (coluna dourada)
local function coluna(alvo)
	local pos = alvo:GetPivot().Position
	local at = Instance.new("Attachment"); at.WorldPosition = chaoSob(pos, {alvo, pasta}) + Vector3.new(0, 0.3, 0); at.Parent = workspace.Terrain
	local V = M.VIS_RP; local n = baixaQ() and 40 or 90
	local pe = emissor(at, {Texture = "rbxasset://textures/particles/sparkles_main.dds", Color = ColorSequence.new(V.cor2, V.cor), LightEmission = 1,
		LightInfluence = 0, Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.9), NumberSequenceKeypoint.new(1, 0.1)}),
		Transparency = NumberSequence.new(0, 1), Lifetime = NumberRange.new(0.9, 1.5), Rate = 0, Speed = NumberRange.new(12, 22),
		SpreadAngle = Vector2.new(25, 25), EmissionDirection = Enum.NormalId.Top, Drag = 2, Acceleration = Vector3.new(0, 2, 0)})
	pe:Emit(n); Debris:AddItem(at, 2)
end
-- ondas de som saindo da boca enquanto o urso ruge
local function ondasDeSom(urso)
	local V = M.VIS_RP; local baixa = baixaQ()
	local mand = urso:FindFirstChild("Mandibula", true); local cab = urso:FindFirstChild("Cabeca", true)
	local n = baixa and math.ceil(V.ondasSom / 2) or V.ondasSom
	-- clarao curto na cabeca + sopro de particulas para a frente
	if cab then
		local at = Instance.new("Attachment"); at.Parent = workspace.Terrain
		local luz = Instance.new("PointLight"); luz.Color = V.cor; luz.Range = 18; luz.Brightness = 3; luz.Shadows = false; luz.Parent = at
		local sopro = emissor(at, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(V.cor2), LightEmission = 0.6,
			LightInfluence = 0.3, Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(1, 5)}),
			Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(1, 1)}), Lifetime = NumberRange.new(0.6, 1.0),
			Rate = baixa and 10 or 22, Speed = NumberRange.new(14, 22), SpreadAngle = Vector2.new(14, 14), Drag = 3})
		local t0 = os.clock()
		local con; con = RS.RenderStepped:Connect(function()
			if not urso.Parent or os.clock() - t0 > V.duracaoRugido then con:Disconnect(); sopro.Enabled = false; TS:Create(luz, TweenInfo.new(0.4), {Brightness = 0}):Play(); Debris:AddItem(at, 1.5); return end
			local p = (mand or cab).TransformedWorldCFrame.Position; local f = urso:GetPivot().LookVector
			at.CFrame = CFrame.lookAt(p, p + f) * CFrame.Angles(math.rad(-90), 0, 0)      -- a "frente" do emissor (Top) aponta para onde o urso olha
			luz.Brightness = 3 * (1 - (os.clock() - t0) / V.duracaoRugido) + 0.5
		end)
	end
	-- poeira levantando em volta das patas (o chao "treme" com o rugido)
	local pe0 = chaoSob(urso:GetPivot().Position, {urso, pasta})
	local atp = Instance.new("Attachment"); atp.WorldPosition = pe0 + Vector3.new(0, 0.3, 0); atp.Parent = workspace.Terrain
	local po = emissor(atp, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(Color3.fromRGB(170, 150, 120)),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.5), NumberSequenceKeypoint.new(1, 4)}), Transparency = NumberSequence.new(0.5, 1),
		Lifetime = NumberRange.new(0.8, 1.4), Rate = 0, Speed = NumberRange.new(6, 10), SpreadAngle = Vector2.new(85, 5), Drag = 3,
		EmissionDirection = Enum.NormalId.Top})
	po:Emit(baixa and 10 or 22); Debris:AddItem(atp, 2)
	-- aneis de som: cada um nasce na boca, avanca e cresce, e some
	for i = 1, n do
		task.delay((i - 1) * V.intervaloSom, function()
			if not urso.Parent then return end
			local p = ((mand or cab) and (mand or cab).TransformedWorldCFrame.Position) or urso:GetPivot().Position
			local f = urso:GetPivot().LookVector
			local anel = pecaRP("OndaSom"); anel.Material = Enum.Material.Neon; anel.Color = V.cor; anel.Transparency = 0.72   -- translucido: nao esconde o treinador
			anel.Size = Vector3.new(0.15, 1.2, 1.2); anel.CFrame = CFrame.lookAt(p, p + f) * CFrame.Angles(0, math.rad(90), 0); anel.Parent = pasta
			local fim = CFrame.lookAt(p + f * V.alcanceSom, p + f * (V.alcanceSom + 1)) * CFrame.Angles(0, math.rad(90), 0)
			TS:Create(anel, TweenInfo.new(0.7, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = fim, Size = Vector3.new(0.15, 11, 11), Transparency = 1}):Play()
			task.delay(0.75, function() anel:Destroy() end)
		end)
	end
end
function M.rugidoProtetorEfx(d)
	if d.fase == "rugido" and d.urso then
		local cab = d.urso:FindFirstChild("Cabeca", true); som(M.SOM_RUGIDO_PROTETOR, cab and cab.TransformedWorldCFrame.Position or d.urso:GetPivot().Position)
		ondasDeSom(d.urso); M.ultimoRugido = os.clock()
	elseif d.fase == "efeito" and d.urso then
		-- nuvem de energia azul que se espalha a partir do urso (a "aura" do rugido chegando ao treinador)
		local c = chaoSob(d.urso:GetPivot().Position, {d.urso, pasta})
		local atn = Instance.new("Attachment"); atn.WorldPosition = c + Vector3.new(0, 2.5, 0); atn.Parent = workspace.Terrain
		local nv = emissor(atn, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(M.VIS_RP.cor2, M.VIS_RP.cor),
			LightEmission = 0.8, LightInfluence = 0, Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 2), NumberSequenceKeypoint.new(1, 7)}),
			Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(1, 1)}), Lifetime = NumberRange.new(0.8, 1.2),
			Rate = 0, Speed = NumberRange.new(16, 26), SpreadAngle = Vector2.new(180, 8), Drag = 4, EmissionDirection = Enum.NormalId.Top})
		nv:Emit(baixaQ() and 20 or 45); Debris:AddItem(atn, 2)
		for _, alvo in ipairs(d.alvos or {}) do coluna(alvo); porAura(alvo, d.duracao or 10) end
		M.ultimoRP = {alvos = #(d.alvos or {}), t = os.clock()}
	elseif d.fase == "fim" and d.alvo then
		tirarAura(d.alvo)
	end
end
M.auras = auras
