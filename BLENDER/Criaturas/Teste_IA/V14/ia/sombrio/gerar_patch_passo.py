"""Passo Sombrio (Dragao Sombrio, 4a ativa, slot Tempestade/tecla 3; escolha do usuario 04/11). Aplica no src/ e gera
V14/ia/patch_passo_sombrio.luau (tudo-ou-nada; backup unico ServerStorage.Backup_Passo_Sombrio_2026-11-04):
ConfigCombate (kit + numeros NAO_APROVADO), Nucleo (N:_PassoSombrio), Montaria (ataque fixo), ConfigMontaria (rotulo/dica),
VFXSombra (sumir/surgir/rastro); atributo HabilidadesForma do modelo Sombrio ganha "Tempestade"."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
AQUI = os.path.dirname(os.path.abspath(__file__))
S_ = r"C:/Users/Rhenan/AppData/Local/Temp/claude/C--Users-Rhenan-Downloads-RPG-Roblox-GitHub-Pacote-Inicial/c92d756a-ad80-4092-8c4d-09d4963b8006/scratchpad"
MARCA = "PATCH_PASSO_SOMBRIO"
NUC = open(os.path.join(AQUI, "passo_nucleo.luau"), encoding="utf-8").read().replace("\r\n", "\n").rstrip("\n")
VFX_BLOCO = open(os.path.join(AQUI, "passo_vfx.luau"), encoding="utf-8").read().replace("\r\n", "\n")
TROCAS = {
 "src/ServerScriptService/Combate_Dragao/ConfigCombate.luau": [
  ('		Sombrio = {"Sopro", "Arremetida", "Coracao"}},            -- PATCH_SOPRO_UMBRAL / CORRENTES_NOITE / ECLIPSE_DRACONICO (04/11): kit completo do Sombrio',
   '		Sombrio = {"Sopro", "Arremetida", "Tempestade", "Coracao"}},   -- PATCH_SOPRO_UMBRAL / CORRENTES / ECLIPSE / PASSO_SOMBRIO (04/11): kit do Sombrio'),
  ('		Sombrio = {Sopro = "SoproUmbral", Arremetida = "Correntes", Coracao = "Eclipse"}},',
   '		Sombrio = {Sopro = "SoproUmbral", Arremetida = "Correntes", Tempestade = "PassoSombrio", Coracao = "Eclipse"}},'),
  ('		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) =====',
   '		-- Passo Sombrio (PATCH_PASSO_SOMBRIO): some em breu e reaparece `distancia` a frente ou `atras` do alvo travado (ate\n'
   '		-- `alcance`), sem atravessar parede; sem dano. sumir/surgir = s de cada metade. NAO_APROVADO\n'
   '		PassoSombrio = {recarga = 9, energia = 20, elemental = true, intensidade = "leve", clipe = "Hab_Investida",\n'
   '			distancia = 60, alcance = 90, atras = 18, sumir = 0.3, surgir = 0.35},\n'
   '		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) ====='),
 ],
 "src/ServerScriptService/Combate_Dragao/Nucleo.luau": [
  ('\n\n-- energia\ntask.spawn(function()', '\n\n' + NUC + '\n\n-- energia\ntask.spawn(function()'),
 ],
 "src/ServerScriptService/Montaria_Dragao_Servidor.server.luau": [
  ('		or ataque == "Eclipse"                                                              -- PATCH_ECLIPSE_DRACONICO (Sombrio)\n',
   '		or ataque == "Eclipse"                                                              -- PATCH_ECLIPSE_DRACONICO (Sombrio)\n'
   '		or ataque == "PassoSombrio"                                                         -- PATCH_PASSO_SOMBRIO (Sombrio)\n'),
 ],
 "src/ReplicatedStorage/Montaria_Dragoes/ConfigMontaria.luau": [
  ('			Sombrio = {Sopro = "Sopro Umbral", Arremetida = "Correntes", Coracao = "Eclipse"}},   -- PATCH_ECLIPSE_DRACONICO',
   '			Sombrio = {Sopro = "Sopro Umbral", Arremetida = "Correntes", Tempestade = "Passo Sombrio", Coracao = "Eclipse"}},   -- PATCH_ECLIPSE_DRACONICO / PATCH_PASSO_SOMBRIO'),
  ('			Sombrio = " | segure 1: Sopro Umbral | 2 Correntes da Noite (mire no chao) | 4 Eclipse Dracônico"},',
   '			Sombrio = " | segure 1: Sopro Umbral | 2 Correntes da Noite (mire no chao) | 3 Passo Sombrio | 4 Eclipse Dracônico"},'),
 ],
 "src/ReplicatedStorage/Combate_Dragoes/VFXSombra.luau": [
  ('function S.evento(d, f)', VFX_BLOCO + 'function S.evento(d, f)'),
  ('	if d.hab == "Eclipse" then eclipseEvento(m, d, f); return true end\n',
   '	if d.hab == "Eclipse" then eclipseEvento(m, d, f); return true end\n'
   '	if d.hab == "PassoSombrio" then passoEvento(m, d, f); return true end   -- PATCH_PASSO_SOMBRIO\n'),
 ],
 "BLENDER/Criaturas/Teste_IA/V14/ia/studio_montar_sombrio.luau": [
  ('m:SetAttribute("HabilidadesForma", "Sopro,Arremetida,Coracao")', 'm:SetAttribute("HabilidadesForma", "Sopro,Arremetida,Tempestade,Coracao")'),
 ],
}
NOMES = {"ConfigCombate.luau": "game.ServerScriptService.Combate_Dragao.ConfigCombate",
         "Nucleo.luau": "game.ServerScriptService.Combate_Dragao.Nucleo",
         "Montaria_Dragao_Servidor.server.luau": "game.ServerScriptService.Montaria_Dragao_Servidor",
         "ConfigMontaria.luau": "game.ReplicatedStorage.Montaria_Dragoes.ConfigMontaria",
         "VFXSombra.luau": "game.ReplicatedStorage.Combate_Dragoes.VFXSombra"}
for rel, pares in TROCAS.items():
    p = os.path.join(RAIZ, rel); s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    if MARCA in s or (rel.endswith("studio_montar_sombrio.luau") and "Tempestade,Coracao" in s): print("ja aplicado", rel); continue
    for a, b in pares:
        n = s.count(a); assert n == 1, (rel, n, a[:60]); s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok", rel)
L = ['-- patch_passo_sombrio.luau (Studio, Edit) — Passo Sombrio, 4a ativa do Dragao Sombrio (04/11).',
     '-- Gerado por sombrio/gerar_patch_passo.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico',
     '-- ServerStorage.Backup_Passo_Sombrio_2026-11-04.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage")',
     'local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end',
     'local novos = {}']
for rel, pares in TROCAS.items():
    nome = rel.split("/")[-1]
    if nome not in NOMES: continue
    L.append('do local s = %s; local src = s.Source:gsub("\\r\\n", "\\n")' % NOMES[nome])
    L.append('  if src:find("%s", 1, true) then return "scripts ja aplicados" end' % MARCA)
    for a, b in pares:
        assert "]=====]" not in a + b
        L.append('  src = troca(src, [=====[' + a + ']=====], [=====[' + b + ']=====])')
    L.append('  assert(loadstring(src), "%s nao compila"); table.insert(novos, {s, src}) end' % nome)
L += ['if not SS:FindFirstChild("Backup_Passo_Sombrio_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Passo_Sombrio_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f:SetAttribute("HabilidadesFormaAntes", workspace.Sombrio:GetAttribute("HabilidadesForma")); f.Parent = SS end',
      'for _, x in ipairs(novos) do x[1].Source = x[2] end',
      'workspace.Sombrio:SetAttribute("HabilidadesForma", "Sopro,Arremetida,Tempestade,Coracao")',
      'return "aplicado: " .. #novos .. " scripts + HabilidadesForma do Sombrio; backup ServerStorage.Backup_Passo_Sombrio_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_passo_sombrio.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
