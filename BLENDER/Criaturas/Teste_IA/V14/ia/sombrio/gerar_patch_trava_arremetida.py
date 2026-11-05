"""Trava de alvo: a ARREMETIDA montada persegue o alvo travado (04/11; achado no teste do Silverwing: a investida e
dirigida pela montaria/camera e ignorava o alvo). Com alvo travado e EmAtaque == "Arremetida", o cliente envia o rumo
(cy) e a inclinacao (cp) da direcao dragao -> alvo e um avanco minimo (no chao a investida so vira com W). So o
Montaria_Cliente muda. Aplica no src/ e gera V14/ia/patch_trava_arremetida.luau; backup ServerStorage.Backup_Trava_Arremetida_2026-11-04."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
MARCA = "PATCH_TRAVA_ARREMETIDA"
A = "\t\tif not (orbAtivo or stick or not UIS.MouseEnabled) then cy, cp = nil, 0 end\n\t\tEntrada:FireServer({f = -mv.Z, t = mv.X, "
B = ("\t\tif not (orbAtivo or stick or not UIS.MouseEnabled) then cy, cp = nil, 0 end\n"
     "\t\tlocal fAv = -mv.Z\n"
     "\t\tlocal tA = travaAtual()                                         -- PATCH_TRAVA_ARREMETIDA: a investida persegue o alvo travado\n"
     "\t\tif tA and m:GetAttribute(\"EmAtaque\") == \"Arremetida\" then\n"
     "\t\t\tlocal v = tA.raiz.Position - m:GetPivot().Position\n"
     "\t\t\tif v.Magnitude > 2 then v = v.Unit; cy = math.atan2(v.X, v.Z); cp = math.asin(math.clamp(v.Y, -1, 1)); fAv = math.max(fAv, 0.3) end\n"
     "\t\tend\n"
     "\t\tEntrada:FireServer({f = fAv, t = mv.X, ")
p = os.path.join(RAIZ, "src/StarterPlayer/StarterPlayerScripts/Montaria_Cliente.client.luau")
s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
if MARCA not in s:
    assert s.count(A) == 1, s.count(A); s = s.replace(A, B)
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok")
L = ['-- patch_trava_arremetida.luau (Studio, Edit) — a Arremetida montada persegue o alvo travado (04/11).',
     '-- Gerado por sombrio/gerar_patch_trava_arremetida.py; backup unico ServerStorage.Backup_Trava_Arremetida_2026-11-04.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage"); local S = game:GetService("StarterPlayer").StarterPlayerScripts.Montaria_Cliente',
     'local src = S.Source:gsub("\\r\\n", "\\n")',
     'if src:find("%s", 1, true) then return "ja aplicado" end' % MARCA,
     'local a, b = [==[' + A + ']==], [==[' + B + ']==]',
     'local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora")',
     'src = src:sub(1, i - 1) .. b .. src:sub(j + 1); assert(loadstring(src), "nao compila")',
     'if not SS:FindFirstChild("Backup_Trava_Arremetida_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Trava_Arremetida_2026-11-04"; S:Clone().Parent = f; f.Parent = SS end',
     'S.Source = src',
     'return "aplicado: Montaria_Cliente (" .. #src .. " bytes)"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_trava_arremetida.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
