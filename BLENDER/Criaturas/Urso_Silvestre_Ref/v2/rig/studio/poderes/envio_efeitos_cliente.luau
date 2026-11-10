local c = game.ReplicatedStorage.Urso_v2_Lab.EfeitosUrso_Cliente
c.Source = [=====[-- EfeitosUrso_Cliente (ModuleScript em ReplicatedStorage.Urso_v2_Lab) - so APRESENTA o que o servidor decidiu.
-- Golpe Colossal: rachaduras temporarias coladas ao chao + placas de chao quebradas + pedras + poeira + tremor local de
-- camera, no instante do contato (evento "impacto" do servidor). Nada aqui decide dano, alvo ou duracao de controle.
-- v2 (04/11, pedido do usuario: "rachaduras com maior alcance e mais reais"):
--   * alcance ~90% do raio do golpe (o servidor manda o raio), rachaduras que CRESCEM do centro para fora (~45 studs/s);
--   * tracado irregular (desvio por segmento), largura afinando ate a ponta, RAMIFICACOES;
--   * fenda escura com borda levantada na cor do chao (lida do raycast: cor da peca ou do material do Terrain);
--   * placas de chao quebradas e inclinadas em volta do centro, pedras que saltam e assentam, poeira ao longo das fendas.
-- Aderencia: cada segmento e posicionado por RAYCAST PARA BAIXO a partir de 2 studs acima do ponto ANTERIOR (segue a
-- inclinacao, nunca pega teto/outro andar); a fenda para em parede (raycast horizontal) ou degrau > 1,2 stud.
-- Nada colide, nada e consultado por raycast de jogo (CanCollide/CanQuery/CanTouch falsos); Terrain e mapa intactos.
-- Valores visuais = LABORATORIO. Qualidade grafica baixa so reduz a quantidade de pecas (regra de combate nao muda).
-- v3 (04/11, "rachaduras mais altas"): no capim da Floresta a fenda rente ao chao sumia. Agora a terra LEVANTA dos dois
--   lados da fenda (placas de solo inclinadas, ate ~1,3 stud perto do centro, baixando para a ponta), na cor de TERRA
--   exposta (marrom, misturada 20% com a cor do chao); placas centrais e pedras maiores; poeira mais alta.
--   A altura depende do chao: sobre Terrain Grass/LeafyGrass (capim de ~2 studs) as bordas sobem ate 2,4; nos demais
--   chaos (pedra, terra, pecas) ficam em 0,8, para nao virar um amontoado de placas.
-- v4 (04/11, "mais poeira e pedras"): ERUPCOES ao longo das fendas, no ritmo em que elas crescem: coluna de poeira
--   que sobe acima do capim + pedras arremessadas (2,5-4,5 studs de altura) que caem perto. Le o terremoto mesmo onde
--   o capim esconde o chao. Substitui a poeira fraca que havia ao longo das fendas.
-- v5 (04/11, "3x mais ... em volta de todo seu corpo"): as fendas saem de TODO o contorno do corpo (elipse em volta
--   do urso, alem do ponto das patas) e vao ~3x mais longe (alcance = 2,45 x raio do golpe, ~34 studs com raio 14);
--   o passo do segmento cresce com a distancia (menos pecas longe); erupcoes em volta do corpo inteiro (ate 32).
--   ATENCAO: so o VISUAL cresceu; o raio de DANO continua o do servidor (LAB, 14).
-- Som: NENHUM audio do urso existe no projeto (M0 04/11) -> ganchos SOM_RUGIDO / SOM_IMPACTO vazios, a preencher.
local RS = game:GetService("RunService")
local TS = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local M = {}
M.VIS = {                -- LABORATORIO (visual)
	alcance = 2.45,              -- fracao do raio do golpe (v5: ~3x a v4)
	fendasCorpo = 16, contorno = {3.8, 7.2},   -- fendas saindo do contorno do corpo (semi-eixos lateral, longitudinal)
	passoLonge = 0.045,          -- o passo cresce 0,045 stud por stud de distancia
	fendas = 6, ramificar = 0.30, passo = 0.85, desvio = 0.42,
	largura0 = 0.95, larguraPonta = 0.10, espessura = 0.05,
	velocidade = 45,             -- studs/s de crescimento
	placas = 9, pedras = 14,
	levante = 0.8, levanteCapim = 2.4, levanteMin = 0.35, corTerra = Color3.fromRGB(96, 74, 52),   -- bordas levantadas (studs)
	materiaisCapim = {Grass = true, LeafyGrass = true},   -- chao com capim alto do terreno (cobre ~2 studs, medido 04/11)
	duracao = 6.0, sumir = 1.5,
	tremorMax = 0.35, tremorDur = 0.55, tremorAlcance = 90,
	erupcoes = 32, pedrasErupcao = 3, alturaErupcao = {2.5, 4.5}, espacoErupcao = 3.5,
	qualidadeBaixa = {fendas = 4, fendasCorpo = 8, ramificar = 0.10, placas = 5, pedras = 6, erupcoes = 12, pedrasErupcao = 2},
}
M.SOM_RUGIDO = nil       -- rbxassetid do rugido quando existir (PENDENTE)
M.SOM_IMPACTO = nil      -- rbxassetid do impacto quando existir (PENDENTE)
local pasta = workspace:FindFirstChild("Urso_v2_EfeitosLab") or Instance.new("Folder")
pasta.Name = "Urso_v2_EfeitosLab"; pasta.Parent = workspace
M.pasta = pasta

local function params(urso)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
	local ex = {pasta, urso}; for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(ex, p.Character) end end
	for _, m in ipairs(game:GetService("CollectionService"):GetTagged("AlvoTesteUrso")) do table.insert(ex, m) end
	rp.FilterDescendantsInstances = ex; return rp
end
local function corChao(hit)
	if not hit then return Color3.fromRGB(110, 96, 80) end
	if hit.Instance:IsA("Terrain") then
		local ok, c = pcall(function() return workspace.Terrain:GetMaterialColor(hit.Material) end); if ok then return c end
	elseif hit.Instance:IsA("BasePart") then return hit.Instance.Color end
	return Color3.fromRGB(110, 96, 80)
end
local function escurecer(c, k) return Color3.new(c.R * k, c.G * k, c.B * k) end
local function peca(nome, cor, mat)
	local p = Instance.new("Part"); p.Name = nome; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Material = mat or Enum.Material.Slate; p.Color = cor; p.TopSurface = Enum.SurfaceType.Smooth
	return p
end
-- um segmento da fenda: fenda escura no fundo + DUAS placas de terra levantadas e inclinadas para fora, uma de cada
-- lado (altura h, que diminui do centro para a ponta). Nas pontas finas (h pequeno) fica so uma borda baixa.
local function segmento(a, b, n, larg, h, corBorda, corFenda, partes, atraso)
	local d = b - a; local len = d.Magnitude; if len < 0.05 then return end
	local meio = (a + b) / 2
	local cf = CFrame.lookAt(meio, meio + d, n)
	local novas = {}
	local fenda = peca("Fenda", corFenda, Enum.Material.Basalt)
	fenda.Size = Vector3.new(larg, M.VIS.espessura, len + 0.15); fenda.CFrame = cf + n * 0.03
	table.insert(novas, fenda)
	if h >= M.VIS.levanteMin then
		for _, lado in ipairs({-1, 1}) do
			local pl = peca("Levante", corBorda:Lerp(escurecer(corBorda, 0.75), math.random() * 0.6), Enum.Material.Ground)
			local alt = h * (0.75 + 0.5 * math.random())
			local ang = math.rad(28 + math.random() * 22)                  -- inclinada para fora
			pl.Size = Vector3.new(0.22 + 0.12 * math.random(), alt / math.cos(ang), len + 0.25)
			-- base na beira da fenda, gira em torno do eixo da fenda e sobe
			pl.CFrame = cf * CFrame.new(lado * (larg / 2 + 0.06), 0, 0) * CFrame.Angles(0, 0, -lado * ang) * CFrame.new(0, pl.Size.Y / 2 - 0.08, 0)
			table.insert(novas, pl)
		end
	else
		local borda = peca("Borda", corBorda, Enum.Material.Ground)
		borda.Size = Vector3.new(larg * 1.9, M.VIS.espessura * 1.6 + h * 0.4, len + 0.12); borda.CFrame = cf + n * (borda.Size.Y / 2 - 0.02)
		table.insert(novas, borda)
	end
	for _, p in ipairs(novas) do
		table.insert(partes, p)
		task.delay(atraso, function() if pasta.Parent then p.Parent = pasta end end)     -- cresce do centro para fora
	end
end
local function fenda(P, dir, compr, larg0, rp, corBorda, corFenda, partes, nivel, distBase, cfg)
	local V = M.VIS; local atual, dist = P, distBase or 0; local feito, s = 0, 0
	while feito < compr and s < 80 do
		s += 1
		local k = feito / compr
		local giro = (math.random() - 0.5) * 2 * V.desvio
		dir = (CFrame.Angles(0, giro, 0) * dir).Unit
		local passo = V.passo + dist * V.passoLonge                           -- longe: segmentos maiores (menos pecas)
		local alvo = atual + dir * passo * (0.75 + 0.5 * math.random())
		if workspace:Raycast(atual + Vector3.new(0, 0.6, 0), Vector3.new(alvo.X - atual.X, 0, alvo.Z - atual.Z), rp) then break end   -- parede
		local hit = workspace:Raycast(Vector3.new(alvo.X, atual.Y + 2.0, alvo.Z), Vector3.new(0, -4.0, 0), rp)
		if not hit or math.abs(hit.Position.Y - atual.Y) > 1.2 then break end                                  -- sem chao ou degrau
		local larg = larg0 + (V.larguraPonta - larg0) * k
		local d = (hit.Position - atual).Magnitude; dist += d; feito += d
		local h = cfg.levante * (1 - k) ^ 0.8 * (nivel == 0 and 1 or 0.55)
		segmento(atual, hit.Position, hit.Normal, larg, h, corBorda, corFenda, partes, dist / V.velocidade)
		if s % 3 == 0 then table.insert(cfg.erup, {pos = hit.Position, n = hit.Normal, t = dist / V.velocidade, nivel = nivel}) end
		if nivel < 2 and s > 1 and k < 0.8 and math.random() < cfg.ramificar then
			local lado = math.random() < 0.5 and -1 or 1
			local dirR = (CFrame.Angles(0, lado * math.rad(30 + math.random() * 28), 0) * dir).Unit
			fenda(hit.Position, dirR, (compr - feito) * (0.35 + 0.25 * math.random()), larg * 0.6, rp, corBorda, corFenda, partes, nivel + 1, dist, cfg)
		end
		atual = hit.Position
	end
end
function M.rachaduras(P, N, urso, raio)
	local V = M.VIS; local rp = params(urso)
	local q = settings().Rendering.QualityLevel.Value
	local baixa = q > 0 and q <= 3
	local cfg = {fendas = baixa and V.qualidadeBaixa.fendas or V.fendas, ramificar = baixa and V.qualidadeBaixa.ramificar or V.ramificar,
		placas = baixa and V.qualidadeBaixa.placas or V.placas, pedras = baixa and V.qualidadeBaixa.pedras or V.pedras,
		fendasCorpo = baixa and V.qualidadeBaixa.fendasCorpo or V.fendasCorpo,
		erupcoes = baixa and V.qualidadeBaixa.erupcoes or V.erupcoes, pedrasErupcao = baixa and V.qualidadeBaixa.pedrasErupcao or V.pedrasErupcao, erup = {}}
	local hit0 = workspace:Raycast(P + Vector3.new(0, 1.0, 0), Vector3.new(0, -2.5, 0), rp)
	local base = corChao(hit0)
	local corBorda = V.corTerra:Lerp(base, 0.2)                     -- terra exposta (o capim nao 'racha' verde)
	local corFenda = escurecer(V.corTerra, 0.22)
	local partes = {}
	local alcance = (raio or 14) * V.alcance
	local capim = hit0 and hit0.Instance:IsA("Terrain") and V.materiaisCapim[hit0.Material.Name] or false
	cfg.levante = capim and V.levanteCapim or V.levante; M.ultimoChao = hit0 and hit0.Material.Name or "?"
	-- 1) fendas que saem do ponto das patas (mais curtas: o resto do alcance vem do contorno do corpo)
	for i = 1, cfg.fendas do
		local ang = (i / cfg.fendas) * math.pi * 2 + (math.random() - 0.5) * 0.6
		local compr = alcance * (0.35 + 0.2 * math.random())
		fenda(P, Vector3.new(math.cos(ang), 0, math.sin(ang)), compr, V.largura0 * (0.8 + 0.4 * math.random()), rp, corBorda, corFenda, partes, 0, 0, cfg)
	end
	-- 2) fendas que saem de TODO o contorno do corpo (elipse em volta do urso), apontando para fora
	if urso and urso.Parent then
		local cf = urso:GetPivot(); local la, lo = V.contorno[1], V.contorno[2]
		for i = 1, cfg.fendasCorpo do
			local th = (i / cfg.fendasCorpo) * math.pi * 2 + (math.random() - 0.5) * 0.3
			local loc = Vector3.new(math.cos(th) * la, 0, math.sin(th) * lo)
			local w = cf:PointToWorldSpace(loc)
			local normal = cf:VectorToWorldSpace(Vector3.new(math.cos(th) / la, 0, math.sin(th) / lo)); normal = Vector3.new(normal.X, 0, normal.Z).Unit
			local h0 = workspace:Raycast(Vector3.new(w.X, P.Y + 2.0, w.Z), Vector3.new(0, -4.0, 0), rp)
			if h0 and not workspace:Raycast(P + Vector3.new(0, 0.6, 0), Vector3.new(w.X - P.X, 0, w.Z - P.Z), rp) then
				local compr = alcance * (0.7 + 0.3 * math.random())
				fenda(h0.Position, normal, compr, V.largura0 * (0.9 + 0.4 * math.random()), rp, corBorda, corFenda, partes, 0, (h0.Position - P).Magnitude, cfg)
			end
		end
	end
	-- centro: afundamento escuro + placas de chao quebradas, inclinadas para fora
	local c = peca("Afundamento", corFenda, Enum.Material.Basalt)
	c.Shape = Enum.PartType.Cylinder; c.Size = Vector3.new(0.06, 2.6, 2.6)
	c.CFrame = CFrame.lookAt(P + N * 0.03, P + N * 1.03) * CFrame.Angles(0, math.rad(90), 0); c.Parent = pasta; table.insert(partes, c)
	for i = 1, cfg.placas do
		local ang = (i / cfg.placas) * math.pi * 2 + math.random() * 0.5
		local r = 1.4 + math.random() * 1.6
		local o = P + Vector3.new(math.cos(ang) * r, 0, math.sin(ang) * r)
		local h = not workspace:Raycast(P + Vector3.new(0, 0.6, 0), o - P, rp) and workspace:Raycast(o + Vector3.new(0, 2, 0), Vector3.new(0, -4, 0), rp)
		if h then
			local pl = peca("Placa", corBorda:Lerp(escurecer(corBorda, 0.7), math.random() * 0.5), Enum.Material.Ground)
			pl.Size = Vector3.new(1.2 + math.random() * 1.1, 0.35 + math.random() * 0.25, 1.0 + math.random() * 1.0)
			local fora = Vector3.new(math.cos(ang), 0, math.sin(ang))
			pl.CFrame = CFrame.lookAt(h.Position, h.Position + fora, h.Normal) * CFrame.Angles(math.rad(-(28 + math.random() * 26)), math.rad(math.random() * 40 - 20), 0) + h.Normal * 0.35
			pl.Parent = pasta; table.insert(partes, pl)
		end
	end
	-- pedras: saltam do centro e assentam no chao (so visual, ancoradas, animadas por tween)
	for i = 1, cfg.pedras do
		local ang = math.random() * math.pi * 2; local r = 2 + math.random() * 4.5
		local o = P + Vector3.new(math.cos(ang) * r, 0, math.sin(ang) * r)
		local h = not workspace:Raycast(P + Vector3.new(0, 0.6, 0), o - P, rp) and workspace:Raycast(o + Vector3.new(0, 2, 0), Vector3.new(0, -4, 0), rp)
		if h then
			local s = 0.4 + math.random() * 0.6
			local pd = peca("Pedra", escurecer(corBorda:Lerp(Color3.fromRGB(110, 105, 100), 0.5), 0.6 + math.random() * 0.3), Enum.Material.Slate)
			pd.Size = Vector3.new(s, s * 0.7, s * 1.1); pd.CFrame = CFrame.new(P + N * 0.4) * CFrame.Angles(math.random() * 3, math.random() * 3, 0)
			pd.Parent = pasta; table.insert(partes, pd)
			local topo = (P + h.Position) / 2 + Vector3.new(0, 1.2 + math.random() * 1.8, 0)
			local t1 = 0.18 + math.random() * 0.1
			TS:Create(pd, TweenInfo.new(t1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = CFrame.new(topo) * CFrame.Angles(math.random() * 3, math.random() * 3, 0)}):Play()
			task.delay(t1, function()
				if pd.Parent then TS:Create(pd, TweenInfo.new(t1 * 1.1, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = CFrame.lookAt(h.Position + h.Normal * s * 0.3, h.Position + h.Normal * s * 0.3 + Vector3.new(math.random() - 0.5, 0, math.random() - 0.5), h.Normal)}):Play() end
			end)
		end
	end
	-- poeira: no centro e em pontos ao longo das fendas
	local function poeira(pos, n, atraso)
		task.delay(atraso, function()
			local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain
			local pe = Instance.new("ParticleEmitter"); pe.Texture = "rbxasset://textures/particles/smoke_main.dds"
			pe.Color = ColorSequence.new(base:Lerp(Color3.fromRGB(170, 160, 145), 0.4))
			pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.2), NumberSequenceKeypoint.new(1, 4.5)})
			pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.4), NumberSequenceKeypoint.new(1, 1)})
			pe.Lifetime = NumberRange.new(0.8, 1.6); pe.Speed = NumberRange.new(5, 12); pe.SpreadAngle = Vector2.new(70, 20)
			pe.Drag = 3; pe.EmissionDirection = Enum.NormalId.Top; pe.Rate = 0; pe.Parent = a; pe:Emit(n)
			Debris:AddItem(a, 2.2)
		end)
	end
	poeira(P + N * 0.3, baixa and 14 or 30, 0)
	-- erupcoes: pontos ao longo das fendas (principais primeiro), espalhados; poeira alta + pedras arremessadas
	table.sort(cfg.erup, function(a, b) return a.nivel < b.nivel end)
	local escolhidos = {}
	for _, e in ipairs(cfg.erup) do
		local longe = true
		for _, o in ipairs(escolhidos) do if (o.pos - e.pos).Magnitude < V.espacoErupcao then longe = false; break end end
		if longe then table.insert(escolhidos, e) end
		if #escolhidos >= cfg.erupcoes then break end
	end
	local corPedra = escurecer(corBorda:Lerp(Color3.fromRGB(110, 105, 100), 0.4), 0.75)
	for _, e in ipairs(escolhidos) do
		task.delay(e.t, function()
			if not pasta.Parent then return end
			local a = Instance.new("Attachment"); a.WorldPosition = e.pos + e.n * 0.4; a.Parent = workspace.Terrain
			local pe = Instance.new("ParticleEmitter"); pe.Texture = "rbxasset://textures/particles/smoke_main.dds"
			pe.Color = ColorSequence.new(V.corTerra:Lerp(Color3.fromRGB(175, 160, 140), 0.45))
			pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.6), NumberSequenceKeypoint.new(1, 5.5)})
			pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.25), NumberSequenceKeypoint.new(0.6, 0.6), NumberSequenceKeypoint.new(1, 1)})
			pe.Lifetime = NumberRange.new(1.2, 2.2); pe.Speed = NumberRange.new(6, 11); pe.SpreadAngle = Vector2.new(25, 25)
			pe.Acceleration = Vector3.new(0, -3, 0); pe.Drag = 2; pe.EmissionDirection = Enum.NormalId.Top; pe.Rate = 0; pe.Parent = a
			pe:Emit(baixa and 5 or 10); Debris:AddItem(a, 2.6)
			for j = 1, cfg.pedrasErupcao do
				local ang = math.random() * math.pi * 2; local r = 0.8 + math.random() * 2.2
				local o = e.pos + Vector3.new(math.cos(ang) * r, 0, math.sin(ang) * r)
				local h = not workspace:Raycast(e.pos + Vector3.new(0, 0.6, 0), o - e.pos, rp) and workspace:Raycast(o + Vector3.new(0, 2, 0), Vector3.new(0, -4, 0), rp)
				if h then
					local s = 0.35 + math.random() * 0.45
					local pd = peca("Pedra", corPedra:Lerp(escurecer(corPedra, 0.6), math.random()), Enum.Material.Slate)
					pd.Size = Vector3.new(s, s * 0.75, s * 1.15); pd.CFrame = CFrame.new(e.pos + e.n * 0.3); pd.Parent = pasta; table.insert(partes, pd)
					local alt = V.alturaErupcao[1] + math.random() * (V.alturaErupcao[2] - V.alturaErupcao[1])
					local t1 = 0.22 + math.random() * 0.12
					TS:Create(pd, TweenInfo.new(t1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = CFrame.new((e.pos + h.Position) / 2 + Vector3.new(0, alt, 0)) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)}):Play()
					task.delay(t1, function()
						if pd.Parent then TS:Create(pd, TweenInfo.new(t1 * 1.15, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = CFrame.lookAt(h.Position + h.Normal * s * 0.3, h.Position + h.Normal * s * 0.3 + Vector3.new(math.random() - 0.5, 0, math.random() - 0.5), h.Normal)}):Play() end
					end)
					task.delay(V.duracao - V.sumir - e.t, function() if pd.Parent then TS:Create(pd, TweenInfo.new(V.sumir), {Transparency = 1}):Play() end end)
					Debris:AddItem(pd, V.duracao + 0.1 - e.t)
				end
			end
		end)
	end
	M.ultimasErupcoes = #escolhidos
	for _, p in ipairs(partes) do
		task.delay(V.duracao - V.sumir, function() if p.Parent then TS:Create(p, TweenInfo.new(V.sumir), {Transparency = 1}):Play() end end)
		Debris:AddItem(p, V.duracao + 0.1)
	end
	return #partes, alcance
end
function M.tremor(P)
	local cam = workspace.CurrentCamera; if not cam then return end
	local d = (cam.CFrame.Position - P).Magnitude; if d > M.VIS.tremorAlcance then return end
	local amp = M.VIS.tremorMax * (1 - d / M.VIS.tremorAlcance); local t0 = os.clock()
	local nome = "TremorUrso" .. tostring(t0)
	RS:BindToRenderStep(nome, Enum.RenderPriority.Camera.Value + 2, function()
		local k = (os.clock() - t0) / M.VIS.tremorDur
		if k >= 1 then RS:UnbindFromRenderStep(nome); return end
		local a = amp * (1 - k)
		cam.CFrame = cam.CFrame * CFrame.new(math.noise(k * 20, 1) * a, math.noise(k * 20, 2) * a, 0)
	end)
end
local function som(id, pos)                 -- som 3D no ponto (nao global), alcance limitado
	if not id then return end
	local at = Instance.new("Attachment"); at.WorldPosition = pos; at.Parent = workspace.Terrain
	local s = Instance.new("Sound"); s.SoundId = id; s.RollOffMaxDistance = 120; s.Parent = at; s:Play(); Debris:AddItem(at, 5)
end
function M.iniciar(remotos)
	if M.con then return end
	M.con = remotos.Efeitos.OnClientEvent:Connect(function(d)
		if d.tipo ~= "GolpeColossal" then return end
		if d.fase == "rugido" and d.urso then
			local cab = d.urso:FindFirstChild("Cabeca", true); som(M.SOM_RUGIDO, cab and cab.TransformedWorldCFrame.Position or d.urso:GetPivot().Position)
			M.rugidos = (M.rugidos or 0) + 1
		elseif d.fase == "impacto" and d.pos then
			local n, alc = M.rachaduras(d.pos, d.normal or Vector3.yAxis, d.urso, d.raio)
			M.ultimo = {n = n, alcance = alc, t = os.clock()}
			M.tremor(d.pos); som(M.SOM_IMPACTO, d.pos)
		end
	end)
end
return M
]=====]
local soma = 0; for i = 1, #c.Source do soma = (soma + string.byte(c.Source, i)) % 1000003 end
return "bytes=" .. #c.Source .. " soma=" .. soma
