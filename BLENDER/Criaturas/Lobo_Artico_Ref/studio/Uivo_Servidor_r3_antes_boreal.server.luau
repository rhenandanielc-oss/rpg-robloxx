-- Uivo_Servidor (Script, Workspace.Teste_LoboArtico) - poder UIVO do Lobo Artico, E1 (aprovado pelo usuario 15/11/2026).
-- ENSAIO no place Teste-animacoes; AUTORIDADE DO SERVIDOR. Nada fora de Workspace.Teste_LoboArtico e tocado.
-- Regra oficial (RPG_02): o Uivo fortalece SO o proprio lobo (sem bonus de grupo, sem dano, sem elemento).
-- Roteiro aprovado: Uivar (1,2 s, parado) -> efeito comeca no FIM do Uivar -> Uivando ate 3,67 s (fim da nota longa)
-- -> PararUivar (1,2 s) -> Repouso.
-- NUMEROS PROVISORIOS (vem do Lobo Ancestral, nao aprovados para o Artico): efeito 6 s, +15% velocidade, +20% janela de
-- esquiva, recarga 18 s (contada desde o pedido aceito), custo 15 de energia. Energia max 100 / regen 6 por s = mesma
-- convencao do ConfigCombate dos dragoes (PROVISORIO).
-- Regra PROVISORIA de interrupcao (a decidir): Interromper antes do fim do Uivar cancela sem efeito; energia e recarga
-- continuam gastas. Depois do fim do Uivar o efeito ja dado continua ate o fim; so a animacao e cortada.
-- Ganchos para o controlador futuro do lobo (ainda nao existe): atributos MultVelocidade e MultEsquiva no modelo;
-- atributo Parado = true durante a animacao (o controlador nao deve mover o lobo).
-- Estado fica no MODELO (servidor), nao no jogador: se o jogador sair/reconectar, efeito e recarga seguem a hora do servidor.
-- Atributos (cliente/HUD/teste): Energia, EnergiaMax, UivoFase ("", "Uivar", "Uivando", "PararUivar"), UivoFaseT,
-- UivoAtivoFim, RecargaFim_Uivo, RecargaDur_Uivo, UivoN (contador), UivoUltimaRecusa.
local Players = game:GetService("Players")
local KSP = game:GetService("KeyframeSequenceProvider")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local lib = game:GetService("ReplicatedStorage"):WaitForChild("Animacoes_LoboArtico")
lobo.ModelStreamingMode = Enum.ModelStreamingMode.Persistent   -- E3: o cliente precisa dos ossos para o som/nevoa/luz

local CFG = {
	custo = 15, recarga = 18, duracao = 6,          -- PROVISORIO
	multVel = 1.15, multEsquiva = 1.20,              -- PROVISORIO
	energiaMax = 100, energiaRegen = 6,              -- PROVISORIO (convencao dos dragoes)
	alcancePedido = 80,                              -- ensaio: jogador precisa estar a ate 80 studs do lobo
	tUivar = 1.2, tNota = 3.67, tParar = 1.2,        -- clipes aprovados (anim_v41)
}

local rede = pasta:FindFirstChild("Rede_Uivo") or Instance.new("RemoteEvent")
rede.Name = "Rede_Uivo"; rede.Parent = pasta
local interromper = pasta:FindFirstChild("Interromper_Uivo") or Instance.new("BindableEvent")
interromper.Name = "Interromper_Uivo"; interromper.Parent = pasta   -- servidor: dano forte / atordoamento

local function agora() return workspace:GetServerTimeNow() end
local energia = CFG.energiaMax
lobo:SetAttribute("EnergiaMax", CFG.energiaMax); lobo:SetAttribute("Energia", energia)
lobo:SetAttribute("MultVelocidade", 1); lobo:SetAttribute("MultEsquiva", 1)
lobo:SetAttribute("UivoFase", ""); lobo:SetAttribute("Parado", false)
lobo:SetAttribute("RecargaFim_Uivo", 0); lobo:SetAttribute("RecargaDur_Uivo", CFG.recarga)

-- faixas no Animator do servidor
local animator = lobo.AnimationController:FindFirstChildOfClass("Animator") or Instance.new("Animator", lobo.AnimationController)
local faixas = {}
local function faixa(nome)
	if faixas[nome] then return faixas[nome] end
	local a = Instance.new("Animation"); a.AnimationId = KSP:RegisterKeyframeSequence(lib["LoboArtico_" .. nome])
	faixas[nome] = animator:LoadAnimation(a)
	return faixas[nome]
end
for _, n in ipairs({"Uivar", "Uivando", "PararUivar"}) do faixa(n) end
-- r3 (16/11): o Repouso agora e do Controle_Servidor (dono da locomocao); o Uivo so toca as 3 faixas Action

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

local function aplicarEfeito(id)
	if id ~= ciclo then return end
	ativoFim = agora() + CFG.duracao
	lobo:SetAttribute("UivoAtivoFim", ativoFim)
	lobo:SetAttribute("MultVelocidade", CFG.multVel); lobo:SetAttribute("MultEsquiva", CFG.multEsquiva)
	local fim = ativoFim
	task.delay(CFG.duracao, function()
		if ativoFim == fim then          -- outro uivo nao renovou
			lobo:SetAttribute("MultVelocidade", 1); lobo:SetAttribute("MultEsquiva", 1)
		end
	end)
end

local function uivar(origem)
	local t = agora()
	if lobo:GetAttribute("Incapacitado") then return recusar("incapacitado") end
	if lobo:GetAttribute("UivoFase") ~= "" then return recusar("ja uivando") end
	if (lobo:GetAttribute("VelAtual") or 0) > 0.3 then return recusar("em movimento") end   -- r3: uiva parado (o controlador freia antes)
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

-- r3: pedido vindo do Controle_Servidor (jogador que assumiu o lobo; o controlador ja freou ate parar)
local pedir = pasta:FindFirstChild("Pedir_Uivo") or Instance.new("BindableEvent")
pedir.Name = "Pedir_Uivo"; pedir.Parent = pasta
pedir.Event:Connect(function(userId)
	if lobo:GetAttribute("Controlador") ~= userId then return recusar("nao e o controlador") end
	uivar("controle " .. tostring(userId))
end)

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

-- so ensaio: permite zerar/ajustar energia pelo servidor para testar a recusa
pasta:SetAttribute("Uivo_Versao", "E1 r3 16/11 (Persistent + Pedir_Uivo + recusa em movimento)")
local definir = pasta:FindFirstChild("Ensaio_DefinirEnergia") or Instance.new("BindableEvent")
definir.Name = "Ensaio_DefinirEnergia"; definir.Parent = pasta
definir.Event:Connect(function(v) energia = math.clamp(v, 0, CFG.energiaMax); lobo:SetAttribute("Energia", math.floor(energia)) end)
