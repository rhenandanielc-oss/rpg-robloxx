-- SonsGelo (ModuleScript, ReplicatedStorage.Combate_Dragoes) — AUDIO do kit de Gelo do Dragao Glacial (02/11), so no
-- cliente e so cosmetico (nada aqui altera dano, recarga, alcance ou alvos). Chamado pelo VFXGelo nos MESMOS instantes
-- dos efeitos (eventos do servidor + tempos ja usados pelo visual), inclusive alem da distancia do LOD visual.
-- Identidade sonora propria (nao e o Montanhas): voz de felino grande grave e cansada (leao "tired/pitched down"),
-- gelo = vidro/gelo real (racha, estala, estilhaca, pedacos caindo), sopro = vento sob pressao + ronco grave + estalos
-- em LACO continuo (nada de reiniciar o arquivo a cada segundo).
-- Audio: SO biblioteca Pro Sound Effects publicada na Roblox ("Courtesy of Pro Sound Effects", conta ProSoundEffects).
-- Mixagem: 3D (InverseTapered), alcance por categoria, limite global e por dragao com PRIORIDADE (um som importante
-- tira o menos importante), variacao de tom, laços com fade in/out e limpeza quando o poder e interrompido.
-- Volumes/tons provisorios (NAO_APROVADO).
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local S = {NAO_APROVADO = true}
local INICIO = require(game:GetService("ReplicatedStorage"):WaitForChild("Montaria_Dragoes"):WaitForChild("SonsConfig")).inicioAudivel or {}
-- PATCH_RUGIDO_SEM_ATRASO: um Sound criado na hora leva ~0,17 s para comecar a soar (medido no Studio); um ja criado
-- e parado ha alguns decimos, ~0,03 s. Cada rugido (SonsConfig.inicioAudivel) fica com UM Sound "aquecido" em
-- SoundService (mudo, parado); ao tocar ele e movido para a cabeca e outro e aquecido para a proxima vez.
local SoundService = game:GetService("SoundService")
local aquecidos = {}
local function aquecer(sid)
	if aquecidos[sid] then return end
	local s = Instance.new("Sound"); s.Name = "Aquecido"; s.SoundId = sid; s.Volume = 0; s.Parent = SoundService
	aquecidos[sid] = s
end
local function novoSom(sid)
	local s = aquecidos[sid]
	if s and s.Parent == SoundService then aquecidos[sid] = nil; aquecer(sid); return s end
	s = Instance.new("Sound"); s.SoundId = sid; return s
end
if game:GetService("RunService"):IsClient() then for n in pairs(INICIO) do aquecer("rbxassetid://" .. n) end end
S.novoSom = novoSom

local function id(n) return "rbxassetid://" .. n end
-- banco (duracao real conferida no Studio em 02/11)
local B = {
	-- voz (felino grande, grave): rugido ancestral, rugido combate, grunhidos
	rugidoAncestral = id(9116300504),                                       -- Lion Roar Growl Exhale Low Rumble Breath 1 (5,8 s)
	rugidoCorpo = id(9116306862),                                           -- Lion Roar Tired 3: pitched down, large (3,9 s)
	esforco = {id(9125470306), id(9125470501)},                             -- Creature Growls Lion Deep Guttural Rumbling 7 / 11
	expira = {id(9113972744), id(9113971975)},                              -- Creature Growls Lion 20 / 6: breathy, tubular ticking
	respiroLongo = id(9113972534),                                          -- Creature Growls Lion 16: breathy (6,5 s)
	inspira = {id(9119305128), id(9119305469)},                             -- Sniff Breathe In 4 / 9
	-- ar e energia
	vento = id(9125742262), ventoB = id(9125742111),                        -- Plasma Trails Constant Airy Whooshing Windy 2 / 1 (33 / 18 s)
	ronco = id(9125443744), roncoB = id(9125443949),                        -- Clouds Swirl Steamy Rumble Churning 1 / 2 (36 s)
	sopro = id(9126167059),                                                 -- Vocal Wind Blowing Air Through Lips Less Cold (3,9 s)
	pressao = id(9114437277), pressaoCurta = id(9114437231),                -- Fire Extinguisher 2 / 1: rajada fria sob pressao
	grave = id(9119661508),                                                 -- Sub Boom Slapback Element 2: SO o corpo grave (cortado)
	corte = {id(9125648149), id(9125648137), id(9125648134)},               -- Magic Zoom Up Sharp Tubular Whoosh: lanca/fragmento cortando o ar
	deslocamento = id(9125647922),                                          -- Magic Zoom Up (1,2 s): ar deslocado
	-- gelo
	cristais = id(9114858178), cristaisB = id(9114858364),                  -- Ice Crack And Sizzle 1 / 3 (estalos pequenos continuos)
	granulos = id(9114862037),                                              -- Ice Cube Movement 2: textura de particulas (crunch)
	estalo = id(9114590476),                                                -- Glass Break: thin plate (estalo cristalino forte)
	tinido = id(9114590297),                                                -- Glass Break: pequeno (estalos/residuo)
	estilhaco = {id(9114591164), id(9114590269)},                           -- Glass Break 9 (shards) / 1 (crash shatter)
	rachar = id(9118762653), racharLongo = id(9118762668),                  -- Safety Glass slow cracking (4,8 / 7,8 s)
	pedacos = {id(9125610574), id(9125610305)},                             -- Ice Break Small Pieces Fall To Concrete 2 / 1
	baque = id(9114861568),                                                 -- Ice Cube Drops: golpe seco
	neveBaque = id(9119316414),                                             -- Snow Impact Big Hits Semi-Deep
	-- asas (membrana pesada)
	asa = {id(9114461411), id(9114461597), id(9114461307)},                 -- Flag Flapping 3 (cloth flutter): batida de membrana
}
S.BANCO = B

-- ===== mixer ======================================================================================================
local MAX_GLOBAL, MAX_POR_PAI = 26, 7
local ativos = {}                                   -- {s = Sound, prio = n, pai = Instance}
local porPai = setmetatable({}, {__mode = "k"})
local cam = workspace.CurrentCamera
local function vivo(x) return x and x.Parent ~= nil end
local function remover(reg)
	for i, r in ipairs(ativos) do if r == reg then table.remove(ativos, i); break end end
	if reg.pai then porPai[reg.pai] = math.max(0, (porPai[reg.pai] or 1) - 1) end
end
local function desligar(reg, fade, suave)
	if reg.morto then return end
	reg.morto = true; remover(reg)
	local s = reg.s
	if vivo(s) then
		-- rugido: saida em Sine Out (cai devagar e se apaga), nao em Quad In (que segura e despenca no fim)
		local estilo = suave and Enum.EasingStyle.Sine or Enum.EasingStyle.Quad
		local dir = suave and Enum.EasingDirection.Out or Enum.EasingDirection.In
		if fade and fade > 0 then TweenService:Create(s, TweenInfo.new(fade, estilo, dir), {Volume = 0}):Play(); Debris:AddItem(s, fade + 0.05)
		else s:Stop(); s:Destroy() end
	end
end
local function posDe(pai)
	if pai:IsA("Attachment") then return pai.WorldPosition elseif pai:IsA("BasePart") then return pai.Position end
end
-- o = {vol, tom, corte (s), dist (alcance max), prio (1 baixo .. 5 rugido), fadeIn, fadeOut, laco, ini (TimePosition),
--      pos (posicao para o corte por distancia, quando o pai ainda nao foi posicionado)}
-- PATCH_RUGIDO_NATURAL (02/11): envelope de rugido - COMECA (entrada de ~0,2 s, tom um pouco abaixo), MUDA DE TOM
-- (sobe ate o pico aos 35% e cai no fim, como o folego acabando) e TERMINA diminuindo (saida longa, ~40% do tempo):
-- nada de cortar seco. Uso: o.rugido = true (o.corte = duracao total).
local function envelopeRugido(s, tom, dur)
	s.PlaybackSpeed = tom * 0.93
	TweenService:Create(s, TweenInfo.new(dur * 0.35, Enum.EasingStyle.Sine, Enum.EasingDirection.Out), {PlaybackSpeed = tom * 1.04}):Play()
	task.delay(dur * 0.35, function()
		if s.Parent then TweenService:Create(s, TweenInfo.new(dur * 0.65, Enum.EasingStyle.Sine, Enum.EasingDirection.In), {PlaybackSpeed = tom * 0.86}):Play() end
	end)
end
local function tocar(pai, sid, o)
	o = o or {}
	-- PATCH_RUGIDO_SEM_ATRASO: pula o comeco quase mudo do arquivo (SonsConfig.inicioAudivel) -> o som sai junto com a boca
	local ini = INICIO[tostring(sid):match("%d+") or ""]
	if ini and not o.ini then o.ini = ini; if o.corte then o.corte = math.max(0.8, o.corte - ini / (o.tom or 1)) end end
	if o.rugido then                                                    -- entrada e saida do envelope (ver acima)
		local dur = o.corte or 3
		o.fadeIn = o.fadeIn or math.min(0.06, dur * 0.05)                 -- entrada curta: ja comeca no trecho audivel
		o.fadeOut = math.max(o.fadeOut or 0, dur * 0.4, 0.6)
	end
	if not (vivo(pai) and sid) then return end
	cam = workspace.CurrentCamera
	local dist = o.dist or 240
	local p = o.pos or posDe(pai); if p and cam and (p - cam.CFrame.Position).Magnitude > dist then return end   -- fora do alcance: nem cria
	local prio = o.prio or 2
	if (porPai[pai] or 0) >= MAX_POR_PAI and not o.laco then return end
	if #ativos >= MAX_GLOBAL then                                        -- cheio: tira o de menor prioridade (se for menor)
		local pior, pi = nil, prio
		for _, r in ipairs(ativos) do if not r.laco and r.prio < pi then pior, pi = r, r.prio end end
		if not pior then return end
		desligar(pior, 0.12)
	end
	local s = novoSom(sid); s.PlaybackSpeed = o.tom or 1; s.Looped = o.laco == true
	s.RollOffMode = Enum.RollOffMode.InverseTapered; s.RollOffMinDistance = o.min or 14; s.RollOffMaxDistance = dist
	local vol = o.vol or 1
	s.Volume = (o.fadeIn and o.fadeIn > 0) and 0 or vol
	if o.ini then s.TimePosition = o.ini end
	s.Parent = pai; s:Play()
	if o.fadeIn and o.fadeIn > 0 then TweenService:Create(s, TweenInfo.new(o.fadeIn, Enum.EasingStyle.Sine, Enum.EasingDirection.Out), {Volume = vol}):Play() end
	if o.rugido then envelopeRugido(s, o.tom or 1, o.corte or 3) end
	local reg = {s = s, prio = prio, pai = pai, laco = o.laco, vol = vol, tom = o.tom or 1}
	table.insert(ativos, reg); porPai[pai] = (porPai[pai] or 0) + 1
	if o.laco then
		if o.corte then task.delay(o.corte, function() desligar(reg, o.fadeOut or 0.4) end) end   -- trava de seguranca
	else
		local fim = o.corte or 6
		task.delay(math.max(0.05, fim - (o.fadeOut or 0.2)), function() desligar(reg, o.fadeOut or 0.2, o.rugido) end)
		s.Ended:Once(function() desligar(reg, 0) end)
	end
	s.AncestryChanged:Connect(function() if not s:IsDescendantOf(game) then desligar(reg, 0) end end)
	return reg
end
local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end
local function var(t, v) return (t or 1) * (1 + (math.random() * 2 - 1) * (v or 0.05)) end
local function ancora(pos, vida) local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain; Debris:AddItem(a, vida or 6); return a end
local function emPos(pos, sid, o) o = o or {}; return tocar(ancora(pos, (o.corte or 4) + 0.6), sid, o) end
local function tomVoz(m) return (m and m:GetAttribute("TomVoz")) or 1 end
local function ossoDe(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end
local cacheOsso = setmetatable({}, {__mode = "k"})
local function osso(m, nome)
	cacheOsso[m] = cacheOsso[m] or {}
	local b = cacheOsso[m][nome]; if vivo(b) then return b end
	b = ossoDe(m, nome); cacheOsso[m][nome] = b; return b
end
local function bocaDe(m) return osso(m, "mouth_upper_tip") or osso(m, "Cabeca") or m.PrimaryPart end
local function cabecaDe(m) return osso(m, "Cabeca") or m.PrimaryPart end
local function peitoDe(m) return osso(m, "Coluna2") or osso(m, "Coluna3") or m.PrimaryPart end
-- limite de frequencia por chave (agrupa: muitos fragmentos = poucas camadas de som)
local ultimo = setmetatable({}, {__mode = "k"})
local function pode(m, chave, intervalo)
	ultimo[m] = ultimo[m] or {}
	if os.clock() - (ultimo[m][chave] or -99) < intervalo then return false end
	ultimo[m][chave] = os.clock(); return true
end

-- laços nomeados por dragao (sopro, carga, tempestade...): param juntos com fade; limpos na interrupcao
local lacos = setmetatable({}, {__mode = "k"})
local function laco(m, nome, pai, sid, o)
	lacos[m] = lacos[m] or {}; lacos[m][nome] = lacos[m][nome] or {}
	o = o or {}; o.laco = true; o.corte = o.corte or 9; o.prio = o.prio or 3
	if o.ini == nil then o.ini = math.random() * 4 end                   -- ponto de partida variado: nao soa igual a cada uso
	local r = tocar(pai, sid, o); if r then table.insert(lacos[m][nome], r) end
	return r
end
local function pararLaco(m, nome, fade)
	local l = lacos[m] and lacos[m][nome]; if not l then return end
	lacos[m][nome] = nil
	for _, r in ipairs(l) do desligar(r, fade or 0.5) end
end
local function ajustarLaco(m, nome, vol, tom, dur)
	local l = lacos[m] and lacos[m][nome]; if not l then return end
	for _, r in ipairs(l) do
		if vivo(r.s) and not r.morto then                                -- sobre o valor-BASE (um fade-in em curso nao zera o ajuste)
			local alvo = {}
			if vol then r.vol *= vol; alvo.Volume = r.vol end
			if tom then r.tom *= tom; alvo.PlaybackSpeed = r.tom end
			TweenService:Create(r.s, TweenInfo.new(dur or 0.5, Enum.EasingStyle.Sine), alvo):Play()
		end
	end
end
local function pararTudo(m, fade) if lacos[m] then for nome in pairs(lacos[m]) do pararLaco(m, nome, fade) end end end
S.pararTudo = pararTudo

-- interrupcao: se o ataque acabou (EmAtaque limpo) e um laço de poder ficou tocando, apaga; dragao removido = limpa
local vigiados = setmetatable({}, {__mode = "k"})
local function vigiar(m)
	if vigiados[m] then return end; vigiados[m] = true
	m:GetAttributeChangedSignal("EmAtaque"):Connect(function()
		if m:GetAttribute("EmAtaque") then return end
		task.delay(0.35, function() if not m:GetAttribute("EmAtaque") then pararTudo(m, 0.6) end end)
	end)
	m.AncestryChanged:Connect(function() if not m:IsDescendantOf(workspace) then pararTudo(m, 0) end end)
end

-- token por poder: um evento novo invalida os agendamentos do uso anterior (sem sons "fantasma" ao cancelar)
local tok = setmetatable({}, {__mode = "k"})
local function novoTok(m, hab) tok[m] = tok[m] or {}; tok[m][hab] = (tok[m][hab] or 0) + 1; return tok[m][hab] end
local function valido(m, hab, t) return vivo(m) and tok[m] and tok[m][hab] == t end
local function depois(m, hab, t, seg, fn) task.delay(seg, function() if valido(m, hab, t) then fn() end end) end

-- ===== SOPRO GLACIAL ==============================================================================================
-- preparo: inspiracao profunda + energia gelada crescendo + estalos | emissao: rajada de pressao no ataque e depois
-- LACO continuo (vento sob pressao, ronco grave, estalos de cristal, textura de particulas) ate o fim | impacto: laço de
-- congelamento no ponto onde o jato bate (segue o ponto) + estilhacos espacados | fim: laços somem e o dragao expira.
local impactoSopro = setmetatable({}, {__mode = "k"})
local function sopro(m, d)
	local b = bocaDe(m)
	if d.fase == "preparo" then
		local t = novoTok(m, "Sopro")
		tocar(b, sorteia(B.inspira), {vol = 0.9, tom = var(0.5, 0.04), corte = 1.2, dist = 140, prio = 3})
		laco(m, "soproPrep", b, B.ronco, {vol = 0.55, tom = 0.55, fadeIn = 0.8, corte = 2.2, dist = 200})
		laco(m, "soproPrep", b, B.cristais, {vol = 0.35, tom = 1.15, fadeIn = 0.6, corte = 2.2, dist = 120})
		depois(m, "Sopro", t, 0.45, function() tocar(b, B.tinido, {vol = 0.3, tom = var(1.7, 0.08), corte = 0.5, dist = 110}) end)
		depois(m, "Sopro", t, 0.8, function() tocar(b, B.tinido, {vol = 0.38, tom = var(1.5, 0.08), corte = 0.5, dist = 110}) end)
	elseif d.fase == "emissao" then
		pararLaco(m, "soproPrep", 0.25)
		pararLaco(m, "sopro", 0.1)
		local lim = math.max(d.duracao or 1.8, 5) + 1.5                     -- trava: segurado ate emissaoMax (5 s)
		tocar(b, B.pressao, {vol = 0.95, tom = var(0.58, 0.03), corte = 0.9, fadeOut = 0.35, dist = 220, prio = 4})   -- ataque do jato
		laco(m, "sopro", b, B.vento, {vol = 0.8, tom = var(0.82, 0.03), fadeIn = 0.2, corte = lim, dist = 230})
		laco(m, "sopro", b, B.ronco, {vol = 0.75, tom = var(0.62, 0.03), fadeIn = 0.3, corte = lim, dist = 260})
		laco(m, "sopro", b, B.cristais, {vol = 0.5, tom = var(1.05, 0.04), fadeIn = 0.35, corte = lim, dist = 150})
		laco(m, "sopro", b, B.granulos, {vol = 0.3, tom = var(1.3, 0.05), fadeIn = 0.4, corte = lim, dist = 120})
		-- ponto de impacto: ancora que o VFXGelo move (S.soproImpacto); laço de congelamento la
		local a = Instance.new("Attachment"); a.Name = "Som_SoproImpacto"; a.WorldPosition = b:IsA("Attachment") and b.WorldPosition or m:GetPivot().Position
		a.Parent = workspace.Terrain; Debris:AddItem(a, lim + 1)
		impactoSopro[m] = {a = a, ativo = false}
		laco(m, "sopro", a, B.cristaisB, {vol = 0, tom = var(0.85, 0.04), corte = lim, dist = 180})
		laco(m, "sopro", a, B.racharLongo, {vol = 0, tom = 1.1, corte = lim, dist = 180})
	elseif d.fase == "fim" then
		novoTok(m, "Sopro")
		pararLaco(m, "soproPrep", 0.2)
		pararLaco(m, "sopro", 0.55)                                       -- encerramento suave (nao corta seco)
		local ip = impactoSopro[m]; impactoSopro[m] = nil
		if ip and vivo(ip.a) then emPos(ip.a.WorldPosition, B.tinido, {vol = 0.3, tom = var(1.4, 0.08), corte = 0.8, dist = 120}) end
		tocar(b, sorteia(B.expira), {vol = 0.55, tom = var(0.78, 0.04) * tomVoz(m) / 0.8, corte = 2.0, fadeOut = 0.6, dist = 110})
		tocar(b, B.sopro, {vol = 0.35, tom = 0.8, corte = 1.6, fadeIn = 0.1, fadeOut = 0.8, dist = 90})
	end
end
-- chamado pelo VFXGelo a cada leitura do ponto de impacto do jato (h = resultado do raycast ou nil)
function S.soproImpacto(m, pos)
	local ip = impactoSopro[m]; if not ip or not vivo(ip.a) then return end
	local l = lacos[m] and lacos[m].sopro; if not l then return end
	local bateu = pos ~= nil
	if pos then ip.a.WorldPosition = pos end
	if bateu ~= ip.ativo then
		ip.ativo = bateu
		for _, r in ipairs(l) do
			if vivo(r.s) and r.pai == ip.a then
				local v = bateu and (r.s.SoundId == B.cristaisB and 0.65 or 0.45) or 0
				TweenService:Create(r.s, TweenInfo.new(0.25), {Volume = v}):Play()
			end
		end
	end
	if bateu and pode(m, "soproEstilhaco", 0.7 + math.random() * 0.5) then
		emPos(pos, sorteia(B.pedacos), {vol = 0.35, tom = var(1.15, 0.1), corte = 1.2, dist = 140})
	end
end

-- ===== RAJADAS DE GELO ============================================================================================
-- preparo: inspiracao curta + cristal se formando | disparo (no instante real da saida): estalo cristalino forte +
-- lanca cortando o ar + ar deslocado; durante o voo a lanca carrega um silvo 3D (passa pelo ouvinte) | impacto em
-- inimigo: seco, fratura e fragmentos | em superficie: estilhacamento, pedacos caindo e eco curto | sem laser/tiro.
local function rajadas(m, d)
	local b = bocaDe(m)
	if d.fase == "preparo" then
		novoTok(m, "Rajadas")
		tocar(b, sorteia(B.inspira), {vol = 0.7, tom = var(0.68, 0.04), corte = 0.8, dist = 120, prio = 3})
		tocar(b, B.rachar, {vol = 0.35, tom = var(1.6, 0.05), corte = 0.7, fadeOut = 0.25, dist = 120})
	elseif d.fase == "disparo" then
		local i = d.indice or 1
		local pos = d.de or (b:IsA("Attachment") and b.WorldPosition) or m:GetPivot().Position
		local a = ancora(pos, 2.5)
		tocar(a, B.estalo, {vol = 0.85, tom = var(1.3 + 0.05 * (i % 2), 0.05), corte = 0.32, fadeOut = 0.12, dist = 220, prio = 4})
		tocar(a, sorteia(B.corte), {vol = 0.8, tom = var(0.92, 0.07), corte = 0.8, dist = 230, prio = 4})
		tocar(a, B.deslocamento, {vol = 0.45, tom = var(0.55, 0.05), corte = 0.7, dist = 160})
		tocar(a, B.pressaoCurta, {vol = 0.3, tom = var(1.25, 0.06), corte = 0.35, dist = 120})
	elseif d.fase == "impacto" then
		local pos = d.pos; if not pos then return end
		if d.acertou then
			emPos(pos, B.baque, {vol = 1.0, tom = var(0.6, 0.05), corte = 0.6, dist = 200, prio = 4})
			emPos(pos, B.estilhaco[1], {vol = 0.95, tom = var(0.88, 0.06), corte = 1.2, dist = 220, prio = 4})
			emPos(pos, B.neveBaque, {vol = 0.6, tom = var(0.75, 0.05), corte = 0.45, dist = 160})
			task.delay(0.12, function() emPos(pos, sorteia(B.pedacos), {vol = 0.45, tom = var(1.1, 0.08), corte = 1.4, dist = 140}) end)
		else
			emPos(pos, B.estilhaco[2], {vol = 0.9, tom = var(0.95, 0.06), corte = 1.9, dist = 230, prio = 4})
			task.delay(0.16, function() emPos(pos, sorteia(B.pedacos), {vol = 0.6, tom = var(1.0, 0.08), corte = 2.4, dist = 200}) end)
			task.delay(0.22, function() emPos(pos, B.estilhaco[2], {vol = 0.22, tom = var(0.82, 0.04), corte = 1.0, dist = 300, min = 40}) end)   -- eco curto
		end
	elseif d.fase == "dissipa" then
		if d.pos then emPos(d.pos, B.tinido, {vol = 0.25, tom = var(1.6, 0.1), corte = 0.7, dist = 120}) end
	end
end
-- lanca em voo: silvo 3D preso a peca (chamado pelo VFXGelo ao montar a lanca)
function S.lanca(m, peca, de)
	if not vivo(peca) then return end
	tocar(peca, B.ventoB, {pos = de, vol = 0.55, tom = var(1.5, 0.06), corte = 1.4, fadeIn = 0.05, fadeOut = 0.15, dist = 140, min = 8, ini = math.random() * 6})
end

-- ===== ZERO ABSOLUTO ==============================================================================================
-- 4 fases acompanhando a propagacao real (tempos iguais aos do visual: frente vVis = min(vel, 58), aneis de cristal
-- em r/vVis + 0,18, zona, derretimento): 1 concentracao grave crescente | 2 expansao: onda de pressao + congelamento
-- que AVANCA (ancora que anda com a frente) e estalos cada vez mais rapidos | 3 cristais: ruptura e emergencia em cada
-- anel + fragmentos | 4 dissipacao: estalos residuais e derretimento.
local function zero(m, d)
	local peito = peitoDe(m)
	if d.fase == "preparo" then
		local t = novoTok(m, "ZeroAbsoluto")
		local e = d.emissao or 1.06
		laco(m, "zeroCarga", peito, B.ronco, {vol = 0.9, tom = 0.48, fadeIn = e, corte = e + 0.6, dist = 260})
		laco(m, "zeroCarga", peito, B.cristais, {vol = 0.45, tom = 0.95, fadeIn = e * 0.8, corte = e + 0.6, dist = 140})
		ajustarLaco(m, "zeroCarga", nil, 1.25, e)                          -- o grave sobe de tom (tensao)
		tocar(cabecaDe(m), sorteia(B.esforco), {vol = 0.6, tom = var(0.82, 0.04) * tomVoz(m) / 0.8, corte = 1.4, dist = 150, prio = 3})
		for k, tt in ipairs({0.35, 0.62, 0.82, 0.96}) do
			depois(m, "ZeroAbsoluto", t, e * tt, function() tocar(peito, B.tinido, {vol = 0.2 + 0.07 * k, tom = var(1.3 + 0.1 * k, 0.06), corte = 0.5, dist = 120}) end)
		end
	elseif d.fase == "onda" then
		local t = tok[m] and tok[m].ZeroAbsoluto or novoTok(m, "ZeroAbsoluto")
		pararLaco(m, "zeroCarga", 0.15)
		local c = d.centro or m:GetPivot().Position
		local zr, zona, vel = d.zonaRaio or 52, d.zona or 4, d.vel or 95
		local vVis = math.min(vel, 58); local tEsp = zr / vVis
		-- 2) descarga: onda de pressao (grave curto + rajada de ar frio) e o congelamento que racha a partir do centro
		local ac = ancora(c, zona + tEsp + 3)
		tocar(ac, B.grave, {vol = 0.6, tom = var(0.78, 0.03), corte = 1.1, fadeOut = 0.5, dist = 320, prio = 4})
		tocar(ac, B.pressao, {vol = 0.95, tom = var(0.44, 0.03), corte = 1.3, fadeOut = 0.5, dist = 300, prio = 4})
		tocar(ac, B.neveBaque, {vol = 0.8, tom = 0.55, corte = 0.8, dist = 260, prio = 4})
		if not d.noChao then return end
		tocar(ac, B.racharLongo, {vol = 0.75, tom = var(0.85, 0.04), corte = math.min(7.5, zona + tEsp), fadeOut = 1.0, dist = 260, prio = 3})
		-- frente que avanca: ancora andando no raio atual, com estalos crescendo
		local up = d.normal or Vector3.yAxis
		local x = up:Cross(Vector3.zAxis); if x.Magnitude < 0.1 then x = up:Cross(Vector3.xAxis) end; x = x.Unit
		local frente = ancora(c, tEsp + 2)
		laco(m, "zeroFrente", frente, B.cristais, {vol = 0.35, tom = 0.9, fadeIn = 0.1, corte = tEsp + 0.4, fadeOut = 0.35, dist = 200})
		laco(m, "zeroFrente", frente, B.granulos, {vol = 0.3, tom = 1.15, fadeIn = 0.1, corte = tEsp + 0.4, fadeOut = 0.35, dist = 160})
		local ang = math.random() * math.pi * 2; local dirF = (x * math.cos(ang) + x:Cross(up).Unit * math.sin(ang))
		local t0 = os.clock()
		task.spawn(function()
			while os.clock() - t0 < tEsp and vivo(frente) do
				local r = (os.clock() - t0) * vVis; frente.WorldPosition = c + dirF * r + up * 1.5
				task.wait(0.05)
			end
		end)
		ajustarLaco(m, "zeroFrente", 2.2, 1.15, tEsp)                      -- estalos crescentes enquanto avanca
		local n = 6
		for k = 1, n do                                                     -- estalos cada vez mais proximos
			local tt = tEsp * (1 - (1 - k / n) ^ 1.6)
			depois(m, "ZeroAbsoluto", t, tt, function()
				local r = math.min(zr, tt * vVis); local a2 = ang + (math.random() - 0.5) * 2.2
				emPos(c + (x * math.cos(a2) + x:Cross(up).Unit * math.sin(a2)) * r, B.tinido, {vol = 0.3 + 0.06 * k, tom = var(1.1 + 0.05 * k, 0.08), corte = 0.6, dist = 200})
			end)
		end
		-- 3) cristais emergindo em cada anel (mesmo tempo do visual): ruptura + emergencia + fragmentos
		for ia, fr in ipairs({0.28, 0.48, 0.68, 0.88}) do
			local r = zr * fr
			depois(m, "ZeroAbsoluto", t, r / vVis + 0.18, function()
				local a2 = math.random() * math.pi * 2; local p = c + (x * math.cos(a2) + x:Cross(up).Unit * math.sin(a2)) * r
				emPos(p, B.estalo, {vol = 0.55 - ia * 0.05, tom = var(0.7 + ia * 0.08, 0.05), corte = 0.5, dist = 220, prio = 3})
				emPos(p, sorteia(B.estilhaco), {vol = 0.45, tom = var(0.65 + ia * 0.07, 0.05), corte = 1.2, dist = 220})
				task.delay(0.15, function() emPos(p, sorteia(B.pedacos), {vol = 0.35, tom = var(0.9, 0.1), corte = 1.5, dist = 150}) end)
			end)
		end
		-- zona congelada: estalos residuais esparsos
		for k = 1, 3 do
			depois(m, "ZeroAbsoluto", t, tEsp + k * zona / 4, function()
				local a2 = math.random() * math.pi * 2; local rr = math.sqrt(math.random()) * zr * 0.8
				emPos(c + (x * math.cos(a2) + x:Cross(up).Unit * math.sin(a2)) * rr, B.tinido, {vol = 0.18, tom = var(1.5, 0.12), corte = 0.6, dist = 120})
			end)
		end
		-- 4) dissipacao: derretimento (crepitar suave sumindo) quando o gelo some
		depois(m, "ZeroAbsoluto", t, zona + tEsp * 0.6, function()
			emPos(c + up * 1.5, B.cristaisB, {vol = 0.35, tom = 0.8, corte = 1.8, fadeIn = 0.2, fadeOut = 1.2, dist = 160, ini = math.random() * 6})
			emPos(c + up * 1.5, B.baque, {vol = 0.18, tom = var(1.4, 0.1), corte = 0.5, dist = 100})
		end)
	end
end

-- ===== NEVASCA ANCESTRAL ==========================================================================================
-- 1 ascensao (asas profundas, ar, esforco, vento crescendo) -> 2 rugido ancestral (grave, longo, organico, na cabeca)
-- -> 3 carregamento (energia e vibracao graves crescendo, estalos pelo corpo) -> 4 PULSOS: em cada onda REAL do
-- servidor, pulso grave + onda de pressao + estalos rapidos + fragmentos cortando o ar + estilhacos, cada pulso com
-- variacao; entre ondas uma camada continua de granizo/fragmentos (agrupada: nunca um som por fragmento) -> 5
-- recuperacao (energia e vento caindo, estalos residuais, respiracao forte, volta ao voo/pouso).
local TONS_PULSO = {0.74, 0.82, 0.7, 0.78}
local function nevasca(m, d)
	local peito, cab = peitoDe(m), cabecaDe(m)
	if d.fase == "inicio" then
		local t = novoTok(m, "Nevasca")
		local dur, rug = d.duracao or 5.6, d.rugido or 1.75
		local s0, s1 = (d.subida and d.subida[1]) or 0.5, (d.subida and d.subida[2]) or 1.6
		pararTudo(m, 0.2)
		-- 1) ascensao: 3 batidas profundas no intervalo da subida + ar deslocado + esforco + vento crescendo
		laco(m, "nevVento", peito, B.ventoB, {vol = 0.75, tom = 0.7, fadeIn = rug, corte = dur + 1, dist = 300})
		for k, tt in ipairs({s0 - 0.15, (s0 + s1) / 2 - 0.1, s1 - 0.2}) do
			depois(m, "Nevasca", t, math.max(0, tt), function()
				tocar(peito, sorteia(B.asa), {vol = 1.35 - k * 0.1, tom = var(0.42, 0.05), corte = 0.9, dist = 220, prio = 3})
				tocar(peito, B.deslocamento, {vol = 0.5, tom = var(0.42, 0.05), corte = 0.9, dist = 180})
			end)
		end
		depois(m, "Nevasca", t, s0 + 0.1, function() tocar(cab, sorteia(B.esforco), {vol = 0.65, tom = var(0.78, 0.04) * tomVoz(m) / 0.8, corte = 1.3, dist = 160, prio = 3}) end)
		-- 3) carregamento (comeca no fim da subida e cresce ate a 1a onda, por baixo do rugido)
		depois(m, "Nevasca", t, s1 - 0.3, function()
			laco(m, "nevCarga", peito, B.ronco, {vol = 1.0, tom = 0.45, fadeIn = 0.9, corte = dur, dist = 340})
			laco(m, "nevCarga", peito, B.cristais, {vol = 0.5, tom = 0.9, fadeIn = 0.8, corte = dur, dist = 180})
			ajustarLaco(m, "nevCarga", nil, 1.3, 1.0)
			for k = 1, 4 do depois(m, "Nevasca", t, 0.15 + k * 0.17, function() tocar(peito, B.tinido, {vol = 0.25 + 0.05 * k, tom = var(1.2 + 0.08 * k, 0.06), corte = 0.5, dist = 160}) end) end
		end)
		-- 2) rugido ancestral, preso a cabeca (sai da boca), maior alcance do kit mas nao o mapa inteiro
		depois(m, "Nevasca", t, rug, function()
			tocar(cab, B.rugidoAncestral, {vol = 2.0, tom = var(0.78, 0.02) * tomVoz(m), corte = 4.2, rugido = true, dist = 420, min = 30, prio = 5})
			tocar(cab, B.rugidoCorpo, {vol = 1.0, tom = var(0.7, 0.02) * tomVoz(m), corte = 3.4, rugido = true, dist = 360, min = 30, prio = 5})
			tocar(cab, B.sopro, {vol = 0.5, tom = 0.6, corte = 2.4, fadeIn = 0.3, fadeOut = 0.8, dist = 200})
			ajustarLaco(m, "nevVento", 1.3, 1.15, 0.6)
		end)
		-- camada continua entre as ondas (fragmentos voando o tempo todo no visual): granizo + cortes espacados
		depois(m, "Nevasca", t, rug + 0.2, function()
			laco(m, "nevGranizo", peito, B.granulos, {vol = 0.45, tom = 1.35, fadeIn = 0.4, corte = dur - rug, dist = 260})
			laco(m, "nevGranizo", peito, B.vento, {vol = 0.6, tom = 1.05, fadeIn = 0.4, corte = dur - rug, dist = 300})
			task.spawn(function()
				local fim = os.clock() + dur - rug - 1.1
				while os.clock() < fim and valido(m, "Nevasca", t) do
					local p = (peito:IsA("Attachment") and peito.WorldPosition or m:GetPivot().Position)
						+ Vector3.new(math.random(-35, 35), math.random(-12, 14), math.random(-35, 35))
					emPos(p, sorteia(B.corte), {vol = 0.4, tom = var(1.15, 0.12), corte = 0.6, dist = 200, prio = 1})
					task.wait(0.42 + math.random() * 0.3)
				end
			end)
		end)
		-- 5) recuperacao (mesmo tempo do visual: duracao - 0,9)
		depois(m, "Nevasca", t, dur - 0.9, function()
			pararLaco(m, "nevCarga", 1.0); pararLaco(m, "nevGranizo", 0.9)
			ajustarLaco(m, "nevVento", 0.35, 0.8, 1.1)
			for k = 1, 3 do depois(m, "Nevasca", t, 0.2 + k * 0.28, function() tocar(peito, B.tinido, {vol = 0.28 - 0.05 * k, tom = var(1.5, 0.12), corte = 0.5, dist = 150}) end) end
			depois(m, "Nevasca", t, 0.35, function() tocar(cab, B.respiroLongo, {vol = 0.7, tom = var(0.8, 0.03) * tomVoz(m) / 0.8, corte = 3.0, fadeOut = 1.0, dist = 140, prio = 3}) end)
			if not d.noAr then                                               -- descida e pouso no solo
				depois(m, "Nevasca", t, 0.3, function() tocar(peito, sorteia(B.asa), {vol = 1.0, tom = var(0.48, 0.05), corte = 0.9, dist = 200}) end)
				depois(m, "Nevasca", t, 0.85, function() tocar(m.PrimaryPart, B.neveBaque, {vol = 0.8, tom = 0.62, corte = 0.7, dist = 200, prio = 3}) end)
			end
		end)
	elseif d.fase == "onda" then
		-- 4) pulso sincronizado a onda real (servidor), variado por indice; o 1o e o mais forte
		local i = d.indice or 1; local k = i == 1 and 1 or 0.78
		local c = d.pos or m:GetPivot().Position
		local a = ancora(c, 3)
		local tom = TONS_PULSO[(i - 1) % #TONS_PULSO + 1]
		tocar(a, B.grave, {vol = 0.85 * k, tom = var(tom, 0.02), corte = 0.95, fadeOut = 0.45, dist = 380, prio = 5})
		tocar(a, B.pressao, {vol = 0.95 * k, tom = var(0.4 + 0.03 * i, 0.03), corte = 1.0, fadeOut = 0.45, dist = 340, prio = 4})
		tocar(a, B.estalo, {vol = 0.7 * k, tom = var(1.15 + 0.06 * (i % 2), 0.05), corte = 0.4, dist = 260, prio = 4})
		if i == 1 then tocar(a, B.estilhaco[2], {vol = 0.8, tom = 0.78, corte = 1.8, dist = 300, prio = 4}) end
		-- fragmentos cortando o ar: 3 cortes em volta, levemente defasados (camada agrupada)
		for j = 1, 3 do
			task.delay(0.04 + j * 0.07 + math.random() * 0.05, function()
				local dir = Vector3.new(math.random() - 0.5, (math.random() - 0.3) * 0.8, math.random() - 0.5).Unit
				emPos(c + dir * (18 + math.random() * 22), sorteia(B.corte), {vol = 0.6 * k, tom = var(0.95 + 0.1 * j, 0.06), corte = 0.7, dist = 260, prio = 2})
			end)
		end
		-- estilhacos quando os fragmentos param (mesmo tempo da desaceleracao visual 0,55-0,9 s)
		task.delay(0.5 + math.random() * 0.15, function()
			local dir = Vector3.new(math.random() - 0.5, -0.2, math.random() - 0.5).Unit
			emPos(c + dir * 30, sorteia(B.pedacos), {vol = 0.5 * k, tom = var(0.95, 0.08), corte = 1.6, dist = 220, prio = 2})
		end)
	elseif d.fase == "fim" then                                          -- (a cauda da recuperacao segue; so os laços param)
		pararLaco(m, "nevCarga", 0.6); pararLaco(m, "nevGranizo", 0.6); pararLaco(m, "nevVento", 1.2)
	end
end

-- ===== passivas ===================================================================================================
-- Sangue Glacial: so na ativacao, um brilho cristalino discreto (sem laço)
function S.sangue(m)
	local p = peitoDe(m); if not p then return end
	tocar(p, B.tinido, {vol = 0.3, tom = var(1.85, 0.04), corte = 0.9, dist = 120, prio = 2})
	tocar(p, B.deslocamento, {vol = 0.16, tom = 1.7, corte = 0.8, dist = 90})
end
-- Frostbite no alvo: pequenos estalos de cristalizacao conforme sobe (25/50/75), estalo forte no limite (congelar),
-- quebra ao fim do congelamento, dissipacao suave se o frio sumir sem congelar
local nivel = setmetatable({}, {__mode = "k"})
local function raizDe(a) return a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart end
function S.frio(alvo, v)
	local r = raizDe(alvo); if not r then return end
	local faixa = math.floor(math.clamp(v, 0, 99) / 25)
	local ant = nivel[alvo] or 0
	if faixa > ant then
		tocar(r, B.cristais, {vol = 0.18 + 0.08 * faixa, tom = var(1.35 - 0.1 * faixa, 0.05), corte = 0.55, fadeOut = 0.2, dist = 110, ini = math.random() * 8})
		tocar(r, B.tinido, {vol = 0.15 + 0.05 * faixa, tom = var(1.6, 0.08), corte = 0.45, dist = 100})
	end
	nivel[alvo] = faixa
end
function S.frioFim(alvo, congelado)
	local ant = nivel[alvo]; nivel[alvo] = nil
	local r = raizDe(alvo); if not r or congelado or not ant then return end
	tocar(r, B.sopro, {vol = 0.18, tom = 1.2, corte = 0.9, fadeIn = 0.1, fadeOut = 0.5, dist = 90})   -- dissipa
end
function S.congelar(alvo, dur)
	local r = raizDe(alvo); if not r then return end
	nivel[alvo] = 3
	tocar(r, B.estalo, {vol = 0.75, tom = var(1.05, 0.05), corte = 0.45, dist = 180, prio = 4})
	tocar(r, B.rachar, {vol = 0.6, tom = var(1.2, 0.05), corte = 1.1, fadeOut = 0.3, dist = 160, prio = 3})
	task.delay(dur or 1.4, function()
		if not vivo(r) then return end
		tocar(r, B.estilhaco[1], {vol = 0.8, tom = var(1.0, 0.06), corte = 1.2, dist = 200, prio = 4})   -- quebra
		task.delay(0.1, function() if vivo(r) then tocar(r, sorteia(B.pedacos), {vol = 0.4, tom = var(1.1, 0.08), corte = 1.4, dist = 140}) end end)
	end)
end
-- ataques fisicos do Glacial que acertam: estalo de gelo curto no ponto (alem do som do golpe no SonsDragao_Cliente)
function S.golpe(pos)
	if pos then emPos(pos, B.tinido, {vol = 0.4, tom = var(1.1, 0.08), corte = 0.6, dist = 140}) end
end

-- ===== despacho ===================================================================================================
function S.evento(d)
	local m = d.d; if not vivo(m) or not m.PrimaryPart then return end
	vigiar(m)
	if d.hab == "Sopro" then sopro(m, d)
	elseif d.hab == "Rajadas" then rajadas(m, d)
	elseif d.hab == "ZeroAbsoluto" then zero(m, d)
	elseif d.hab == "Nevasca" then nevasca(m, d)
	elseif (d.hab == "Mordida" or d.hab == "Garra" or d.hab == "Cauda") and d.fase == "impacto" and d.acertou then S.golpe(d.pos) end
end
-- mixer compartilhado (PATCH_AUDIO_FOGO 02/11): o SonsFogo usa o MESMO orcamento global, prioridades e limpeza
S.mixer = {tocar = tocar, emPos = emPos, laco = laco, pararLaco = pararLaco, ajustarLaco = ajustarLaco, pararTudo = pararTudo,
	vigiar = vigiar, novoTok = novoTok, valido = valido, depois = depois, pode = pode, osso = osso, var = var, sorteia = sorteia,
	ancora = ancora, tomVoz = tomVoz, vivo = vivo, tok = tok}
-- diagnostico (testes): sons vivos deste modulo
function S.contagem() local n, l = 0, 0; for _, r in ipairs(ativos) do n += 1; if r.laco then l += 1 end end; return n, l end
return S
