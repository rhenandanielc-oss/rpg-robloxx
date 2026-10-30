-- ConfigCombate (ModuleScript, ServerScriptService.Combate_Dragao) — PROTOTIPO.
-- OFICIAL (Documento 02 + ATUALIZACAO OFICIAL 2026-10-29):
--   Dragao das Montanhas = Fogo/Terra/Ar (Raio REMOVIDO so desta forma; continua no sistema global para outras especies).
--   Nasce com 1 elemento e desbloqueia os outros 2 pela progressao (max 3 equipados).
--   Habilidades da forma: Sopro Draconico, Arremetida Draconica, Tempestade de Asas, Ruptura Vulcanica
--   (Dominio Draconico deixou de pertencer ao Dragao das Montanhas; o codigo dele fica disponivel para outras formas).
--   Recarga COMPARTILHADA por habilidade (trocar elemento nao reinicia).
--   Ruptura Vulcanica: propria da forma, visual de Terra+Fogo, NAO exige esses elementos desbloqueados, nao concede elemento.
-- PENDENTE: escalas de dano, recargas, energia, alcance, lancamento e fusoes. TODO numero abaixo e EXPERIMENTAL (NAO_APROVADO).
local NAO_APROVADO = true
return {
	NAO_APROVADO = NAO_APROVADO,
	elementosGlobais = {"Fogo", "Terra", "Ar", "Raio", "Gelo", "Agua", "Luz", "Sombra"},  -- referencia; cada forma restringe abaixo
	elementosForma = {Montanhas = {"Fogo", "Terra", "Ar"}},       -- Glacial/Sombrio: definir quando os documentos/modelos existirem
	habilidadesForma = {Montanhas = {"Sopro", "Arremetida", "Tempestade", "Ruptura"}},
	maxElementos = 3,
	energiaMax = 100, energiaRegen = 6,                         -- por segundo
	basicos = {
		Mordida = {clipe = "Ataque_Mordida", recarga = 1.6, dano = 18, alcance = 34, raio = 14, intensidade = "leve"},
		Garra = {clipe = "Ataque_Garra_E", clipeD = "Ataque_Garra_D", recarga = 1.8, dano = 14, alcance = 30, raio = 18, intensidade = "moderado"},
		Cauda = {clipe = "Ataque_Cauda", recarga = 3, dano = 20, raio = 62, intensidade = "pesado"},
		Rugido = {clipe = "Rugido_Combate", recarga = 8, dano = 0},  -- sem dano: nao ha regra aprovada
	},
	habilidades = {
		Sopro = {recarga = 9, energia = 25, emissao = 1.8, tick = 0.3, elemental = true,
			porElemento = {
				-- alcance AUMENTADO para teste (antes 75/95/60); angulo do cone casado com a largura visual do jato
				Fogo = {forma = "cone", alcance = 110, angulo = 12, dano = 6},
				Terra = {forma = "projetil", alcance = 120, quantidade = 4, velocidade = 150, raioImpacto = 13, dano = 12},
				Raio = {forma = "descarga", alcance = 100, largura = 5, pulsos = 3, dano = 10},   -- outras especies (nao Montanhas)
				Ar = {forma = "cone", alcance = 95, angulo = 18, dano = 5},
			}},
		Arremetida = {recarga = 12, energia = 30, distancia = 85, duracao = 0.7, raio = 22, dano = 26, intensidade = "pesado"},
		Tempestade = {recarga = 16, energia = 40, raio = 78, dano = 16, intensidade = "moderado",
			elevacao = 11},                                        -- quanto o corpo sobe de verdade na versao terrestre
		Ruptura = {recarga = 15, energia = 35, dano = 24, intensidade = "pesado",
			requerSolo = true, distSoloMax = 7,                    -- patas ate 7 studs do chao
			ondaRaio = 22,                                         -- onda de choque no impacto (centro do corpo)
			aneis = {24, 36, 48}, pilaresPorAnel = {6, 8, 10}, intervaloAnel = 0.16,   -- erupcao em VOLTA do dragao (360 graus)
			folgaCorpo = 7, folgaAsa = 5,                          -- exclusao: distancia minima do pilar aos ossos/membranas
			raioPilar = 8, protecaoOvo = 16,
			lancamento = {vertical = 48, horizontal = 28}},        -- reacao curta (studs/s); intensidade a balancear
		Dominio = {recarga = 30, energia = 35, duracao = 12, multiplicadorDano = 1.0},   -- NAO pertence ao Montanhas (outras formas)
	},
	pvpAtivoAtributo = "PvPAtivo",                              -- Workspace:SetAttribute("PvPAtivo", true) libera dano entre jogadores
	zonaSeguraTag = "ZonaSegura",                               -- CollectionService: partes que protegem quem esta dentro
	estruturaProtegidaTag = "EstruturaProtegida",               -- efeitos (pilares) nunca nascem dentro destas partes
	pedidoIntervaloMin = 0.25,                                  -- anti-spam do RemoteEvent
	sons = {},                                                  -- sem audio licenciado disponivel: pontos de sincronia apenas
}
