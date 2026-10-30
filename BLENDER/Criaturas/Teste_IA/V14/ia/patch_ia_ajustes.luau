-- patch_ia_ajustes.luau (Studio, modo Edit) — correcoes achadas nos testes em Play da IA selvagem (30/10).
--  1) jogador parado perto do lago: alerta no ar mandava o dragao voltar ao ninho, a ameaca expirava pela distancia
--     e ele voltava para "investigar" o mesmo jogador (decola/pousa em ciclo). Agora: alerta pessoal no ar POUSA ali;
--     investigar so quando o alvo sumiu de vista; quem fica parado perto sem avancar e "habituado" (25 s de alerta,
--     depois 90 s sem novo alerta, a menos que chegue muito perto).
--  2) invasor 60 studs abaixo na encosta: escolhia garra (sem alcance) e o sopro nao tinha visao. Agora: corpo a corpo
--     so no mesmo nivel; sem visao, o guardiao avanca no ninho ate a borda para enxergar (dentro da zona critica).
--  3) giro no lugar levava ~8 s para 180 graus (calibracao V14): 40 graus/s. Ameaca com rugido 1x por confronto; depois
--     postura de combate (Preparar_Combate) sem repetir a entrada.
local SSS, SS = game:GetService("ServerScriptService"), game:GetService("ServerStorage")
local alvos = {Cerebro = SSS.IA_Dragao.Cerebro, Config = SSS.IA_Dragao.Config, CombServ = SSS.Combate_Dragao_Servidor}
if alvos.Cerebro.Source:find("PATCH_IA_AJUSTES", 1, true) then return "ja aplicado" end
local novo = {}; for k, s in pairs(alvos) do novo[k] = s.Source end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true); assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end

-- Config
troca("Config", [=[giroParado = 22,]=], [=[giroParado = 40,]=])

-- Cerebro
troca("Cerebro", [=[local function zonaSegura(pos)]=], [=[-- PATCH_IA_AJUSTES: postura de combate sem entrada (o rugido de ameaca fica so na 1a vez do confronto)
EstadosDragao.ESTADOS.PosturaCombate = EstadosDragao.ESTADOS.PosturaCombate or {postura = "pe", loop = {"Preparar_Combate"}}
local function zonaSegura(pos)]=])
troca("Cerebro", [=[if motivo == "coletou" or motivo == "ataque" or motivo == "invasao" then a.persegue = true end]=],
	[=[a.inicio = a.inicio or os.clock()
	if motivo == "coletou" or motivo == "ataque" or motivo == "invasao" then a.persegue = true end]=])
troca("Cerebro", [=[if dD <= cfg.espacoPessoal and not zonaSegura(r.Position) then]=],
	[=[local hab = self.habituado and self.habituado[alvo]
		local habituado = hab and agora - hab < 90 and dD > cfg.espacoCritico and not self.ameacas[alvo]
		if dD <= cfg.espacoPessoal and not habituado and not zonaSegura(r.Position) then]=])
troca("Cerebro", [=[if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) or (r and zonaSegura(r.Position)) then]=],
	[=[local cansou = a.motivo == "proximo" and a.nivel < 2 and agora - (a.inicio or agora) > 25     -- parado perto sem avancar
		if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) or (r and zonaSegura(r.Position)) or cansou then
			if a.motivo == "proximo" then self.habituado = self.habituado or {}; self.habituado[alvo] = agora end]=])
troca("Cerebro", [=[if a.nivel < 2 and a.ultimaPos and r and alvo.Parent then self.investigar = {pos = a.ultimaPos, t = agora} end]=],
	[=[if a.nivel < 2 and a.ultimaPos and r and alvo.Parent and not cansou and plano(r.Position - self.L:pos()).Magnitude > cfg.observarDist then
				self.investigar = {pos = a.ultimaPos, t = agora}                -- so se o alvo sumiu de vista
			end]=])
troca("Cerebro", [=[if self.L.noAr then self:irAoNinho(false, vivo, 60); return end]=],
	[=[if self.L.noAr then
		if a.pessoal then self.L:pousar(vivo)                              -- alerta pessoal: pousa ali e encara
		else self:irAoNinho(false, vivo, 60); return end
	end]=])
troca("Cerebro", [=[if d <= self.cfg.distAtaque then return true end]=],
	[=[local dy = math.abs(r.Position.Y - (self.L:pos().Y - self.L.alturaPivo))
	if d <= self.cfg.distAtaque and dy < 25 then return true end           -- perto e no mesmo nivel]=])
troca("Cerebro", [=[local dir = plano(pI - self.casa); dir = dir.Magnitude > 1 and dir.Unit or self.L:frente()]=],
	[=[local dir = plano(pI - self.casa); dir = dir.Magnitude > 1 and dir.Unit or self.L:frente()
			local cabP = self.m.PrimaryPart:FindFirstChild("Cabeca", true).WorldPosition
			local semVisao = workspace:Raycast(cabP, pI - cabP, self.L.params) ~= nil]=])
troca("Cerebro", [=[or (self.casa + dir * self.cfg.distGuarda)]=], [=[or (self.casa + dir * self.cfg.distGuarda)
			-- sem visao (invasor na encosta/atras da borda): avanca ate a borda para enxergar, sem sair da zona critica
			if semVisao and dIN > self.cfg.distGuarda + 12 then guarda = self.casa + dir * math.min(dIN - 18, self.cfg.critica) end]=])
troca("Cerebro", [=[else self:comportamento("AmeacaNinho", 1.0, vivo) end]=], [=[else self:comportamento("PosturaCombate", 1.0, vivo) end]=])

-- Combate: corpo a corpo so no mesmo nivel
troca("CombServ", [=[local acima = r.Position.Y - p.Y]=], [=[local acima = r.Position.Y - p.Y
	local pePos = c.peE and c.peE.TransformedWorldCFrame.Position.Y or (p.Y - 10)
	local dyPe = r.Position.Y - pePos; local mesmoNivel = dyPe > -12 and dyPe < 20       -- garras/cauda/ruptura: alvo no chao do dragao]=])
troca("CombServ", [=[elseif d < 45 and not noAr then add(atras and "Cauda" or "Garra", 0.95) end]=],
	[=[elseif d < 45 and not noAr and mesmoNivel then add(atras and "Cauda" or "Garra", 0.95)
	elseif d < 45 then table.insert(bloqueio, "corpo a corpo: desnivel") end]=])
troca("CombServ", [=[if atras and d < 62 then add("Cauda", 1.0) end]=], [=[if atras and d < 62 and mesmoNivel then add("Cauda", 1.0) end]=])
troca("CombServ", [=[if not noAr and d > 10 and d < R.aneis[#R.aneis] + 4 and not atras and os.clock()]=],
	[=[if not noAr and mesmoNivel and d > 10 and d < R.aneis[#R.aneis] + 4 and not atras and os.clock()]=])

for k in pairs(alvos) do assert(loadstring(novo[k]), k .. " nao compila") end
local bk = SS:FindFirstChild("Backup_IA_Ajustes")
if not bk then
	bk = Instance.new("Folder"); bk.Name = "Backup_IA_Ajustes"
	for k, s in pairs(alvos) do local c = s:Clone(); c.Name = k .. "__" .. s.Name; if c:IsA("BaseScript") then c.Enabled = false end; c.Parent = bk end
	bk.Parent = SS
end
for k, s in pairs(alvos) do s.Source = novo[k] end
return "aplicado"
