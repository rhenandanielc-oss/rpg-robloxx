"""Eclipse Draconico (Dragao Sombrio, 04/11) — aplica as trocas no src/ e gera V14/ia/patch_eclipse_draconico.luau com
as MESMAS ancoras (tudo-ou-nada, backup unico ServerStorage.Backup_Eclipse_Draconico_2026-11-04). O VFXSombra (src/)
vai inteiro para o Studio. Clipes: Sombrio_Eclipse_Draconico = Hab_Concentracao [0; 0,9] + Rugido_Combate a partir de
1,15 s (0,25 s de transicao interpolada); _Camada (ar) = 1o quadro do Rugido_Combate_Camada segurado + o mesmo rugido."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = "PATCH_ECLIPSE_DRACONICO"
NUC = open(os.path.join(AQUI, "eclipse_nucleo.luau"), encoding="utf-8").read().replace("\r\n", "\n").rstrip("\n")
TROCAS = {
 "src/ServerScriptService/Combate_Dragao/ConfigCombate.luau": [
  ('		Sombrio = {"Sopro", "Arremetida"}},                       -- PATCH_SOPRO_UMBRAL / PATCH_CORRENTES_NOITE (04/11): Sombrio = Sopro Umbral + Correntes',
   '		Sombrio = {"Sopro", "Arremetida", "Coracao"}},            -- PATCH_SOPRO_UMBRAL / CORRENTES_NOITE / ECLIPSE_DRACONICO (04/11): kit completo do Sombrio'),
  ('		Sombrio = {Sopro = "SoproUmbral", Arremetida = "Correntes"}},',
   '		Sombrio = {Sopro = "SoproUmbral", Arremetida = "Correntes", Coracao = "Eclipse"}},'),
  ('		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) =====',
   '		-- Eclipse Draconico (PATCH_ECLIPSE_DRACONICO): especial; concentracao -> rugido; no pico (boca aberta, ~2,15 s) a area\n'
   '		-- escurece (so visual) e DETONA as Marcas Sombrias proprias dos alvos na esfera: danoPorMarca x marcas (sem marca = 0).\n'
   '		-- escuro = s de escurecimento depois da detonacao. NAO_APROVADO\n'
   '		Eclipse = {recarga = 25, energia = 50, elemental = true, intensidade = "pesado", clipe = "Eclipse_Draconico",\n'
   '			detona = 2.15, duracao = 3.7, raio = 60, danoPorMarca = 9, escuro = 4.0},\n'
   '		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) ====='),
 ],
 "src/ServerScriptService/Combate_Dragao/Nucleo.luau": [
  ('\n-- energia\ntask.spawn(function()', '\n' + NUC + '\n\n-- energia\ntask.spawn(function()'),
 ],
 "src/ServerScriptService/Combate_Dragao/Passivas.luau": [
  ('function P.consumirMarcas(fonte, alvo)                              -- (Eclipse Draconico, futuro): devolve quantas havia\n'
   '	local n = P.marcasDe(fonte, alvo); if n > 0 then marcas[alvo][fonte] = nil; atribMarca(alvo) end; return n\nend',
   'function P.consumirMarcas(fonte, alvo)                              -- Eclipse Draconico: zera as marcas desta origem; devolve quantas havia\n'
   '	local n = P.marcasDe(fonte, alvo)\n'
   '	if n > 0 then marcas[alvo][fonte] = nil; alvo:SetAttribute("MarcaSombria_" .. fonte.Name, nil); atribMarca(alvo) end   -- PATCH_ECLIPSE_DRACONICO: limpa o atributo da origem\n'
   '	return n\nend'),
 ],
 "src/ServerScriptService/Montaria_Dragao_Servidor.server.luau": [
  ('		or ataque == "Correntes"                                                            -- PATCH_CORRENTES_NOITE (Sombrio)',
   '		or ataque == "Correntes"                                                            -- PATCH_CORRENTES_NOITE (Sombrio)\n'
   '		or ataque == "Eclipse"                                                              -- PATCH_ECLIPSE_DRACONICO (Sombrio)'),
 ],
 "src/ReplicatedStorage/Montaria_Dragoes/ConfigMontaria.luau": [
  ('			Sombrio = {Sopro = "Sopro Umbral", Arremetida = "Correntes"}},',
   '			Sombrio = {Sopro = "Sopro Umbral", Arremetida = "Correntes", Coracao = "Eclipse"}},   -- PATCH_ECLIPSE_DRACONICO'),
  ('			Sombrio = " | segure 1: Sopro Umbral | 2 Correntes da Noite (mire no chao)"},',
   '			Sombrio = " | segure 1: Sopro Umbral | 2 Correntes da Noite (mire no chao) | 4 Eclipse Dracônico"},'),
 ],
}
NOMES = {"ConfigCombate.luau": "game.ServerScriptService.Combate_Dragao.ConfigCombate",
         "Nucleo.luau": "game.ServerScriptService.Combate_Dragao.Nucleo",
         "Passivas.luau": "game.ServerScriptService.Combate_Dragao.Passivas",
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
L = ['-- patch_eclipse_draconico.luau (Studio, Edit) — Eclipse Draconico do Dragao Sombrio (3a ativa da Sombra, 04/11).',
     '-- Gerado por sombrio/gerar_patch_eclipse.py com as MESMAS trocas do src/. Tudo-ou-nada (scripts checados antes de',
     '-- trocar); backup unico ServerStorage.Backup_Eclipse_Draconico_2026-11-04. Atualiza VFXSombra; cria 2 clipes.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
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
      'local conc, rug, rugAr = pasta:FindFirstChild("Sombrio_Hab_Concentracao"), pasta:FindFirstChild("Sombrio_Rugido_Combate"), pasta:FindFirstChild("Sombrio_Rugido_Combate_Camada")',
      'assert(conc and rug and rugAr, "clipe base ausente")',
      '-- junta trechos {kfs, de, ate, deslocamento} num clipe novo (os quadros entre trechos o Roblox interpola)',
      'local function juntar(nome, partes)',
      '  local novo = Instance.new("KeyframeSequence"); novo.Name = nome; novo.Loop = false; novo.Priority = partes[1][1].Priority',
      '  for _, p in ipairs(partes) do for _, k in ipairs(p[1]:GetChildren()) do',
      '    if k:IsA("Keyframe") and k.Time >= p[2] - 1e-4 and k.Time <= p[3] + 1e-4 then local c = k:Clone(); c.Time = k.Time - p[2] + p[4]; c.Parent = novo end',
      '  end end',
      '  novo:SetAttribute("Origem", "Hab_Concentracao [0;0,9] + Rugido_Combate +1,15 s (PATCH_ECLIPSE_DRACONICO)"); return novo',
      'end',
      'if not SS:FindFirstChild("Backup_Eclipse_Draconico_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Eclipse_Draconico_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; RS.Combate_Dragoes.VFXSombra:Clone().Parent = f; f.Parent = SS end',
      'for _, v in ipairs({{"Sombrio_Eclipse_Draconico", {{conc, 0, 0.9, 0}, {rug, 0, 9, 1.15}}}, {"Sombrio_Eclipse_Draconico_Camada", {{rugAr, 0, 0, 0}, {rugAr, 0, 9, 1.15}}}}) do',
      '  local velho = pasta:FindFirstChild(v[1]); if velho then velho:Destroy() end; juntar(v[1], v[2]).Parent = pasta',
      'end',
      'for _, x in ipairs(novos) do x[1].Source = x[2] end',
      'RS.Combate_Dragoes.VFXSombra.Source = vfx',
      'return "aplicado: ConfigCombate + Nucleo + Passivas + Montaria + ConfigMontaria (" .. #novos .. ") + VFXSombra + 2 clipes; backup ServerStorage.Backup_Eclipse_Draconico_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_eclipse_draconico.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
