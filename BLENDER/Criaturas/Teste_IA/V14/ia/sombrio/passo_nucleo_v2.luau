-- PATCH_PASSO_SOMBRIO_V2 (04/11, pedido do usuario: "algo que durasse mais tempo"): o dragao e, se montado, o CAVALEIRO
-- se desfazem em breu por `duracao` s: ficam INVISIVEIS para os outros (o dono ve um vulto) e ganham `bonus` de
-- velocidade (chao e voo, somado ao Rastro do Breu). Invisivel NAO e invulneravel: dano em area ainda pega. Durante o
-- efeito ninguem trava o alvo neles, a IA selvagem nao os percebe e o servidor recusa trava/alvo neles. Atacar nao
-- cancela. Sem teleporte. Atributos (fim = tempo do servidor): PassoInvisivel no modelo e no Character do cavaleiro,
-- PassoBonus no modelo. NAO_APROVADO.
function N:_PassoSombrio(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	local fim = workspace:GetServerTimeNow() + def.duracao
	local cav = m:GetAttribute("Cavaleiro"); local plr = cav and Players:GetPlayerByUserId(cav); local ch = plr and plr.Character
	m:SetAttribute("PassoInvisivel", fim); m:SetAttribute("PassoBonus", def.bonus)
	if ch then ch:SetAttribute("PassoInvisivel", fim) end
	FX:FireAllClients({d = m, hab = "PassoSombrio", fase = "inicio", el = el, fim = fim, cav = ch})
	m:SetAttribute("UltimoPasso", ("%.1f s, +%d%% vel%s"):format(def.duracao, def.bonus * 100, ch and ", com cavaleiro" or ""))
	task.delay(def.duracao, function()
		if m:GetAttribute("PassoInvisivel") == fim then m:SetAttribute("PassoInvisivel", nil); m:SetAttribute("PassoBonus", nil) end
		if ch and ch:GetAttribute("PassoInvisivel") == fim then ch:SetAttribute("PassoInvisivel", nil) end
		if m.Parent then FX:FireAllClients({d = m, hab = "PassoSombrio", fase = "fim", el = el, cav = ch}) end
	end)
	self:tocar(def.clipe, noAr, {}, function() end)
	task.wait(def.ativar)
end
