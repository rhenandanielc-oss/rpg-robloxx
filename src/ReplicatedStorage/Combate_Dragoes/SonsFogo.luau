-- SonsFogo (ModuleScript, ReplicatedStorage.Combate_Dragoes) — AUDIO do Fogo do Dragao das Montanhas (02/11), so no
-- cliente e so cosmetico. Chamado pelo VFXCombate em todo evento de Fogo (antes do LOD visual). Usa o MESMO mixer do
-- SonsGelo (orcamento global, prioridades, laços com fade, limpeza quando o ataque acaba ou e interrompido).
-- Identidade vulcanica: voz do Montanhas (Creature Roar/Lion Guttural), fogo sob pressao (querosene/macarico em laço),
-- lava grave, rajadas de ar gigantes nas batidas, rochas e brasas. So Pro Sound Effects. Volumes NAO_APROVADO.
local TweenService = game:GetService("TweenService")
local Mx = require(script.Parent:WaitForChild("SonsGelo")).mixer
local tocar, emPos, laco, pararLaco, ajustarLaco, pararTudo = Mx.tocar, Mx.emPos, Mx.laco, Mx.pararLaco, Mx.ajustarLaco, Mx.pararTudo
local novoTok, valido, depois, pode, osso, var, sorteia, vivo = Mx.novoTok, Mx.valido, Mx.depois, Mx.pode, Mx.osso, Mx.var, Mx.sorteia, Mx.vivo
local S = {NAO_APROVADO = true}

local function id(n) return "rbxassetid://" .. n end
local B = {
	-- voz (Montanhas)
	grunhido = {id(9125467833), id(9125467848)},                            -- Creature Growls Lion Deep Guttural Rumbling 1 / 3
	inspira = {id(9119305002), id(9119304904)},                             -- Sniff Breathe In 2 / 1 (tom baixo = peito grande)
	expira = {id(9113971433), id(9113972148)},                              -- Creature Growls Lion 2 / 7: breathy
	rugidoCurto = id(9113985604),                                           -- Creature Roar Mix Of Animals 1 (3,3 s)
	rugidoVulcao = id(9120030507),                                          -- Thunder With Lion Roar Searing Blast 4 (5,4 s)
	-- fogo
	chamaLaco = id(9112780561),                                             -- Fire Whoosh 1: kerosene, flaring, loop (49 s)
	lavaGrave = id(9112822943), lavaGraveB = id(9112822944),                -- Lava Fire Deep Rumbling 2 / 1 (loops)
	macarico = {id(9114446277), id(9114446802)},                            -- Fire Whoosh 6 / 13: torch starts
	rajadaFogo = {id(9114444052), id(9114444008), id(9114442751)},          -- Fire Whoosh 5 / 3 / 2: punchy bursts
	ondaChama = {id(9114430091), id(9114429180)},                           -- Fire Burst 2 / 6: wave of flame
	arQuente = id(9114431819),                                              -- Fire Burst 6: ascending air release
	chiado = id(9114439212),                                                -- Fire Whoosh 1: searing burst, hissing
	lambidas = id(9114463219),                                              -- Flame Licks 8: crepitar curto
	-- ar
	pressao = {id(9125577419), id(9125577695), id(9125577249), id(9125577210), id(9125577719), id(9125577652)},   -- Giant Air Blast Low Burst
	fole = id(9113050274),                                                  -- Air Blast Mechanical Bellows Growly Rumble (turbulencia)
	subida = id(9125805579), avanco = id(9126229255),                       -- Rising Whoosh / Whoosh By Fast Airy
	-- rocha e corpo
	rochas = {id(9125871199), id(9118630399), id(9117372203)},              -- Throwing Stones / Bone Hits Rock Debris / Pile Rocks
	rochaGrande = id(9118627392), rochaGrave = id(9118633669),              -- Big Bone Hits Rock / Deep Crunchy Hits
	lavaRochas = id(9112823563),                                            -- Lava Rumble 2: rocks, violent (loop)
	mordida = {id(9125467298), id(9125466463)},                             -- Creature Bite Pterodactyl Crunch
	asa = {id(9120771864), id(9120776877)},                                 -- Wing Flaps: Large Flying Creature
	-- rugidos (PATCH_RUGIDOS_FOGO): combate curto e feroz / aereo poderoso; rosnado de preparo
	rugCombate = id(9113980319), rugCombateB = id(9113985445),             -- Giant Crab Monster Roar Growl 1 / Creature Roar Deep Throaty 2
	rugAereo = id(9113985604), rugAereoCorpo = id(9113987603),              -- Creature Roar Mix Of Animals 1 / Giant Crab Monster Roars 1
	rosnado = {id(9113973520), id(9113973748)},                             -- Creature Growls Pit Bull 4 / 3
}
S.BANCO = B
local function peito(m) return osso(m, "Coluna2") or osso(m, "spine_0") or m.PrimaryPart end
local function cabeca(m) return osso(m, "Cabeca") or m.PrimaryPart end
local function bocaO(m) return osso(m, "mouth_upper_tip") or cabeca(m) end

-- ===== SOPRO DRACONICO: preparo (inspiracao, calor acumulando, estalos) -> emissao: rajada de macarico no ataque e
-- LACO continuo (fogo sob pressao + ronco de combustao + turbulencia) com variacao lenta de intensidade -> impacto em
-- laço no ponto atingido -> fim suave e expiracao. Nunca reinicia o arquivo enquanto segura.
local impacto = setmetatable({}, {__mode = "k"})
local function sopro(m, d)
	local b = bocaO(m)
	if d.fase == "preparo" then
		local t = novoTok(m, "SoproF")
		tocar(b, sorteia(B.inspira), {vol = 0.95, tom = var(0.45, 0.04), corte = 1.3, dist = 150, prio = 3})
		laco(m, "soproPrep", peito(m), B.lavaGrave, {vol = 0.6, tom = 0.7, fadeIn = 0.9, corte = 2.2, dist = 200})
		depois(m, "SoproF", t, 0.55, function() tocar(b, B.lambidas, {vol = 0.35, tom = var(1.2, 0.08), corte = 0.6, dist = 110}) end)
		depois(m, "SoproF", t, 0.85, function() tocar(b, B.lambidas, {vol = 0.45, tom = var(1.05, 0.08), corte = 0.6, dist = 110}) end)
	elseif d.fase == "emissao" then
		local t = novoTok(m, "SoproF")
		pararLaco(m, "soproPrep", 0.25); pararLaco(m, "sopro", 0.1)
		local lim = math.max(d.duracao or 1.8, 6) + 1.5
		tocar(b, sorteia(B.macarico), {vol = 1.0, tom = var(0.7, 0.04), corte = 1.1, fadeOut = 0.4, dist = 240, prio = 4})
		laco(m, "sopro", b, B.chamaLaco, {vol = 0.95, tom = var(0.78, 0.03), fadeIn = 0.15, corte = lim, dist = 250, prio = 4})
		laco(m, "sopro", b, B.lavaGrave, {vol = 0.55, tom = var(0.9, 0.03), fadeIn = 0.3, corte = lim, dist = 220})
		laco(m, "sopro", b, B.fole, {vol = 0.3, tom = var(0.8, 0.04), fadeIn = 0.4, corte = lim, dist = 160})
		-- variacao natural de intensidade (respiracao do fluxo), lenta e suave
		task.spawn(function()
			while valido(m, "SoproF", t) do
				local r = 0.88 + math.random() * 0.24                       -- sobe/desce e volta ao mesmo nivel (sem deriva)
				ajustarLaco(m, "sopro", r, nil, 0.7); task.wait(0.7)
				if not valido(m, "SoproF", t) then break end
				ajustarLaco(m, "sopro", 1 / r, nil, 0.7); task.wait(0.7)
			end
		end)
		local a = Instance.new("Attachment"); a.Name = "Som_SoproFogoImpacto"; a.WorldPosition = m:GetPivot().Position; a.Parent = workspace.Terrain
		game:GetService("Debris"):AddItem(a, lim + 1)
		impacto[m] = {a = a, ativo = false}
		laco(m, "sopro", a, B.chamaLaco, {vol = 0, tom = 1.15, corte = lim, dist = 180})
		laco(m, "sopro", a, B.lavaGraveB, {vol = 0, tom = 1.2, corte = lim, dist = 160})
	elseif d.fase == "fim" then
		novoTok(m, "SoproF")
		pararLaco(m, "soproPrep", 0.2); pararLaco(m, "sopro", 0.6)
		local ip = impacto[m]; impacto[m] = nil
		if ip and vivo(ip.a) then emPos(ip.a.WorldPosition, B.lambidas, {vol = 0.35, tom = var(0.9, 0.08), corte = 1.2, fadeOut = 0.6, dist = 130}) end
		tocar(cabeca(m), sorteia(B.expira), {vol = 0.6, tom = var(0.7, 0.04), corte = 1.8, fadeOut = 0.6, dist = 110})
	end
end
function S.soproImpacto(m, pos)
	local ip = impacto[m]; if not ip or not vivo(ip.a) then return end
	local bateu = pos ~= nil
	if pos then ip.a.WorldPosition = pos end
	if bateu ~= ip.ativo then
		ip.ativo = bateu
		for _, s in ipairs(ip.a:GetChildren()) do
			if s:IsA("Sound") then TweenService:Create(s, TweenInfo.new(0.25), {Volume = bateu and (s.SoundId == B.chamaLaco and 0.5 or 0.45) or 0}):Play() end
		end
	end
	if bateu and pode(m, "soproEstalo", 0.6 + math.random() * 0.5) then
		emPos(pos, B.lambidas, {vol = 0.4, tom = var(1.1, 0.1), corte = 0.8, dist = 140})
	end
end

-- ===== ARREMETIDA (5 s): preparo (grunhido + calor) -> aceleracao: vento crescendo com a velocidade real + chamas
-- acompanhando (laço) + batida forte no ar -> mordida/impacto grave com explosao ignea -> fim: vento e chamas caem,
-- respiracao. O volume do vento segue o atributo Velocidade (o mesmo do controlador).
local function arremetida(m, d)
	local pp = m.PrimaryPart
	if d.fase == "preparo" then
		local t = novoTok(m, "Arr")
		tocar(cabeca(m), sorteia(B.grunhido), {vol = 0.85, tom = var(0.85, 0.04), corte = 1.3, dist = 200, prio = 4})
		tocar(peito(m), sorteia(B.macarico), {vol = 0.45, tom = var(0.6, 0.04), corte = 0.9, fadeOut = 0.4, dist = 160})
		if d.noAr then
			tocar(peito(m), B.asa[2], {vol = 1.4, tom = var(0.6, 0.04), corte = 1.2, dist = 220, prio = 4})
			tocar(peito(m), sorteia(B.pressao), {vol = 0.6, tom = var(0.95, 0.04), corte = 1.0, fadeOut = 0.4, dist = 220})
		end
		local dur = d.duracao or 5
		laco(m, "arr", pp, B.fole, {vol = 0.0, tom = 0.8, corte = dur + 1.5, dist = 220, prio = 3})
		laco(m, "arr", pp, B.chamaLaco, {vol = 0.0, tom = 0.9, corte = dur + 1.5, dist = 200, prio = 3})
		task.spawn(function()                                              -- vento/chamas pela velocidade
			while valido(m, "Arr", t) do
				local v = m:GetAttribute("Velocidade") or 0; local k = math.clamp(v / 70, 0, 1)
				for _, s in ipairs(pp:GetChildren()) do
					if s:IsA("Sound") and s.Looped and (s.SoundId == B.fole or s.SoundId == B.chamaLaco) then
						local alvoV = s.SoundId == B.fole and 0.15 + 0.85 * k or 0.1 + 0.5 * k
						s.Volume += (alvoV - s.Volume) * 0.35; s.PlaybackSpeed += ((0.75 + 0.45 * k) - s.PlaybackSpeed) * 0.3
					end
				end
				task.wait(0.1)
			end
		end)
	elseif d.fase == "mordida" then
		tocar(cabeca(m), sorteia(B.rajadaFogo), {vol = 0.55, tom = var(0.8, 0.05), corte = 0.7, dist = 180})
	elseif d.fase == "impacto" then
		local p = d.pos or pp.Position
		emPos(p, sorteia(B.mordida), {vol = 1.4, tom = var(0.62, 0.04), corte = 0.6, dist = 240, prio = 5})
		emPos(p, B.rochaGrande, {vol = 1.1, tom = var(0.6, 0.04), corte = 0.7, dist = 240, prio = 5})
		emPos(p, sorteia(B.ondaChama), {vol = 0.85, tom = var(0.9, 0.05), corte = 1.4, fadeOut = 0.6, dist = 260, prio = 4})
		emPos(p, sorteia(B.pressao), {vol = 0.5, tom = var(1.1, 0.05), corte = 0.8, fadeOut = 0.3, dist = 220})
	elseif d.fase == "fim" then
		novoTok(m, "Arr")
		pararLaco(m, "arr", 1.0)
		task.delay(0.5, function() if vivo(m) then tocar(cabeca(m), sorteia(B.expira), {vol = 0.55, tom = var(0.75, 0.04), corte = 1.8, fadeOut = 0.5, dist = 110}) end end)
	end
end

-- ===== TEMPESTADE DE ASAS: decolagem (impulso das patas, batida alar, ar) -> cada batida REAL: onda grave de pressao
-- (variada) + ar quente/turbulencia + rochas levantadas e se chocando + combustao de brasas + impacto nos inimigos ->
-- leito continuo de lava/rochas e fole durante a tempestade -> dissipacao e pouso.
local function tempestade(m, d)
	local c = peito(m)
	if d.fase == "preparo" then
		local t = novoTok(m, "Temp")
		tocar(cabeca(m), sorteia(B.grunhido), {vol = 0.7, tom = var(0.8, 0.04), corte = 1.4, dist = 200, prio = 3})
		tocar(cabeca(m), sorteia(B.inspira), {vol = 0.7, tom = var(0.5, 0.04), corte = 1.2, dist = 120})
		local dur = d.duracao or 5.5
		laco(m, "temp", c, B.fole, {vol = 0.5, tom = 0.75, fadeIn = 1.2, corte = dur + 0.8, fadeOut = 1.0, dist = 260})
		laco(m, "temp", c, B.lavaRochas, {vol = 0.35, tom = 0.9, fadeIn = 1.5, corte = dur + 0.8, fadeOut = 1.0, dist = 240})
		if d.noAr then tocar(c, sorteia(B.asa), {vol = 1.3, tom = var(0.65, 0.04), corte = 1.0, dist = 220}) end
	elseif d.fase == "impulso" then
		local p = d.pos or m:GetPivot().Position
		emPos(p, B.rochaGrave, {vol = 0.9, tom = var(0.7, 0.04), corte = 0.9, fadeOut = 0.3, dist = 220, prio = 4})
		tocar(c, B.asa[2], {vol = 1.5, tom = var(0.55, 0.03), corte = 1.2, dist = 260, prio = 4})
		tocar(c, B.subida, {vol = 0.8, tom = var(0.7, 0.04), corte = 1.0, dist = 200})
	elseif d.fase == "batida" then
		local i = d.indice or 1; local k = i == 1 and 1 or 0.8
		local p = d.pos or m:GetPivot().Position
		-- onda grave de pressao: arquivo e tom diferentes a cada batida (nada de repeticao identica)
		tocar(c, B.pressao[(i - 1) % #B.pressao + 1], {vol = 1.3 * k, tom = var(0.62 + 0.04 * (i % 3), 0.03), corte = 1.4, fadeOut = 0.5, dist = 340, min = 25, prio = 5})
		tocar(c, B.asa[1], {vol = 1.2 * k, tom = var(0.55, 0.05), corte = 0.7, dist = 240, prio = 3})
		emPos(p + Vector3.new(0, 4, 0), B.arQuente, {vol = 0.7 * k, tom = var(0.85, 0.05), corte = 1.2, fadeOut = 0.5, dist = 260, prio = 3})
		if d.superficie then
			task.delay(0.1, function() emPos(p, sorteia(B.rochas), {vol = 0.9 * k, tom = var(0.8, 0.08), corte = 1.6, dist = 220, prio = 3}) end)
			task.delay(0.35 + math.random() * 0.15, function() emPos(p + Vector3.new(math.random(-20, 20), 0, math.random(-20, 20)), sorteia(B.rochas), {vol = 0.55 * k, tom = var(1.0, 0.1), corte = 1.2, dist = 180, prio = 2}) end)
		end
		task.delay(0.15, function() emPos(p + Vector3.new(0, 3, 0), sorteia(B.rajadaFogo), {vol = 0.45 * k, tom = var(0.75, 0.06), corte = 0.9, dist = 200, prio = 2}) end)
		if (d.alvos or 0) > 0 then tocar(c, B.rochaGrande, {vol = 0.6, tom = var(0.7, 0.05), corte = 0.6, dist = 200, prio = 3}) end
		if d.total and i >= d.total then pararLaco(m, "temp", 1.4) end    -- dissipacao depois da ultima batida
	elseif d.fase == "pouso" then
		local p = d.pos or m:GetPivot().Position
		emPos(p, B.rochaGrave, {vol = 0.8, tom = var(0.75, 0.04), corte = 0.9, fadeOut = 0.3, dist = 200, prio = 3})
		tocar(cabeca(m), sorteia(B.expira), {vol = 0.55, tom = var(0.72, 0.04), corte = 1.8, fadeOut = 0.5, dist = 110})
	end
end

-- ===== CORACAO INFERNAL: carga (pulso grave, calor e vibracao vulcanica crescendo) -> espada expelida (combustao
-- concentrada + rugido curto + energia liberada) -> giro: chama cortando o ar presa a PONTA da lamina (anda com ela;
-- volume/tom pela velocidade angular, mesma funcao de angulo do servidor) -> impactos igneos -> dissipacao.
local function coracaoEstado(d, t)
	if t < 0 then return 0, 0, false end
	if t <= d.expele then local k = t / d.expele; return 0, 1 - (1 - k) ^ 3, true end
	local k = math.clamp((t - d.expele) / d.giro, 0, 1)
	return d.sentido * 2 * math.pi * d.voltas * (k * k * (3 - 2 * k)), 1, t <= d.expele + d.giro
end
local function coracao(m, d)
	if d.fase == "carga" then
		local t = novoTok(m, "Cor")
		local dur = d.carga or 1.1
		laco(m, "corCarga", peito(m), B.lavaGraveB, {vol = 1.0, tom = 0.6, fadeIn = dur, corte = dur + 0.5, fadeOut = 0.3, dist = 260})
		ajustarLaco(m, "corCarga", nil, 1.3, dur)
		tocar(peito(m), sorteia(B.pressao), {vol = 0.55, tom = 0.45, corte = 1.2, fadeIn = dur * 0.6, fadeOut = 0.3, dist = 240})
		tocar(cabeca(m), sorteia(B.grunhido), {vol = 0.7, tom = var(0.7, 0.04), corte = dur, dist = 180})
	elseif d.fase == "lamina" then
		local t = novoTok(m, "Cor")
		pararLaco(m, "corCarga", 0.15)
		local b = bocaO(m)
		tocar(b, B.chiado, {vol = 1.1, tom = var(0.8, 0.03), corte = 1.2, fadeOut = 0.5, dist = 300, prio = 5})
		tocar(cabeca(m), B.rugidoVulcao, {vol = 1.1, tom = var(0.85, 0.03), corte = 1.5, fadeOut = 0.6, dist = 340, min = 25, prio = 5})
		tocar(b, sorteia(B.macarico), {vol = 0.8, tom = var(0.55, 0.04), corte = 0.9, dist = 220})
		-- chama cortando o ar presa a ponta da lamina (anda com ela)
		local a = Instance.new("Attachment"); a.Parent = workspace.Terrain; game:GetService("Debris"):AddItem(a, d.expele + d.giro + d.dissipa + 1)
		a.WorldPosition = b:IsA("Attachment") and b.WorldPosition or m:GetPivot().Position   -- nasce na boca (o corte por distancia usa a posicao)
		local r = laco(m, "corLamina", a, B.chamaLaco, {vol = 0.2, tom = 0.9, corte = d.expele + d.giro + d.dissipa + 0.5, fadeOut = 0.5, dist = 260, prio = 4})
		local r2 = laco(m, "corLamina", a, B.fole, {vol = 0.1, tom = 1.0, corte = d.expele + d.giro + d.dissipa + 0.5, fadeOut = 0.5, dist = 200})
		local angAnt, tAnt = 0, workspace:GetServerTimeNow() - d.t0
		task.spawn(function()
			while valido(m, "Cor", t) do
				local tt = workspace:GetServerTimeNow() - d.t0
				if tt > d.expele + d.giro + d.dissipa then break end
				local ang, ext = coracaoEstado(d, math.min(tt, d.expele + d.giro))
				local cpos = (osso(m, "Coluna2") and (osso(m, "Coluna2").TransformedWorldCFrame.Position)) or m:GetPivot().Position
				local dir = CFrame.Angles(0, ang, 0):VectorToWorldSpace(d.dir0)
				a.WorldPosition = Vector3.new(cpos.X, cpos.Y + (d.dy or 0), cpos.Z) + dir * (d.rIn + (d.rOut - d.rIn) * ext)
				local w = math.abs(ang - angAnt) / math.max(tt - tAnt, 1 / 60); angAnt, tAnt = ang, tt
				local k = math.clamp(w / 7, 0, 1)
				local fade = tt > d.expele + d.giro and math.max(0, 1 - (tt - d.expele - d.giro) / d.dissipa) or 1
				for _, x in ipairs({r, r2}) do
					if x and vivo(x.s) then x.s.Volume = (x == r and (0.35 + 0.75 * k) or (0.15 + 0.6 * k)) * fade; x.s.PlaybackSpeed = (x == r and 0.8 or 0.9) + 0.4 * k end
				end
				task.wait(0.05)
			end
			pararLaco(m, "corLamina", 0.4)
			if vivo(m) then tocar(peito(m), B.lambidas, {vol = 0.4, tom = var(0.85, 0.06), corte = 1.2, fadeOut = 0.6, dist = 130}) end
		end)
	elseif d.fase == "impacto" then
		local p = d.pos or m:GetPivot().Position
		emPos(p, sorteia(B.rajadaFogo), {vol = 0.9, tom = var(0.85, 0.06), corte = 0.9, dist = 220, prio = 4})
		emPos(p, sorteia(B.ondaChama), {vol = 0.5, tom = var(1.1, 0.05), corte = 0.9, fadeOut = 0.4, dist = 200})
	end
end

-- ===== RUGIDO de combate (solo/andando) e AEREO: rosnado curto no preparo -> no instante da emissao (marcador do
-- Nucleo, boca abrindo) a voz + corpo grave em camadas; bafo quente baixo no fim. Volume moderado, alcance de rugido.
local function rugido(m, d)
	local cab = cabeca(m)
	if d.fase == "preparo" then
		novoTok(m, "Rug")
		tocar(cab, sorteia(B.rosnado), {vol = 0.55, tom = var(0.75, 0.04), corte = 0.6, fadeOut = 0.2, dist = 160, prio = 3})
	elseif d.fase == "emissao" then
		if d.tipo == "aereo" then
			tocar(cab, B.rugAereo, {vol = 1.1, tom = var(0.74, 0.03), corte = 2.0, fadeOut = 0.6, dist = 360, min = 25, prio = 5})
			tocar(cab, B.rugAereoCorpo, {vol = 0.5, tom = var(0.7, 0.03), corte = 1.8, fadeOut = 0.6, dist = 300, min = 25, prio = 4})
		else
			tocar(cab, B.rugCombate, {vol = 1.05, tom = var(0.82, 0.04), corte = 1.2, fadeOut = 0.45, dist = 340, min = 22, prio = 5})
			tocar(cab, B.rugCombateB, {vol = 0.55, tom = var(0.9, 0.04), corte = 1.0, fadeOut = 0.4, dist = 300, min = 22, prio = 4})
		end
		task.delay(d.tipo == "aereo" and 1.6 or 1.0, function()
			if vivo(m) then tocar(bocaO(m), B.arQuente, {vol = 0.18, tom = 0.85, corte = 1.0, fadeIn = 0.1, fadeOut = 0.5, dist = 90}) end
		end)
	end
end

-- ===== passiva: Sangue de Magma (so na ativacao, discreto) ======================================================
local function sangue(m)
	tocar(peito(m), B.lavaGraveB, {vol = 0.5, tom = 0.7, corte = 1.6, fadeIn = 0.3, fadeOut = 0.8, dist = 140})
	tocar(cabeca(m), sorteia(B.grunhido), {vol = 0.45, tom = var(0.75, 0.05), corte = 1.0, dist = 150})
end

function S.evento(d)
	local m = d.d; if not (vivo(m) and m.PrimaryPart) then return end
	Mx.vigiar(m)
	if d.hab == "Sopro" then sopro(m, d)
	elseif d.hab == "Arremetida" then arremetida(m, d)
	elseif d.hab == "Tempestade" then tempestade(m, d)
	elseif d.hab == "Coracao" then coracao(m, d)
	elseif d.hab == "SangueDeMagma" and d.fase == "ativar" then sangue(m)
	elseif d.hab == "Rugido" then rugido(m, d) end
end
return S
