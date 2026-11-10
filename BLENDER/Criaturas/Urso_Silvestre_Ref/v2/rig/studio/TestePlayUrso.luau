-- TestePlayUrso (ModuleScript em ServerStorage.Urso_v2_Piloto) - toca os clipes do urso durante o PLAY, SEM publicar:
-- AnimationClipProvider:RegisterAnimationClip(kfs) gera um id temporario valido so no Studio.
-- Um ensaio por vez: tocar() sempre chama parar() antes (desliga a conexao do deslocamento, para as faixas,
-- volta o modelo a posicao inicial). Ao encerrar o Play o DataModel de teste e descartado.
-- Deslocamento/giro = PARAMETROS TECNICOS da simulacao do Blender (Andar 3,23; Corrida 16,8 studs/s; Virar +-60 graus/s;
-- Arrancada/Frenagem perfil v(t) do manifesto), NAO regras do jogo. Tudo amarrado ao TEMPO DA FAIXA, nunca a um relogio.
-- Lote 2 (04/11): modos "perfil" (v(t) por quadro, integrado pelo trapezio como o qa_urso.py, v linear entre quadros)
-- e "giro" (em torno da cabeca da Raiz, como a simulacao do Blender); sequencia() encadeia clipes com mistura.
local RS = game:GetService("RunService")
local ACP = game:GetService("AnimationClipProvider")
local M = {}
local modelo = workspace:WaitForChild("Teste_Urso_v2"):WaitForChild("Urso_Silvestre_v2_Piloto")
local PASTA = game.ServerStorage.Urso_v2_Piloto
local ANIM = PASTA.Animacoes
local PIVO0 = modelo:GetPivot()
local RAIZ0 = PIVO0:PointToObjectSpace(modelo:FindFirstChild("Raiz", true).WorldPosition)   -- centro do giro (repouso)
local estado = {con = nil, faixa = nil, ids = {}, faixas = {}}

local function animator()
	local ac = modelo:FindFirstChildOfClass("AnimationController")
	local an = ac:FindFirstChildOfClass("Animator") or Instance.new("Animator")
	an.Parent = ac
	return an
end

-- parametros do manifesto gravados pelo empacotador (Dados_Clipes.Perfis_<clipe>): v, giro, perfil por quadro
local function params(nome)
	local sv = PASTA.Dados_Clipes:FindFirstChild("Perfis_" .. nome)
	local p = {v = 0, giro = 0, perfil = nil}
	if not sv then return p end
	for k, val in string.gmatch(sv.Value, "(%a+)=([^;]*)") do
		if k == "perfil" then
			if val ~= "" then p.perfil = {}; for x in string.gmatch(val, "[^,]+") do table.insert(p.perfil, tonumber(x)) end end
		else p[k] = tonumber(val) end
	end
	if p.perfil then                                   -- s acumulado no inicio de cada quadro (trapezio)
		local acum = {0}
		for q = 2, #p.perfil do acum[q] = acum[q - 1] + 0.5 * (p.perfil[q] + p.perfil[q - 1]) / 30 end
		p.acum = acum
	end
	return p
end
M.params = params

-- s(t) para o perfil: v linear entre quadros -> integral exata do trecho
local function sPerfil(p, t)
	local f = t * 30; local i = math.clamp(math.floor(f), 0, #p.perfil - 1); local u = math.clamp(f - i, 0, 1)
	local v0 = p.perfil[i + 1]; local v1 = p.perfil[math.min(i + 2, #p.perfil)]
	return p.acum[i + 1] + (v0 * u + 0.5 * (v1 - v0) * u * u) / 30
end
M.sPerfil = sPerfil

function M.pivoEm(s, ang)                           -- pivo para deslocamento s (frente) e giro ang (rad) na Raiz
	local c = CFrame.new(RAIZ0)
	return PIVO0 * c * CFrame.Angles(0, ang, 0) * c:Inverse() + PIVO0.LookVector * s
end

function M.parar()
	if estado.con then estado.con:Disconnect(); estado.con = nil end
	for _, f in ipairs(animator():GetPlayingAnimationTracks()) do f:Stop(0) end
	estado.faixa = nil
	modelo:PivotTo(PIVO0)
	-- o Animator deixa os ossos na ultima pose quando a faixa para (medido 04/11 no Comer parado no meio do loop):
	-- volta ao repouso para que o ensaio seguinte comece limpo
	for _, b in ipairs(modelo:GetDescendants()) do if b:IsA("Bone") then b.Transform = CFrame.identity end end
end

local function faixa(nome)
	estado.ids[nome] = estado.ids[nome] or ACP:RegisterAnimationClip(ANIM[nome])
	if not estado.faixas[nome] then
		local a = Instance.new("Animation"); a.AnimationId = estado.ids[nome]
		estado.faixas[nome] = animator():LoadAnimation(a)
	end
	return estado.faixas[nome]
end

local function esperarCarga(f)                      -- num Play novo a 1a faixa demora a carregar
	local c0 = os.clock()
	while f.Length == 0 and os.clock() - c0 < 5 do task.wait() end
end

-- modo: nil = parametros do manifesto (Perfis_<clipe>); vel/giro explicitos sobrepoem. dur = tempo de clipe (s).
function M.tocar(nome, vel, dur, velocidadeClipe, giro)
	M.parar()
	local f = faixa(nome)
	f:Play(0, 1, velocidadeClipe or 1); f.TimePosition = 0       -- faixa em cache: sempre do inicio
	estado.faixa = f
	esperarCarga(f)
	local p = params(nome)
	vel = vel or p.v; giro = giro or p.giro
	if (vel and vel ~= 0) or (giro and giro ~= 0) or p.perfil then
		local acc, ult = 0, f.TimePosition
		estado.con = RS.Stepped:Connect(function()
			local tp = f.TimePosition; local d = tp - ult; if d < -0.5 * f.Length then d += f.Length end; ult = tp
			acc += math.max(d, 0)
			if dur and acc > dur then estado.con:Disconnect(); estado.con = nil; return end
			local s = p.perfil and sPerfil(p, math.min(tp, f.Length)) or (vel or 0) * acc
			modelo:PivotTo(M.pivoEm(s, math.rad(giro or 0) * acc))
		end)
	end
	return {id = estado.ids[nome], duracao = f.Length, loop = f.Looped}
end

-- sequencia Arrancada -> Corrida (n ciclos) -> Frenagem, com mistura (fade) de 'mistura' s entre clipes.
-- Deslocamento: cada faixa contribui com v_i(t_i) * (avanco do TimePosition dela), ponderado pelo peso atual
-- (WeightCurrent); nenhum relogio independente. Registra amostras para a analise.
function M.sequencia(ciclosCorrida, mistura, amostrar)
	M.parar()
	local nomes = {"Urso_Arrancada", "Urso_Corrida", "Urso_Frenagem"}
	local P = {}; for _, n in ipairs(nomes) do P[n] = params(n); esperarCarga(faixa(n)) end
	local fa, fc, ff = faixa(nomes[1]), faixa(nomes[2]), faixa(nomes[3])
	local function vDe(n, f)
		local p = P[n]; local t = f.TimePosition
		if p.perfil then
			local i = math.clamp(math.floor(t * 30), 0, #p.perfil - 1); local u = t * 30 - i
			return p.perfil[i + 1] + (p.perfil[math.min(i + 2, #p.perfil)] - p.perfil[i + 1]) * math.clamp(u, 0, 1)
		end
		return p.v or 0
	end
	local s, fase, reg = 0, "Arrancada", {}
	local trocas = {}
	local FX = {fa, fc, ff}; local ultTP = {0, 0, 0}
	fa:Play(0); fa.TimePosition = 0; estado.faixa = fa
	estado.con = RS.Stepped:Connect(function()
		local ds, v, soma = 0, 0, 0
		for i, f in ipairs(FX) do
			local tp = f.TimePosition; local d = tp - ultTP[i]
			if d < -0.5 * f.Length then d += f.Length end          -- volta do loop
			if d < 0 or d > 0.25 then d = 0 end                   -- reinicio da faixa (Play/TimePosition = 0)
			ultTP[i] = tp
			-- so faixas tocando: uma faixa parada continua informando WeightCurrent = 1 (medido 04/11)
			local w = f.IsPlaying and math.max(f.WeightCurrent, 1e-3) or 0
			if w > 0 then local vi = vDe(nomes[i], f); ds += w * vi * d; v += w * vi; soma += w end
		end
		if soma > 0 then ds /= soma; v /= soma end
		s += ds
		modelo:PivotTo(M.pivoEm(s, 0))
		if amostrar then table.insert(reg, {t = os.clock(), fase = fase, v = v, s = s, wa = fa.WeightCurrent, wc = fc.WeightCurrent, wf = ff.WeightCurrent}) end
	end)
	-- Arrancada ate (Length - mistura); a Corrida entra EM FASE em (Length_C - mistura): as duas chegam juntas ao ponto
	-- de emenda (ultimo quadro da Arrancada = quadro 0 da Corrida). Medido 04/11: entrar no quadro 0 cruzava passadas
	-- defasadas (osso a 28,7 studs/s contra 19,7 no clipe sozinho).
	while fa.TimePosition < fa.Length - mistura - 1e-3 and fa.IsPlaying do task.wait() end
	table.insert(trocas, {"Arrancada->Corrida", fa.TimePosition}); fase = "mistura A->C"
	fc:Play(mistura); fc.TimePosition = math.max(fc.Length - mistura - (fa.Length - mistura - fa.TimePosition), 0); fa:Stop(mistura)
	ultTP[2] = fc.TimePosition                            -- a entrada nao conta como avanco (medido 04/11: salto do pivo)
	task.wait(mistura); fase = "Corrida"
	local voltas = 0; local ult = fc.TimePosition
	while voltas < ciclosCorrida do
		task.wait(); if fc.TimePosition < ult then voltas += 1 end; ult = fc.TimePosition
	end
	-- Frenagem comeca na pose do quadro 0 da Corrida: entra no MESMO tempo em que a Corrida esta (a volta do loop so e
	-- detectada um passo depois). Medido 04/11: entrar no quadro 0 com a Corrida em 0,04-0,08 s escorregava a pata 0,23.
	table.insert(trocas, {"Corrida->Frenagem", fc.TimePosition}); fase = "mistura C->F"
	ff:Play(mistura); ff.TimePosition = fc.TimePosition; fc:Stop(mistura)
	ultTP[3] = ff.TimePosition
	task.wait(mistura); fase = "Frenagem"
	while ff.IsPlaying do task.wait() end
	if estado.con then estado.con:Disconnect(); estado.con = nil end
	return {trocas = trocas, deslocamento = s, amostras = reg}   -- o pivo fica no fim do trajeto; parar() o devolve
end

-- cadeia de posturas/acoes (lote 3, 04/11): toca os clipes um apos o outro SEM reiniciar a pose (o seguinte entra
-- por mistura sobre o anterior). passos = {{nome, ciclos = n (loops, em tempo de faixa), segurar = s}}.
-- 'segurar': a faixa e congelada (AdjustSpeed 0) NO PASSO de animacao (Stepped), antes de chegar ao fim, em
-- Length - 0,0005 -> a pose terminal de Sentar/Deitar fica sustentada pela propria faixa, sem loop e sem voltar
-- sozinha; o seguinte entra por mistura e a faixa congelada sai (Stop com fade). As trocas tambem sao decididas no
-- passo. Medido 04/11: congelar pelo task.wait chegava depois do fim da faixa -> a faixa ja encerrada nao segurava a
-- pose e o fade do clipe seguinte misturava com o repouso (osso a 24-32 studs/s). Sem deslocamento (pivo fixo).
function M.cadeia(passos, mistura, aoPasso)
	M.parar()
	local trocas, ant = {}, nil
	for _, p in ipairs(passos) do esperarCarga(faixa(p[1])) end
	for i, p in ipairs(passos) do
		local f = faixa(p[1]); local ultimo = (i == #passos)
		local antInfo = ant and string.format("anterior tocando=%s tp=%.3f/%.3f", tostring(ant.IsPlaying), ant.TimePosition, ant.Length) or ""
		f:Play(ant and mistura or 0, 1, p.vel or 1); f.TimePosition = 0
		if ant then ant:Stop(mistura) end
		estado.faixa = f
		table.insert(trocas, {p[1], os.clock(), antInfo})
		if aoPasso then aoPasso(i, p[1], f) end
		local pronto, acc, ult = false, 0, 0
		local con = RS.Stepped:Connect(function(_, dt)
			if pronto then return end
			local tp = f.TimePosition
			if f.Looped then
				local d = tp - ult; if d < -0.5 * f.Length then d += f.Length end; ult = tp; acc += math.max(d, 0)
				if acc + dt >= (p.ciclos or 1) * f.Length - (ultimo and 0 or mistura) then pronto = true end
			elseif p.segurar then
				if tp + 2 * dt >= f.Length then f:AdjustSpeed(0); f.TimePosition = f.Length - 0.0005; pronto = true end
			else
				if tp + dt >= f.Length - (ultimo and 0 or mistura) then pronto = true end
			end
		end)
		while not pronto do task.wait() end
		con:Disconnect()
		if p.segurar then
			table.insert(trocas, {p[1] .. " (pose terminal sustentada; tocando=" .. tostring(f.IsPlaying) .. ")", os.clock(), ""})
			task.wait(p.segurar)
		elseif ultimo and not f.Looped then
			while f.IsPlaying do task.wait() end
		end
		ant = f
	end
	return trocas
end

function M.info()
	local f = estado.faixa
	return {tocando = f and f.IsPlaying or false, tempo = f and f.TimePosition or 0, conexao = estado.con ~= nil,
		pivo = modelo:GetPivot().Position, faixas = #animator():GetPlayingAnimationTracks()}
end
return M
