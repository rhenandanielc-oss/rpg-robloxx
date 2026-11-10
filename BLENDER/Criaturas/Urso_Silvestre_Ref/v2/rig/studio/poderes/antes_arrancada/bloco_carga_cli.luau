-- ================================================================== Carga Selvagem (Etapa 3, 04/11) - visual + queda local
-- So apresentacao: o servidor ja decidiu trajeto, impacto, queda e prazos. Aqui:
--   * CORRIDA: poeira/terra (cor do chao) levantando atras das patas enquanto a carga dura;
--   * IMPACTO: estouro de poeira e pedrinhas no ponto + tremor curto da camera de quem esta perto;
--   * PAREDE: estouro de poeira no ponto da batida;
--   * ATORDOADO: estrelinhas girando sobre a cabeca do derrubado enquanto dura (todos veem);
--   * QUEDA (so no cliente do jogador derrubado, dono da fisica do proprio personagem): PlatformStand + giro do tombo;
--     no "levantar" sai do PlatformStand e entra em GettingUp. Se este cliente falhar, o SERVIDOR libera no prazo.
M.SOM_CARGA_IMPACTO = nil        -- rbxassetid quando existir (PENDENTE)
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
function M.cargaEfx(d)
	if d.tipo == "CargaSelvagem" and d.urso then
		if d.fase == "inicio" then iniciarCarga(d.urso)
		elseif d.fase == "impacto" and d.pos then estouro(d.pos, d.urso, M.VIS_CS.estouro, M.VIS_CS.pedras); tremorCurto(d.pos); som(M.SOM_CARGA_IMPACTO, d.pos)
		elseif d.fase == "parede" and d.pos then estouro(d.pos, d.urso, math.floor(M.VIS_CS.estouro * 0.7), math.floor(M.VIS_CS.pedras * 0.6)); tremorCurto(d.pos)
		elseif d.fase == "fim" then pararCarga(d.urso) end
	elseif d.tipo == "Atordoado" and d.alvo then
		if d.fase == "inicio" then porTonto(d.alvo, d.dur) else tirarTonto(d.alvo) end
	elseif d.tipo == "Queda" then                                    -- so chega ao cliente do proprio derrubado
		local ch = Players.LocalPlayer.Character; local h = ch and ch:FindFirstChildOfClass("Humanoid"); local r = ch and ch:FindFirstChild("HumanoidRootPart")
		if not (h and r) then return end
		if d.fase == "cair" then h.PlatformStand = true; r.AssemblyAngularVelocity = d.giro or Vector3.zero; M.quedaLocal = os.clock()
		elseif d.fase == "levantar" then h.PlatformStand = false; h:ChangeState(Enum.HumanoidStateType.GettingUp); M.levantouLocal = os.clock() end
	end
end
M.cargas = cargas; M.tontos = tontos
