"""Eclipse em voo (Dragao Sombrio, 04/11; pedido do usuario): decola, ruge, solta o poder no ar, segue rugindo
pairando enquanto a area dura e pousa quando o poder cessa. Troca a funcao N:_Eclipse inteira (sombrio/
eclipse_voo_nucleo.luau) e acrescenta altura/tempos ao ConfigCombate. Aplica no src/ e gera
V14/ia/patch_eclipse_voo.luau (tudo-ou-nada); backup unico ServerStorage.Backup_Eclipse_Voo_2026-11-04."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = "PATCH_ECLIPSE_VOO"
NUC = open(os.path.join(AQUI, "eclipse_voo_nucleo.luau"), encoding="utf-8").read().replace("\r\n", "\n").rstrip("\n")
nuc = open(os.path.join(RAIZ, "src/ServerScriptService/Combate_Dragao/Nucleo.luau"), encoding="utf-8").read().replace("\r\n", "\n")
if MARCA not in nuc:
    i = nuc.index("function N:_Eclipse(def, el, noAr, op)"); j = nuc.index("\n\n-- energia\n", i)
    VELHA = nuc[i:j]
else:
    VELHA = None
TROCAS = {
 "src/ServerScriptService/Combate_Dragao/ConfigCombate.luau": [
  ('			danoArea = 3, tickArea = 0.5, clipeLoop = "Eclipse_Rugido_Loop", clipeFim = "Eclipse_Rugido_Fim", fimRugido = 0.6},',
   '			danoArea = 3, tickArea = 0.5, clipeLoop = "Eclipse_Rugido_Loop", clipeFim = "Eclipse_Rugido_Fim", fimRugido = 0.6,\n'
   '			-- PATCH_ECLIPSE_VOO (04/11, pedido do usuario): decola (altura), ruge (rugir s), solta no ar e pousa (descida s)\n'
   '			altura = 24, subidaAr = 10, rugir = 1.2, descida = 1.1},'),
 ],
 "src/ServerScriptService/Combate_Dragao/Nucleo.luau": [(VELHA, NUC)] if VELHA else [],
}
NOMES = {"ConfigCombate.luau": "game.ServerScriptService.Combate_Dragao.ConfigCombate",
         "Nucleo.luau": "game.ServerScriptService.Combate_Dragao.Nucleo"}
if VELHA:
    for rel, pares in TROCAS.items():
        p = os.path.join(RAIZ, rel); s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
        for a, b in pares:
            n = s.count(a); assert n == 1, (rel, n, a[:60]); s = s.replace(a, b)
        open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok", rel)
    assert "]==]" not in NUC and "]==]" not in VELHA
    L = ['-- patch_eclipse_voo.luau (Studio, Edit) — Eclipse em voo: decola, ruge, solta, ruge pairando, pousa (04/11).',
         '-- Gerado por sombrio/gerar_patch_eclipse_voo.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico',
         '-- ServerStorage.Backup_Eclipse_Voo_2026-11-04.',
         'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
         'local SS = game:GetService("ServerStorage")',
         'local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end',
         'local novos = {}']
    for rel, pares in TROCAS.items():
        nome = rel.split("/")[-1]
        L.append('do local s = %s; local src = s.Source:gsub("\\r\\n", "\\n")' % NOMES[nome])
        L.append('  if src:find("%s", 1, true) then return "scripts ja aplicados" end' % MARCA)
        for a, b in pares:
            L.append('  src = troca(src, [==[' + a + ']==], [==[' + b + ']==])')
        L.append('  assert(loadstring(src), "%s nao compila"); table.insert(novos, {s, src}) end' % nome)
    L += ['if not SS:FindFirstChild("Backup_Eclipse_Voo_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Eclipse_Voo_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f.Parent = SS end',
          'for _, x in ipairs(novos) do x[1].Source = x[2] end',
          'return "aplicado: ConfigCombate + Nucleo (" .. #novos .. "); backup ServerStorage.Backup_Eclipse_Voo_2026-11-04"']
    open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_eclipse_voo.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("patch gerado")
else:
    print("ja aplicado no src")
