-- patch_ia_derrota_ar.luau (Studio, modo Edit) — DECISAO DO USUARIO (30/10): "Ele pode ser derrotado, lutar tanto no ar
-- quanto na terra". Tudo-ou-nada; originais em ServerStorage.Backup_IA_DerrotaAr. Valores EXPERIMENTAIS (NAO_APROVADO).
--  Vida/derrota: guardiao tem Vida/VidaMax; so dragoes de JOGADOR o ferem (Nucleo e Mordida Aerea da montaria; zona
--    segura vale); em 0 -> Incapacitado (a IA pousa se estiver no ar e deita; o ninho fica sem defesa); recupera apos
--    tempoRecuperacao com 50% da vida; regenera fora de combate; barra de vida so em combate. Sem recompensa/loot (nao ha
--    regra aprovada).
--  Combate aereo: alvo voando (ex.: jogador montado) -> o guardiao decola, persegue no ar mantendo distancia de ataque
--    e ataca no ar (o Combate ja escolhe Mordida aerea / Sopro / Arremetida / Tempestade aerea quando NoAr); alvo no
--    chao -> pousa e luta em terra (como antes).
local SSS, SS = game:GetService("ServerScriptService"), game:GetService("ServerStorage")
local alvos = {Cerebro = SSS.IA_Dragao.Cerebro, Config = SSS.IA_Dragao.Config, Locomotor = SSS.IA_Dragao.Locomotor,
	Nucleo = SSS.Combate_Dragao.Nucleo, Montaria = SSS.Montaria_Dragao_Servidor}
if alvos.Cerebro.Source:find("PATCH_IA_DERROTA_AR", 1, true) then return "ja aplicado" end
local novo = {}; for k, s in pairs(alvos) do novo[k] = s.Source end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true); assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end

-- ============================================================== Config
troca("Config", [=[distEntreDragoes = 90,]=], [=[distEntreDragoes = 90,
	-- DERROTAVEL (usuario 30/10): vida, recuperacao apos derrota, regeneracao fora de combate (sem dano ha regenApos s)
	vidaGuardiao = 600, tempoRecuperacao = 120, regenVida = 2, regenApos = 20,
	-- combate aereo: alvo a mais de alturaAlvoNoAr acima do chao = voando; distancia mantida na perseguicao
	alturaAlvoNoAr = 22, distCombateAr = 38,]=])

-- ============================================================== Nucleo
troca("Nucleo", [=[N.emZonaSegura = emZonaSegura]=], [=[N.emZonaSegura = emZonaSegura
-- PATCH_IA_DERROTA_AR: guardiao selvagem DERROTAVEL (decisao do usuario 30/10). Vida em atributos; so dragao de JOGADOR
-- fere; em 0 -> Incapacitado (o Cerebro pousa/deita e recupera). Valores experimentais (Config da IA).
function N.danoGuardiao(g, dano, atacante)
	if not (g and g.Parent and g:GetAttribute("GuardiaoNinho")) or g:GetAttribute("Incapacitado") or not dano or dano <= 0 then return false end
	if not (atacante and atacante:GetAttribute("DonoUserId")) then return false end
	if g.PrimaryPart and emZonaSegura(g.PrimaryPart.Position) then return false end
	local max = g:GetAttribute("VidaMax") or 600
	local v = math.max(0, (g:GetAttribute("Vida") or max) - dano)
	g:SetAttribute("Vida", v); g:SetAttribute("UltimoDano", workspace:GetServerTimeNow())
	local plr = Players:GetPlayerByUserId(atacante:GetAttribute("DonoUserId"))
	local ev = game:GetService("ServerStorage"):FindFirstChild("IA_Eventos")
	if ev and ev:FindFirstChild("GuardiaoAtacado") then ev.GuardiaoAtacado:Fire(g, (plr and plr.Character) or atacante) end
	if v <= 0 then g:SetAttribute("Incapacitado", true); g:SetAttribute("Derrotado", workspace:GetServerTimeNow()) end
	return true
end]=])
troca("Nucleo", [=[local dono = self.m:GetAttribute("DonoUserId")]=], [=[local dono = self.m:GetAttribute("DonoUserId")
	-- dragao de JOGADOR tambem mira guardioes selvagens (derrotaveis; zona segura vale; derrotado nao e alvo)
	if dono then
		for _, g in ipairs(workspace:GetChildren()) do
			if g ~= self.m and g:IsA("Model") and g:GetAttribute("GuardiaoNinho") and not g:GetAttribute("Incapacitado") and g.PrimaryPart
				and not emZonaSegura(g.PrimaryPart.Position) then table.insert(l, g) end
		end
	end]=])
troca("Nucleo", [=[if h and h.Health > 0 and dano > 0 then]=], [=[if not h and a:GetAttribute("GuardiaoNinho") then
			if N.danoGuardiao(a, dano * mult, self.m) then n += 1 end
		elseif h and h.Health > 0 and dano > 0 then]=])
troca("Nucleo", [=[local function naEsfera(c, r, alvo) return (raiz(alvo).Position - c).Magnitude <= r end]=],
	[=[-- alvo grande (guardiao): soma o raio do corpo (o centro do dragao fica longe da superficie atingida)
local function naEsfera(c, r, alvo)
	local extra = alvo:GetAttribute("GuardiaoNinho") and (alvo:GetAttribute("CorpoRaio") or 8) * 1.6 or 0
	return (raiz(alvo).Position - c).Magnitude <= r + extra
end]=])

-- ============================================================== Montaria (Mordida Aerea do jogador fere o guardiao)
troca("Montaria", [=[if hum and hum.Health > 0 and not M.mordida.atingidos[alvo] and not Players:GetPlayerFromCharacter(alvo) then]=],
	[=[if alvo and alvo:GetAttribute("GuardiaoNinho") and not hum then
			if not M.mordida.atingidos[alvo] then
				M.mordida.atingidos[alvo] = true
				local okN, Nc = pcall(require, game:GetService("ServerScriptService").Combate_Dragao.Nucleo)
				if okN and Nc.danoGuardiao(alvo, MA.dano, m) then
					m:SetAttribute("MordidaAcertou", workspace:GetServerTimeNow()); M.vel *= MA.freioImpacto
				end
			end
		elseif hum and hum.Health > 0 and not M.mordida.atingidos[alvo] and not Players:GetPlayerFromCharacter(alvo) then]=])

-- ============================================================== Locomotor
troca("Locomotor", [=[for _, m in ipairs(game:GetService("CollectionService"):GetTagged("Invasor_Teste")) do table.insert(lista, m) end]=],
	[=[for _, m in ipairs(game:GetService("CollectionService"):GetTagged("Invasor_Teste")) do table.insert(lista, m) end
	-- outros dragoes nao sao "terreno" (chao/parede/obstaculo de voo); a convivencia cuida da distancia entre eles
	for _, d in ipairs(workspace:GetChildren()) do if d ~= self.m and d:IsA("Model") and d:GetAttribute("FormaRegional") then table.insert(lista, d) end end]=])
troca("Locomotor", [=[-- melhor meio para chegar:]=], [=[-- COMBATE AEREO (30/10): persegue um alvo no ar mantendo 'distIdeal' (plano) e a altura dele (nunca abaixo da folga
-- sobre o relevo); paira quando esta na distancia; obstaculo a frente -> sobe em vez de avancar. Roda enquanto vivo().
function L:perseguirAr(alvoPos, vivo, distIdeal)
	local cfg = self.cfg
	if not self.noAr then local ok, m = self:decolar(vivo); if not ok then return false, m end end
	while vivo() do
		local dt = RunService.Heartbeat:Wait()
		local alvo = alvoPos(); if not alvo then return false, "sem alvo" end
		local p = self:pos(); local d = plano(alvo - p); local dist = d.Magnitude
		local erro = dist > 1 and self:_girarPara(d.Unit, cfg.giroVoo * 1.4, dt) or 0
		local f = self:frente()
		local g = self:chaoEm(p) or (p.Y - 200)
		local alvoY = math.max(alvo.Y + 4, g + self.alturaPivo + cfg.folgaVoo * 0.6)
		local dy = math.clamp(alvoY - p.Y, -cfg.vSubida * dt, cfg.vSubida * dt)
		local avanco = 0
		if dist > distIdeal + 10 then avanco = math.min(cfg.vooVel * dt, dist - distIdeal)
		elseif dist < distIdeal - 12 then avanco = -cfg.vooVel * 0.4 * dt end
		if avanco > 0 and workspace:Spherecast(p + Vector3.new(0, 20, 0), 22, f * 60, self.params) then avanco = 0; dy = cfg.vSubida * dt end
		if math.abs(avanco) < 1e-3 and math.abs(dy) < cfg.vSubida * dt * 0.5 then self:clipe("Pairar", true)
		elseif erro > math.rad(35) then self:clipe(difAng(self.psi, yawDe(d) - yawDe(self.f0)) > 0 and "Curva_Aerea_E" or "Curva_Aerea_D", true)
		elseif dy > cfg.vSubida * dt * 0.6 then self:clipe("Subida", true)
		elseif dy < -cfg.vSubida * dt * 0.6 then self:clipe("Descida", true)
		else self:clipe("Voo", true) end
		self.pitch = 0
		self:_aplicar(Vector3.new(p.X, p.Y + dy, p.Z) + f * avanco)
	end
	return true
end

-- melhor meio para chegar:]=])

-- ============================================================== Cerebro
troca("Cerebro", [=[local function zonaSegura(pos)]=], [=[-- PATCH_IA_DERROTA_AR: derrotavel (Vida/Incapacitado) e combate no ar (decisao do usuario 30/10)
local function zonaSegura(pos)]=])
troca("Cerebro", [=[self.cxAlerta = self.T.Alerta.Event:Connect(]=], [=[if not modelo:GetAttribute("VidaMax") then modelo:SetAttribute("VidaMax", self.cfg.vidaGuardiao) end
	modelo:SetAttribute("Vida", modelo:GetAttribute("VidaMax")); modelo:SetAttribute("Incapacitado", nil)
	self.cxAlerta = self.T.Alerta.Event:Connect(]=])
troca("Cerebro", [=[if self.estado ~= "Sleep" then self.sono = math.min(1, self.sono + self.cfg.sonoTaxa * dt) end]=],
	[=[if self.estado ~= "Sleep" then self.sono = math.min(1, self.sono + self.cfg.sonoTaxa * dt) end
		-- vida: regenera fora de combate; a barra so aparece em combate/derrotado
		local vmax, vida = self.m:GetAttribute("VidaMax"), self.m:GetAttribute("Vida")
		local ud = self.m:GetAttribute("UltimoDano")
		if vmax and vida and vida < vmax and not self.m:GetAttribute("Incapacitado") and (not ud or workspace:GetServerTimeNow() - ud > self.cfg.regenApos) then
			self.m:SetAttribute("Vida", math.min(vmax, vida + self.cfg.regenVida * dt))
		end
		self:barraVida()]=])
troca("Cerebro", [=[function C:_Investigate(vivo)]=], [=[function C:barraVida()
	local b = self.barra
	if not b then
		b = Instance.new("BillboardGui"); b.Name = "BarraVida"; b.Size = UDim2.fromOffset(170, 12); b.StudsOffset = Vector3.new(0, 26, 0)
		b.MaxDistance = 320; b.Enabled = false
		local fundo = Instance.new("Frame"); fundo.Name = "Fundo"; fundo.Size = UDim2.fromScale(1, 1); fundo.BorderSizePixel = 0
		fundo.BackgroundColor3 = Color3.fromRGB(25, 20, 20); fundo.BackgroundTransparency = 0.2; fundo.Parent = b
		local v = Instance.new("Frame"); v.Name = "V"; v.Size = UDim2.fromScale(1, 1); v.BorderSizePixel = 0; v.BackgroundColor3 = Color3.fromRGB(185, 45, 35); v.Parent = fundo
		b.Adornee = self.m.PrimaryPart; b.Parent = self.m.PrimaryPart; self.barra = b
	end
	local max = self.m:GetAttribute("VidaMax") or 1; local v = self.m:GetAttribute("Vida") or max
	local ud = self.m:GetAttribute("UltimoDano")
	b.Enabled = (ud ~= nil and workspace:GetServerTimeNow() - ud < 20) or self.m:GetAttribute("Incapacitado") == true
	b.Fundo.V.Size = UDim2.fromScale(math.clamp(v / max, 0, 1), 1)
end
function C:alvoNoAr(alvo)
	local r = raizDe(alvo); if not r then return false end
	local g = self.L:chaoEm(r.Position)
	return g ~= nil and r.Position.Y - g > self.cfg.alturaAlvoNoAr
end
function C:_Investigate(vivo)]=])
troca("Cerebro", [=[while vivo() and self.m:GetAttribute("Incapacitado") do task.wait(0.5) end]=],
	[=[self.ameacas = {}                                                  -- derrotado: esquece o confronto
	local fimInc = os.clock() + self.cfg.tempoRecuperacao
	while vivo() and self.m:GetAttribute("Incapacitado") and os.clock() < fimInc do task.wait(0.5) end
	if vivo() and self.m:GetAttribute("Incapacitado") then              -- recupera sozinho (metade da vida)
		self.m:SetAttribute("Incapacitado", nil); self.m:SetAttribute("Vida", math.floor((self.m:GetAttribute("VidaMax") or 600) * 0.5))
		self:registrar("recuperado da derrota")
	end]=])
troca("Cerebro", [=[if self.m:GetAttribute("EmAtaque") then task.wait(0.1); continue end      -- golpe em curso: nao interrompe nem desliza]=],
	[=[if self.m:GetAttribute("EmAtaque") then
			if self.L.noAr and self.m:GetAttribute("EmAtaque") ~= "Arremetida" then self.L:clipe("Pairar", true) end   -- golpe no ar: paira
			task.wait(0.1); continue
		end]=])
troca("Cerebro", [=[local dDN = plano(self.L:pos() - self.casa).Magnitude]=], [=[local dDN = plano(self.L:pos() - self.casa).Magnitude
		-- COMBATE AEREO: alvo voando -> persegue no ar e ataca no ar; alvo no chao -> segue a defesa em terra (abaixo)
		if self:alvoNoAr(alvo) and (self.L.noAr or self.L:ceuLivre()) then
			local lim = a.pessoal and self.cfg.territorio or self.cfg.perseguicaoMax
			if dIN > lim + 60 or zonaSegura(pI) then self.ameacas[alvo] = nil; self:registrar("combate aereo interrompido (limite)"); break end
			self:definir("AirCombat")
			local t0 = os.clock()
			self.L:perseguirAr(function() local rr = raizDe(alvo); return rr and rr.Position end,
				function() return vivo() and os.clock() - t0 < 0.5 and not self.m:GetAttribute("EmAtaque") end, self.cfg.distCombateAr)
			if vivo() and self:podeAtacar(alvo) and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then
				ultimoAtaque = os.clock(); self:definir("Attack"); Territorio.Eventos.AtaqueSolicitado:Fire(self.m, alvo)
			end
			task.wait(); continue
		end]=])
troca("Cerebro", [=[self:definir("DefendNest")]=], [=[if self.L.noAr then self.L:pousar(vivo, true) end            -- alvo voltou ao chao: pousa para lutar em terra
			self:definir("DefendNest")]=])

for k in pairs(alvos) do assert(loadstring(novo[k]), k .. " nao compila") end
local bk = SS:FindFirstChild("Backup_IA_DerrotaAr")
if not bk then
	bk = Instance.new("Folder"); bk.Name = "Backup_IA_DerrotaAr"
	for k, s in pairs(alvos) do local c = s:Clone(); c.Name = k .. "__" .. s.Name; if c:IsA("BaseScript") then c.Enabled = false end; c.Parent = bk end
	bk.Parent = SS
end
for k, s in pairs(alvos) do s.Source = novo[k] end
return "aplicado"
