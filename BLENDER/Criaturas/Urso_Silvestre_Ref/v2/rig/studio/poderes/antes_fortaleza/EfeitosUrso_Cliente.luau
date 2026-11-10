-- EfeitosUrso_Cliente (ModuleScript em ReplicatedStorage.Urso_v2_Lab) - so APRESENTA o que o servidor decidiu.
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
--   O raio de DANO do servidor passou a 38 a partir do CENTRO do corpo (pedido do usuario) e o visual acompanha.
--   04/11: "aumente 2x mais o alcance" -> raio 76 (~66 studs de fendas a partir do contorno).
--   Medido 04/11: Debris guarda no maximo ~1000 itens e APAGA os mais antigos -> com ~2300 pecas so 967 apareciam
--   (um lado sem fendas). Pecas agora saem por task.delay proprio (Debris so para os poucos Attachments) e o total
--   caiu (menos ramificacoes, segmentos maiores longe, fendas do corpo sem ramo de 2o nivel).
-- Som: NENHUM audio do urso existe no projeto (M0 04/11) -> ganchos SOM_RUGIDO / SOM_IMPACTO vazios, a preencher.
local RS = game:GetService("RunService")
local TS = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local M = {}
M.VIS = {                -- LABORATORIO (visual)
	alcance = 0.87,              -- fracao do raio do golpe, a partir do contorno do corpo (raio 38 -> ~33 studs)
	fendasCorpo = 14, contorno = {3.8, 7.2},   -- fendas saindo do contorno do corpo (semi-eixos lateral, longitudinal)
	passoLonge = 0.10,           -- o passo cresce 0,10 stud por stud de distancia (alcance 2x: menos pecas longe)
	fendas = 6, ramificar = 0.16, passo = 0.85, desvio = 0.38,
	largura0 = 0.95, larguraPonta = 0.10, espessura = 0.05,
	velocidade = 45,             -- studs/s de crescimento
	placas = 9, pedras = 14,
	levante = 0.8, levanteCapim = 2.4, levanteMin = 0.35, corTerra = Color3.fromRGB(96, 74, 52),   -- bordas levantadas (studs)
	materiaisCapim = {Grass = true, LeafyGrass = true},   -- chao com capim alto do terreno (cobre ~2 studs, medido 04/11)
	duracao = 6.0, sumir = 1.5,
	tremorMax = 0.35, tremorDur = 0.55, tremorAlcance = 160,
	erupcoes = 44, pedrasErupcao = 3, alturaErupcao = {2.5, 4.5}, espacoErupcao = 5.5,
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
		if nivel < 1 and s > 1 and k < 0.8 and math.random() < cfg.ramificar then
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
					task.delay(V.duracao + 0.1 - e.t, function() pd:Destroy() end)
				end
			end
		end)
	end
	M.ultimasErupcoes = #escolhidos
	for _, p in ipairs(partes) do
		task.delay(V.duracao - V.sumir, function() if p.Parent then TS:Create(p, TweenInfo.new(V.sumir), {Transparency = 1}):Play() end end)
		task.delay(V.duracao + 0.1, function() p:Destroy() end)          -- nao usar Debris (limite de ~1000 itens)
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
-- ================================================================== Carga Selvagem (Etapa 3, 04/11) - visual + queda local
-- So apresentacao: o servidor ja decidiu trajeto, impacto, queda e prazos. Aqui:
--   * CORRIDA: poeira/terra (cor do chao) levantando atras das patas enquanto a carga dura;
--   * IMPACTO: estouro de poeira e pedrinhas no ponto + tremor curto da camera de quem esta perto;
--   * PAREDE: estouro de poeira no ponto da batida;
--   * ATORDOADO: estrelinhas girando sobre a cabeca do derrubado enquanto dura (todos veem);
--   * QUEDA (so no cliente do jogador derrubado, dono da fisica do proprio personagem): PlatformStand + giro do tombo;
--     no "levantar" sai do PlatformStand e entra em GettingUp. Se este cliente falhar, o SERVIDOR libera no prazo.
M.SOM_CARGA_IMPACTO = nil        -- rbxassetid quando existir (PENDENTE)
M.SOM_CARGA_ARRANCADA = nil      -- idem (PENDENTE)
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
function M.iniciar(remotos)
	if M.con then return end
	M.con = remotos.Efeitos.OnClientEvent:Connect(function(d)
		if d.tipo == "RugidoProtetor" then M.rugidoProtetorEfx(d); return end
		if d.tipo == "CargaSelvagem" or d.tipo == "Atordoado" or d.tipo == "Queda" then M.cargaEfx(d); return end
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
