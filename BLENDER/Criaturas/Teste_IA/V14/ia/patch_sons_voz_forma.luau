-- patch_sons_voz_forma.luau (Studio, modo Edit) — sistema universal de animacoes (01/11): VOZ por forma regional e
-- vozes dos clipes novos. Mesmo audio licenciado (Pro Sound Effects); so muda o TOM e quando toca.
--  1) atributo TomVoz no modelo multiplica o tom de rugidos, rosnados e respiracao (Glacial 0,8 = grave e contido;
--     sem atributo = 1, o Dragao das Montanhas nao muda);
--  2) vozes dos clipes novos: Rugido_Territorial (rugido longo no pico), Intimidar (rosnado nos grunhidos, com chance),
--     Curiosidade (fungada curta), Dano_Forte/_Ar (gemido de esforco); o intervalo minimo por dragao continua valendo.
local SP, SS = game:GetService("StarterPlayer"), game:GetService("ServerStorage")
local alvos = {SC = SP.StarterPlayerScripts.SonsDragao_Cliente}
if alvos.SC.Source:find("PATCH_VOZ_FORMA", 1, true) then return "ja aplicado" end
local novo = {}; for k, s in pairs(alvos) do novo[k] = s.Source:gsub("\r\n", "\n") end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true); assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end
troca("SC", [=[	Comer = {{0.1, "mordida", 1, 0.7, 0.8}, {0.433, "mordida", 1, 0.7, 0.8}, {0.766, "mordida", 1, 0.7, 0.8}},
}]=], [=[	Comer = {{0.1, "mordida", 1, 0.7, 0.8}, {0.433, "mordida", 1, 0.7, 0.8}, {0.766, "mordida", 1, 0.7, 0.8}},
	-- PATCH_VOZ_FORMA (01/11): clipes do sistema universal
	Rugido_Territorial = {{0.3, "rugido", 1, 1.2, 0.85}}, Intimidar = {{0.2, "esforco", 0.6, 0.7, 0.75}, {0.7, "esforco", 0.6, 0.7, 0.75}},
	Curiosidade = {{0.45, "respiro", 0.8, 0.5, 0.9}}, Dano_Forte = {{0.05, "esforco", 1, 0.8, 0.95}}, Dano_Forte_Ar = {{0.05, "esforco", 1, 0.8, 0.95}},
}]=])
troca("SC", [=[local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end]=],
	[=[local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end
-- PATCH_VOZ_FORMA: tom de voz da forma regional (atributo TomVoz no modelo; 1 = padrao)
local function tomVoz(pai) local mm = pai and pai:FindFirstAncestorWhichIsA("Model"); return (mm and mm:GetAttribute("TomVoz")) or 1 end]=])
troca("SC", [=[				tocar(pp, sorteia(Cfg[k]), ev[4], ev[5] * (0.95 + math.random() * 0.1), k == "esforco" and 1.2 or nil)]=],
	[=[				tocar(pp, sorteia(Cfg[k]), ev[4], ev[5] * (0.95 + math.random() * 0.1) * tomVoz(pp), k == "esforco" and 1.2 or nil)]=])
troca("SC", [=[				tocar(pp, Cfg.respiro, Cfg.respiroVolume * (cansado and 1.4 or 1), faixa(Cfg.respiroTom), 1.8)]=],
	[=[				tocar(pp, Cfg.respiro, Cfg.respiroVolume * (cansado and 1.4 or 1), faixa(Cfg.respiroTom) * tomVoz(pp), 1.8)]=])
troca("SC", [=[		elseif h == "Rugido" and f == "emissao" then tocar(pp, Cfg.rugido, 1.5, 0.95) end]=],
	[=[		elseif h == "Rugido" and f == "emissao" then tocar(pp, Cfg.rugido, 1.5, 0.95 * tomVoz(pp)) end]=])
for k in pairs(alvos) do local f, e = loadstring(novo[k]); assert(f, k .. " nao compila: " .. tostring(e)) end
local bk = SS:FindFirstChild("Backup_Sons_Voz_2026-11-02")
if not bk then
	bk = Instance.new("Folder"); bk.Name = "Backup_Sons_Voz_2026-11-02"
	for k, s in pairs(alvos) do local c = s:Clone(); c.Name = k .. "__" .. s.Name; c.Enabled = false; c.Parent = bk end
	bk.Parent = SS
end
for k, s in pairs(alvos) do s.Source = novo[k] end
local g = workspace:FindFirstChild("Glacial"); if g then g:SetAttribute("TomVoz", 0.8) end
local gg = workspace:FindFirstChild("Glacial_Guardiao"); if gg then gg:SetAttribute("TomVoz", 0.8) end
return "aplicado"
