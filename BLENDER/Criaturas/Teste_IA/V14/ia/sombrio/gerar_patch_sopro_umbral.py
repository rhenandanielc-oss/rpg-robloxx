"""Sopro Umbral (Dragao Sombrio, 04/11) — aplica as trocas no src/ e gera V14/ia/patch_sopro_umbral.luau com as MESMAS
ancoras (tudo-ou-nada, backup unico ServerStorage.Backup_Sopro_Umbral_2026-11-04). O modulo novo VFXSombra vai do
src/ para o Studio dentro do patch. Clipes: copias dos Hab_* do Sombrio (chao, _Ar -> _Camada, _Sup = so pescoco)."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
MARCA = "PATCH_SOPRO_UMBRAL"
TROCAS = {
 "src/ServerScriptService/Combate_Dragao/ConfigCombate.luau": [
  ('	habilidadesForma = {Montanhas = {"Sopro", "Arremetida", "Tempestade", "Coracao"}, Glacial = {"Sopro", "Arremetida", "Tempestade", "Coracao"}},',
   '	habilidadesForma = {Montanhas = {"Sopro", "Arremetida", "Tempestade", "Coracao"}, Glacial = {"Sopro", "Arremetida", "Tempestade", "Coracao"},\n'
   '		Sombrio = {"Sopro"}},                                     -- PATCH_SOPRO_UMBRAL (04/11): Sombrio so com o Sopro Umbral por enquanto'),
  ('	kitForma = {Glacial = {Sopro = "SoproGlacial", Arremetida = "Rajadas", Tempestade = "ZeroAbsoluto", Coracao = "Nevasca"}},',
   '	kitForma = {Glacial = {Sopro = "SoproGlacial", Arremetida = "Rajadas", Tempestade = "ZeroAbsoluto", Coracao = "Nevasca"},\n'
   '		Sombrio = {Sopro = "SoproUmbral"}},'),
  ('		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) =====',
   '		-- ===== KIT DA SOMBRA (Dragao Sombrio, definido pelo usuario em 03/11; numeros NAO_APROVADO) =====\n'
   '		-- Sopro Umbral: jato continuo de nevoa negra-violeta (mesma mecanica do sopro segurado), dano Sombra por pulso\n'
   '		-- (com o multiplicador da Marca Sombria); cada alvo ganha no maximo 1 marca por marcaIntervalo s de jato.\n'
   '		-- Vinheta leve na tela do jogador atingido: so visual (VFXSombra)\n'
   '		SoproUmbral = {recarga = 10, energia = 25, emissao = 1.8, tick = 0.3, elemental = true, emissaoMax = 5, energiaSeg = 8,\n'
   '			emAtaque = "Sopro", clipes = "Sopro_Umbral", marcaIntervalo = 1.0,\n'
   '			porElemento = {Sombra = {forma = "cone", alcance = 95, angulo = 13, dano = 5}}},\n'
   '		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) ====='),
 ],
 "src/ServerScriptService/Combate_Dragao/Passivas.luau": [
  ('function P.aplicarMarca(fonte, alvo)',
   'P.intervaloMarca = {}                                              -- PATCH_SOPRO_UMBRAL: [fonte] = s, enquanto um jato continuo dura\n'
   'function P.aplicarMarca(fonte, alvo)'),
  ('	e.n = math.min(M_.max, e.n + 1); e.ultimo = os.clock(); e.prox = nil',
   '	local iv = P.intervaloMarca[fonte]                              -- jato continuo: no maximo 1 marca por intervalo (renova a duracao)\n'
   '	if iv and e.marcou and os.clock() - e.marcou < iv then e.ultimo = os.clock(); e.prox = nil; return false end\n'
   '	e.n = math.min(M_.max, e.n + 1); e.ultimo = os.clock(); e.prox = nil; e.marcou = os.clock()'),
 ],
 "src/ServerScriptService/Combate_Dragao/Nucleo.luau": [
  ('function N:_SoproGlacial(def, el, noAr, op) return self:_Sopro(def, "Gelo", noAr, op) end',
   'function N:_SoproGlacial(def, el, noAr, op) return self:_Sopro(def, "Gelo", noAr, op) end\n'
   '-- PATCH_SOPRO_UMBRAL (04/11): Sopro Umbral (Sombrio) = mesmo jato segurado com elemento Sombra; cada pulso causa dano\n'
   '-- (com o multiplicador da Marca), mas o mesmo alvo ganha no maximo 1 marca por marcaIntervalo\n'
   'function N:_SoproUmbral(def, el, noAr, op)\n'
   '	Passivas.intervaloMarca[self.m] = def.marcaIntervalo\n'
   '	local ok, err = pcall(self._Sopro, self, def, "Sombra", noAr, op)\n'
   '	Passivas.intervaloMarca[self.m] = nil\n'
   '	if not ok then error(err, 0) end\n'
   'end'),
 ],
 "src/ReplicatedStorage/Combate_Dragoes/VFXCombate.luau": [
  ('	if d.fase == "reacao" then reacao(d.alvo, el, d.intensidade); return end',
   '	-- PATCH_SOPRO_UMBRAL (04/11): Sombra (Dragao Sombrio) no modulo proprio; o que ele nao trata segue no perfil Neutro\n'
   '	if el == "Sombra" then\n'
   '		local VS = script.Parent:FindFirstChild("VFXSombra")\n'
   '		if VS and require(VS).evento(d, f) then return end\n'
   '		el = "Neutro"; P = PERFIL.Neutro\n'
   '	end\n'
   '	if d.fase == "reacao" then reacao(d.alvo, el, d.intensidade); return end'),
 ],
}
NOMES = {"ConfigCombate.luau": "game.ServerScriptService.Combate_Dragao.ConfigCombate",
         "Passivas.luau": "game.ServerScriptService.Combate_Dragao.Passivas",
         "Nucleo.luau": "game.ServerScriptService.Combate_Dragao.Nucleo",
         "VFXCombate.luau": "game.ReplicatedStorage.Combate_Dragoes.VFXCombate"}
# 1) src
for rel, pares in TROCAS.items():
    p = os.path.join(RAIZ, rel); s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    if MARCA in s: print("ja aplicado", rel); continue
    for a, b in pares:
        n = s.count(a); assert n == 1, (rel, n, a[:60]); s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok", rel)
vfx = open(os.path.join(RAIZ, "src/ReplicatedStorage/Combate_Dragoes/VFXSombra.luau"), encoding="utf-8").read().replace("\r\n", "\n")
assert "]=====]" not in vfx
# 2) patch Luau
L = ['-- patch_sopro_umbral.luau (Studio, Edit) — Sopro Umbral do Dragao Sombrio (1a ativa do kit de Sombra, 04/11).',
     '-- Gerado por sombrio/gerar_patch_sopro_umbral.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico',
     '-- ServerStorage.Backup_Sopro_Umbral_2026-11-04 (scripts antes da troca). Cria: VFXSombra e 9 clipes Sombrio_Sopro_Umbral_*.',
     'local RS, SS = game:GetService("ReplicatedStorage"), game:GetService("ServerStorage")',
     'local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end',
     '-- clipes (sempre recriados): chao, _Camada (versao _Ar) e _Sup (so pescoco/cabeca/mandibula, como a Mordida_Sup)',
     'local pasta = RS.Animacoes_Sombrio',
     'local SUP = {Pescoco2 = true, spine_3 = true, Pescoco4 = true, Cabeca = true, Mandibula = true, mouth_upper = true, mouth_upper_tip = true, mouth_lower_tip = true}',
     'local MAPA = {Inicio = "Hab_Preparo_Respiratorio", Loop = "Hab_Emissao_Loop", Fim = "Hab_Emissao_Fim"}',
     'for fase, base in pairs(MAPA) do',
     '  local chao, ar = pasta:FindFirstChild("Sombrio_" .. base), pasta:FindFirstChild("Sombrio_" .. base .. "_Ar")',
     '  assert(chao and ar, "clipe base ausente: " .. base)',
     '  for _, v in ipairs({{chao, ""}, {ar, "_Camada"}, {chao, "_Sup"}}) do',
     '    local nome = "Sombrio_Sopro_Umbral_" .. fase .. v[2]; local velho = pasta:FindFirstChild(nome); if velho then velho:Destroy() end',
     '    local c = v[1]:Clone(); c.Name = nome; c.Loop = fase == "Loop"',
     '    if v[2] == "_Sup" then for _, p in ipairs(c:GetDescendants()) do if p:IsA("Pose") and not SUP[p.Name] then p.Weight = 0 end end; c:SetAttribute("Parcial", "pescoco/cabeca/mandibula") end',
     '    c:SetAttribute("Origem", v[1].Name); c.Parent = pasta',
     '  end',
     'end',
     'local novos = {}']
for rel, pares in TROCAS.items():
    nome = rel.split("/")[-1]
    L.append('do local s = %s; local src = s.Source:gsub("\\r\\n", "\\n")' % NOMES[nome])
    L.append('  if src:find("%s", 1, true) then return "clipes recriados | scripts ja aplicados" end' % MARCA)
    for a, b in pares:
        L.append('  src = troca(src, [==[' + a + ']==], [==[' + b + ']==])')
    L.append('  assert(loadstring(src), "%s nao compila"); table.insert(novos, {s, src}) end' % nome)
L += ['local vfx = [=====[' + "\n" + vfx + ']=====]',   # a 1a quebra de linha apos [=====[ e descartada pelo Lua
      'assert(loadstring(vfx), "VFXSombra nao compila")',
      'if not SS:FindFirstChild("Backup_Sopro_Umbral_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Sopro_Umbral_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f.Parent = SS end',
      'for _, x in ipairs(novos) do x[1].Source = x[2] end',
      'local VS = RS.Combate_Dragoes:FindFirstChild("VFXSombra") or Instance.new("ModuleScript"); VS.Name = "VFXSombra"; VS.Source = vfx; VS.Parent = RS.Combate_Dragoes',
      'return "aplicado: ConfigCombate + Passivas + Nucleo + VFXCombate (" .. #novos .. ") + VFXSombra + 9 clipes; backup ServerStorage.Backup_Sopro_Umbral_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_sopro_umbral.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
