-- patch_sons_sombra.luau (Studio, Edit) — audio do kit da Sombra (04/11). Gerado por sombrio/gerar_patch_sons_sombra.py.
-- Cria ReplicatedStorage.Combate_Dragoes.SonsSombra e liga o VFXSombra; backup unico ServerStorage.Backup_Sons_Sombra_2026-11-04.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage"); local CD = game:GetService("ReplicatedStorage").Combate_Dragoes
local V = CD.VFXSombra; local src = V.Source:gsub("\r\n", "\n")
if src:find("PATCH_SONS_SOMBRA", 1, true) then return "ja aplicado" end
local a, b = [======[function S.evento(d, f)
	local m = d.d
]======], [======[function S.evento(d, f)
	local m = d.d
	local SN = script.Parent:FindFirstChild("SonsSombra")               -- PATCH_SONS_SOMBRA: audio antes do LOD visual
	if SN and d.fase ~= "reacao" then local ok, e = pcall(require(SN).evento, d); if not ok then warn("SonsSombra: " .. tostring(e)) end end
]======]
local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora VFXSombra")
src = src:sub(1, i - 1) .. b .. src:sub(j + 1); assert(loadstring(src), "VFXSombra nao compila")
local sons = [======[-- SonsSombra (ModuleScript, ReplicatedStorage.Combate_Dragoes) — AUDIO do kit da Sombra do Dragao Sombrio (04/11), so no
-- cliente e so cosmetico. Chamado pelo VFXSombra em todo evento de Sombra (antes do LOD visual). Usa o MESMO mixer do
-- SonsGelo (orcamento global, prioridades, laços com fade, limpeza quando o ataque acaba ou e interrompido).
-- Identidade: breu que SUGA o ar (whoosh reverso), vozes de espirito passando, zumbido grave maligno, respiracao
-- oca; correntes de metal pesado; nada de fogo nem de gelo. So Pro Sound Effects. Volumes/tons NAO_APROVADO.
local Mx = require(script.Parent:WaitForChild("SonsGelo")).mixer
local tocar, emPos, laco, pararLaco, ajustarLaco = Mx.tocar, Mx.emPos, Mx.laco, Mx.pararLaco, Mx.ajustarLaco
local novoTok, valido, depois, osso, var, sorteia, vivo = Mx.novoTok, Mx.valido, Mx.depois, Mx.osso, Mx.var, Mx.sorteia, Mx.vivo
local S = {NAO_APROVADO = true}

local function id(n) return "rbxassetid://" .. n end
local B = {
	-- voz (por ora a do padrao: Creature Roar / Lion Guttural, rebaixada)
	rugido = id(9113985445),                                                -- Creature Roar Deep Throaty Growls 2
	grunhido = {id(9125467833), id(9125467848)},                            -- Creature Growls Lion Deep Guttural Rumbling 1 / 3
	inspira = {id(9119305002), id(9119304904)},                             -- Sniff Breathe In 2 / 1
	expira = {id(9113971433), id(9113972148)},                              -- Creature Growls Lion 2 / 7: breathy
	-- breu
	succao = {id(9120735678), id(9120735974), id(9120736187)},              -- Whoosh Suction 6 / 11 / 12: reverso, airy whomping (2,4 s)
	succaoMagica = id(9120747424),                                          -- Whooshy Magic Sucks Somewhat Phasey 7 (2,3 s)
	grito = id(9118840222),                                                 -- Screaming Suck Burst 3: reverso, hissing (2,6 s)
	espirito = {id(9119466852), id(9119467870), id(9125988635)},            -- Spirit Pass Bys (Ghosts): vozes airy passando (2,1-2,3 s)
	drone = id(9114353261),                                                 -- Evil Drone Deep Unsetting Rumbly Keening 1 (36 s, laço)
	droneSwell = id(9114353038),                                            -- Evil Drone Deep Airy Swell 1 (18 s)
	respiro = id(9113586909),                                               -- Breathing Tone Eerie Soft 2 (36 s, laço): exalacao oca
	ventoOco = id(9113324288),                                              -- Basement Wind Tubular Airy Swirling 12 (10,6 s)
	-- golpe grave
	sub = {id(9119661511), id(9119661508)},                                 -- Sub Boom Slapback Element 1 / 2
	baque = id(9113551773),                                                 -- Boom Thump Rattling Impacts Light Crunch 1
	metal = {id(9116908474), id(9116907950)},                               -- Metal Whomps Deep Pounding Impacts 13 / 8
	-- correntes
	corrente = {id(9113760230), id(9113760351), id(9113760343)},            -- Chain Movement 2 / 5 / 6
	correnteLaco = id(9113763820),                                          -- Chain Rattles 3: clinking constante (2,9 s)
	correnteBate = id(9113764228),                                          -- Chains And Metal Impacts 1 (3,8 s)
	guincho = id(9113766302),                                               -- Chain Winch 2: puxando para apertar (1,4 s)
}
S.BANCO = B
local function peito(m) return osso(m, "Coluna2") or osso(m, "spine_0") or m.PrimaryPart end
local function cabeca(m) return osso(m, "Cabeca") or m.PrimaryPart end
local function bocaO(m) return osso(m, "mouth_upper_tip") or cabeca(m) end
local function raizA(a) return a and a.Parent and (a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart) end

-- ===== SOPRO UMBRAL: preparo (o breu suga o ar para dentro do peito) -> emissao: laço de zumbido maligno + respiracao
-- oca + vento tubular, vozes de espirito no disparo, intensidade respirando devagar -> fim suave e exalacao.
local function sopro(m, d)
	local b = bocaO(m)
	if d.fase == "preparo" then
		novoTok(m, "SoproS")
		tocar(b, sorteia(B.succao), {vol = 0.9, tom = var(0.7, 0.04), corte = 1.6, fadeOut = 0.3, dist = 170, prio = 3})
		tocar(cabeca(m), sorteia(B.inspira), {vol = 0.8, tom = var(0.45, 0.04), corte = 1.2, dist = 120})
	elseif d.fase == "emissao" then
		local t = novoTok(m, "SoproS")
		pararLaco(m, "soproS", 0.1)
		local lim = math.max(d.duracao or 1.8, 6) + 1.5
		tocar(b, sorteia(B.espirito), {vol = 0.9, tom = var(0.72, 0.05), corte = 2.0, fadeOut = 0.6, dist = 230, prio = 4})
		laco(m, "soproS", b, B.drone, {vol = 0.8, tom = var(0.85, 0.03), fadeIn = 0.2, corte = lim, dist = 230, prio = 4})
		laco(m, "soproS", b, B.respiro, {vol = 0.55, tom = var(0.7, 0.03), fadeIn = 0.3, corte = lim, dist = 180})
		laco(m, "soproS", b, B.ventoOco, {vol = 0.45, tom = var(0.8, 0.04), fadeIn = 0.4, corte = lim, dist = 160})
		task.spawn(function()                                              -- variacao lenta, sem deriva
			while valido(m, "SoproS", t) do
				local r = 0.86 + math.random() * 0.26
				ajustarLaco(m, "soproS", r, nil, 0.8); task.wait(0.8)
				if not valido(m, "SoproS", t) then break end
				ajustarLaco(m, "soproS", 1 / r, nil, 0.8); task.wait(0.8)
			end
		end)
	elseif d.fase == "fim" then
		novoTok(m, "SoproS")
		pararLaco(m, "soproS", 0.7)
		tocar(cabeca(m), sorteia(B.expira), {vol = 0.55, tom = var(0.6, 0.04), corte = 1.8, fadeOut = 0.6, dist = 110})
	end
end

-- ===== CORRENTES DA NOITE: grunhido + succao nas garras -> aviso no ponto (zumbido subindo + correntes se mexendo sob o
-- chao) -> erupcao (golpe grave + metal + correntes batendo + vozes) -> cada alvo PRESO: guincho apertando + chocalho
-- em laço enquanto preso -> soltar: correntes caindo.
local presoLaco = setmetatable({}, {__mode = "k"})
local function correntes(m, d)
	if d.fase == "preparo" then
		novoTok(m, "Cor")
		tocar(cabeca(m), sorteia(B.grunhido), {vol = 0.75, tom = var(0.7, 0.04), corte = 1.3, dist = 200, prio = 3})
		tocar(peito(m), B.succaoMagica, {vol = 0.6, tom = var(0.75, 0.04), corte = 1.8, fadeOut = 0.4, dist = 170})
	elseif d.fase == "aviso" and d.pos then
		local dur = d.duracao or 0.5
		emPos(d.pos, B.droneSwell, {vol = 0.7, tom = 0.9, fadeIn = dur * 0.8, corte = dur + 0.6, fadeOut = 0.4, dist = 200, prio = 3})
		emPos(d.pos, sorteia(B.corrente), {vol = 0.5, tom = var(0.7, 0.05), corte = dur + 0.4, dist = 140})
	elseif d.fase == "erupcao" and d.pos then
		emPos(d.pos, sorteia(B.sub), {vol = 1.0, tom = var(0.8, 0.04), corte = 1.6, fadeOut = 0.5, dist = 300, min = 20, prio = 5})
		emPos(d.pos, sorteia(B.metal), {vol = 0.9, tom = var(0.7, 0.05), corte = 1.2, dist = 240, prio = 5})
		emPos(d.pos, B.correnteBate, {vol = 1.0, tom = var(0.85, 0.05), corte = 2.2, fadeOut = 0.6, dist = 230, prio = 4})
		emPos(d.pos, sorteia(B.espirito), {vol = 0.55, tom = var(0.8, 0.06), corte = 1.8, fadeOut = 0.5, dist = 200})
	elseif d.fase == "prender" then
		local r = raizA(d.alvo); if not r then return end
		tocar(r, B.guincho, {vol = 0.95, tom = var(0.8, 0.05), corte = 1.4, dist = 170, prio = 4})
		tocar(r, sorteia(B.corrente), {vol = 0.7, tom = var(0.75, 0.05), corte = 1.6, dist = 150})
		presoLaco[d.alvo] = true                                          -- chave = o alvo: o laço passa do fim do ataque
		laco(d.alvo, "preso", r, B.correnteLaco, {vol = 0.35, tom = var(0.7, 0.04), fadeIn = 0.4, corte = (d.duracao or 2.5) + 1.0, fadeOut = 0.5, dist = 120})
	elseif d.fase == "soltar" then
		if d.alvo and presoLaco[d.alvo] then presoLaco[d.alvo] = nil; pararLaco(d.alvo, "preso", 0.4) end
		local r = raizA(d.alvo)
		if r then emPos(r.Position, sorteia(B.corrente), {vol = 0.6, tom = var(0.9, 0.06), corte = 1.2, fadeOut = 0.4, dist = 140}) end
	end
end

-- ===== ECLIPSE DRACONICO: inicio (o ar e sugado para o ceu: succao magica + grito reverso + zumbido crescendo ate a
-- detonacao + rugido) -> detonar (dois golpes graves + baque + vozes; leito de zumbido e respiracao oca no centro
-- enquanto a area escura dura; rugidos do dragao em sequencia) -> marca (metal por alvo detonado) -> fimRugido (tudo
-- some aos poucos, exalacao).
local function eclipse(m, d)
	if d.fase == "inicio" then
		local t = novoTok(m, "Ecl")
		local det = d.detona or 2.15
		tocar(peito(m), B.succaoMagica, {vol = 0.9, tom = 0.6, corte = 2.3, dist = 300, prio = 4})
		depois(m, "Ecl", t, math.max(0, det - 1.3), function() tocar(peito(m), B.grito, {vol = 0.8, tom = 0.7, corte = 1.4, fadeOut = 0.2, dist = 320, prio = 4}) end)
		laco(m, "eclCarga", peito(m), B.droneSwell, {vol = 0.15, tom = 0.7, fadeIn = 0.2, corte = det + 0.6, fadeOut = 0.3, dist = 320})
		ajustarLaco(m, "eclCarga", 6, 1.25, det)
		tocar(cabeca(m), B.rugido, {vol = 1.0, tom = var(0.62, 0.03), corte = 2.6, fadeOut = 0.5, dist = 360, min = 25, prio = 5})
	elseif d.fase == "detonar" then
		local t = novoTok(m, "Ecl")
		pararLaco(m, "eclCarga", 0.15)
		local p = d.pos or m:GetPivot().Position
		emPos(p, B.sub[1], {vol = 1.3, tom = 0.7, corte = 2.5, fadeOut = 0.8, dist = 420, min = 30, prio = 6})
		emPos(p, B.sub[2], {vol = 1.0, tom = 0.55, corte = 2.5, fadeOut = 0.8, dist = 420, min = 30, prio = 6})
		emPos(p, B.baque, {vol = 1.0, tom = 0.7, corte = 1.4, dist = 320, prio = 5})
		emPos(p, sorteia(B.espirito), {vol = 0.8, tom = 0.65, corte = 2.0, fadeOut = 0.6, dist = 300, prio = 4})
		local dur = (d.duracao or 4) + 1.5
		local a = Instance.new("Attachment"); a.Name = "Som_Eclipse"; a.WorldPosition = p; a.Parent = workspace.Terrain
		game:GetService("Debris"):AddItem(a, dur + 2)
		laco(m, "eclArea", a, B.drone, {vol = 0.85, tom = 0.6, fadeIn = 0.4, corte = dur, fadeOut = 1.0, dist = 300, prio = 4})
		laco(m, "eclArea", a, B.respiro, {vol = 0.5, tom = 0.55, fadeIn = 0.8, corte = dur, fadeOut = 1.0, dist = 220})
		task.spawn(function()                                              -- o dragao segue rugindo enquanto a area dura
			task.wait(1.4)
			while valido(m, "Ecl", t) do
				tocar(cabeca(m), B.rugido, {vol = 0.75, tom = var(0.58, 0.04), corte = 2.2, fadeOut = 0.6, dist = 340, min = 22, prio = 4})
				task.wait(1.9 + math.random() * 0.5)
			end
		end)
	elseif d.fase == "marca" then
		local r = raizA(d.alvo); if not r then return end
		local k = math.clamp((d.marcas or 1) / 5, 0.3, 1)
		emPos(r.Position, sorteia(B.metal), {vol = 0.5 + 0.5 * k, tom = var(0.95 - 0.25 * k, 0.04), corte = 1.0, dist = 200, prio = 4})
	elseif d.fase == "fimRugido" then
		novoTok(m, "Ecl")
		pararLaco(m, "eclCarga", 0.2); pararLaco(m, "eclArea", 1.4)
		task.delay(0.4, function() if vivo(m) then tocar(cabeca(m), sorteia(B.expira), {vol = 0.6, tom = var(0.55, 0.04), corte = 1.8, fadeOut = 0.6, dist = 120}) end end)
	end
end

-- ===== PASSO SOMBRIO: o corpo se desfaz (succao + vozes passando) -> enquanto invisivel, so uma respiracao oca BAIXA e
-- curta de alcance (pista justa para quem esta perto) -> volta (vozes no sentido contrario + baque leve).
local passoChave = setmetatable({}, {__mode = "k"})
local function passo(m, d)
	if d.fase == "inicio" then
		novoTok(m, "Passo")
		local c = peito(m)
		tocar(c, sorteia(B.succao), {vol = 0.85, tom = var(0.9, 0.05), corte = 1.6, fadeOut = 0.3, dist = 180, prio = 4})
		tocar(c, sorteia(B.espirito), {vol = 0.7, tom = var(0.85, 0.05), corte = 1.8, fadeOut = 0.5, dist = 170})
		local dur = d.fim and math.max(0.5, d.fim - workspace:GetServerTimeNow()) or 5
		passoChave[m] = c                                                 -- chave = o osso (nao o dragao): passa do fim do ataque
		laco(c, "passo", c, B.respiro, {vol = 0.3, tom = 0.8, fadeIn = 0.6, corte = dur + 0.5, fadeOut = 0.5, dist = 60})
	elseif d.fase == "fim" then
		novoTok(m, "Passo")
		local c = peito(m)
		local k = passoChave[m]; passoChave[m] = nil; if k then pararLaco(k, "passo", 0.4) end
		tocar(c, sorteia(B.espirito), {vol = 0.6, tom = var(0.7, 0.05), corte = 1.6, fadeOut = 0.5, dist = 170})
		tocar(c, B.baque, {vol = 0.45, tom = var(0.9, 0.05), corte = 0.9, dist = 140})
	end
end

function S.evento(d)
	if d.hab == "Correntes" and d.fase == "soltar" then correntes(d.d, d); return end   -- soltar mesmo sem o dragao
	local m = d.d; if not (vivo(m) and m.PrimaryPart) then return end
	Mx.vigiar(m)
	if d.hab == "Sopro" then sopro(m, d)
	elseif d.hab == "Correntes" then correntes(m, d)
	elseif d.hab == "Eclipse" then eclipse(m, d)
	elseif d.hab == "PassoSombrio" then passo(m, d) end
end
return S
]======]
assert(loadstring(sons), "SonsSombra nao compila")
if not SS:FindFirstChild("Backup_Sons_Sombra_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Sons_Sombra_2026-11-04"; V:Clone().Parent = f; f.Parent = SS end
local M = CD:FindFirstChild("SonsSombra") or Instance.new("ModuleScript"); M.Name = "SonsSombra"; M.Source = sons; M.Parent = CD
V.Source = src
return "aplicado: SonsSombra (" .. #sons .. " bytes) + VFXSombra (" .. #src .. " bytes)"
