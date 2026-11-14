-- LaminaVento_Cliente (LocalScript, StarterPlayerScripts) — efeito VISUAL da Lamina de Vento da Wyvern (so cosmetico; o
-- servidor decide trajetoria, acertos e fim; nada aqui muda hitbox, alvo, dano ou recarga).
-- r2 (pedido "mais chamativo, com mais aura", 14/11) sobre a E3 (2 pecas ForceField + rastro na largura da lamina, que de
-- lado virava dois paineis, e lufada dupla no alvo):
--   preparo : fios de vento azul-gelo CONVERGEM para as pontas das asas (ossos strut_b_02_L/R) e ganham forca ate abrir.
--   emissao : cada asa solta seu corte diagonal (das pontas ao centro em 0,12 s); no cruzamento, clarao branco LOCAL (bola
--             de ~4 studs, 0,15 s; nada de tela cheia) e duas ondas translucidas curtas.
--   voo     : cada diagonal = nucleo branco estreito + borda azul-gelo curva (Beams virados para a camera: legiveis de tras e
--             de perfil); fitas finas nas 4 pontas e no centro (desenham a curva teleguiada); halo curto de ar no centro.
--   desfecho: alvo = expansao breve de ar (1 so: "impacto" do alvo final nao soma rajada com "acertou"); parede = rajada
--             aberta pela superficie (normal do servidor); fim do alcance = os fios se desfazem, sem rajada.
-- Eventos do RemoteEvent Combate_Dragoes.FX com hab = "LaminaVento" (contrato do servidor Combate_Wyvern/LaminaVento):
--   preparo{d,noAr} | emissao{id,pe,pd,centro,dir,vel,alvo,noAr,meia} | voo{id,pos,dir} (0,1 s) | impacto{id,pos,acertou}
--   | acertou/bateu/dissipa{id,pos,normal}.
-- Custo: por X 1 pasta (pecas ancoradas sem colisao/consulta), 6 Beams, 5 Trails, 1 emissor de halo; preparo 2 emissores;
-- rajadas <= 16 particulas. LOD: longe da camera (> 160 studs), qualidade grafica baixa (<= 3) ou com >= 5 X ativos o X
-- sai so com o nucleo. Limpeza: pasta por disparo destruida no fim, no cancelamento do preparo (1,5 s) e por prazo (6 s).
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Debris = game:GetService("Debris")
local FX = RS:WaitForChild("Combate_Dragoes"):WaitForChild("FX")
local BRANCO = Color3.fromRGB(255, 255, 255)
local GELO = Color3.fromRGB(165, 215, 255)
local FUMACA = "rbxasset://textures/particles/smoke_main.dds"
local BRILHO = "rbxasset://textures/particles/sparkles_main.dds"
local LONGE, MAX_CHEIO, PRAZO = 160, 5, 6
local ATIVOS = {}                                    -- [id] = estado do X
local PREP = {}                                      -- [modelo] = {pasta, emissores, pecas, t0}
local FINAL = {}                                     -- [id] = posicao do desfecho (para nao somar rajada do impacto)

local function raiz()
	local f = workspace:FindFirstChild("VFX_Temporarios")
	if not f then f = Instance.new("Folder"); f.Name = "VFX_Temporarios"; f.Parent = workspace end
	return f
end
local function qualidadeBaixa()
	local ok, q = pcall(function() return UserSettings():GetService("UserGameSettings").SavedQualityLevel end)
	return ok and q ~= Enum.SavedQualitySetting.Automatic and q.Value <= 3
end
local function peca(nome, pai, forma)
	local p = Instance.new("Part"); p.Name = nome
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Transparency = 1; p.Size = Vector3.new(0.2, 0.2, 0.2)
	if forma then p.Shape = forma end
	p.Parent = pai
	return p
end
local function seq(a, b) return NumberSequence.new(a, b) end
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end

-- ---------------------------------------------------------------- preparo: fios de vento convergindo nas pontas
local function limparPrep(m)
	local p = PREP[m]; if not p then return end
	PREP[m] = nil
	for _, e in ipairs(p.emissores) do e.Enabled = false end
	for _, par in ipairs(p.pecas) do if par[4] then par[4]:Destroy() end end   -- nucleo de carga some na abertura
	Debris:AddItem(p.pasta, 0.6)                                       -- deixa os ultimos fios terminarem
end
local function iniciarPrep(m)
	limparPrep(m)
	local pasta = Instance.new("Folder"); pasta.Name = "LaminaVento_Preparo"; pasta.Parent = raiz()
	local reduzido = qualidadeBaixa()
	local p = {pasta = pasta, emissores = {}, pecas = {}, t0 = os.clock(), m = m}
	for _, nome in ipairs({"strut_b_02_L", "strut_b_02_R"}) do
		local b = osso(m, nome)
		if b then
			local esfera = peca("Carga", pasta); esfera.Size = Vector3.new(7, 7, 7); esfera.Shape = Enum.PartType.Ball
			local e = Instance.new("ParticleEmitter"); e.Name = "Fios"
			e.Texture = BRILHO; e.Color = ColorSequence.new(GELO, BRANCO); e.LightEmission = 0.9; e.LightInfluence = 0
			e.Shape = Enum.ParticleEmitterShape.Sphere; e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface
			e.ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward                -- nascem na esfera e correm PARA a ponta da asa
			e.Speed = NumberRange.new(11, 15); e.Lifetime = NumberRange.new(0.3, 0.4)
			e.Orientation = Enum.ParticleOrientation.VelocityParallel
			e.Size = seq(0.9, 0.3); e.Squash = seq(2.4, 2.4)                    -- fio esticado na direcao do movimento (r2b: maior)
			e.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.3, 0.25), NumberSequenceKeypoint.new(1, 0.9)})
			e.Rate = 0; e.Parent = esfera
			-- nucleo de carga: bolinha azul-gelo na ponta da asa que cresce ate a abertura (r2b: so os fios nao se liam de tras)
			local nuc = peca("NucleoCarga", pasta, Enum.PartType.Ball); nuc.Material = Enum.Material.Neon; nuc.Color = GELO
			nuc.Transparency = 0.35; nuc.Size = Vector3.one * 0.4
			table.insert(p.emissores, e); table.insert(p.pecas, {esfera, b, reduzido, nuc})
		end
	end
	PREP[m] = p
	task.delay(1.5, function() if PREP[m] == p then limparPrep(m) end end)      -- cancelado (sem emissao): limpa
end

-- ---------------------------------------------------------------- emissao: clarao local e duas ondas
local function onda(pai, pos, eixo, r0, r1, dur, atraso, transp)
	task.delay(atraso or 0, function()
		if not pai.Parent then return end
		local d = peca("Onda", pai, Enum.PartType.Cylinder)
		d.Material = Enum.Material.ForceField; d.Color = GELO; d.Transparency = transp or 0.2
		local cf = CFrame.lookAt(pos, pos + eixo) * CFrame.Angles(0, math.rad(90), 0)  -- eixo do cilindro (X) = eixo pedido
		local t0 = os.clock()
		while d.Parent and os.clock() - t0 < dur do
			local k = (os.clock() - t0) / dur
			local r = r0 + (r1 - r0) * (1 - (1 - k) ^ 2)
			d.Size = Vector3.new(0.15, r * 2, r * 2); d.CFrame = cf; d.Transparency = (transp or 0.2) + (1 - (transp or 0.2)) * k
			RunService.RenderStepped:Wait()
		end
		d:Destroy()
	end)
end
local function clarao(pai, pos)
	local b = peca("Clarao", pai, Enum.PartType.Ball); b.Material = Enum.Material.Neon; b.Color = BRANCO; b.Transparency = 0.15
	task.spawn(function()
		local t0 = os.clock()
		while b.Parent and os.clock() - t0 < 0.15 do
			local k = (os.clock() - t0) / 0.15
			b.Size = Vector3.one * (1.5 + 2.8 * k); b.Position = pos; b.Transparency = 0.15 + 0.85 * k
			RunService.RenderStepped:Wait()
		end
		b:Destroy()
	end)
end
local function rajada(pai, pos, normal, n, forte)
	local a = peca("Rajada", pai); a.CFrame = CFrame.lookAt(pos, pos + (normal or Vector3.yAxis)) * CFrame.Angles(math.rad(-90), 0, 0)
	local e = Instance.new("ParticleEmitter"); e.Texture = FUMACA; e.Color = ColorSequence.new(BRANCO, GELO)
	e.LightEmission = 0.35; e.LightInfluence = 0.5
	e.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.45), NumberSequenceKeypoint.new(1, 1)})
	e.Size = seq(1.6, forte and 6 or 4); e.Lifetime = NumberRange.new(0.25, 0.45); e.Speed = NumberRange.new(14, 22)
	e.Drag = 6; e.SpreadAngle = normal and Vector2.new(80, 80) or Vector2.new(180, 180)   -- na parede abre pela superficie
	e.EmissionDirection = Enum.NormalId.Top; e.Rate = 0; e.Parent = a; e:Emit(n)
	Debris:AddItem(a, 0.9)
end

-- ---------------------------------------------------------------- o X em voo
local function beam(pai, a0, a1, cor, larg, transp, curva, luz)
	local b = Instance.new("Beam"); b.Attachment0 = a0; b.Attachment1 = a1
	b.Color = ColorSequence.new(cor); b.LightEmission = luz or 1; b.LightInfluence = 0
	b.Width0 = larg; b.Width1 = larg; b.FaceCamera = true; b.Segments = 12
	b.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.12, transp),
		NumberSequenceKeypoint.new(0.88, transp), NumberSequenceKeypoint.new(1, 1)})
	b.CurveSize0 = curva or 0; b.CurveSize1 = -(curva or 0)
	b.Parent = pai
	return b
end
local function fita(pai, a0, a1, cor, vida, transp)
	local t = Instance.new("Trail"); t.Attachment0 = a0; t.Attachment1 = a1
	t.Color = ColorSequence.new(cor); t.LightEmission = 0.8; t.LightInfluence = 0; t.FaceCamera = true
	t.Transparency = seq(transp, 1); t.Lifetime = vida; t.MinLength = 0.1; t.WidthScale = seq(1, 0.2)
	t.Parent = pai
	return t
end
local function criarX(e)
	local pasta = Instance.new("Folder"); pasta.Name = "LaminaVento_" .. tostring(e.id); pasta.Parent = raiz()
	Debris:AddItem(pasta, PRAZO + 1)
	local meia = e.meia or 10
	local n = 0; for _ in pairs(ATIVOS) do n += 1 end
	local reduzido = qualidadeBaixa() or n >= MAX_CHEIO
	local base = peca("LaminaVento_Base", pasta)
	local function at(nome) local a = Instance.new("Attachment"); a.Name = nome; a.Parent = base; return a end
	-- 4 pontas (2 diagonais) + o centro; cada ponta com um par proximo para a fita fina
	local P = {}
	for i = 1, 4 do P[i] = {at("Ponta" .. i), at("PontaF" .. i)} end
	local C, C2 = at("Centro"), at("CentroF")
	local nucleo, bordas, fitas = {}, {}, {}
	for k, par in ipairs({{1, 2}, {3, 4}}) do
		local a0, a1 = P[par[1]][1], P[par[2]][1]
		nucleo[k] = beam(pasta, a0, a1, BRANCO, 0.45, 0.05, 0, 1)
		bordas[k] = beam(pasta, a0, a1, GELO, 2.6, 0.55, meia * 0.07, 0.7)          -- borda larga, curva leve (com 0,22 virava argola por cima do X)
	end
	for i = 1, 4 do fitas[i] = fita(pasta, P[i][1], P[i][2], GELO, 0.35, 0.35) end
	fitas[5] = fita(pasta, C, C2, BRANCO, 0.45, 0.25)                                 -- fita do centro: desenha a curva
	local halo = Instance.new("ParticleEmitter"); halo.Texture = FUMACA; halo.Color = ColorSequence.new(GELO, BRANCO)
	halo.LightEmission = 0.4; halo.LightInfluence = 0.3; halo.Rate = 28; halo.Speed = NumberRange.new(0)
	halo.Lifetime = NumberRange.new(0.18, 0.28); halo.Size = seq(meia * 0.35, meia * 0.6)       -- fica dentro do X
	halo.Transparency = seq(0.82, 1); halo.LockedToPart = false; halo.Parent = C
	local x = {id = e.id, pasta = pasta, base = base, P = P, C = C, C2 = C2, nucleo = nucleo, bordas = bordas, fitas = fitas,
		halo = halo, pos = e.centro, dir = e.dir, sPos = e.centro, sDir = e.dir, vel = e.vel or 80, t = 0, meia = meia,
		pe = e.pe or e.centro, pd = e.pd or e.centro, reduzido = reduzido}
	ATIVOS[e.id] = x
	-- emissao: clarao local no cruzamento + duas ondas curtas (na frente do peito)
	clarao(pasta, e.centro)
	if not reduzido then onda(pasta, e.centro, e.dir, 1.5, meia * 0.9, 0.22, 0, 0.25); onda(pasta, e.centro, e.dir, 1, meia * 0.6, 0.22, 0.07, 0.35) end
	return x
end
local function pousar(x)
	-- pose do X: plano perpendicular a dir; diagonais (+-1,+-1) * meia nos eixos lado/cima
	local lado = x.dir:Cross(Vector3.yAxis); if lado.Magnitude < 1e-3 then lado = x.dir:Cross(Vector3.xAxis) end; lado = lado.Unit
	local cima = lado:Cross(x.dir).Unit
	local m = x.meia
	local fim = {x.pos + (lado + cima) * m, x.pos - (lado + cima) * m, x.pos + (lado - cima) * m, x.pos - (lado - cima) * m}
	local k = math.clamp(x.t / 0.12, 0, 1)                                -- 0,12 s: cada corte sai da SUA asa e cruza
	if k < 1 then
		-- diagonal 1 (pontas 1,2) nasce centrada na ponta da asa esquerda (pe), diagonal 2 (3,4) na direita (pd), com 35% do
		-- tamanho; corre para o cruzamento crescendo
		local kk = 1 - (1 - k) ^ 2
		for i = 1, 4 do
			local ini = (i <= 2) and x.pe or x.pd
			local partida = ini + (fim[i] - x.pos) * 0.35
			fim[i] = partida:Lerp(fim[i], kk)
		end
	end
	x.base.CFrame = CFrame.new(x.pos)
	for i = 1, 4 do x.P[i][1].WorldPosition = fim[i]; x.P[i][2].WorldPosition = fim[i] + cima * 0.3 end
	x.C.WorldPosition = x.pos; x.C2.WorldPosition = x.pos + cima * 0.45
end
local function aplicarLOD(x)
	local cam = workspace.CurrentCamera
	local longe = cam and (cam.CFrame.Position - x.pos).Magnitude > LONGE
	local cheio = not (x.reduzido or longe)
	for _, b in ipairs(x.bordas) do b.Enabled = cheio end
	for i = 1, 4 do x.fitas[i].Enabled = cheio end
	x.halo.Enabled = cheio and not x.fim
end
local function encerrar(id, fase, pos, normal)
	local x = ATIVOS[id]; if not x then return end
	ATIVOS[id] = nil; x.fim = true
	pos = pos or x.pos
	FINAL[id] = pos; task.delay(1, function() FINAL[id] = nil end)
	if fase == "acertou" then
		onda(x.pasta, pos, x.dir, 1.5, x.meia * 0.8, 0.22, 0, 0.3); rajada(x.pasta, pos, nil, x.reduzido and 6 or 14, true)
	elseif fase == "bateu" then
		onda(x.pasta, pos, normal or -x.dir, 1.5, x.meia * 1.0, 0.25, 0, 0.3); rajada(x.pasta, pos, normal or -x.dir, x.reduzido and 6 or 16, true)
	end                                                                   -- dissipa: so os fios se desfazem (abaixo)
	x.halo.Enabled = false
	task.spawn(function()                                                 -- desfaz nucleo/bordas; as fitas terminam sozinhas
		local t0 = os.clock()
		while os.clock() - t0 < 0.3 and x.pasta.Parent do
			local k = (os.clock() - t0) / 0.3
			for _, b in ipairs(x.nucleo) do b.Width0 = 0.45 * (1 - k); b.Width1 = b.Width0 end
			for _, b in ipairs(x.bordas) do b.Width0 = 2.6 * (1 + k); b.Width1 = b.Width0
				b.Transparency = NumberSequence.new(0.55 + 0.45 * k) end
			if fase == "dissipa" then x.pos += x.dir * x.vel * 0.3 * RunService.RenderStepped:Wait(); pousar(x) else RunService.RenderStepped:Wait() end
		end
		for _, b in ipairs(x.nucleo) do b.Enabled = false end
		for _, b in ipairs(x.bordas) do b.Enabled = false end
		Debris:AddItem(x.pasta, 0.6)                                       -- 0,6 s para as fitas sumirem
	end)
end

FX.OnClientEvent:Connect(function(e)
	if type(e) ~= "table" or e.hab ~= "LaminaVento" then return end
	if e.fase == "preparo" and e.d then
		iniciarPrep(e.d)
	elseif e.fase == "emissao" and e.id and e.centro and e.dir then
		if e.d then limparPrep(e.d) end
		criarX(e)
	elseif e.fase == "voo" and e.id and ATIVOS[e.id] then
		local x = ATIVOS[e.id]; x.sPos, x.sDir = e.pos, e.dir
	elseif (e.fase == "acertou" or e.fase == "bateu" or e.fase == "dissipa") and e.id then
		encerrar(e.id, e.fase, e.pos, e.normal)
	elseif e.fase == "impacto" and e.pos then
		-- acerto no caminho: sopro pequeno. Se for o alvo final, o "acertou" chega no mesmo quadro e ja faz a rajada: espera um
		-- instante e so solta o sopro se nao houver desfecho no mesmo lugar (E3 somava duas rajadas no alvo)
		local id, pos = e.id, e.pos
		task.delay(0.05, function()
			local f = id and FINAL[id]
			if f and (f - pos).Magnitude < 1.5 then return end
			local x = id and ATIVOS[id]
			rajada(x and x.pasta or raiz(), pos, nil, 7, false)
		end)
	end
end)

RunService.RenderStepped:Connect(function(dt)
	for m, p in pairs(PREP) do                                            -- carga nas pontas: segue o osso, cresce ate abrir
		local k = math.clamp((os.clock() - p.t0) / 0.45, 0, 1)
		for i, par in ipairs(p.pecas) do
			local esfera, b, reduz = par[1], par[2], par[3]
			if b.Parent then
				local pos = b.TransformedWorldCFrame.Position
				esfera.CFrame = CFrame.new(pos)
				local nuc = par[4]
				if nuc then nuc.CFrame = CFrame.new(pos); nuc.Size = Vector3.one * (0.4 + 1.6 * k * (0.9 + 0.1 * math.sin(os.clock() * 40))) end
			end
			p.emissores[i].Rate = (reduz and 10 or 18) + (reduz and 10 or 40) * k
		end
		if not m.Parent then limparPrep(m) end
	end
	for id, x in pairs(ATIVOS) do
		x.t += dt
		x.dir = (x.dir:Lerp(x.sDir, math.min(1, dt * 10))).Unit           -- segue o estado do servidor sem saltos
		x.pos += x.dir * x.vel * dt
		x.sPos += x.sDir * x.vel * dt
		x.pos = x.pos:Lerp(x.sPos, math.min(1, dt * 6))
		pousar(x); aplicarLOD(x)
		if x.t > PRAZO then encerrar(id, "dissipa") end
	end
end)
