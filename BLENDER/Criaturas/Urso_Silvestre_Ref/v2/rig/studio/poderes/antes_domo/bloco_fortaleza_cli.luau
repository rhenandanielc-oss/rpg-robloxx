-- ================================================================== Fortaleza Viva (Etapa 4, 05/11) - visual A: parede de energia
-- So apresentacao: o servidor decide reserva, golpes, quebra e duracao. Pedidos do usuario: "parede baixa de energia
-- translucida no contorno, que trinca conforme a reserva cai e estilhaca na quebra" e (05/11) "ao rugir, particulas devem
-- sair de si, formando o escudo". Aqui:
--   * ATIVAR (no rugido): estouro de particulas do PEITO do urso + fagulhas que voam em arco ate o contorno; cada painel da
--     parede so CRESCE do chao quando a sua fagulha chega (o escudo se forma a partir do urso);
--   * a parede ACOMPANHA o urso (raio do servidor), cada painel colado no chao por raycast (nunca flutua nem entra no teto);
--   * GOLPE: o painel mais proximo do ponto pisca; TRINCAS aparecem quando a reserva cai abaixo de 2/3 e de 1/3;
--   * QUEBRA: os paineis estilhacam em cacos que voam para fora e somem + estouro de particulas + tremor curto;
--   * FIM (expirou): a parede desce para o chao e some. Nada colide nem e consultado (CanCollide/CanQuery/CanTouch falsos).
M.SOM_FV_ATIVAR, M.SOM_FV_GOLPE, M.SOM_FV_QUEBRA = nil, nil, nil   -- rbxassetid quando existirem (PENDENTE)
M.VIS_FV = {paineis = 28, paineisBaixa = 16, altura = 4.5, espessura = 0.3, transp = 0.35,
	cor = Color3.fromRGB(255, 205, 120), corTrinca = Color3.fromRGB(90, 55, 20),
	fagulhaViagem = {0.30, 0.55}, crescer = 0.35, estouro = 60, cacos = 3}
local fortesV = {}                      -- [urso] = {paineis = {{p, ang, k, y, trincas}}, con, raio, nivel}
M.fortesV = fortesV
local function chaoFV(pos, rp)
	local h = workspace:Raycast(pos + Vector3.new(0, 6, 0), Vector3.new(0, -14, 0), rp); return h and h.Position.Y
end
local function corpoFV(urso)
	local b = urso:FindFirstChild("Coluna3", true)
	return b and b:IsA("Bone") and b.TransformedWorldCFrame.Position or urso:GetPivot().Position + Vector3.new(0, 4, 0)
end
local function limparFV(urso)
	local f = fortesV[urso]; if not f then return end; fortesV[urso] = nil
	if f.con then f.con:Disconnect() end
	for _, q in ipairs(f.paineis) do q.p:Destroy(); for _, t in ipairs(q.trincas) do t.p:Destroy() end end
end
local function trincar(f, nivel)
	-- nivel 1: 1/3 dos paineis com uma trinca; nivel 2: todos com duas
	for i, q in ipairs(f.paineis) do
		local quer = (nivel >= 2 and 2) or ((nivel == 1 and i % 3 == 0) and 1) or 0
		while #q.trincas < quer do
			local t = peca("TrincaFortaleza", M.VIS_FV.corTrinca, Enum.Material.Neon)
			local alt = M.VIS_FV.altura * (0.45 + 0.4 * math.random())
			t.Size = Vector3.new(0.12, alt, M.VIS_FV.espessura + 0.06); t.Transparency = 0.15; t.Parent = pasta
			table.insert(q.trincas, {p = t, off = CFrame.new((math.random() - 0.5) * q.p.Size.X * 0.7, (math.random() - 0.5) * 1.2, 0) * CFrame.Angles(0, 0, math.rad(math.random(-35, 35)))})
		end
	end
end
local function montarParede(urso, raio)
	limparFV(urso)
	local V = M.VIS_FV; local rp = params(urso); local n = baixaQ() and V.paineisBaixa or V.paineis
	local f = {paineis = {}, raio = raio, nivel = 0, rp = rp}; fortesV[urso] = f
	local larg = 2 * math.pi * raio / n * 1.06
	for i = 1, n do
		local p = peca("ParedeFortaleza", V.cor, Enum.Material.ForceField); p.Transparency = V.transp
		p.Size = Vector3.new(larg, V.altura, V.espessura); p.Parent = pasta
		table.insert(f.paineis, {p = p, ang = (i - 1) / n * 2 * math.pi, k = 0, y = nil, trincas = {}})
	end
	local giro = 0
	f.con = RS.RenderStepped:Connect(function()
		if not urso.Parent then limparFV(urso); return end
		local c = urso:GetPivot().Position; giro += 1
		for i, q in ipairs(f.paineis) do
			local pos = c + Vector3.new(math.cos(q.ang) * f.raio, 0, math.sin(q.ang) * f.raio)
			if not q.y or (i + giro) % 8 == 0 then q.y = chaoFV(pos, rp) or q.y or c.Y end      -- chao: refeito aos poucos
			local h = math.max(0.05, V.altura * q.k)
			local cf = CFrame.lookAt(Vector3.new(pos.X, q.y - 0.3 + h / 2, pos.Z), Vector3.new(c.X, q.y - 0.3 + h / 2, c.Z))
			q.p.Size = Vector3.new(q.p.Size.X, h, V.espessura); q.p.CFrame = cf
			for _, t in ipairs(q.trincas) do t.p.CFrame = cf * t.off end
		end
	end)
	return f
end
local function fagulhasFV(urso, f)
	local V = M.VIS_FV; local peito = corpoFV(urso)
	-- estouro de particulas saindo do corpo
	local a = Instance.new("Attachment"); a.WorldPosition = peito; a.Parent = workspace.Terrain
	local e = emissor(a, {Texture = "rbxasset://textures/particles/sparkles_main.dds", Color = ColorSequence.new(V.cor),
		LightEmission = 1, Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.9), NumberSequenceKeypoint.new(1, 0.1)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.1), NumberSequenceKeypoint.new(1, 1)}),
		Lifetime = NumberRange.new(0.35, 0.6), Speed = NumberRange.new(18, 30), SpreadAngle = Vector2.new(180, 180), Rate = 0, Drag = 2})
	e:Emit(baixaQ() and math.floor(V.estouro / 2) or V.estouro); Debris:AddItem(a, 1.2)
	-- fagulhas em arco do peito ate a base de cada painel; o painel cresce quando ela chega
	for _, q in ipairs(f.paineis) do
		local c = urso:GetPivot().Position
		local alvo = Vector3.new(c.X + math.cos(q.ang) * f.raio, (q.y or c.Y) + 0.4, c.Z + math.sin(q.ang) * f.raio)
		local fg = peca("FagulhaFortaleza", V.cor, Enum.Material.Neon); fg.Shape = Enum.PartType.Ball; fg.Size = Vector3.new(0.45, 0.45, 0.45)
		fg.CFrame = CFrame.new(peito); fg.Parent = pasta
		local dur = V.fagulhaViagem[1] + math.random() * (V.fagulhaViagem[2] - V.fagulhaViagem[1])
		local meio = (peito + alvo) / 2 + Vector3.new(0, 2.5 + math.random() * 1.5, 0)
		TS:Create(fg, TweenInfo.new(dur / 2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = CFrame.new(meio)}):Play()
		task.delay(dur / 2, function()
			if fg.Parent then TS:Create(fg, TweenInfo.new(dur / 2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = CFrame.new(alvo)}):Play() end
		end)
		task.delay(dur, function()
			fg:Destroy()
			if fortesV[urso] ~= f then return end
			local t0 = os.clock(); local con
			con = RS.RenderStepped:Connect(function()
				local k = math.min(1, (os.clock() - t0) / V.crescer); q.k = 1 - (1 - k) ^ 3
				if k >= 1 or fortesV[urso] ~= f then con:Disconnect() end
			end)
		end)
	end
end
local function golpeFV(urso, d)
	local f = fortesV[urso]; if not f then return end
	local c = urso:GetPivot().Position; local alvo = d.pos or (c + Vector3.new(math.random() - 0.5, 0, math.random() - 0.5))
	local melhor, dm = nil, math.huge
	for _, q in ipairs(f.paineis) do local dd = (q.p.Position - alvo).Magnitude; if dd < dm then melhor, dm = q, dd end end
	if melhor then
		melhor.p.Transparency = 0; melhor.p.Color = Color3.new(1, 1, 1)
		TS:Create(melhor.p, TweenInfo.new(0.35), {Transparency = M.VIS_FV.transp, Color = M.VIS_FV.cor}):Play()
	end
	local frac = (d.reserva or 0) / math.max(1, d.max or 1)
	local nivel = frac < 1 / 3 and 2 or (frac < 2 / 3 and 1 or 0)
	if nivel > f.nivel then f.nivel = nivel; trincar(f, nivel) end
	som(M.SOM_FV_GOLPE, alvo)
end
local function quebraFV(urso)
	local f = fortesV[urso]; if not f then return end
	local V = M.VIS_FV; local c = urso:GetPivot().Position
	for _, q in ipairs(f.paineis) do
		for j = 1, (baixaQ() and 1 or V.cacos) do
			local k = peca("CacoFortaleza", V.cor, Enum.Material.Neon); k.Transparency = 0.3
			k.Size = Vector3.new(q.p.Size.X * 0.4, V.altura * (0.25 + 0.2 * math.random()), V.espessura)
			k.CFrame = q.p.CFrame * CFrame.new((math.random() - 0.5) * q.p.Size.X * 0.6, (math.random() - 0.5) * V.altura * 0.6, 0); k.Parent = pasta
			local fora = Vector3.new(k.Position.X - c.X, 0, k.Position.Z - c.Z).Unit
			TS:Create(k, TweenInfo.new(0.7, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = k.CFrame + fora * (2.5 + math.random() * 2.5) + Vector3.new(0, 1.5 + math.random() * 2, 0), Transparency = 1}):Play()
			task.delay(0.75, function() k:Destroy() end)
		end
	end
	local a = Instance.new("Attachment"); a.WorldPosition = c + Vector3.new(0, 2, 0); a.Parent = workspace.Terrain
	local e = emissor(a, {Texture = "rbxasset://textures/particles/sparkles_main.dds", Color = ColorSequence.new(V.cor), LightEmission = 1,
		Size = NumberSequence.new(0.7, 0.1), Lifetime = NumberRange.new(0.5, 0.9), Speed = NumberRange.new(20, 34),
		SpreadAngle = Vector2.new(180, 30), Rate = 0, Drag = 1.5})
	e:Emit(baixaQ() and 40 or 90); Debris:AddItem(a, 1.5)
	tremorCurto(c); som(M.SOM_FV_QUEBRA, c)
	limparFV(urso)
end
local function fimFV(urso)
	local f = fortesV[urso]; if not f then return end
	local t0 = os.clock(); local k0 = {}
	for i, q in ipairs(f.paineis) do k0[i] = q.k; TS:Create(q.p, TweenInfo.new(0.6), {Transparency = 1}):Play() end
	local con; con = RS.RenderStepped:Connect(function()
		local s = math.min(1, (os.clock() - t0) / 0.6)
		if fortesV[urso] ~= f then con:Disconnect(); return end
		for i, q in ipairs(f.paineis) do q.k = k0[i] * (1 - s) end
		if s >= 1 then con:Disconnect(); limparFV(urso) end
	end)
end
function M.fortalezaEfx(d)
	if not d.urso then return end
	if d.fase == "ativar" then
		local f = montarParede(d.urso, d.raio or 12); fagulhasFV(d.urso, f); som(M.SOM_FV_ATIVAR, d.urso:GetPivot().Position)
		M.ultimaFortaleza = #f.paineis
	elseif d.fase == "golpe" then golpeFV(d.urso, d)
	elseif d.fase == "quebra" then quebraFV(d.urso)
	elseif d.fase == "fim" then fimFV(d.urso) end
end
