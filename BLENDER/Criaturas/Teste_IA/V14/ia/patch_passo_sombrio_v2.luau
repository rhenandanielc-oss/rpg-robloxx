-- patch_passo_sombrio_v2.luau (Studio, Edit) — Passo Sombrio v2: invisivel + impulso por 5 s (04/11).
-- Gerado por sombrio/gerar_patch_passo_v2.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico
-- ServerStorage.Backup_Passo_Sombrio_v2_2026-11-04.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage")
local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end
local novos = {}
do local s = game.ServerScriptService.Combate_Dragao.ConfigCombate; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_PASSO_SOMBRIO_V2", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [=====[		-- Passo Sombrio (PATCH_PASSO_SOMBRIO): some em breu e reaparece `distancia` a frente ou `atras` do alvo travado (ate
		-- `alcance`), sem atravessar parede; sem dano. sumir/surgir = s de cada metade. NAO_APROVADO
		PassoSombrio = {recarga = 9, energia = 20, elemental = true, intensidade = "leve", clipe = "Hab_Investida",
			distancia = 60, alcance = 90, atras = 18, sumir = 0.3, surgir = 0.35},
]=====], [=====[		-- Passo Sombrio (PATCH_PASSO_SOMBRIO_V2, 04/11): dragao e cavaleiro ficam invisiveis aos outros por `duracao` s com
		-- +`bonus` de velocidade (chao e voo); nao e invulneravel; sem dano. ativar = s ocupado na ativacao. NAO_APROVADO
		PassoSombrio = {recarga = 20, energia = 25, elemental = true, intensidade = "leve", clipe = "Hab_Investida",
			duracao = 5, bonus = 0.6, ativar = 0.4},
]=====])
  assert(loadstring(src), "ConfigCombate.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Combate_Dragao.Nucleo; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_PASSO_SOMBRIO_V2", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [=====[-- PATCH_PASSO_SOMBRIO (04/11, escolha do usuario: 4a ativa do Sombrio, slot Tempestade/tecla 3): o dragao se desfaz em
-- breu e REAPARECE adiante. Sem alvo: `distancia` a frente (direcao da mira/frente). Com alvo travado/da IA: ATRAS do
-- alvo (a `atras` alem dele), ate `alcance`. Nunca atravessa parede (raio do corpo ao destino; para antes do obstaculo);
-- no chao reaparece no chao (mesma altura do pivo sobre o terreno); no ar mantem a altura (atras do alvo: a altura dele).
-- Sem dano (mobilidade). O corpo fica parado durante o passo (CorpoElevado: montaria/IA nao disputam o pivo). NAO_APROVADO.
local rpPasso = RaycastParams.new(); rpPasso.FilterType = Enum.RaycastFilterType.Exclude
function N:_PassoSombrio(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	local vfxF = workspace:FindFirstChild("VFX_Temporarios")
	local ign = {m, vfxF}; for _, a in ipairs(self:alvosValidos()) do table.insert(ign, a) end
	for _, p in ipairs(game:GetService("Players"):GetPlayers()) do if p.Character then table.insert(ign, p.Character) end end
	rpPasso.FilterDescendantsInstances = ign
	local pv = m:GetPivot(); local p0 = pv.Position
	local g0 = workspace:Raycast(p0 + Vector3.new(0, 6, 0), Vector3.new(0, -60, 0), rpPasso)
	local altura = g0 and (p0.Y - g0.Position.Y) or 0                  -- pivo sobre o chao (o dragao fica em pe no destino)
	-- destino desejado
	local destino
	local alvo = op.alvo and op.alvo.Parent and raiz(op.alvo)
	if alvo then
		local v = plano(alvo.Position - p0); local d = v.Magnitude
		local u = d > 0.5 and v.Unit or plano(self:frente()).Unit
		destino = p0 + u * math.min(d + def.atras, def.alcance)
		if noAr then destino = Vector3.new(destino.X, alvo.Position.Y + 6, destino.Z) end
	else
		local dir = (typeof(op.direcao) == "Vector3" and op.direcao.Magnitude > 0.1) and op.direcao.Unit or self:frente()
		if not noAr then dir = plano(dir).Magnitude > 0.1 and plano(dir).Unit or plano(self:frente()).Unit end
		destino = p0 + dir * def.distancia
	end
	-- parede/obstaculo entre a origem e o destino (no meio do corpo): para antes
	local cc = self:centroCorpo(); local off = cc - p0
	local v = destino - p0
	local h = v.Magnitude > 1 and workspace:Raycast(cc, v, rpPasso)
	if h then destino = p0 + v.Unit * math.max(0, (h.Position - cc).Magnitude - (m:GetAttribute("CorpoRaio") or 8) * 1.4) end
	if not noAr then                                                   -- no chao: assenta no terreno do destino
		local g = workspace:Raycast(destino + Vector3.new(0, 40, 0), Vector3.new(0, -160, 0), rpPasso)
		if g then destino = Vector3.new(destino.X, g.Position.Y + altura, destino.Z) else destino = Vector3.new(destino.X, p0.Y, destino.Z) end
	end
	FX:FireAllClients({d = m, hab = "PassoSombrio", fase = "sumir", el = el, de = p0 + off, ate = destino + off, tempo = def.sumir})
	m:SetAttribute("CorpoElevado", true)
	self:tocar(def.clipe, noAr, {}, function() end)
	task.wait(def.sumir)
	if m.Parent then m:PivotTo(CFrame.new(destino) * (pv - pv.Position)) end   -- mesma orientacao, novo lugar
	FX:FireAllClients({d = m, hab = "PassoSombrio", fase = "surgir", el = el, pos = destino + off, tempo = def.surgir})
	m:SetAttribute("UltimoPasso", ("%.0f studs%s"):format((destino - p0).Magnitude, alvo and " (atras do alvo)" or ""))
	task.wait(def.surgir)
	m:SetAttribute("CorpoElevado", nil)
end]=====], [=====[-- PATCH_PASSO_SOMBRIO_V2 (04/11, pedido do usuario: "algo que durasse mais tempo"): o dragao e, se montado, o CAVALEIRO
-- se desfazem em breu por `duracao` s: ficam INVISIVEIS para os outros (o dono ve um vulto) e ganham `bonus` de
-- velocidade (chao e voo, somado ao Rastro do Breu). Invisivel NAO e invulneravel: dano em area ainda pega. Durante o
-- efeito ninguem trava o alvo neles, a IA selvagem nao os percebe e o servidor recusa trava/alvo neles. Atacar nao
-- cancela. Sem teleporte. Atributos (fim = tempo do servidor): PassoInvisivel no modelo e no Character do cavaleiro,
-- PassoBonus no modelo. NAO_APROVADO.
function N:_PassoSombrio(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	local fim = workspace:GetServerTimeNow() + def.duracao
	local cav = m:GetAttribute("Cavaleiro"); local plr = cav and Players:GetPlayerByUserId(cav); local ch = plr and plr.Character
	m:SetAttribute("PassoInvisivel", fim); m:SetAttribute("PassoBonus", def.bonus)
	if ch then ch:SetAttribute("PassoInvisivel", fim) end
	FX:FireAllClients({d = m, hab = "PassoSombrio", fase = "inicio", el = el, fim = fim, cav = ch})
	m:SetAttribute("UltimoPasso", ("%.1f s, +%d%% vel%s"):format(def.duracao, def.bonus * 100, ch and ", com cavaleiro" or ""))
	task.delay(def.duracao, function()
		if m:GetAttribute("PassoInvisivel") == fim then m:SetAttribute("PassoInvisivel", nil); m:SetAttribute("PassoBonus", nil) end
		if ch and ch:GetAttribute("PassoInvisivel") == fim then ch:SetAttribute("PassoInvisivel", nil) end
		if m.Parent then FX:FireAllClients({d = m, hab = "PassoSombrio", fase = "fim", el = el, cav = ch}) end
	end)
	self:tocar(def.clipe, noAr, {}, function() end)
	task.wait(def.ativar)
end]=====])
  assert(loadstring(src), "Nucleo.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Montaria_Dragao_Servidor; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_PASSO_SOMBRIO_V2", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [=====[		or ataque == "PassoSombrio"                                                         -- PATCH_PASSO_SOMBRIO (Sombrio)
]=====], [=====[]=====])
  src = troca(src, [=====[			* (1 + (m:GetAttribute("RastroBonus") or 0))                                -- PATCH_RASTRO_BREU (03/11): passiva do Sombrio]=====], [=====[			* (1 + (m:GetAttribute("RastroBonus") or 0) + (m:GetAttribute("PassoBonus") or 0))   -- PATCH_RASTRO_BREU (03/11) + PATCH_PASSO_SOMBRIO_V2]=====])
  src = troca(src, [=====[(e.correr and Cfg.vooRapidoVel or Cfg.vooVel) * f * (1 + (m:GetAttribute("RastroBonus") or 0)) or 0   -- PATCH_RASTRO_BREU]=====], [=====[(e.correr and Cfg.vooRapidoVel or Cfg.vooVel) * f * (1 + (m:GetAttribute("RastroBonus") or 0) + (m:GetAttribute("PassoBonus") or 0)) or 0   -- PATCH_RASTRO_BREU + PATCH_PASSO_SOMBRIO_V2]=====])
  assert(loadstring(src), "Montaria_Dragao_Servidor.server.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Combate_Dragao_Servidor; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_PASSO_SOMBRIO_V2", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [=====[			if rr and (rr.Position - m:GetPivot().Position).Magnitude <= 420 then
]=====], [=====[			local inv = alvo:GetAttribute("PassoInvisivel")                   -- PATCH_PASSO_SOMBRIO_V2: invisivel nao vira alvo
			if rr and (rr.Position - m:GetPivot().Position).Magnitude <= 420 and not (typeof(inv) == "number" and inv > workspace:GetServerTimeNow()) then
]=====])
  assert(loadstring(src), "Combate_Dragao_Servidor.server.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.IA_Dragao.Cerebro; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_PASSO_SOMBRIO_V2", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [=====[function raizDe(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end
]=====], [=====[function raizDe(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end
local function invisivel(x) local v = x and x:GetAttribute("PassoInvisivel"); return typeof(v) == "number" and v > workspace:GetServerTimeNow() end   -- PATCH_PASSO_SOMBRIO_V2
]=====])
  src = troca(src, [=====[		if ch and h and h.Health > 0 and raizDe(ch) then table.insert(l, ch) end
]=====], [=====[		if ch and h and h.Health > 0 and raizDe(ch) and not invisivel(ch) then table.insert(l, ch) end
]=====])
  src = troca(src, [=====[	for _, m in ipairs(CollectionService:GetTagged("Invasor_Teste")) do if raizDe(m) then table.insert(l, m) end end
]=====], [=====[	for _, m in ipairs(CollectionService:GetTagged("Invasor_Teste")) do if raizDe(m) and not invisivel(m) then table.insert(l, m) end end
]=====])
  src = troca(src, [=====[		if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) or (r and zonaSegura(r.Position)) or cansou then
]=====], [=====[		if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) or (r and zonaSegura(r.Position)) or cansou
			or invisivel(alvo) then                                          -- PATCH_PASSO_SOMBRIO_V2: sumiu em breu
]=====])
  src = troca(src, [=====[	local r = raizDe(alvo); if not r or zonaSegura(r.Position) then return false end
]=====], [=====[	local r = raizDe(alvo); if not r or zonaSegura(r.Position) or invisivel(alvo) then return false end
]=====])
  assert(loadstring(src), "Cerebro.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.StarterPlayer.StarterPlayerScripts.Montaria_Cliente; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_PASSO_SOMBRIO_V2", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [=====[local function candidatosTrava()
]=====], [=====[local function invisivel(x) local v = x and x:GetAttribute("PassoInvisivel"); return typeof(v) == "number" and v > workspace:GetServerTimeNow() end   -- PATCH_PASSO_SOMBRIO_V2
local function candidatosTrava()
]=====])
  src = troca(src, [=====[		if raizAlvo(md) and alvoVivo(md) then table.insert(l, md) end
]=====], [=====[		if raizAlvo(md) and alvoVivo(md) and not invisivel(md) then table.insert(l, md) end
]=====])
  src = troca(src, [=====[	if not (m and r and alvoVivo(trava.alvo)) or (r.Position - m:GetPivot().Position).Magnitude > TRAVA.quebra then soltarTrava(); return nil end
]=====], [=====[	if not (m and r and alvoVivo(trava.alvo)) or invisivel(trava.alvo) or (r.Position - m:GetPivot().Position).Magnitude > TRAVA.quebra then soltarTrava(); return nil end
]=====])
  assert(loadstring(src), "Montaria_Cliente.client.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.StarterPlayer.StarterPlayerScripts.RastroBreu_Cliente; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_PASSO_SOMBRIO_V2", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [=====[local RunService = game:GetService("RunService")
]=====], [=====[local RunService = game:GetService("RunService")
local lp = game:GetService("Players").LocalPlayer
]=====])
  src = troca(src, [=====[			if m:GetAttribute("RastroModo") then nivel = 2 elseif (m:GetAttribute("RastroCarga") or 0) > 0 then nivel = 1 end
]=====], [=====[			if m:GetAttribute("RastroModo") then nivel = 2 elseif (m:GetAttribute("RastroCarga") or 0) > 0 then nivel = 1 end
			local inv = m:GetAttribute("PassoInvisivel")                 -- PATCH_PASSO_SOMBRIO_V2: invisivel = sem linhas para os outros
			if typeof(inv) == "number" and inv > workspace:GetServerTimeNow() and m:GetAttribute("DonoUserId") ~= lp.UserId then nivel = 0 end
]=====])
  assert(loadstring(src), "RastroBreu_Cliente.client.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ReplicatedStorage.Combate_Dragoes.VFXSombra; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_PASSO_SOMBRIO_V2", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [=====[-- ===== PASSO SOMBRIO (04/11): o dragao se desfaz em breu e reaparece adiante ==========================================
-- sumir: o corpo (e o cavaleiro) some aos poucos (LocalTransparencyModifier, so no cliente), estouro de breu na saida e
-- um rastro de fumaca escura ao longo do caminho; surgir: estouro na chegada e o corpo volta aos poucos. Sem luz.
local function partesVisiveis(m)
	local l = {}
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then table.insert(l, d) end end
	for _, p in ipairs(Players:GetPlayers()) do                         -- quem esta montado some junto
		local ch = p.Character; local hum = ch and ch:FindFirstChildOfClass("Humanoid")
		local sela = hum and hum.SeatPart
		local montado = ch and (sela and sela:IsDescendantOf(m) or (ch:GetAttribute("MontadoEm") == m.Name))
		if not montado and ch and ch:FindFirstChild("HumanoidRootPart") then
			for _, w in ipairs(ch.HumanoidRootPart:GetJoints()) do local o = w.Part0 == ch.HumanoidRootPart and w.Part1 or w.Part0; if o and o:IsDescendantOf(m) then montado = true end end
		end
		if montado then for _, d in ipairs(ch:GetDescendants()) do if d:IsA("BasePart") or d:IsA("Decal") then table.insert(l, d) end end end
	end
	return l
end
local function desvanecer(lista, de, ate, dur)
	local t0 = os.clock(); local c
	c = RunService.RenderStepped:Connect(function()
		local k = math.min(1, (os.clock() - t0) / dur); local v = de + (ate - de) * (k * k * (3 - 2 * k))
		for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = v end end
		if k >= 1 then c:Disconnect() end
	end)
end
local function estouroBreu(pos, f, escala)
	if f <= 0 then return end
	local a = ancora(pos); Debris:AddItem(a, 2.2)
	emissor(a, flipFumaca({Color = seq({PRETO, BREU, C3(55, 20, 95)}), LightEmission = 0.05, LightInfluence = 0.5, Size = ns(0, 4 * escala, 1, 14 * escala),
		Transparency = ns(0, 0.35, 0.5, 0.55, 1, 1), Lifetime = NumberRange.new(0.7, 1.1), Speed = NumberRange.new(14, 26), Drag = 3,
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-60, 60), SpreadAngle = Vector2.new(180, 180), Rate = 0})):Emit(math.max(6, math.floor(26 * f)))
	emissor(a, {Texture = TEX.fumaca, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = seq({PRETO, C3(90, 35, 160)}), LightEmission = 0.1,
		LightInfluence = 0.4, Size = ns(0, 0.8 * escala, 1, 0.2), Squash = ns(0, 1.2, 1, 0.6), Transparency = ns(0, 0.4, 1, 1),
		Lifetime = NumberRange.new(0.35, 0.55), Speed = NumberRange.new(40, 70), Drag = 4, SpreadAngle = Vector2.new(180, 180), Rate = 0}):Emit(math.max(4, math.floor(18 * f)))
end
local function passoEvento(m, d, f)
	local escala = math.clamp((m:GetAttribute("CorpoRaio") or 8) / 8, 0.5, 2)
	if d.fase == "sumir" then
		local lista = partesVisiveis(m); local dur = d.tempo or 0.3
		desvanecer(lista, 0, 1, dur)
		task.delay(dur + 0.05, function() for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = 1 end end end)
		estouroBreu(d.de, f, escala)
		if f > 0 and d.de and d.ate then                                 -- rastro de breu pelo caminho (sombra que corre)
			local v = d.ate - d.de; local n = math.clamp(math.floor(v.Magnitude / 6), 2, 16)
			for i = 1, n do
				task.delay(dur * 0.6 + (i / n) * 0.14, function()
					local a = ancora(d.de + v * (i / n)); Debris:AddItem(a, 1.6)
					emissor(a, flipFumaca({Color = seq({PRETO, BREU}), LightEmission = 0, LightInfluence = 0.5, Size = ns(0, 5 * escala, 1, 9 * escala),
						Transparency = ns(0, 0.45, 0.4, 0.6, 1, 1), Lifetime = NumberRange.new(0.6, 0.9), Speed = NumberRange.new(1, 4), Drag = 2,
						Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30), SpreadAngle = Vector2.new(180, 180), Rate = 0})):Emit(3)
				end)
			end
		end
	elseif d.fase == "surgir" then
		estouroBreu(d.pos, f, escala)
		local lista = partesVisiveis(m)
		desvanecer(lista, 1, 0, d.tempo or 0.35)
		task.delay((d.tempo or 0.35) + 0.1, function() for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = 0 end end end)
	end
end

]=====], [=====[-- ===== PASSO SOMBRIO v2 (04/11, PATCH_PASSO_SOMBRIO_V2): dragao (e cavaleiro) se desfazem em breu por alguns segundos ======================
-- So no cliente (LocalTransparencyModifier). Para os OUTROS somem por completo (sem nome/vida do cavaleiro); para o
-- dono/cavaleiro ficam um vulto (VULTO) para ele continuar se guiando. Estouro de breu ao sumir e ao voltar; o corpo
-- some/volta aos poucos (ENTRA/SAI s). O fim vem do atributo PassoInvisivel (tempo do servidor). Sem luz.
local lpPasso = Players.LocalPlayer
local VULTO, ENTRA, SAI = 0.65, 0.35, 0.45
local passoAtivo = {}
local function invisivelAte(x) local v = x and x.Parent and x:GetAttribute("PassoInvisivel"); return typeof(v) == "number" and v > workspace:GetServerTimeNow() end
local function partesDe(md, l) for _, d in ipairs(md:GetDescendants()) do if d:IsA("BasePart") or d:IsA("Decal") then table.insert(l, d) end end end
local function estouroBreu(pos, f, escala)
	if f <= 0 then return end
	local a = ancora(pos); Debris:AddItem(a, 2.2)
	emissor(a, flipFumaca({Color = seq({PRETO, BREU, C3(55, 20, 95)}), LightEmission = 0.05, LightInfluence = 0.5, Size = ns(0, 4 * escala, 1, 14 * escala),
		Transparency = ns(0, 0.35, 0.5, 0.55, 1, 1), Lifetime = NumberRange.new(0.7, 1.1), Speed = NumberRange.new(14, 26), Drag = 3,
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-60, 60), SpreadAngle = Vector2.new(180, 180), Rate = 0})):Emit(math.max(6, math.floor(26 * f)))
	emissor(a, {Texture = TEX.fumaca, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = seq({PRETO, C3(90, 35, 160)}), LightEmission = 0.1,
		LightInfluence = 0.4, Size = ns(0, 0.8 * escala, 1, 0.2), Squash = ns(0, 1.2, 1, 0.6), Transparency = ns(0, 0.4, 1, 1),
		Lifetime = NumberRange.new(0.35, 0.55), Speed = NumberRange.new(40, 70), Drag = 4, SpreadAngle = Vector2.new(180, 180), Rate = 0}):Emit(math.max(4, math.floor(18 * f)))
end
local function passoEvento(m, d, f)
	local escala = math.clamp((m:GetAttribute("CorpoRaio") or 8) / 8, 0.5, 2)
	local centro = (m.PrimaryPart and m.PrimaryPart.Position) or m:GetPivot().Position
	if d.fase == "fim" then estouroBreu(centro, f, escala); return end
	if d.fase ~= "inicio" then return end
	estouroBreu(centro, f, escala)
	if passoAtivo[m] then return end
	passoAtivo[m] = true
	local cav = typeof(d.cav) == "Instance" and d.cav or nil
	local meu = m:GetAttribute("DonoUserId") == lpPasso.UserId or (cav ~= nil and cav == lpPasso.Character)
	local alvoT = meu and VULTO or 1
	local hum = (not meu) and cav and cav:FindFirstChildOfClass("Humanoid")
	local tipoNome = hum and hum.DisplayDistanceType
	if hum then hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None end   -- nome/vida do cavaleiro somem
	local placas = {}                                                  -- placas (nome/barra de vida) do dragao e do cavaleiro
	if not meu then
		for _, md in ipairs(cav and {m, cav} or {m}) do
			for _, g in ipairs(md:GetDescendants()) do if g:IsA("BillboardGui") and g.Enabled then g.Enabled = false; table.insert(placas, g) end end
		end
	end
	local lista, tLista, k, saindo = {}, -1, 0, false
	local c
	c = RunService.RenderStepped:Connect(function(dt)
		if os.clock() - tLista > 0.5 then                                  -- refaz a lista (acessorios, partes novas)
			lista = {}; partesDe(m, lista); if cav and cav.Parent then partesDe(cav, lista) end; tLista = os.clock()
		end
		if not saindo and not invisivelAte(m) then saindo = true end
		k = saindo and math.max(0, k - dt / SAI) or math.min(1, k + dt / ENTRA)
		local v = alvoT * (k * k * (3 - 2 * k))
		for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = v end end
		if saindo and k <= 0 then
			c:Disconnect(); passoAtivo[m] = nil
			for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = 0 end end
			if hum and hum.Parent then hum.DisplayDistanceType = tipoNome end
			for _, g in ipairs(placas) do if g.Parent then g.Enabled = true end end
		end
	end)
end

]=====])
  assert(loadstring(src), "VFXSombra.luau nao compila"); table.insert(novos, {s, src}) end
if not SS:FindFirstChild("Backup_Passo_Sombrio_v2_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Passo_Sombrio_v2_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f.Parent = SS end
for _, x in ipairs(novos) do x[1].Source = x[2] end
return "aplicado: " .. #novos .. " scripts; backup ServerStorage.Backup_Passo_Sombrio_v2_2026-11-04"
