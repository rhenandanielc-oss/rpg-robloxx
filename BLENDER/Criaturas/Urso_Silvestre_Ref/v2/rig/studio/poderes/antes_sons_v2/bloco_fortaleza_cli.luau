-- ================================================================== Fortaleza Viva (Etapa 4, 05/11) - DOMO de LINHAS de energia (v3)
-- So apresentacao: o servidor decide reserva, golpes, quebra e duracao. Pedidos do usuario (05/11):
--   v2: "escudo em volta de todo o corpo, ate no ar; animacao de trincado e de retencao com som; 50% maior; amarelo;
--       particulas formam o escudo GRADUALMENTE em 3-5 s";
--   v3: "algo mais como LINHAS, que vao se formando em volta do urso; a rachadura 100% NO escudo (no video, por o escudo
--       nao ser reto, a rachadura ficava para fora)".
-- Aqui:
--   * DOMO = malha de LINHAS amarelas (meridianos + paralelos) sobre uma esfera de raio do servidor (18) + uma pelicula
--     ForceField bem translucida (esfera; a metade de baixo fica sob o chao). Tudo soldado a uma raiz que segue o urso;
--   * FORMACAO em formacao s: as linhas se DESENHAM aos poucos (anel da base gira em volta do urso -> meridianos sobem da
--     base ao topo -> paralelos fecham), cada trecho acende quando a "cabeca" da linha passa; particulas saem do corpo do
--     urso o tempo todo e fagulhas voam ate as cabecas das linhas; a pelicula aparece no fim;
--   * GOLPE: no ponto da esfera virado para o atacante -> RETENCAO (anel de luz que se abre SOBRE a esfera, linhas
--     vizinhas brilham, particulas) + SOM de retencao + TRINCAS desenhadas SOBRE a superficie: cada trinca e uma
--     sequencia de trechos curtos (0,45 stud) em cima da esfera (raio + 0,06), com desvios, que crescem do ponto;
--   * QUEBRA: as linhas estilhacam para fora + estouro + tremor; FIM: o domo apaga.
-- Nada colide nem e consultado (CanCollide/CanQuery/CanTouch falsos). Qualidade baixa: metade das linhas.
-- SOM: o projeto nao tem audio do urso; usa sons EMBUTIDOS do Roblox (content/sounds), so como PROVISORIO.
M.SOM_FV_ATIVAR = {id = "rbxassetid://1841209502", vel = 0.9, vol = 0.8}         -- Beautiful Shimmer (APM): acompanha a formacao do domo
M.SOM_FV_RUGIDO = {id = "rbxassetid://9116300504", vel = 0.72, vol = 1.0, atraso = 0.62}   -- rugido grave da FortalezaInicio (0,7 s)
M.SOM_FV_RETENCAO = {id = "rbxasset://sounds/impact_water.mp3", vel = 0.55, vol = 0.9}     -- PROVISORIO (embutido)
M.SOM_FV_QUEBRA = {id = "rbxassetid://9114592102", vel = 0.8, vol = 1.0}          -- Glass Breaks 11 (ProSoundEffects)
M.VIS_FV = {meridianos = 14, meridianosBaixa = 8, paralelos = {0, 20, 40, 60, 75}, passoGraus = 7.5, espessura = 0.16,
	cor = Color3.fromRGB(255, 215, 40), corBrilho = Color3.fromRGB(255, 255, 210), corTrinca = Color3.fromRGB(140, 80, 0),
	transpLinha = 0.15, transpPelicula = 0.8, taxaCorpo = 45, trincasPorGolpe = 6, passoTrinca = 0.45}
local fortesV = {}                      -- [urso] = {raiz, linhas = {{p, t}}, pelicula, con, raio, t0, formacao}
M.fortesV = fortesV
local function corpoFV(urso)
	local b = urso:FindFirstChild("Coluna3", true)
	return b and b:IsA("Bone") and b.TransformedWorldCFrame.Position or urso:GetPivot().Position + Vector3.new(0, 4, 0)
end
local function somFV(s, pos)
	if not s then return end
	if M.som then M.som(s, pos); return end
	local at = Instance.new("Attachment"); at.WorldPosition = pos; at.Parent = workspace.Terrain
	local so = Instance.new("Sound"); so.SoundId = s.id; so.PlaybackSpeed = s.vel or 1; so.Volume = s.vol or 1
	so.RollOffMaxDistance = 140; so.Parent = at; so:Play(); Debris:AddItem(at, 4)
end
local function soldar(p, raiz)                -- chamar com a peca ja no lugar e ja dentro do workspace
	local w = Instance.new("WeldConstraint"); w.Part0 = raiz; w.Part1 = p; w.Parent = p
	p.Massless = true; p.Anchored = false
end
local function esf(phi, th) return Vector3.new(math.cos(phi) * math.cos(th), math.sin(phi), math.cos(phi) * math.sin(th)) end
-- trecho reto entre dois pontos da esfera (curto: a flecha fica < 0,02 stud), centrado na superficie
local function trecho(nome, cor, a, b, esp, pai)
	local m = (a + b) / 2; local L = (b - a).Magnitude; if L < 0.02 then return nil end
	local p = peca(nome, cor, Enum.Material.Neon); p.Size = Vector3.new(esp, esp, L + esp * 0.6); p.Transparency = 1
	p.CFrame = CFrame.lookAt(m, b, m.Unit); p.Parent = pai; return p
end
local function limparFV(urso)
	local f = fortesV[urso]; if not f then return end; fortesV[urso] = nil
	if f.con then f.con:Disconnect() end
	if f.emAt then f.emAt:Destroy() end
	for _, a in ipairs(f.aneis or {}) do for _, s in ipairs(a.seg) do s:Destroy() end end
	f.raiz:Destroy()                    -- leva linhas, pelicula e trincas soldadas
end
local function montarDomo(urso, raio, formacao)
	limparFV(urso)
	local V = M.VIS_FV; local c = urso:GetPivot().Position
	local raiz = peca("RaizDomoFortaleza", V.cor); raiz.Transparency = 1; raiz.Size = Vector3.new(0.2, 0.2, 0.2); raiz.CFrame = CFrame.new(c); raiz.Parent = pasta
	local f = {raiz = raiz, linhas = {}, aneis = {}, raio = raio, t0 = os.clock(), formacao = formacao, cabecas = {}}; fortesV[urso] = f
	local function poe(p, t) if p then p.CFrame = p.CFrame + c; soldar(p, raiz); table.insert(f.linhas, {p = p, t = t, aceso = false}) end end
	local passo = math.rad(V.passoGraus)
	-- (1) anel da base: gira em volta do urso em 22% do tempo
	local nB = math.floor(2 * math.pi / passo + 0.5)
	for i = 0, nB - 1 do
		local a, b = esf(0.02, i * passo) * raio, esf(0.02, (i + 1) * passo) * raio
		poe(trecho("LinhaFortaleza", V.cor, a, b, V.espessura * 1.4, raiz), formacao * 0.22 * i / nB)
	end
	-- (2) meridianos: sobem da base ao topo, entre 15% e 75% do tempo (cada um um pouco depois do anterior)
	local nM = baixaQ() and V.meridianosBaixa or V.meridianos; local nS = math.floor(math.rad(90) / passo + 0.5)
	for m = 0, nM - 1 do
		local th = m / nM * 2 * math.pi; local ini = formacao * (0.15 + 0.2 * m / nM)
		for k = 0, nS - 1 do
			local a, b = esf(k * passo, th) * raio, esf(math.min(math.rad(89.5), (k + 1) * passo), th) * raio
			poe(trecho("LinhaFortaleza", V.cor, a, b, V.espessura, raiz), ini + formacao * 0.4 * k / nS)
		end
	end
	-- (3) paralelos: fecham em volta, de baixo para cima, entre 40% e 95% do tempo
	for j, g in ipairs(V.paralelos) do
		if g > 0 then
			local phi = math.rad(g); local n = math.max(8, math.floor(2 * math.pi * math.cos(phi) / passo + 0.5))
			local ini = formacao * (0.40 + 0.11 * (j - 2))
			for i = 0, n - 1 do
				local a, b = esf(phi, i / n * 2 * math.pi) * raio, esf(phi, (i + 1) / n * 2 * math.pi) * raio
				poe(trecho("LinhaFortaleza", V.cor, a, b, V.espessura, raiz), ini + formacao * 0.18 * i / n)
			end
		end
	end
	-- pelicula (esfera translucida; a metade de baixo fica sob o chao): aparece no fim da formacao
	local pel = peca("PeliculaFortaleza", V.cor, Enum.Material.ForceField); pel.Shape = Enum.PartType.Ball
	pel.Size = Vector3.new(raio * 2, raio * 2, raio * 2); pel.Transparency = 1; pel.CFrame = CFrame.new(c); pel.Parent = raiz; soldar(pel, raiz)
	f.pelicula = pel
	table.sort(f.linhas, function(a, b) return a.t < b.t end)
	local prox = 1
	f.con = RS.RenderStepped:Connect(function()
		if not urso.Parent then limparFV(urso); return end
		local pv = urso:GetPivot().Position
		f.raiz.CFrame = CFrame.new(pv)
		local t = os.clock() - f.t0
		while prox <= #f.linhas and f.linhas[prox].t <= t do      -- acende os trechos na ordem (a "cabeca" da linha avanca)
			local q = f.linhas[prox]; prox += 1; q.aceso = true
			q.p.Transparency = 0; q.p.Color = V.corBrilho
			TS:Create(q.p, TweenInfo.new(0.35), {Transparency = V.transpLinha, Color = V.cor}):Play()
			f.ultimaCabeca = q.p
		end
		if not f.pelVis and t >= formacao * 0.7 then f.pelVis = true; TS:Create(pel, TweenInfo.new(formacao * 0.3), {Transparency = V.transpPelicula}):Play() end
		for i = #f.aneis, 1, -1 do                                 -- aneis de retencao: abrem SOBRE a esfera
			local a = f.aneis[i]; local k = (os.clock() - a.t0) / 0.5
			if k >= 1 then for _, s in ipairs(a.seg) do s:Destroy() end; table.remove(f.aneis, i)
			else
				local alfa = math.rad(2 + 20 * (1 - (1 - k) ^ 2)); local n = #a.seg
				for s, sp in ipairs(a.seg) do
					local b1 = a.t1 * math.cos((s - 1) / n * 2 * math.pi) + a.t2 * math.sin((s - 1) / n * 2 * math.pi)
					local b2 = a.t1 * math.cos(s / n * 2 * math.pi) + a.t2 * math.sin(s / n * 2 * math.pi)
					local p1 = (a.n * math.cos(alfa) + b1 * math.sin(alfa)) * (f.raio + 0.08)
					local p2 = (a.n * math.cos(alfa) + b2 * math.sin(alfa)) * (f.raio + 0.08)
					local mm = (p1 + p2) / 2
					sp.Size = Vector3.new(0.22, 0.22, (p2 - p1).Magnitude + 0.1); sp.CFrame = f.raiz.CFrame * CFrame.lookAt(mm, p2, mm.Unit)
					sp.Transparency = 0.1 + 0.9 * k
				end
			end
		end
		if f.emAt then f.emAt.WorldPosition = corpoFV(urso) end
	end)
	return f
end
-- particulas do corpo durante a formacao + fagulhas do peito ate a cabeca da linha que esta se desenhando
local function formarDomo(urso, f, formacao)
	local V = M.VIS_FV
	local a = Instance.new("Attachment"); a.WorldPosition = corpoFV(urso); a.Parent = workspace.Terrain; f.emAt = a
	local e = emissor(a, {Texture = "rbxasset://textures/particles/sparkles_main.dds", Color = ColorSequence.new(V.cor), LightEmission = 1,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.8), NumberSequenceKeypoint.new(1, 0.1)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.1), NumberSequenceKeypoint.new(1, 1)}),
		Lifetime = NumberRange.new(0.6, 1.1), Speed = NumberRange.new(8, 16), SpreadAngle = Vector2.new(70, 70),
		Rate = baixaQ() and V.taxaCorpo / 2 or V.taxaCorpo, Drag = 1.5, EmissionDirection = Enum.NormalId.Top})
	e:Emit(30)
	task.delay(formacao + 0.3, function() if e.Parent then e.Enabled = false end end)
	local nF = baixaQ() and 14 or 28
	for i = 1, nF do
		task.delay(formacao * (i - 1) / nF, function()
			if fortesV[urso] ~= f or not f.ultimaCabeca then return end
			local de = corpoFV(urso); local para = f.ultimaCabeca.Position; local dur = 0.35 + math.random() * 0.2
			local fg = peca("FagulhaFortaleza", V.cor, Enum.Material.Neon); fg.Shape = Enum.PartType.Ball; fg.Size = Vector3.new(0.45, 0.45, 0.45)
			fg.CFrame = CFrame.new(de); fg.Parent = pasta
			local meio = (de + para) / 2 + Vector3.new(0, 2 + math.random() * 2, 0)
			TS:Create(fg, TweenInfo.new(dur / 2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = CFrame.new(meio)}):Play()
			task.delay(dur / 2, function() if fg.Parent then TS:Create(fg, TweenInfo.new(dur / 2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = CFrame.new(para)}):Play() end end)
			task.delay(dur, function() fg:Destroy() end)
		end)
	end
end
local function direcaoGolpe(f, d)
	local c = f.raiz.Position; local o = d.pos or d.alvoPos or (c + Vector3.new(1, 0.5, 0))
	local dir = o - c; if dir.Magnitude < 0.1 then dir = Vector3.new(1, 0.5, 0) end
	return Vector3.new(dir.X, math.max(dir.Y, dir.Magnitude * 0.12), dir.Z).Unit      -- n (local, a partir do centro)
end
local function tangentes(n)
	local t1 = n:Cross(Vector3.yAxis); if t1.Magnitude < 0.1 then t1 = n:Cross(Vector3.xAxis) end; t1 = t1.Unit
	return t1, n:Cross(t1).Unit
end
local function golpeFV(urso, d)
	local f = fortesV[urso]; if not f then return end
	local V = M.VIS_FV; local n = direcaoGolpe(f, d); local R = f.raio
	local frac = (d.reserva or 0) / math.max(1, d.max or 1); local pMundo = f.raiz.Position + n * R
	-- RETENCAO: anel de luz que se abre sobre a esfera (animado no RenderStepped) + linhas vizinhas brilham + particulas
	local t1, t2 = tangentes(n); local seg = {}
	for i = 1, (baixaQ() and 12 or 20) do local s = peca("OndaFortaleza", V.corBrilho, Enum.Material.Neon); s.Transparency = 1; s.Parent = pasta; table.insert(seg, s) end
	table.insert(f.aneis, {n = n, t1 = t1, t2 = t2, seg = seg, t0 = os.clock()})
	for _, q in ipairs(f.linhas) do
		if q.aceso then
			local dd = (q.p.Position - pMundo).Magnitude
			if dd < 8 then q.p.Color = V.corBrilho; q.p.Transparency = 0; TS:Create(q.p, TweenInfo.new(0.3 + dd * 0.05), {Color = V.cor, Transparency = V.transpLinha}):Play() end
		end
	end
	if f.pelicula then f.pelicula.Transparency = 0.55; TS:Create(f.pelicula, TweenInfo.new(0.4), {Transparency = V.transpPelicula}):Play() end
	local a = Instance.new("Attachment"); a.WorldCFrame = CFrame.lookAt(pMundo, pMundo - n); a.Parent = workspace.Terrain
	local e = emissor(a, {Texture = "rbxasset://textures/particles/sparkles_main.dds", Color = ColorSequence.new(V.corBrilho), LightEmission = 1,
		Size = NumberSequence.new(0.6, 0.05), Lifetime = NumberRange.new(0.3, 0.6), Speed = NumberRange.new(6, 12),
		SpreadAngle = Vector2.new(85, 85), Rate = 0, Drag = 5, EmissionDirection = Enum.NormalId.Front})
	e:Emit(baixaQ() and 15 or 35); Debris:AddItem(a, 1)
	somFV(M.SOM_FV_RETENCAO, pMundo)
	-- TRINCAS SOBRE a superficie: cada uma anda pela esfera em trechos curtos (raio + 0,06) e acende do ponto para fora
	local Rt = R + 0.06; local escala = 1 + 1.6 * (1 - frac); local passoT = V.passoTrinca
	for i = 1, V.trincasPorGolpe do
		local ang = (i / V.trincasPorGolpe) * 2 * math.pi + math.random() * 0.6
		local dirT = (t1 * math.cos(ang) + t2 * math.sin(ang)).Unit
		local atual = n * Rt; local nPassos = math.floor((1.6 + math.random() * 1.6) * escala / passoT + 0.5)
		for k = 1, nPassos do
			local desv = (math.random() - 0.5) * 0.9
			local nrm = atual.Unit; local tg = (dirT - nrm * dirT:Dot(nrm)).Unit
			local lat = nrm:Cross(tg).Unit; tg = (tg + lat * desv).Unit
			local prox = (atual + tg * passoT).Unit * Rt                          -- de volta para a superficie
			local tr = trecho("TrincaFortaleza", V.corTrinca, atual, prox, 0.13, nil)
			if tr then
				tr.CFrame = f.raiz.CFrame * tr.CFrame; tr.Parent = f.raiz; soldar(tr, f.raiz)
				task.delay(0.03 * k, function() if tr.Parent then tr.Transparency = 0.05 end end)
			end
			dirT = (prox - atual).Unit; atual = prox
		end
	end
end
local function quebraFV(urso)
	local f = fortesV[urso]; if not f then return end
	local V = M.VIS_FV; local c = f.raiz.Position
	for i, q in ipairs(f.linhas) do
		if q.aceso and i % (baixaQ() and 4 or 2) == 0 then
			local k = peca("CacoFortaleza", V.cor, Enum.Material.Neon); k.Transparency = 0.1
			k.Size = q.p.Size; k.CFrame = q.p.CFrame; k.Parent = pasta
			local fora = (q.p.Position - c).Unit
			TS:Create(k, TweenInfo.new(0.75, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = k.CFrame * CFrame.Angles(math.random() * 3, math.random() * 3, 0) + fora * (3 + math.random() * 5) + Vector3.new(0, 1, 0), Transparency = 1}):Play()
			task.delay(0.8, function() k:Destroy() end)
		end
	end
	local a = Instance.new("Attachment"); a.WorldPosition = c + Vector3.new(0, 4, 0); a.Parent = workspace.Terrain
	local e = emissor(a, {Texture = "rbxasset://textures/particles/sparkles_main.dds", Color = ColorSequence.new(V.cor), LightEmission = 1,
		Size = NumberSequence.new(0.8, 0.1), Lifetime = NumberRange.new(0.6, 1.0), Speed = NumberRange.new(25, 40),
		SpreadAngle = Vector2.new(180, 180), Rate = 0, Drag = 1.5})
	e:Emit(baixaQ() and 50 or 120); Debris:AddItem(a, 1.6)
	tremorCurto(c); somFV(M.SOM_FV_QUEBRA, c)
	limparFV(urso)
end
local function fimFV(urso)
	local f = fortesV[urso]; if not f then return end
	for _, p in ipairs(f.raiz:GetChildren()) do if p:IsA("BasePart") then TS:Create(p, TweenInfo.new(0.8), {Transparency = 1}):Play() end end
	task.delay(0.85, function() if fortesV[urso] == f then limparFV(urso) end end)
end
function M.fortalezaEfx(d)
	if not d.urso then return end
	if d.fase == "inicio" then somFV(M.SOM_FV_RUGIDO, d.urso:GetPivot().Position + Vector3.new(0, 6, 0)); return end
	if d.fase == "ativar" then
		local form = d.formacao or 4
		local f = montarDomo(d.urso, d.raio or 18, form); formarDomo(d.urso, f, form); somFV(M.SOM_FV_ATIVAR, d.urso:GetPivot().Position)
		M.ultimaFortaleza = #f.linhas
	elseif d.fase == "golpe" then golpeFV(d.urso, d)
	elseif d.fase == "quebra" then quebraFV(d.urso)
	elseif d.fase == "fim" then fimFV(d.urso) end
end
