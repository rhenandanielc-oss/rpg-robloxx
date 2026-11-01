-- patch_animacao_universal.luau (Studio, modo Edit) — sistema universal de animacoes dos dragoes (01/11), parte IA.
-- Liga os comportamentos novos (EstadosDragao: Intimidacao, RugidoTerritorial, Curiosidade, M:Pontual) ao guardiao
-- selvagem, sempre com motivo (nada aleatorio sem contexto):
--  1) foco: o servidor grava o atributo AlvoOlhar (Vector3) no modelo enquanto encara alguem; o MovimentoVivo_Cliente
--     vira pescoco/cabeca para ele (tambem andando) = rugido DIRECIONADO, intimidacao e curiosidade olhando o alvo;
--  2) alerta PESSOAL (alguem perto do dragao) -> Intimidacao (cabeca baixa, dentes, grunhidos); alerta do ninho segue
--     o Alerta antigo;
--  3) jogador distante observado -> Curiosidade (1 a cada 2 observacoes) ou Observacao; investigar -> Curiosidade;
--  4) depois de um confronto (Recover) -> Rugido territorial (dominio); parado no territorio sem ameaca -> rugido
--     territorial no maximo 1 a cada 4 min e so com jogador perto para ver (nunca em sequencia);
--  5) dano: a Vida caindo toca Dano_Leve/Dano_Forte (versao _Ar no ar) por cima do estado, com peso proporcional ao
--     golpe; nunca durante um ataque do proprio dragao (EmAtaque).
-- Tudo-ou-nada: confere cada trecho, compila, guarda copia em ServerStorage.Backup_Animacao_Universal_2026-11-01.
local SSS, SS, SP = game:GetService("ServerScriptService"), game:GetService("ServerStorage"), game:GetService("StarterPlayer")
local alvos = {Cerebro = SSS.IA_Dragao.Cerebro, MV = SP.StarterPlayerScripts.MovimentoVivo_Cliente}
if alvos.Cerebro.Source:find("PATCH_ANIM_UNIVERSAL", 1, true) then return "ja aplicado" end
local novo = {}; for k, s in pairs(alvos) do novo[k] = s.Source:gsub("\r\n", "\n") end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true); assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end

-- MovimentoVivo_Cliente: foco vindo da IA
troca("MV", [=[	elseif not cav and horiz < 2 then]=], [=[	elseif not cav and m:GetAttribute("AlvoOlhar") and e.cabeca then
		-- IA (sistema universal 01/11): rugido direcionado, intimidacao e curiosidade encaram o alvo (tambem andando)
		alvoDir = (m:GetAttribute("AlvoOlhar") - e.cabeca.TransformedWorldCFrame.Position).Unit
	elseif not cav and horiz < 2 then]=])

-- Cerebro
troca("Cerebro", [=[local C = {}
C.__index = C]=], [=[-- PATCH_ANIM_UNIVERSAL (01/11): foco do olhar, intimidacao, curiosidade, rugido territorial e reacao a dano
local C = {}
C.__index = C
local INTERVALO_RUGIDO_TERRITORIAL = 240]=])
troca("Cerebro", [=[	self:registrar("criado; ninho=" .. self.T.id)]=], [=[	-- reacao a dano por cima do estado (peso proporcional ao golpe), nunca no meio de um ataque proprio
	self.vidaAnt = modelo:GetAttribute("Vida")
	self.cxVida = modelo:GetAttributeChangedSignal("Vida"):Connect(function()
		local v, vmax = modelo:GetAttribute("Vida"), modelo:GetAttribute("VidaMax") or 1
		local antes = self.vidaAnt; self.vidaAnt = v
		if not (v and antes) or v >= antes or modelo:GetAttribute("EmAtaque") or modelo:GetAttribute("Incapacitado") then return end
		if os.clock() - (self.ultDano or 0) < 0.7 then return end
		self.ultDano = os.clock()
		local frac = (antes - v) / vmax; local forte = frac >= 0.06
		local nome = (forte and "Dano_Forte" or "Dano_Leve") .. (self.L.noAr and "_Ar" or "")
		self.E:Pontual(nome, math.clamp(0.45 + frac * 6, 0.45, 1))
	end)
	self:registrar("criado; ninho=" .. self.T.id)]=])
troca("Cerebro", [=[function C:registrar(msg)]=], [=[-- foco do olhar (MovimentoVivo_Cliente): posicao da cabeca do alvo, ou nil para soltar
function C:focar(alvo)
	local r = alvo and raizDe and raizDe(alvo)
	self.m:SetAttribute("AlvoOlhar", r and (r.Position + Vector3.new(0, 2, 0)) or nil)
end
function C:registrar(msg)]=])
-- raizDe e local definida depois de registrar: a funcao focar a usa so em tempo de execucao (upvalue resolvido abaixo)
troca("Cerebro", [=[local function raizDe(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end]=],
	[=[function raizDe(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end]=])
troca("Cerebro", [=[local C = {}
C.__index = C
local INTERVALO]=], [=[local raizDe
local C = {}
C.__index = C
local INTERVALO]=])
-- 2) alerta pessoal -> intimidacao (encara o alvo)
troca("Cerebro", [=[	self.L:virarPara(a.ultimaPos, vivo)
	self:comportamento("Alerta", 3, vivo)]=], [=[	self.L:virarPara(a.ultimaPos, vivo)
	self:focar(alvo)
	local estadoAlerta = a.pessoal and "Intimidacao" or "Alerta"
	self:comportamento(estadoAlerta, a.pessoal and 3.6 or 3, vivo)]=])
troca("Cerebro", [=[		local _, a2 = self:maiorAmeaca(); if a2 and a2.ultimaPos then self:encarar(a2.ultimaPos, vivo) end
		self:comportamento("Alerta", 2, vivo)
	end
end]=], [=[		local alvo2, a2 = self:maiorAmeaca(); if a2 and a2.ultimaPos then self:encarar(a2.ultimaPos, vivo); self:focar(alvo2) end
		self:comportamento((a2 and a2.pessoal) and "Intimidacao" or "Alerta", 2, vivo)
	end
	self:focar(nil)
end]=])
-- 3) observacao / investigacao -> curiosidade
troca("Cerebro", [=[	if not self.L.noAr then self.L:virarPara(r.Position, vivo) end
	self:comportamento("Observacao", 6, vivo)
end]=], [=[	if not self.L.noAr then self.L:virarPara(r.Position, vivo) end
	self:focar(alvo)
	self.nObs = (self.nObs or 0) + 1
	self:comportamento(self.nObs % 2 == 0 and "Curiosidade" or "Observacao", 6, vivo)
	self:focar(nil)
end]=])
troca("Cerebro", [=[	self:definir("Investigate"); self:comportamento("Observacao", self.cfg.investigarTempo, vivo)   -- fareja e olha em volta]=],
	[=[	self:definir("Investigate"); self:comportamento("Curiosidade", self.cfg.investigarTempo, vivo)   -- fareja, inclina a cabeca]=])
-- 4) rugido territorial: depois do confronto e, raramente, parado no territorio com jogador perto
troca("Cerebro", [=[	self:comportamento("Alerta", 4, vivo)
	self:comportamento("Espreguicar", 5, vivo)]=], [=[	self:comportamento("Alerta", 4, vivo)
	self:comportamento("RugidoTerritorial", 4.6, vivo); self.ultRugidoT = os.clock()      -- reafirma o territorio
	self:comportamento("Espreguicar", 5, vivo)]=])
troca("Cerebro", [=[function C:_Idle(vivo) self:emPe(vivo); self:comportamento("Idle", 6 + math.random() * 6, vivo) end]=],
	[=[function C:_Idle(vivo)
	self:emPe(vivo)
	local semAmeaca = not self:maiorAmeaca()
	if semAmeaca and not self.dormente and self.observado and os.clock() - (self.ultRugidoT or -1e9) > INTERVALO_RUGIDO_TERRITORIAL
		and plano(self.L:pos() - self.casa).Magnitude < self.cfg.territorio * 0.6 then
		self.ultRugidoT = os.clock(); self:comportamento("RugidoTerritorial", 4.6, vivo); return     -- alguem observa de longe
	end
	self:comportamento("Idle", 6 + math.random() * 6, vivo)
end]=])
-- foco no combate em terra (rugido/ameaca de ninho direcionados) e limpeza ao sair
troca("Cerebro", [=[			self.L:virarPara(pI, function() return vivo() end)
			if not ameacou then]=], [=[			self.L:virarPara(pI, function() return vivo() end)
			self:focar(alvo)
			if not ameacou then]=])
troca("Cerebro", [=[	self.aposConfronto = os.clock(); self.recuperado = false
end
return C]=], [=[	self.aposConfronto = os.clock(); self.recuperado = false
	self:focar(nil)
end
return C]=])
troca("Cerebro", [=[	if self.cxAlerta then self.cxAlerta:Disconnect() end; if self.cxAtacado then self.cxAtacado:Disconnect() end]=],
	[=[	if self.cxAlerta then self.cxAlerta:Disconnect() end; if self.cxAtacado then self.cxAtacado:Disconnect() end
	if self.cxVida then self.cxVida:Disconnect() end]=])

for k in pairs(alvos) do local f, e = loadstring(novo[k]); assert(f, k .. " nao compila: " .. tostring(e)) end
local bk = SS:FindFirstChild("Backup_Animacao_Universal_2026-11-01")
for k, s in pairs(alvos) do
	if not bk:FindFirstChild(k .. "__" .. s.Name) then
		local c = s:Clone(); c.Name = k .. "__" .. s.Name; if c:IsA("BaseScript") then c.Enabled = false end; c.Parent = bk
	end
end
for k, s in pairs(alvos) do s.Source = novo[k] end
return "aplicado"
