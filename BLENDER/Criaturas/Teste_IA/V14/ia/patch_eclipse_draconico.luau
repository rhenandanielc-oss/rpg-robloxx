-- patch_eclipse_draconico.luau (Studio, Edit) — Eclipse Draconico do Dragao Sombrio (3a ativa da Sombra, 04/11).
-- Gerado por sombrio/gerar_patch_eclipse.py com as MESMAS trocas do src/. Tudo-ou-nada (scripts checados antes de
-- trocar); backup unico ServerStorage.Backup_Eclipse_Draconico_2026-11-04. Atualiza VFXSombra; cria 2 clipes.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local RS, SS = game:GetService("ReplicatedStorage"), game:GetService("ServerStorage")
local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end
local novos = {}
do local s = game.ServerScriptService.Combate_Dragao.ConfigCombate; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_ECLIPSE_DRACONICO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[		Sombrio = {"Sopro", "Arremetida"}},                       -- PATCH_SOPRO_UMBRAL / PATCH_CORRENTES_NOITE (04/11): Sombrio = Sopro Umbral + Correntes]==], [==[		Sombrio = {"Sopro", "Arremetida", "Coracao"}},            -- PATCH_SOPRO_UMBRAL / CORRENTES_NOITE / ECLIPSE_DRACONICO (04/11): kit completo do Sombrio]==])
  src = troca(src, [==[		Sombrio = {Sopro = "SoproUmbral", Arremetida = "Correntes"}},]==], [==[		Sombrio = {Sopro = "SoproUmbral", Arremetida = "Correntes", Coracao = "Eclipse"}},]==])
  src = troca(src, [==[		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) =====]==], [==[		-- Eclipse Draconico (PATCH_ECLIPSE_DRACONICO): especial; concentracao -> rugido; no pico (boca aberta, ~2,15 s) a area
		-- escurece (so visual) e DETONA as Marcas Sombrias proprias dos alvos na esfera: danoPorMarca x marcas (sem marca = 0).
		-- escuro = s de escurecimento depois da detonacao. NAO_APROVADO
		Eclipse = {recarga = 25, energia = 50, elemental = true, intensidade = "pesado", clipe = "Eclipse_Draconico",
			detona = 2.15, duracao = 3.7, raio = 60, danoPorMarca = 9, escuro = 4.0},
		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) =====]==])
  assert(loadstring(src), "ConfigCombate.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Combate_Dragao.Nucleo; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_ECLIPSE_DRACONICO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[
-- energia
task.spawn(function()]==], [==[
-- PATCH_ECLIPSE_DRACONICO (04/11): Eclipse Draconico (Sombrio, slot Coracao, especial). Concentracao (inicio do
-- Hab_Concentracao) -> Rugido_Combate; no pico do rugido a area em volta do corpo escurece (so visual, no cliente) e as
-- Marcas Sombrias PROPRIAS dos alvos na esfera (com linha de visao) DETONAM: o alvo perde todas as marcas deste Sombrio
-- e recebe danoPorMarca x marcas (sem marca = sem dano; a detonacao nao cria marca nova). Sem invisibilidade,
-- invulnerabilidade nem execucao. Contrajogo: sair da area na antecipacao / nao acumular marcas. Numeros NAO_APROVADO.
function N:_Eclipse(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "inicio", el = el, noAr = noAr, detona = def.detona, raio = def.raio})
	self:tocar(def.clipe, noAr, {}, function() end)
	task.wait(def.detona)
	if not m.Parent or m:GetAttribute("Incapacitado") then FX:FireAllClients({d = m, hab = "Eclipse", fase = "fim", el = el}); return end
	local c = self:centroCorpo()
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "detonar", el = el, pos = c, raio = def.raio, duracao = def.escuro})
	local mult = ((m:GetAttribute("DominioAtivo") and Cfg.habilidades.Dominio.multiplicadorDano) or 1) * Passivas.multiplicadorOfensivo(m)
	local total, nAlvos = 0, 0
	for _, a in ipairs(self:alvosValidos()) do
		if naEsfera(c, def.raio, a) and self:visivel(c, a) then
			local n = Passivas.consumirMarcas(m, a)                         -- zera ANTES do dano: o multiplicador da Marca nao soma
			if n > 0 and N.ferir(m, a, def.danoPorMarca * n * mult, el, "Eclipse", def.intensidade, true) then   -- como tick: nao marca de novo
				FX:FireAllClients({d = m, fase = "reacao", alvo = a, intensidade = def.intensidade, el = el, tipo = "Eclipse"})
				FX:FireAllClients({d = m, hab = "Eclipse", fase = "marca", el = el, alvo = a, marcas = n})
				total += n; nAlvos += 1
			end
		end
	end
	m:SetAttribute("UltimoEclipse", ("alvos=%d marcas=%d raio=%d"):format(nAlvos, total, def.raio))
	local resto = def.duracao - def.detona
	if resto > 0 then task.wait(resto) end
end

-- energia
task.spawn(function()]==])
  assert(loadstring(src), "Nucleo.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Combate_Dragao.Passivas; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_ECLIPSE_DRACONICO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[function P.consumirMarcas(fonte, alvo)                              -- (Eclipse Draconico, futuro): devolve quantas havia
	local n = P.marcasDe(fonte, alvo); if n > 0 then marcas[alvo][fonte] = nil; atribMarca(alvo) end; return n
end]==], [==[function P.consumirMarcas(fonte, alvo)                              -- Eclipse Draconico: zera as marcas desta origem; devolve quantas havia
	local n = P.marcasDe(fonte, alvo)
	if n > 0 then marcas[alvo][fonte] = nil; alvo:SetAttribute("MarcaSombria_" .. fonte.Name, nil); atribMarca(alvo) end   -- PATCH_ECLIPSE_DRACONICO: limpa o atributo da origem
	return n
end]==])
  assert(loadstring(src), "Passivas.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Montaria_Dragao_Servidor; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_ECLIPSE_DRACONICO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[		or ataque == "Correntes"                                                            -- PATCH_CORRENTES_NOITE (Sombrio)]==], [==[		or ataque == "Correntes"                                                            -- PATCH_CORRENTES_NOITE (Sombrio)
		or ataque == "Eclipse"                                                              -- PATCH_ECLIPSE_DRACONICO (Sombrio)]==])
  assert(loadstring(src), "Montaria_Dragao_Servidor.server.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ReplicatedStorage.Montaria_Dragoes.ConfigMontaria; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_ECLIPSE_DRACONICO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[			Sombrio = {Sopro = "Sopro Umbral", Arremetida = "Correntes"}},]==], [==[			Sombrio = {Sopro = "Sopro Umbral", Arremetida = "Correntes", Coracao = "Eclipse"}},   -- PATCH_ECLIPSE_DRACONICO]==])
  src = troca(src, [==[			Sombrio = " | segure 1: Sopro Umbral | 2 Correntes da Noite (mire no chao)"},]==], [==[			Sombrio = " | segure 1: Sopro Umbral | 2 Correntes da Noite (mire no chao) | 4 Eclipse Dracônico"},]==])
  assert(loadstring(src), "ConfigMontaria.luau nao compila"); table.insert(novos, {s, src}) end
local vfx = [=====[
-- VFXSombra (ModuleScript, ReplicatedStorage.Combate_Dragoes) — efeitos COSMETICOS da Sombra (kit do Dragao Sombrio,
-- definido pelo usuario em 03/11), so no cliente. Chamado pelo VFXCombate para todo evento com el = "Sombra";
-- evento() devolve true quando tratou o evento (o resto segue no perfil Neutro do VFXCombate).
-- Sopro Umbral (04/11; v2 visual 04/11): jato continuo de nevoa negra-violeta + vinheta LEVE na tela do jogador atingido (so visual,
-- curta, sem cegar). Desempenho: sem luz dinamica, taxas limitadas e escaladas pelo fator de LOD recebido.
-- Valores artisticos NAO_APROVADO (prototipo para revisao do usuario).
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local S = {}

local C3 = Color3.fromRGB
local PRETO, BREU, VIOLETA, VIOLETA_CLARO = C3(6, 0, 12), C3(28, 6, 45), C3(120, 40, 200), C3(175, 95, 255)
local TEX = {fumaca = "rbxasset://textures/particles/smoke_main.dds", faisca = "rbxasset://textures/particles/sparkles_main.dds",
	-- texturas neutras (brancas) ja enviadas para o Gelo; aqui so recebem cor
	nevoa = "rbxassetid://105424368956403", jato_h = "rbxassetid://114995351681928"}
local VINHETA = {pico = 0.55, segura = 0.25, some = 0.6, largura = 0.2}   -- transparencia minima, s, s, fracao da tela

local function seq(cs) local k = {}; for i, c in ipairs(cs) do table.insert(k, ColorSequenceKeypoint.new((i - 1) / (#cs - 1), c)) end; return ColorSequence.new(k) end
local function ns(...) local a = {...}; local k = {}; for i = 1, #a, 2 do table.insert(k, NumberSequenceKeypoint.new(a[i], a[i + 1])) end; return NumberSequence.new(k) end
local function ancora(pos) local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain; return a end
local function emissor(pai, t) local e = Instance.new("ParticleEmitter"); for k, v in pairs(t) do e[k] = v end; e.Parent = pai; return e end
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end
local cacheOsso = {}
local function ossoC(m, nome)
	cacheOsso[m] = cacheOsso[m] or {}
	local b = cacheOsso[m][nome]; if b and b.Parent then return b end
	b = osso(m, nome); cacheOsso[m][nome] = b; return b
end
local function raizDe(m) return m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart end
local function boca(m)
	local cab, tip = ossoC(m, "Cabeca"), ossoC(m, "mouth_upper_tip")
	if cab and tip then
		local p = tip.TransformedWorldCFrame.Position; local d = p - cab.TransformedWorldCFrame.Position
		return p, d.Magnitude > 0.1 and d.Unit or m:GetPivot().LookVector
	end
	return m:GetPivot().Position + Vector3.new(0, 20, 0), m:GetPivot().LookVector
end
local function pastaFX()
	local f = workspace:FindFirstChild("VFX_Temporarios")
	if not f then f = Instance.new("Folder"); f.Name = "VFX_Temporarios"; f.Parent = workspace end
	return f
end
local function peca(props, pai)
	local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	for k, v in pairs(props) do p[k] = v end; p.Parent = pai or pastaFX(); return p
end

-- ===== vinheta leve (so o jogador atingido pelo Sopro Umbral) ======================================================
-- 4 faixas nas bordas com gradiente para dentro; nada no centro da tela. Cada acerto renova; sem acertos, some.
local vin
local function vinheta()
	local lp = Players.LocalPlayer; if not lp then return end
	if not (vin and vin.gui.Parent) then
		local g = Instance.new("ScreenGui"); g.Name = "VinhetaSombra"; g.IgnoreGuiInset = true; g.ResetOnSpawn = false; g.DisplayOrder = 5
		local faixas = {}
		for _, lado in ipairs({{0, 0, 1, VINHETA.largura, 90}, {0, 1 - VINHETA.largura, 1, VINHETA.largura, -90}, {0, 0, VINHETA.largura, 1, 0}, {1 - VINHETA.largura, 0, VINHETA.largura, 1, 180}}) do
			local fr = Instance.new("Frame"); fr.BorderSizePixel = 0; fr.BackgroundColor3 = BREU; fr.BackgroundTransparency = 1
			fr.Position = UDim2.fromScale(lado[1], lado[2]); fr.Size = UDim2.fromScale(lado[3], lado[4])
			local gr = Instance.new("UIGradient"); gr.Rotation = lado[5]; gr.Transparency = ns(0, 0, 1, 1)
			gr.Color = seq({PRETO, VIOLETA}); gr.Parent = fr
			fr.Parent = g; table.insert(faixas, fr)
		end
		g.Parent = lp:WaitForChild("PlayerGui")
		vin = {gui = g, faixas = faixas, ate = 0}
	end
	vin.ate = os.clock() + VINHETA.segura
	if vin.con then return end
	vin.con = RunService.RenderStepped:Connect(function()
		local resto = os.clock() - vin.ate                                 -- < 0: segurando; 0..some: sumindo
		local k = resto <= 0 and 0 or math.min(1, resto / VINHETA.some)
		local tr = VINHETA.pico + (1 - VINHETA.pico) * k
		for _, fr in ipairs(vin.faixas) do fr.BackgroundTransparency = tr end
		if k >= 1 then vin.con:Disconnect(); vin.con = nil end
	end)
end

-- ===== reacao ao acerto de Sombra =================================================================================
local function reacao(d, f)
	local a = d.alvo; if not (a and a.Parent) then return end
	local h = Instance.new("Highlight"); h.FillColor = VIOLETA; h.OutlineColor = PRETO; h.OutlineTransparency = 0.6
	h.FillTransparency = d.intensidade == "pesado" and 0.35 or d.intensidade == "moderado" and 0.5 or 0.7; h.Parent = a
	TweenService:Create(h, TweenInfo.new(0.35), {FillTransparency = 1, OutlineTransparency = 1}):Play(); Debris:AddItem(h, 0.4)
	local r = raizDe(a)
	if r and f > 0 then
		local a2 = ancora(r.Position); Debris:AddItem(a2, 1.2)
		emissor(a2, {Texture = TEX.fumaca, Color = seq({VIOLETA, BREU}), LightEmission = 0.2, LightInfluence = 0.6, Size = ns(0, 1, 1, 3),
			Transparency = ns(0, 0.5, 1, 1), Lifetime = NumberRange.new(0.4, 0.7), Speed = NumberRange.new(3, 8), SpreadAngle = Vector2.new(180, 180), Rate = 0}):Emit(math.max(1, math.floor(5 * f)))
	end
	local lp = Players.LocalPlayer
	if lp and lp.Character == a then                                   -- so quem foi atingido: tremor curto (igual ao generico)
		if d.tipo == "Sopro" then vinheta() end
		local amp = d.intensidade == "pesado" and 0.35 or d.intensidade == "moderado" and 0.2 or 0.1
		local cam = workspace.CurrentCamera; local t0 = os.clock()
		local c; c = RunService.RenderStepped:Connect(function()
			local k = 1 - (os.clock() - t0) / 0.25; if k <= 0 then c:Disconnect(); return end
			cam.CFrame *= CFrame.new((math.random() - 0.5) * amp * k, (math.random() - 0.5) * amp * k, 0)
		end)
	end
end

-- ===== SOPRO UMBRAL v2 (revisao visual 04/11): fluxo volumetrico de breu ==========================================
-- Sem feixes (liam como tubo/laser). Camadas: garganta densa e pequena na boca -> nucleo de breu (flipbook proprio de
-- fumaca turbulenta, recolorido) que cresce e desacelera -> turbilhoes lentos e largos que sobem e se desfazem;
-- violeta so na borda (nevoa atras do nucleo) e fiapos finos dando a direcao; sem centelhas. Origem entre as pontas
-- da boca; direcao da cabeca puxada para a mira no maximo BOCA_MAX. Paredes/chao: a vida das particulas encurta ate o
-- contato (nao atravessa) e ali sai uma nuvem baixa; personagens nao param o jato (o cone do servidor os atravessa).
-- Abre crescendo (0,3 s); ao fim a emissao para e o que esta no ar se dissipa. 175 particulas/s no fator 1, ~140 vivas
-- (a garganta, 80/s, vive 0,3 s; v1: 150/s, ~155 vivas).
local FB_FUMACA = "rbxassetid://114973539727313"                   -- V14/vfx/gerar_flipbooks.py (cinza neutro, 8x8)
local BOCA_MAX, ABRE = math.rad(35), 0.3
local sopro = {}
local function velPara(alc, frac, drag, vida) local d = alc * frac; if drag <= 0.01 then return d / vida end; return d * drag / (1 - math.exp(-drag * vida)) end
local function vidaAte(D, v0, k, vida)                                -- tempo para a particula percorrer D (arrasto k)
	if k <= 0.01 then return math.min(vida, D / v0) end
	local x = D * k / v0; if x >= 1 then return vida end
	return math.min(vida, -math.log(1 - x) / k)
end
local function bocaJato(m)
	local cab, up, lo = ossoC(m, "Cabeca"), ossoC(m, "mouth_upper_tip"), ossoC(m, "mouth_lower_tip")
	if cab and up then
		local pu = up.TransformedWorldCFrame.Position
		local d = pu - cab.TransformedWorldCFrame.Position; d = d.Magnitude > 0.1 and d.Unit or m:GetPivot().LookVector
		local p = lo and (pu + lo.TransformedWorldCFrame.Position) / 2 or pu
		return p + d * 0.3, d
	end
	return boca(m)
end
local function limitar(d, alvo, max)                                  -- gira d para alvo, no maximo `max` rad
	local ang = math.acos(math.clamp(d:Dot(alvo), -1, 1)); if ang <= max then return alvo end
	local ax = d:Cross(alvo); if ax.Magnitude < 1e-4 then return d end
	return CFrame.fromAxisAngle(ax.Unit, max) * d
end
local function raioSolido(o, v, m)                                    -- terreno/paredes; personagens nao bloqueiam
	local ign = {m, pastaFX()}; local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
	for _ = 1, 3 do
		rp.FilterDescendantsInstances = ign
		local h = workspace:Raycast(o, v, rp); if not h then return nil end
		local mdl = h.Instance:FindFirstAncestorOfClass("Model")
		if mdl and mdl:FindFirstChildOfClass("Humanoid") then table.insert(ign, mdl) else return h end
	end
end
local function flipFumaca(t) t.Texture = FB_FUMACA; t.FlipbookLayout = Enum.ParticleFlipbookLayout.Grid8x8; t.FlipbookMode = Enum.ParticleFlipbookMode.OneShot; return t end
-- {fracao do alcance, arrasto, vida, taxa, variacao de velocidade}
local PERF = {garganta = {0.25, 2.5, 0.3, 80, 0.85}, nucleo = {0.95, 1.6, 1.25, 55, 0.78}, turbilhao = {0.8, 2.4, 1.6, 12, 0.6},
	borda = {0.9, 1.4, 1.2, 12, 0.8}, fiapos = {1.0, 1.2, 0.8, 16, 0.85}}
local function limparSopro(m)
	local s = sopro[m]; if not s then return end
	sopro[m] = nil; if s.con then s.con:Disconnect() end
	s.anc:Destroy(); s.imp:Destroy()
end
local function emissoresSopro(m)
	local s = sopro[m]; if s and s.anc.Parent then return s end
	s = {anc = ancora(m:GetPivot().Position), imp = ancora(m:GetPivot().Position), e = {}, vel = {}, f = 1}; sopro[m] = s
	local F = Enum.NormalId.Front
	-- garganta: curta e densa, levemente alongada no sentido do jato (Squash) para nao abrir buracos entre particulas
	-- rapidas; textura macia (o flipbook esticado virava lascas afiadas na boca)
	s.e.garganta = emissor(s.anc, {Texture = TEX.fumaca, Color = seq({PRETO, BREU}), LightEmission = 0, LightInfluence = 0.3,
		Orientation = Enum.ParticleOrientation.VelocityParallel, Squash = ns(0, 0.8, 1, 0),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.9, 0.2), NumberSequenceKeypoint.new(1, 3, 0.6)}),
		Transparency = ns(0, 0.55, 0.2, 0.3, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-50, 50),
		SpreadAngle = Vector2.new(4, 4), EmissionDirection = F, Rate = 0, ZOffset = 1.5})
	s.e.nucleo = emissor(s.anc, flipFumaca({Color = seq({PRETO, BREU, C3(38, 12, 58)}), LightEmission = 0, LightInfluence = 0.35,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.4, 0.3), NumberSequenceKeypoint.new(0.06, 3, 0.6), NumberSequenceKeypoint.new(0.3, 5.5, 1.2), NumberSequenceKeypoint.new(0.65, 8.5, 2), NumberSequenceKeypoint.new(1, 10.5, 2.5)}),
		Transparency = ns(0, 0.6, 0.08, 0.3, 0.5, 0.45, 0.85, 0.75, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-45, 45),
		Acceleration = Vector3.new(0, 1.2, 0), SpreadAngle = Vector2.new(6, 6), EmissionDirection = F, Rate = 0, ZOffset = 1}))
	s.e.turbilhao = emissor(s.anc, flipFumaca({Color = seq({BREU, C3(18, 6, 28)}), LightEmission = 0, LightInfluence = 0.4,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.4, 0.4), NumberSequenceKeypoint.new(1, 13, 3)}),
		Transparency = ns(0, 0.85, 0.3, 0.55, 0.75, 0.75, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-90, 90),
		Acceleration = Vector3.new(0, 2.2, 0), SpreadAngle = Vector2.new(16, 16), EmissionDirection = F, Rate = 0}))
	s.e.borda = emissor(s.anc, {Texture = TEX.nevoa, Color = seq({C3(95, 35, 160), C3(45, 15, 80)}), LightEmission = 0.25, LightInfluence = 0.5,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.2, 0.3), NumberSequenceKeypoint.new(1, 12, 2.5)}),
		Transparency = ns(0, 0.92, 0.35, 0.74, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30),
		SpreadAngle = Vector2.new(11, 11), EmissionDirection = F, Rate = 0, ZOffset = -1})
	s.e.fiapos = emissor(s.anc, {Texture = TEX.fumaca, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = ColorSequence.new(PRETO),
		LightEmission = 0, LightInfluence = 0.3, Size = ns(0, 0.25, 1, 0.75), Transparency = ns(0, 0.6, 0.4, 0.45, 1, 1),
		SpreadAngle = Vector2.new(9, 9), EmissionDirection = F, Rate = 0, ZOffset = 2})
	s.eImp = emissor(s.imp, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.5,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 3, 0.8), NumberSequenceKeypoint.new(1, 12, 3)}), Transparency = ns(0, 0.75, 0.3, 0.6, 1, 1),
		Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(5, 11), Drag = 2.5, Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-40, 40),
		SpreadAngle = Vector2.new(80, 80), EmissionDirection = F, Rate = 0}))
	return s
end
local function ligarSopro(m, ligado, f, alvo, alcance)
	local s = emissoresSopro(m); s.alvo = alvo
	if ligado then
		s.ligado, s.t0, s.f, s.prox = true, os.clock(), f, 0
		s.alc = alcance or 95; local alc = s.alc
		for k, e in pairs(s.e) do
			local p = PERF[k]; local v = velPara(alc, p[1], p[2], p[3]); s.vel[k] = v
			e.Drag = p[2]; e.Lifetime = NumberRange.new(p[3] * 0.85, p[3]); e.Speed = NumberRange.new(v * p[5], v * 1.04)
		end
		if s.con then return end
		s.con = RunService.RenderStepped:Connect(function()
			if not m.Parent then limparSopro(m); return end
			local b, d = bocaJato(m)
			if s.alvo then local v = s.alvo - b; if v.Magnitude > 5 then d = limitar(d, v.Unit, BOCA_MAX) end end
			s.anc.WorldCFrame = CFrame.lookAt(b, b + d)
			local agora = os.clock()
			if s.ligado then local k = math.min(1, (agora - s.t0) / ABRE); for n, e in pairs(s.e) do e.Rate = PERF[n][4] * s.f * (0.3 + 0.7 * k) end end
			if agora < s.prox then return end
			s.prox = agora + 0.1                                       -- contato: 10x/s basta
			local h = raioSolido(b, d * s.alc, m)
			local D = h and (h.Position - b).Magnitude or s.alc
			for n, e in pairs(s.e) do local p = PERF[n]; local t = vidaAte(D * 1.12, s.vel[n] * 1.04, p[2], p[3]); e.Lifetime = NumberRange.new(t * 0.85, t) end
			if h and s.ligado then
				local r = d - 2 * d:Dot(h.Normal) * h.Normal                   -- espalha rente a superficie, no sentido do jato
				local p = h.Position - d * 2 + h.Normal * 0.6                 -- um pouco antes do contato: emenda com o jato
				s.imp.WorldCFrame = CFrame.lookAt(p, p + (h.Normal + r * 0.6).Unit); s.eImp.Rate = 10 * s.f
			else s.eImp.Rate = 0 end
		end)
	else
		s.ligado = false; for _, e in pairs(s.e) do e.Rate = 0 end; s.eImp.Rate = 0
		task.delay(1.8, function() if s.con and not s.ligado then s.con:Disconnect(); s.con = nil end end)
	end
end
local function soproEvento(m, d, f)
	if d.fase == "preparo" then                                       -- breu puxado para a boca: nasce numa casca e converge
		local b = bocaJato(m)
		local casca = peca({Shape = Enum.PartType.Ball, Size = Vector3.new(9, 9, 9), Transparency = 1, CFrame = CFrame.new(b)}); Debris:AddItem(casca, 1.6)
		local e = emissor(casca, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.5, Size = ns(0, 1.6, 1, 0.3),
			Transparency = ns(0, 1, 0.25, 0.55, 0.8, 0.5, 1, 1), Lifetime = NumberRange.new(0.4, 0.5), Speed = NumberRange.new(8, 11), Rate = 36 * f,
			Shape = Enum.ParticleEmitterShape.Sphere, ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface}))
		local c; c = RunService.Heartbeat:Connect(function() if not casca.Parent or not m.Parent then c:Disconnect(); return end; casca.CFrame = CFrame.new((bocaJato(m))) end)
		task.delay(1.0, function() if e.Parent then e.Rate = 0 end end)
	elseif d.fase == "emissao" then
		ligarSopro(m, true, f, d.alvoPos, d.alcance)
	elseif d.fase == "mira" then local s = emissoresSopro(m); s.alvo = d.alvoPos
	elseif d.fase == "fim" then
		ligarSopro(m, false, f)
		local b, dr = bocaJato(m); local a = ancora(b); a.WorldCFrame = CFrame.lookAt(b, b + dr); Debris:AddItem(a, 2.2)
		local e = emissor(a, flipFumaca({Color = seq({PRETO, BREU}), LightEmission = 0, LightInfluence = 0.5, Size = ns(0, 0.8, 1, 4.5),
			Transparency = ns(0, 0.6, 0.3, 0.45, 1, 1), Lifetime = NumberRange.new(1.0, 1.6), Speed = NumberRange.new(1.5, 4), Drag = 1,
			Acceleration = Vector3.new(0, 1.4, 0), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30),
			SpreadAngle = Vector2.new(30, 30), EmissionDirection = Enum.NormalId.Front, Rate = 10 * f}))   -- resto saindo da boca
		task.delay(0.4, function() if e.Parent then e.Rate = 0 end end)
	end
end

-- ===== CORRENTES DA NOITE v4 (revisao visual 04/11): elos encaixados que saem do chao e contem o alvo ===============
-- Elo = anel alongado COM FURO (UnionOperation Combate_Dragoes.Elo_Sombra, feita por sombrio/criar_elo_sombra.luau;
-- sem ela, 4 barras), alternando 90 graus e encaixado no vizinho (passo = comprimento - 2 fios: a ponta de um elo
-- passa pelo furo do outro). Por alvo: NCORR correntes saem de pontos REAIS do chao em volta (raycast; sem chao, a
-- corrente nao aparece), empurradas para fora da terra ate um anel que FECHA em volta do corpo (bracos e tronco) a
-- partir dos pontos de chegada e da um tranco amortecido; presas, ficam esticadas com vibracao amortecida e tremor
-- minimo e seguem o alvo (se ele se afasta, mais elos saem do chao; nenhum elo estica). Soltar: o anel afrouxa e cai e
-- as correntes recolhem para o chao em T_SOLTA s; tudo e destruido no fim. Acabamento: Metal quase preto (reflexo
-- discreto) + Highlight violeta so no contorno (le em grafico baixo). Orcamento por alvo (servidor prende ate 3):
-- ate NCORR x MAX_BASE + MAX_ANEL = 45 elos, 1 Highlight, 1 Heartbeat (BulkMoveTo); sem colisao/consulta/sombra/luz.
local ELO = {comp = 1.1, larg = 0.6, fio = 0.17}                      -- studs (escala 1 = R15 de ~5,5 de altura)
local NCORR, MAX_BASE, MAX_ANEL, R_BASE = 3, 9, 18, 4.0
local T_SOBE, T_FECHA, T_SOLTA = 0.28, 0.22, 0.35
local COR_ELO = C3(20, 13, 28)
local correntes = {}                                                 -- [alvo] = {modelo, cad, anel, con, ...}
local function novoElo(esc, pai)                                     -- {{parte, deslocamento}}; eixo longo = Y, plano XY
	local t = script.Parent:FindFirstChild("Elo_Sombra")
	if t then
		local p = t:Clone(); p.Size = t.Size * esc; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
		p.CastShadow = false; p.Transparency = 1; p.CFrame = CFrame.new(0, -500, 0); p.Parent = pai; return {{p, CFrame.identity}}
	end
	local L, W, F = ELO.comp * esc, ELO.larg * esc, ELO.fio * esc; local r = {}
	for _, sx in ipairs({-1, 1}) do table.insert(r, {peca({Size = Vector3.new(F, L, F), Color = COR_ELO, Material = Enum.Material.Metal, Transparency = 1, CFrame = CFrame.new(0, -500, 0)}, pai), CFrame.new(sx * (W - F) / 2, 0, 0)}) end
	for _, sy in ipairs({-1, 1}) do table.insert(r, {peca({Size = Vector3.new(W - 2 * F, F, F), Color = COR_ELO, Material = Enum.Material.Metal, Transparency = 1, CFrame = CFrame.new(0, -500, 0)}, pai), CFrame.new(0, sy * (L - F) / 2, 0)}) end
	return r
end
local function cfElo(pos, dir, giro)                                 -- eixo longo do elo ao longo de dir, girado `giro` nele
	local up = math.abs(dir.Y) > 0.97 and Vector3.xAxis or Vector3.yAxis
	return CFrame.lookAt(pos, pos + dir, up) * CFrame.Angles(math.rad(90), 0, 0) * CFrame.Angles(0, giro, 0)
end
local function cfChao(pos, n)                                        -- cilindro deitado no chao (eixo X = normal)
	local r = n:Cross(Vector3.zAxis); if r.Magnitude < 0.1 then r = n:Cross(Vector3.xAxis) end
	return CFrame.fromMatrix(pos, n, r.Unit)
end
local function normalChao(pos, ign)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = ign
	local h = workspace:Raycast(pos + Vector3.new(0, 3, 0), Vector3.new(0, -8, 0), rp); return h and h.Normal or Vector3.yAxis
end
local function aviso(d, f)
	local r = d.raio or 16; local dur = d.duracao or 0.5
	local n = normalChao(d.pos, {pastaFX(), d.d})
	local disco = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.15, r * 0.6, r * 0.6), Color = VIOLETA, Material = Enum.Material.SmoothPlastic, Transparency = 0.8,
		CFrame = cfChao(d.pos + n * 0.12, n)})
	local miolo = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.18, r * 0.4, r * 0.4), Color = PRETO, Material = Enum.Material.SmoothPlastic, Transparency = 0.5,
		CFrame = cfChao(d.pos + n * 0.14, n)})
	TweenService:Create(disco, TweenInfo.new(dur), {Size = Vector3.new(0.15, r * 2, r * 2), Transparency = 0.55}):Play()
	TweenService:Create(miolo, TweenInfo.new(dur), {Size = Vector3.new(0.18, r * 1.5, r * 1.5)}):Play()
	task.delay(dur, function()
		TweenService:Create(disco, TweenInfo.new(0.4), {Transparency = 1}):Play(); TweenService:Create(miolo, TweenInfo.new(0.4), {Transparency = 1}):Play()
	end)
	Debris:AddItem(disco, dur + 0.5); Debris:AddItem(miolo, dur + 0.5)
	if f > 0 then
		local a = ancora(d.pos + n * 0.5); Debris:AddItem(a, dur + 1)
		local e = emissor(a, {Texture = TEX.fumaca, Color = seq({VIOLETA, PRETO}), LightEmission = 0.1, LightInfluence = 0.6, Size = ns(0, 1.5, 1, 3),
			Transparency = ns(0, 0.55, 1, 1), Lifetime = NumberRange.new(0.5, 0.8), Speed = NumberRange.new(r * 0.6, r * 1.2), Drag = 3,
			SpreadAngle = Vector2.new(180, 10), EmissionDirection = Enum.NormalId.Top, Rate = 20 * f})
		task.delay(dur, function() if e.Parent then e.Rate = 0 end end)
	end
end
local function erupcao(d, f)
	if f <= 0 then return end
	local a = ancora(d.pos + Vector3.new(0, 1, 0)); Debris:AddItem(a, 2)
	emissor(a, {Texture = TEX.nevoa, Color = seq({PRETO, BREU, VIOLETA}), LightEmission = 0.1, LightInfluence = 0.6, Size = ns(0, 2, 1, 6),
		Transparency = ns(0, 0.55, 1, 1), Lifetime = NumberRange.new(0.6, 0.9), Speed = NumberRange.new(5, 11), SpreadAngle = Vector2.new(60, 60),
		Rotation = NumberRange.new(0, 360), Acceleration = Vector3.new(0, 3, 0), EmissionDirection = Enum.NormalId.Top, Rate = 0}):Emit(math.max(2, math.floor(12 * f)))
end
local function poeiraBase(pos, n, f, qtd)
	local a = ancora(pos + n * 0.3); Debris:AddItem(a, 1.6)
	emissor(a, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.6, Size = ns(0, 0.8, 1, 2.6), Transparency = ns(0, 0.5, 1, 1),
		Lifetime = NumberRange.new(0.6, 1.0), Speed = NumberRange.new(1.5, 4), Drag = 2, SpreadAngle = Vector2.new(70, 70), Rotation = NumberRange.new(0, 360),
		EmissionDirection = Enum.NormalId.Top, Rate = 0})):Emit(math.max(1, math.floor(qtd * f)))
end
local function destruirCorrentes(c, devagar)
	if c.con then c.con:Disconnect(); c.con = nil end
	c.modelo:Destroy()
	for _, x in ipairs(c.extras) do if devagar then Debris:AddItem(x, 1.2) else x:Destroy() end end
end
local function soltarCorrentes(alvo, rapido)
	local c = correntes[alvo]; if not c then return end
	if rapido then correntes[alvo] = nil; destruirCorrentes(c, false); return end
	if c.soltando then return end
	c.soltando = os.clock(); local lento = c.lento or 1
	for _, x in ipairs(c.extras) do local e = x:FindFirstChildOfClass("ParticleEmitter"); if e then e.Rate = 0 end end
	for _, cad in ipairs(c.cad) do poeiraBase(cad.base, cad.normal, c.f, 4) end
	TweenService:Create(c.hl, TweenInfo.new(T_SOLTA * lento), {OutlineTransparency = 1, FillTransparency = 1}):Play()
	task.delay(T_SOLTA * lento + 0.05, function() if correntes[alvo] == c then correntes[alvo] = nil; destruirCorrentes(c, true) end end)
end
local function easeOutBack(x) local k = 1.3; return 1 + (k + 1) * (x - 1) ^ 3 + k * (x - 1) ^ 2 end
local ESCONDE = CFrame.new(0, -500, 0)
local function prender(d, f)
	local alvo = d.alvo; local r = alvo and raizDe(alvo); if not r or f <= 0 then return end
	soltarCorrentes(alvo, true)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {alvo, pastaFX()}; rp.IgnoreWater = true
	local _, ext = alvo:GetBoundingBox()
	local esc = math.clamp(ext.Y / 5.5, 0.8, 2)
	local passo = (ELO.comp - 2 * ELO.fio) * esc
	local hc = workspace:Raycast(r.Position, Vector3.new(0, -30, 0), rp)
	local chaoY = hc and hc.Position.Y or (r.Position.Y - 3)
	local modelo = Instance.new("Model"); modelo.Name = "Correntes_" .. alvo.Name; modelo.Parent = pastaFX()
	local hl = Instance.new("Highlight"); hl.Adornee = modelo; hl.DepthMode = Enum.HighlightDepthMode.Occluded
	hl.FillColor = VIOLETA; hl.FillTransparency = 0.9; hl.OutlineColor = C3(115, 45, 190); hl.OutlineTransparency = 0.5; hl.Parent = modelo
	local lento = math.max(1, tonumber(workspace:GetAttribute("VFXSombra_Lento")) or 1)   -- so revisao (capturas): desacelera a animacao
	local c = {modelo = modelo, hl = hl, cad = {}, extras = {}, t0 = os.clock(), f = f, esc = esc, passo = passo, lento = lento,
		anel = {a = math.max(ext.X / 2 + 0.2 * esc, esc), b = math.max(ext.Z / 2 + 0.3 * esc, esc), y = 0.35 * esc, elos = {}}}
	correntes[alvo] = c
	local giro = math.random() * math.pi * 2
	for i = 1, NCORR do
		local fi = giro + (i - 1) * 2 * math.pi / NCORR + (math.random() - 0.5) * 0.35
		local rb = R_BASE * esc * (0.9 + math.random() * 0.2)
		local pw = r.CFrame * Vector3.new(math.cos(fi) * rb, 0, math.sin(fi) * rb)
		local h = workspace:Raycast(Vector3.new(pw.X, r.Position.Y + 2, pw.Z), Vector3.new(0, -(r.Position.Y - chaoY) - 8, 0), rp)
		if h then                                                         -- sem chao real ali: essa corrente nao existe
			local cad = {fi = fi, base = h.Position, normal = h.Normal, giro = math.random() * math.pi, fase = math.random() * 6, elos = {}}
			for _ = 1, MAX_BASE do table.insert(cad.elos, {pc = novoElo(esc, modelo), vis = false}) end
			table.insert(c.cad, cad)
			local a = ancora(h.Position + h.Normal * 0.3); table.insert(c.extras, a)  -- breu residual na boca do buraco
			emissor(a, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.6, Size = ns(0, 0.7, 1, 2.2), Transparency = ns(0, 0.6, 1, 1),
				Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(0.5, 1.5), SpreadAngle = Vector2.new(60, 60), Rotation = NumberRange.new(0, 360),
				EmissionDirection = Enum.NormalId.Top, Rate = 3 * f}))
			poeiraBase(h.Position, h.Normal, f, 5)
		end
	end
	local A = c.anel                                                     -- perimetro da elipse (Ramanujan) -> n par de elos
	local per = math.pi * (3 * (A.a + A.b) - math.sqrt((3 * A.a + A.b) * (A.a + 3 * A.b)))
	local n = math.clamp(math.floor(per / passo + 0.5), 8, MAX_ANEL); if n % 2 == 1 then n -= 1 end
	A.n, A.th0 = n, (c.cad[1] and c.cad[1].fi or giro)
	for _ = 1, n do table.insert(A.elos, {pc = novoElo(esc, modelo), vis = false}) end
	local partes, cfs = {}, {}
	local function por(el, cf, tr)
		for _, x in ipairs(el.pc) do table.insert(partes, x[1]); table.insert(cfs, cf * x[2]); if x[1].Transparency ~= tr then x[1].Transparency = tr end end
	end
	local tc = T_SOBE * 0.7 + T_FECHA                                     -- anel fechado
	c.con = RunService.Heartbeat:Connect(function()
		if not (alvo.Parent and r.Parent) then soltarCorrentes(alvo, true); return end
		local agora = os.clock(); local t = (agora - c.t0) / lento
		if not c.soltando and agora - c.t0 > (d.duracao or 2.5) + 1.5 then soltarCorrentes(alvo, false) end   -- seguranca se o "soltar" nao chegar
		local s = c.soltando and math.min(1, (agora - c.soltando) / (T_SOLTA * lento)) or 0
		local tr = s > 0 and s ^ 1.5 or 0
		local rcf = r.CFrame
		local escA = t < tc and 1.15 or 1 + 0.15 * math.exp(-(t - tc) / 0.12) * math.cos(22 * (t - tc))
		escA += 0.35 * s; local dy = -0.9 * esc * s
		local function pontoAnel(th) return rcf * Vector3.new(math.cos(th) * A.a * escA, A.y + dy, math.sin(th) * A.b * escA) end
		table.clear(partes); table.clear(cfs)
		-- correntes do chao: a ponta sobe com inercia (passa um pouco e volta); elos saem empurrados da terra
		local sobe = math.min(1, t / T_SOBE)
		local frac = s > 0 and (1 - s * s) or (sobe < 1 and easeOutBack(sobe) or 1)
		for _, cad in ipairs(c.cad) do
			local alvoP = pontoAnel(cad.fi)
			local V = alvoP - cad.base; local L = V.Magnitude
			if L > (MAX_BASE - 0.5) * passo then                            -- alvo se afastou: a corrente sai de um ponto mais perto
				local p = alvoP - V.Unit * (MAX_BASE - 1) * passo
				local h = workspace:Raycast(p + Vector3.new(0, 3, 0), Vector3.new(0, -12, 0), rp)
				if h then cad.base, cad.normal = h.Position, h.Normal; V = alvoP - cad.base; L = V.Magnitude end
			end
			local u = L > 0.01 and V / L or Vector3.yAxis
			local perp = u:Cross(Vector3.yAxis); perp = perp.Magnitude > 0.1 and perp.Unit or Vector3.xAxis
			local tl = t - T_SOBE
			local amp = (tl > 0 and 0.22 * esc * math.exp(-tl / 0.2) * math.sin(38 * tl) or 0) + 0.02 * esc * math.sin(6 * t + cad.fase)
			local comp = L * frac; local ponta = cad.base + u * comp
			for k, el in ipairs(cad.elos) do
				local sk = (k - 0.5) * passo
				if sk <= comp + 0.1 * passo then
					local x = math.clamp((comp - sk) / L, 0, 1)
					por(el, cfElo(ponta - u * sk + perp * (math.sin(math.pi * x) * amp), u, cad.giro + (k % 2) * math.pi / 2), tr); el.vis = true
				elseif el.vis then por(el, ESCONDE, 1); el.vis = false end
			end
		end
		-- anel: fecha a partir dos pontos de chegada das correntes
		local fecha = math.clamp((t - T_SOBE * 0.7) / T_FECHA, 0, 1)
		local meio = math.pi / math.max(1, #c.cad) + 0.3
		for j, el in ipairs(A.elos) do
			local th = A.th0 + (j - 1) * 2 * math.pi / A.n
			local dmin = math.pi
			if #c.cad == 0 then dmin = 0 else for _, cad in ipairs(c.cad) do local dd = math.abs((th - cad.fi + math.pi) % (2 * math.pi) - math.pi); if dd < dmin then dmin = dd end end end
			if dmin <= fecha * meio then
				local tg = rcf:VectorToWorldSpace(Vector3.new(-math.sin(th) * A.a, 0, math.cos(th) * A.b)).Unit
				por(el, cfElo(pontoAnel(th), tg, (j % 2) * math.pi / 2), tr); el.vis = true
			elseif el.vis then por(el, ESCONDE, 1); el.vis = false end
		end
		if #partes > 0 then workspace:BulkMoveTo(partes, cfs, Enum.BulkMoveMode.FireCFrameChanged) end
	end)
end
local function correntesEvento(m, d, f)
	if d.fase == "aviso" then aviso(d, f)
	elseif d.fase == "erupcao" then erupcao(d, f)
	elseif d.fase == "prender" then prender(d, f)
	elseif d.fase == "soltar" then if d.alvo then soltarCorrentes(d.alvo, false) end end
end

-- ===== ECLIPSE DRACONICO v2 (04/11, "mais real e mais escandaloso"): um ECLIPSE de verdade no ceu ===================
-- Ceu: um SOL branco-dourado surge acima/a frente do dragao e uma LUA negra desliza sobre ele durante a antecipacao
-- (BillboardGui em studs: le de qualquer camera, sem textura enviada). No pico do rugido = TOTALIDADE: anel de diamante
-- (clarao na borda da lua), CORONA violeta-branca com raios girando, e o mundo escurece de verdade em volta (ColorCorrection
-- local forte, mais forte quanto mais perto: total ate o raio, some ate 2,5 x raio). No chao: cupula de sombra que se
-- expande ate o raio (vista de fora), onda escura, chao escurecido, bruma na borda, tremor de camera em quem esta perto.
-- Marcas detonadas: coluna de breu sobe do alvo + implosao/estouro (tamanho = numero de marcas). Fim: a lua sai, a luz
-- volta em ~1,2 s. Antecipacao no corpo: escurece (1 Highlight) e fios de breu convergem. Sem luz dinamica.
-- Orcamento: 1 BillboardGui (~20 frames), 1 ColorCorrection, 60 part./s na antecipacao, ~115 vivas na area por `duracao`.
-- Limite: em terreno muito irregular o disco plano do chao pode cortar/flutuar.
local ECL = {brilho = -0.38, contraste = 0.22, saturacao = -0.78, tinta = C3(165, 150, 225), entra = 0.35, sai = 1.2, longe = 2.5}
local eclipses = {}                                                  -- areas ativas {pos, raio, t0, tot, ate}
local cc, ccCon, ccPeso = nil, nil, 0
local function pesoEclipse(e, cam, agora)                            -- 0..1: distancia da camera x fase do eclipse
	local d = (cam.CFrame.Position - e.pos).Magnitude
	local dist = d <= e.raio and 1 or math.max(0, 1 - (d - e.raio) / (e.raio * (ECL.longe - 1)))
	local fase
	if agora < e.tot then fase = 0.55 * math.clamp((agora - e.t0) / math.max(0.1, e.tot - e.t0), 0, 1) ^ 2    -- lua cobrindo
	elseif agora < e.ate then fase = 1 else fase = math.max(0, 1 - (agora - e.ate) / ECL.sai) end           -- totalidade / saida
	return dist * fase
end
local function ligarCorEclipse()
	if ccCon then return end
	local Lt = game:GetService("Lighting")
	ccCon = RunService.RenderStepped:Connect(function(dt)
		local cam = workspace.CurrentCamera; local alvo = 0; local agora = os.clock()
		for i = #eclipses, 1, -1 do
			local e = eclipses[i]
			if agora > e.ate + ECL.sai then table.remove(eclipses, i) elseif cam then alvo = math.max(alvo, pesoEclipse(e, cam, agora)) end
		end
		ccPeso = ccPeso + (alvo - ccPeso) * math.min(1, dt / ECL.entra)
		if ccPeso > 0.002 then
			if not (cc and cc.Parent) then cc = Instance.new("ColorCorrectionEffect"); cc.Name = "EclipseSombra"; cc.Parent = Lt end
			cc.Brightness = ECL.brilho * ccPeso; cc.Contrast = ECL.contraste * ccPeso; cc.Saturation = ECL.saturacao * ccPeso
			cc.TintColor = Color3.new(1, 1, 1):Lerp(ECL.tinta, ccPeso)
		elseif #eclipses == 0 then
			if cc then cc:Destroy(); cc = nil end
			ccCon:Disconnect(); ccCon = nil; ccPeso = 0
		end
	end)
end
local function chaoDe(pos, ign)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = ign
	local h = workspace:Raycast(pos + Vector3.new(0, 4, 0), Vector3.new(0, -80, 0), rp); return h and h.Position, h and h.Normal
end
-- ceu: sol + lua + corona num BillboardGui (tudo em escala: um "disco" = frame redondo)
local ceus = {}                                                       -- [dragao] = {gui, ...}
local function circulo(pai, tam, cor, tr, z)
	local f = Instance.new("Frame"); f.AnchorPoint = Vector2.new(0.5, 0.5); f.Position = UDim2.fromScale(0.5, 0.5); f.Size = UDim2.fromScale(tam, tam)
	f.BackgroundColor3 = cor; f.BackgroundTransparency = tr; f.BorderSizePixel = 0; f.ZIndex = z or 1
	local c = Instance.new("UICorner"); c.CornerRadius = UDim.new(0.5, 0); c.Parent = f; f.Parent = pai; return f
end
local function criarCeu(m, dur)
	local velho = ceus[m]; if velho then velho.gui:Destroy(); velho.anc:Destroy() end
	local pv = m:GetPivot(); local lv = Vector3.new(pv.LookVector.X, 0, pv.LookVector.Z); lv = lv.Magnitude > 0.05 and lv.Unit or Vector3.zAxis
	local pos = pv.Position + lv * 110 + Vector3.new(0, 135, 0)
	local anc = ancora(pos)
	local D = 64                                                      -- studs: diametro do sol
	local gui = Instance.new("BillboardGui"); gui.Name = "EclipseCeu"; gui.Adornee = anc; gui.Size = UDim2.new(D * 3, 0, D * 3, 0)
	gui.LightInfluence = 0; gui.AlwaysOnTop = false; gui.MaxDistance = 3000; gui.ResetOnSpawn = false; gui.Parent = anc
	local raiz = Instance.new("Frame"); raiz.BackgroundTransparency = 1; raiz.Size = UDim2.fromScale(1, 1); raiz.Parent = gui
	local S1 = 1 / 3                                                  -- fracao da gui = 1 diametro do sol
	local brilho = {}                                                 -- halo quente do sol (some na totalidade)
	for i, k in ipairs({2.6, 2.0, 1.55, 1.25}) do table.insert(brilho, circulo(raiz, S1 * k, C3(255, 236, 200), 1, i)) end
	local sol = circulo(raiz, S1, C3(255, 246, 225), 1, 6)
	local corona = {}                                                 -- corona violeta-branca (aparece na totalidade)
	for i, k in ipairs({2.9, 2.2, 1.7, 1.3, 1.1}) do table.insert(corona, circulo(raiz, S1 * k, i >= 4 and C3(235, 225, 255) or C3(150, 90, 255), 1, 6 + i)) end
	local raios = Instance.new("Frame"); raios.BackgroundTransparency = 1; raios.AnchorPoint = Vector2.new(0.5, 0.5); raios.Position = UDim2.fromScale(0.5, 0.5)
	raios.Size = UDim2.fromScale(1, 1); raios.ZIndex = 12; raios.Parent = raiz
	local fitas = {}
	for i = 1, 10 do                                                  -- raios finos da corona (giram devagar)
		local f = Instance.new("Frame"); f.AnchorPoint = Vector2.new(0.5, 0.5); f.Position = UDim2.fromScale(0.5, 0.5)
		f.Size = UDim2.fromScale(0.012 + (i % 3) * 0.006, S1 * (1.9 + (i % 4) * 0.35)); f.Rotation = i * 36 + (i % 2) * 11
		f.BackgroundColor3 = C3(220, 200, 255); f.BackgroundTransparency = 1; f.BorderSizePixel = 0; f.ZIndex = 12; f.Parent = raios
		local gr = Instance.new("UIGradient"); gr.Rotation = 90; gr.Transparency = ns(0, 1, 0.42, 0.15, 0.5, 0, 0.58, 0.15, 1, 1); gr.Parent = f
		table.insert(fitas, f)
	end
	local lua = circulo(raiz, S1 * 1.04, C3(4, 0, 8), 0, 20)
	local diamante = circulo(raiz, S1 * 0.22, C3(255, 255, 255), 1, 21)
	local C = {gui = gui, anc = anc, lua = lua, sol = sol, brilho = brilho, corona = corona, fitas = fitas, raios = raios, diamante = diamante,
		t0 = os.clock(), dur = dur, S1 = S1, fase = "cobrindo"}
	ceus[m] = C
	for _, b in ipairs(brilho) do TweenService:Create(b, TweenInfo.new(0.4), {BackgroundTransparency = 0.86}):Play() end
	TweenService:Create(sol, TweenInfo.new(0.4), {BackgroundTransparency = 0}):Play()
	local x0 = 0.5 + S1 * 1.25
	lua.Position = UDim2.fromScale(x0, 0.5 - S1 * 0.35)
	TweenService:Create(lua, TweenInfo.new(dur, Enum.EasingStyle.Sine, Enum.EasingDirection.Out), {Position = UDim2.fromScale(0.5, 0.5)}):Play()
	local con; con = RunService.RenderStepped:Connect(function(dt)
		if not gui.Parent then con:Disconnect(); return end
		raios.Rotation += dt * 6
		if C.fase == "cobrindo" then                                   -- o halo do sol diminui conforme a lua cobre
			local k = math.clamp((os.clock() - C.t0) / dur, 0, 1)
			for i, b in ipairs(brilho) do b.BackgroundTransparency = 0.86 + 0.14 * k ^ 1.5 end
		end
	end)
	return C
end
local function totalidade(m, dur)
	local C = ceus[m]; if not C then return end
	C.fase = "total"
	for _, b in ipairs(C.brilho) do b.BackgroundTransparency = 1 end
	-- anel de diamante: clarao na borda da lua, depois a corona aparece
	C.diamante.Position = UDim2.fromScale(0.5 + C.S1 * 0.45, 0.5 - C.S1 * 0.22); C.diamante.BackgroundTransparency = 0; C.diamante.Size = UDim2.fromScale(C.S1 * 0.5, C.S1 * 0.5)
	TweenService:Create(C.diamante, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {BackgroundTransparency = 1, Size = UDim2.fromScale(C.S1 * 0.12, C.S1 * 0.12)}):Play()
	for i, c in ipairs(C.corona) do TweenService:Create(c, TweenInfo.new(0.35 + i * 0.05), {BackgroundTransparency = ({0.93, 0.88, 0.8, 0.55, 0.25})[i]}):Play() end
	for _, f in ipairs(C.fitas) do TweenService:Create(f, TweenInfo.new(0.6), {BackgroundTransparency = 0.35}):Play() end
	task.delay(dur, function()                                        -- a lua sai e a luz volta
		if not C.gui.Parent then return end
		C.fase = "saindo"
		TweenService:Create(C.lua, TweenInfo.new(1.2, Enum.EasingStyle.Sine, Enum.EasingDirection.In), {Position = UDim2.fromScale(0.5 - C.S1 * 1.3, 0.5 + C.S1 * 0.35)}):Play()
		for _, c in ipairs(C.corona) do TweenService:Create(c, TweenInfo.new(0.6), {BackgroundTransparency = 1}):Play() end
		for _, f in ipairs(C.fitas) do TweenService:Create(f, TweenInfo.new(0.5), {BackgroundTransparency = 1}):Play() end
		for _, b in ipairs(C.brilho) do TweenService:Create(b, TweenInfo.new(1.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {BackgroundTransparency = 0.86}):Play() end
		task.delay(1.0, function() TweenService:Create(C.sol, TweenInfo.new(0.6), {BackgroundTransparency = 1}):Play(); for _, b in ipairs(C.brilho) do TweenService:Create(b, TweenInfo.new(0.6), {BackgroundTransparency = 1}):Play() end end)
		task.delay(1.7, function() if ceus[m] == C then ceus[m] = nil end; C.gui:Destroy(); C.anc:Destroy() end)
	end)
end
local function tremer(pos, raio, amp, durT)
	local cam = workspace.CurrentCamera; if not cam or (cam.CFrame.Position - pos).Magnitude > raio * 2 then return end
	local t0 = os.clock(); local c; c = RunService.RenderStepped:Connect(function()
		local k = 1 - (os.clock() - t0) / durT; if k <= 0 then c:Disconnect(); return end
		cam.CFrame *= CFrame.Angles((math.random() - 0.5) * amp * k * 0.02, (math.random() - 0.5) * amp * k * 0.02, 0)
	end)
end
local function eclipseEvento(m, d, f)
	if d.fase == "inicio" then
		local dur = d.detona or 2.15
		criarCeu(m, dur)
		local pv = m:GetPivot().Position
		table.insert(eclipses, {pos = pv, raio = d.raio or 60, t0 = os.clock(), tot = os.clock() + dur, ate = os.clock() + dur + 4}); ligarCorEclipse()
		-- o corpo escurece aos poucos (Highlight so de preenchimento + contorno violeta discreto) e fios de breu sao puxados
		local hl = Instance.new("Highlight"); hl.Name = "EclipseCorpo"; hl.FillColor = PRETO; hl.FillTransparency = 1; hl.OutlineColor = C3(110, 40, 185)
		hl.OutlineTransparency = 1; hl.DepthMode = Enum.HighlightDepthMode.Occluded; hl.Adornee = m; hl.Parent = pastaFX()
		TweenService:Create(hl, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {FillTransparency = 0.4, OutlineTransparency = 0.35}):Play()
		task.delay(dur + 4, function() if hl.Parent then TweenService:Create(hl, TweenInfo.new(1), {FillTransparency = 1, OutlineTransparency = 1}):Play(); Debris:AddItem(hl, 1.05) end end)
		local casca = peca({Shape = Enum.PartType.Ball, Size = Vector3.new(36, 36, 36), Transparency = 1, CFrame = m:GetPivot()}); Debris:AddItem(casca, dur + 1.2)
		if f > 0 then
			local e = emissor(casca, {Texture = TEX.fumaca, Orientation = Enum.ParticleOrientation.VelocityParallel, Squash = ns(0, 1.4, 1, 0.4),
				Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.4, Size = ns(0, 1.6, 1, 0.3), Transparency = ns(0, 1, 0.25, 0.45, 0.85, 0.4, 1, 1),
				Lifetime = NumberRange.new(0.6, 0.75), Speed = NumberRange.new(24, 30), Rate = 60 * f,
				Shape = Enum.ParticleEmitterShape.Sphere, ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface})
			task.delay(dur - 0.15, function() if e.Parent then e.Rate = 0 end end)
		end
		local c; c = RunService.Heartbeat:Connect(function()             -- a casca segue o tronco (o dragao pode estar voando)
			if not casca.Parent or not m.Parent then c:Disconnect(); return end
			local q = ossoC(m, "Coluna3") or ossoC(m, "Coluna2"); casca.CFrame = CFrame.new(q and q.TransformedWorldCFrame.Position or m:GetPivot().Position)
		end)
	elseif d.fase == "detonar" then
		local r, dur = d.raio or 60, d.duracao or 4
		totalidade(m, dur)
		local achou = false                                              -- ajusta a area (inicio) para a posicao exata da detonacao
		for _, e in ipairs(eclipses) do if (e.pos - d.pos).Magnitude < 40 and os.clock() < e.ate then e.pos = d.pos; e.tot = os.clock(); e.ate = os.clock() + dur; achou = true end end
		if not achou then table.insert(eclipses, {pos = d.pos, raio = r, t0 = os.clock() - 1, tot = os.clock(), ate = os.clock() + dur}) end
		ligarCorEclipse()
		tremer(d.pos, r, 1.2, 0.6)
		if f <= 0 then return end
		local g, n = chaoDe(d.pos, {m, pastaFX()})
		-- cupula de sombra: esfera escura translucida que estoura ate o raio (le de fora; quem esta dentro ve a cor)
		local cup = peca({Shape = Enum.PartType.Ball, Size = Vector3.new(10, 10, 10), Color = PRETO, Material = Enum.Material.SmoothPlastic, Transparency = 0.55, CFrame = CFrame.new(g or d.pos)})
		TweenService:Create(cup, TweenInfo.new(0.55, Enum.EasingStyle.Quart, Enum.EasingDirection.Out), {Size = Vector3.new(r * 2, r * 2, r * 2), Transparency = 0.82}):Play()
		task.delay(dur, function() if cup.Parent then TweenService:Create(cup, TweenInfo.new(ECL.sai), {Transparency = 1}):Play() end end)
		Debris:AddItem(cup, dur + ECL.sai + 0.1)
		if g then                                                        -- onda escura rente ao chao ate o raio
			local onda = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.2, 8, 8), Color = PRETO, Material = Enum.Material.SmoothPlastic,
				Transparency = 0.2, CFrame = cfChao(g + n * 0.15, n)})
			local borda = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.16, 10, 10), Color = C3(110, 40, 185), Material = Enum.Material.Neon,
				Transparency = 0.45, CFrame = cfChao(g + n * 0.1, n)})
			local ti = TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
			TweenService:Create(onda, ti, {Size = Vector3.new(0.2, r * 2.2, r * 2.2), Transparency = 1}):Play()
			TweenService:Create(borda, ti, {Size = Vector3.new(0.16, r * 2.3, r * 2.3), Transparency = 1}):Play()
			Debris:AddItem(onda, 0.7); Debris:AddItem(borda, 0.7)
			-- chao da area escurece: 1 disco translucido rente ao chao
			local sombraChao = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.12, r * 2, r * 2), Color = PRETO, Material = Enum.Material.SmoothPlastic,
				Transparency = 1, CFrame = cfChao(g + n * 0.06, n)})
			TweenService:Create(sombraChao, TweenInfo.new(0.4), {Transparency = 0.55}):Play()
			task.delay(dur, function() if sombraChao.Parent then TweenService:Create(sombraChao, TweenInfo.new(ECL.sai), {Transparency = 1}):Play() end end)
			Debris:AddItem(sombraChao, dur + ECL.sai + 0.1)
			-- area: nevoa baixa espalhada no disco + anel continuo na borda (Disc com ShapePartial 0,1 = faixa fina), enquanto dura
			local base = peca({Size = Vector3.new(r * 2, 0.2, r * 2), Transparency = 1, CFrame = CFrame.new(g + n * 0.8)}); Debris:AddItem(base, dur + 2.5)
			local fundo = emissor(base, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.6, Size = ns(0, 9, 1, 18),
				Transparency = ns(0, 1, 0.3, 0.68, 1, 1), Lifetime = NumberRange.new(2, 2.6), Speed = NumberRange.new(0.3, 1.2), Drag = 1,
				Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-10, 10), EmissionDirection = Enum.NormalId.Top, Rate = 10 * f,
				Shape = Enum.ParticleEmitterShape.Disc, ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume}))
			local anel = emissor(base, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.6, Size = ns(0, 7, 1, 14),
				Transparency = ns(0, 1, 0.25, 0.5, 1, 1), Lifetime = NumberRange.new(1.6, 2.2), Speed = NumberRange.new(1, 3), Drag = 1,
				Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-15, 15), EmissionDirection = Enum.NormalId.Top, Rate = 45 * f,
				Shape = Enum.ParticleEmitterShape.Disc, ShapePartial = 0.1, ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume}))
			task.delay(dur, function() if fundo.Parent then fundo.Rate = 0; anel.Rate = 0 end end)
		end
		local b = bocaJato(m); local ab = ancora(b); Debris:AddItem(ab, 1.6)    -- o rugido solta breu pela boca
		emissor(ab, flipFumaca({Color = seq({PRETO, BREU}), LightEmission = 0, LightInfluence = 0.5, Size = ns(0, 2, 1, 9), Transparency = ns(0, 0.5, 1, 1),
			Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(12, 22), Drag = 2, SpreadAngle = Vector2.new(50, 50),
			Rotation = NumberRange.new(0, 360), Rate = 0})):Emit(math.max(2, math.floor(14 * f)))
	elseif d.fase == "marca" then
		local a = d.alvo; local rr = a and raizDe(a); if not rr or f <= 0 then return end
		local n = math.clamp(d.marcas or 1, 1, 5)
		local casca = peca({Shape = Enum.PartType.Ball, Size = Vector3.new(7 + n * 1.5, 7 + n * 1.5, 7 + n * 1.5), Transparency = 1, CFrame = rr.CFrame}); Debris:AddItem(casca, 1.4)
		emissor(casca, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.5, Size = ns(0, 2 + n * 0.3, 1, 0.4), Transparency = ns(0, 0.8, 0.4, 0.45, 1, 1),
			Lifetime = NumberRange.new(0.25, 0.3), Speed = NumberRange.new(14, 18), Rate = 0, Rotation = NumberRange.new(0, 360),
			Shape = Enum.ParticleEmitterShape.Sphere, ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface})):Emit(4 + n * 3)
		task.delay(0.28, function()                                       -- implode e estoura + coluna de breu subindo do alvo
			if not rr.Parent then return end
			local at = ancora(rr.Position); Debris:AddItem(at, 2.2)
			emissor(at, flipFumaca({Color = seq({PRETO, BREU, C3(60, 22, 100)}), LightEmission = 0.05, LightInfluence = 0.5, Size = ns(0, 1.5, 1, 4 + n * 1.2),
				Transparency = ns(0, 0.4, 0.6, 0.6, 1, 1), Lifetime = NumberRange.new(0.5, 0.8), Speed = NumberRange.new(6 + n, 10 + n * 2), Drag = 3,
				SpreadAngle = Vector2.new(180, 180), Rotation = NumberRange.new(0, 360), Rate = 0})):Emit(5 + n * 3)
			local col = emissor(at, {Texture = TEX.fumaca, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = seq({PRETO, C3(70, 25, 120)}),
				LightEmission = 0.1, LightInfluence = 0.4, Size = ns(0, 1.2 + n * 0.25, 1, 0.3), Squash = ns(0, 1.5, 1, 1),
				Transparency = ns(0, 0.3, 0.7, 0.6, 1, 1), Lifetime = NumberRange.new(0.6, 0.9), Speed = NumberRange.new(28 + n * 4, 40 + n * 5),
				SpreadAngle = Vector2.new(4, 4), EmissionDirection = Enum.NormalId.Top, Rate = 50})
			task.delay(0.5, function() if col.Parent then col.Rate = 0 end end)
		end)
	end
end

function S.evento(d, f)
	local m = d.d
	if d.hab == "Correntes" and d.fase == "soltar" then correntesEvento(m, d, f); return true end   -- soltar mesmo sem o dragao
	if not m or not m.Parent then return false end
	if d.fase == "reacao" then reacao(d, f); return true end           -- vinheta mesmo sem LOD visual
	if d.hab == "Sopro" then if f > 0 or d.fase == "fim" then soproEvento(m, d, f) end; return true end
	if d.hab == "Correntes" then correntesEvento(m, d, f); return true end
	if d.hab == "Eclipse" then eclipseEvento(m, d, f); return true end
	return false
end
return S
]=====]
assert(loadstring(vfx), "VFXSombra nao compila")
local pasta = RS.Animacoes_Sombrio
local conc, rug, rugAr = pasta:FindFirstChild("Sombrio_Hab_Concentracao"), pasta:FindFirstChild("Sombrio_Rugido_Combate"), pasta:FindFirstChild("Sombrio_Rugido_Combate_Camada")
assert(conc and rug and rugAr, "clipe base ausente")
-- junta trechos {kfs, de, ate, deslocamento} num clipe novo (os quadros entre trechos o Roblox interpola)
local function juntar(nome, partes)
  local novo = Instance.new("KeyframeSequence"); novo.Name = nome; novo.Loop = false; novo.Priority = partes[1][1].Priority
  for _, p in ipairs(partes) do for _, k in ipairs(p[1]:GetChildren()) do
    if k:IsA("Keyframe") and k.Time >= p[2] - 1e-4 and k.Time <= p[3] + 1e-4 then local c = k:Clone(); c.Time = k.Time - p[2] + p[4]; c.Parent = novo end
  end end
  novo:SetAttribute("Origem", "Hab_Concentracao [0;0,9] + Rugido_Combate +1,15 s (PATCH_ECLIPSE_DRACONICO)"); return novo
end
if not SS:FindFirstChild("Backup_Eclipse_Draconico_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Eclipse_Draconico_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; RS.Combate_Dragoes.VFXSombra:Clone().Parent = f; f.Parent = SS end
for _, v in ipairs({{"Sombrio_Eclipse_Draconico", {{conc, 0, 0.9, 0}, {rug, 0, 9, 1.15}}}, {"Sombrio_Eclipse_Draconico_Camada", {{rugAr, 0, 0, 0}, {rugAr, 0, 9, 1.15}}}}) do
  local velho = pasta:FindFirstChild(v[1]); if velho then velho:Destroy() end; juntar(v[1], v[2]).Parent = pasta
end
for _, x in ipairs(novos) do x[1].Source = x[2] end
RS.Combate_Dragoes.VFXSombra.Source = vfx
return "aplicado: ConfigCombate + Nucleo + Passivas + Montaria + ConfigMontaria (" .. #novos .. ") + VFXSombra + 2 clipes; backup ServerStorage.Backup_Eclipse_Draconico_2026-11-04"
