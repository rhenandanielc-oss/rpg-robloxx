-- ConfigPoderes_Teste (ModuleScript em ServerStorage.Crocodilo_Piloto) - VALORES PROVISORIOS SO DO PLACE DE TESTE.
-- [PROPOSTA] Nenhum destes numeros e regra do jogo: elemento, passiva, kit, dano, recarga e a regra do agarrao PvP do
-- Crocodilo Primordial continuam PENDENTES (decisao do criador). Agarrao e efeitos so valem para bonecos BonecoTeste.
return {
	SoBonecos = true,                       -- trava: alvo precisa ter o atributo BonecoTeste (nunca jogadores)
	Agarrao = {
		alcance = 6.5,                      -- studs da PONTA DOS DENTES ate o centro do boneco no contato
		ponta = 4.5,                        -- ponta dos dentes = 4,5 a frente do osso Mandibula (+Y do osso)
		sustentacao = 3.5,                  -- s segurando antes de soltar (usuario 16/11: 3,5 s por enquanto)
		dano_contato = 10, dano_por_segundo = 4,
	},
	Giro = {voltas = 2, dano_por_volta = 8},
	Submersao = {profundidade = 2.4, tempo = 4.0, descida = 1.5},
	Cauda = {raio = 11, empurrao = 9, dano = 6},
	AlturaAgua = 4.3,                       -- placa de agua so visual (teste)
}
