"""Correntes prendem alvos no AR + Eclipse no ar longe do chao (Dragao Sombrio, 04/11; pedido do usuario).
- Nucleo: bloco das Correntes trocado por sombrio/correntes_ar_nucleo.luau (selecao 3D, AlignPosition em personagem no
  ar, PresoFator em dragao/guardiao); _Eclipse: centro da area = chao sob o dragao se houver chao a ate `pertoChao`
  studs, senao em volta do corpo no ar (FX ar = true).
- Locomotor (IA) e Montaria: o movimento de um dragao com PresoFator e multiplicado pelo fator (freia ate parar).
- ConfigCombate: Eclipse.pertoChao = 40. VFXSombra vai inteiro.
Aplica no src/ e gera V14/ia/patch_correntes_eclipse_ar.luau (tudo-ou-nada); backup ServerStorage.Backup_Correntes_Eclipse_Ar_2026-11-04."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = "PATCH_CORRENTES_AR"
NOVO = open(os.path.join(AQUI, "correntes_ar_nucleo.luau"), encoding="utf-8").read().replace("\r\n", "\n").rstrip("\n")
nuc = open(os.path.join(RAIZ, "src/ServerScriptService/Combate_Dragao/Nucleo.luau"), encoding="utf-8").read().replace("\r\n", "\n")
TROCAS = {}
if MARCA not in nuc:
    i = nuc.index("local presos, resistente = {}, {}"); j = nuc.index("\n\n-- Rajadas de Gelo", i)
    VELHO = nuc[i:j]
    TROCAS = {
     "src/ServerScriptService/Combate_Dragao/Nucleo.luau": [
      (VELHO, NOVO),
      ('	local c = self:centroCorpo() - Vector3.new(0, yAtual, 0)                 -- area no chao sob o dragao\n'
       '	FX:FireAllClients({d = m, hab = "Eclipse", fase = "detonar", el = el, pos = c, raio = def.raio, duracao = def.escuro})\n',
       '	-- PATCH_CORRENTES_AR / ECLIPSE no ar: com chao ate pertoChao abaixo -> area no chao; senao, em volta do corpo no ar\n'
       '	local cc = self:centroCorpo(); local vfxF = workspace:FindFirstChild("VFX_Temporarios")\n'
       '	local gE = chaoAbaixo(cc - Vector3.new(0, yAtual, 0), {m, vfxF}, def.pertoChao or 40)\n'
       '	local c = gE and (gE + Vector3.new(0, 3, 0)) or cc\n'
       '	FX:FireAllClients({d = m, hab = "Eclipse", fase = "detonar", el = el, pos = c, raio = def.raio, duracao = def.escuro, ar = gE == nil})\n'),
     ],
     "src/ServerScriptService/Combate_Dragao/ConfigCombate.luau": [
      ('			altura = 24, subidaAr = 10, rugir = 1.2, descida = 1.1},',
       '			altura = 24, subidaAr = 10, rugir = 1.2, descida = 1.1,\n'
       '			pertoChao = 40},   -- PATCH_CORRENTES_AR: mais alto que isto, a area do Eclipse fica em volta do dragao no ar'),
     ],
     "src/ServerScriptService/IA_Dragao/Locomotor.luau": [
      ('	if self.m:GetAttribute("EmAtaque") == "Arremetida" or self.m:GetAttribute("CorpoElevado") then return end   -- o combate move o corpo\n',
       '	if self.m:GetAttribute("EmAtaque") == "Arremetida" or self.m:GetAttribute("CorpoElevado") then return end   -- o combate move o corpo\n'
       '	local pf = self.m:GetAttribute("PresoFator")                           -- PATCH_CORRENTES_AR: preso pelas Correntes da Noite\n'
       '	if pf then local atual = self:pos(); pos = atual + (pos - atual) * math.clamp(pf, 0, 1) end\n'),
     ],
     "src/ServerScriptService/Montaria_Dragao_Servidor.server.luau": [
      ('local function aplicar(M, pos)\n	local L = M.L\n',
       'local function aplicar(M, pos)\n	local L = M.L\n'
       '	local pf = M.m:GetAttribute("PresoFator")                               -- PATCH_CORRENTES_AR: preso pelas Correntes da Noite\n'
       '	if pf then local atual = L:pos(); pos = atual + (pos - atual) * math.clamp(pf, 0, 1) end\n'),
     ],
    }
NOMES = {"ConfigCombate.luau": "game.ServerScriptService.Combate_Dragao.ConfigCombate",
         "Nucleo.luau": "game.ServerScriptService.Combate_Dragao.Nucleo",
         "Locomotor.luau": "game.ServerScriptService.IA_Dragao.Locomotor",
         "Montaria_Dragao_Servidor.server.luau": "game.ServerScriptService.Montaria_Dragao_Servidor"}
for rel, pares in TROCAS.items():
    p = os.path.join(RAIZ, rel); s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    for a, b in pares:
        n = s.count(a); assert n == 1, (rel, n, a[:60]); s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok", rel)
if not TROCAS: print("src ja aplicado"); raise SystemExit
vfx = open(os.path.join(RAIZ, "src/ReplicatedStorage/Combate_Dragoes/VFXSombra.luau"), encoding="utf-8").read().replace("\r\n", "\n")
assert "]=====]" not in vfx and all("]==]" not in a + b for pr in TROCAS.values() for a, b in pr)
L = ['-- patch_correntes_eclipse_ar.luau (Studio, Edit) — Correntes prendem no ar + Eclipse no ar longe do chao (04/11).',
     '-- Gerado por sombrio/gerar_patch_ar.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico',
     '-- ServerStorage.Backup_Correntes_Eclipse_Ar_2026-11-04.',
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
      'if not SS:FindFirstChild("Backup_Correntes_Eclipse_Ar_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Correntes_Eclipse_Ar_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; RS.Combate_Dragoes.VFXSombra:Clone().Parent = f; f.Parent = SS end',
      'for _, x in ipairs(novos) do x[1].Source = x[2] end',
      'RS.Combate_Dragoes.VFXSombra.Source = vfx',
      'return "aplicado: Nucleo + ConfigCombate + Locomotor + Montaria (" .. #novos .. ") + VFXSombra; backup ServerStorage.Backup_Correntes_Eclipse_Ar_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_correntes_eclipse_ar.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
