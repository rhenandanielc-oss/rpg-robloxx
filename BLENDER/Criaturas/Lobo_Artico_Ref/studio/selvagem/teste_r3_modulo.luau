-- ModuleScript TEMPORARIO do ensaio da IA r3 (ServerStorage.R3_TesteTemporario; apagar ao fim do teste). Uso no Play
-- (Server): local R = require(game.ServerStorage.R3_TesteTemporario)(); R.rodar("tunel_para"); ...; R.resumo("tunel_para")
return function()
	local Players = game:GetService("Players")
	local PFS = game:GetService("PathfindingService")
	if _G.R3T then return _G.R3T end
	local R = {}; _G.R3T = R
	local raiz = workspace.Criaturas_IA.Lobos_Articos
	R.alc = raiz:WaitForChild("Alcateia_Floresta")
	local hab = workspace.Tundra_Congelada.Habitats.Ecologia_Fauna.Lobo_Artico.Alcateia_Floresta
	local function P(n) local p = hab:FindFirstChild(n, true); return p and p.Position end
	R.abrigo, R.entrada, R.descanso = P("Abrigo_Filhotes"), P("Entrada_Toca"), P("Descanso_Toca")
	R.res = {}
	local function jog() local j = Players:GetPlayers()[1]; return j, j and j.Character end
	R.jog = jog
	local function plano(v) return Vector3.new(v.X, 0, v.Z) end
	R.plano = plano
	function R.lobos()
		local l = {}
		for _, f in ipairs(R.alc:GetChildren()) do local o = f:FindFirstChild("LoboArtico_LOW"); if o then table.insert(l, {pasta = f, lobo = o}) end end
		return l
	end
	function R.medir()
		local _, c = jog(); local r = c and c:FindFirstChild("HumanoidRootPart"); local h = c and c:FindFirstChildOfClass("Humanoid")
		local s = {t = os.clock(), tensao = R.alc:GetAttribute("Tensao"), motivo = R.alc:GetAttribute("Motivo"), vida = h and h.Health, lobos = {}}
		if r then s.dD = (r.Position - R.descanso).Magnitude; s.p = r.Position end
		for _, m in ipairs(R.lobos()) do
			local e = m.lobo:GetAttribute("Escala") or 1; local pv = m.lobo:GetPivot()
			local fr = plano(pv.LookVector).Unit; local foc = pv.Position + fr * 6.2 * e
			local x = {papel = m.pasta:GetAttribute("Papel"), est = m.pasta:GetAttribute("IA_Estado"), cont = m.pasta:GetAttribute("IA_Contato"), p = pv.Position}
			if r then
				x.dF = plano(r.Position - foc).Magnitude
				local rel = plano(r.Position - pv.Position); local al = rel:Dot(fr); local la = math.abs(rel:Dot(Vector3.new(-fr.Z, 0, fr.X)))
				x.dentro = al > -0.8 * e and al < 6.0 * e and la < 1.3 * e
			end
			table.insert(s.lobos, x)
		end
		return s
	end
	local path = PFS:CreatePath({AgentRadius = 1.5, AgentHeight = 5, AgentCanJump = true, WaypointSpacing = 4})
	path:ComputeAsync(R.entrada + Vector3.new(0, 2, 0), R.descanso + Vector3.new(0, 2, 0))
	R.tunel = {}
	if path.Status == Enum.PathStatus.Success then for _, w in ipairs(path:GetWaypoints()) do table.insert(R.tunel, w.Position) end end
	function R.idxDist(d)
		local bi, bd = 1, math.huge
		for i, q in ipairs(R.tunel) do local x = math.abs((q - R.descanso).Magnitude - d); if x < bd then bi, bd = i, x end end
		return bi
	end
	function R.andarTunel(dAlvo, vel)
		local _, c = jog(); local h = c:FindFirstChildOfClass("Humanoid"); h.WalkSpeed = vel or 6
		local hrp = c.HumanoidRootPart
		local iAt, dm = 1, math.huge
		for i, q in ipairs(R.tunel) do local d = (q - hrp.Position).Magnitude; if d < dm then iAt, dm = i, d end end
		local iAl = R.idxDist(dAlvo); local passo = iAl >= iAt and 1 or -1
		for i = iAt, iAl, passo do
			local t0 = os.clock()
			repeat h:MoveTo(R.tunel[i]); task.wait(0.1) until plano(hrp.Position - R.tunel[i]).Magnitude < 2.5 or os.clock() - t0 > 4
		end
	end
	function R.irReto(p, vel)
		local _, c = jog(); local h = c:FindFirstChildOfClass("Humanoid"); h.WalkSpeed = vel or 6
		local t0 = os.clock()
		repeat h:MoveTo(p); task.wait(0.1) until plano(c.HumanoidRootPart.Position - p).Magnitude < 2.5 or os.clock() - t0 > 20
	end
	function R.pos(p) local _, c = jog(); c:PivotTo(CFrame.new(p + Vector3.new(0, 3, 0))); c.HumanoidRootPart.AssemblyLinearVelocity = Vector3.zero end
	function R.resetar()
		for _, k in ipairs({"AlvoId", "AlvoMotivo", "AlvoAte", "AlvoJogador", "Tensao", "TensaoId", "TensaoPos", "Motivo", "AvisoDesde", "InvestigarPos", "InvestigarAte"}) do R.alc:SetAttribute(k, nil) end
		local _, c = jog(); local h = c:FindFirstChildOfClass("Humanoid"); h.MaxHealth = 1e6; h.Health = 1e6
	end
	R.ROT = {}
	R.ROT.tunel_para = function() R.pos(R.tunel[1]); task.wait(3); R.andarTunel(45, 6); task.wait(15) end
	R.ROT.tunel_recua = function() R.pos(R.tunel[1]); task.wait(3); R.andarTunel(45, 6); task.wait(5); R.andarTunel(170, 9); task.wait(12) end
	R.ROT.tunel_insiste = function() R.pos(R.tunel[1]); task.wait(3); R.andarTunel(45, 6); task.wait(5); R.andarTunel(8, 4); task.wait(10) end
	R.ROT.tunel_critica = function() R.pos(R.tunel[1]); task.wait(3); R.andarTunel(16, 6); task.wait(12) end
	R.ROT.coleta = function()
		R.pos(R.tunel[R.idxDist(60)]); task.wait(2)
		local j = jog()
		R.alc:SetAttribute("AlvoId", j.UserId); R.alc:SetAttribute("AlvoMotivo", "coleta"); R.alc:SetAttribute("AlvoAte", os.clock() + 20)
		R.alc:SetAttribute("Tensao", "Defesa"); R.alc:SetAttribute("TensaoId", j.UserId); R.alc:SetAttribute("Motivo", "coleta do ovo (simulada)")
		task.wait(10); R.andarTunel(400, 16); R.irReto(R.entrada + (plano(R.entrada - R.descanso).Unit) * 110, 16); task.wait(15)
	end
	R.ROT.dano_sem_autoria = function()
		R.pos(R.tunel[R.idxDist(60)]); task.wait(4)
		local fn = R.lobos()[1].pasta:FindFirstChild("ReceberDano"); if fn then fn:Invoke(5, "Fisico") end; task.wait(10)
	end
	R.ROT.dano_validado = function()
		R.pos(R.tunel[R.idxDist(60)]); task.wait(4)
		local fn = R.lobos()[1].pasta:FindFirstChild("ReceberDano"); if fn then fn:Invoke(5, "Fisico", (jog())) end; task.wait(10)
	end
	R.ROT.morre = function()
		R.pos(R.tunel[R.idxDist(50)]); task.wait(1)
		local j, c = jog(); R.alc:SetAttribute("AlvoId", j.UserId); R.alc:SetAttribute("AlvoMotivo", "dano"); R.alc:SetAttribute("AlvoAte", os.clock() + 20)
		R.alc:SetAttribute("Tensao", "Defesa"); task.wait(6); c:FindFirstChildOfClass("Humanoid").Health = 0; task.wait(12)
	end
	local fora = plano(R.entrada - R.descanso).Unit
	R.fora = fora
	function R.andarRetoAteAviso(destino, dVis, vel)             -- anda ate ver um lobo AMEACANDO a <= dVis do focinho e para
		local _, c = jog(); local h = c:FindFirstChildOfClass("Humanoid"); h.WalkSpeed = vel or 6
		local hrp = c.HumanoidRootPart; local t0 = os.clock()
		repeat
			h:MoveTo(destino); task.wait(0.1)
			local s = R.medir(); local df = math.huge
			for _, x in ipairs(s.lobos) do if x.est == "Ameacar" and x.dF then df = math.min(df, x.dF) end end
			if df <= dVis then h:MoveTo(hrp.Position); return df end
		until plano(hrp.Position - destino).Magnitude < 2.5 or os.clock() - t0 > 40
		return -1
	end
	function R.esperarCalmo(seg)                                  -- jogador longe; espera Calmo e os lobos voltarem
		R.pos(R.entrada + fora * 160); local t0 = os.clock()
		repeat task.wait(1) until ((R.alc:GetAttribute("Tensao") or "Calmo") == "Calmo") or os.clock() - t0 > (seg or 40)
		return os.clock() - t0
	end
	R.ROT.fora_para = function() R.pos(R.entrada + fora * 80); task.wait(3); R.parouEm = R.andarRetoAteAviso(R.entrada, 33, 6); task.wait(20) end
	R.ROT.fora_recua = function() R.pos(R.entrada + fora * 80); task.wait(3); R.parouEm = R.andarRetoAteAviso(R.entrada, 33, 6); task.wait(6); R.irReto(R.entrada + fora * 120, 8); task.wait(18) end
	R.ROT.fora_insiste = function() R.pos(R.entrada + fora * 80); task.wait(3); R.parouEm = R.andarRetoAteAviso(R.entrada, 33, 6); task.wait(4); R.irReto(R.entrada, 4); task.wait(14) end
	R.ROT.fora_recua2 = function() R.pos(R.entrada + fora * 70); task.wait(1.5); R.parouEm = R.andarRetoAteAviso(R.entrada, 30, 6); task.wait(6); R.irReto(R.entrada + fora * 110, 8); task.wait(18) end
	R.ROT.fora_insiste2 = function() R.pos(R.entrada + fora * 70); task.wait(1.5); R.parouEm = R.andarRetoAteAviso(R.entrada, 30, 6); task.wait(4); R.irReto(R.entrada + fora * 4, 4); task.wait(14) end
	function R.dump(nome)                                         -- linhas "t;nivel;motivo;Lid:estado/contato/dF;..." a cada 0,25 s
		local r = R.res[nome]; local t0 = r.amostras[1].t; local out, ultimo = {}, -1
		for _, s in ipairs(r.amostras) do
			local t = s.t - t0
			if t - ultimo >= 0.25 then
				ultimo = t; local l = {}
				for _, x in ipairs(s.lobos) do table.insert(l, string.format("%s:%s/%s/%.1f", (x.papel or "?"):sub(1, 3), tostring(x.est), tostring(x.cont or "-"), x.dF or -1)) end
				table.insert(out, string.format("%.2f;%s;%s;%s", t, tostring(s.tensao), tostring(s.motivo or ""), table.concat(l, ";")))
			end
		end
		return table.concat(out, string.char(10))
	end
	function R.rodar(nome)
		R.resetar()
		local r = {nome = nome, amostras = {}, fim = false}; R.res[nome] = r
		local vivo = true
		task.spawn(function() while vivo do table.insert(r.amostras, R.medir()); task.wait(0.1) end end)
		task.spawn(function() local ok, err = pcall(R.ROT[nome]); vivo = false; r.fim = true; r.erro = (not ok) and tostring(err) or nil end)
		return "rodando " .. nome
	end
	function R.resumo(nome)
		local r = R.res[nome]; if not r then return "sem " .. nome end
		local out, ant, t0 = {}, nil, r.amostras[1] and r.amostras[1].t or 0
		local dmin, dentro, pDef, pAm = math.huge, 0, nil, nil
		for _, s in ipairs(r.amostras) do
			local k = tostring(s.tensao) .. " | " .. tostring(s.motivo)
			if k ~= ant then
				local df = math.huge; for _, x in ipairs(s.lobos) do if x.dF then df = math.min(df, x.dF) end end
				table.insert(out, string.format("%5.1fs %s (dDescanso %.0f, focinho+perto %.1f)", s.t - t0, k, s.dD or -1, df)); ant = k
			end
			if s.tensao == "Ameaca" and not pAm then pAm = s.t end
			if s.tensao == "Defesa" and not pDef then pDef = s.t end
			for _, x in ipairs(s.lobos) do
				if x.dF and not pDef then dmin = math.min(dmin, x.dF) end
				if x.dentro then dentro += 0.1 end
			end
		end
		local ult = r.amostras[#r.amostras]
		local est = {}; if ult then for _, x in ipairs(ult.lobos) do table.insert(est, (x.papel or "?") .. "=" .. tostring(x.est) .. "/" .. tostring(x.cont)) end end
		table.insert(out, string.format("aviso antes da defesa: %s | menor focinho->jogador antes da defesa: %.1f | dentro do corpo (soma) %.1f s | fim=%s %s | final: %s",
			(pAm and pDef) and string.format("%.1f s", pDef - pAm) or "-", dmin, dentro, tostring(r.fim), r.erro or "", table.concat(est, ", ")))
		return table.concat(out, "\n")
	end
	return R
end
