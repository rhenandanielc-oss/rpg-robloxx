-- patch_ia_margem.luau (Studio, modo Edit) — complemento do patch_ia_selvagem (30/10), achado no teste em Play:
-- o guardiao ia ao ponto "Agua" vindo do lado do lago e bebia DE COSTAS para a agua, com a cauda dentro dela.
-- Agora: acha a agua real (voxels Water) perto do ponto, para em terra firme de FRENTE para ela, boca na beira.
-- Tudo-ou-nada; original fica em ServerStorage.Backup_Scripts_IA_Selvagem (do patch anterior) e Backup_IA_Margem.
local SSS, SS = game:GetService("ServerScriptService"), game:GetService("ServerStorage")
local s = SSS.IA_Dragao.Cerebro
local src = s.Source
if src:find("PATCH_IA_MARGEM", 1, true) then return "ja aplicado" end
local function troca(a, b)
	local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a)
	assert(not string.find(src, a, j + 1, true), "trecho repetido: " .. a)
	src = src:sub(1, i - 1) .. b .. src:sub(j + 1)
end
troca([=[function C:_SearchWater(vivo)]=], [=[function C:_SearchWater_antigo(vivo)          -- substituida (PATCH_IA_MARGEM)]=])
troca([=[function C:_SearchFood(vivo)]=], [=[-- PATCH_IA_MARGEM: BEBER NA MARGEM — acha a agua real (voxels Water) perto do ponto, fica em terra firme de FRENTE
-- para a agua, boca na beira (antes parava no ponto vindo do lado do lago: cauda na agua, de costas para ela).
-- Sem agua perto do ponto: fonte inacessivel, registra e desiste (sem ficar tentando).
function C:margem(poi)
	self.margens = self.margens or {}
	if self.margens[poi] ~= nil then return self.margens[poi] or nil end
	local T = workspace.Terrain; local c = poi.Position; local achou
	for r = 4, 96, 6 do
		for k = 0, 23 do
			local a = k / 24 * 2 * math.pi
			local p = c + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r)
			local m = T:ReadVoxels(Region3.new(p - Vector3.new(2, 6, 2), p + Vector3.new(2, 14, 2)):ExpandToGrid(4), 4)
			for y = 1, m.Size.Y do if m[1][y][1] == Enum.Material.Water then achou = p; break end end
			if achou then break end
		end
		if achou then break end
	end
	self.margens[poi] = achou or false
	return achou
end
function C:_SearchWater(vivo)
	if not self:emPe(vivo) then return end
	local poi = self:poi("Agua"); if not poi then return end
	local agua = self:margem(poi)
	if not agua then self:registrar("agua inacessivel perto de " .. poi.Name); self.sede = 0.5; return end
	local w = plano(agua - poi.Position); w = w.Magnitude > 0.5 and w.Unit or plano(agua - self.L:pos()).Unit
	local beira = agua - w * 3                                         -- ultimo trecho seco antes da agua
	local destino = beira - w * (self.L.distBoca - 4)                  -- corpo em terra, boca na beira
	self.destino = destino
	local ok = self:ir(destino, false, vivo, 6); if not ok or not vivo() then return end
	self.L:virarPara(agua + w * 20, vivo)
	self:definir("Drink"); if self:comportamento("BeberAgua", 9.5, vivo) then self.sede = 0 end
end

function C:_SearchFood(vivo)]=])
-- sono: ja deitado perto do ninho (ex.: descansando nele) adormece ali mesmo, sem levantar e deitar de novo
troca([=[function C:_Sleep(vivo)]=], [=[function C:_Sleep(vivo)
	if self.E.postura == "deitado" and plano(self.L:pos() - self.casa).Magnitude < 60 then
		self:definir("Sleep"); if self:comportamento("Sono", 45, vivo) then self.sono = 0; self:comportamento("Despertar", 5, vivo) end
		return
	end]=])
if not SS:FindFirstChild("Backup_IA_Margem") then local b = s:Clone(); b.Name = "Backup_IA_Margem"; b.Parent = SS end
assert(loadstring(src), "nao compila")
s.Source = src
return "aplicado"
