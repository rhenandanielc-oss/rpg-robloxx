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
		profundidade_agua = 0.85,           -- agua: desce da altura de nado para a de espreita (render R2: agua 5,15 x 4,3)
	},
	Giro = {voltas = 2, dano_por_volta = 8},
	Submersao = {                           -- P4 16/11 (agua real; numeros de TESTE)
		folga_topo = 1.5, folga_fundo = 1.0, -- topo do corpo abaixo da superficie / sola acima do fundo
		espreita = 0.8, descida = 0.5, subida = 0.6,   -- s (ref. 5.9: afunda em 0,5 s)
		velocidade = 10, vel_clipe = 1.3,    -- studs/s submerso (proposta: nado 8 x 1,25) e velocidade do clipe
		distancia = 50, olhar_frente = 18,   -- percurso maximo e onde mede a profundidade a frente (cabeca ~16)
		energia_s = 5, energia_teste = 100,  -- ref. secao 4: 5 de energia/s
		tempo_terra = 4.0,                   -- variante em terra (postura baixa)
		profundidade = 2.4,                  -- [P3] so a arena antiga (placa visual)
	},
	Corpo = {pivo = 2.87, olhos = 5.0, topo = 5.74},   -- alturas acima da sola (medidas: Studio e malha no Blender)
	Cauda = {raio = 11, empurrao = 9, dano = 6},
	AlturaAgua = 4.3,                       -- placa de agua so visual (teste)
}
