-- ================================================================== Carga Selvagem (Etapa 3, 04/11) - visual + queda local
-- So apresentacao: o servidor ja decidiu trajeto, impacto, queda e prazos. Aqui:
--   * CORRIDA: poeira/terra (cor do chao) levantando atras das patas enquanto a carga dura;
--   * IMPACTO: estouro de poeira e pedrinhas no ponto + tremor curto da camera de quem esta perto;
--   * PAREDE: estouro de poeira no ponto da batida;
--   * ATORDOADO: estrelinhas girando sobre a cabeca do derrubado enquanto dura (todos veem);
--   * QUEDA (so no cliente do jogador derrubado, dono da fisica do proprio personagem): PlatformStand + giro do tombo;
--     no "levantar" sai do PlatformStand e entra em GettingUp. Se este cliente falhar, o SERVIDOR libera no prazo.
M.SOM_CARGA_IMPACTO = {id = "rbxassetid://9113470802", vel = 0.85, vol = 1.2}     -- Body Fall Heavy Rustle 2 (ProSoundEffects)
M.SOM_CARGA_ARRANCADA = {id = "rbxassetid://9119049891", vel = 0.9, vol = 1.0}    -- Shale Break Low End Crackling Rock 3 (ProSoundEffects)
M.VIS_CS = {poeiraTaxa = 70, estouro = 70, pedras = 10, tremorMax = 0.35, tremorAlcance = 45, estrelas = 3}
local cargas = {}                -- [urso] = {at, emissores, con}
local tontos = {}                -- [modelo] = {at, con, pecas}
local function poeiraChao(pos, ex) local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = ex
	local h = workspace:Raycast(pos + Vector3.new(0, 2, 0), Vector3.new(0, -12, 0), rp); return h end
local function emPoeira(pai, cor, taxa)
	return emissor(pai, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(cor, escurecer(cor, 0.8)),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.2), NumberSequenceKeypoint.new(1, 4.5)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.45), NumberSequenceKeypoint.new(1, 1)}),
		Lifetime = NumberRange.new(0.7, 1.3), Rate = taxa, Speed = NumberRange.new(2, 6), SpreadAngle = Vector2.new(60, 25),
		Acceleration = Vector3.new(0, 2, 0), Drag = 3, LightInfluence = 1, EmissionDirection = Enum.NormalId.Top})
end
local function estouro(pos, urso, n, pedras)
	local hit = poeiraChao(pos, {pasta, urso}); local c = corChao(hit); local p = hit and hit.Position or pos
	local at = Instance.new("Attachment"); at.WorldPosition = p + Vector3.new(0, 0.5, 0); at.Parent = workspace.Terrain
	local e = emPoeira(at, c, 0); e.Speed = NumberRange.new(8, 16); e.SpreadAngle = Vector2.new(80, 80); e:Emit(baixaQ() and math.floor(n / 2) or n)
	for i = 1, (baixaQ() and math.floor(pedras / 2) or pedras) do
		local q = peca("PedraCarga", escurecer(c, 0.7), Enum.Material.Slate); q.Size = Vector3.new(0.4, 0.4, 0.4) * (0.6 + math.random())
		q.CFrame = CFrame.new(p + Vector3.new(0, 0.6, 0)); q.Anchored = false; q.CanCollide = true; q.Parent = pasta
		q.AssemblyLinearVelocity = Vector3.new(math.random(-12, 12), math.random(10, 20), math.random(-12, 12))
		task.delay(2.5, function() q:Destroy() end)
	end
	task.delay(2.5, function() at:Destroy() end)
end
local function tremorCurto(pos)
	local cam = workspace.CurrentCamera; if not cam then return end
	local d = (cam.CFrame.Position - pos).Magnitude; if d > M.VIS_CS.tremorAlcance then return end
	local amp = M.VIS_CS.tremorMax * (1 - d / M.VIS_CS.tremorAlcance); local t0 = os.clock(); local nome = "TremorCarga" .. tostring(t0)
	RS:BindToRenderStep(nome, Enum.RenderPriority.Camera.Value + 2, function()
		local k = (os.clock() - t0) / 0.35; if k >= 1 then RS:UnbindFromRenderStep(nome); return end
		local a = amp * (1 - k); cam.CFrame = cam.CFrame * CFrame.new(math.noise(k * 25, 1) * a, math.noise(k * 25, 2) * a, 0)
	end)
end
local function pararCarga(urso)
	local c = cargas[urso]; if not c then return end; cargas[urso] = nil
	for _, e in ipairs(c.emissores) do e.Enabled = false end
	if c.con then c.con:Disconnect() end
	task.delay(1.6, function() for _, a in ipairs(c.ats) do a:Destroy() end end)
end
local function iniciarCarga(urso)
	pararCarga(urso)
	local c = {emissores = {}, ats = {}}; cargas[urso] = c
	local hit = poeiraChao(urso:GetPivot().Position, {pasta, urso}); local cor = corChao(hit)
	for _, n in ipairs({"PeE", "PeD", "MaoE", "MaoD"}) do
		local at = Instance.new("Attachment"); at.Parent = workspace.Terrain; table.insert(c.ats, at)
		table.insert(c.emissores, emPoeira(at, cor, baixaQ() and M.VIS_CS.poeiraTaxa / 2 or M.VIS_CS.poeiraTaxa))
		local b = urso:FindFirstChild(n, true)
		c[n] = {at = at, b = b}
	end
	c.con = RS.RenderStepped:Connect(function()
		if not urso.Parent then pararCarga(urso); return end
		local pv = urso:GetPivot()
		for _, n in ipairs({"PeE", "PeD", "MaoE", "MaoD"}) do
			local s = c[n]; local p = s.b and s.b.TransformedWorldCFrame.Position or pv.Position
			s.at.WorldPosition = Vector3.new(p.X, pv.Position.Y + 0.3, p.Z)
		end
	end)
end
local function tirarTonto(mod)
	local t = tontos[mod]; if not t then return end; tontos[mod] = nil
	if t.con then t.con:Disconnect() end
	for _, p in ipairs(t.pecas) do p:Destroy() end
end
local function porTonto(mod, dur)
	tirarTonto(mod)
	local cab = mod:FindFirstChild("Head") or mod:FindFirstChild("HumanoidRootPart"); if not cab then return end
	local t = {pecas = {}}; tontos[mod] = t
	for i = 1, M.VIS_CS.estrelas do
		local p = peca("EstrelaTonto", Color3.fromRGB(255, 225, 90), Enum.Material.Neon); p.Shape = Enum.PartType.Ball
		p.Size = Vector3.new(0.35, 0.35, 0.35); p.Parent = pasta; table.insert(t.pecas, p)
	end
	local t0 = os.clock()
	t.con = RS.RenderStepped:Connect(function()
		if not cab.Parent or os.clock() - t0 > (dur or 2) + 1 then tirarTonto(mod); return end
		local c = cab.Position + Vector3.new(0, 1.4, 0)
		for i, p in ipairs(t.pecas) do
			local a = (os.clock() - t0) * 6 + i * 2 * math.pi / #t.pecas
			p.CFrame = CFrame.new(c + Vector3.new(math.cos(a) * 1.1, math.sin(a * 2) * 0.15, math.sin(a) * 1.1))
		end
	end)
end
-- ARRANCADA (05/11, pedido do usuario: "ao ativar a habilidade o urso empurra o chao, fazendo-o rachar e sai correndo"):
-- no evento "arrancada" (EmpurraoS do clipe CargaInicio) o chao racha ATRAS das patas traseiras, as fendas abrem para
-- tras e para os lados (o empurrao), com estouro de terra/pedrinhas em cada pata e um tremor curto. Mesma fenda do Golpe
-- Colossal (cresce, borda levantada na cor de terra, some sozinha), em tamanho menor. So visual; nada colide.
M.VIS_ARR = {fendasPorPata = 4, compr = {8, 13}, largura = 1.1, abertura = 50, levante = 0.9, levanteCapim = 2.6, ramificar = 0.25,
	torroes = 9, chuteDist = {3, 7}, chuteAlt = {2.5, 5}, poeira = 26, duracao = 5.5, sumir = 1.2}
-- v2 (05/11, 1a gravacao: no capim alto da Floresta a fenda sumia e a poeira saia VERDE, cor do capim): fendas maiores
-- com terra levantada mais alta, TORROES de terra chutados para tras (o empurrao) e poeira na cor de TERRA, mais alta.
local function rachaArrancada(urso, dir)
	local A = M.VIS_ARR; local rp = params(urso); local pv = urso:GetPivot()
	dir = dir and Vector3.new(dir.X, 0, dir.Z).Magnitude > 0.01 and Vector3.new(dir.X, 0, dir.Z).Unit or Vector3.new(pv.LookVector.X, 0, pv.LookVector.Z).Unit
	local partes = {}; local q = baixaQ()
	local corT = M.VIS.corTerra
	for _, n in ipairs({"PeE", "PeD"}) do
		local b = urso:FindFirstChild(n, true)
		local p = b and b.TransformedWorldCFrame.Position or (pv.Position - dir * 3.5)
		local hit = workspace:Raycast(Vector3.new(p.X, pv.Position.Y + 2, p.Z), Vector3.new(0, -6, 0), rp)
		if hit then
			local capim = hit.Instance:IsA("Terrain") and M.VIS.materiaisCapim[hit.Material.Name] or false
			local cfg = {levante = capim and A.levanteCapim or A.levante, ramificar = A.ramificar, erup = {}}
			local corBorda = corT:Lerp(corChao(hit), 0.15); local corFenda = escurecer(corT, 0.22)
			for i = 1, (q and 2 or A.fendasPorPata) do
				local ang = math.rad((math.random() * 2 - 1) * A.abertura)
				local d = (CFrame.Angles(0, ang, 0) * -dir).Unit
				fenda(hit.Position, d, A.compr[1] + math.random() * (A.compr[2] - A.compr[1]), A.largura * (0.8 + 0.4 * math.random()), rp, corBorda, corFenda, partes, 0, 0, cfg)
			end
			-- torroes chutados para tras: saem da pata, sobem em arco e assentam (ancorados, tween; nada colide)
			for i = 1, (q and math.floor(A.torroes / 2) or A.torroes) do
				local ang = math.rad((math.random() * 2 - 1) * A.abertura)
				local d = (CFrame.Angles(0, ang, 0) * -dir).Unit
				local dist = A.chuteDist[1] + math.random() * (A.chuteDist[2] - A.chuteDist[1])
				local alvo = hit.Position + d * dist
				local h2 = workspace:Raycast(alvo + Vector3.new(0, 3, 0), Vector3.new(0, -7, 0), rp)
				if h2 then
					local s = 0.45 + math.random() * 0.55
					local t = peca("Torrao", corT:Lerp(escurecer(corT, 0.6), math.random()), Enum.Material.Ground)
					t.Size = Vector3.new(s, s * 0.7, s * 1.1); t.CFrame = CFrame.new(hit.Position + Vector3.new(0, 0.4, 0)); t.Parent = pasta; table.insert(partes, t)
					local alt = A.chuteAlt[1] + math.random() * (A.chuteAlt[2] - A.chuteAlt[1]); local t1 = 0.2 + math.random() * 0.1
					TS:Create(t, TweenInfo.new(t1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = CFrame.new((hit.Position + h2.Position) / 2 + Vector3.new(0, alt, 0)) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)}):Play()
					task.delay(t1, function() if t.Parent then TS:Create(t, TweenInfo.new(t1 * 1.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = CFrame.lookAt(h2.Position + h2.Normal * s * 0.3, h2.Position + h2.Normal * s * 0.3 + d, h2.Normal)}):Play() end end)
				end
			end
			-- poeira de terra (nao a cor do capim), alta, jogada para tras
			local a = Instance.new("Attachment"); a.WorldPosition = hit.Position + Vector3.new(0, 0.6, 0); a.Parent = workspace.Terrain
			local e = emPoeira(a, corT:Lerp(Color3.fromRGB(170, 150, 120), 0.35), 0)
			e.Speed = NumberRange.new(7, 14); e.SpreadAngle = Vector2.new(35, 35); e.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.6), NumberSequenceKeypoint.new(1, 6)})
			e.Lifetime = NumberRange.new(1.0, 1.8); e.Acceleration = Vector3.new(0, -2, 0)
			a.CFrame = CFrame.lookAt(a.WorldPosition, a.WorldPosition + (-dir + Vector3.new(0, 1.2, 0))) * CFrame.Angles(-math.pi / 2, 0, 0)
			e:Emit(q and math.floor(A.poeira / 2) or A.poeira); Debris:AddItem(a, 2.5)
		end
	end
	for _, p in ipairs(partes) do
		task.delay(A.duracao - A.sumir, function() if p.Parent then TS:Create(p, TweenInfo.new(A.sumir), {Transparency = 1}):Play() end end)
		task.delay(A.duracao + 0.1, function() p:Destroy() end)
	end
	tremorCurto(pv.Position); M.ultimaArrancada = #partes
	return #partes
end
function M.cargaEfx(d)
	if d.tipo == "CargaSelvagem" and d.urso then
		if d.fase == "inicio" then iniciarCarga(d.urso)
		elseif d.fase == "arrancada" then rachaArrancada(d.urso, d.dir); som(M.SOM_CARGA_ARRANCADA, d.urso:GetPivot().Position)
		elseif d.fase == "impacto" and d.pos then estouro(d.pos, d.urso, M.VIS_CS.estouro, M.VIS_CS.pedras); tremorCurto(d.pos); som(M.SOM_CARGA_IMPACTO, d.pos)
		elseif d.fase == "parede" and d.pos then estouro(d.pos, d.urso, math.floor(M.VIS_CS.estouro * 0.7), math.floor(M.VIS_CS.pedras * 0.6)); tremorCurto(d.pos)
		elseif d.fase == "fim" then pararCarga(d.urso) end
	elseif d.tipo == "Atordoado" and d.alvo then
		if d.fase == "inicio" then porTonto(d.alvo, d.dur) else tirarTonto(d.alvo) end
	elseif d.tipo == "Queda" then                                    -- so chega ao cliente do proprio derrubado
		local ch = Players.LocalPlayer.Character; local h = ch and ch:FindFirstChildOfClass("Humanoid"); local r = ch and ch:FindFirstChild("HumanoidRootPart")
		if not (h and r) then return end
		if d.fase == "cair" then h.PlatformStand = true; r.AssemblyAngularVelocity = d.giro or Vector3.zero; if typeof(d.lanc) == "Vector3" then r.AssemblyLinearVelocity = d.lanc end; M.quedaLocal = os.clock()
		elseif d.fase == "levantar" then h.PlatformStand = false; h:ChangeState(Enum.HumanoidStateType.GettingUp); M.levantouLocal = os.clock() end
	end
end
M.cargas = cargas; M.tontos = tontos
