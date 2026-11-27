return {
	{"SolInfernal_Servidor", {
		{[==[	estado.ocupado = true
	local roxo = cerbero:GetAttribute("Furia") == true
	log(string.format("lancando]==], [==[	if cerbero:GetAttribute("PoderAtivo") then log("recusado: poder ativo (" .. tostring(cerbero:GetAttribute("PoderAtivo")) .. ")") return end
	cerbero:SetAttribute("PoderAtivo", "Sol"); cerbero:SetAttribute("MordidaBloqueada", true)   -- poder ativo (27/11)
	estado.ocupado = true
	local roxo = cerbero:GetAttribute("Furia") == true
	log(string.format("lancando]==]},
		{[==[			bola:Destroy()
			estado.prontoEm = os.clock() + C.Recarga * C.RecargaInterrompida
]==], [==[			bola:Destroy()
			cerbero:SetAttribute("PoderAtivo", nil); cerbero:SetAttribute("MordidaBloqueada", nil)
			estado.prontoEm = os.clock() + C.Recarga * C.RecargaInterrompida
]==]},
		{[==[	bola:SetAttribute("Escala", 1); bola:SetAttribute("Voando", true)
]==], [==[	bola:SetAttribute("Escala", 1); bola:SetAttribute("Voando", true)
	cerbero:SetAttribute("MordidaBloqueada", nil)   -- disparou: pode morder
]==]},
		{[==[	bola:Destroy()
	estado.prontoEm = os.clock() + C.Recarga
]==], [==[	bola:Destroy()
	cerbero:SetAttribute("PoderAtivo", nil)
	estado.prontoEm = os.clock() + C.Recarga
]==]},
	}},
	{"Investida_Servidor", {
		{[==[	estado.ocupado = true; estado.dono = dono; estado.dirAlvo = nil; donoRastro = dono
]==], [==[	if cerbero:GetAttribute("PoderAtivo") then log("recusado: poder ativo (" .. tostring(cerbero:GetAttribute("PoderAtivo")) .. ")") return end
	cerbero:SetAttribute("PoderAtivo", "Investida")   -- poder ativo (27/11); mordida liberada no boost
	estado.ocupado = true; estado.dono = dono; estado.dirAlvo = nil; donoRastro = dono
]==]},
		{[==[						sobre = {modelo = m, h = h, inicio = os.clock(), danoFeito = false}
]==], [==[						sobre = {modelo = m, h = h, inicio = os.clock(), danoFeito = false}
						cerbero:SetAttribute("MordidaBloqueada", true)
]==]},
		{[==[				sobre = nil
]==], [==[				sobre = nil
				cerbero:SetAttribute("MordidaBloqueada", nil)
]==]},
		{[==[						tocar("Cerbero_InvestidaImpacto", 0.08)
]==], [==[						tocar("Cerbero_InvestidaImpacto", 0.08)
						cerbero:SetAttribute("MordidaBloqueada", true)
]==]},
		{[==[	estado.ocupado = false; estado.dono = nil
]==], [==[	estado.ocupado = false; estado.dono = nil
	cerbero:SetAttribute("PoderAtivo", nil); cerbero:SetAttribute("MordidaBloqueada", nil)
]==]},
	}},
	{"VigiliaFuria_Servidor", {
		{[==[	estado.ocupado = true
	log(string.format("FURIA]==], [==[	if cerbero:GetAttribute("PoderAtivo") then log("recusado: poder ativo (" .. tostring(cerbero:GetAttribute("PoderAtivo")) .. ")") return end
	cerbero:SetAttribute("PoderAtivo", "Furia"); cerbero:SetAttribute("MordidaBloqueada", true)   -- poder ativo so no rugido (27/11)
	estado.ocupado = true
	log(string.format("FURIA]==]},
		{[==[		cerbero:SetAttribute("MultDano", C.FuriaMultDano)
]==], [==[		cerbero:SetAttribute("MultDano", C.FuriaMultDano)
		cerbero:SetAttribute("PoderAtivo", nil); cerbero:SetAttribute("MordidaBloqueada", nil)
		cerbero:SetAttribute("FuriaSustentada", true)   -- Mordida_Servidor: cabecas independentes, +15% de velocidade de ataque
]==]},
		{[==[		cerbero:SetAttribute("MultDano", 1); cerbero:SetAttribute("Furia", false); cerbero:SetAttribute("FuriaFade", nil)
]==], [==[		cerbero:SetAttribute("MultDano", 1); cerbero:SetAttribute("Furia", false); cerbero:SetAttribute("FuriaFade", nil)
		cerbero:SetAttribute("FuriaSustentada", nil)
]==]},
	}},
}
