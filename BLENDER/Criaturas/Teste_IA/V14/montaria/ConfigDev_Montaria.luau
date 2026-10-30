-- ConfigDev_Montaria (ModuleScript, ServerStorage — NAO replica ao cliente). Ambiente de DESENVOLVIMENTO apenas.
-- Libera voo montado sem a missao para os UserIds abaixo, somente dentro do Roblox Studio e nunca no place de producao.
-- Para desligar: ativo = false (ou apague este modulo). A missao oficial e o atributo VooDesbloqueado nao mudam.
return {
	ativo = true,
	userIds = {4975569556},                       -- usuario de teste autorizado (UserId, nao nome exibido)
	placeIdsProducao = {114230639394991},         -- rpg_roblox: bloqueado mesmo no Studio
}
