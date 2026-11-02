-- patch_sopro_em_movimento.luau (Studio, modo Edit) — usuario 02/11: "ao usar poderes continuos andando, ele anda
-- parado em vez de mexer as pernas". Causa: os clipes do sopro (Inicio/Loop/Fim, solo e ar) controlam o CORPO INTEIRO
-- com prioridade Action e cobrem o Andar/Correr (solo) e o misturador de voo (ar) que a montaria continua tocando.
-- Correcao:
--  1) versoes "_Sup" (parte superior) dos clipes de sopro: copia do clipe com Pose.Weight = 0 em todo osso que nao e
--     pescoco/cabeca/mandibula/focinho (conferido no motor: patas, asas, cauda e quadril ficam 100% com a locomocao);
--     Glacial (Sopro_Glacial_*) e Dragao das Montanhas (Sopro_*), solo e _Camada (ar);
--  2) Nucleo._Sopro: enquanto o dragao se move (atributo Velocidade > 3) toca a versao _Sup; parado, a versao completa
--     (postura firme). Troca com fade no meio do sopro se o jogador comecar/parar de andar.
-- Reversivel: apagar os *_Sup (o Nucleo cai no clipe completo) e o backup em ServerStorage.Backup_Sopro_Movimento_2026-11-02.
local RS, SS, SSS = game:GetService("ReplicatedStorage"), game:GetService("ServerStorage"), game:GetService("ServerScriptService")
local SUP = {Pescoco2 = true, spine_3 = true, Pescoco4 = true, Cabeca = true, Mandibula = true, mouth_upper = true, mouth_upper_tip = true, mouth_lower_tip = true}
local criados = 0
local function parcial(pasta, nome)
	local k = pasta:FindFirstChild(nome); if not k then return end
	local velho = pasta:FindFirstChild(nome .. "_Sup"); if velho then velho:Destroy() end
	local c = k:Clone(); c.Name = nome:gsub("_Camada$", "") .. "_Sup" .. (nome:find("_Camada$") and "_Camada" or "")
	for _, p in ipairs(c:GetDescendants()) do if p:IsA("Pose") and not SUP[p.Name] then p.Weight = 0 end end
	c:SetAttribute("Parcial", "pescoco/cabeca/mandibula (Pose.Weight 0 no resto)")
	local ant = pasta:FindFirstChild(c.Name); if ant then ant:Destroy() end
	c.Parent = pasta; criados += 1
end
for _, par in ipairs({{RS.Animacoes_Glacial, "Glacial_Sopro_Glacial_"}, {RS.Animacoes_Silverwing, "Silverwing_Sopro_"}}) do
	for _, f in ipairs({"Inicio", "Loop", "Fim"}) do parcial(par[1], par[2] .. f); parcial(par[1], par[2] .. f .. "_Camada") end
end

local alvos = {NU = SSS.Combate_Dragao.Nucleo, MS = SSS.Montaria_Dragao_Servidor}
if alvos.NU.Source:find("PATCH_SOPRO_MOVIMENTO", 1, true) then return "clipes _Sup: " .. criados .. " | Nucleo ja aplicado" end
local novo = {}; for k, s in pairs(alvos) do novo[k] = s.Source:gsub("\r\n", "\n") end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true); assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end
troca("NU", [=[	local px = def.clipes or "Sopro"
	local t0 = self:tocar(px .. "_Inicio", noAr, {Emissao = 1.05}, function() end)
	task.wait(1.05)
	local loop = self:clipe(px .. "_Loop", noAr); if loop then loop.Looped = true; loop:Play(0.1) end]=], [=[	local px = def.clipes or "Sopro"
	-- PATCH_SOPRO_MOVIMENTO (02/11): andando/voando, so pescoco/cabeca/mandibula (_Sup); as patas e asas seguem a locomocao
	local function movendo() return (self.m:GetAttribute("Velocidade") or 0) > 3 end
	local function escolher(nome) return (movendo() and self:clipe(nome .. "_Sup", noAr)) and (nome .. "_Sup") or nome end
	local t0 = self:tocar(escolher(px .. "_Inicio"), noAr, {Emissao = 1.05}, function() end)
	task.wait(1.05)
	local loopMov = movendo()
	local loop = self:clipe(escolher(px .. "_Loop"), noAr); if loop then loop.Looped = true; loop:Play(0.1) end]=])
troca("NU", [=[			if not self.m.Parent or self.m:GetAttribute("Incapacitado") then break end   -- removido/incapacitado: encerra ja]=],
	[=[			if not self.m.Parent or self.m:GetAttribute("Incapacitado") then break end   -- removido/incapacitado: encerra ja
			if movendo() ~= loopMov then                                  -- comecou/parou de andar no meio do sopro: troca com fade
				loopMov = movendo()
				local novoLoop = self:clipe(escolher(px .. "_Loop"), noAr)
				if novoLoop and novoLoop ~= loop then
					novoLoop.Looped = true; novoLoop:Play(0.25); if loop then loop:Stop(0.25) end; loop = novoLoop
				end
			end]=])
troca("NU", [=[	local tf = self:tocar(px .. "_Fim", noAr, {}, function() end); task.wait(0.8)]=],
	[=[	local tf = self:tocar(escolher(px .. "_Fim"), noAr, {}, function() end); task.wait(0.8)]=])
troca("MS", [=[	aplicar(M, Vector3.new(np.X, g + L.alturaPivo, np.Z))
	-- ataque que deixa andar]=], [=[	aplicar(M, Vector3.new(np.X, g + L.alturaPivo, np.Z))
	if math.floor(math.abs(M.vel)) ~= m:GetAttribute("Velocidade") then m:SetAttribute("Velocidade", math.floor(math.abs(M.vel))) end   -- PATCH_SOPRO_MOVIMENTO
	-- ataque que deixa andar]=])
for k in pairs(alvos) do local f, e = loadstring(novo[k]); assert(f, k .. " nao compila: " .. tostring(e)) end
local bk = SS:FindFirstChild("Backup_Sopro_Movimento_2026-11-02")
if not bk then
	bk = Instance.new("Folder"); bk.Name = "Backup_Sopro_Movimento_2026-11-02"
	for k, s in pairs(alvos) do local c = s:Clone(); c.Name = k .. "__" .. s.Name; c.Parent = bk end
	bk.Parent = SS
end
for k, s in pairs(alvos) do s.Source = novo[k] end
return "clipes _Sup: " .. criados .. " | Nucleo aplicado"
