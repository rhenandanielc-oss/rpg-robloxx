-- Nucleo (ModuleScript, ServerScriptService.Combate_Dragao) — combate do Dragao das Montanhas, AUTORIDADE DO SERVIDOR.
-- PATCH_KIT_GELO (02/11): kit oficial do Dragao Glacial (Sopro Glacial, Rajadas, Zero Absoluto, Nevasca; Frostbite).
-- Validacao (elemento unico da forma, energia, recarga por habilidade, ocupado, vivo/incapacitado), deteccao de
-- acerto (geometria + linha de visao, no instante dos marcadores da animacao no servidor, com tempo de reserva),
-- aplicacao de dano (Humanoid:TakeDamage) e eventos cosmeticos para os clientes (RemoteEvent FX, so servidor->cliente).
-- O cliente nunca informa dano, alvo ou acerto.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local RS = game:GetService("ReplicatedStorage")
local Cfg = require(script.Parent.ConfigCombate)
local Passivas = require(script.Parent.Passivas)

local pastaRede = RS:FindFirstChild("Combate_Dragoes") or Instance.new("Folder"); pastaRede.Name = "Combate_Dragoes"; pastaRede.Parent = RS
local FX = pastaRede:FindFirstChild("FX") or Instance.new("RemoteEvent"); FX.Name = "FX"; FX.Parent = pastaRede

local N = {}
N.__index = N
N.registro = {}
N.FX = FX
N.Passivas = Passivas

local function raiz(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end
local function plano(v) return Vector3.new(v.X, 0, v.Z) end

function N.registrar(modelo)
	if N.registro[modelo] then return N.registro[modelo] end
	local self = setmetatable({}, N)
	self.m = modelo
	self.forma = modelo:GetAttribute("FormaRegional") or "Montanhas"
	self.energia = Cfg.energiaMax
	self.recargas = {}                                          -- habilidade -> os.clock() liberado
	self.ocupado = false
	local ac = modelo:FindFirstChildOfClass("AnimationController")
	self.animator = ac:FindFirstChildOfClass("Animator") or Instance.new("Animator", ac)
	self.trilhas = {}
	self.cabeca = osso(modelo, "Cabeca"); self.mand = osso(modelo, "Mandibula"); self.quadril = osso(modelo, "Quadril")
	self.peE = osso(modelo, "PernaDE_3") or osso(modelo, "front_foot_l"); self.peD = osso(modelo, "PernaDD_3") or osso(modelo, "front_foot_r")
	self.focinho = osso(modelo, "mouth_upper_tip")              -- rig Mesh2Motion (Silverwing): boca real
	local pa = RS:FindFirstChild("Animacoes_" .. modelo.Name) or RS:FindFirstChild("Animacoes_" .. (modelo:GetAttribute("PastaAnimacoes") or ""))
	local ap = pa and pa:FindFirstChild("Apelidos")
	self.apelidos = ap and require(ap) or nil; self.pastaAnim = pa
	-- elementos: atributos ElementoNato e ElementosDesbloqueados ("Terra,Ar"); equipado = ElementoAtivo
	local nato = modelo:GetAttribute("ElementoNato") or "Fogo"
	modelo:SetAttribute("ElementoNato", nato)
	if not modelo:GetAttribute("ElementoAtivo") then modelo:SetAttribute("ElementoAtivo", nato) end
	modelo:SetAttribute("Energia", self.energia)
	modelo:SetAttribute("Passivas", table.concat(Cfg.passivasForma[self.forma] or {}, ","))   -- exibicao (HUD); efeito so no servidor
	N.registro[modelo] = self
	self:auditarDados()
	modelo.AncestryChanged:Connect(function(_, p) if not p then N.registro[modelo] = nil end end)
	return self
end

-- ===== elementos ===============================================================================================
function N:elementos()
	-- filtra pela forma ANTES de aplicar o limite (dado antigo "Raio,Terra,Ar" nao pode esconder o Ar)
	local permitidos = {}
	for _, e in ipairs(Cfg.elementosForma[self.forma] or {}) do permitidos[e] = true end
	local daForma = Cfg.elementosForma[self.forma] or {}
	if #daForma == 1 then return {daForma[1]} end                -- forma de elemento unico (Montanhas = Fogo): e o proprio
	local validos = {}
	local function add(e) if permitidos[e] and not table.find(validos, e) and #validos < Cfg.maxElementos then table.insert(validos, e) end end
	add(self.m:GetAttribute("ElementoNato"))
	for e in string.gmatch(self.m:GetAttribute("ElementosDesbloqueados") or "", "[^,%s]+") do add(e) end
	return validos
end
-- migracao NAO destrutiva (atualizacao oficial): dados antigos com Raio/Dominio nao sao apagados nem convertidos;
-- ficam inativos e marcados em "MigracaoPendente" ate haver decisao aprovada (nenhum elemento e concedido automaticamente)
function N:auditarDados()
	local permitidos = {}; for _, e in ipairs(Cfg.elementosForma[self.forma] or {}) do permitidos[e] = true end
	local notas = {}
	local nato = self.m:GetAttribute("ElementoNato")
	if not permitidos[nato] then table.insert(notas, "ElementoNato " .. tostring(nato) .. " fora da forma") end
	for e in string.gmatch(self.m:GetAttribute("ElementosDesbloqueados") or "", "[^,%s]+") do
		if not permitidos[e] then table.insert(notas, "Desbloqueado " .. e .. " ignorado") end
	end
	if self.m:GetAttribute("DominioAtivo") then self.m:SetAttribute("DominioAtivo", nil); table.insert(notas, "Dominio ativo encerrado") end
	local ativo = self.m:GetAttribute("ElementoAtivo")
	local validos = self:elementos()
	if not permitidos[ativo] then
		self.m:SetAttribute("ElementoAtivo", validos[1])            -- nil se nenhum valido: habilidades elementais ficam bloqueadas
		table.insert(notas, "ElementoAtivo " .. tostring(ativo) .. " -> " .. tostring(validos[1]))
	end
	self.m:SetAttribute("MigracaoPendente", #notas > 0 and table.concat(notas, "; ") or nil)
	self.m:SetAttribute("ElementosValidos", table.concat(validos, ","))                     -- exibicao/selecao no cliente
	return notas
end
-- PATCH_KIT_GELO: slot (tecla/HUD/IA) -> habilidade real da forma (Glacial: Sopro Glacial, Rajadas, Zero Absoluto, Nevasca)
function N:real(hab) local k = Cfg.kitForma and Cfg.kitForma[self.forma]; return (k and k[hab]) or hab end
function N:temHabilidade(hab)
	if Cfg.basicos[hab] then return true end
	for _, h in ipairs(Cfg.habilidadesForma[self.forma] or {}) do if h == hab then return true end end
	return false
end
function N:trocarElemento(e)
	if #(Cfg.elementosForma[self.forma] or {}) <= 1 then return false, "forma de elemento unico (sem troca)" end   -- oficial 30/10
	for _, x in ipairs(self:elementos()) do
		if x == e then self.m:SetAttribute("ElementoAtivo", e); FX:FireAllClients({d = self.m, fase = "elemento", el = e}); return true end
	end
	return false, "elemento nao equipado/permitido"
end

-- ===== animacao ===============================================================================================
function N:clipe(nome, camada)
	local chave = camada and (nome .. "_Camada") or nome
	local t = self.trilhas[chave]; if t then return t end
	local pasta = self.pastaAnim or RS:FindFirstChild("Animacoes_Dragao_V14")
	local kfs = pasta and (pasta:FindFirstChild("Dragao_V14_" .. chave) or pasta:FindFirstChild("Dragao_V14_" .. nome))
	if not kfs and self.apelidos and pasta then                  -- outro rig: prefixo proprio ou apelido (sem cair no "*")
		-- ordem: clipe proprio da camada (no ar) -> apelido da camada -> clipe proprio -> apelido
		local px = self.apelidos.prefixo or ""
		local ac, a = self.apelidos[chave], self.apelidos[nome]
		kfs = (chave ~= nome and (pasta:FindFirstChild(px .. chave) or (ac and pasta:FindFirstChild(ac))))
			or pasta:FindFirstChild(px .. nome) or (a and pasta:FindFirstChild(a))
	end
	if not kfs then return nil end
	local a = Instance.new("Animation"); a.Name = chave
	a.AnimationId = kfs:GetAttribute("AnimationId") or game:GetService("AnimationClipProvider"):RegisterAnimationClip(kfs)
	t = self.animator:LoadAnimation(a); t.Priority = Enum.AnimationPriority.Action
	self.trilhas[chave] = t
	return t
end
-- toca o clipe e chama cb(marcador, valor) nos marcadores; se o clipe/marcador nao vier, usa os tempos de reserva
function N:tocar(nome, camada, reserva, cb, loop)
	local t = self:clipe(nome, camada)
	local feitos = {}
	local cons = {}
	local function marca(n, v) if feitos[n .. tostring(v)] then return end; feitos[n .. tostring(v)] = true; cb(n, v) end
	if t then
		for n in pairs(reserva or {}) do table.insert(cons, t:GetMarkerReachedSignal(n):Connect(function(v) marca(n, v) end)) end
		t.Looped = loop == true; t:Play(0.15)
	end
	-- reserva: dispara o que nao chegou ate (tempo + 0,15 s)
	for n, tempo in pairs(reserva or {}) do
		task.delay(tempo + 0.15, function()
			local chegou = false; for k in pairs(feitos) do if k:sub(1, #n) == n then chegou = true end end
			if not chegou then marca(n, nil) end
		end)
	end
	return t, function() for _, c in ipairs(cons) do c:Disconnect() end end
end

-- ===== geometria e alvos =======================================================================================
function N:boca()
	local fwd = self:frente()
	if self.focinho then return self.focinho.TransformedWorldCFrame.Position + fwd * 1.5, fwd end
	local c = self.cabeca and self.cabeca.TransformedWorldCFrame or self.m:GetPivot()
	return c.Position + c.UpVector * 10 + Vector3.new(0, -1.5, 0), fwd
end
function N:frente()
	local cab = self.cabeca.TransformedWorldCFrame.Position; local q = self.quadril.TransformedWorldCFrame.Position
	local f = plano(cab - q); return f.Magnitude > 0.1 and f.Unit or Vector3.zAxis
end
local CS = game:GetService("CollectionService")
local function emZonaSegura(pos)
	for _, z in ipairs(CS:GetTagged(Cfg.zonaSeguraTag)) do
		if z:IsA("BasePart") then
			local p = z.CFrame:PointToObjectSpace(pos); local s = z.Size / 2
			if math.abs(p.X) <= s.X and math.abs(p.Y) <= s.Y and math.abs(p.Z) <= s.Z then return true end
		end
	end
	return false
end
N.emZonaSegura = emZonaSegura
-- PATCH_IA_DERROTA_AR: guardiao selvagem DERROTAVEL (decisao do usuario 30/10). Vida em atributos; so dragao de JOGADOR
-- fere; em 0 -> Incapacitado (o Cerebro pousa/deita e recupera). Valores experimentais (Config da IA).
function N.danoGuardiao(g, dano, atacante, el)
	if not (g and g.Parent and g:GetAttribute("GuardiaoNinho")) or g:GetAttribute("Incapacitado") or not dano or dano <= 0 then return false end
	if not (atacante and atacante:GetAttribute("DonoUserId")) then return false end
	if g.PrimaryPart and emZonaSegura(g.PrimaryPart.Position) then return false end
	-- resistencia a Fogo (Sangue de Magma ou atributo ResistenciaFogo) e ativacao do reforco (passiva do proprio guardiao)
	if Passivas.tem(g, "SangueDeMagma") then dano = Passivas.danoRecebido(g, dano, el)
	elseif el == "Fogo" then dano *= (1 - Passivas.resistenciaFogo(g)) end
	if el == "Gelo" then dano *= (1 - Passivas.resistenciaGelo(g)) end
	dano *= Passivas.vulnerabilidade(g)
	if dano <= 0 then return false end
	local max = g:GetAttribute("VidaMax") or 600
	local v = math.max(0, (g:GetAttribute("Vida") or max) - dano)
	g:SetAttribute("Vida", v); g:SetAttribute("UltimoDano", workspace:GetServerTimeNow())
	local plr = Players:GetPlayerByUserId(atacante:GetAttribute("DonoUserId"))
	local ev = game:GetService("ServerStorage"):FindFirstChild("IA_Eventos")
	if ev and ev:FindFirstChild("GuardiaoAtacado") then ev.GuardiaoAtacado:Fire(g, (plr and plr.Character) or atacante) end
	if v <= 0 then g:SetAttribute("Incapacitado", true); g:SetAttribute("Derrotado", workspace:GetServerTimeNow()) end
	return true
end
function N:alvosValidos()
	local l = {}
	local pvp = workspace:GetAttribute(Cfg.pvpAtivoAtributo) == true
	local dono = self.m:GetAttribute("DonoUserId")
	-- dragao de JOGADOR tambem mira guardioes selvagens (derrotaveis; zona segura vale; derrotado nao e alvo)
	if dono then
		for _, g in ipairs(workspace:GetChildren()) do
			if g ~= self.m and g:IsA("Model") and g:GetAttribute("GuardiaoNinho") and not g:GetAttribute("Incapacitado") and g.PrimaryPart
				and not emZonaSegura(g.PrimaryPart.Position) then table.insert(l, g) end
		end
	end
	for _, h in ipairs(workspace:GetDescendants()) do
		if h:IsA("Humanoid") and h.Health > 0 then
			local mod = h.Parent
			if mod ~= self.m and raiz(mod) then
				local plr = Players:GetPlayerFromCharacter(mod)
				local ok = true
				if plr then
					if dono and plr.UserId == dono then ok = false              -- nunca o proprio dono
					elseif dono and not pvp then ok = false end                -- dragao de jogador so fere jogadores com PvP ativo
				end
				if mod:GetAttribute("AliadoDe") == dono and dono then ok = false end
				if ok and emZonaSegura(raiz(mod).Position) then ok = false end      -- zonas seguras: ninguem e atingido dentro
				if ok then table.insert(l, mod) end
			end
		end
	end
	return l
end
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include
function N:visivel(de, alvoMod)
	rp.FilterDescendantsInstances = {workspace.Terrain}
	local p = raiz(alvoMod).Position
	return workspace:Raycast(de, p - de, rp) == nil
end
-- dano UNICO do combate (habilidades, basicos, mordida aerea da montaria e ticks de Burning): resistencia a Fogo do alvo,
-- vida do guardiao ou Humanoid. Acerto que causou dano (e nao e tick) aplica Burning se a fonte tem a passiva.
function N.ferir(fonte, a, dano, el, tipo, intensidade, ehTick, frost)
	if not (a and a.Parent) or not dano or dano <= 0 then return false end
	local h = a:FindFirstChildOfClass("Humanoid")
	local ok = false
	if not h and a:GetAttribute("GuardiaoNinho") then
		ok = N.danoGuardiao(a, dano, fonte, el)
	elseif h and h.Health > 0 then
		if el == "Fogo" then dano *= (1 - Passivas.resistenciaFogo(a)) end
		if el == "Gelo" then dano *= (1 - Passivas.resistenciaGelo(a)) end
		dano *= Passivas.vulnerabilidade(a)                             -- Frostbite: alvo muito congelado sofre mais
		if Passivas.tem(fonte, "MarcaSombria") then el = el or "Sombra"; if el == "Sombra" then dano *= Passivas.multiplicadorMarca(fonte, a) end end   -- PATCH_MARCA_SOMBRIA
		if dano > 0 then h:TakeDamage(dano); ok = true end
	end
	if ok and not ehTick then
		FX:FireAllClients({d = fonte, fase = "reacao", alvo = a, intensidade = intensidade, el = el, tipo = tipo})
		Passivas.aplicarBurning(fonte, a)
		Passivas.aplicarFrostbite(fonte, a, frost or Cfg.passivas.Frostbite.basico)   -- Glacial: todo acerto acumula
		Passivas.marcarCombate(fonte)
		if el == "Sombra" then Passivas.aplicarMarca(fonte, a) end      -- PATCH_MARCA_SOMBRIA: acerto (nao tick) marca
	end
	if ok then local t = workspace:GetServerTimeNow(); if fonte then fonte:SetAttribute("UltimoCombate", t) end; a:SetAttribute("UltimoCombate", t) end   -- PATCH_MARCA_SOMBRIA: Rastro do Breu
	return ok
end
function N:aplicar(alvos, dano, tipo, intensidade, el, frost)
	local mult = ((self.m:GetAttribute("DominioAtivo") and Cfg.habilidades.Dominio.multiplicadorDano) or 1) * Passivas.multiplicadorOfensivo(self.m)
	local n = 0
	for _, a in ipairs(alvos) do
		if N.ferir(self.m, a, dano * mult, el, tipo, intensidade, nil, frost) then n += 1 end
	end
	return n
end
local function noCone(o, f, alvo, alc, ang)
	local v = raiz(alvo).Position - o; local d = v.Magnitude
	if d > alc or d < 0.1 then return false end
	return math.deg(math.acos(math.clamp(f:Dot(v.Unit), -1, 1))) <= ang
end
-- alvo grande (guardiao): soma o raio do corpo (o centro do dragao fica longe da superficie atingida)
local function naEsfera(c, r, alvo)
	local extra = alvo:GetAttribute("GuardiaoNinho") and (alvo:GetAttribute("CorpoRaio") or 8) * 1.6 or 0
	return (raiz(alvo).Position - c).Magnitude <= r + extra
end

-- ===== validacao ===============================================================================================
function N:podeUsar(hab)
	if self.m:GetAttribute("Incapacitado") then return false, "incapacitado" end
	if self.ocupado then return false, "ocupado" end
	local def = Cfg.habilidades[self:real(hab)] or Cfg.basicos[hab]; if not def then return false, "habilidade inexistente" end
	if not self:temHabilidade(hab) then return false, "habilidade nao pertence a forma " .. self.forma end
	if self.m:GetAttribute("Montaria_Transicao") then return false, "transicao de montaria" end
	if (self.recargas[hab] or 0) > os.clock() then return false, ("recarga %.1fs"):format(self.recargas[hab] - os.clock()) end
	if (def.energia or 0) > self.energia then return false, "energia" end
	if def.elemental and not table.find(self:elementos(), self.m:GetAttribute("ElementoAtivo")) then return false, "sem elemento valido" end
	if def.requerSolo then local ok, motivo = self:noSolo(def); if not ok then return false, motivo end end
	return true, def
end
-- usar(hab, opcoes): opcoes.alvo (Model) ou opcoes.direcao (Vector3); executa em task e retorna na hora
function N:usar(hab, op)
	op = op or {}
	local ok, def = self:podeUsar(hab); if not ok then return false, def end
	self.energia -= (def.energia or 0); self.m:SetAttribute("Energia", self.energia)
	self.recargas[hab] = os.clock() + def.recarga             -- compartilhada: chave = habilidade, nao elemento
	self.m:SetAttribute("RecargaFim_" .. hab, workspace:GetServerTimeNow() + def.recarga)    -- so exibicao (HUD); a validacao usa self.recargas
	self.m:SetAttribute("RecargaDur_" .. hab, def.recarga)
	self.ocupado = true                                        -- Dominio libera depois da animacao de ativacao
	local el = self.m:GetAttribute("ElementoAtivo")
	local noAr = self.m:GetAttribute("NoAr") == true
	self.m:SetAttribute("EmAtaque", def.emAtaque or self:real(hab))
	Passivas.marcarCombate(self.m)
	task.spawn(function()
		local okE, err = pcall(self["_" .. self:real(hab)], self, def, el, noAr, op)
		if not okE then warn("Combate " .. hab .. ": " .. tostring(err)) end
		self.ocupado = false; self.m:SetAttribute("EmAtaque", nil)
	end)
	return true
end
function N:direcaoPara(op)
	if op.alvo and raiz(op.alvo) then return plano(raiz(op.alvo).Position - self.m:GetPivot().Position).Unit end
	if typeof(op.direcao) == "Vector3" and plano(op.direcao).Magnitude > 0.1 then return plano(op.direcao).Unit end
	return self:frente()
end

-- ===== basicos =================================================================================================
function N:_Mordida(def, el, noAr)
	FX:FireAllClients({d = self.m, hab = "Mordida", fase = "preparo", el = el})
	-- PATCH_MORDIDA_MOVIMENTO (03/11): andando no chao (modelos com MordidaEmMovimento), so pescoco/cabeca/mandibula (_Sup)
	local mov = not noAr and self.m:GetAttribute("MordidaEmMovimento") and (self.m:GetAttribute("Velocidade") or 0) > 3
	local nomeM = (mov and self:clipe("Ataque_Mordida_Sup", false)) and "Ataque_Mordida_Sup" or "Ataque_Mordida"
	local t = self:tocar(nomeM, noAr, {Impacto = 0.74}, function(n)
		if n == "Impacto" then
			local b = self:boca(); local alvos = {}
			for _, a in ipairs(self:alvosValidos()) do if naEsfera(b + self:frente() * 6, def.raio, a) and self:visivel(b, a) then table.insert(alvos, a) end end
			self:aplicar(alvos, def.dano, "Mordida", def.intensidade, el)
			FX:FireAllClients({d = self.m, hab = "Mordida", fase = "impacto", pos = b, el = el, acertou = #alvos > 0})
		end
	end)
	task.wait(math.max(t and t.Length or 0, 1.4) - 0.1)
end
function N:_Garra(def, el, noAr)
	local esquerda = math.random() < 0.5
	FX:FireAllClients({d = self.m, hab = "Garra", fase = "preparo", el = el})
	local t = self:tocar(esquerda and def.clipe or def.clipeD, false, {Impacto = 0.72}, function(n)
		if n == "Impacto" then
			local pe = (esquerda and self.peE or self.peD).TransformedWorldCFrame.Position + self:frente() * 3
			local alvos = {}
			for _, a in ipairs(self:alvosValidos()) do if naEsfera(pe, def.raio, a) then table.insert(alvos, a) end end
			self:aplicar(alvos, def.dano, "Garra", def.intensidade, el)
			FX:FireAllClients({d = self.m, hab = "Garra", fase = "impacto", pos = pe, el = el, acertou = #alvos > 0})
		end
	end)
	task.wait(math.max(t and t.Length or 0, 1.5) - 0.1)
end
function N:_Cauda(def, el)
	local t = self:tocar("Ataque_Cauda", false, {Impacto = 0.92}, function(n)
		if n == "Impacto" then
			local q = self.quadril.TransformedWorldCFrame.Position; local f = self:frente(); local alvos = {}
			for _, a in ipairs(self:alvosValidos()) do
				local v = plano(raiz(a).Position - q)
				if v.Magnitude <= def.raio and (v.Magnitude < 1 or f:Dot(v.Unit) < 0.35) then table.insert(alvos, a) end   -- lados/tras
			end
			self:aplicar(alvos, def.dano, "Cauda", def.intensidade, el)
			FX:FireAllClients({d = self.m, hab = "Cauda", fase = "impacto", pos = q - f * 40, el = el})
		end
	end)
	task.wait(math.max(t and t.Length or 0, 1.8) - 0.1)
end
function N:_Rugido(def, el, noAr)
	-- PATCH_RUGIDOS_FOGO: clipe por situacao (config porForma); sem config, o rugido padrao (camada no ar)
	local nome, tEm, camada = "Rugido_Combate", def.emissao or 0.95, noAr
	local pf = def.porForma and def.porForma[self.forma]
	if pf then
		local esc = noAr and pf.ar or ((self.m:GetAttribute("Velocidade") or 0) > 3 and pf.mov) or pf.chao
		if esc and self:clipe(esc[1], false) then nome, tEm, camada = esc[1], esc[2], false end
	end
	FX:FireAllClients({d = self.m, hab = "Rugido", fase = "preparo", el = el, noAr = noAr})
	local t = self:tocar(nome, camada, {RugidoInicio = tEm}, function(n)
		if n == "RugidoInicio" then FX:FireAllClients({d = self.m, hab = "Rugido", fase = "emissao", el = el, tipo = noAr and "aereo" or "combate"}) end
	end)
	task.wait(math.max(t and t.Length or 0, tEm + 0.6) - 0.1)
end

-- ===== habilidades oficiais (prototipos) ======================================================================
function N:_Sopro(def, el, noAr, op)
	local e = def.porElemento[el]
	FX:FireAllClients({d = self.m, hab = "Sopro", fase = "preparo", el = el})
	local px = def.clipes or "Sopro"
	-- PATCH_SOPRO_MOVIMENTO (02/11): andando/voando, so pescoco/cabeca/mandibula (_Sup); as patas e asas seguem a locomocao
	local function movendo() return (self.m:GetAttribute("Velocidade") or 0) > 3 end
	local function escolher(nome) return (movendo() and self:clipe(nome .. "_Sup", noAr)) and (nome .. "_Sup") or nome end
	local t0 = self:tocar(escolher(px .. "_Inicio"), noAr, {Emissao = 1.05}, function() end)
	task.wait(1.05)
	local loopMov = movendo()
	local loop = self:clipe(escolher(px .. "_Loop"), noAr); if loop then loop.Looped = true; loop:Play(0.1) end
	if t0 then t0:Stop(0.1) end
	local alvoPos = op.alvo and raiz(op.alvo) and raiz(op.alvo).Position
	if not alvoPos and typeof(op.direcao) == "Vector3" and op.direcao.Magnitude > 0.1 then   -- montado: mira pela camera, so a frente
		local d = op.direcao.Unit
		if plano(d).Magnitude > 0.1 and plano(d).Unit:Dot(self:frente()) > 0.35 then alvoPos = self:boca() + d * e.alcance end
	end
	FX:FireAllClients({d = self.m, hab = "Sopro", fase = "emissao", el = el, forma = e.forma, alcance = e.alcance, angulo = e.angulo, duracao = def.emissao, alvoPos = alvoPos})
	local fim = os.clock() + def.emissao
	if e.forma == "projetil" then
		for i = 1, e.quantidade do
			local b, f = self:boca()
			local destino = alvoPos and (alvoPos + Vector3.new(math.random(-6, 6), 0, math.random(-6, 6))) or (b + f * e.alcance)
			local dir = (destino - b); if dir.Magnitude > e.alcance then destino = b + dir.Unit * e.alcance end
			rp.FilterDescendantsInstances = {workspace.Terrain}
			local hit = workspace:Raycast(b, destino - b, rp); if hit then destino = hit.Position end
			local voo = (destino - b).Magnitude / e.velocidade
			FX:FireAllClients({d = self.m, hab = "Sopro", fase = "projetil", el = el, de = b, ate = destino, tempo = voo})
			task.delay(voo, function()
				local alvos = {}
				for _, a in ipairs(self:alvosValidos()) do if naEsfera(destino, e.raioImpacto, a) then table.insert(alvos, a) end end
				self:aplicar(alvos, e.dano, "Sopro", "moderado", el)
				FX:FireAllClients({d = self.m, hab = "Sopro", fase = "impacto", pos = destino, el = el})
			end)
			task.wait(def.emissao / e.quantidade)
		end
	else
		local pulsos = 0
		-- SOPRO CONTINUO (oficial 29/10): segurando a tecla, segue enquanto houver energia (ate emissaoMax); a mira do
		-- cursor atualiza a direcao dentro do cone do pescoco; alem da emissao base consome energia por segundo
		local t0, ultMira = os.clock(), 0
		while true do
			local agora = os.clock()
			local segue = op.segurar and self.segurando ~= false and agora - t0 < (def.emissaoMax or 6) and self.energia > 0
			if not self.m.Parent or self.m:GetAttribute("Incapacitado") then break end   -- removido/incapacitado: encerra ja
			if movendo() ~= loopMov then                                  -- comecou/parou de andar no meio do sopro: troca com fade
				loopMov = movendo()
				local novoLoop = self:clipe(escolher(px .. "_Loop"), noAr)
				if novoLoop and novoLoop ~= loop then
					novoLoop.Looped = true; novoLoop:Play(0.25); if loop then loop:Stop(0.25) end; loop = novoLoop
				end
			end
			if agora >= fim and not segue then break end
			if op.segurar and self.segurando == false and agora - t0 > 0.5 then break end
			if agora > fim then self.energia = math.max(0, self.energia - (def.energiaSeg or 8) * def.tick); self.m:SetAttribute("Energia", self.energia) end
			if op.segurar and self.miraDir then
				local d = self.miraDir; local pd = plano(d)
				if pd.Magnitude > 0.1 and pd.Unit:Dot(self:frente()) > 0.25 and math.abs(d.Y) < 0.85 then
					local novo = self:boca() + d * e.alcance
					if not alvoPos or (novo - alvoPos).Magnitude > 3 then
						alvoPos = novo
						if agora - ultMira > 0.12 then ultMira = agora; FX:FireAllClients({d = self.m, hab = "Sopro", fase = "mira", el = el, alvoPos = alvoPos}) end
					end
				end
			end
			local b, f = self:boca()
			if alvoPos then local v = alvoPos - b; f = v.Magnitude > 1 and v.Unit or f end
			local alvos = {}
			if e.forma == "cone" then
				for _, a in ipairs(self:alvosValidos()) do if noCone(b, f, a, e.alcance, e.angulo) and self:visivel(b, a) then table.insert(alvos, a) end end
			elseif e.forma == "descarga" and pulsos < e.pulsos then
				pulsos += 1
				rp.FilterDescendantsInstances = {workspace.Terrain}
				local fimRaio = b + f * e.alcance; local hit = workspace:Raycast(b, f * e.alcance, rp); if hit then fimRaio = hit.Position end
				for _, a in ipairs(self:alvosValidos()) do
					local p = raiz(a).Position; local s = math.clamp((p - b):Dot(f), 0, (fimRaio - b).Magnitude)
					if (b + f * s - p).Magnitude <= e.largura + 3 then table.insert(alvos, a) end
				end
				FX:FireAllClients({d = self.m, hab = "Sopro", fase = "pulso", el = el, de = b, ate = fimRaio})
			end
			if #alvos > 0 then self:aplicar(alvos, e.dano, "Sopro", "leve", el, def.frost) end
			task.wait(e.forma == "descarga" and def.emissao / e.pulsos or def.tick)
		end
	end
	if loop then loop:Stop(0.15) end
	self.segurando = nil; self.miraDir = nil
	FX:FireAllClients({d = self.m, hab = "Sopro", fase = "fim", el = el})
	local tf = self:tocar(escolher(px .. "_Fim"), noAr, {}, function() end); task.wait(0.8)
end

-- PATCH_ARREMETIDA_5S (atualizacao oficial 02/11): Arremetida = 5 s de velocidade extraordinaria. Montado, quem move o
-- corpo e o PROPRIO controlador da montaria (le ArremetidaFim: acelera a partir da velocidade atual, o jogador dirige,
-- colisoes e relevo do controlador valem; no fim desacelera). Na IA (sem controlador): perseguicao integrada quadro a
-- quadro (v*dt, giro limitado, para antes de parede). Aqui so a vigia da cabeca: alvo valido a frente -> UMA mordida
-- devastadora por ativacao (mandibula abre antes do contato, dano so se a cabeca alcancar), que encerra a fase ofensiva.
local function cabecaPos(self) return (self.focinho or self.cabeca).TransformedWorldCFrame.Position end
-- a mordida alcanca? horizontal a partir da frente da boca + faixa vertical (o pescoco desce/mira o alvo na mordida)
local function alcancaMordida(self, def, a)
	local c = cabecaPos(self) + self:frente() * def.avancoMordida; local r = raiz(a).Position
	local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) * 1.6 or 0
	return plano(r - c).Magnitude <= def.raioMordida + extra and math.abs(r.Y - c.Y) <= (def.alturaMordida or 22) + extra
end
function N:mordidaArremetida(def, el, noAr, alvo, vel)
	local m = self.m
	m:SetAttribute("AlvoGolpe", raiz(alvo).Position)                         -- cliente: cabeca/pescoco encaram o alvo
	FX:FireAllClients({d = m, hab = "Arremetida", fase = "mordida", el = el, alvo = alvo})
	-- clipe: andando/voando so pescoco/cabeca/mandibula (_Sup), sobre a locomocao; a mandibula fecha no contato previsto
	local nome = self:clipe("Ataque_Mordida_Sup", noAr) and "Ataque_Mordida_Sup" or "Ataque_Mordida"
	local t = self:clipe(nome, noAr)
	local dist = plano(raiz(alvo).Position - cabecaPos(self)).Magnitude
	local tContato = math.clamp((dist - def.raioMordida) / math.max(vel, 1), 0.12, 0.6)
	local fecha = 0.74                                                       -- marcador Impacto do Ataque_Mordida (s)
	if t then t.Looped = false; t:Play(0.08, 1, math.clamp(fecha / tContato, 1, 3.2)) end
	local acertou = false
	local t0 = os.clock()
	while os.clock() - t0 < tContato + 0.25 and m.Parent and alvo.Parent do       -- fechamento: dano so se a cabeca alcancar
		RunService.Heartbeat:Wait()
		if alcancaMordida(self, def, alvo) and os.clock() - t0 >= tContato * 0.7 then acertou = true; break end
	end
	m:SetAttribute("AlvoGolpe", nil)
	if not acertou then FX:FireAllClients({d = m, hab = "Arremetida", fase = "erro", el = el}); return false end
	self:aplicar({alvo}, def.danoMordida, "Arremetida", def.intensidade, el)     -- + Burning (ferir); servidor valida tudo
	self:empurrar({alvo}, cabecaPos(self) - self:frente() * 10, def.empurraoMordida, def.empurraoMordida * 0.3, "Arremetida")
	m:SetAttribute("ArremetidaImpacto", workspace:GetServerTimeNow())           -- controlador: tranco de desaceleracao
	FX:FireAllClients({d = m, hab = "Arremetida", fase = "impacto", el = el, pos = raiz(alvo).Position, acertou = true, mordida = true, vel = vel})
	return true
end
function N:_Arremetida(def, el, noAr, op)
	local m = self.m
	local montado = m:GetAttribute("Controlador") == "Montaria"
	FX:FireAllClients({d = m, hab = "Arremetida", fase = "preparo", el = el, noAr = noAr, duracao = def.duracao})
	m:SetAttribute("ArremetidaFim", workspace:GetServerTimeNow() + def.duracao)
	FX:FireAllClients({d = m, hab = "Arremetida", fase = "emissao", el = el, noAr = noAr, duracao = def.duracao})
	-- IA: estado da perseguicao integrada (montado, nada disto e usado)
	local gp = RaycastParams.new(); gp.FilterType = Enum.RaycastFilterType.Include; gp.FilterDescendantsInstances = {workspace.Terrain, workspace:FindFirstChild("Baseplate")}
	local function chao(p) local h = workspace:Raycast(p + Vector3.new(0, 45, 0), Vector3.new(0, -300, 0), gp); return h and h.Position.Y end
	local piv = m:GetPivot(); local rot = piv.Rotation; local pos = piv.Position
	local alt0 = pos.Y - (chao(pos) or pos.Y)
	local dir = self:frente()                                                  -- parte do rumo do corpo; corrige ate o alvo
	local v = montado and (m:GetAttribute("Velocidade") or 0) or 8                -- IA: o atributo pode estar velho
	local vMax, acel = noAr and def.velAr or def.velChao, noAr and def.acelAr or def.acelChao
	local mordeu = false; local proxTentativa = 0
	local t0 = os.clock()
	while m.Parent and not m:GetAttribute("Incapacitado") and os.clock() - t0 < def.duracao do
		local dt = RunService.Heartbeat:Wait()
		if montado then v = m:GetAttribute("Velocidade") or v
		else
			local alvoR = op.alvo and op.alvo.Parent and raiz(op.alvo)
			local alinh = 1
			if alvoR then                                                       -- correcao de rumo limitada (nada de curva instantanea)
				local want = plano(alvoR.Position - pos); if want.Magnitude > 1 then
					local ang = math.atan2(dir:Cross(want.Unit).Y, dir:Dot(want.Unit))
					alinh = math.cos(ang)
					-- devagar vira mais (patas/asas reposicionam); rapido, curva aberta: nada de orbitar o alvo
					local giro = math.rad(def.giroIA) * (1 + 1.2 * math.clamp(1 - v / vMax, 0, 1))
					local passo = math.clamp(ang, -giro * dt, giro * dt)
					dir = CFrame.Angles(0, passo, 0):VectorToWorldSpace(dir)
					rot = CFrame.Angles(0, passo, 0) * rot                         -- o corpo gira junto (mesmo offset do rig)
				end
			end
			local vAlvo = vMax * math.clamp(alinh, 0.3, 1)                       -- alvo fora do eixo: segura a velocidade para alinhar
			v = v < vAlvo and math.min(vAlvo, v + acel * dt) or math.max(vAlvo, v - acel * 1.5 * dt)
			if workspace:Spherecast(pos + Vector3.new(0, 20, 0), 14, dir * math.max(22, v * dt * 3), gp) then break end   -- parede: para
			local nova = pos + dir * v * dt
			local y
			if noAr then
				-- no ar: MERGULHA/sobe em direcao a CABECA do alvo (troca velocidade horizontal por vertical, ate 60 graus)
				local pitch = 0
				if alvoR then
					local dyw = alvoR.Position.Y - cabecaPos(self).Y; local dh = plano(alvoR.Position - pos).Magnitude
					pitch = math.clamp(math.atan2(dyw, math.max(dh, 1)), -math.rad(60), math.rad(45))
				end
				nova = pos + dir * v * math.cos(pitch) * dt
				y = pos.Y + v * math.sin(pitch) * dt
				local g = chao(nova); if g then y = math.max(y, g + 4) end
			else y = (chao(nova) or (nova.Y - alt0)) + alt0 end
			pos = Vector3.new(nova.X, y, nova.Z)
			m:PivotTo(CFrame.new(pos) * rot)
			m:SetAttribute("Velocidade", math.floor(v))
		end
		-- vigia: inimigo valido na trajetoria da cabeca, no tempo de abrir a mandibula
		if not mordeu and os.clock() >= proxTentativa then
			local c = cabecaPos(self); local f = self:frente()
			for _, a in ipairs(self:alvosValidos()) do
				local r = raiz(a); local rel = plano(r.Position - c)                -- horizontal (a altura tem faixa propria)
				local frente = rel:Dot(f); local lado = (rel - f * frente).Magnitude
				local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) * 1.6 or 0
				if frente > -4 and frente <= def.raioMordida + extra + v * def.antecipa and lado <= def.raioMordida + extra + (montado and 4 or 0)
					and math.abs(r.Position.Y - c.Y) <= (def.alturaMordida or 22) + extra and self:visivel(c, a) then
					if self:mordidaArremetida(def, el, noAr, a, v) then mordeu = true else proxTentativa = os.clock() + 0.3 end
					break
				end
			end
			if mordeu then break end                                             -- 1 mordida por ativacao: fim da fase ofensiva
		end
	end
	m:SetAttribute("ArremetidaFim", nil)                                         -- o controlador desacelera (sem parada brusca)
	FX:FireAllClients({d = m, hab = "Arremetida", fase = "fim", el = el, mordeu = mordeu})
	if mordeu then task.wait(def.recuperacao) end
end

-- Tempestade de Asas: terrestre = agacha, IMPULSO (o corpo sobe de verdade, def.elevacao) e batidas repetidas; aerea =
-- batidas direto, sem decolagem. Cada batida REAL do clipe (def.batidasChao/batidasAr) solta uma onda de vento quente:
-- dano (1a cheia, demais x fatorSecundario) + empurrao para fora, 1 acerto por alvo POR BATIDA.
local gpTerreno = RaycastParams.new(); gpTerreno.FilterType = Enum.RaycastFilterType.Include
function N:empurrar(alvos, origem, horizontal, vertical, hab)
	for _, a in ipairs(alvos) do
		local r = raiz(a)
		if r and not a:GetAttribute("GuardiaoNinho") then                       -- guardiao (ancorado) nao e lancado
			local v = plano(r.Position - origem); v = v.Magnitude > 0.1 and v.Unit or self:frente()
			local vel = v * horizontal + Vector3.new(0, vertical, 0)
			local plr = Players:GetPlayerFromCharacter(a)
			if plr then FX:FireClient(plr, {d = self.m, hab = hab, fase = "lancamento", vel = vel})   -- personagem e do cliente
			elseif not r.Anchored then
				local h = a:FindFirstChildOfClass("Humanoid"); if h then h:ChangeState(Enum.HumanoidStateType.Jumping) end
				r.AssemblyLinearVelocity = vel
			end
		end
	end
end
function N:_Tempestade(def, el, noAr)
	-- PATCH_TEMPESTADE_V2: linha do tempo explicita (clipes + batidas); cada batida = 1 onda (dano/empurrao/FX)
	local batidas = noAr and def.batidasAr or def.batidasChao
	local dur = noAr and def.clipeAr * def.voltasAr or (def.retomaQueda + def.pousoApos + 0.45)
	FX:FireAllClients({d = self.m, hab = "Tempestade", fase = "preparo", el = el, noAr = noAr, batidas = batidas, duracao = dur})
	local base = self.m:GetPivot()
	gpTerreno.FilterDescendantsInstances = {workspace.Terrain, workspace:FindFirstChild("Baseplate")}
	local function chaoSob(p) local h = workspace:Raycast(p + Vector3.new(0, 30, 0), Vector3.new(0, -400, 0), gpTerreno); return h and h.Position, h end
	local feitas = {}
	local function batida(i)
		if feitas[i] or not self.m.Parent or self.m:GetAttribute("Incapacitado") then return end; feitas[i] = true
		local c = self.m:GetPivot().Position; local solo, hit = chaoSob(c)
		local centro = solo or c
		local altura = solo and (c.Y - solo.Y) or 999
		local alvos = {}
		for _, a in ipairs(self:alvosValidos()) do
			if naEsfera(centro, def.raio, a) and self:visivel(c + Vector3.new(0, 25, 0), a) then table.insert(alvos, a) end
		end
		local fator = i == 1 and 1 or def.fatorSecundario
		local fe = i == 1 and 1 or def.fatorEmpurraoSec
		self:aplicar(alvos, def.dano * fator, "Tempestade", def.intensidade, el)
		self:empurrar(alvos, centro, def.empurrao.horizontal * fe, def.empurrao.vertical * fe, "Tempestade")
		FX:FireAllClients({d = self.m, hab = "Tempestade", fase = "batida", el = el, pos = centro, raio = def.raio, altura = altura,
			frente = self:frente(), indice = i, total = #batidas, superficie = hit ~= nil and altura <= 60, material = hit and hit.Material.Name,
			alvos = #alvos})
	end
	local t0 = os.clock()
	for i, tb in ipairs(batidas) do task.delay(tb, function() batida(i) end) end
	if noAr then
		local t = self:clipe("Tempestade_Asas_Ar", false)
		if t then t.Looped = true; t:Play(0.2) end
		task.wait(dur - 0.1)
		if t then t:Stop(0.35); t.Looped = false end
		return
	end
	local tc = self:tocar("Tempestade_Asas", false, {}, function() end)
	self.m:SetAttribute("CorpoElevado", true)
	local H = def.elevacao or 10
	local tImp, tDesce = 1.1, def.retomaQueda
	task.delay(tImp, function()
		if self.m.Parent then FX:FireAllClients({d = self.m, hab = "Tempestade", fase = "impulso", el = el, pos = chaoSob(base.Position) or base.Position, duracao = dur - tImp}) end
	end)
	-- elevacao REAL do corpo: impulso (sobe com desaceleracao), sustentacao com leve oscilacao das batidas, descida no fim
	task.spawn(function()
		while self.m.Parent and os.clock() - t0 < dur do
			RunService.Heartbeat:Wait()
			local k = os.clock() - t0
			local h = 0
			if k >= tImp and k < tImp + 0.45 then h = H * (1 - (1 - (k - tImp) / 0.45) ^ 2)
			elseif k >= tImp + 0.45 and k < tDesce then h = H + 0.8 * math.sin((k - tImp) * 7.2)
			elseif k >= tDesce and k < tDesce + def.pousoApos then local x = (k - tDesce) / def.pousoApos; h = H * (1 - x * x)
			end
			self.m:PivotTo(base + Vector3.new(0, math.max(h, 0), 0))
		end
	end)
	-- 3a batida -> clipe aereo (mais 2 batidas no alto) -> trecho final do clipe terrestre (descida e pouso)
	task.wait(def.trocaAr)
	local ar = self:clipe("Tempestade_Asas_Ar", false)
	if ar and self.m.Parent then ar.Looped = false; ar:Play(0.3); if tc then tc:Stop(0.3) end end
	task.wait(def.retomaQueda - def.trocaAr)
	if tc and self.m.Parent then tc:Play(0.25); tc.TimePosition = def.quedaClipe end
	if ar then ar:Stop(0.25) end
	task.wait(def.pousoApos)
	if self.m.Parent then FX:FireAllClients({d = self.m, hab = "Tempestade", fase = "pouso", el = el, pos = chaoSob(base.Position) or base.Position}) end
	task.wait(math.max(0.1, dur - (os.clock() - t0)))
	self.m:SetAttribute("CorpoElevado", nil)
	self.m:PivotTo(base)
end

function N:_Dominio(def, el, noAr)
	self:tocar("Dominio", noAr, {Ativacao = 1.6}, function(n)
		if n == "Ativacao" then
			self.m:SetAttribute("DominioAtivo", true)
			FX:FireAllClients({d = self.m, hab = "Dominio", fase = "ativar", el = el, duracao = def.duracao})
		end
	end)
	task.wait(3.1); self.ocupado = false; self.m:SetAttribute("EmAtaque", nil)
	task.wait(math.max(0, def.duracao - 1.5))
	self.m:SetAttribute("DominioAtivo", nil)
	FX:FireAllClients({d = self.m, hab = "Dominio", fase = "encerrar", el = el})
end

-- ===== Ruptura Vulcanica (propria do Dragao das Montanhas; exige solo) =========================================
local function filtroMundo(self)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude
	local ex = {self.m}
	for _, pl in ipairs(Players:GetPlayers()) do if pl.Character then table.insert(ex, pl.Character) end end
	for _, h in ipairs(workspace:GetDescendants()) do if h:IsA("Humanoid") then table.insert(ex, h.Parent) end end
	local fx = workspace:FindFirstChild("VFX_Temporarios"); if fx then table.insert(ex, fx) end
	p.FilterDescendantsInstances = ex; return p
end
function N.emEstrutura(pos)
	for _, z in ipairs(CS:GetTagged(Cfg.estruturaProtegidaTag)) do
		if z:IsA("BasePart") then
			local p = z.CFrame:PointToObjectSpace(pos); local s = z.Size / 2 + Vector3.new(2, 2, 2)
			if math.abs(p.X) <= s.X and math.abs(p.Y) <= s.Y and math.abs(p.Z) <= s.Z then return true end
		end
	end
	return false
end
function N:centroCorpo()                                             -- meio do tronco (entre quadril e ombros), nao o pivo
	local q = self.quadril.TransformedWorldCFrame.Position
	local c3 = osso(self.m, "Coluna3") or osso(self.m, "Coluna2"); local o = c3 and c3.TransformedWorldCFrame.Position or q
	return (q + o) / 2
end
-- silhueta do corpo no plano (pose atual): segmentos osso-pai -> osso-filho com folga, e poligonos das membranas
local function distSeg2(p, a, b)
	local ab = Vector2.new(b.X - a.X, b.Z - a.Z); local ap = Vector2.new(p.X - a.X, p.Z - a.Z)
	local t = ab.Magnitude > 1e-4 and math.clamp(ap:Dot(ab) / ab:Dot(ab), 0, 1) or 0
	return (ap - ab * t).Magnitude
end
local function dentroPoligono(p, pts)
	local dentro = false; local j = #pts
	for i = 1, #pts do
		local a, b = pts[i], pts[j]
		if ((a.Z > p.Z) ~= (b.Z > p.Z)) and (p.X < (b.X - a.X) * (p.Z - a.Z) / (b.Z - a.Z) + a.X) then dentro = not dentro end
		j = i
	end
	return dentro
end
function N:silhueta()
	local def = Cfg.habilidades.Ruptura
	local segs, membranas = {}, {}
	local pos = {}
	for _, b in ipairs(self.m:GetDescendants()) do if b:IsA("Bone") then pos[b] = b.TransformedWorldCFrame.Position end end
	for b, p in pairs(pos) do
		if b.Parent:IsA("Bone") and pos[b.Parent] then
			local asa = b.Name:find("Asa") or b.Name:find("Dedo")
			table.insert(segs, {pos[b.Parent], p, asa and def.folgaAsa or def.folgaCorpo})
		end
	end
	for _, l in ipairs({"E", "D"}) do                                  -- membrana: ombro da asa + cotovelo + pontas dos dedos
		local pts = {}
		for _, n in ipairs({"Asa" .. l .. "_1", "Asa" .. l .. "_2", "Dedo1" .. l, "Dedo2" .. l, "Dedo3" .. l}) do
			local b = osso(self.m, n); if b then table.insert(pts, pos[b]) end
			for _, f in ipairs(b and b:GetChildren() or {}) do if f:IsA("Bone") then table.insert(pts, pos[f]) end end   -- pontas
		end
		local q = self.quadril.TransformedWorldCFrame.Position; table.insert(pts, q)
		-- ordena em volta do centroide para formar o poligono
		local cx, cz = 0, 0; for _, p in ipairs(pts) do cx += p.X; cz += p.Z end; cx /= #pts; cz /= #pts
		table.sort(pts, function(a, b) return math.atan2(a.Z - cz, a.X - cx) < math.atan2(b.Z - cz, b.X - cx) end)
		table.insert(membranas, pts)
	end
	return {intersecta = function(_, p, r)
		for _, s in ipairs(segs) do if distSeg2(p, s[1], s[2]) < s[3] + r then return true end end
		for _, pts in ipairs(membranas) do if dentroPoligono(p, pts) then return true end end
		return false
	end}
end
function N:centroPatas()
	local a, b = self.peE.TransformedWorldCFrame.Position, self.peD.TransformedWorldCFrame.Position
	return (a + b) / 2
end
function N:noSolo(def)
	if self.m:GetAttribute("NoAr") then return false, "no ar (Ruptura exige solo)" end
	local c = self:centroPatas()
	local hit = workspace:Raycast(c + Vector3.new(0, 10, 0), Vector3.new(0, -(10 + def.distSoloMax + 10), 0), filtroMundo(self))
	if not hit then return false, "sem solo" end
	-- pes traseiros tambem apoiados (evita borda/salto)
	local tE = osso(self.m, "PernaTE_3") or osso(self.m, "back_foot_l")
	if tE then
		local p = tE.TransformedWorldCFrame.Position
		local h2 = workspace:Raycast(p + Vector3.new(0, 10, 0), Vector3.new(0, -(20 + def.distSoloMax), 0), filtroMundo(self))
		if not h2 or p.Y - h2.Position.Y > def.distSoloMax + 4 then return false, "sem apoio traseiro" end
	end
	if c.Y - hit.Position.Y > def.distSoloMax + 4 then return false, "patas longe do chao" end
	return true
end
function N:_Ruptura(def, el, noAr, op)
	local atingidos = {}                                              -- um acerto por alvo por uso (onda + pilares)
	local function acertar(centro, raio, origem)
		local l = {}
		for _, a in ipairs(self:alvosValidos()) do
			if not atingidos[a] and naEsfera(centro, raio, a) and self:visivel(centro + Vector3.new(0, 4, 0), a) then atingidos[a] = true; table.insert(l, a) end
		end
		if #l == 0 then return end
		self:aplicar(l, def.dano, "Ruptura", def.intensidade, "Fogo")
		for _, a in ipairs(l) do                                      -- reacao curta de lancamento (para fora + para cima)
			local r = raiz(a); local v = plano(r.Position - origem); v = v.Magnitude > 0.1 and v.Unit or self:frente()
			local vel = v * def.lancamento.horizontal + Vector3.new(0, def.lancamento.vertical, 0)
			local plr = Players:GetPlayerFromCharacter(a)
			if plr then FX:FireClient(plr, {d = self.m, hab = "Ruptura", fase = "lancamento", vel = vel})   -- personagem e do cliente
			else
				local h = a:FindFirstChildOfClass("Humanoid"); if h then h:ChangeState(Enum.HumanoidStateType.Jumping) end
				r.AssemblyLinearVelocity = vel
			end
		end
	end
	local frente = self:direcaoPara(op)
	FX:FireAllClients({d = self.m, hab = "Ruptura", fase = "preparo", el = "Fogo"})
	local impacto = false
	local t = self:tocar("Ruptura_Vulcanica", false, {RuptureImpact = 1.4, RuptureEruption = 1.65, RuptureEnd = 3.4}, function(n)
		if n == "RuptureImpact" and not impacto then
			impacto = true
			if self.m:GetAttribute("NoAr") then return end
			local c = self:centroPatas()
			local hit = workspace:Raycast(c + Vector3.new(0, 10, 0), Vector3.new(0, -40, 0), filtroMundo(self))
			local chao = hit and hit.Position or c
			self.impactoPos = chao
			FX:FireAllClients({d = self.m, hab = "Ruptura", fase = "impacto", pos = chao, raio = def.ondaRaio})
			acertar(chao, def.ondaRaio, chao)                         -- onda curta junto as patas (o golpe)
			-- pilares EM VOLTA do dragao (360 graus), centrados no corpo, com zona interna livre. Cada posicao e validada:
			-- fora do corpo inteiro (ossos do tronco/pescoco/cabeca/cauda/pernas + membranas das asas, na pose ATUAL),
			-- sobre superficie real e firme, sem teto, sem parede entre o centro e o pilar, longe de ovos e estruturas.
			local centro = self:centroCorpo()
			local hc = workspace:Raycast(centro + Vector3.new(0, 20, 0), Vector3.new(0, -80, 0), filtroMundo(self))
			local solo = hc and hc.Position or chao
			local ovos = {}; for _, o in ipairs(workspace:GetDescendants()) do if o.Name == "Ovo" and o:IsA("BasePart") then table.insert(ovos, o.Position) end end
			local fp = filtroMundo(self)
			local corpo = self:silhueta()
			local pilares, rejeitados = {}, {corpo = 0, solo = 0, parede = 0, ovo = 0}
			local giro0 = math.random() * math.pi * 2
			for i, R in ipairs(def.aneis) do
				local n = def.pilaresPorAnel[i]
				for k = 1, n do
					local ang = giro0 + (k - 0.5 + (i % 2) * 0.5) / n * math.pi * 2 + math.rad(math.random(-9, 9))
					local xz = solo + Vector3.new(math.cos(ang), 0, math.sin(ang)) * (R + math.random(-3, 3))
					local motivo
					if corpo:intersecta(xz, def.raioPilar * 0.5) then motivo = "corpo" end
					local h
					if not motivo then
						h = workspace:Raycast(xz + Vector3.new(0, 30, 0), Vector3.new(0, -70, 0), fp)
						if not (h and h.Normal.Y > 0.7 and math.abs(h.Position.Y - solo.Y) < 12) then motivo = "solo" end
					end
					if not motivo and (workspace:Raycast(h.Position + Vector3.new(0, 1, 0), Vector3.new(0, 24, 0), fp)
						or workspace:Raycast(solo + Vector3.new(0, 4, 0), (h.Position - solo) + Vector3.new(0, 0, 0), fp)) then motivo = "parede" end
					if not motivo then
						for _, o in ipairs(ovos) do if (o - h.Position).Magnitude < def.protecaoOvo then motivo = "ovo" end end
						if N.emEstrutura(h.Position) then motivo = "ovo" end
					end
					if motivo then rejeitados[motivo] += 1 else table.insert(pilares, {pos = h.Position, anel = i, normal = h.Normal}) end
				end
			end
			self.m:SetAttribute("UltimaRuptura", ("pilares=%d corpo=%d solo=%d parede=%d ovo/estrutura=%d"):format(#pilares, rejeitados.corpo, rejeitados.solo, rejeitados.parede, rejeitados.ovo))
			FX:FireAllClients({d = self.m, hab = "Ruptura", fase = "erupcao", pilares = pilares, intervalo = def.intervaloAnel, centro = solo})
			for i = 1, #def.aneis do
				task.delay(0.25 + (i - 1) * def.intervaloAnel, function()       -- pilar sai da terra 0,25 s apos o golpe: janela de esquiva
					for _, p in ipairs(pilares) do if p.anel == i then acertar(p.pos, def.raioPilar, chao) end end
				end)
			end
		end
	end)
	task.wait(math.max(t and t.Length or 0, 3.6) - 0.1)
	FX:FireAllClients({d = self.m, hab = "Ruptura", fase = "fim"})
end

-- ===== Coracao Infernal (oficial 30/10; substitui a Ruptura no Montanhas) ======================================
-- Linha do tempo: CARGA (peito e garganta brilham) -> EXPELE (a lamina sai do focinho e se estende ate o raio externo,
-- na direcao da cabeca) -> GIRO (a lamina gira ao redor do corpo, no plano horizontal da boca, centrada no tronco que
-- continua se movendo: no ar o voo nao para) -> DISSIPA. A mesma funcao de angulo roda no cliente (VFX) com o t0 do
-- servidor; o dano acompanha a trajetoria REAL: a cada quadro o setor varrido entre o angulo anterior e o atual e
-- testado (raio interno..externo, meia-largura da lamina, faixa vertical). 1 acerto por alvo por uso.
function N.coracaoEstado(def, t)
	-- devolve (angulo em rad a partir da direcao inicial, extensao 0..1, ativo)
	if t < 0 then return 0, 0, false end
	if t <= def.expele then local k = t / def.expele; return 0, 1 - (1 - k) ^ 3, true end
	local k = math.clamp((t - def.expele) / def.giro, 0, 1)
	return def.sentido * 2 * math.pi * def.voltas * (k * k * (3 - 2 * k)), 1, t <= def.expele + def.giro
end
local function anguloAssinado(de, para)                              -- em torno de +Y (positivo = anti-horario visto de cima)
	return math.atan2(de:Cross(para).Y, de:Dot(para))
end
function N:_Coracao(def, el, noAr, op)
	FX:FireAllClients({d = self.m, hab = "Coracao", fase = "carga", el = el, carga = def.carga})
	local t = self:tocar("Coracao_Infernal", noAr, {Expele = def.carga}, function() end)
	task.wait(def.carga)
	if not self.m.Parent or self.m:GetAttribute("Incapacitado") then return end
	-- geometria fixada no instante em que a lamina sai da boca
	local b = self:boca()
	local c0 = self:centroCorpo()
	local dir0 = plano(b - c0); dir0 = dir0.Magnitude > 1 and dir0.Unit or self:frente()
	local rIn = math.clamp(plano(b - c0).Magnitude, 6, 40)
	local dy = b.Y - c0.Y
	local t0 = workspace:GetServerTimeNow()
	FX:FireAllClients({d = self.m, hab = "Coracao", fase = "lamina", el = el, t0 = t0, dir0 = dir0, rIn = rIn, rOut = def.raioExterno,
		dy = dy, expele = def.expele, giro = def.giro, voltas = def.voltas, sentido = def.sentido, dissipa = def.dissipa, largura = def.larguraLamina})
	local atingidos = {}
	local angAnt = 0
	local fimAtivo = def.expele + def.giro
	while self.m.Parent and not self.m:GetAttribute("Incapacitado") do
		RunService.Heartbeat:Wait()
		local tt = workspace:GetServerTimeNow() - t0
		local ang, ext, ativo = N.coracaoEstado(def, tt)
		if not ativo then break end
		local centro = self:centroCorpo(); local yL = centro.Y + dy
		local alcance = rIn + (def.raioExterno - rIn) * ext
		local a0, a1 = math.min(angAnt, ang), math.max(angAnt, ang)
		for _, a in ipairs(self:alvosValidos()) do
			if not atingidos[a] then
				local p = raiz(a).Position
				local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) * 1.6 or 2
				local v = plano(p - centro); local r = v.Magnitude
				if r > 0.5 and r >= rIn - extra - 4 and r <= alcance + extra and math.abs(p.Y - yL) <= def.alturaFaixa + extra then
					local phi = anguloAssinado(dir0, v.Unit)
					local tol = math.asin(math.clamp((def.larguraLamina + extra) / r, 0, 1))
					-- o setor varrido pode passar de 360 graus: testa phi e as voltas equivalentes
					local dentro = false
					for k = -2, 2 do
						local q = phi + k * 2 * math.pi
						if q >= a0 - tol and q <= a1 + tol then dentro = true; break end
					end
					if dentro then
						atingidos[a] = true
						self:aplicar({a}, def.dano, "Coracao", def.intensidade, el)
						FX:FireAllClients({d = self.m, hab = "Coracao", fase = "impacto", el = el, pos = p})
					end
				end
			end
		end
		angAnt = ang
		if tt > fimAtivo then break end
	end
	self.m:SetAttribute("UltimoCoracao", ("alvos=%d raio=%d voltas=%.2f"):format((function() local n = 0; for _ in pairs(atingidos) do n += 1 end; return n end)(), def.raioExterno, def.voltas))
	task.wait(def.dissipa)
	local resto = t and (t.Length - (def.carga + fimAtivo + def.dissipa)) or 0
	if resto > 0 then task.wait(math.min(resto, 0.8)) end                  -- recuperacao do clipe
end

-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11) ===============================================================
function N:_SoproGlacial(def, el, noAr, op) return self:_Sopro(def, "Gelo", noAr, op) end
-- PATCH_SOPRO_UMBRAL (04/11): Sopro Umbral (Sombrio) = mesmo jato segurado com elemento Sombra; cada pulso causa dano
-- (com o multiplicador da Marca), mas o mesmo alvo ganha no maximo 1 marca por marcaIntervalo
function N:_SoproUmbral(def, el, noAr, op)
	Passivas.intervaloMarca[self.m] = def.marcaIntervalo
	local ok, err = pcall(self._Sopro, self, def, "Sombra", noAr, op)
	Passivas.intervaloMarca[self.m] = nil
	if not ok then error(err, 0) end
end
-- PATCH_CORRENTES_NOITE (04/11): Correntes da Noite (Sombrio, slot Arremetida). Longo alcance: o ponto vem da mira
-- (montado: direcao da boca ao cursor, com mira viva ate a batida; IA: o alvo). As garras batem no chao -> aviso curto
-- no ponto (tempo para sair) -> correntes de sombra saem do chao e PRENDEM ate maxAlvos alvos no raio (nao andam nem
-- pulam; podem atacar), com acerto inicial (Marca) e dano Sombra continuo enquanto presos (ticks: multiplicador da
-- Marca, sem marcar). Alvo no ar (acima de alturaChao) nao e preso. Recem-solto fica resistente por `resistencia` s:
-- novas correntes so causam o acerto. Dragoes/guardioes (sem Humanoid) so recebem dano. Numeros NAO_APROVADO.
-- PATCH_CORRENTES_AR (04/11, pedido do usuario: "as correntes tambem devem prender o aereo"): o alvo pode estar no AR.
-- Centro: alvo da IA / ponto mirado; se ali nao ha chao perto (mais de `alturaChao` acima), o centro fica no ar (no
-- alvo/ponto) e as correntes saem de fendas de sombra no ar (visual). Selecao: distancia 3D ao centro <= raio (+ corpo
-- dos guardioes). Prender: personagem (Humanoid) perde andar/pulo aos poucos e, se estiver no ar, e SEGURADO onde esta
-- (AlignPosition com forca crescente); dragao/guardiao (sem Humanoid) recebe PresoFator 1 -> 0 em `aperta` s, que a IA
-- (Locomotor) e a montaria usam para frear ate parar. Tempo preso, ticks, dano, Marca e resistencia iguais.
local presos, resistente = {}, {}                                     -- [alvo] = {ate, ws, pulo, usaJP, fonte, ...} / [alvo] = os.clock()
N.presosCorrentes = presos
local function soltarCorrente(a)
	local p = presos[a]; if not p then return end
	presos[a] = nil
	local h = a.Parent and a:FindFirstChildOfClass("Humanoid")
	if h then h.WalkSpeed = p.ws; if p.usaJP then h.JumpPower = p.pulo else h.JumpHeight = p.pulo end end
	if p.segura then p.segura:Destroy() end; if p.ancA then p.ancA:Destroy() end
	if a.Parent then a:SetAttribute("PresoCorrentes", nil); a:SetAttribute("PresoFator", nil) end
	FX:FireAllClients({d = p.fonte, hab = "Correntes", fase = "soltar", alvo = a, el = "Sombra"})
end
local rpC = RaycastParams.new(); rpC.FilterType = Enum.RaycastFilterType.Exclude
local function chaoAbaixo(pos, ignorar, ate)
	rpC.FilterDescendantsInstances = ignorar
	local h = workspace:Raycast(pos + Vector3.new(0, 6, 0), Vector3.new(0, -(ate or 400) - 6, 0), rpC); return h and h.Position
end
function N:_Correntes(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	local ignorar = {m}; for _, a in ipairs(self:alvosValidos()) do table.insert(ignorar, a) end
	local vfx = workspace:FindFirstChild("VFX_Temporarios"); if vfx then table.insert(ignorar, vfx) end
	self.miraDir = nil                                                     -- so a mira desta ativacao (mira viva do cliente)
	FX:FireAllClients({d = m, hab = "Correntes", fase = "preparo", el = el, noAr = noAr})
	self:tocar(def.clipe, noAr, {}, function() end)
	local batida = noAr and def.batidaAr or def.batida
	task.wait(batida)
	if not m.Parent or m:GetAttribute("Incapacitado") then return end
	-- ponto: alvo da IA ou mira; perto do chao -> centro no chao; longe -> centro no ar (no proprio ponto)
	local p
	if op.alvo and raiz(op.alvo) then p = raiz(op.alvo).Position
	else
		local d = self.miraDir or (typeof(op.direcao) == "Vector3" and op.direcao.Magnitude > 0.1 and op.direcao.Unit) or self:frente()
		local b = self:boca()
		rpC.FilterDescendantsInstances = {m, vfx}                            -- a mira PODE acertar um alvo no ar
		local h = workspace:Raycast(b, d * def.alcance, rpC)
		p = h and h.Position or (b + d * def.alcance)
	end
	local pv = m:GetPivot().Position
	if (p - pv).Magnitude > def.alcance then p = pv + (p - pv).Unit * def.alcance end
	local g = chaoAbaixo(p, ignorar, def.alturaChao + 4)
	local noChao = g ~= nil
	local centro = g or p
	FX:FireAllClients({d = m, hab = "Correntes", fase = "aviso", el = el, pos = centro, raio = def.raio, duracao = def.aviso, ar = not noChao})
	task.wait(def.aviso)
	if not m.Parent then return end
	local lista = {}                                                       -- no raio (3D), mais proximos primeiro
	for _, a in ipairs(self:alvosValidos()) do
		local r = raiz(a)
		if r then
			local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) or 0
			local dist = (r.Position - centro).Magnitude
			if noChao then dist = math.min(dist, (plano(r.Position - centro).Magnitude ^ 2 + math.max(0, math.abs(r.Position.Y - centro.Y) - def.alturaChao) ^ 2) ^ 0.5) end
			if dist <= def.raio + extra then table.insert(lista, {a, dist}) end
		end
	end
	table.sort(lista, function(x, y) return x[2] < y[2] end)
	FX:FireAllClients({d = m, hab = "Correntes", fase = "erupcao", el = el, pos = centro, raio = def.raio, ar = not noChao})
	for i = 1, math.min(#lista, def.maxAlvos) do
		local a = lista[i][1]
		self:aplicar({a}, def.dano, "Correntes", def.intensidade, el)         -- acerto inicial: dano + Marca
		local h = a:FindFirstChildOfClass("Humanoid")
		local vivo = (h and h.Health > 0) or (not h and not a:GetAttribute("Incapacitado"))
		if vivo and (resistente[a] or 0) < os.clock() and not presos[a] then
			local r = raiz(a)
			local usaJP = h and h.UseJumpPower
			local p = {ate = os.clock() + def.preso, ws = h and h.WalkSpeed or 0, pulo = h and (usaJP and h.JumpPower or h.JumpHeight) or 0, usaJP = usaJP, fonte = m, t0 = os.clock()}
			presos[a] = p
			-- PATCH_CORRENTES_APERTA (04/11): as correntes apertam aos poucos; o movimento cai ate 0 em def.aperta s
			local ap = def.aperta or 0
			local noAlto = not chaoAbaixo(r.Position, ignorar, def.alturaChao)  -- alvo no ar: segura onde esta
			if h and noAlto then
				p.ancA = Instance.new("Attachment"); p.ancA.Name = "Correntes_Ancora"; p.ancA.Parent = r
				p.segura = Instance.new("AlignPosition"); p.segura.Name = "Correntes_Segura"; p.segura.Mode = Enum.PositionAlignmentMode.OneAttachment
				p.segura.Attachment0 = p.ancA; p.segura.Position = r.Position; p.segura.Responsiveness = 12; p.segura.MaxForce = 0; p.segura.Parent = r
			end
			local function fator() if ap <= 0 then return 0 end; local x = math.clamp((os.clock() - p.t0) / ap, 0, 1); return (1 - x) ^ 2 end
			local function apertar()
				local k = fator()
				if h then
					local ws, pl = p.ws * k, p.pulo * k
					if h.WalkSpeed > ws + 0.01 then h.WalkSpeed = ws end                -- outro script tentou soltar: continua apertando
					if usaJP then if h.JumpPower > pl + 0.01 then h.JumpPower = pl end elseif h.JumpHeight > pl + 0.01 then h.JumpHeight = pl end
					if p.segura then p.segura.MaxForce = (1 - k) * r.AssemblyMass * workspace.Gravity * 6 end
				else
					a:SetAttribute("PresoFator", k)                                   -- IA/montaria freiam por este fator
				end
			end
			apertar()
			if ap > 0 then task.spawn(function() while presos[a] == p and os.clock() - p.t0 < ap + 0.05 do RunService.Heartbeat:Wait(); if presos[a] == p then apertar() end end end) end
			a:SetAttribute("PresoCorrentes", workspace:GetServerTimeNow() + def.preso)
			FX:FireAllClients({d = m, hab = "Correntes", fase = "prender", el = el, alvo = a, duracao = def.preso, aperta = ap, ar = noAlto})
			task.spawn(function()
				while presos[a] == p and os.clock() < p.ate do
					task.wait(def.tick)
					local ok = a.Parent and ((h and h.Health > 0) or (not h and not a:GetAttribute("Incapacitado")))
					if presos[a] ~= p or not ok then break end
					apertar()                                                   -- PATCH_CORRENTES_APERTA (antes: WalkSpeed = 0 direto)
					N.ferir(m, a, def.danoTick, el, "Correntes", "leve", true)  -- tick: usa a Marca, nao marca
				end
				if presos[a] == p then soltarCorrente(a); resistente[a] = os.clock() + def.resistencia end
			end)
		end
	end
	local resto = (noAr and def.duracaoAr or def.duracao) - batida - def.aviso
	if resto > 0 then task.wait(resto) end
end

-- Rajadas de Gelo: 4 lancas, cada uma com a mira do momento do disparo (cursor do cavaleiro, que o cliente segue
-- enviando, ou alvo da IA com antecipacao), dentro do cone do pescoco. Voo simulado no servidor quadro a quadro:
-- segmento percorrido x alvos (hitbox fina) e x mundo (impacto no chao/parede). 1 acerto por lanca.
function N:voarLanca(def, el, de, dir, i)
	local pos, perc = de, 0
	local fm = filtroMundo(self)
	while perc < def.alcance and self.m.Parent do
		local dt = RunService.Heartbeat:Wait()
		local passo = math.min(def.velocidade * dt, def.alcance - perc)
		for _, a in ipairs(self:alvosValidos()) do
			local p = raiz(a).Position
			local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) * 1.4 or 2.2
			local s = math.clamp((p - pos):Dot(dir), 0, passo)
			if (pos + dir * s - p).Magnitude <= def.raio + extra then
				self:aplicar({a}, def.dano, "Rajadas", def.intensidade, el, def.frost)
				FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "impacto", el = el, pos = pos + dir * s, indice = i, acertou = true})
				return
			end
		end
		local h = workspace:Raycast(pos, dir * passo, fm)
		if h then FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "impacto", el = el, pos = h.Position, normal = h.Normal, indice = i, acertou = false}); return end
		pos += dir * passo; perc += passo
	end
	FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "dissipa", el = el, pos = pos, indice = i})
end
function N:_Rajadas(def, el, noAr, op)
	FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "preparo", el = el})
	self.miraDir = nil
	self:tocar(def.clipe, noAr, {}, function() end)
	local t0 = os.clock()
	for i, ts in ipairs(def.disparos) do
		local espera = ts - (os.clock() - t0); if espera > 0 then task.wait(espera) end
		if not self.m.Parent or self.m:GetAttribute("Incapacitado") then return end
		local b = self:boca(); local f = self:frente()
		local dir
		local md = self.miraDir or op.direcao
		if typeof(md) == "Vector3" and md.Magnitude > 0.1 then dir = md.Unit end
		if op.alvo and raiz(op.alvo) then                                      -- IA: mira com antecipacao do movimento
			local r = raiz(op.alvo); local tv = (r.Position - b).Magnitude / def.velocidade
			dir = ((r.Position + r.AssemblyLinearVelocity * tv) - b).Unit
		end
		dir = dir or f
		local pd = plano(dir)
		if pd.Magnitude < 0.1 or pd.Unit:Dot(f) < def.coneMin then dir = (f + Vector3.new(0, math.clamp(dir.Y, -0.5, 0.4), 0)).Unit end
		dir = Vector3.new(dir.X, math.clamp(dir.Y, -0.8, 0.6), dir.Z).Unit
		FX:FireAllClients({d = self.m, hab = "Rajadas", fase = "disparo", el = el, de = b, dir = dir, vel = def.velocidade, alcance = def.alcance, indice = i})
		task.spawn(function() self:voarLanca(def, el, b, dir, i) end)
	end
	local resto = def.duracao - (os.clock() - t0); if resto > 0.1 then task.wait(resto - 0.1) end
	self.miraDir = nil
end

-- Zero Absoluto: descarga em def.emissao; a onda nasce no chao sob o corpo (no ar, se houver chao ate alturaMaxAr;
-- senao na altura do corpo) e se expande a velOnda ate o raio: 1 acerto por alvo quando a frente da onda passa.
-- Depois a zona congelada segue acumulando Frostbite (sem dano) por def.zona segundos.
function N:_ZeroAbsoluto(def, el, noAr, op)
	FX:FireAllClients({d = self.m, hab = "ZeroAbsoluto", fase = "preparo", el = el, noAr = noAr, emissao = def.emissao})
	self:tocar(def.clipe, noAr, {}, function() end)
	task.wait(def.emissao)
	if not self.m.Parent or self.m:GetAttribute("Incapacitado") then return end
	local c = self:centroCorpo()
	local h = workspace:Raycast(c + Vector3.new(0, 5, 0), Vector3.new(0, -(def.alturaMaxAr + 25), 0), filtroMundo(self))
	local centro = h and h.Position or c
	FX:FireAllClients({d = self.m, hab = "ZeroAbsoluto", fase = "onda", el = el, centro = centro, normal = h and h.Normal, noChao = h ~= nil,
		raio = def.raio, vel = def.velOnda, zona = def.zona, zonaRaio = def.zonaRaio})
	local atingidos, r = {}, 0
	while r < def.raio and self.m.Parent do
		local dt = RunService.Heartbeat:Wait()
		r = math.min(def.raio, r + def.velOnda * dt)
		for _, a in ipairs(self:alvosValidos()) do
			if not atingidos[a] then
				local p = raiz(a).Position
				local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) * 1.6 or 2
				if plano(p - centro).Magnitude <= r + extra and math.abs(p.Y - centro.Y) <= def.alturaFaixa + extra then
					atingidos[a] = true
					self:aplicar({a}, def.dano, "ZeroAbsoluto", def.intensidade, el, def.frost)
				end
			end
		end
	end
	if h then
		local m = self.m
		task.spawn(function()
			local fim = os.clock() + def.zona
			while os.clock() < fim and m.Parent do
				task.wait(def.zonaTick)
				for _, a in ipairs(self:alvosValidos()) do
					local p = raiz(a).Position
					if plano(p - centro).Magnitude <= def.zonaRaio and math.abs(p.Y - centro.Y) <= 14 then Passivas.aplicarFrostbite(m, a, def.zonaFrost) end
				end
			end
		end)
	end
	local resto = def.duracao - def.emissao - def.raio / def.velOnda; if resto > 0.05 then task.wait(resto) end
end

-- Nevasca Ancestral (ultimate): o combate move o corpo (CorpoElevado: montaria e IA nao disputam o pivo). Solo: sobe
-- elevacaoSolo e no fim desce de volta; ar: ganha subidaAr e estabiliza. Ondas de fragmentos em def.ondas (1a cheia,
-- seguintes x fatorOnda), esfera em volta do tronco com linha de visao.
function N:_Nevasca(def, el, noAr, op)
	FX:FireAllClients({d = self.m, hab = "Nevasca", fase = "inicio", el = el, noAr = noAr, duracao = def.duracao, rugido = def.rugido,
		ondas = def.ondas, raio = def.raio, subida = def.subida})
	self:tocar(def.clipe, noAr, {}, function() end)
	self.m:SetAttribute("CorpoElevado", true)
	local t0 = os.clock()
	local H = noAr and def.subidaAr or def.elevacaoSolo
	local s0, s1, d0, d1 = def.subida[1], def.subida[2], def.descida[1], def.descida[2]
	local feitas, yAtual = {}, 0
	local function onda(i)
		local c = self:centroCorpo(); local lista = {}
		for _, a in ipairs(self:alvosValidos()) do if naEsfera(c, def.raio, a) and self:visivel(c, a) then table.insert(lista, a) end end
		self:aplicar(lista, def.dano * (i == 1 and 1 or def.fatorOnda), "Nevasca", def.intensidade, el, def.frost)
		FX:FireAllClients({d = self.m, hab = "Nevasca", fase = "onda", el = el, indice = i, pos = c, raio = def.raio})
	end
	while self.m.Parent and not self.m:GetAttribute("Incapacitado") do
		RunService.Heartbeat:Wait()
		local k = os.clock() - t0
		if k >= def.duracao then break end
		local y
		if k < s0 then y = 0
		elseif k < s1 then local x = (k - s0) / (s1 - s0); y = H * (1 - (1 - x) ^ 2)
		elseif noAr or k < d0 then y = H + 0.8 * math.sin((k - s1) * 2.2)
		elseif k < d1 then local x = (k - d0) / (d1 - d0); y = (H + 0.8 * math.sin((d0 - s1) * 2.2)) * (1 - x * x * (3 - 2 * x))
		else y = 0 end
		self.m:PivotTo(self.m:GetPivot() + Vector3.new(0, y - yAtual, 0)); yAtual = y
		for i, to in ipairs(def.ondas) do if not feitas[i] and k >= to then feitas[i] = true; onda(i) end end
	end
	if not noAr and self.m.Parent then self.m:PivotTo(self.m:GetPivot() - Vector3.new(0, yAtual, 0)) end   -- volta ao chao exato
	self.m:SetAttribute("CorpoElevado", nil)
	FX:FireAllClients({d = self.m, hab = "Nevasca", fase = "fim", el = el})
end

-- PATCH_ECLIPSE_DRACONICO (04/11): Eclipse Draconico (Sombrio, slot Coracao, especial). Concentracao (inicio do
-- Hab_Concentracao) -> Rugido_Combate; no pico do rugido a area em volta do corpo escurece (so visual, no cliente) e as
-- Marcas Sombrias PROPRIAS dos alvos na esfera (com linha de visao) DETONAM: o alvo perde todas as marcas deste Sombrio
-- e recebe danoPorMarca x marcas (sem marca = sem dano; a detonacao nao cria marca nova). Sem invisibilidade,
-- invulnerabilidade nem execucao. Contrajogo: sair da area na antecipacao / nao acumular marcas. Numeros NAO_APROVADO.
-- PATCH_ECLIPSE_VOO (04/11, pedido do usuario): o dragao LEVANTA VOO, ruge, SOLTA o poder no ar e segue rugindo
-- pairando enquanto a area dura; quando o poder comeca a cessar, fecha a boca e POUSA. O combate move o corpo
-- (CorpoElevado: montaria e IA nao disputam o pivo, como na Nevasca). No ar: ganha um pouco de altura e paira.
-- Detonacao das Marcas (danoPorMarca x marcas) e dano continuo da area (danoArea por tickArea) iguais; o centro da
-- area e o chao sob o dragao (o corpo esta no alto). Numeros NAO_APROVADO.
function N:_Eclipse(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "inicio", el = el, noAr = noAr, detona = def.detona, raio = def.raio})
	m:SetAttribute("CorpoElevado", true)
	local P = Enum.AnimationPriority
	local function trilha(nome, camada, laco, prio) local t = self:tocar(nome, camada, {}, function() end, laco); if t then t.Priority = prio end; return t end
	local tDec = not noAr and trilha("Decolagem", false, false, P.Action2) or nil
	local tPairar
	task.delay(noAr and 0 or 0.8, function() if m.Parent then tPairar = trilha("Pairar", false, true, P.Action2); if tDec then tDec:Stop(0.3) end end end)
	local tRugido; task.delay(def.rugir or 1.2, function() if m.Parent then tRugido = trilha("Rugido_Combate", true, false, P.Action3) end end)
	local H = noAr and (def.subidaAr or 10) or (def.altura or 24)
	local s0, s1 = noAr and 0 or 0.2, noAr and 1.0 or 1.5
	local yAtual = 0
	local function subir(k)                                           -- altura do corpo no instante k (decola, paira, pousa)
		local y
		if k < s0 then y = 0 elseif k < s1 then local x = (k - s0) / (s1 - s0); y = H * (1 - (1 - x) ^ 2) else y = H + 0.9 * math.sin((k - s1) * 2.0) end
		return y
	end
	local t0 = os.clock(); local morto = false
	local con = RunService.Heartbeat:Connect(function()
		if not m.Parent then return end
		local y = subir(os.clock() - t0)
		m:PivotTo(m:GetPivot() + Vector3.new(0, y - yAtual, 0)); yAtual = y
	end)
	local function encerrar()                                         -- desce e pousa (no chao) ou estabiliza (no ar)
		con:Disconnect()
		if m.Parent and not noAr then
			local y0 = yAtual; local d0 = os.clock(); local desce = def.descida or 1.1; local pousou = false
			while m.Parent and os.clock() - d0 < desce do
				RunService.Heartbeat:Wait()
				local x = math.min(1, (os.clock() - d0) / desce); local y = y0 * (1 - x * x * (3 - 2 * x))
				m:PivotTo(m:GetPivot() + Vector3.new(0, y - yAtual, 0)); yAtual = y
				if not pousou and x > 0.55 then pousou = true; local tp = trilha("Pouso", false, false, P.Action2); if tPairar then tPairar:Stop(0.25) end; if tp then task.delay(0.5, function() tp:Stop(0.3) end) end end
			end
			if m.Parent then m:PivotTo(m:GetPivot() - Vector3.new(0, yAtual, 0)); yAtual = 0 end   -- volta ao chao exato
		end
		if tPairar then tPairar:Stop(0.3) end
		m:SetAttribute("CorpoElevado", nil)
	end
	task.wait(def.detona)
	if not m.Parent or m:GetAttribute("Incapacitado") then FX:FireAllClients({d = m, hab = "Eclipse", fase = "fimRugido", el = el}); encerrar(); return end
	-- PATCH_CORRENTES_AR / ECLIPSE no ar: com chao ate pertoChao abaixo -> area no chao; senao, em volta do corpo no ar
	local cc = self:centroCorpo(); local vfxF = workspace:FindFirstChild("VFX_Temporarios")
	local gE = chaoAbaixo(cc - Vector3.new(0, yAtual, 0), {m, vfxF}, def.pertoChao or 40)
	local c = gE and (gE + Vector3.new(0, 3, 0)) or cc
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "detonar", el = el, pos = c, raio = def.raio, duracao = def.escuro, ar = gE == nil})
	local mult = ((m:GetAttribute("DominioAtivo") and Cfg.habilidades.Dominio.multiplicadorDano) or 1) * Passivas.multiplicadorOfensivo(m)
	local total, nAlvos = 0, 0
	for _, a in ipairs(self:alvosValidos()) do
		if naEsfera(c, def.raio, a) and self:visivel(c, a) then
			local n = Passivas.consumirMarcas(m, a)                         -- zera ANTES do dano: o multiplicador da Marca nao soma
			if n > 0 and N.ferir(m, a, def.danoPorMarca * n * mult, el, "Eclipse", def.intensidade, true) then   -- como tick: nao marca de novo
				FX:FireAllClients({d = m, fase = "reacao", alvo = a, intensidade = def.intensidade, el = el, tipo = "Eclipse"})
				FX:FireAllClients({d = m, hab = "Eclipse", fase = "marca", el = el, alvo = a, marcas = n})
				total += n; nAlvos += 1
			end
		end
	end
	m:SetAttribute("UltimoEclipse", ("alvos=%d marcas=%d raio=%d"):format(nAlvos, total, def.raio))
	-- rugido sustentado (laco aereo com a boca aberta) e dano continuo na area enquanto ela existe
	local tLaco
	task.delay(0.45, function() if m.Parent then tLaco = trilha(def.clipeLoop, true, true, P.Action3); if tLaco and tRugido then tRugido:Stop(0.3) end end end)
	local ta, ticks, feridos = os.clock(), 0, {}
	while os.clock() - ta < def.escuro do
		task.wait(def.tickArea)
		if not m.Parent or m:GetAttribute("Incapacitado") then morto = true; break end   -- dragao derrubado: a area acaba
		ticks += 1
		for _, a in ipairs(self:alvosValidos()) do
			if naEsfera(c, def.raio, a) and self:visivel(c, a) and N.ferir(m, a, def.danoArea * mult, el, "Eclipse", "leve", true) then
				FX:FireAllClients({d = m, fase = "reacao", alvo = a, intensidade = "leve", el = el, tipo = "EclipseArea"})
				feridos[a.Name] = (feridos[a.Name] or 0) + 1
			end
		end
	end
	local fr = {}; for n, k in pairs(feridos) do table.insert(fr, n .. "=" .. k) end
	m:SetAttribute("UltimoEclipseArea", ("ticks=%d %s"):format(ticks, table.concat(fr, " ")))
	-- o poder comeca a cessar: fecha a boca e pousa
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "fimRugido", el = el})
	if m.Parent and not morto then
		local tFim = trilha(def.clipeFim, true, false, P.Action3)
		if tLaco then tLaco:Stop(0.25) end; if tRugido then tRugido:Stop(0.25) end
		if tFim then task.delay(def.fimRugido, function() tFim:Stop(0.3) end) end
	end
	encerrar()
end

-- energia
task.spawn(function()
	while true do
		local dt = task.wait(0.5)
		for m, s in pairs(N.registro) do
			if s.energia < Cfg.energiaMax then s.energia = math.min(Cfg.energiaMax, s.energia + Cfg.energiaRegen * dt); m:SetAttribute("Energia", math.floor(s.energia)) end
		end
	end
end)
Passivas.ligar(N)
return N
