"""Correntes: prisao GRADUAL + Eclipse com entrada/saida graduais (Dragao Sombrio, 04/11; pedido do usuario).
Servidor (Nucleo/ConfigCombate): ao prender, a velocidade e o pulo do alvo caem aos poucos ate 0 em `aperta` s (curva
suave), em vez de zerar no ato; tempo total preso, ticks, dano e resistencia iguais. Cliente (VFXSombra, vai inteiro).
Aplica as trocas no src/ e gera V14/ia/patch_correntes_aperta.luau com as MESMAS ancoras (tudo-ou-nada); backup unico
ServerStorage.Backup_Correntes_Aperta_2026-11-04 (Nucleo, ConfigCombate, VFXSombra antes)."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
MARCA = "PATCH_CORRENTES_APERTA"
TROCAS = {
 "src/ServerScriptService/Combate_Dragao/ConfigCombate.luau": [
  ('			duracao = 3.4, duracaoAr = 2.4, dano = 10, preso = 2.5, tick = 0.5, danoTick = 4, resistencia = 6},',
   '			duracao = 3.4, duracaoAr = 2.4, dano = 10, preso = 2.5, tick = 0.5, danoTick = 4, resistencia = 6,\n'
   '			aperta = 0.9},   -- PATCH_CORRENTES_APERTA: s ate o alvo perder TODO o movimento (cai aos poucos)'),
 ],
 "src/ServerScriptService/Combate_Dragao/Nucleo.luau": [
  ('			local p = {ate = os.clock() + def.preso, ws = h.WalkSpeed, pulo = usaJP and h.JumpPower or h.JumpHeight, usaJP = usaJP, fonte = m}\n'
   '			presos[a] = p\n'
   '			h.WalkSpeed = 0; if usaJP then h.JumpPower = 0 else h.JumpHeight = 0 end\n'
   '			a:SetAttribute("PresoCorrentes", workspace:GetServerTimeNow() + def.preso)\n'
   '			FX:FireAllClients({d = m, hab = "Correntes", fase = "prender", el = el, alvo = a, duracao = def.preso})\n',
   '			local p = {ate = os.clock() + def.preso, ws = h.WalkSpeed, pulo = usaJP and h.JumpPower or h.JumpHeight, usaJP = usaJP, fonte = m, t0 = os.clock()}\n'
   '			presos[a] = p\n'
   '			-- PATCH_CORRENTES_APERTA (04/11): as correntes apertam aos poucos; andar e pulo caem ate 0 em def.aperta s\n'
   '			local ap = def.aperta or 0\n'
   '			local function fator() if ap <= 0 then return 0 end; local x = math.clamp((os.clock() - p.t0) / ap, 0, 1); return (1 - x) ^ 2 end\n'
   '			local function apertar()\n'
   '				local k = fator(); local ws, pl = p.ws * k, p.pulo * k\n'
   '				if h.WalkSpeed > ws + 0.01 then h.WalkSpeed = ws end                -- outro script tentou soltar: continua apertando\n'
   '				if usaJP then if h.JumpPower > pl + 0.01 then h.JumpPower = pl end elseif h.JumpHeight > pl + 0.01 then h.JumpHeight = pl end\n'
   '			end\n'
   '			apertar()\n'
   '			if ap > 0 then task.spawn(function() while presos[a] == p and os.clock() - p.t0 < ap + 0.05 do RunService.Heartbeat:Wait(); if presos[a] == p then apertar() end end end) end\n'
   '			a:SetAttribute("PresoCorrentes", workspace:GetServerTimeNow() + def.preso)\n'
   '			FX:FireAllClients({d = m, hab = "Correntes", fase = "prender", el = el, alvo = a, duracao = def.preso, aperta = ap})\n'),
  ('					if h.WalkSpeed ~= 0 then h.WalkSpeed = 0 end                -- outro script tentou soltar: continua preso\n',
   '					apertar()                                                   -- PATCH_CORRENTES_APERTA (antes: WalkSpeed = 0 direto)\n'),
 ],
}
NOMES = {"ConfigCombate.luau": "game.ServerScriptService.Combate_Dragao.ConfigCombate",
         "Nucleo.luau": "game.ServerScriptService.Combate_Dragao.Nucleo"}
for rel, pares in TROCAS.items():
    p = os.path.join(RAIZ, rel); s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    if MARCA in s: print("ja aplicado", rel); continue
    for a, b in pares:
        n = s.count(a); assert n == 1, (rel, n, a[:60]); s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok", rel)
vfx = open(os.path.join(RAIZ, "src/ReplicatedStorage/Combate_Dragoes/VFXSombra.luau"), encoding="utf-8").read().replace("\r\n", "\n")
assert "]=====]" not in vfx
L = ['-- patch_correntes_aperta.luau (Studio, Edit) — Correntes com prisao gradual + Eclipse com entrada/saida graduais (04/11).',
     '-- Gerado por sombrio/gerar_patch_aperta.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico',
     '-- ServerStorage.Backup_Correntes_Aperta_2026-11-04.',
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
      'if not SS:FindFirstChild("Backup_Correntes_Aperta_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Correntes_Aperta_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; RS.Combate_Dragoes.VFXSombra:Clone().Parent = f; f.Parent = SS end',
      'for _, x in ipairs(novos) do x[1].Source = x[2] end',
      'RS.Combate_Dragoes.VFXSombra.Source = vfx',
      'return "aplicado: ConfigCombate + Nucleo (" .. #novos .. ") + VFXSombra; backup ServerStorage.Backup_Correntes_Aperta_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_correntes_aperta.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
