"""Fumaca residual v3 (meio-termo pedido apos ver o v2, que virou nuvem preta maior que a cabeca): cinza-carvao mais claro,
alfa 0,45, 1,4x taxa, 1,1x tamanho, 12 brasas. No Studio, se o v2 estiver aplicado, volta antes ao v1 pelo backup do v2.
--- texto do v2 ---
Fumaca residual v2: Fogo mais forte (05/11, usuario: "Reforcar o Fogo"). No v1 a fumaca cinza do Fogo ficava discreta
atras do resto claro do VFXFogo. Agora: cinza mais escuro e mais opaco, ~1,9x a taxa, 1,35x o tamanho, vida maior e o
dobro de brasas. Os outros elementos nao mudam (taxa/tam/vida sao opcionais por elemento, padrao 1).
Edita o src/ e gera V14/ia/patch_fumaca_fogo_v3.luau (exige o v1 aplicado; backup unico Backup_Fumaca_Fogo_v3_2026-11-05)."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
MARCA = "PATCH_FUMACA_FOGO_V3"
P = os.path.join(RAIZ, "src/ReplicatedStorage/Combate_Dragoes/VFXCombate.luau")
TROCAS = [
    ('\tFogo = {cor = {C3(96, 86, 80), C3(52, 49, 48)}, luzI = 1, sobe = 2.2, alfa = 0.55, tex = FB.fumaca, brasa = C3(255, 150, 60)},\n',
     '\tFogo = {cor = {C3(104, 96, 90), C3(62, 59, 58)}, luzI = 1, sobe = 2.4, alfa = 0.45, tex = FB.fumaca, brasa = C3(255, 150, 60),   -- PATCH_FUMACA_FOGO_V3\n'
     '\t\ttaxa = 1.4, tam = 1.1, vida = 2.2, brasas = 12},\n'),
    ('\t\tlocal t = table.clone(base)\n',
     '\t\tlocal t = table.clone(base); tam = tam * (R.tam or 1); taxa = taxa * (R.taxa or 1)\n'),
    ('\t\tt.Lifetime = NumberRange.new(1.1, 1.9);',
     '\t\tt.Lifetime = NumberRange.new(1.1, R.vida or 1.9);'),
    ('EmissionDirection = Enum.NormalId.Front, Rate = 7 * f}))\n',
     'EmissionDirection = Enum.NormalId.Front, Rate = (R.brasas or 7) * f}))\n'),
]
s = open(P, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
assert "PATCH_FUMACA_RESIDUAL" in s, "v1 nao esta no src"
if MARCA not in s:
    for a, b in TROCAS:
        assert s.count(a) == 1, a[:60]; s = s.replace(a, b)
    open(P, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok VFXCombate", len(s.encode()), "bytes", s.count("\n"), "linhas")
else:
    print("src ja tinha a marca")
L = ['-- patch_fumaca_fogo_v3.luau (Studio, Edit) — fumaca residual do Fogo reforcada (05/11). Gerado por sombrio/gerar_patch_fumaca_fogo_v3.py.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage"); local V = game:GetService("ReplicatedStorage").Combate_Dragoes.VFXCombate',
     'local src = V.Source:gsub("\\r\\n", "\\n")',
     'if src:find("%s", 1, true) then return "ja aplicado" end' % MARCA,
     'if src:find("PATCH_FUMACA_FOGO_V2", 1, true) then local bk = SS:FindFirstChild("Backup_Fumaca_Fogo_v2_2026-11-05"); assert(bk, "sem backup do v2"); src = bk.VFXCombate.Source:gsub("\\r\\n", "\\n") end   -- volta ao v1',
     'assert(src:find("PATCH_FUMACA_RESIDUAL", 1, true), "aplique antes o patch_fumaca_residual.luau")']
for i, (a, b) in enumerate(TROCAS):
    assert "]======]" not in a + b
    L += ['do local a, b = [======[' + a + ']======], [======[' + b + ']======]',
          '\tlocal i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora %d")' % (i + 1),
          '\tsrc = src:sub(1, i - 1) .. b .. src:sub(j + 1) end']
L += ['assert(loadstring(src), "VFXCombate nao compila")',
      'if not SS:FindFirstChild("Backup_Fumaca_Fogo_v3_2026-11-05") then local f = Instance.new("Folder"); f.Name = "Backup_Fumaca_Fogo_v3_2026-11-05"; V:Clone().Parent = f; f.Parent = SS end',
      'V.Source = src',
      'local _, n = src:gsub("\\n", "")',
      'return "aplicado: VFXCombate " .. #src .. " bytes / " .. n .. " linhas"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_fumaca_fogo_v3.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
