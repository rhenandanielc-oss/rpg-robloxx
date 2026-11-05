-- PATCH_PASSO_SOMBRIO (04/11, escolha do usuario: 4a ativa do Sombrio, slot Tempestade/tecla 3): o dragao se desfaz em
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
end
