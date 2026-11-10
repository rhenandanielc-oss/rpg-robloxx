-- InerciaCavaleiro (ModuleScript, CLIENTE, so visual) - montaria do urso, TESTE (09/11/2026).
-- Pedido do usuario: "Quero que o jogador tambem se mova junto aos movimentos, como as leis da fisica."
-- Modelo: pendulo amortecido. O quadril do cavaleiro e carregado pela sela (ponto do assento preso ao osso Coluna2 do
-- urso). O tronco e uma massa a H studs acima do quadril, puxada por uma mola angular para a posicao "em pe na sela" e
-- amortecida em relacao ao quadril; por isso, quando a sela acelera (arranca, freia, galopa, sobe, desce, vira ou inclina),
-- o tronco fica para tras, balanca e volta. A cabeca e uma 2a massa em cima do tronco (mola propria, mais rapida).
-- O resultado vira uma rotacao EXTRA somada as juntas Waist e Neck (Motor6D ou AnimationConstraint) depois do Animator.
-- Nada disto e regra de jogo nem passa pelo servidor. Peso: atributo "InerciaPeso" (0..1) no modelo do cavaleiro.
local M = {}
M.P = {
	-- r2 (09/11): tronco mais firme e amortecido (no galope chegava a 24 graus e batia no limite de 20)
	tronco = {h = 1.6, freq = 2.2, amort = 0.55, max = 14},   -- freq em Hz; amort = razao de amortecimento; max em graus
	cabeca = {h = 0.9, freq = 3.0, amort = 0.40, max = 12},
	vert = {freq = 3.0, amort = 0.5, dobra = 40, max = 9, aceno = 0.5},   -- dobra: graus por stud de compressao
}

local function massa(p) return {q = nil, v = Vector3.zero, P = p} end

-- um passo do pendulo: base (ponto de apoio) e alvo (direcao "em pe"); devolve a direcao atual da massa
local function passo(m, base, vbase, dirAlvo, dt)
	local P = m.P; local w = 2 * math.pi * P.freq
	local alvo = base + dirAlvo * P.h
	if not m.q then m.q = alvo; m.v = vbase end
	local a = (alvo - m.q) * (w * w) - (m.v - vbase) * (2 * P.amort * w)
	m.v += a * dt; m.q += m.v * dt
	local r = m.q - base; local d = r.Magnitude > 1e-6 and r.Unit or dirAlvo
	m.q = base + d * P.h                                       -- haste rigida: so gira em volta da base
	local vr = m.v - vbase; m.v = vbase + (vr - d * vr:Dot(d))   -- tira a componente radial
	return d
end

-- rotacao (no espaco da junta) que leva dirAlvo para d, limitada e pesada
local function extra(junta, parte0, dirAlvo, d, maxGraus, peso)
	local eixo = dirAlvo:Cross(d); local s = eixo.Magnitude
	if s < 1e-6 or peso <= 0 then return CFrame.identity end
	local mx = math.rad(maxGraus)                                  -- r3: limite suave (tanh), sem "travar" no maximo
	local ang = mx * math.tanh(math.atan2(s, dirAlvo:Dot(d)) / mx) * peso
	local eixoL = parte0.CFrame:VectorToObjectSpace(eixo / s)
	local f0 = junta:IsA("Motor6D") and junta.C0 or junta.Attachment0.CFrame
	return CFrame.fromAxisAngle(f0.Rotation:VectorToObjectSpace(eixoL), ang), math.deg(ang)
end

-- cria o controlador: rig = R15 do cavaleiro; assento() devolve o CFrame do assento no mundo (quadril, eixo Y = "em pe")
function M.novo(rig, assento)
	local J = {}
	for _, d in rig:GetDescendants() do
		if (d:IsA("Motor6D") or d.ClassName == "AnimationConstraint") and (d.Name == "Waist" or d.Name == "Neck") then J[d.Name] = d end
	end
	local self = {tronco = massa(M.P.tronco), cabeca = massa(M.P.cabeca), pAnt = nil, peso = 0, log = {maxT = 0, maxC = 0, maxV = 0}}
	function self.atualizar(dt)
		dt = math.clamp(dt, 1 / 240, 1 / 20)
		local alvoPeso = rig:GetAttribute("InerciaPeso") or 0
		self.peso += (alvoPeso - self.peso) * math.min(1, dt * 6)
		local cf = assento(); local p = cf.Position; local up = cf.UpVector
		local salto = self.pAnt and (p - self.pAnt) or Vector3.zero
		if salto.Magnitude > 3 then                              -- teleporte (PivotTo): leva as massas junto, sem "sentir" o pulo
			for _, m in {self.tronco, self.cabeca} do if m.q then m.q += salto end end
			salto = Vector3.zero; self.vAnt = nil
		end
		local vb = salto / dt; self.pAnt = p
		-- mola vertical: o corpo absorve a subida/descida da sela (o pendulo nao sente aceleracao ao longo do tronco)
		local acc = self.vAnt and (vb - self.vAnt) / dt or Vector3.zero; self.vAnt = vb
		self.aF = (self.aF or Vector3.zero):Lerp(acc, math.min(1, dt * 20))
		local V = M.P.vert; local wv = 2 * math.pi * V.freq
		self.y = self.y or 0; self.vy = self.vy or 0
		self.vy += (-wv * wv * self.y - 2 * V.amort * wv * self.vy - self.aF:Dot(up)) * dt
		self.y = math.clamp(self.y + self.vy * dt, -0.4, 0.4)
		local dobra = math.rad(math.clamp(-self.y * V.dobra, -V.max, V.max))    -- y < 0 (comprime) -> tronco dobra para a frente
		local dT = passo(self.tronco, p, vb, up, dt)
		dT = CFrame.fromAxisAngle(cf.RightVector, -dobra):VectorToWorldSpace(dT)
		local topo = p + dT * M.P.tronco.h; local vTopo = self.tronco.v
		local dC = passo(self.cabeca, topo, vTopo, dT, dt)
		dC = CFrame.fromAxisAngle(cf.RightVector, -dobra * V.aceno):VectorToWorldSpace(dC)   -- a cabeca acena junto
		if math.abs(math.deg(dobra)) > self.log.maxV then self.log.maxV = math.abs(math.deg(dobra)) end
		local w, n = J.Waist, J.Neck
		if w then
			local e, g = extra(w, rig.LowerTorso, up, dT, M.P.tronco.max, self.peso); w.Transform = e * w.Transform
			if g and g > self.log.maxT then self.log.maxT = g end
		end
		if n then
			local e, g = extra(n, rig.UpperTorso, dT, dC, M.P.cabeca.max, self.peso); n.Transform = e * n.Transform
			if g and g > self.log.maxC then self.log.maxC = g end
		end
	end
	return self
end
return M
