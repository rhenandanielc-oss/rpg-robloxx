"""Patch POR DIFERENCA da montaria nova (06/11), para aplicar sem o servidor HTTP local (o Studio recusou 127.0.0.1:8766 na
Assistant HTTP allowlist). Para cada script: confere tamanho/linhas iguais ao git HEAD, troca so os trechos que mudaram
(ancoras unicas com contexto) e confere tamanho/linhas iguais ao src/ no fim; cria o AnimCavaleiro. Tudo-ou-nada; backup
unico ServerStorage.Backup_Anim_Cavaleiro_2026-11-06. Gera V14/ia/patch_montaria_diff.luau."""
import os, subprocess, difflib
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
ARQS = [("src/ServerScriptService/Montaria_Dragao_Servidor.server.luau", 'game:GetService("ServerScriptService").Montaria_Dragao_Servidor'),
        ("src/ReplicatedStorage/Montaria_Dragoes/ConfigMontaria.luau", 'game:GetService("ReplicatedStorage").Montaria_Dragoes.ConfigMontaria')]
NOVO = "src/ReplicatedStorage/Montaria_Dragoes/AnimCavaleiro.luau"
def ler(p): return open(os.path.join(RAIZ, p), encoding="utf-8", newline="").read().replace("\r\n", "\n")
def head(p): return subprocess.run(["git", "-C", RAIZ, "show", "HEAD:" + p], capture_output=True, check=True).stdout.decode("utf-8").replace("\r\n", "\n")
def medida(s): return len(s.encode("utf-8")), s.count("\n")
def trocas(velho, novo):
    a, b = velho.split("\n"), novo.split("\n"); out = []
    ops = [o for o in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if o[0] != "equal"]
    grupos = []                                   # junta trechos proximos (as ancoras com contexto nao podem se sobrepor)
    for o in ops:
        if grupos and o[1] - grupos[-1][2] <= 12: grupos[-1] = ("replace", grupos[-1][1], o[2], grupos[-1][3], o[4])
        else: grupos.append(o)
    for tag, i1, i2, j1, j2 in grupos:
        c = 2
        while True:
            lo, hi = max(0, i1 - c), min(len(a), i2 + c)
            old = "\n".join(a[lo:hi]); new = "\n".join(a[lo:i1] + b[j1:j2] + a[i2:hi])
            if velho.count(old) == 1 or c > 40: break
            c += 2
        assert velho.count(old) == 1, "ancora nao unica"
        out.append((old, new))
    return out
L = ['-- patch_montaria_diff.luau (Studio, Edit) — montaria nova por diferenca (06/11). Gerado por sombrio/gerar_patch_montaria_diff.py.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage"); local P = game:GetService("ReplicatedStorage").Montaria_Dragoes',
     'local function med(s) local _, n = s:gsub("\\n", ""); return #s, n end',
     'local feitos = {}']
for p, caminho in ARQS:
    v, n = head(p), ler(p); tv, tn = medida(v), medida(n)
    tr = trocas(v, n)
    for o, w in tr: assert "]======]" not in o + w
    L += ['do local s = %s; local src = s.Source:gsub("\\r\\n", "\\n")' % caminho,
          '\tlocal b0, l0 = med(src); assert(b0 == %d and l0 == %d, "%s no Studio difere do git HEAD (" .. b0 .. "/" .. l0 .. "): nao troco")' % (tv[0], tv[1], os.path.basename(p))]
    for o, w in tr:
        L += ['\tdo local a, b = [======[' + o + ']======], [======[' + w + ']======]',
              '\t\tlocal i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora")',
              '\t\tsrc = src:sub(1, i - 1) .. b .. src:sub(j + 1) end']
    L += ['\tlocal b1, l1 = med(src); assert(b1 == %d and l1 == %d, "%s: resultado difere do src (" .. b1 .. "/" .. l1 .. ")")' % (tn[0], tn[1], os.path.basename(p)),
          '\tassert(loadstring(src), "%s nao compila"); table.insert(feitos, {s, src}) end' % os.path.basename(p)]
mod = ler(NOVO); assert "]======]" not in mod
L += ['local mod = [======[' + mod + ']======]', 'assert(loadstring(mod), "AnimCavaleiro nao compila")',
      'if not SS:FindFirstChild("Backup_Anim_Cavaleiro_2026-11-06") then local f = Instance.new("Folder"); f.Name = "Backup_Anim_Cavaleiro_2026-11-06"; for _, t in ipairs(feitos) do t[1]:Clone().Parent = f end; f.Parent = SS end',
      'for _, t in ipairs(feitos) do t[1].Source = t[2] end',
      'local Mo = P:FindFirstChild("AnimCavaleiro") or Instance.new("ModuleScript"); Mo.Name = "AnimCavaleiro"; Mo.Source = mod; Mo.Parent = P',
      'local r = {}; for _, t in ipairs(feitos) do local b, n = med(t[2]); table.insert(r, t[1].Name .. " " .. b .. "/" .. n) end',
      'return "aplicado: " .. table.concat(r, ", ") .. "; AnimCavaleiro " .. #mod .. " bytes"']
saida = os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_montaria_diff.luau")
open(saida, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("patch gerado", os.path.getsize(saida), "bytes")
