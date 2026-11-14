-- SoproPredatorio (ModuleScript, ServerScriptService.Combate_Wyvern) — ativa SOPRO PREDATORIO da Wyvern (vaga 1).
-- Regra (kit aprovado 13/11): "inspira, estende o pescoco e sopra pela boca um jato continuo e concentrado de Ar a curta
-- distancia. O fluxo comeca estreito e abre levemente, branco translucido, com som aspero. A cabeca pode acompanhar a
-- presa durante o sopro."
-- AUTORIDADE DO SERVIDOR: reaproveita o Sopro do Nucleo (N._Sopro) com o elemento Ar, como o Sopro Umbral do Sombrio:
-- clipes <prefixo>Sopro_Inicio/Loop/Fim (+ _Sup andando/voando), cone continuo segurando a tecla (ate emissaoMax,
-- consumindo energia por segundo), mira viva dentro do cone do pescoco, dano por tick nos alvos visiveis do cone.
-- So MONTADA nesta etapa (como Rasante e Lamina): a IA selvagem usando o kit e decisao pendente do usuario (na Lamina o
-- guardiao passou a disparar no jogador assim que a vaga entrou em habilidadesForma).
-- O visual proprio (jato estreito que abre de leve, cabeca seguindo a mira, som aspero) e do cliente
-- SoproPredatorio_Cliente, a partir dos eventos FX do Sopro (preparo/emissao/mira/fim, el = "Ar").
local S = {}
function S.executar(self, def, el, noAr, op)
	if self.m:GetAttribute("Controlador") ~= "Montaria" then return end
	return self:_Sopro(def, "Ar", noAr, op or {})
end
return S
