-- Uivo_Servidor (Script, Workspace.Teste_LoboArtico) - poder UIVO BOREAL do Lobo Artico (r4, 16/11/2026).
-- ENSAIO no place Teste-animacoes; AUTORIDADE DO SERVIDOR. Nada fora de Workspace.Teste_LoboArtico e tocado (a lentidao
-- so marca/atrasa modelos inimigos que estejam a 20 studs do lobo no ensaio).
-- r4: adaptado ao REFERENCIAS_PODERES_E_EFEITOS.md v5.2 (decisoes do usuario de 16/11; usuario: "Adaptar ao Boreal"):
--   +20% velocidade, +25% CHANCE de esquiva (base 5%, teto 35%), 8 s; inimigos a ate 20 studs: -30% velocidade por 4 s;
--   recarga 22 s, energia 25; energia 100 com regen 5/s. Numeros [PROPOSTA][A TESTAR] do documento.
--   Esquiva = chance sorteada no servidor a cada golpe (BindableFunction SortearEsquiva), separada da Esquiva Perfeita.
--   Lentidao: teto global de 60% somado por alvo (regra 7 do balanceamento); jogadores so se CFG.lentidao.jogadores
--   (PvP [A CONFIRMAR]); o dono/controlador nunca e afetado.
-- r5 (16/11, kit completo): o Uivo passa a gravar BONUS (BonusVel_Uivo / BonusEsquiva_Uivo) e o Kit_Servidor soma todos
--   os bonus em MultVelocidade / ChanceEsquiva (teto 35%); a lentidao virou generica (BindableEvent AplicarLentidao:
--   modelo, valor, duracao) e a energia e compartilhada (BindableFunction GastarEnergia: custo -> true/false).
-- Historico: E1/r3 (15-16/11) usava 15% / 20% de janela / 6 s / 18 s / 15 e regen 6 (copia: Uivo_Servidor_r3_antes_boreal).
-- Roteiro (aprovado): Uivar (1,2 s, parado) -> efeito comeca no FIM do Uivar -> Uivando ate 3,67 s -> PararUivar (1,2 s).
-- Interrupcao (aprovada): no Uivar = sem efeito (energia e recarga gastas); depois = efeito mantido, so a animacao corta.
-- Atributos: Energia, EnergiaMax, UivoFase, UivoFaseT, UivoAtivoFim, UivoDur, RecargaFim_Uivo, RecargaDur_Uivo, UivoN,
-- UivoUltimaRecusa, MultVelocidade, ChanceEsquiva, Parado, UivoLentos; nos alvos: Lentidao, Lentidao_Boreal_Fim.
local Players = game:GetService("Players")
local KSP = game:GetService("KeyframeSequenceProvider")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local lib = game:GetService("ReplicatedStorage"):WaitForChild("Animacoes_LoboArtico")
lobo.ModelStreamingMode = Enum.ModelStreamingMode.Persistent   -- o cliente precisa dos ossos para os efeitos

local CFG = {
	custo = 25, recarga = 22, duracao = 8,           -- Uivo Boreal [PROPOSTA][A TESTAR]
	multVel = 1.20,                                  -- +20% velocidade
	esquivaBase = 0.05, bonusEsquiva = 0.25, tetoEsquiva = 0.35,
	energiaMax = 100, energiaRegen = 5,              -- base dos lobos (Adulto)
	lentidao = {raio = 20, valor = 0.30, dur = 4, teto = 0.60, jogadores = false},
	alcancePedido = 80,                              -- ensaio: jogador a ate 80 studs do lobo (pedido direto)
	tUivar = 1.2, tNota = 3.67, tParar = 1.2,        -- clipes aprovados (anim_v41)
}

local rede = pasta:FindFirstChild("Rede_Uivo") or Instance.new("RemoteEvent")
rede.Name = "Rede_Uivo"; rede.Parent = pasta
local interromper = pasta:FindFirstChild("Interromper_Uivo") or Instance.new("BindableEvent")
interromper.Name = "Interromper_Uivo"; interromper.Parent = pasta   -- servidor: dano forte / atordoamento

local function agora() return workspace:GetServerTimeNow() end
local energia = CFG.energiaMax
lobo:SetAttribute("EnergiaMax", CFG.energiaMax); lobo:SetAttribute("Energia", energia)
lobo:SetAttribute("MultVelocidade", 1); lobo:SetAttribute("ChanceEsquiva", CFG.esquivaBase)
lobo:SetAttribute("BonusVel_Uivo", 0); lobo:SetAttribute("BonusEsquiva_Uivo", 0)
lobo:SetAttribute("MultEsquiva", nil)
lobo:SetAttribute("UivoFase", ""); lobo:SetAttribute("Parado", false)
lobo:SetAttribute("RecargaFim_Uivo", 0); lobo:SetAttribute("RecargaDur_Uivo", CFG.recarga); lobo:SetAttribute("UivoDur", CFG.duracao)

-- faixas no Animator do servidor (o Repouso e do Controle_Servidor)
local animator = lobo.AnimationController:FindFirstChildOfClass("Animator") or Instance.new("Animator", lobo.AnimationController)
local faixas = {}
local function faixa(nome)
	if faixas[nome] then return faixas[nome] end
	local a = Instance.new("Animation"); a.AnimationId = KSP:RegisterKeyframeSequence(lib["LoboArtico_" .. nome])
	faixas[nome] = animator:LoadAnimation(a)
	return faixas[nome]
end
for _, n in ipairs({"Uivar", "Uivando", "PararUivar"}) do faixa(n) end

local ciclo = 0            -- id do uivo em andamento (troca ao cancelar/terminar)
local recargaFim, ativoFim = 0, 0

local function fase(nome)
	lobo:SetAttribute("UivoFase", nome); lobo:SetAttribute("UivoFaseT", agora())
	for _, n in ipairs({"Uivar", "Uivando", "PararUivar"}) do
		if n ~= nome and faixas[n].IsPlaying then faixas[n]:Stop(0.15) end
	end
	if nome ~= "" then faixas[nome]:Play(0.15) end
end

local function recusar(motivo)
	lobo:SetAttribute("UivoUltimaRecusa", motivo .. " @" .. string.format("%.2f", agora()))
	return false, motivo
end

-- lentidao em area ------------------------------------------------------------------------------------------------
local lentos = {}                                   -- [modelo] = {fontes = {{valor, fim}}, base = WalkSpeed original}
local function recalcular(m)
	local reg = lentos[m]; if not reg then return end
	local t, soma = agora(), 0
	for i = #reg.fontes, 1, -1 do
		if reg.fontes[i][2] <= t + 0.01 then table.remove(reg.fontes, i) else soma += reg.fontes[i][1] end
	end
	soma = math.min(soma, CFG.lentidao.teto)
	local hum = m:FindFirstChildOfClass("Humanoid")
	if hum and reg.base then hum.WalkSpeed = reg.base * (1 - soma) end
	m:SetAttribute("Lentidao", soma)                 -- criaturas sem Humanoid leem isto no proprio controlador
	if soma <= 0 then
		m:SetAttribute("Lentidao_Boreal_Fim", nil)
		lentos[m] = nil
	end
end
local function aplicarLentidao(m, valor, dur)
	valor = valor or CFG.lentidao.valor; dur = dur or CFG.lentidao.dur
	local reg = lentos[m]
	if not reg then
		local hum = m:FindFirstChildOfClass("Humanoid")
		reg = {fontes = {}, base = hum and hum.WalkSpeed or nil}; lentos[m] = reg
	end
	local fim = agora() + dur
	table.insert(reg.fontes, {valor, fim})
	m:SetAttribute("Lentidao_Boreal_Fim", fim)       -- o cliente desenha a geada no corpo do alvo
	recalcular(m)
	task.delay(dur + 0.05, function() recalcular(m) end)
end
local function alvoDe(parte)                        -- sobe ate o Model com Humanoid ou atributo Criatura
	local m = parte:FindFirstAncestorOfClass("Model")
	while m do
		if m:FindFirstChildOfClass("Humanoid") or m:GetAttribute("Criatura") then return m end
		m = m:FindFirstAncestorOfClass("Model")
	end
	return nil
end
local function lentidaoEmArea()
	local centro = lobo:GetPivot().Position
	local controlador = lobo:GetAttribute("Controlador")
	local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Exclude; op.FilterDescendantsInstances = {lobo}
	local vistos, n = {}, 0
	for _, parte in ipairs(workspace:GetPartBoundsInRadius(centro, CFG.lentidao.raio, op)) do
		local m = alvoDe(parte)
		if m and not vistos[m] then
			vistos[m] = true
			local jogador = Players:GetPlayerFromCharacter(m)
			local ehDono = jogador and (jogador.UserId == controlador or jogador.UserId == lobo:GetAttribute("DonoUserId"))
			local raiz = m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart or parte
			local dentro = (raiz.Position - centro).Magnitude <= CFG.lentidao.raio
			if dentro and not ehDono and (CFG.lentidao.jogadores or not jogador) then aplicarLentidao(m); n += 1 end
		end
	end
	lobo:SetAttribute("UivoLentos", n)
end

local function aplicarEfeito(id)
	if id ~= ciclo then return end
	ativoFim = agora() + CFG.duracao
	lobo:SetAttribute("UivoAtivoFim", ativoFim)
	lobo:SetAttribute("BonusVel_Uivo", CFG.multVel - 1)
	lobo:SetAttribute("BonusEsquiva_Uivo", CFG.bonusEsquiva)
	lentidaoEmArea()
	local fim = ativoFim
	task.delay(CFG.duracao, function()
		if ativoFim == fim then          -- outro uivo nao renovou
			lobo:SetAttribute("BonusVel_Uivo", 0); lobo:SetAttribute("BonusEsquiva_Uivo", 0)
		end
	end)
end

local function uivar(origem)
	local t = agora()
	if lobo:GetAttribute("Incapacitado") then return recusar("incapacitado") end
	if lobo:GetAttribute("UivoFase") ~= "" then return recusar("ja uivando") end
	if lobo:GetAttribute("PoderAtivo") then return recusar("outro poder ativo") end          -- r5 (kit)
	if (lobo:GetAttribute("VelAtual") or 0) > 0.3 then return recusar("em movimento") end   -- uiva parado (o controlador freia antes)
	if t < recargaFim then return recusar(string.format("recarga %.1f s", recargaFim - t)) end
	if energia < CFG.custo then return recusar(string.format("energia %.0f < %d", energia, CFG.custo)) end
	energia -= CFG.custo; lobo:SetAttribute("Energia", math.floor(energia))
	recargaFim = t + CFG.recarga; lobo:SetAttribute("RecargaFim_Uivo", recargaFim)
	lobo:SetAttribute("UivoN", (lobo:GetAttribute("UivoN") or 0) + 1)
	ciclo += 1; local id = ciclo
	lobo:SetAttribute("Parado", true)
	fase("Uivar")
	task.delay(CFG.tUivar, function()
		if id ~= ciclo then return end
		aplicarEfeito(id); fase("Uivando")
		task.delay(CFG.tNota, function()
			if id ~= ciclo then return end
			fase("PararUivar")
			task.delay(CFG.tParar, function()
				if id ~= ciclo then return end
				ciclo += 1; fase(""); lobo:SetAttribute("Parado", false)
			end)
		end)
	end)
	return true, origem
end

interromper.Event:Connect(function(motivo)
	if lobo:GetAttribute("UivoFase") == "" then return end
	local antesDoEfeito = lobo:GetAttribute("UivoFase") == "Uivar"
	ciclo += 1                                   -- invalida os passos agendados
	fase(""); lobo:SetAttribute("Parado", false)
	lobo:SetAttribute("UivoInterrompido", (motivo or "?") .. (antesDoEfeito and " (sem efeito)" or " (efeito mantido)"))
end)

rede.OnServerEvent:Connect(function(jogador, pedido)
	if pedido ~= "Uivo" then return end          -- so o nome do poder vem do cliente; numeros ficam no servidor
	local ch = jogador.Character; local hrp = ch and ch:FindFirstChild("HumanoidRootPart")
	if not hrp then return recusar("sem personagem") end
	if (hrp.Position - lobo:GetPivot().Position).Magnitude > CFG.alcancePedido then return recusar("longe do lobo") end
	local dono = lobo:GetAttribute("DonoUserId")
	if dono and dono ~= jogador.UserId then return recusar("nao e o dono") end
	uivar("jogador " .. jogador.UserId)
end)

-- pedido vindo do Controle_Servidor (jogador que assumiu o lobo; o controlador ja freou ate parar)
local pedir = pasta:FindFirstChild("Pedir_Uivo") or Instance.new("BindableEvent")
pedir.Name = "Pedir_Uivo"; pedir.Parent = pasta
pedir.Event:Connect(function(userId)
	if lobo:GetAttribute("Controlador") ~= userId then return recusar("nao e o controlador") end
	uivar("controle " .. tostring(userId))
end)

-- esquiva por CHANCE, sorteada no servidor a cada golpe (o sistema de dano chama antes de aplicar o dano)
local sortear = pasta:FindFirstChild("SortearEsquiva") or Instance.new("BindableFunction")
sortear.Name = "SortearEsquiva"; sortear.Parent = pasta
sortear.OnInvoke = function()
	return math.random() < math.min(CFG.tetoEsquiva, lobo:GetAttribute("ChanceEsquiva") or CFG.esquivaBase)
end

-- r5: lentidao generica e energia compartilhada (para o Kit_Servidor)
local evLent = pasta:FindFirstChild("AplicarLentidao") or Instance.new("BindableEvent")
evLent.Name = "AplicarLentidao"; evLent.Parent = pasta
evLent.Event:Connect(function(m, valor, dur) if typeof(m) == "Instance" and m:IsA("Model") then aplicarLentidao(m, valor, dur) end end)
local fnEn = pasta:FindFirstChild("GastarEnergia") or Instance.new("BindableFunction")
fnEn.Name = "GastarEnergia"; fnEn.Parent = pasta
fnEn.OnInvoke = function(custo)
	if type(custo) ~= "number" or custo < 0 then return false end
	if energia < custo then return false end
	energia -= custo; lobo:SetAttribute("Energia", math.floor(energia)); return true
end

Players.PlayerRemoving:Connect(function(j)
	-- o estado e do lobo: efeito e recarga continuam na hora do servidor; nada e reiniciado ao reconectar
	if lobo:GetAttribute("DonoUserId") == j.UserId then lobo:SetAttribute("DonoAusente", true) end
end)

task.spawn(function()
	while lobo.Parent do
		local dt = task.wait(0.25)
		if energia < CFG.energiaMax then
			energia = math.min(CFG.energiaMax, energia + CFG.energiaRegen * dt)
			lobo:SetAttribute("Energia", math.floor(energia))
		end
	end
end)

pasta:SetAttribute("Uivo_Versao", "Boreal r5 16/11 (bonus somados no Kit, lentidao generica, energia compartilhada)")
-- so ensaio: permite zerar/ajustar energia pelo servidor para testar a recusa
local definir = pasta:FindFirstChild("Ensaio_DefinirEnergia") or Instance.new("BindableEvent")
definir.Name = "Ensaio_DefinirEnergia"; definir.Parent = pasta
definir.Event:Connect(function(v) energia = math.clamp(v, 0, CFG.energiaMax); lobo:SetAttribute("Energia", math.floor(energia)) end)
