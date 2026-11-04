-- PATCH_ECLIPSE_DRACONICO (04/11): Eclipse Draconico (Sombrio, slot Coracao, especial). Concentracao (inicio do
-- Hab_Concentracao) -> Rugido_Combate; no pico do rugido a area em volta do corpo escurece (so visual, no cliente) e as
-- Marcas Sombrias PROPRIAS dos alvos na esfera (com linha de visao) DETONAM: o alvo perde todas as marcas deste Sombrio
-- e recebe danoPorMarca x marcas (sem marca = sem dano; a detonacao nao cria marca nova). Sem invisibilidade,
-- invulnerabilidade nem execucao. Contrajogo: sair da area na antecipacao / nao acumular marcas. Numeros NAO_APROVADO.
function N:_Eclipse(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "inicio", el = el, noAr = noAr, detona = def.detona, raio = def.raio})
	self:tocar(def.clipe, noAr, {}, function() end)
	task.wait(def.detona)
	if not m.Parent or m:GetAttribute("Incapacitado") then FX:FireAllClients({d = m, hab = "Eclipse", fase = "fim", el = el}); return end
	local c = self:centroCorpo()
	FX:FireAllClients({d = m, hab = "Eclipse", fase = "detonar", el = el, pos = c, raio = def.raio, duracao = def.escuro})
	local mult = ((m:GetAttribute("DominioAtivo") and Cfg.habilidades.Dominio.multiplicadorDano) or 1) * Passivas.multiplicadorOfensivo(m)
	local total, nAlvos = 0, 0
	for _, a in ipairs(self:alvosValidos()) do
		if naEsfera(c, def.raio, a) and self:visivel(c, a) then
			local n = Passivas.consumirMarcas(m, a)                         -- zera ANTES do dano: o multiplicador da Marca nao soma
			if n > 0 and N.ferir(m, a, def.danoPorMarca * n * mult, el, "Eclipse", def.intensidade, true) then   -- como tick: nao marca de novo
				FX:FireAllClients({d = m, fase = "reacao", alvo = a, intensidade = def.intensidade, el = el, tipo = "Eclipse"})
				FX:FireAllClients({d = m, hab = "Eclipse", fase = "marca", el = el, alvo = a, marcas = n})
				total += n; nAlvos += 1
			end
		end
	end
	m:SetAttribute("UltimoEclipse", ("alvos=%d marcas=%d raio=%d"):format(nAlvos, total, def.raio))
	local resto = def.duracao - def.detona
	if resto > 0 then task.wait(resto) end
end
