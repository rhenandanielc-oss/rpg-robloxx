-- MontariaCrocodilo_Servidor (Script em ServerScriptService do place de TESTE Crocodilo-testes) - 20/11
-- Liga a montaria do crocodilo (1a entrega: montar/descer pelo botao, locomocao montada em terra e nado na superficie).
-- Toda a regra fica no PoderesTeste (secao MONTARIA): autoridade do servidor; o cliente so manda intencao.
local M = require(game.ServerStorage:WaitForChild("Crocodilo_Piloto"):WaitForChild("PoderesTeste"))
print("[MontariaCrocodilo] " .. tostring(M.montariaIniciar()))
