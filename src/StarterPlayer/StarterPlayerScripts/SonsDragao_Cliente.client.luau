-- SonsDragao_Cliente (LocalScript) — sons 3D dos dragoes (so visual/audio no cliente; nao afeta jogo).
-- Asas e passos: SINCRONIZADOS com as animacoes que estao tocando (fase da trilha -> evento), volume pelo peso.
-- Ataques: eventos cosmeticos do combate (Combate_Dragoes.FX) e atributos da Mordida Aerea.
-- PATCH_AUDIO_GELO (02/11): perfil de som POR FORMA (SonsConfig.formas[FormaRegional]; o que faltar cai no padrao do
-- Montanhas), vozes por comportamento proprias do Glacial, vento do voo pela velocidade e alcance por categoria.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Cfg = require(RS:WaitForChild("Montaria_Dragoes"):WaitForChild("SonsConfig"))
local cam = workspace.CurrentCamera

-- perfil da forma (heranca do padrao por metatable)
local perfis = {}
local function cfgDe(m)
	local forma = m and m:GetAttribute("FormaRegional")
	local P = forma and Cfg.formas and Cfg.formas[forma]
	if not P then return Cfg end
	if not perfis[forma] then perfis[forma] = setmetatable(P, {__index = Cfg}) end
	return perfis[forma]
end

-- eventos por ciclo de cada clipe: fases (0..1) em que toca o som. Batida = golpe descendente; passos = apoio de cada pe
local Q4 = {0.1375, 0.3875, 0.6375, 0.8875}; local Q4s = {0.125, 0.375, 0.625, 0.875}
local ASAS = {Voo = Q4, Voo_AFK = Q4, Pairar = Q4, Pairar_AFK = Q4, Subida = Q4s, Subida_AFK = Q4s,
	Decolagem = {0.45, 0.85}, Voo_Rapido = {0.55}}
local PASSOS = {Andar = {0.02, 0.27, 0.52, 0.77}, Correr = {0.02, 0.14, 0.52, 0.64}, Correr_Frenagem = {0.1, 0.3},
	Pouso = {0.35}, Montaria_Levantar = {0.6}}
-- extras por forma (nao mudam o Montanhas): Glacial reabre as asas ao sair do mergulho (1 batida forte)
local ASAS_FORMA = {Glacial = {Mergulho_Saida = {0.3}}}

-- VOZ (comportamento da IA): som num ponto do clipe, com chance e intervalo minimo por dragao (nada de rugir sempre)
-- {fase, som em SonsConfig, chance, volume, tom}
local VOZ = {
	Ninho_Ameaca = {{0.36, "rugido", 1, 1.0, 0.9}}, Reagir_Estimulo = {{0.12, "esforco", 0.8, 0.7, 0.9}},
	Idle_Alerta_Mantido = {{0.5, "esforco", 0.35, 0.55, 0.85}}, Preparar_Combate = {{0.3, "esforco", 0.4, 0.65, 0.8}},
	Comer = {{0.1, "mordida", 1, 0.7, 0.8}, {0.433, "mordida", 1, 0.7, 0.8}, {0.766, "mordida", 1, 0.7, 0.8}},
	-- PATCH_VOZ_FORMA (01/11): clipes do sistema universal
	Rugido_Territorial = {{0.3, "rugido", 1, 1.2, 0.85}}, Intimidar = {{0.2, "esforco", 0.6, 0.7, 0.75}, {0.7, "esforco", 0.6, 0.7, 0.75}},
	Curiosidade = {{0.45, "respiro", 0.8, 0.5, 0.9}}, Dano_Forte = {{0.05, "esforco", 1, 0.8, 0.95}}, Dano_Forte_Ar = {{0.05, "esforco", 1, 0.8, 0.95}},
}
-- PATCH_AUDIO_GELO: vozes do Glacial — cada comportamento com o SEU som (territorial, ameaca de ninho, intimidacao,
-- alerta, grunhido, farejar, comer, beber, sono, despertar, dano leve/forte); tons ja contam com TomVoz 0.8
-- PATCH_RUGIDOS_FOGO (02/11): Dragao das Montanhas — fases = momentos reais dos clipes novos (preparo/inspiracao,
-- emissao com a boca abrindo, bafo quente no fim); rugidos em CAMADAS (voz + corpo grave), grunhidos discretos
local VOZ_MONTANHAS = {
	Rugido_Territorial = {{0.12, "inspira", 1, 0.55, 0.62}, {0.30, "rugidoTerritorial", 1, 1.15, 0.92}, {0.31, "rugidoCorpo", 1, 0.6, 0.72},
		{0.86, "bafo", 0.8, 0.22, 0.8}},
	Rugido_Ameaca = {{0.25, "rosnado", 1, 0.75, 0.72}, {0.56, "rugidoAmeaca", 1, 1.05, 0.95}, {0.565, "rugidoAmeacaCorpo", 1, 0.55, 0.78}},
	Rugido_Vitoria = {{0.18, "inspira", 1, 0.5, 0.6}, {0.36, "rugidoVitoria", 1, 1.0, 0.82}, {0.365, "rugidoCorpo", 1, 0.45, 0.85},
		{0.8, "bafo", 0.7, 0.2, 0.85}},
	Ninho_Ameaca = {{0.18, "rosnado", 1, 0.7, 0.75}, {0.36, "rugidoAmeaca", 1, 1.0, 0.9}, {0.365, "rugidoAmeacaCorpo", 1, 0.5, 0.8}},
	Intimidar = {{0.18, "intimidar", 0.8, 0.6, 0.78}, {0.68, "rosnado", 0.5, 0.5, 0.82}},
	Reagir_Estimulo = {{0.12, "alerta", 0.8, 0.6, 0.95}}, Ninho_Alerta = {{0.2, "alerta", 0.8, 0.6, 0.9}},
	Idle_Alerta_Mantido = {{0.5, "grunhido", 0.35, 0.45, 0.9}}, Preparar_Combate = {{0.3, "rosnado", 0.45, 0.5, 0.8}},
	Curiosidade = {{0.4, "farejar", 0.9, 0.45, 0.8}}, Observar_Farejar = {{0.25, "farejar", 0.9, 0.45, 0.78}, {0.65, "farejar", 0.6, 0.4, 0.85}},
	Comer = {{0.1, "mastigar", 1, 0.6, 0.75}, {0.433, "mastigar", 1, 0.6, 0.7}, {0.766, "mastigar", 1, 0.6, 0.78}},
	Beber = {{0.2, "beber", 1, 0.45, 0.85}},
	Adormecer = {{0.6, "respiroSono", 1, 0.35, 0.5}}, Dormir = {{0.1, "respiroSono", 1, 0.3, 0.48}},
	Acordar = {{0.15, "despertar", 1, 0.45, 0.8}, {0.6, "esforco", 0.6, 0.45, 0.9}},
	Dano_Leve = {{0.05, "danoLeve", 1, 0.65, 1.0}}, Dano_Leve_Ar = {{0.05, "danoLeve", 1, 0.65, 1.0}},
	Dano_Forte = {{0.05, "dano", 1, 0.8, 0.9}}, Dano_Forte_Ar = {{0.05, "dano", 1, 0.8, 0.9}},
}
local VOZ_FORMA = {Montanhas = VOZ_MONTANHAS, Glacial = {
	Ninho_Ameaca = {{0.36, "intimidar", 1, 1.0, 1.0}}, Rugido_Territorial = {{0.3, "rugido", 1, 1.25, 1.0}},
	Intimidar = {{0.15, "intimidar", 0.9, 0.85, 1.0}, {0.65, "grunhido", 0.6, 0.6, 0.95}},
	Reagir_Estimulo = {{0.12, "alerta", 0.8, 0.65, 1.05}}, Ninho_Alerta = {{0.2, "alerta", 0.8, 0.65, 1.0}},
	Idle_Alerta_Mantido = {{0.5, "grunhido", 0.35, 0.5, 1.0}}, Preparar_Combate = {{0.3, "esforco", 0.5, 0.65, 0.95}},
	Curiosidade = {{0.4, "farejar", 0.9, 0.45, 0.9}},
	Observar_Farejar = {{0.25, "farejar", 0.9, 0.45, 0.88}, {0.65, "farejar", 0.6, 0.4, 0.95}},
	Comer = {{0.1, "mastigar", 1, 0.6, 0.85}, {0.433, "mastigar", 1, 0.6, 0.8}, {0.766, "mastigar", 1, 0.6, 0.88}},
	Comer_Mastigar = {{0.15, "mastigar", 1, 0.55, 0.88}, {0.6, "mastigar", 1, 0.55, 0.82}},
	Beber = {{0.2, "beber", 1, 0.5, 0.95}}, Beber_Loop = {{0.2, "beber", 1, 0.45, 0.9}},
	Adormecer = {{0.6, "respiroSono", 1, 0.4, 1.0}}, Dormir = {{0.1, "respiroSono", 1, 0.35, 0.95}},
	Acordar = {{0.15, "despertar", 1, 0.6, 1.1}, {0.6, "esforco", 0.6, 0.5, 1.0}},
	Espreguicar = {{0.3, "esforco", 0.8, 0.5, 1.0}, {0.75, "respiro", 0.8, 0.4, 1.0}}, Deitar = {{0.7, "respiro", 0.7, 0.35, 1.0}},
	Dano_Leve = {{0.05, "danoLeve", 1, 0.7, 1.1}}, Dano_Leve_Ar = {{0.05, "danoLeve", 1, 0.7, 1.1}},
	Dano_Forte = {{0.05, "dano", 1, 0.85, 1.05}}, Dano_Forte_Ar = {{0.05, "dano", 1, 0.85, 1.05}},
}}
local function fasesDe(t) local f = {}; for n, l in pairs(t) do f[n] = {}; for _, e in ipairs(l) do table.insert(f[n], e[1]) end end; return f end
local VOZF = fasesDe(VOZ); local VOZF_FORMA = {}; for k, t in pairs(VOZ_FORMA) do VOZF_FORMA[k] = fasesDe(t) end
local function vozDe(m, nome)
	local forma = m:GetAttribute("FormaRegional"); local t = forma and VOZ_FORMA[forma]
	if t and t[nome] then return t[nome], VOZF_FORMA[forma][nome] end
	return VOZ[nome], VOZF[nome]
end
local function asasDe(m, nome)
	local forma = m:GetAttribute("FormaRegional"); local t = forma and ASAS_FORMA[forma]
	return ASAS[nome] or (t and t[nome])
end
local INTERVALO_VOZ = {rugido = 12, esforco = 7, mordida = 0.5, intimidar = 8, grunhido = 5, alerta = 5, farejar = 2.5,
	mastigar = 0.5, beber = 1.5, respiroSono = 4, despertar = 10, dano = 1.2, danoLeve = 0.8,
	rugidoTerritorial = 8, rugidoCorpo = 2, rugidoAmeaca = 4, rugidoAmeacaCorpo = 2, rugidoVitoria = 20, rosnado = 2.5, bafo = 3, inspira = 2}
local CORTE_VOZ = {esforco = 1.2, grunhido = 1.5, alerta = 1.2, farejar = 1.4, mastigar = 1.1, beber = 1.3, respiroSono = 4.5, respiro = 1.8,
	rugidoTerritorial = 3.0, rugidoCorpo = 2.6, rugidoAmeaca = 1.4, rugidoAmeacaCorpo = 1.3, rugidoVitoria = 2.2, rosnado = 1.1, bafo = 1.2,
	inspira = 1.1, dano = 0.9, despertar = 1.0, intimidar = 1.1}
local LONGE = {rugido = true, intimidar = true, rugidoCombate = true, dano = true, rugidoTerritorial = true, rugidoCorpo = true,
	rugidoAmeaca = true, rugidoAmeacaCorpo = true, rugidoVitoria = true}
local RUGIDOS = {rugido = true, rugidoTerritorial = true, rugidoAmeaca = true, rugidoVitoria = true, rugidoCombate = true}
local ultimoRugidoGlobal, donoUltimoRugido = -99, nil      -- dois dragoes nao rugem por cima um do outro
local PERTO = {respiro = true, farejar = true, beber = true, mastigar = true, respiroSono = true, bafo = true, inspira = true}
local ultimaVoz = {}

local ativos = {}
local function tocar(pai, sid, vol, tom, corte, dist)
	if not (pai and pai.Parent and sid) then return end
	if (ativos[pai] or 0) >= (Cfg.maxSimultaneos or 6) then return end
	local d = dist or Cfg.distMax
	if pai:IsA("BasePart") and (pai.Position - cam.CFrame.Position).Magnitude > d then return end   -- fora do alcance: nem cria
	ativos[pai] = (ativos[pai] or 0) + 1
	task.delay(corte or 2.5, function() ativos[pai] = math.max(0, (ativos[pai] or 1) - 1) end)
	local s = Instance.new("Sound"); s.SoundId = sid; s.Volume = vol or 1; s.PlaybackSpeed = tom or 1
	s.RollOffMode = Enum.RollOffMode.InverseTapered; s.RollOffMinDistance = 12; s.RollOffMaxDistance = d
	s.Parent = pai; s:Play()
	if corte then task.delay(corte, function() if s.Parent then s:Stop(); s:Destroy() end end)
	else s.Ended:Once(function() s:Destroy() end); task.delay(12, function() if s.Parent then s:Destroy() end end) end
end
local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end
-- PATCH_VOZ_FORMA: tom de voz da forma regional (atributo TomVoz no modelo; 1 = padrao)
local function tomVoz(pai) local mm = pai and pai:FindFirstAncestorWhichIsA("Model"); return (mm and mm:GetAttribute("TomVoz")) or 1 end
local function faixa(f) return f and (f[1] + (f[2] - f[1]) * math.random()) or 1 end
local function tocarVoz(m, pp, nome, fase)
	local C = cfgDe(m)
	for _, ev in ipairs((vozDe(m, nome))) do
		if ev[1] == fase and math.random() <= ev[3] then
			local k = ev[2]; ultimaVoz[m] = ultimaVoz[m] or {}
			if C[k] and os.clock() - (ultimaVoz[m][k] or -99) >= (INTERVALO_VOZ[k] or 5) then
				ultimaVoz[m][k] = os.clock()
				local dist = LONGE[k] and (C.distVoz or Cfg.distMax) or PERTO[k] and (C.distRespiro or 120) or nil
				local vol = ev[4]
				if RUGIDOS[k] then                                    -- outro dragao rugiu ha pouco: este entra baixo (sem embolar)
					if donoUltimoRugido ~= m and os.clock() - ultimoRugidoGlobal < 1.6 then vol *= 0.35 end
					ultimoRugidoGlobal, donoUltimoRugido = os.clock(), m
				end
				tocar(pp, sorteia(C[k]), vol, ev[5] * (0.95 + math.random() * 0.1) * tomVoz(pp), CORTE_VOZ[k], dist)
			end
		end
	end
end

local estado = {}                      -- [modelo] = {[track] = ultimaFase}
-- nome logico da trilha: o servidor publica MapaTrilhas (nome -> AnimationId); o nome nao replica
local function temSom(m, n) return ASAS[n] or PASSOS[n] or vozDe(m, n) or asasDe(m, n) end
local function nomeTrilha(m, t)
	local id = t.Animation and t.Animation.AnimationId or ""
	local mapa = m:FindFirstChild("MapaTrilhas")
	-- um mesmo clipe pode servir a varios nomes (apelidos: Andar/Giro_E/Correr...): prefere um nome que tenha som
	local achado
	if mapa then for _, sv in ipairs(mapa:GetChildren()) do
		if sv.Value == id or sv.Value:find(id, 1, true) or id:find(sv.Value, 1, true) then
			if temSom(m, sv.Name) then return sv.Name end
			achado = achado or sv.Name
		end
	end end
	return achado or (t.Animation and t.Animation.Name or "")
end
local function dragoes()
	local l = {}
	for _, m in ipairs(workspace:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("FormaRegional") and m.PrimaryPart and m:FindFirstChildOfClass("AnimationController") then table.insert(l, m) end
	end
	return l
end

-- vento do voo pela VELOCIDADE (perfis com ventoVoo): laço unico por dragao, volume/tom seguem a velocidade medida no
-- cliente (posicao), some ao pousar ou longe. Planeio = so vento (as batidas so existem nos clipes de batida).
local vento, ultPos, estavaNoAr = {}, {}, {}
local function atualizarVento(m, pp, dt)
	local C = cfgDe(m); if not C.ventoVoo then return end
	local p = pp.Position; local ant = ultPos[m]; ultPos[m] = p
	local v = ant and (p - ant).Magnitude / math.max(dt, 1 / 60) or 0
	local noAr = m:GetAttribute("NoAr") or m:GetAttribute("MontariaModo") == "voo"
	local longe = (p - cam.CFrame.Position).Magnitude > (C.distAsa or 200)
	-- pouso (ar -> chao): ultima batida de frenagem + baque de peso no apoio (nem todo pouso toca o clipe Pouso)
	if estavaNoAr[m] and not noAr and C.pouso and not longe then
		tocar(pp, sorteia(C.asa), C.asaVolume * 0.8, faixa(C.asaTom), nil, C.distAsa)
		task.delay(0.12, function() tocar(pp, C.pouso, 0.85, 0.62 + math.random() * 0.08, 0.7, C.distPasso) end)
	end
	estavaNoAr[m] = noAr and true or nil
	local s = vento[m]
	if not noAr or longe then
		if s then vento[m] = nil; TweenService:Create(s, TweenInfo.new(0.6), {Volume = 0}):Play(); task.delay(0.65, function() s:Destroy() end) end
		return
	end
	if not s then
		s = Instance.new("Sound"); s.SoundId = C.ventoVoo; s.Looped = true; s.Volume = 0; s.TimePosition = math.random() * 20
		s.RollOffMode = Enum.RollOffMode.InverseTapered; s.RollOffMinDistance = 16; s.RollOffMaxDistance = C.distAsa or 200
		s.Parent = pp; s:Play(); vento[m] = s
	end
	local a, b = C.ventoVooVel[1], C.ventoVooVel[2]
	local k = math.clamp((v - a) / (b - a), 0, 1) ^ 0.7               -- curva suave: ja se ouve no voo de cruzeiro
	local alvoV = C.ventoVooVolume * (0.12 + 0.88 * k)
	local alvoT = C.ventoVooTom[1] + (C.ventoVooTom[2] - C.ventoVooTom[1]) * k
	s.Volume += (alvoV - s.Volume) * math.min(1, dt * 3)                -- suavizado (sem degraus)
	s.PlaybackSpeed += (alvoT - s.PlaybackSpeed) * math.min(1, dt * 2)
end

local acc = 0
RunService.Heartbeat:Connect(function(dt)
	acc += dt; if acc < 1 / 30 then return end
	local passo = acc; acc = 0
	for _, m in ipairs(dragoes()) do
		local pp = m.PrimaryPart
		atualizarVento(m, pp, passo)
		if (pp.Position - cam.CFrame.Position).Magnitude > Cfg.distMax then continue end
		local an = m:FindFirstChildOfClass("AnimationController"):FindFirstChildOfClass("Animator"); if not an then continue end
		local C = cfgDe(m)
		local st = estado[m] or {}; estado[m] = st
		local asaJa = false
		for _, t in ipairs(an:GetPlayingAnimationTracks()) do
			local nome = nomeTrilha(m, t)
			local asas = asasDe(m, nome); local voz, vozF = vozDe(m, nome)
			local fases = asas or PASSOS[nome] or vozF
			if fases and t.Length > 0 and t.WeightCurrent > 0.3 then
				local f = (t.TimePosition / t.Length) % 1
				local ant = st[t]
				if ant then
					for _, alvo in ipairs(fases) do
						local passou = (ant < alvo and f >= alvo) or (f < ant and (alvo > ant or alvo <= f))   -- cruzou (inclusive na volta do laco)
						if passou then
							if asas and not asaJa then
								asaJa = true                                   -- mistura de varias trilhas de voo: 1 batida
								tocar(pp, sorteia(C.asa), C.asaVolume * math.clamp(t.WeightCurrent, 0.4, 1), faixa(C.asaTom), nil, C.distAsa)
							elseif PASSOS[nome] and not m:GetAttribute("NoAr") then
								tocar(pp, sorteia(C.passo), C.passoVolume, faixa(C.passoTom), 0.6, C.distPasso)   -- corte curto: corrida rapida nao esgota a cota de sons
								tocar(pp, C.passoPeso, C.passoPesoVolume * (nome == "Correr" and 1.4 or 1), 0.9 + math.random() * 0.2, C.passoPesoCorte, C.distPasso)
							elseif voz then
								tocarVoz(m, pp, nome, alvo)
							end
						end
					end
				end
				st[t] = f
			else st[t] = nil end
		end
	end
end)

-- respiracao grave e discreta (intervalos irregulares); depois de correr/voar fica mais frequente por ~20 s
local esforcoAte, proxRespiro = {}, {}
task.spawn(function()
	while true do
		task.wait(1)
		for _, m in ipairs(dragoes()) do
			local pp = m.PrimaryPart; local C = cfgDe(m)
			if (pp.Position - cam.CFrame.Position).Magnitude > (C.distRespiro or 120) then continue end
			local modo = m:GetAttribute("MontariaModo")
			if modo == "voo" or m:GetAttribute("NoAr") or m:GetAttribute("EmAtaque") then esforcoAte[m] = os.clock() + 20; continue end
			local cansado = (esforcoAte[m] or 0) > os.clock()
			local prox = proxRespiro[m]
			if not prox then
				local a, b = C.respiroIntervalo[1], C.respiroIntervalo[2]
				proxRespiro[m] = os.clock() + (cansado and a * 0.5 or a) + math.random() * (b - a)
			elseif os.clock() >= prox then
				proxRespiro[m] = nil
				tocar(pp, sorteia(C.respiro), C.respiroVolume * (cansado and 1.4 or 1), faixa(C.respiroTom) * tomVoz(pp), 1.8, C.distRespiro)
			end
		end
	end
end)

-- Mordida Aerea: avanco (whoosh) no inicio, mordida no fechar da boca, estalo forte se acertar
local ligados = {}
local function ligar(m)
	if ligados[m] or not (m:IsA("Model") and m:GetAttribute("FormaRegional")) then return end
	ligados[m] = true
	m:GetAttributeChangedSignal("EmAtaque"):Connect(function()
		if m:GetAttribute("EmAtaque") == "MordidaAerea" and m.PrimaryPart then
			local C = cfgDe(m)
			if C.ataqueVoz then tocar(m.PrimaryPart, sorteia(C.ataqueVoz), 0.8, 0.95 * tomVoz(m.PrimaryPart), 1.4, C.distVoz) end
			task.delay(0.25, function() tocar(m.PrimaryPart, C.avanco, 1.2, 0.85) end)
			task.delay(0.58, function() tocar(m.PrimaryPart, sorteia(C.mordida), 1.3, faixa(C.mordidaTom), C.ataqueVoz and 0.8 or nil) end)
		end
	end)
	m:GetAttributeChangedSignal("MordidaAcertou"):Connect(function()
		if m.PrimaryPart then local C = cfgDe(m); tocar(m.PrimaryPart, sorteia(C.mordida), 1.8, 0.6, C.ataqueVoz and 0.8 or nil) end
	end)
	m.AncestryChanged:Connect(function()
		if not m:IsDescendantOf(workspace) then local s = vento[m]; vento[m] = nil; ultPos[m] = nil; estavaNoAr[m] = nil; if s then s:Destroy() end end
	end)
end
for _, m in ipairs(workspace:GetChildren()) do ligar(m) end
workspace.ChildAdded:Connect(function(m) task.defer(ligar, m) end)

-- habilidades (eventos cosmeticos do servidor)
local FX = RS:WaitForChild("Combate_Dragoes"):WaitForChild("FX", 30)
if FX then
	FX.OnClientEvent:Connect(function(e)
		if type(e) ~= "table" or typeof(e.d) ~= "Instance" or not e.d.PrimaryPart then return end
		local pp = e.d.PrimaryPart; local h, f, el = e.hab, e.fase, e.el
		local C = cfgDe(e.d)
		if el == "Gelo" and (h == "Sopro" or h == "Rajadas" or h == "ZeroAbsoluto" or h == "Nevasca") then return end   -- PATCH_AUDIO_GELO: SonsGelo
		if el == "Fogo" and (h == "Sopro" or h == "Arremetida" or h == "Tempestade" or h == "Coracao" or h == "SangueDeMagma" or h == "Rugido") then return end   -- PATCH_AUDIO_FOGO: SonsFogo
		if h == "Sopro" and f == "emissao" then
			if el == "Fogo" then tocar(pp, C.fogo, 1.4, 0.8); task.delay(0.9, function() tocar(pp, C.fogo, 1.2, 0.75) end)
			elseif el == "Terra" then tocar(pp, C.rochaArrasto, 1.2, 0.9)
			else tocar(pp, C.ar, 1.3, 0.8) end
		elseif h == "Sopro" and f == "preparo" then tocar(pp, C.rugido, 0.6, 1.15, 0.9)
		elseif h == "Sopro" and f == "projetil" then tocar(pp, C.avanco, 0.7, 1.1)
		elseif h == "Arremetida" and f == "emissao" then tocar(pp, C.avanco, 1.4, 0.75)
		elseif h == "Arremetida" and f == "impacto" then tocar(pp, C.rocha, 1, 1, 0.6)
		elseif h == "Tempestade" and f == "impulso" then tocar(pp, sorteia(C.asa), 1.6, 0.6); tocar(pp, C.ar, 1.2, 0.7)
		elseif h == "Tempestade" and f == "batida" then                    -- cada batida real: asa + rajada (seguintes mais leves)
			local k = (e.indice or 1) == 1 and 1 or 0.65
			tocar(pp, sorteia(C.asa), 1.6 * k, 0.6); tocar(pp, C.ar, 1.2 * k, 0.7); if e.superficie then tocar(pp, C.rochaArrasto, 0.6 * k, 0.9) end
		elseif h == "Tempestade" and f == "pouso" then tocar(pp, C.rocha, 0.8, 1, 0.5)
		-- Coracao Infernal: carga (rosnado grave contido) -> lamina sai da boca (chama forte + rugido curto) -> silvos a cada
		-- meia volta da lamina (casados com a funcao de giro do servidor) -> impactos
		elseif h == "Coracao" and f == "carga" then tocar(pp, C.esforco, 0.7, 0.7, 1.1); tocar(pp, C.fogo, 0.5, 0.6)
		elseif h == "Coracao" and f == "lamina" then
			tocar(pp, C.rugido, 1.0, 0.8, 1.2); tocar(pp, C.fogo, 1.5, 0.75)
			local n = math.max(1, math.floor((e.voltas or 1) * 2))
			for i = 1, n do
				local k = (i - 0.5) / n                                       -- fracao do giro (velocidade maior no meio)
				task.delay((e.expele or 0.4) + (e.giro or 1.7) * k, function() if pp.Parent then tocar(pp, C.avanco, 1.1, 0.7 + 0.1 * math.random()); tocar(pp, C.fogo, 0.6, 0.9) end end)
			end
		elseif h == "Coracao" and f == "impacto" then tocar(pp, C.impacto, 0.8, 0.85, C.impactoCorte)
		elseif h == "SangueDeMagma" and f == "ativar" then tocar(pp, C.esforco, 0.6, 0.65, 1.0)
		elseif h == "Ruptura" and f == "preparo" then tocar(pp, C.rugido, 0.9, 0.9)
		elseif h == "Ruptura" and f == "impacto" then tocar(pp, C.rocha, 1.6, 0.8); tocar(pp, C.rochaArrasto, 1.2, 0.8)
		elseif h == "Mordida" and f == "preparo" then
			if C.ataqueVoz and math.random() < 0.5 then tocar(pp, sorteia(C.ataqueVoz), 0.7, 1.0 * tomVoz(pp), 1.2, C.distVoz) end
			task.delay(0.5, function() tocar(pp, C.garra, 0.5, 1.2) end)
		elseif h == "Mordida" and f == "impacto" then
			tocar(pp, sorteia(C.mordida), e.acertou and 1.2 or 0.7, faixa(C.mordidaTom), C.ataqueVoz and 0.8 or nil)
			if e.acertou then tocar(pp, C.impacto, 0.7, 0.8, C.impactoCorte) end
		elseif h == "Garra" and f == "preparo" then
			if math.random() < 0.35 then tocar(pp, sorteia(C.esforco), C.esforcoVolume, 0.8 + math.random() * 0.15, 1.0) end
			task.delay(0.45, function() tocar(pp, C.garra, C.garraVolume, 0.85 + math.random() * 0.1) end)
		elseif h == "Garra" and f == "impacto" and e.acertou then tocar(pp, C.impacto, 0.8, 0.9, C.impactoCorte)
		elseif h == "Cauda" and f == "impacto" then tocar(pp, C.garra, 1.0, 0.7)
		elseif h == "Rugido" and f == "emissao" then tocar(pp, C.rugidoCombate or C.rugido, 1.5, 0.95 * tomVoz(pp), nil, C.distVoz) end
	end)
end
