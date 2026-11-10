-- ================================================================== PASSIVAS (05/11) - so visual
-- FURIA DO PROTETOR: enquanto dura, o urso fica com contorno vermelho-alaranjado (Highlight) e solta brasas e vapor
--   do corpo; no inicio, um estouro curto. Todos veem.
-- FARO DO PROTETOR: "farejou" = sopro de particulas no focinho do urso (todos veem); "marca" = SO no cliente do
--   treinador: cada inimigo escondido ganha contorno amarelo visivel atraves das paredes + um marcador acima dele
--   (aparece mesmo se o alvo estiver invisivel), por dur s.
M.VIS_PAS = {corFuria = Color3.fromRGB(255, 70, 20), corFaro = Color3.fromRGB(255, 225, 80)}
-- FURIA v2 (05/11, pedido do usuario com imagem de referencia: "deixe a aura mais parecida com isto" - urso escuro envolto
-- em FIOS de energia dourada/laranja que correm para tras pelo corpo, brasas no ar e OLHOS acesos): olhos acesos (2 esferas
-- Neon presas ao osso Cabeca + luz), fios finos e alongados (particulas orientadas pela velocidade, esticadas) que nascem
-- em pontos aleatorios do corpo a cada quadro e correm para tras e para cima, brasas soltas, brilho dourado de contorno e
-- uma luz quente no peito. So visual; todos veem.
-- v2b (05/11, 1a captura: o corpo ficou laranja e os fios pareciam estrelas soltas): o corpo ESCURECE (preenchimento
-- marrom-escuro) com contorno dourado; os fios viram RASTROS de luz (Trail) que deslizam pela pele da cabeca ate a garupa,
-- ondulando, e somem; faiscas finas e brasas completam. Sem luz no peito (tingia o corpo).
-- v2d: 30 rastros (12 em qualidade baixa), cores mais saturadas e rastros tambem pelos flancos (+-1,55 rad).
-- v3 olhos (05/11, pedido do usuario com imagem: "o olho total amarelo, nao uma bola na frente, e uma linha meio saindo do
-- olho para tras"): cada olho vira uma ELIPSE amarela Neon colada sobre o olho do modelo (posicao/normal medidas no Edit
-- de frente e de 3/4) e, do canto de fora, sai uma LINHA curva (Beam, Bezier pelos eixos dos attachments) que abre para
-- tras e sobe em direcao a orelha, afinando e tremulando. Tudo preso ao osso Cabeca (acompanha as animacoes).
M.VIS_FUR = {olho = Color3.fromRGB(255, 190, 60), fioA = Color3.fromRGB(255, 225, 120), fioB = Color3.fromRGB(255, 150, 20),
	fioC = Color3.fromRGB(230, 80, 10), taxaFios = 110, taxaFiosBaixa = 40, taxaBrasas = 30, rastros = 30, rastrosBaixa = 12,
	escuro = Color3.fromRGB(25, 12, 4)}
-- olho direito no espaco do pivo, em repouso (o esquerdo e espelhado em X); medido 05/11 com marcadores no Edit
M.OLHO_FURIA = {pos = Vector3.new(0.55, 7.28, -5.13), normal = Vector3.new(0.75, 0.12, -0.65), tam = Vector3.new(0.24, 0.15, 0.16),   -- 05/11 v3b: elipsoide EMBUTIDO no globo do olho (de lado a v3 sobressaia como uma bola)
	linhaIni = Vector3.new(0.11, 0.03, 0.10), linhaFim = Vector3.new(0.5, 0.95, 1.2),           -- relativos ao centro do olho
	tang0 = Vector3.new(0.85, -0.05, 0.5), tang1 = Vector3.new(0, 0.85, 0.5), curva0 = 0.55, curva1 = 0.5, largura0 = 0.11, largura1 = 0.012}
M.PONTOS_FURIA = {{"Cabeca", 1.0}, {"Pescoco2", 1.2}, {"Coluna3", 1.6}, {"EscapulaE", 1.0}, {"EscapulaD", 1.0},
	{"Coluna2", 1.8}, {"Coluna1", 1.6}, {"Pelve", 1.4}}
M.CAMINHO_FURIA = {{"Cabeca", 1.2, 1.4}, {"Pescoco2", 1.6, 2.1}, {"Coluna3", 2.3, 2.9}, {"Coluna2", 2.4, 3.1}, {"Coluna1", 2.2, 2.9}, {"Pelve", 1.9, 2.4}}   -- osso, meia largura e meia altura do corpo em volta da coluna
local furiasV = {}                      -- [urso] = {...}
local function tirarFuria(urso)
	local f = furiasV[urso]; if not f then return end; furiasV[urso] = nil
	if f.con then f.con:Disconnect() end
	if f.hl then f.hl:Destroy() end
	for _, e in ipairs(f.ems or {}) do e.Enabled = false end
	for _, o in ipairs(f.olhos or {}) do TS:Create(o.p, TweenInfo.new(0.4), {Transparency = 1}):Play(); o.beam.Enabled = false end
	for _, r in ipairs(f.rastros or {}) do r.tr.Enabled = false end
	if f.luz then TS:Create(f.luz, TweenInfo.new(0.5), {Brightness = 0}):Play() end
	task.delay(1.2, function()
		for _, a in ipairs(f.ats or {}) do a:Destroy() end
		for _, o in ipairs(f.olhos or {}) do o.p:Destroy(); o.a0:Destroy(); o.a1:Destroy() end
		for _, r in ipairs(f.rastros or {}) do r.a0:Destroy(); r.a1:Destroy() end
	end)
end
local function emFio(at, V, taxa)
	return emissor(at, {Texture = "rbxasset://textures/particles/fire_sparks_main.dds", LightEmission = 1, LightInfluence = 0,
		Color = ColorSequence.new({ColorSequenceKeypoint.new(0, V.fioA), ColorSequenceKeypoint.new(0.35, V.fioB), ColorSequenceKeypoint.new(1, V.fioC)}),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(0.6, 0.35), NumberSequenceKeypoint.new(1, 0)}),
		Squash = NumberSequence.new(1.6), Orientation = Enum.ParticleOrientation.VelocityParallel,
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.7, 0.3), NumberSequenceKeypoint.new(1, 1)}),
		Lifetime = NumberRange.new(0.3, 0.6), Speed = NumberRange.new(2, 5), SpreadAngle = Vector2.new(25, 25), Rate = taxa, Drag = 1.2,
		EmissionDirection = Enum.NormalId.Top})
end
M.SOM_FURIA = {id = "rbxassetid://9120050567", vel = 0.8, vol = 0.7, inicio = 0.1, dur = 1.3, sai = 0.35, boca = 26}   -- Tiger Snarl 6 (Pro SFX); boca abre pelo volume
local function porFuria(urso, dur)
	tirarFuria(urso)
	if M.som then M.som(M.SOM_FURIA, urso:GetPivot().Position + Vector3.new(0, 6, -4), urso) end
	local V = M.VIS_FUR; local f = {ems = {}, ats = {}, olhos = {}}; furiasV[urso] = f
	-- corpo escurecido + contorno dourado
	local hl = Instance.new("Highlight"); hl.FillColor = V.escuro; hl.OutlineColor = V.fioB; hl.FillTransparency = 0.45
	hl.OutlineTransparency = 0.35; hl.DepthMode = Enum.HighlightDepthMode.Occluded; hl.Adornee = urso; hl.Parent = urso; f.hl = hl
	-- emissores dos fios (2, espalhados pelo corpo) + brasas + peito com luz quente
	local q = baixaQ()
	for i = 1, 2 do local a = Instance.new("Attachment"); a.Parent = workspace.Terrain; table.insert(f.ats, a); table.insert(f.ems, emFio(a, V, (q and V.taxaFiosBaixa or V.taxaFios) / 2)) end
	local aB = Instance.new("Attachment"); aB.Parent = workspace.Terrain; table.insert(f.ats, aB)
	table.insert(f.ems, emissor(aB, {Texture = "rbxasset://textures/particles/sparkles_main.dds", LightEmission = 1, LightInfluence = 0,
		Color = ColorSequence.new(V.fioB, V.fioC), Size = NumberSequence.new(0.22, 0.05), Lifetime = NumberRange.new(1.0, 2.0),
		Speed = NumberRange.new(1, 3), SpreadAngle = Vector2.new(180, 180), Rate = q and V.taxaBrasas / 2 or V.taxaBrasas, Drag = 0.6}))
	-- RASTROS: cada um desliza pela pele da cabeca ate a garupa (lado e altura sorteados), ondulando, e recomeca
	f.rastros = {}
	for i = 1, (q and V.rastrosBaixa or V.rastros) do
		local a0 = Instance.new("Attachment"); a0.Parent = workspace.Terrain; local a1 = Instance.new("Attachment"); a1.Parent = workspace.Terrain
		local tr = Instance.new("Trail"); tr.Attachment0 = a0; tr.Attachment1 = a1; tr.LightEmission = 1; tr.LightInfluence = 0; tr.FaceCamera = true
		tr.Color = ColorSequence.new({ColorSequenceKeypoint.new(0, V.fioA), ColorSequenceKeypoint.new(0.4, V.fioB), ColorSequenceKeypoint.new(1, V.fioC)})
		tr.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.6, 0.35), NumberSequenceKeypoint.new(1, 1)})
		tr.Lifetime = 0.32; tr.MinLength = 0.05; tr.WidthScale = NumberSequence.new(1, 0.2); tr.Enabled = false; tr.Parent = a0
		table.insert(f.rastros, {a0 = a0, a1 = a1, tr = tr, p = 0, vel = 1, lado = 0, alt = 0.6, fase = 0})
	end
	local function sorteia(r) r.p = 0; r.vel = 0.9 + math.random() * 0.9; r.lado = (math.random() * 2 - 1); r.alt = 0.35 + math.random() * 0.75; r.fase = math.random() * 6; r.tr.Enabled = false end
	for _, r in ipairs(f.rastros) do sorteia(r); r.p = math.random() * 0.9 end
	local luz = Instance.new("PointLight"); luz.Color = V.fioB; luz.Brightness = 0; luz.Range = 0.1; luz.Shadows = false; luz.Parent = aB; f.luz = luz
	-- olhos: elipse amarela colada sobre cada olho + linha curva saindo do canto de fora (presos ao osso da cabeca)
	local cab = urso:FindFirstChild("Cabeca", true); local pv = urso:GetPivot(); local O = M.OLHO_FURIA
	if cab and cab:IsA("Bone") then
		for _, sx in ipairs({1, -1}) do
			local function esp(v) return Vector3.new(v.X * sx, v.Y, v.Z) end
			local c = O.pos; local wC = pv:PointToWorldSpace(esp(c)); local wN = pv:VectorToWorldSpace(esp(O.normal)).Unit
			local locCF = cab.WorldCFrame:ToObjectSpace(CFrame.lookAt(wC, wC + wN))
			local p = peca("OlhoFuria", V.olho, Enum.Material.Neon); p.Size = O.tam; p.Transparency = 0
			local sm = Instance.new("SpecialMesh"); sm.MeshType = Enum.MeshType.Sphere; sm.Parent = p; p.Parent = pasta
			local lo = Instance.new("PointLight"); lo.Color = V.olho; lo.Brightness = 1.2; lo.Range = 2.5; lo.Parent = p
			local a0 = Instance.new("Attachment"); a0.Parent = workspace.Terrain; local a1 = Instance.new("Attachment"); a1.Parent = workspace.Terrain
			local bm = Instance.new("Beam"); bm.Attachment0 = a0; bm.Attachment1 = a1; bm.FaceCamera = true; bm.LightEmission = 1; bm.LightInfluence = 0
			bm.Segments = 24; bm.Width0 = O.largura0; bm.Width1 = O.largura1; bm.CurveSize0 = O.curva0; bm.CurveSize1 = O.curva1
			bm.Color = ColorSequence.new({ColorSequenceKeypoint.new(0, V.fioA), ColorSequenceKeypoint.new(0.45, Color3.fromRGB(255, 200, 40)), ColorSequenceKeypoint.new(1, V.fioC)})
			bm.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.7, 0.15), NumberSequenceKeypoint.new(1, 1)}); bm.Parent = a0
			local function lp(v) return cab.WorldCFrame:PointToObjectSpace(pv:PointToWorldSpace(esp(c + v))) end
			local function lv(v) return cab.WorldCFrame:VectorToObjectSpace(pv:VectorToWorldSpace(esp(v))).Unit end
			table.insert(f.olhos, {p = p, locCF = locCF, a0 = a0, a1 = a1, beam = bm, i0 = lp(O.linhaIni), i1 = lp(O.linhaFim), t0 = lv(O.tang0), t1 = lv(O.tang1), fase = sx})
		end
	end
	for _, e in ipairs(f.ems) do e:Emit(25) end
	local t0 = os.clock(); local pontos = M.PONTOS_FURIA
	f.con = RS.RenderStepped:Connect(function()
		if not urso.Parent or os.clock() - t0 > (dur or 6) + 1 then tirarFuria(urso); return end
		local pvA = urso:GetPivot(); local tras = -pvA.LookVector
		-- fios nascem em pontos aleatorios do corpo e correm para tras e para cima
		for i = 1, 2 do
			local pt = pontos[math.random(1, #pontos)]; local b = urso:FindFirstChild(pt[1], true)
			local base = b and b:IsA("Bone") and b.TransformedWorldCFrame.Position or pvA.Position + Vector3.new(0, 5, 0)
			local r = pt[2]; local pos = base + Vector3.new((math.random() - 0.5) * 2 * r, (math.random() - 0.2) * r, (math.random() - 0.5) * 2 * r)
			f.ats[i].WorldCFrame = CFrame.lookAt(pos, pos + tras) * CFrame.Angles(math.rad(-25), 0, 0)    -- topo do attachment = para tras (e um pouco para cima)
			f.ems[i].Acceleration = tras * 6 + Vector3.new(0, 3, 0)
		end
		-- rastros: posicao ao longo do caminho de ossos, por fora do corpo, com ondulacao
		local cam = M.CAMINHO_FURIA
		for _, r in ipairs(f.rastros) do
			r.p += r.vel / 60
			if r.p >= 1 then sorteia(r) else
				local x = r.p * (#cam - 1) + 1; local i0 = math.floor(x); local i1 = math.min(#cam, i0 + 1); local k = x - i0
				local b0 = urso:FindFirstChild(cam[i0][1], true); local b1 = urso:FindFirstChild(cam[i1][1], true)
				if b0 and b1 then
					local q0, q1 = b0.TransformedWorldCFrame.Position, b1.TransformedWorldCFrame.Position
					local p0 = q0:Lerp(q1, k); local w = cam[i0][2] + (cam[i1][2] - cam[i0][2]) * k; local hh = cam[i0][3] + (cam[i1][3] - cam[i0][3]) * k
					local dir = q1 - q0; if dir.Magnitude < 0.01 then dir = tras end; dir = dir.Unit
					local lat = dir:Cross(Vector3.yAxis); if lat.Magnitude < 0.01 then lat = pvA.RightVector end; lat = lat.Unit
					local ang = r.lado * 1.55 + math.sin(r.p * 9 + r.fase) * 0.14      -- -1,55..1,55 rad em volta do dorso e flancos, ondulando
					local pos = p0 + (lat * math.sin(ang) * w + Vector3.yAxis * math.cos(ang) * hh) * (1.0 + 0.08 * r.alt)
					r.a0.WorldPosition = pos; r.a1.WorldPosition = pos + Vector3.yAxis * 0.12
					if not r.tr.Enabled and r.p > 0.04 then r.tr.Enabled = true end
				end
			end
		end
		local c3 = urso:FindFirstChild("Coluna2", true)
		aB.WorldPosition = (c3 and c3:IsA("Bone") and c3.TransformedWorldCFrame.Position or pvA.Position + Vector3.new(0, 5, 0)) + Vector3.new((math.random() - 0.5) * 6, math.random() * 2, (math.random() - 0.5) * 8)
		if cab then
			local cc = cab.TransformedWorldCFrame; local tt = os.clock() - t0
			for _, o in ipairs(f.olhos) do
				o.p.CFrame = cc * o.locCF
				local tre = Vector3.new(0, math.sin(tt * 11 + o.fase) * 0.05, math.sin(tt * 7 + o.fase * 2) * 0.06)      -- a ponta tremula
				o.a0.WorldPosition = cc:PointToWorldSpace(o.i0); o.a1.WorldPosition = cc:PointToWorldSpace(o.i1 + tre)
				o.a0.WorldAxis = cc:VectorToWorldSpace(o.t0); o.a1.WorldAxis = cc:VectorToWorldSpace(o.t1)
				o.beam.Width0 = M.OLHO_FURIA.largura0 * (0.85 + 0.3 * math.sin(tt * 13 + o.fase))
			end
		end
		local pul = 0.5 + 0.5 * math.sin((os.clock() - t0) * 7)
		hl.OutlineTransparency = 0.2 + 0.3 * pul
	end)
end
local function farejou(urso)
	local b = urso:FindFirstChild("Cabeca", true)
	local p = b and b:IsA("Bone") and (b.TransformedWorldCFrame * CFrame.new(0, 0, -1.5)).Position or urso:GetPivot().Position + Vector3.new(0, 4, -5)
	local at = Instance.new("Attachment"); at.WorldPosition = p; at.Parent = workspace.Terrain
	local e = emissor(at, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(Color3.fromRGB(235, 230, 210)),
		Size = NumberSequence.new(0.4, 1.6), Transparency = NumberSequence.new(0.5, 1), Lifetime = NumberRange.new(0.4, 0.7),
		Speed = NumberRange.new(2, 4), SpreadAngle = Vector2.new(30, 30), Rate = 0})
	e:Emit(12); Debris:AddItem(at, 1.2)
end
local function marcar(alvos, dur)
	local V = M.VIS_PAS
	for _, m in ipairs(alvos or {}) do
		if typeof(m) == "Instance" and m.Parent then
			local hl = Instance.new("Highlight"); hl.FillColor = V.corFaro; hl.OutlineColor = V.corFaro; hl.FillTransparency = 0.75
			hl.OutlineTransparency = 0; hl.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop; hl.Adornee = m; hl.Parent = m
			local ok, ext = pcall(function() return m:GetExtentsSize() end)
			local bb = Instance.new("BillboardGui"); bb.Name = "FaroProtetorMarca"; bb.AlwaysOnTop = true; bb.Size = UDim2.fromOffset(34, 34)
			bb.StudsOffsetWorldSpace = Vector3.new(0, (ok and ext.Y or 5) / 2 + 1.5, 0); bb.Adornee = m:IsA("Model") and (m.PrimaryPart or m:FindFirstChildWhichIsA("BasePart", true)) or nil
			local fr = Instance.new("Frame"); fr.Size = UDim2.fromScale(1, 1); fr.BackgroundColor3 = V.corFaro; fr.BackgroundTransparency = 0.15; fr.Parent = bb
			Instance.new("UICorner", fr).CornerRadius = UDim.new(1, 0)
			local st = Instance.new("UIStroke"); st.Color = Color3.fromRGB(90, 60, 0); st.Thickness = 2; st.Parent = fr
			bb.Parent = Players.LocalPlayer:FindFirstChildOfClass("PlayerGui")
			local t0 = os.clock(); local con
			con = RS.RenderStepped:Connect(function()
				local k = (os.clock() - t0) / (dur or 3)
				if k >= 1 or not m.Parent then con:Disconnect(); hl:Destroy(); bb:Destroy(); return end
				local pul = 0.5 + 0.5 * math.sin((os.clock() - t0) * 10)
				fr.Size = UDim2.fromScale(0.75 + 0.25 * pul, 0.75 + 0.25 * pul); hl.FillTransparency = 0.6 + 0.3 * k
			end)
			M.ultimaMarca = (M.ultimaMarca or 0) + 1
		end
	end
end
function M.passivasEfx(d)
	if not d.urso then return end
	if d.tipo == "FuriaProtetor" then
		if d.fase == "inicio" then porFuria(d.urso, d.dur) else tirarFuria(d.urso) end
	elseif d.tipo == "FaroProtetor" then
		if d.fase == "farejou" then farejou(d.urso) elseif d.fase == "marca" then marcar(d.alvos, d.dur) end
	end
end
M.furiasV = furiasV
