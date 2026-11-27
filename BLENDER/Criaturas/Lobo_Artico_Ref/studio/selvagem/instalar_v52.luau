-- Instala a anim_v52 no rpg_roblox (Edit; aprovado pelo usuario 27/11): Movimento_LoboArtico v52 (so as trajetorias da PartidaCurva
-- E/D mudam: v51, 87 graus em 2,4 s). Tudo-ou-nada: confere a fonte v49, compila, faz backup do Movimento e dos 18 KFS que serao
-- trocados (16 curvas do Andar + PartidaCurva E/D) em ServerStorage.LoboArtico_Backups.Antes_v52_27_11. Os KFS sao remontados depois
-- por montar_kfs_lobo_v52.luau (em lotes). O Controle (r13) nao muda.
local HS = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local lib = game.ReplicatedStorage.Animacoes_LoboArtico
local mov = lib:FindFirstChild("Movimento_LoboArtico"); assert(mov, "sem Movimento_LoboArtico")
local cab = mov.Source:sub(1, 400)
if cab:find("gerar_movimento_v52.py", 1, true) then return "Movimento ja em v52" end
assert(cab:find("gerar_movimento_v49.py", 1, true), "Movimento com fonte inesperada")
local novo = HS:GetAsync("http://127.0.0.1:8766/Movimento_LoboArtico_v52.lua?t=" .. os.time(), true)
local f, err = loadstring(novo); assert(f, "nao compila: " .. tostring(err))
local M = f(); assert(M.Curvas.PartidaCurvaEsquerda and M.Curvas.AndarCurvaEsquerda, "dados incompletos")
local nomes = {"PartidaCurvaEsquerda", "PartidaCurvaDireita"}
for _, l in ipairs({"Esquerda", "Direita"}) do
	for _, a in ipairs({"AndarCurva", "AndarCurvaFechada", "AndarParaCurva", "CurvaParaAndar", "CurvaParaFechada", "FechadaParaCurva", "CurvaBreve", "CurvaCurta"}) do table.insert(nomes, a .. l) end
end
for _, n in ipairs(nomes) do assert(lib:FindFirstChild("LoboArtico_" .. n), "KFS ausente: " .. n) end
local bk = SS.LoboArtico_Backups
if not bk:FindFirstChild("Antes_v52_27_11") then
	local p = Instance.new("Folder"); p.Name = "Antes_v52_27_11"
	local c = mov:Clone(); c.Name = "Movimento_LoboArtico_v49"; c.Parent = p
	for _, n in ipairs(nomes) do lib["LoboArtico_" .. n]:Clone().Parent = p end
	p:SetAttribute("Origem", "antes da anim_v52 (16 curvas do Andar + PartidaCurva E/D v48 + Movimento v49; instalar_v52.luau, 27/11)"); p.Parent = bk
end
mov.Source = novo
return "Movimento v49 -> v52; backup com " .. (#bk.Antes_v52_27_11:GetChildren()) .. " itens"
