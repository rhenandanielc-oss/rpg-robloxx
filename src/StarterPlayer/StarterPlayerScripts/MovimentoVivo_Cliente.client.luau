-- MovimentoVivo_Cliente (LocalScript, StarterPlayerScripts) — camada DINAMICA de movimento das criaturas (so visual).
-- As animacoes (clipes) dao o ciclo base (batidas, passos, respiracao). Esta camada soma, a cada quadro, a reacao ao
-- movimento REAL do modelo, que nenhum clipe fixo consegue: pescoco/cabeca entram na curva, coluna dobra, cauda abre
-- para fora com atraso (molas por segmento), pescoco acompanha subida/descida, patas reagem a aceleracao/freada, asa
-- interna da curva baixa, cabeca segue a camera do cavaleiro e, solta e parada, olha jogadores proximos.
-- Nada disso vai ao servidor nem altera combate/fisica. Perfis por rig em ReplicatedStorage.MovimentoVivo.Perfis.
local RS = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Perfis = require(RS:WaitForChild("MovimentoVivo"):WaitForChild("Perfis"))
local cam = workspace.CurrentCamera
local eu = Players.LocalPlayer
local rad, clamp = math.rad, math.clamp

local function mola(s, alvo, k, dt)
	local w = math.sqrt(k)
	s.v += (k * (alvo - s.x) - 2 * w * 0.85 * s.v) * dt
	s.x += s.v * dt
	return s.x
end
local function novaMola() return {x = 0, v = 0} end

local estados = {}
local function preparar(m, P)
	local ossos = {}
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") then ossos[d.Name] = d end end
	local function lista(nomes) local t = {}; for i, n in ipairs(nomes or {}) do t[i] = ossos[n] end; return t end
	local e = {
		P = P, m = m,
		pescoco = lista(P.pescoco), cabeca = ossos[P.cabeca], coluna = lista(P.coluna), cauda = lista(P.cauda),
		ombroE = ossos[P.ombros.E], ombroD = ossos[P.ombros.D], patasD = lista(P.patasD), patasT = lista(P.patasT),
		molas = {}, ultCF = m:GetPivot(), ultVel = Vector3.zero, t = 0,
	}
	for _, n in ipairs({"pYaw", "pPitch", "cYaw", "cPitch", "colYaw", "colPitch", "patas", "asa", "oYaw", "oPitch"}) do e.molas[n] = novaMola() end
	e.caudaLat, e.caudaVert = {}, {}
	for i = 1, #e.cauda do e.caudaLat[i] = novaMola(); e.caudaVert[i] = novaMola() end
	return e
end

local atual   -- estado do modelo em processamento: guarda quanto esta camada somou em cada osso neste quadro
local function girar(osso, eixoMundo, ang)
	if not osso or math.abs(ang) < 1e-4 then return end
	local local_ = osso.TransformedWorldCFrame:VectorToObjectSpace(eixoMundo)
	local R = CFrame.fromAxisAngle(local_, ang)
	osso.Transform = osso.Transform * R
	if atual then atual.soma[osso] = (atual.soma[osso] or CFrame.identity) * R end
end

local function jogadorProximo(m, dist)
	local p = m:GetPivot().Position; local melhor, dm = nil, dist
	for _, pl in ipairs(Players:GetPlayers()) do
		local h = pl.Character and pl.Character:FindFirstChild("Head")
		if h then local d = (h.Position - p).Magnitude; if d < dm then melhor, dm = h, d end end
	end
	return melhor
end

local function passo(e, dt)
	local P, m = e.P, e.m
	-- a soma vale para UM quadro sobre a pose do clipe. Se nenhum clipe reescreveu o osso desde o quadro anterior
	-- (modelo sem animacao tocando), desfaz a soma anterior antes de somar de novo: antes a rotacao acumulava a cada
	-- quadro e a cabeca girava sem parar perto do jogador ("cabeca louca", usuario 31/10)
	for osso, r in pairs(e.ultSoma or {}) do
		if osso.Transform == r.T then osso.Transform = r.T * r.soma:Inverse() end
	end
	e.soma = {}; atual = e
	local cf = m:GetPivot()
	-- movimento real: o servidor move o modelo ancorado e o pivo chega em degraus (~30 Hz, metade dos quadros sem
	-- mudar). As grandezas so sao recalculadas quando o pivo muda, com o tempo ACUMULADO desde a ultima mudanca, e
	-- suavizadas (senao alternam 0 / dobro e a mola fica com metade do efeito)
	e.acum = (e.acum or 0) + dt
	local mudou = (cf.Position - e.ultCF.Position).Magnitude > 1e-4 or cf.LookVector:Dot(e.ultCF.LookVector) < 0.9999999
	if mudou or e.acum > 0.25 then
		local T = math.max(e.acum, 1e-3)
		local f0, f1 = e.ultCF.LookVector, cf.LookVector
		local h0, h1 = Vector3.new(f0.X, 0, f0.Z), Vector3.new(f1.X, 0, f1.Z)
		local g = 0
		if h0.Magnitude > 1e-3 and h1.Magnitude > 1e-3 then
			h0, h1 = h0.Unit, h1.Unit
			g = math.atan2(h0:Cross(h1).Y, h0:Dot(h1)) / T                                -- rad/s, + = esquerda
		end
		local v = (cf.Position - e.ultCF.Position) / T
		if v.Magnitude > 200 then v = e.vel or Vector3.zero end                          -- teleporte: ignora
		local s = math.min(1, T * 10)
		e.giro = (e.giro or 0) + (g - (e.giro or 0)) * s
		local velAnt = (e.vel or v).Magnitude
		e.vel = (e.vel or v):Lerp(v, s)
		-- aceleracao = variacao da RAPIDEZ suavizada (a direcao girando na curva nao conta como acelerar)
		local a = (e.vel.Magnitude - velAnt) / T
		e.acel = (e.acel or 0) + (a - (e.acel or 0)) * math.min(1, T * 4)
		e.ultCF, e.acum = cf, 0
	end
	local giro, vel, acel = e.giro or 0, e.vel or Vector3.zero, e.acel or 0
	local horiz = Vector3.new(vel.X, 0, vel.Z).Magnitude
	local traj = (vel.Magnitude > 3) and math.deg(math.atan2(vel.Y, horiz)) or 0
	local noAr = m:GetAttribute("MontariaModo") == "voo" or m:GetAttribute("NoAr") == true
	local cav = m:GetAttribute("Cavaleiro")

	local oYaw, oPitch = 0, 0
	local alvoDir
	if m:GetAttribute("AlvoGolpe") and e.cabeca then                -- PATCH_ARREMETIDA_5S: mordida da investida encara o alvo
		alvoDir = (m:GetAttribute("AlvoGolpe") - e.cabeca.TransformedWorldCFrame.Position).Unit
	elseif cav and eu and cav == eu.UserId then alvoDir = m:GetAttribute("MiraLocal") or cam.CFrame.LookVector
	elseif not cav and m:GetAttribute("AlvoOlhar") and e.cabeca then
		-- IA (sistema universal 01/11): rugido direcionado, intimidacao e curiosidade encaram o alvo (tambem andando)
		alvoDir = (m:GetAttribute("AlvoOlhar") - e.cabeca.TransformedWorldCFrame.Position).Unit
	elseif not cav and horiz < 2 then
		local h = jogadorProximo(m, P.olharDist)
		local cab = e.cabeca
		if h and cab then alvoDir = (h.Position - cab.TransformedWorldCFrame.Position).Unit end
	end
	-- PATCH_MERGULHO_PICADO (10/11): no picado/freio o clipe manda no pescoco (cabeca na direcao da queda): sem olhar a
	-- mira, sem curvar pela trajetoria vertical e sem giro (rumo travado); as molas voltam ao neutro suave
	local fasePic = m:GetAttribute("MergulhoFase")
	if fasePic and fasePic ~= "recuperacao" then alvoDir = nil; traj = 0; giro = 0 end
	if alvoDir then
		local rel = cf:VectorToObjectSpace(alvoDir)
		oYaw = clamp(math.deg(math.atan2(-rel.X, -rel.Z)), -P.maxOlharYaw, P.maxOlharYaw) * P.olharYaw
		oPitch = clamp(math.deg(math.asin(clamp(rel.Y, -1, 1))), -P.maxOlharPitch, P.maxOlharPitch) * P.olharPitch
	end

	local M = e.molas
	local gC = clamp(giro, -1.5, 1.5)
	local yawP = mola(M.pYaw, clamp(gC * P.curvaPescoco + oYaw, -P.maxPescoco, P.maxPescoco), P.molaPescoco, dt)
	local pitP = mola(M.pPitch, clamp(traj * P.trajPescoco, -P.maxTraj, P.maxTraj) + oPitch, P.molaPescoco, dt)
	local yawC = mola(M.cYaw, gC * P.curvaCabeca + oYaw * 0.3, P.molaCabeca, dt)
	local pitC = mola(M.cPitch, oPitch * 0.3, P.molaCabeca, dt)
	local yawCol = mola(M.colYaw, clamp(gC * P.curvaColuna, -P.maxColuna, P.maxColuna), P.molaColuna, dt)
	local pitCol = mola(M.colPitch, clamp(-acel * P.acelTorax, -6, 6), P.molaColuna, dt)
	local patas = mola(M.patas, clamp(acel * P.acelPatas, -P.maxAcel, P.maxAcel), P.molaPatas, dt)
	local asa = mola(M.asa, noAr and clamp(gC * P.curvaAsa, -P.maxAsa, P.maxAsa) or 0, P.molaAsa, dt)
	e.dbg = (e.dbg or 0) + dt
	if e.dbg > 0.25 then                                   -- leitura para testes (atributo LOCAL, nao replica)
		e.dbg = 0
		m:SetAttribute("MV_dbg", string.format("giro=%.2f traj=%.0f acel=%.1f pesc=%.1f col=%.1f asa=%.1f olhar=%.1f",
			giro, traj, acel, yawP, yawCol, asa, oYaw))
	end

	local U, R = cf.UpVector, cf.RightVector
	for i, o in ipairs(e.coluna) do
		local k = P.divColuna[i] or 0
		girar(o, U, rad(yawCol * k)); girar(o, R, rad(pitCol * k))
	end
	for i, o in ipairs(e.pescoco) do
		local k = P.divPescoco[i] or 0
		girar(o, U, rad(yawP * k)); girar(o, R, rad(pitP * k))
	end
	girar(e.cabeca, U, rad(yawC)); girar(e.cabeca, R, rad(pitC))
	for i, o in ipairs(e.cauda) do
		local kM = P.molaCauda[i] or 6
		local lat = mola(e.caudaLat[i], clamp(-gC * P.curvaCauda, -P.maxCaudaSeg, P.maxCaudaSeg), kM, dt)
		local ver = mola(e.caudaVert[i], clamp(traj * P.trajCauda, -8, 8) + (noAr and clamp(acel * 0.12, -4, 4) or 0), kM, dt)
		girar(o, U, rad(lat)); girar(o, R, rad(ver))
	end
	local gp = noAr and 1 or 0.35
	for _, o in ipairs(e.patasD) do girar(o, R, rad(-patas * gp)) end
	for _, o in ipairs(e.patasT) do girar(o, R, rad(-patas * gp * 1.2)) end
	if math.abs(asa) > 0.05 then
		local F = cf.LookVector
		girar(e.ombroE, F, rad(asa * P.sinalAsa)); girar(e.ombroD, F, rad(asa * P.sinalAsa))
	end
	local ult = {}
	for osso, soma in pairs(e.soma) do ult[osso] = {T = osso.Transform, soma = soma} end
	e.ultSoma = ult; atual = nil
end

local function registrar(m)
	if estados[m] or not m:IsA("Model") then return end
	local nome = m:GetAttribute("PerfilMovimento"); local P = nome and Perfis[nome]
	if not P then return end
	estados[m] = preparar(m, P)
	m.AncestryChanged:Connect(function(_, pai) if not pai then estados[m] = nil end end)
end
for _, m in ipairs(workspace:GetChildren()) do registrar(m) end
workspace.ChildAdded:Connect(function(m) task.defer(registrar, m) end)

_G.MovimentoVivo = estados   -- depuracao (cliente)
RunService.PreSimulation:Connect(function(dt)
	dt = math.min(dt, 1 / 20)
	local cp = cam.CFrame.Position
	for m, e in pairs(estados) do
		if m.Parent and m.PrimaryPart and (m.PrimaryPart.Position - cp).Magnitude < e.P.distMax then
			local ok, err = pcall(passo, e, dt)
			if not ok and not e.avisado then e.avisado = true; warn("MovimentoVivo: " .. tostring(err)) end
		end
	end
end)
