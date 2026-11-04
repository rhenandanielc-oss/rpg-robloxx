"""Eclipse: area escura com DANO continuo + rugido sustentado enquanto a area existe (Dragao Sombrio, 04/11; pedido do
usuario). Servidor (ConfigCombate/Nucleo): depois da detonacao das marcas, a cada tickArea s durante `escuro` s, quem
esta na esfera (raio, linha de visao) leva danoArea Sombra (como tick: multiplicador da Marca, sem marcar); o dragao fica
rugindo (clipe em laco) e so fecha a boca quando a area some; se for incapacitado, a area para. Clipes novos:
Sombrio_Eclipse_Rugido_Loop (Rugido_Combate 1,1-2,0 s, boca aberta, emenda suave) e _Fim (2,0-2,6 s), + _Camada (ar).
Cliente (VFXSombra vai inteiro): breu saindo da boca durante o rugido. Numeros NAO_APROVADO.
Aplica as trocas no src/ e gera V14/ia/patch_eclipse_area.luau (tudo-ou-nada); backup ServerStorage.Backup_Eclipse_Area_2026-11-04."""
import os
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
MARCA = "PATCH_ECLIPSE_AREA"
TROCAS = {
 "src/ServerScriptService/Combate_Dragao/ConfigCombate.luau": [
  ('			detona = 2.15, duracao = 3.7, raio = 60, danoPorMarca = 9, escuro = 4.0},',
   '			detona = 2.15, duracao = 3.7, raio = 60, danoPorMarca = 9, escuro = 4.0,\n'
   '			-- PATCH_ECLIPSE_AREA (04/11, pedido do usuario): a area escura fere quem esta dentro enquanto dura e o dragao\n'
   '			-- segue rugindo ate ela sumir (ocupado: detona + escuro + fim). NAO_APROVADO\n'
   '			danoArea = 3, tickArea = 0.5, clipeLoop = "Eclipse_Rugido_Loop", clipeFim = "Eclipse_Rugido_Fim", fimRugido = 0.6},'),
 ],
 "src/ServerScriptService/Combate_Dragao/Nucleo.luau": [
  ('	FX:FireAllClients({d = m, hab = "Eclipse", fase = "inicio", el = el, noAr = noAr, detona = def.detona, raio = def.raio})\n'
   '	self:tocar(def.clipe, noAr, {}, function() end)\n',
   '	FX:FireAllClients({d = m, hab = "Eclipse", fase = "inicio", el = el, noAr = noAr, detona = def.detona, raio = def.raio})\n'
   '	local tPrinc = self:tocar(def.clipe, noAr, {}, function() end)\n'),
  ('	m:SetAttribute("UltimoEclipse", ("alvos=%d marcas=%d raio=%d"):format(nAlvos, total, def.raio))\n'
   '	local resto = def.duracao - def.detona\n'
   '	if resto > 0 then task.wait(resto) end\n',
   '	m:SetAttribute("UltimoEclipse", ("alvos=%d marcas=%d raio=%d"):format(nAlvos, total, def.raio))\n'
   '	-- PATCH_ECLIPSE_AREA: rugido sustentado (laco com a boca aberta) e dano continuo na area enquanto ela existe\n'
   '	if not def.danoArea then local resto = def.duracao - def.detona; if resto > 0 then task.wait(resto) end; return end\n'
   '	local tLaco\n'
   '	task.delay(0.45, function()                                          -- entra no laco ainda com a boca aberta\n'
   '		if not m.Parent then return end\n'
   '		tLaco = self:tocar(def.clipeLoop, noAr, {}, function() end, true)\n'
   '		if tLaco and tPrinc then tPrinc:Stop(0.3) end\n'
   '	end)\n'
   '	local t0, ticks, feridos = os.clock(), 0, {}\n'
   '	while os.clock() - t0 < def.escuro do\n'
   '		task.wait(def.tickArea)\n'
   '		if not m.Parent or m:GetAttribute("Incapacitado") then break end            -- dragao derrubado: a area acaba\n'
   '		ticks += 1\n'
   '		for _, a in ipairs(self:alvosValidos()) do\n'
   '			if naEsfera(c, def.raio, a) and self:visivel(c, a) and N.ferir(m, a, def.danoArea * mult, el, "Eclipse", "leve", true) then\n'
   '				FX:FireAllClients({d = m, fase = "reacao", alvo = a, intensidade = "leve", el = el, tipo = "EclipseArea"})\n'
   '				feridos[a.Name] = (feridos[a.Name] or 0) + 1\n'
   '			end\n'
   '		end\n'
   '	end\n'
   '	local fr = {}; for n, k in pairs(feridos) do table.insert(fr, n .. "=" .. k) end\n'
   '	m:SetAttribute("UltimoEclipseArea", ("ticks=%d %s"):format(ticks, table.concat(fr, " ")))\n'
   '	FX:FireAllClients({d = m, hab = "Eclipse", fase = "fimRugido", el = el})\n'
   '	if m.Parent then\n'
   '		local tFim = self:tocar(def.clipeFim, noAr, {}, function() end)\n'
   '		if tLaco then tLaco:Stop(0.25) end; if tPrinc then tPrinc:Stop(0.25) end\n'
   '		task.wait(tFim and def.fimRugido or 0.1)\n'
   '	end\n'),
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
L = ['-- patch_eclipse_area.luau (Studio, Edit) — Eclipse: area escura com dano continuo + rugido sustentado (04/11).',
     '-- Gerado por sombrio/gerar_patch_eclipse_area.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico',
     '-- ServerStorage.Backup_Eclipse_Area_2026-11-04. Cria 4 clipes (laco/fim + _Camada).',
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
      'local rug, rugAr = pasta:FindFirstChild("Sombrio_Rugido_Combate"), pasta:FindFirstChild("Sombrio_Rugido_Combate_Camada")',
      'assert(rug and rugAr, "Rugido_Combate ausente")',
      '-- trecho [de, ate] do clipe; laco: repete o 1o quadro no fim (+emenda s) para a volta ser suave',
      'local function trecho(nome, base, de, ate, laco, emenda)',
      '  local novo = Instance.new("KeyframeSequence"); novo.Name = nome; novo.Loop = laco; novo.Priority = base.Priority',
      '  local primeiro',
      '  for _, k in ipairs(base:GetChildren()) do if k:IsA("Keyframe") and k.Time >= de - 1e-4 and k.Time <= ate + 1e-4 then',
      '    local c = k:Clone(); c.Time = k.Time - de; c.Parent = novo; if not primeiro or k.Time < primeiro.Time then primeiro = k end end end',
      '  if laco and primeiro then local c = primeiro:Clone(); c.Time = (ate - de) + emenda; c.Parent = novo end',
      '  novo:SetAttribute("Origem", base.Name .. (" [%.2f; %.2f]"):format(de, ate) .. " (PATCH_ECLIPSE_AREA)"); return novo',
      'end',
      'if not SS:FindFirstChild("Backup_Eclipse_Area_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Eclipse_Area_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; RS.Combate_Dragoes.VFXSombra:Clone().Parent = f; f.Parent = SS end',
      'for _, v in ipairs({{"Sombrio_Eclipse_Rugido_Loop", rug, 1.1, 2.0, true}, {"Sombrio_Eclipse_Rugido_Loop_Camada", rugAr, 1.1, 2.0, true},',
      '    {"Sombrio_Eclipse_Rugido_Fim", rug, 2.0, 2.6, false}, {"Sombrio_Eclipse_Rugido_Fim_Camada", rugAr, 2.0, 2.6, false}}) do',
      '  local velho = pasta:FindFirstChild(v[1]); if velho then velho:Destroy() end; trecho(v[1], v[2], v[3], v[4], v[5], 0.35).Parent = pasta',
      'end',
      'for _, x in ipairs(novos) do x[1].Source = x[2] end',
      'RS.Combate_Dragoes.VFXSombra.Source = vfx',
      'return "aplicado: ConfigCombate + Nucleo (" .. #novos .. ") + VFXSombra + 4 clipes; backup ServerStorage.Backup_Eclipse_Area_2026-11-04"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_eclipse_area.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
