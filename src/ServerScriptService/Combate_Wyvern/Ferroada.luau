-- Ferroada (ModuleScript, ServerScriptService.Combate_Wyvern) — ataque BASICO FERROADA da Wyvern (fora das vagas de ativas;
-- kit aprovado pelo usuario 13/11/2026). Ferroada FISICA de curto alcance com a cauda; a toxina e aplicada pela passiva
-- ToxinaFerrao (N.ferir -> T.aoAcertar com tipo "Ferroada"). AUTORIDADE DO SERVIDOR: o cliente so pede (tecla da Garra);
-- o Nucleo valida recarga/ocupado/transicao/incapacitado antes de chamar F.executar.
-- Clipe: FerraoAtaque aprovado (1,5 s). Medido no Blender (Wyvern_E7_clipes_L7): a ponta do ferrao passa por cima da
-- cabeca e fica ~15,7 studs a frente, na altura da cabeca (~12), de 0,58 a 0,75 s.
-- ADAPTACAO (rig x jogo): o ferrao golpeia na altura da cabeca; um alvo do porte de um jogador fica ~9 studs abaixo da
-- ponta. A area de acerto e uma capsula vertical da ponta do ferrao (osso tail_tip, posicao ANIMADA no servidor no instante
-- do impacto) ate 10 studs abaixo, com raio def.raio (+ corpo do alvo se for guardiao). Um acerto por alvo.
-- So no chao por enquanto (no ar fica para depois). Numeros em ConfigCombate.habilidades.Ferroada (PROVISORIOS).
-- r2 (usuario 13/11): "se o alvo estiver de lado ou atras, a cauda deve seguir o alvo que esta na mira". O giro (yaw, ate
-- +-180 graus) vai da frente do corpo ate a mira: alvo travado (op.alvo, ja validado pelo servidor) ou a direcao pedida
-- (op.direcao = camera/mira). A cauda gira em torno da BASE (osso tail_01) no plano horizontal: no cliente
-- (Ferroada_Cliente, pelos atributos FerroadaYaw/FerroadaT0, todos veem) e aqui no acerto (o ponto da ponta e girado
-- pelo mesmo yaw em torno da base). O corpo e a cabeca nao giram.
local F = {}
F.IMPACTO = 0.66                 -- s do clipe em que o ferrao esta a frente (meio da janela 0,58-0,75)
F.DESCE = 10                     -- studs: a capsula vai da ponta ate aqui abaixo

local function distSeg(p, a, b)
	local ab = b - a; local t = math.clamp((p - a):Dot(ab) / ab:Dot(ab), 0, 1)
	return (p - (a + ab * t)).Magnitude
end
local function yawDe(a, b)                                       -- angulo assinado em torno de +Y (anti-horario visto de cima)
	local a2, b2 = Vector3.new(a.X, 0, a.Z), Vector3.new(b.X, 0, b.Z)
	if a2.Magnitude < 1e-3 or b2.Magnitude < 1e-3 then return 0 end
	a2, b2 = a2.Unit, b2.Unit
	return math.atan2(a2:Cross(b2).Y, a2:Dot(b2))
end
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end

-- self = registro do Nucleo (metatabela N): self.m, self:tocar, self:alvosValidos, self:aplicar, self.FX, N.pontoAlvo
function F.executar(self, def, el, noAr, op)
	local N = getmetatable(self)
	local m = self.m
	if noAr then return end                                          -- so no chao nesta etapa
	self.ferrao = self.ferrao or osso(m, "tail_tip")
	self.baseCauda = self.baseCauda or osso(m, "tail_01")
	-- mira: alvo travado > direcao pedida > frente
	local frente = self:frente()
	local base0 = self.baseCauda and self.baseCauda.TransformedWorldCFrame.Position or m:GetPivot().Position
	local dirMira = (op and op.alvo and op.alvo.Parent and (N.pontoAlvo(op.alvo) - base0)) or (op and typeof(op.direcao) == "Vector3" and op.direcao) or frente
	local yaw = yawDe(frente, dirMira)
	m:SetAttribute("FerroadaYaw", math.deg(yaw)); m:SetAttribute("FerroadaT0", workspace:GetServerTimeNow())
	N.FX:FireAllClients({d = m, hab = "Ferroada", fase = "preparo"})
	local t = self:tocar("Ferroada", false, {Impacto = F.IMPACTO}, function(n)
		if n ~= "Impacto" or not self.ferrao then return end
		local ponta = self.ferrao.TransformedWorldCFrame.Position
		if self.baseCauda and math.abs(yaw) > 1e-3 then                -- cauda girada para a mira em torno da base
			local b = self.baseCauda.TransformedWorldCFrame.Position
			ponta = b + CFrame.fromAxisAngle(Vector3.yAxis, yaw):VectorToWorldSpace(ponta - b)
		end
		local base = ponta - Vector3.new(0, F.DESCE, 0)
		local alvos = {}
		for _, a in ipairs(self:alvosValidos()) do
			local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) or 0
			if distSeg(N.pontoAlvo(a), ponta, base) <= def.raio + extra then table.insert(alvos, a) end
		end
		local n2 = self:aplicar(alvos, def.dano, "Ferroada", def.intensidade, nil)   -- fisico: sem elemento
		m:SetAttribute("FerroadaUltima", workspace:GetServerTimeNow())
		m:SetAttribute("FerroadaAcertos", n2)
		N.FX:FireAllClients({d = m, hab = "Ferroada", fase = "impacto", pos = ponta, acertou = n2 > 0})
	end)
	task.wait(math.max(t and t.Length or 0, 1.5) - 0.1)
	m:SetAttribute("FerroadaYaw", nil); m:SetAttribute("FerroadaT0", nil)
end
return F
