"""Passo Sombrio v2 (04/11, pedido do usuario): troca o teleporte por INVISIBILIDADE + IMPULSO de velocidade por 5 s
(dragao e cavaleiro montado). Aplica no src/ e gera V14/ia/patch_passo_sombrio_v2.luau (tudo-ou-nada; backup unico
ServerStorage.Backup_Passo_Sombrio_v2_2026-11-04):
ConfigCombate (numeros NAO_APROVADO), Nucleo (N:_PassoSombrio novo), Montaria (sai do ataque fixo; PassoBonus no chao
e no voo), Combate_Dragao_Servidor (recusa alvo invisivel), Cerebro da IA (nao percebe/encerra ameaca de invisivel),
Montaria_Cliente (trava ignora/solta invisivel), RastroBreu_Cliente (linhas somem para os outros), VFXSombra (efeito)."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = "PATCH_PASSO_SOMBRIO_V2"
def ler(n): return open(os.path.join(AQUI, n), encoding="utf-8").read().replace("\r\n", "\n")
NUC_V1, NUC_V2 = ler("passo_nucleo.luau").rstrip("\n"), ler("passo_nucleo_v2.luau").rstrip("\n")
VFX_V1, VFX_V2 = ler("passo_vfx.luau"), ler("passo_vfx_v2.luau")
INV = 'local function invisivel(x) local v = x and x:GetAttribute("PassoInvisivel"); return typeof(v) == "number" and v > workspace:GetServerTimeNow() end   -- PATCH_PASSO_SOMBRIO_V2\n'
TROCAS = {
 "src/ServerScriptService/Combate_Dragao/ConfigCombate.luau": [
  ('		-- Passo Sombrio (PATCH_PASSO_SOMBRIO): some em breu e reaparece `distancia` a frente ou `atras` do alvo travado (ate\n'
   '		-- `alcance`), sem atravessar parede; sem dano. sumir/surgir = s de cada metade. NAO_APROVADO\n'
   '		PassoSombrio = {recarga = 9, energia = 20, elemental = true, intensidade = "leve", clipe = "Hab_Investida",\n'
   '			distancia = 60, alcance = 90, atras = 18, sumir = 0.3, surgir = 0.35},\n',
   '		-- Passo Sombrio (PATCH_PASSO_SOMBRIO_V2, 04/11): dragao e cavaleiro ficam invisiveis aos outros por `duracao` s com\n'
   '		-- +`bonus` de velocidade (chao e voo); nao e invulneravel; sem dano. ativar = s ocupado na ativacao. NAO_APROVADO\n'
   '		PassoSombrio = {recarga = 20, energia = 25, elemental = true, intensidade = "leve", clipe = "Hab_Investida",\n'
   '			duracao = 5, bonus = 0.6, ativar = 0.4},\n'),
 ],
 "src/ServerScriptService/Combate_Dragao/Nucleo.luau": [(NUC_V1, NUC_V2)],
 "src/ServerScriptService/Montaria_Dragao_Servidor.server.luau": [
  ('		or ataque == "PassoSombrio"                                                         -- PATCH_PASSO_SOMBRIO (Sombrio)\n', ''),
  ('			* (1 + (m:GetAttribute("RastroBonus") or 0))                                -- PATCH_RASTRO_BREU (03/11): passiva do Sombrio',
   '			* (1 + (m:GetAttribute("RastroBonus") or 0) + (m:GetAttribute("PassoBonus") or 0))   -- PATCH_RASTRO_BREU (03/11) + PATCH_PASSO_SOMBRIO_V2'),
  ('(e.correr and Cfg.vooRapidoVel or Cfg.vooVel) * f * (1 + (m:GetAttribute("RastroBonus") or 0)) or 0   -- PATCH_RASTRO_BREU',
   '(e.correr and Cfg.vooRapidoVel or Cfg.vooVel) * f * (1 + (m:GetAttribute("RastroBonus") or 0) + (m:GetAttribute("PassoBonus") or 0)) or 0   -- PATCH_RASTRO_BREU + PATCH_PASSO_SOMBRIO_V2'),
 ],
 "src/ServerScriptService/Combate_Dragao_Servidor.server.luau": [
  ('			if rr and (rr.Position - m:GetPivot().Position).Magnitude <= 420 then\n',
   '			local inv = alvo:GetAttribute("PassoInvisivel")                   -- PATCH_PASSO_SOMBRIO_V2: invisivel nao vira alvo\n'
   '			if rr and (rr.Position - m:GetPivot().Position).Magnitude <= 420 and not (typeof(inv) == "number" and inv > workspace:GetServerTimeNow()) then\n'),
 ],
 "src/ServerScriptService/IA_Dragao/Cerebro.luau": [
  ('function raizDe(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end\n',
   'function raizDe(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end\n' + INV),
  ('		if ch and h and h.Health > 0 and raizDe(ch) then table.insert(l, ch) end\n',
   '		if ch and h and h.Health > 0 and raizDe(ch) and not invisivel(ch) then table.insert(l, ch) end\n'),
  ('	for _, m in ipairs(CollectionService:GetTagged("Invasor_Teste")) do if raizDe(m) then table.insert(l, m) end end\n',
   '	for _, m in ipairs(CollectionService:GetTagged("Invasor_Teste")) do if raizDe(m) and not invisivel(m) then table.insert(l, m) end end\n'),
  ('		if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) or (r and zonaSegura(r.Position)) or cansou then\n',
   '		if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) or (r and zonaSegura(r.Position)) or cansou\n'
   '			or invisivel(alvo) then                                          -- PATCH_PASSO_SOMBRIO_V2: sumiu em breu\n'),
  ('	local r = raizDe(alvo); if not r or zonaSegura(r.Position) then return false end\n',
   '	local r = raizDe(alvo); if not r or zonaSegura(r.Position) or invisivel(alvo) then return false end\n'),
 ],
 "src/StarterPlayer/StarterPlayerScripts/Montaria_Cliente.client.luau": [
  ('local function candidatosTrava()\n',
   INV + 'local function candidatosTrava()\n'),
  ('		if raizAlvo(md) and alvoVivo(md) then table.insert(l, md) end\n',
   '		if raizAlvo(md) and alvoVivo(md) and not invisivel(md) then table.insert(l, md) end\n'),
  ('	if not (m and r and alvoVivo(trava.alvo)) or (r.Position - m:GetPivot().Position).Magnitude > TRAVA.quebra then soltarTrava(); return nil end\n',
   '	if not (m and r and alvoVivo(trava.alvo)) or invisivel(trava.alvo) or (r.Position - m:GetPivot().Position).Magnitude > TRAVA.quebra then soltarTrava(); return nil end\n'),
 ],
 "src/StarterPlayer/StarterPlayerScripts/RastroBreu_Cliente.client.luau": [
  ('local RunService = game:GetService("RunService")\n',
   'local RunService = game:GetService("RunService")\n'
   'local lp = game:GetService("Players").LocalPlayer\n'),
  ('			if m:GetAttribute("RastroModo") then nivel = 2 elseif (m:GetAttribute("RastroCarga") or 0) > 0 then nivel = 1 end\n',
   '			if m:GetAttribute("RastroModo") then nivel = 2 elseif (m:GetAttribute("RastroCarga") or 0) > 0 then nivel = 1 end\n'
   '			local inv = m:GetAttribute("PassoInvisivel")                 -- PATCH_PASSO_SOMBRIO_V2: invisivel = sem linhas para os outros\n'
   '			if typeof(inv) == "number" and inv > workspace:GetServerTimeNow() and m:GetAttribute("DonoUserId") ~= lp.UserId then nivel = 0 end\n'),
 ],
 "src/ReplicatedStorage/Combate_Dragoes/VFXSombra.luau": [
  (VFX_V1, VFX_V2.replace("-- ===== PASSO SOMBRIO v2 (04/11)", "-- ===== PASSO SOMBRIO v2 (04/11, PATCH_PASSO_SOMBRIO_V2)")),
 ],
}
NOMES = {"ConfigCombate.luau": "game.ServerScriptService.Combate_Dragao.ConfigCombate",
         "Nucleo.luau": "game.ServerScriptService.Combate_Dragao.Nucleo",
         "Montaria_Dragao_Servidor.server.luau": "game.ServerScriptService.Montaria_Dragao_Servidor",
         "Combate_Dragao_Servidor.server.luau": "game.ServerScriptService.Combate_Dragao_Servidor",
         "Cerebro.luau": "game.ServerScriptService.IA_Dragao.Cerebro",
         "Montaria_Cliente.client.luau": "game.StarterPlayer.StarterPlayerScripts.Montaria_Cliente",
         "RastroBreu_Cliente.client.luau": "game.StarterPlayer.StarterPlayerScripts.RastroBreu_Cliente",
         "VFXSombra.luau": "game.ReplicatedStorage.Combate_Dragoes.VFXSombra"}
for rel, pares in TROCAS.items():
    p = os.path.join(RAIZ, rel)
    for tent in range(5):
        try: s = open(p, encoding="utf-8", newline="").read(); break
        except OSError: pass
    nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    if MARCA in s: print("ja aplicado", rel); continue
    for a, b in pares:
        n = s.count(a); assert n == 1, (rel, n, a[:60]); s = s.replace(a, b)
    for tent in range(5):
        try: open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); break
        except OSError: pass
    print("src ok", rel)
L = ['-- patch_passo_sombrio_v2.luau (Studio, Edit) — Passo Sombrio v2: invisivel + impulso por 5 s (04/11).',
     '-- Gerado por sombrio/gerar_patch_passo_v2.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico',
     '-- ServerStorage.Backup_Passo_Sombrio_v2_2026-11-04.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage")',
     'local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end',
     'local novos = {}']
for rel, pares in TROCAS.items():
    nome = rel.split("/")[-1]
    L.append('do local s = %s; local src = s.Source:gsub("\\r\\n", "\\n")' % NOMES[nome])
    L.append('  if src:find("%s", 1, true) then return "scripts ja aplicados" end' % MARCA)
    for a, b in pares:
        assert "]=====]" not in a + b
        L.append('  src = troca(src, [=====[' + a + ']=====], [=====[' + b + ']=====])')
    L.append('  assert(loadstring(src), "%s nao compila"); table.insert(novos, {s, src}) end' % nome)
L += ['if not SS:FindFirstChild("Backup_Passo_Sombrio_v2_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Passo_Sombrio_v2_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f.Parent = SS end',
      'for _, x in ipairs(novos) do x[1].Source = x[2] end',
      'return "aplicado: " .. #novos .. " scripts; backup ServerStorage.Backup_Passo_Sombrio_v2_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_passo_sombrio_v2.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
