"""IA selvagem com o kit da Sombra (04/11, "prossiga" do usuario apos a proposta). A escolha de habilidade da IA
(Combate_Dragao_Servidor.escolher) usava as taticas do kit de Fogo pelo NOME DO SLOT: com o Sombrio, o Eclipse caia na
regra da lamina do Coracao Infernal, o Passo na regra de grupo da Tempestade e as Correntes na regra de trajeto da
Arremetida. Aqui o kit Sombra ganha tatica propria (so quando kitForma mapeia Coracao -> Eclipse); as outras formas nao
mudam. O Locomotor da IA passa a somar o PassoBonus (andar/correr e voo). Aplica no src/ e gera
V14/ia/patch_ia_sombra.luau (tudo-ou-nada; backup unico ServerStorage.Backup_IA_Sombra_2026-11-04)."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
MARCA = "PATCH_IA_KIT_SOMBRA"
BLOCO = '''	-- PATCH_IA_KIT_SOMBRA (04/11): kit do Sombrio com tatica propria (slots: Arremetida = Correntes, Tempestade = Passo,
	-- Coracao = Eclipse). NAO_APROVADO
	if kitS then
		local CO, EC = Cfg.habilidades.Correntes, Cfg.habilidades.Eclipse
		-- Correntes: media/longa distancia, com linha de visao; vem do chao, entao serve contra alvo no ar (prioridade
		-- maior se ele voa acima ou esta alem do sopro)
		if d >= 22 and d < CO.alcance then
			if not c:visivel(b, alvo) then table.insert(bloqueio, "Correntes: sem linha de visao")
			else add("Arremetida", (acima > 15 or d > alcSopro(c)) and 1.05 or 0.8) end
		end
		-- Eclipse: alvos dentro da area; grupo (2+) ou um alvo com 3+ marcas desta origem (mais marcas, mais vontade)
		if os.clock() - (ultimoCoracao[c.m] or -99) > EC.recarga * 1.5 then
			local naArea, marcas = 0, 0
			for _, a in ipairs(c:alvosValidos()) do
				if (raiz(a).Position - p).Magnitude < EC.raio * 0.8 then naArea += 1; marcas += a:GetAttribute("MarcaSombria_" .. c.m.Name) or 0 end
			end
			if naArea >= 2 or (naArea == 1 and marcas >= 3) then add("Coracao", 1.15 + math.min(marcas, 5) * 0.03)
			elseif naArea == 1 then table.insert(bloqueio, "Eclipse: poucas marcas (" .. marcas .. ")") end
		end
		-- Passo Sombrio: some e acelera para escapar ferido ou para encurtar a distancia de um alvo longe
		local vida, vmax = c.m:GetAttribute("Vida"), c.m:GetAttribute("VidaMax")
		local ferido = vida and vmax and vmax > 0 and vida / vmax < 0.35
		if not c.m:GetAttribute("PassoInvisivel") and (ferido or d > 110) then add("Tempestade", ferido and 1.3 or 0.7) end
	end
'''
TROCAS = {
 "src/ServerScriptService/Combate_Dragao_Servidor.server.luau": [
  ('local function alcSopro(c)\n\tlocal e = Cfg.habilidades.Sopro.porElemento[c.m:GetAttribute("ElementoAtivo") or ""]; return e and e.alcance or 100\nend\n',
   'local function alcSopro(c)\n'
   '\tif c:real("Coracao") == "Eclipse" then                             -- PATCH_IA_KIT_SOMBRA: Sopro Umbral tem alcance proprio\n'
   '\t\tlocal e = Cfg.habilidades.SoproUmbral.porElemento.Sombra; return e and e.alcance or 95\n'
   '\tend\n'
   '\tlocal e = Cfg.habilidades.Sopro.porElemento[c.m:GetAttribute("ElementoAtivo") or ""]; return e and e.alcance or 100\nend\n'),
  ('	local noAr = c.m:GetAttribute("NoAr") == true\n	local perto, atrasN = 0, 0\n',
   '	local noAr = c.m:GetAttribute("NoAr") == true\n'
   '	local kitS = c:real("Coracao") == "Eclipse"                             -- PATCH_IA_KIT_SOMBRA\n'
   '	local perto, atrasN = 0, 0\n'),
  ('	if c:temHabilidade("Coracao") and os.clock() - (ultimoCoracao[c.m] or -99) > CI.recarga * 1.5 then\n',
   '	if not kitS and c:temHabilidade("Coracao") and os.clock() - (ultimoCoracao[c.m] or -99) > CI.recarga * 1.5 then\n'),
  ('	if perto >= 3 or (perto >= 2 and (atrasN >= 1 or math.random() < 0.35)) then\n',
   '	if not kitS and (perto >= 3 or (perto >= 2 and (atrasN >= 1 or math.random() < 0.35))) then\n'),
  ('	if d >= 50 and d < 170 then\n',
   '	if not kitS and d >= 50 and d < 170 then\n'),
  ('	-- PATCH_RUGIDOS_FOGO: rugido de combate ocasional',
   BLOCO + '	-- PATCH_RUGIDOS_FOGO: rugido de combate ocasional'),
 ],
 "src/ServerScriptService/IA_Dragao/Locomotor.luau": [
  ('		or (self.m:GetAttribute("RitmoAndarBase") or cfg.andarVel * cfg.andarRitmo)\n',
   '		or (self.m:GetAttribute("RitmoAndarBase") or cfg.andarVel * cfg.andarRitmo)\n'
   '	vel *= 1 + (self.m:GetAttribute("PassoBonus") or 0)                  -- PATCH_IA_KIT_SOMBRA: Passo Sombrio da IA\n'),
  ('		local vel = rapido and cfg.vooRapidoVel or cfg.vooVel\n',
   '		local vel = (rapido and cfg.vooRapidoVel or cfg.vooVel) * (1 + (self.m:GetAttribute("PassoBonus") or 0))   -- PATCH_IA_KIT_SOMBRA\n'),
 ],
}
NOMES = {"Combate_Dragao_Servidor.server.luau": "game.ServerScriptService.Combate_Dragao_Servidor",
         "Locomotor.luau": "game.ServerScriptService.IA_Dragao.Locomotor"}
for rel, pares in TROCAS.items():
    p = os.path.join(RAIZ, rel); s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    if MARCA in s: print("ja aplicado", rel); continue
    for a, b in pares:
        n = s.count(a); assert n == 1, (rel, n, a[:60])
    for a, b in pares: s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok", rel)
L = ['-- patch_ia_sombra.luau (Studio, Edit) — IA selvagem com o kit da Sombra + PassoBonus no Locomotor (04/11).',
     '-- Gerado por sombrio/gerar_patch_ia_sombra.py; backup unico ServerStorage.Backup_IA_Sombra_2026-11-04.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage")',
     'local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end',
     'local novos = {}']
for rel, pares in TROCAS.items():
    nome = rel.split("/")[-1]
    L.append('do local s = %s; local src = s.Source:gsub("\\r\\n", "\\n")' % NOMES[nome])
    L.append('  if src:find("%s", 1, true) then return "ja aplicado" end' % MARCA)
    for a, b in pares:
        assert "]=====]" not in a + b
        L.append('  src = troca(src, [=====[' + a + ']=====], [=====[' + b + ']=====])')
    L.append('  assert(loadstring(src), "%s nao compila"); table.insert(novos, {s, src}) end' % nome)
L += ['if not SS:FindFirstChild("Backup_IA_Sombra_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_IA_Sombra_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f.Parent = SS end',
      'for _, x in ipairs(novos) do x[1].Source = x[2] end',
      'return "aplicado: " .. #novos .. " scripts; backup ServerStorage.Backup_IA_Sombra_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_ia_sombra.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
