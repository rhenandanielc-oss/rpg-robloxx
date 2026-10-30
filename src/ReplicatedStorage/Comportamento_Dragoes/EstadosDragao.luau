-- EstadosDragao (ModuleScript) — estados de comportamento NATURAL do Dragao das Montanhas (sem IA, sem combate).
-- So decide QUAL animacao toca e COMO trocar: entrada -> laco, com fades; impede trocas incompativeis inserindo a
-- transicao certa (ex.: deitado -> andar passa por "levantar"). A IA (o que fazer e quando) fica para outra etapa.
-- Uso:  local E = require(EstadosDragao); local d = E.novo(modelo); d:Mudar("Sono"); d:Estado(); d.Mudou:Connect(fn)
local M = {}
M.__index = M

-- postura: "pe" | "deitado" | "abaixado" | "sentado" ; loop pode ser lista (variacoes sorteadas para evitar repeticao)
M.ESTADOS = {
	Idle        = {postura = "pe", loop = {"Idle_Neutro", "Idle_Neutro", "Observar"}},
	Observacao  = {postura = "pe", entrada = "Observar_Farejar", loop = {"Observar", "Idle_Neutro"}},
	Alerta      = {postura = "pe", entrada = "Reagir_Estimulo", loop = {"Idle_Alerta_Mantido"}},
	Alimentacao = {postura = "pe", entrada = "Comer", depois = "Idle"},
	Mastigando  = {postura = "pe", loop = {"Comer_Mastigar"}},                -- refeicao longa (IA decide quando parar)
	BeberAgua   = {postura = "pe", entrada = "Beber", depois = "Idle"},
	BebendoLongo = {postura = "pe", loop = {"Beber_Loop"}},
	Descanso    = {postura = "deitado", entrada = "Deitar", loop = {"Deitado_Acordado"}},
	Sono        = {postura = "deitado", entrada = "Adormecer", loop = {"Dormir"}},
	Despertar   = {postura = "pe", entrada = "Acordar", depois = "Idle", saida_de = "deitado"},
	Espreguicar = {postura = "pe", entrada = "Espreguicar", depois = "Idle"},
	ProtecaoNinho = {postura = "deitado", entrada = "Ninho_Acomodar", loop = {"Ninho_Repouso"}},
	InspecaoNinho = {postura = "pe", entrada = "Ninho_Inspecionar", depois = "Idle"},
	AlertaNinho = {postura = "pe", entrada = "Ninho_Alerta", loop = {"Idle_Alerta_Mantido"}, saida_de = "deitado"},   -- o proprio clipe levanta
	AmeacaNinho = {postura = "pe", entrada = "Ninho_Ameaca", loop = {"Preparar_Combate"}, levantar = "Ninho_Alerta"},   -- do ninho: sobe em alerta, nao "acordar"
	InteracaoAmigavel = {postura = "pe", entrada = "Dono_Reconhecer", loop = {"Dono_Carinho"}},
	ReceberAlimento = {postura = "pe", entrada = "Dono_Receber_Alimento", depois = "InteracaoAmigavel"},
	MontariaEspera  = {postura = "abaixado", entrada = "Montaria_Abaixar", loop = {"Montaria_Aguardar"}},
	-- usuario 31/10: sentado nobre (peito alto, traseiras dobradas, cauda curva no chao), descanso acordado em pe de guarda
	Sentado     = {postura = "sentado", entrada = "Sentar", loop = {"Sentado"}},
}
-- como sair de cada postura para ficar em pe (inserido automaticamente)
M.LEVANTAR = {deitado = "Acordar", abaixado = "Montaria_Levantar", sentado = "Levantar_Sentado"}
-- estados que so podem comecar a partir de certas posturas (o resto passa por "pe" primeiro)
M.EXIGE = {Sono = {deitado = true}}
M.FADE = 0.35

function M.novo(modelo)
	local self = setmetatable({}, M)
	self.modelo = modelo
	local ac = modelo:FindFirstChildOfClass("AnimationController") or modelo:FindFirstChildWhichIsA("Humanoid")
	self.animator = ac:FindFirstChildOfClass("Animator") or Instance.new("Animator", ac)
	-- clipes num lugar unico em ReplicatedStorage (o cliente precisa deles para reproduzir clipes registrados
	-- com AnimationClipProvider; no ServerStorage a animacao tocava no servidor mas nao aparecia na tela)
	local rs = game:GetService("ReplicatedStorage")
	self.pasta = rs:FindFirstChild("Animacoes_" .. modelo.Name) or rs:FindFirstChild("Animacoes_" .. (modelo:GetAttribute("PastaAnimacoes") or ""))
		or modelo:WaitForChild("Animacoes")                              -- copias do mesmo rig usam PastaAnimacoes
	-- outro rig (ex.: Silverwing): ModuleScript "Apelidos" na pasta mapeia nomes logicos -> clipes que existem
	local ap = self.pasta:FindFirstChild("Apelidos")
	self.apelidos = ap and require(ap) or nil
	self.prefixo = self.apelidos and self.apelidos.prefixo or "Dragao_V14_"
	self.trilhas = {}
	self.estado, self.postura, self.atual = nil, "pe", nil
	self.geracao = 0
	self.Mudou = Instance.new("BindableEvent")
	return self
end

-- KeyframeSequence do nome logico (ou nil): "<prefixo><nome>", depois o apelido, depois o apelido "*"
function M:_kfs(nome)
	local kfs = self.pasta:FindFirstChild(self.prefixo .. nome)
	if kfs or not self.apelidos then return kfs end
	local a = self.apelidos[nome]
	if a == nil then a = self.apelidos["*"] end
	return a and self.pasta:FindFirstChild(a) or nil
end

function M:_trilha(nome)
	local t = self.trilhas[nome]; if t then return t end
	local kfs = self:_kfs(nome); assert(kfs, "clipe ausente: " .. nome)
	local anim = Instance.new("Animation"); anim.Name = nome
	local id = kfs:GetAttribute("AnimationId")                         -- publicado: AnimationId real
	if id then anim.AnimationId = id else anim.AnimationId = game:GetService("AnimationClipProvider"):RegisterAnimationClip(kfs) end
	t = self.animator:LoadAnimation(anim); t.Priority = Enum.AnimationPriority.Core
	-- o nome da trilha nao replica para o cliente: mapa AnimationId -> nome (sons sincronizados no cliente)
	local mapa = self.modelo:FindFirstChild("MapaTrilhas") or Instance.new("Folder"); mapa.Name = "MapaTrilhas"; mapa.Parent = self.modelo
	local sv = Instance.new("StringValue"); sv.Name = nome; sv.Value = anim.AnimationId; sv.Parent = mapa
	self.trilhas[nome] = t
	return t
end

function M:_tocar(nome, loop, fade)
	local t = self:_trilha(nome)
	if self.atual and self.atual ~= t then self.atual:Stop(fade or M.FADE) end
	t.Looped = loop; t:Play(fade or M.FADE); self.atual = t
	return t
end

function M:_esperar(t, g)
	-- espera o fim do clipe (menos o fade, para emendar sem parar), a nao ser que outro Mudar() tenha acontecido.
	-- Logo apos LoadAnimation o Length vale 0 ate o clipe carregar: sem esta espera o laco de variacoes girava sem
	-- ceder e travava o Studio.
	local limite = os.clock() + 5
	while t.Length <= 0 and os.clock() < limite do task.wait(0.05) end
	if t.Length <= 0 then warn("EstadosDragao: clipe sem duracao", t.Animation and t.Animation.Name) return false end
	local fim = os.clock() + math.max(0.1, t.Length / math.max(t.Speed, 0.01) - M.FADE)
	while os.clock() < fim do if self.geracao ~= g then return false end task.wait(0.05) end
	return self.geracao == g
end

function M:_laco(def, g)
	local lista = def.loop; if not lista then return end
	repeat
		local nome = lista[math.random(#lista)]
		local t = self:_tocar(nome, #lista == 1)
		if #lista == 1 then return end                                   -- laco unico: o proprio clipe repete
		if not self:_esperar(t, g) then return end
		task.wait()                                                        -- garante que o laco sempre cede
	until self.geracao ~= g
end

-- Muda para 'estado'; insere transicoes de postura quando necessario. Nao bloqueia (roda em task).
function M:Mudar(estado)
	local def = M.ESTADOS[estado]; if not def then return false, "estado desconhecido: " .. tostring(estado) end
	if estado == self.estado then return true end
	local exige = M.EXIGE[estado]
	if exige and not exige[self.postura] then
		-- ex.: Sono exige estar deitado: deita primeiro (Descanso) e depois adormece
		local antes = self.postura == "pe" and "Descanso" or nil
		if not antes then return false, ("%s nao pode comecar de postura %s"):format(estado, self.postura) end
		self.geracao += 1; local g = self.geracao
		task.spawn(function()
			self:_executar("Descanso", M.ESTADOS.Descanso, g, true)
			if self.geracao == g then self:_executar(estado, def, g) end
		end)
		return true
	end
	self.geracao += 1; local g = self.geracao
	task.spawn(function() self:_executar(estado, def, g) end)
	return true
end

function M:_executar(estado, def, g, semLaco)
	-- de deitado/abaixado para um estado em pe: levanta primeiro (exceto se o proprio estado ja e a saida)
	if self.postura ~= "pe" and def.postura == "pe" and def.saida_de ~= self.postura then
		local t = self:_tocar((self.postura == "deitado" and def.levantar) or M.LEVANTAR[self.postura], false)
		if not self:_esperar(t, g) then return end
		self.postura = "pe"
	end
	-- de abaixado para deitado (ou vice-versa): passa por em pe
	if self.postura ~= "pe" and def.postura ~= "pe" and self.postura ~= def.postura then
		local t = self:_tocar(M.LEVANTAR[self.postura], false)
		if not self:_esperar(t, g) then return end
		self.postura = "pe"
	end
	self.estado = estado; self.Mudou:Fire(estado)
	-- entrada (pulada se ja estamos na postura deitada e a entrada e "deitar": ex. Descanso -> ProtecaoNinho)
	local pularEntrada = def.postura == "deitado" and self.postura == "deitado" and def.entrada ~= "Adormecer"
	if def.entrada and not pularEntrada then
		local t = self:_tocar(def.entrada, false)
		if not self:_esperar(t, g) then return end
	end
	self.postura = def.postura
	if semLaco then return end
	if def.depois and not def.loop then
		if self.geracao == g then self.estado = nil; self:Mudar(def.depois) end
		return
	end
	self:_laco(def, g)
end

function M:Estado() return self.estado, self.postura end
return M
