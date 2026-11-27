-- r13: marcha como 4o parametro de M.rodar (andar/trote/correr). Modulo TEMPORARIO de ensaio do Controle r11 (curvas andando) no Play do rpg_roblox. Vai para ServerStorage.R3_TesteTemporario
-- e e apagado no fim. Guia Workspace.Teste_LoboArtico pelo IA_Mover (andar) ate um ponto alvo e registra por quadro: pivo,
-- rumo, CtrlModo/CtrlCurva, bloqueios e a posicao MUNDIAL dos ossos dos dedos (Dedos_E/D, DedosPe_E/D) para medir o deslize
-- das patas apoiadas (fase = ponta a menos de 0,05 da sua altura minima; deslize = maior desvio horizontal em relacao ao meio).
local RS = game:GetService("RunService")
local M = {}
local tl = workspace.Teste_LoboArtico; local lobo = tl.LoboArtico_LOW
local ev = tl:WaitForChild("IA_Mover")
local OSSOS = {}
for _, d in ipairs(lobo:GetDescendants()) do if d:IsA("Bone") and (d.Name == "Dedos_E" or d.Name == "Dedos_D" or d.Name == "DedosPe_E" or d.Name == "DedosPe_D") then OSSOS[d.Name] = d end end
local REG, con, fimT = nil, nil, 0
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
function M.colocar(pos, rumoGraus)
	if con then con:Disconnect(); con = nil end
	ev:Fire(Vector3.zero, "andar"); task.wait(0.5)
	local r = math.rad(rumoGraus or 0)
	lobo:PivotTo(CFrame.new(pos) * CFrame.Angles(0, r, 0)); return "ok"
end
-- alvoFn(t) -> Vector3 (ponto alvo no mundo)
function M.rodar(nome, alvoFn, dur, marcha)
	marcha = marcha or "andar"
	if con then con:Disconnect() end
	REG = {nome = nome, q = {}, t0 = os.clock(), dts = {}}; fimT = os.clock() + dur
	con = RS.Heartbeat:Connect(function(dt)
		local t = os.clock() - REG.t0
		if os.clock() > fimT then ev:Fire(Vector3.zero, "andar"); con:Disconnect(); con = nil; REG.fim = true; return end
		local pv = lobo:GetPivot(); local alvo = alvoFn(t)
		ev:Fire(plano(alvo - pv.Position), marcha)
		local f = plano(pv.LookVector).Unit
		local reg = {t = t, x = pv.Position.X, y = pv.Position.Y, z = pv.Position.Z, rumo = math.deg(math.atan2(-f.X, -f.Z)),
			modo = (lobo:GetAttribute("CtrlModo") or "?") .. "/" .. tostring(lobo:GetAttribute("CtrlMarcha")), curva = lobo:GetAttribute("CtrlCurva"), bloq = lobo:GetAttribute("CtrlBloqueio"), vel = lobo:GetAttribute("VelAtual"), p = {}}
		local d = plano(alvo - pv.Position); reg.erro = (d.Magnitude > 0.1) and math.deg(math.atan2(f.X * d.Z - f.Z * d.X, f.X * d.X + f.Z * d.Z)) or 0
		reg.dist = d.Magnitude
		for n, b in pairs(OSSOS) do local w = b.TransformedWorldCFrame.Position; reg.p[n] = {w.X, w.Y, w.Z} end
		table.insert(REG.q, reg); table.insert(REG.dts, dt)
	end)
	return "rodando " .. nome
end
function M.pronto() return REG and REG.fim == true end
function M.resultado()
	local Q = REG.q; local out = {"cenario " .. REG.nome .. " quadros=" .. #Q}
	-- sequencia de clipes de andar
	local seq, ult = {}, nil
	for _, r in ipairs(Q) do local c = (r.modo or "?") .. ":" .. tostring(r.curva or "-"); if c ~= ult then table.insert(seq, string.format("%.1f %s", r.t, c)); ult = c end end
	table.insert(out, "seq: " .. table.concat(seq, " | "))
	-- trocas de modo e bloqueios
	local trocas, bl = 0, {}
	for i = 2, #Q do if Q[i].modo ~= Q[i - 1].modo then trocas += 1 end; if Q[i].bloq and Q[i].bloq ~= Q[i - 1].bloq then table.insert(bl, Q[i].bloq) end end
	table.insert(out, "trocas_modo=" .. trocas .. " bloqueios=" .. #bl .. (bl[1] and (" ex: " .. bl[1]) or ""))
	-- erro de rumo no fim, primeiro alinhamento
	local alinh
	for _, r in ipairs(Q) do if not alinh and math.abs(r.erro) < 9 and r.t > 0.5 then alinh = r.t end end
	table.insert(out, string.format("erro_final=%.1f dist_final=%.1f alinhou_em=%s s", Q[#Q].erro, Q[#Q].dist, alinh and string.format("%.1f", alinh) or "nao"))
	-- giro do pivo sem deslocamento (giro no lugar): graus girados com vel < 0,3
	local giroParado = 0
	for i = 2, #Q do
		local dr = (Q[i].rumo - Q[i - 1].rumo + 540) % 360 - 180
		local dx = math.sqrt((Q[i].x - Q[i - 1].x) ^ 2 + (Q[i].z - Q[i - 1].z) ^ 2)
		if dx < 0.3 * (Q[i].t - Q[i - 1].t) then giroParado += math.abs(dr) end
	end
	table.insert(out, string.format("giro_com_pivo_parado=%.1f graus", giroParado))
	-- deslize das patas (osso dos dedos)
	for n in pairs(OSSOS) do
		local ymin = math.huge; for _, r in ipairs(Q) do ymin = math.min(ymin, r.p[n][2]) end
		local segs, cur = {}, {}
		for i, r in ipairs(Q) do if r.p[n][2] < ymin + 0.05 then table.insert(cur, i) elseif #cur > 0 then table.insert(segs, cur); cur = {} end end
		if #cur > 0 then table.insert(segs, cur) end
		local lst, pior, acima = {}, 0, 0
		for _, sg in ipairs(segs) do
			if #sg >= 6 then
				local m = Q[sg[math.floor(#sg / 2) + 1]].p[n]; local mx = 0
				for _, i in ipairs(sg) do local p = Q[i].p[n]; mx = math.max(mx, math.sqrt((p[1] - m[1]) ^ 2 + (p[3] - m[3]) ^ 2)) end
				table.insert(lst, string.format("%.3f", mx)); pior = math.max(pior, mx); if mx > 0.05 then acima += 1 end
			end
		end
		table.insert(out, string.format("%s fases=%d pior=%.3f >0,05=%d [%s]", n, #lst, pior, acima, table.concat(lst, " ")))
	end
	local s = 0; for _, d in ipairs(REG.dts) do s += d end
	table.insert(out, string.format("dt_medio_servidor=%.1f ms", s / math.max(1, #REG.dts) * 1000))
	return table.concat(out, "\n")
end
function M.trajeto(passo)
	local o = {}
	for i = 1, #REG.q, passo or 15 do local r = REG.q[i]; table.insert(o, string.format("%.1f:%.1f,%.1f,%.0f,%s", r.t, r.x, r.z, r.rumo, tostring(r.curva or r.modo))) end
	return table.concat(o, " ")
end
return M
