"""Correntes da Noite (Dragao Sombrio, 04/11) — aplica as trocas no src/ e gera V14/ia/patch_correntes_noite.luau com
as MESMAS ancoras (tudo-ou-nada, backup unico ServerStorage.Backup_Correntes_Noite_2026-11-04). O VFXSombra (src/)
vai inteiro para o Studio. Clipes: Sombrio_Correntes_Noite = copia de Hab_Area; _Camada = Hab_Area_Ar."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = "PATCH_CORRENTES_NOITE"
NUC = open(os.path.join(AQUI, "correntes_nucleo.luau"), encoding="utf-8").read().replace("\r\n", "\n").rstrip("\n")
TROCAS = {
 "src/ServerScriptService/Combate_Dragao/ConfigCombate.luau": [
  ('		Sombrio = {"Sopro"}},                                     -- PATCH_SOPRO_UMBRAL (04/11): Sombrio so com o Sopro Umbral por enquanto',
   '		Sombrio = {"Sopro", "Arremetida"}},                       -- PATCH_SOPRO_UMBRAL / PATCH_CORRENTES_NOITE (04/11): Sombrio = Sopro Umbral + Correntes'),
  ('		Sombrio = {Sopro = "SoproUmbral"}},',
   '		Sombrio = {Sopro = "SoproUmbral", Arremetida = "Correntes"}},'),
  ('		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) =====',
   '		-- Correntes da Noite (PATCH_CORRENTES_NOITE): longo alcance; batida das garras -> aviso no chao -> prende ate maxAlvos\n'
   '		-- no raio (sem andar/pular) com dano Sombra continuo; no ar nao prende; resistencia apos soltar. NAO_APROVADO\n'
   '		Correntes = {recarga = 12, energia = 30, elemental = true, intensidade = "moderado", clipe = "Correntes_Noite",\n'
   '			alcance = 160, raio = 16, maxAlvos = 3, alturaChao = 8, batida = 1.7, batidaAr = 1.0, aviso = 0.5,\n'
   '			duracao = 3.4, duracaoAr = 2.4, dano = 10, preso = 2.5, tick = 0.5, danoTick = 4, resistencia = 6},\n'
   '		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) ====='),
 ],
 "src/ServerScriptService/Combate_Dragao/Nucleo.luau": [
  ('	if not ok then error(err, 0) end\nend',
   '	if not ok then error(err, 0) end\nend\n' + NUC),
 ],
 "src/ServerScriptService/Montaria_Dragao_Servidor.server.luau": [
  ('		or ataque == "Rajadas" or ataque == "ZeroAbsoluto" or ataque == "Nevasca"            -- PATCH_KIT_GELO',
   '		or ataque == "Rajadas" or ataque == "ZeroAbsoluto" or ataque == "Nevasca"            -- PATCH_KIT_GELO\n'
   '		or ataque == "Correntes"                                                            -- PATCH_CORRENTES_NOITE (Sombrio)'),
 ],
 "src/ReplicatedStorage/Montaria_Dragoes/ConfigMontaria.luau": [
  ('passivas = {SangueDeMagma = "Sangue de Magma", Burning = "Burning", SangueGlacial = "Sangue Glacial", Frostbite = "Frostbite"},',
   'passivas = {SangueDeMagma = "Sangue de Magma", Burning = "Burning", SangueGlacial = "Sangue Glacial", Frostbite = "Frostbite",\n'
   '			MarcaSombria = "Marca Sombria", RastroBreu = "Rastro do Breu"},   -- PATCH_CORRENTES_NOITE: rotulos do Sombrio'),
  ('		rotulosForma = {Glacial = {Sopro = "Sopro Glacial", Arremetida = "Rajadas", Tempestade = "Zero Absol.", Coracao = "Nevasca"}},',
   '		rotulosForma = {Glacial = {Sopro = "Sopro Glacial", Arremetida = "Rajadas", Tempestade = "Zero Absol.", Coracao = "Nevasca"},\n'
   '			Sombrio = {Sopro = "Sopro Umbral", Arremetida = "Correntes"}},'),
  ('		dicaForma = {Glacial = " | segure 1: Sopro Glacial | 2 Rajadas de Gelo (mire) | 3 Zero Absoluto | 4 Nevasca Ancestral"},',
   '		dicaForma = {Glacial = " | segure 1: Sopro Glacial | 2 Rajadas de Gelo (mire) | 3 Zero Absoluto | 4 Nevasca Ancestral",\n'
   '			Sombrio = " | segure 1: Sopro Umbral | 2 Correntes da Noite (mire no chao)"},'),
  ('		miraVivaForma = {Glacial = {Arremetida = 2.6}},',
   '		miraVivaForma = {Glacial = {Arremetida = 2.6}, Sombrio = {Arremetida = 1.6}},   -- Correntes: mira ate a batida'),
  ('		corEnergiaForma = {Glacial = Color3.fromRGB(150, 215, 255)},',
   '		corEnergiaForma = {Glacial = Color3.fromRGB(150, 215, 255), Sombrio = Color3.fromRGB(165, 90, 255)},'),
 ],
}
NOMES = {"ConfigCombate.luau": "game.ServerScriptService.Combate_Dragao.ConfigCombate",
         "Nucleo.luau": "game.ServerScriptService.Combate_Dragao.Nucleo",
         "Montaria_Dragao_Servidor.server.luau": "game.ServerScriptService.Montaria_Dragao_Servidor",
         "ConfigMontaria.luau": "game.ReplicatedStorage.Montaria_Dragoes.ConfigMontaria"}
for rel, pares in TROCAS.items():
    p = os.path.join(RAIZ, rel); s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    if MARCA in s: print("ja aplicado", rel); continue
    for a, b in pares:
        n = s.count(a); assert n == 1, (rel, n, a[:60]); s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok", rel)
vfx = open(os.path.join(RAIZ, "src/ReplicatedStorage/Combate_Dragoes/VFXSombra.luau"), encoding="utf-8").read().replace("\r\n", "\n")
assert "]=====]" not in vfx and "]==]" not in NUC
L = ['-- patch_correntes_noite.luau (Studio, Edit) — Correntes da Noite do Dragao Sombrio (2a ativa da Sombra, 04/11).',
     '-- Gerado por sombrio/gerar_patch_correntes.py com as MESMAS trocas do src/. Tudo-ou-nada (scripts checados antes de',
     '-- trocar); backup unico ServerStorage.Backup_Correntes_Noite_2026-11-04. Atualiza VFXSombra; cria 2 clipes.',
     'local RS, SS = game:GetService("ReplicatedStorage"), game:GetService("ServerStorage")',
     'local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end',
     'local novos = {}']
for rel, pares in TROCAS.items():
    nome = rel.split("/")[-1]
    L.append('do local s = %s; local src = s.Source:gsub("\\r\\n", "\\n")' % NOMES[nome])
    L.append('  if src:find("%s", 1, true) then return "scripts ja aplicados" end' % MARCA)
    for a, b in pares:
        L.append('  src = troca(src, [==[' + a + ']==], [==[' + b + ']==])')
    L.append('  assert(loadstring(src), "%s nao compila"); table.insert(novos, {s, src}) end' % nome)
L += ['local vfx = [=====[' + "\n" + vfx + ']=====]',
      'assert(loadstring(vfx), "VFXSombra nao compila")',
      'local pasta = RS.Animacoes_Sombrio',
      'local chao, ar = pasta:FindFirstChild("Sombrio_Hab_Area"), pasta:FindFirstChild("Sombrio_Hab_Area_Ar"); assert(chao and ar, "Hab_Area ausente")',
      'if not SS:FindFirstChild("Backup_Correntes_Noite_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Correntes_Noite_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; RS.Combate_Dragoes.VFXSombra:Clone().Parent = f; f.Parent = SS end',
      'for _, v in ipairs({{chao, "Sombrio_Correntes_Noite"}, {ar, "Sombrio_Correntes_Noite_Camada"}}) do local velho = pasta:FindFirstChild(v[2]); if velho then velho:Destroy() end; local c = v[1]:Clone(); c.Name = v[2]; c.Loop = false; c:SetAttribute("Origem", v[1].Name); c.Parent = pasta end',
      'for _, x in ipairs(novos) do x[1].Source = x[2] end',
      'RS.Combate_Dragoes.VFXSombra.Source = vfx',
      'return "aplicado: ConfigCombate + Nucleo + Montaria + ConfigMontaria (" .. #novos .. ") + VFXSombra + 2 clipes; backup ServerStorage.Backup_Correntes_Noite_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_correntes_noite.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
