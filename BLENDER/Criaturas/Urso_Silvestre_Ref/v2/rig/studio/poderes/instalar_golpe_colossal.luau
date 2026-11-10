local raiz = game.ServerStorage:FindFirstChild("Urso_v2_Piloto") or Instance.new("Folder"); raiz.Name = "Urso_v2_Piloto"; raiz.Parent = game.ServerStorage
local dados = raiz:FindFirstChild("Dados_Clipes") or Instance.new("Folder"); dados.Name = "Dados_Clipes"; dados.Parent = raiz
local v
v = dados:FindFirstChild("Urso_GolpeColossal"); if v then v:Destroy() end
v = Instance.new("StringValue"); v.Name = "Urso_GolpeColossal"; v.Value = [==[Urso_GolpeColossal|30|0|97|Raiz,Pelve,Coluna1,Coluna2,Coluna3,Pescoco,Pescoco2,Cabeca,Mandibula,OrelhaE,OrelhaD,EscapulaE,BracoE,AntebracoE,MaoE,DedosE,EscapulaD,BracoD,AntebracoD,MaoD,DedosD,Cauda1,Cauda2,CoxaE,CanelaE,PeE,DedosPeE,CoxaD,CanelaD,PeD,DedosPeD
Raiz|6|EAhDvI7MhQnSrTrTnShQ7MvFsSofge2UuDrSpYra7bvcvc7brapYtV9RzN3IhDAAAAAAAAAAAAAAAAAAAAAAyJ0c4vB6iC+1CitDqUucsakOQAAAAvBhEnG/HnJhKrKnK1J1IlHnF5CLAAAAAAAAAAAAAAA
Raiz|7|Ev7F1CvHpLjOjQ/Q/QjQjOpL5EkQoegiBoe6S2CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnL54BxvC7pC1nBpBAAAAkEuLyRsW8Zickd4ckbqYiU2O+HiBAAAAAAAAAAAAAAA
Pelve|1|EAKcsB2B8BiCgC+B2BqBU9BxFxJpMxN9NrPzQxR5R5RnRnQ7O/M5KnIlF5BAAAAAAAAAAAAAAAAAAAAAA2FoRidqpB81ByiCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Pelve|4|EgxTAAAAABABABACCCDPXlB3BpC7CrD5DhEjE/DvD5C5BVAAAAAAAAAAAAAAAAAAAAAAiC4FyI0JkIyDAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Coluna1|1|EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAe4EyGkGqDEAAAAJftB7BjCpCtCrCnChCzBnBVBAAAAAAAAAAAAAAA
Coluna1|4|EgxTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADDDAAAAAACACCCCACAAAAAAAAAAAAAAAAAAAA
Coluna2|1|EAAAAAAAAAAAAAJZpB1BhCpCvCzC3C1C1CvCpC/B3BpCrD3D1DlD/BNAAAAAAAAAAAAAAAoBgD+D6E4F4FsGmI8LuJmNqMyGIAAAAV9B7C3DnE1E5E5EvEhEpDtCpBFAAAAAAAAAAAAAAA
Coluna2|4|EgxTAAAAAAAAAAAAAAAAABBABDBDBBDDFFHHDBAAAAAAAAAAAAAAAEGKIKIIGCDLRNAAAAAAEGIGIGECCCAAAAAAAAAAAAAAAAAA
Coluna3|1|EAAAAAAAAAAAAAFRbjBrBxBzB5B3B7B3BzBxBrBjBbRFAAAAAAAAAAAAAAAAAAAAAAU6BgDoEuFiIkH8JoJ+EEAAAAPtBlC3CnDvDzDxDrDhDvC5BfDAAAAAAAAAAAAAAA
Coluna3|4|EgxTAAAAAAAAAAAAAAAAAABABABABBABAAAAAAAAAAAAAAAAAAAAAAAAACECCCBFLHAAAAACCEEECECCCAAAAAAAAAAAAAAAAAAA
Pescoco|1|EAiBgDuE0FsG4G4GsG0FuE+BrGlLpLvI9CsEmG2GiHoHmHiH0GkGuFwE8BvE/E5D5PgGrDxH6MxJAyJ5MyH2ClLqMnFnFoMlL2CyJzEoO4EtClJ7Q5VrXyQiXuVwLMAAAAlBpDhFvGvHjItIrI7HhH7FnEpCJAAAAAAAAAAAAAAA
Pescoco|4|EgxTAABDDJJLLLDQWSICDFHLNRTTVTTFSUOyBRKUjBcAbkBTHehBQOhBgBHbOvBRKgByBqBSJlB5BpBAAAAAEMSWUWQOKGCCAAAAAAAAAAAAAAAAA
Pescoco2|1|EAAAAAAAAAAAAAKaqB2BiCqCwC0C4C2C2CwCqCgC4BBzCpE9EnE1CRAAAAAAAAAAAAAAA0BiEoFqEqB7CrGlI/JAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Pescoco2|4|EgxTAAAAAAAAAAAAAAAAABBABDBDBBDAEGGCCAAAAAAAAAAAAAAAAADDFBEIGCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Cabeca|1|EAU6B2CsD6DiEiE6DsD2CkB5D5G/GtFnCkCiDsDwD0D0DwDsDiD4CoCa9DhDtB3NsHhDzH8MzJA0J7M0H2CnLqMnFnFqMnL2C6IzG0LsDb9DtI9KlL0K8O4NuHIAAAAZjCnDlE5EnFtFrFhFxE3D3CvBFAAAAAAAAAAAAAAA
Cabeca|4|EgxTAAABBBDFDDBGIICCBBBBDDFDFFDBIGCSHEINKAJOHDMLGENOBLKRFCGMMEDPXPBAAAACGGKIKGGECCAAAAAAAAAAAAAAAAAA
Mandibula|1|EAAAAAAAAAAAAAAAAAAAAAAAAAAAAsOofowB82B+W+sBDpOmYhSAiSlYqOiFjVmX7J9JkX/UiF3Bj7B3mBr1B5qBlPAAoDyQiXuVwLMAAAAlBpDhFvGvHjItIrI7HhH7FnEpCJAAAAAAAAAAAAAAA
Mandibula|4|EgxTAAAAAAAAAAAAAAAAAAAAAAAAAAAFvBtF5KjG1OCiF5I2GA1G6IhF9B0HrI2DwDvI6H5BU4RqIqHwCGAAAJlB5BpBAAAAAEMSWUWQOKGCCAAAAAAAAAAAAAAAAA
OrelhaE|1|EAAAAAAAAAAAAAtBlEvGvInKvLxMlNtNtNhNrMpL/JnIpGhErBAAAAAAAAAAAAAAAAAAAAAAsEoNmWsf0oB+qBrjBpxBntB/XZAAAAuC+G0K0N6PqR+R6R8QkPwMkJgFUAAAAAAAAAAAAAAA
OrelhaE|4|EgxTAAAAAAAAAAAAAADHLVfpBzB7BlCnCrClC/BzBhBLAAAAAAAAAAAAAAAAAAAAAAmBoD8EsF0E+BrBpFtI7FHAAAAW4B0CgDiD+CwC+BsBaOGAAAAAAAAAAAAAAAAA
OrelhaD|1|EAAAAAAAAAAAAAtBlEvGvInKvLxMlNtNtNhNrMpL/JnIpGhErBAAAAAAAAAAAAAAAAAAAAAAsEoNmWsf0oB+qBrjBpxBntB/XZAAAAuC+G0K0N6PqR+R6R8QkPwMkJgFUAAAAAAAAAAAAAAA
OrelhaD|4|EgxTAAAAAAAAAAAAAADHLVfpBzB7BlCnCrClC/BzBhBLAAAAAAAAAAAAAAAAAAAAAAmBoD8EsF0E+BrBpFtI7FHAAAAW4B0CgDiD+CwC+BsBaOGAAAAAAAAAAAAAAAAA
BracoE|1|EwhCwB+D2FwG8G4GoGwFyEyDuB/EjHlEmB+JkU4W6W2VqT6P0LiHuCnB5D5EnEhCXTNBAAAAAAAAAAAAAAAIUY5CzJtUhmB9+Bj5CgUwSwL0EGAAAANpBhC0G6IoJiIwF4BxChHnLlOvHAAAAAAAAAAAAAAA
BracoE|2|ElBAEGIIMMMMIELflBnBjBfdTHKeqB0B2ByBsBeIJTPJBAAAAAAAAAAAAAAAGQUIRlBTsBwEmE4GkHmEEAAAANnB5B1BzCpDzD3DxDhDvC3BfFAAAAAAAAAAAAAAA
BracoE|3|E+OQqB+BqCwCwCwCoC+BwBUjClE5EjEhCe2BgCoCqCqCoCiC4BuBkBSBRVTNBAAAAAAAAAAAAAAAIUYBvB9C/DlEN+J4LyJ6EEAAAAPrBjClBjC7CxDpE5EnFvFpF1E7BAAAAAAAAAAAAAAA
BracoE|4|EstTFNXdfjBjBhBdXJiBwBcB1BhEtFtG/G9GpG/ElDlBO0BiC6BeKKGCAAAAAAAAAAAAAAADJLmBgE4HoMuO6IrBpClCjBBAAAAEMQTZfbRCauB8BgCcAAAAAAAAAAAAAAA
AntebracoE|1|E74DvDvJzNhQjR9Q/PpO/LpJ7DmN0Y+amVgFtQhW7X3YxYnX9U5RlOtK7G9CiByDsE8DwCQAAAAAAAAAAAAAAAvB1D3E+BkPkemuB48B64B7jC3pC52BxZZAAAAwCoHsL2DqHsL8P4U6ZwemiBgkBmiByOAAAAAAAAAAAAAAA
AntebracoE|3|E1nBjBjDvEnFzFxFnF1E9DhDnBqEiI8I+G0BrFnH5HjIhIzH7G7FzEtDnCfMmBuBoBaGAAAAAAAAAAAAAAAPnBxBW+E8JmP+T0SnWlY/RtIHAAAAasC4DmBuC2DoF6GuIgKoL6LoL4EAAAAAAAAAAAAAAA
AntebracoE|4|E+jTZlCvDzEtF/FnG/FtFtE7BqG4KqK+GyBlF5H1JpL1MtNpNrMxKlI1FrCc+CyDkD+BMAAAAAAAAAAAAAAAlB7C7DyB+LsV4bscoT5XxlBrlB3UXAAAAmCiGkJ+CwFqI+KmN4OoPyO0MyJuDAAAAAAAAAAAAAAA
MaoE|1|Eq3B4B6E8GmI6I8IuI2HwGkFkCnH9MhNzImB6N4SqWuZmcmekf4e+c6ZsV6PuJyCdZPDAAAAAAAAAAAAAAAKagBlIxalsBj6B7gCl3Bmd+fwY4LMAAAAlBpDnFxCrHzLjP9RhUrV3V7U9R/GAAAAAAAAAAAAAAA
MaoE|2|E/JHXhBlBnBnBjBdZTHcyB2BoBCvB3B3BvBjBTCYwBiCoCkC0BcKKGCAAAAAAAAAAAAAAADJLZzBlBO+CiF9EjFrDrBAAAAAEMSDLPFEauBkCyC6CoBAAAAAAAAAAAAAAA
MaoE|3|E8WW8B2CoDwDwDsDiD2CiCa7CtF5FtEfwD8E0FoG6GoH0H8H4HqHoG2E0CSRNJBAAAAAAAAAAAAAAAGOSjCvHhMrP9QrNoN6O4L6FIAAAAT1BxCxBnDzE3FxGlHxHxHrHtGvCAAAAAAAAAAAAAAA
MaoE|4|EiuTFRbjBrBxBxBxBvBjBR2B6CwCwBDnCzDhF9GjJtL7N7PjRnR7P1M/HlCcaQCAAAAAAAAAAAAAAAJVfgHmVoe4fsa2PjIjLlKtFFAAAASyBuCkBmDyEyF+F8FsFyEyDsCaAAAAAAAAAAAAAAA
BracoD|1|EkkCwB+D0FyG6G2GmGuFwEwDsB7E9G9DwBqKuU+WiX4VsT+P0LgHwCpB5D7ElEhCVRLBAAAAAAAAAAAAAAAIQY7C1JtUnmBx/B76CiUoSqLwEGAAAANnBhC7C3DzEzFtGlHwE8H+J+K4KyHoDtBnG7K/GAAAAAAAAA
BracoD|2|EoBBDFHLLNNNJFQkBuBwBqBmBkBaMJdxB9B/B/B1BnBLMWSMEAAAAAAAAAAAAAAAHRXJasBWxBlF9E5HpI9EDAAAAQuBmC0C+CiDiD6CyCyB0B2BwBuBwB0BuBkBYGAAAAAAAAA
BracoD|3|EnUT3BtC/ClDnDjD5CtC9BZ4CmF+FgFoCzBvC9CnDpDnDjD3CrC9BtBXEWcaQEAAAAAAAAAAAAAAAJXfEmCmE8FyG6C3M3O9L7FHAAAAU2B0CuDkE0EiFqFqFiC2BqBYMqBsCmD8DqEmCAAAAAAAAA
BracoD|4|E+sTFPZfjBlBnBjBfZJkB0BgBA5BpE1F3GpHnHzGlFrDpBOyBkC6BeMMGAAAAAAAAAAAAAAAABJNoBmEkI6MoPwJ3B7C1CvBBAAAAGOUagBgBiBiBeDNZjBpBdLMkByBcAAAAAAAAA
AntebracoD|1|E77DtDrJrN3P3QxQzP7N1LhJ3D6M6XgamUoE1Q/V3XrY/XzWpUlRzN/JzG3CesDkE0DsCOAAAAAAAAAAAAAAArBvDtE+B4OmdotBw8Bi7BtiCxnC90BzYZAAAAuC+G+K2OiSiV0XyZ0auHwE6BVhCkDwJoPqUkYgNAAAAAAAAA
AntebracoD|3|EyzBuB8D0FyG+G8GwG6F8E4DyBpF9J5KtI3B+GmJ8JkKgKuJuImH0FmE4CkBLrB3BvBfFAAAAAAAAAAAAAAAUuB8BbjGjM7SlZxY2b4diWoKKAAAAf7CxEjGvH3I7JzKhLjD7BXIcpB9DpGvI/JtFAAAAAAAAA
AntebracoD|4|EuiTbrC1D7E3FnGvGpGzFxE/ByGmLyKmHuB3FvItKjMrNlO9N9M9KvI5FvCcgD0DmDgCMAAAAAAAAAAAAAAAlB/C9D4BuMuWqdweuV1YtmBhmB/UVAAAAmCiGqJ2LuNqOwO+N4MoD+BYHbqB6D2F8GgHoDAAAAAAAAA
MaoD|1|Ek7B6B8EiHuIgJiJ0I6H2GmFmCrHnNnN1IqBmOmT2W8Z0c0e2fuf2d0akWuQ6J6CdZPBAAAAAAAAAAAAAAAIaetItbptBt7BxiCr5B+dygB8YgMMAAAAlBtDpF/GxI5J7KzL/LzDnFrGlH/H/KtN/OrPxOxGAAAAAAAAA
MaoD|2|EgTQsBiCqCwCsCoCgC2BoBS5BpDvDvCBiD8DiEiE6DqDyC0BUJbnBnBbPPHBAAAAAAAAAAAAAAAEOUMJnCxFnJjLqJ6JgHkDCAAAAJZrB7BrC5CnDvD1DZHGWaCfhC/C3DhCAAAAAAAAA
MaoD|3|EjPNjB1B/BlClCjC7B1BpBP6BwD8DmDoBlB5B9B/BhClCtC3ChDjD7CjClBBOMICAAAAAAAAAAAAAAADLPaoDgF8FuGyEjJrKnIlEDAAAAOmB6BuC6CoDwD2D6DuBmBcUMgByBgCsC0CqBAAAAAAAAA
MaoD|4|E4tTHRbnBtBxB1BxBvBlBR4B8CwCyBFrC3DpFjHnJzL9N/PlRpR9P3M/HnCcYQCAAAAAAAAAAAAAAAJVdiHqVuekgB8aqQlIlLhKtFDAAAAQyBsCiDyD6DiEgE8DiBuB2B4B4BsC4C0CuC8BaAAAAAAAAA
CoxaE|1|E14BpBzDtF3GvH9H5HnHrG/ElCmH6O+SsTyPmJ6IyJ+JiKgK0JgJoImH8FwE8CgBAAAAAAAAAAAAAAAAAAAAAAjDtJ/PhXvezoBpKzMnK/EFAAAAQuBmC+CyDgEsEwEyEoE2D6CwBIAAAAAAAAAAAAAAA
CoxaE|2|EDAACCCCCCACCDDFHHFFHHFHHFFDFBBBAAAAAAAAAAAAAAAAAAAAAACIMQWgBBABAAAAAAAAAAACAAACAAAAAAAAAAAAAAAAAAA
CoxaE|3|EoDAGIIKMKKIGEJTXZRLHLJJJJJHHFDBBAAAAAAAAAAAAAAAAAAAAAAEKQWiBuBWeaMAAAAAADFHHJJJLHHFDAAAAAAAAAAAAAAAA
CoxaE|4|EuuTDLRXdjBlBlBhBdNsBuC2CiCoBSOIGAFJNPRPLJBAAAAAAAAAAAAAAAAAAAAAAIckBcDxChBvBvBXAAAAACGMOQSSSQQMIECAAAAAAAAAAAAAAA
CanelaE|1|E8vDuBgE+FoHgIoIgIqHsG+EkChHpO3RtRtMzEtDzDxDtDjD5CtC9BxBjBZNDAAAAAAAAAAAAAAAAAAAAAAO2B0DwGyK8UgZ4f2auNOAAAArB5D9F5HnJrKjLrLnLtK9I1G1DPAAAAAAAAAAAAAAA
CanelaE|3|E7DBDFHJHJHFFBIQUSOGEEECEECCCCAAAAAAAAAAAAAAAAAAAAAAAAAABDFLXbhBdNBAAAACEIIKMMMMMKIEAAAAAAAAAAAAAAAA
CanelaE|4|E8mTHXjBxB3B9B/B9B1BtBTiC6DoE0DqCYSSSQOMKIGEEACAAAAAAAAAAAAAAAAAAAAAABHNZxBzDpFpItI1EFAAAAQsBkCyCgDkDmDgD4CqC8BqBWCAAAAAAAAAAAAAAA
PeE|1|E/2BPnB7BpCtCvCrChC5BrBP8BoFyIuKwKoJgK2KmLsLkL4KgKgJ8HuG8EiDiBAAAAAAAAAAAAAAAAAAAAAArDlKxRxZpiBtuB9OzTlR9IJAAAAeyC+DiFgG0GgHiH8GqGqF+DmCKAAAAAAAAAAAAAAA
PeE|2|EjEBDFFFHHFDFAGOUYYQSUUUUUQQOMIEEAAAAAAAAAAAAAAAAAAAAAAFRfrB9B1ChBtBnBVAAAAACGKMOOQSQOMKECAAAAAAAAAAAAAAA
PeE|3|E7GBDHHHJHHFFBIUkBsBuBqBuByB0B0ByByBuBoBkBeWOEAAAAAAAAAAAAAAAAAAAAAANvBvCzD9E1G/BzCrCnBAAAAAEKSWaeeeeaYQKAAAAAAAAAAAAAAAA
PeE|4|EwuTADFHHHHHFFBISecYQMGCFLRVXZVRNDAAAAAAAAAAAAAAAAAAAAAAOmB0BwBKzCzB1C7C1BBAAAAGQWeiBiBgBgBcYQOGAAAAAAAAAAAAAAAA
CoxaD|1|E52BrBzDxF5GzH/H7HrHrGjFjCoH8O+SqTsP6IqIgJqJwJsJgJuI0H2GyFmE0CeAAAAAAAAAAAAAAAAAAAAAA7C5I9OxVzcvmBvJzLpJtEFAAAAOqBgC0CmD2D+DmEmE+DsD0CuBGAAAAAAAAAAAAAAA
CoxaD|2|ESABDFFFFFFDDIOWaYUYYYaYYWUQOMGEAAAAAAAAAAAAAAAAAAAAAAHXlB3BrClDCEGCAAAAAAABBBBABBAABAAAAAAAAAAAAAAAAA
CoxaD|3|E/JFPXdfjBhBfbVHegCwCwC+BecegBeeccYUQOICAAAAAAAAAAAAAAAAAAAAAAHbtBjC9CpElC5CtCnBAAAAAEKSWcegBgBgBcaSKCAAAAAAAAAAAAAAA
CoxaD|4|EwuTDJRZdjBlBlBjBfLsBwC0CkCoBQMKEADHLNNNLHBAAAAAAAAAAAAAAAAAAAAAAIYeYFrCfrBpBVBAAAAEGKMOQSQOOMIEAAAAAAAAAAAAAAAA
CanelaD|1|E8tDwBmEoGyHsI0IsI2H0GmFmCrH5OnSzRrM/DzC1CzCtClC5BvBlBbRJFBAAAAAAAAAAAAAAAAAAAAAAGagCmE0HmRkY2e6ZgNOAAAApB1D5FvH9I/J3KhL7KhKzItGxDPAAAAAAAAAAAAAAA
CanelaD|3|EoMEQWaegBeaYSIZzBhC9BrBNJJJHHFFDBBBAAAAAAAAAAAAAAAAAAAAAAAAACIOc+B2CsD8CuBCAAAADNTZhBhBnBlBlBjBfVNAAAAAAAAAAAAAAAA
CanelaD|4|EknTHZlBxB7BhChChC7BvBTkCiEsE4DoCWOOOMKIIEECCAAAAAAAAAAAAAAAAAAAAAAAAADHTjBhDhF9H/HvEDAAAAOsB+BwC6CgDgD8C0CoC4BoBWCAAAAAAAAAAAAAAA
PeD|1|Ep2BPtBhCtC1C3CxCpC/BvBTkC0F8IyKsK+IwJoK2K6K2KoKyJ2IyHmG4E+CiBAAAAAAAAAAAAAAAAAAAAAAnD7J9QvY1gBpsB1OpT9Q3IJAAAAcyC8DiF8FwG8GgH2GmGmF8DkCKAAAAAAAAAAAAAAA
PeD|2|E6HCKMQQQSOMKENdrBtBlBXXZZZZZVTRNLFBAAAAAAAAAAAAAAAAAAAAAAGYmB8BwC4D+B0CoCkBCAAAADJRTZbbddZVRHBAAAAAAAAAAAAAAA
PeD|3|EyGCGGIKKIIGECFVnBxBzBxB3B5B9B7B7B5B1BvBpBhBZPFAAAAAAAAAAAAAAAAAAAAAAS2B+CoE6FgIoCgD4CuBCAAAAFNTZdhBhBjBfdZRJBAAAAAAAAAAAAAAA
PeD|4|EyuTBDFHJHJHHFBIUeeYQMICDLPRVXTPLDAAAAAAAAAAAAAAAAAAAAAAMkBuBqBIzCxBzC7C1BBAAAAGQYciBiBgBecWSMGCAAAAAAAAAAAAAAA]==]; v.Parent = dados
v = dados:FindFirstChild("Perfis_Urso_GolpeColossal"); if v then v:Destroy() end
v = Instance.new("StringValue"); v.Name = "Perfis_Urso_GolpeColossal"; v.Value = "v=0;giro=0;perfil="; v.Parent = dados

-- 2) KeyframeSequence (adaptador proprio do urso) + instante do impacto marcado no Blender
local P = game.ServerStorage.Urso_v2_Piloto
local A = require(P.AdaptadorUrso:Clone())
local modelo = workspace.Teste_Urso_v2.Urso_Silvestre_v2_Piloto
local kfs, faltam, np = A.montar(modelo, "Urso_GolpeColossal", Enum.AnimationPriority.Action2)
local velho = P.Animacoes:FindFirstChild("Urso_GolpeColossal"); if velho then velho:Destroy() end
kfs:SetAttribute("ImpactoS", 1.9333); kfs:SetAttribute("ImpactoQuadro", 58); kfs:SetAttribute("RugidoS", 1.0); kfs.Parent = P.Animacoes
-- 3) modulos (fonte gravada pelo instalador; versoes no repo: rig/studio/poderes/*.luau)
local pod = P:FindFirstChild("Poderes") or Instance.new("Folder"); pod.Name = "Poderes"; pod.Parent = P
local s = pod:FindFirstChild("PoderesUrso_Servidor") or Instance.new("ModuleScript"); s.Name = "PoderesUrso_Servidor"
s.Source = [=====[-- PoderesUrso_Servidor (ModuleScript em ServerStorage.Urso_v2_Piloto.Poderes) - LABORATORIO ISOLADO do Urso Silvestre v2.
-- Etapa 1: GOLPE COLOSSAL. O SERVIDOR decide tudo: dono, estado, recarga, energia, ponto de impacto, alvos e dano.
-- O cliente so pede (RemoteEvent Pedido) e mostra efeitos (RemoteEvent Efeitos). Nada aqui e regra oficial:
-- TODOS os numeros sao PARAMETROS DE LABORATORIO PROVISORIOS (tabela LAB). Nao usa nem altera os sistemas dos dragoes.
-- Elegibilidade de alvo (LAB, ate existir o sistema oficial de PvP/aliancas no place):
--   * boneco de teste com atributo AlvoTesteUrso = true;
--   * jogador so com workspace.PvPAtivo == true (mesmo atributo de laboratorio dos dragoes), nunca o dono do urso,
--     nunca quem tem AliadoDe == dono, ninguem dentro de parte com tag ZonaSegura.
local RS = game:GetService("RunService")
local Players = game:GetService("Players")
local CS = game:GetService("CollectionService")
local M = {}

M.LAB = {               -- PROVISORIO (nao aprovado): ajustar so com decisao do usuario
	GolpeColossal = {
		recarga = 8.0,          -- s
		energia = 20,           -- custo (energia do urso em atributo EnergiaLab; sem sistema oficial de energia no place)
		raio = 76.0,            -- (2x em 04/11: "aumente 2x mais o alcance"; era 38) studs, horizontal, a partir do CENTRO DO CORPO (v5, 04/11, pedido do usuario: "amplie o raio" -
		                        -- acompanha as rachaduras em volta do corpo inteiro; antes 14 a partir do ponto das patas)
		alturaMax = 4.0,        -- studs: diferenca vertical maxima entre o chao do impacto e o pe do alvo
		dano = 40,              -- dano fixo de laboratorio (sem queda com a distancia nesta versao)
		janelaAcerto = 0.10,    -- s: o dano e aplicado uma unica vez dentro desta janela apos o contato
		alcanceRaioChao = 6.0,  -- studs: raycast do ponto entre as patas para baixo
	},
}

local pasta = game.ServerStorage:WaitForChild("Urso_v2_Piloto")
local remotos = game.ReplicatedStorage:FindFirstChild("Urso_v2_Lab") or Instance.new("Folder")
remotos.Name = "Urso_v2_Lab"; remotos.Parent = game.ReplicatedStorage
local function remoto(n) local r = remotos:FindFirstChild(n) or Instance.new("RemoteEvent"); r.Name = n; r.Parent = remotos; return r end
local Pedido, Efeitos = remoto("Pedido"), remoto("Efeitos")

local ACP = game:GetService("AnimationClipProvider")
local estado = {}           -- [urso] = {acao, faixa, recargaAte, ataque}
local log = {}              -- registro do laboratorio (testes leem daqui)
M.log = log
local function registrar(t) t.t = workspace:GetServerTimeNow(); table.insert(log, t); if #log > 400 then table.remove(log, 1) end end

local function raiz(mod) return mod and (mod:FindFirstChild("HumanoidRootPart") or mod.PrimaryPart) end
local function emZonaSegura(pos)
	for _, z in ipairs(CS:GetTagged("ZonaSegura")) do
		if z:IsA("BasePart") then
			local p = z.CFrame:PointToObjectSpace(pos); local s = z.Size / 2
			if math.abs(p.X) <= s.X and math.abs(p.Y) <= s.Y and math.abs(p.Z) <= s.Z then return true end
		end
	end
	return false
end
local function elegivel(urso, mod)
	if mod == urso then return false, "proprio" end
	local h = mod:FindFirstChildOfClass("Humanoid"); if not (h and h.Health > 0) then return false, "sem_vida" end
	local r = raiz(mod); if not r then return false, "sem_raiz" end
	local dono = urso:GetAttribute("DonoUserId")
	local plr = Players:GetPlayerFromCharacter(mod)
	if plr then
		if dono and plr.UserId == dono then return false, "dono" end
		if workspace:GetAttribute("PvPAtivo") ~= true then return false, "pvp_desligado" end
	elseif not mod:GetAttribute("AlvoTesteUrso") then return false, "nao_alvo" end
	if dono and mod:GetAttribute("AliadoDe") == dono then return false, "aliado" end
	if emZonaSegura(r.Position) then return false, "zona_segura" end
	return true
end

local function animator(urso)
	local ac = urso:FindFirstChildOfClass("AnimationController") or Instance.new("AnimationController", urso)
	return ac:FindFirstChildOfClass("Animator") or Instance.new("Animator", ac)
end
local idCache = {}
local function faixa(urso, nome)
	local kfs = pasta.Animacoes:FindFirstChild(nome); assert(kfs, "KFS ausente: " .. nome)
	idCache[nome] = idCache[nome] or ACP:RegisterAnimationClip(kfs)
	local a = Instance.new("Animation"); a.AnimationId = idCache[nome]
	local f = animator(urso):LoadAnimation(a); f.Priority = Enum.AnimationPriority.Action2
	return f, kfs
end

-- ponto de impacto: meio das duas patas dianteiras (ossos MaoE/MaoD), raycast PARA BAIXO a partir de pouco acima
-- (2,5 studs): acha o chao sob as patas, nunca um teto ou outro andar acima.
local function pontoImpacto(urso)
	local function osso(n) local b = urso:FindFirstChild(n, true); return b and b.TransformedWorldCFrame.Position end
	local a, b = osso("MaoE"), osso("MaoD"); if not (a and b) then return nil end
	local c = (a + b) / 2
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
	local excl = {urso}; for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(excl, p.Character) end end
	for _, m in ipairs(CS:GetTagged("AlvoTesteUrso")) do table.insert(excl, m) end
	rp.FilterDescendantsInstances = excl
	local r = workspace:Raycast(c + Vector3.new(0, 2.5, 0), Vector3.new(0, -M.LAB.GolpeColossal.alcanceRaioChao, 0), rp)
	return r and r.Position or nil, r and r.Normal or nil, rp
end

-- alvos (v5: medidos do CENTRO do corpo, nao das patas): horizontal <= raio, |altura| <= alturaMax, linha de visada livre (do chao +1,5 ate o centro do alvo, ignorando
-- personagens): parede/obstaculo bloqueia. Cada MODELO conta uma vez (nao por parte).
local function alvos(urso, P, rp)
	local piv = urso:GetPivot().Position; local C = Vector3.new(piv.X, P.Y, piv.Z)     -- centro do corpo, na altura do chao
	local L = M.LAB.GolpeColossal; local lista, motivos = {}, {}
	local vistos = {}
	for _, h in ipairs(workspace:GetDescendants()) do
		if h:IsA("Humanoid") then
			local mod = h.Parent
			if mod and not vistos[mod] then
				vistos[mod] = true
				local ok, por = elegivel(urso, mod)
				local r = raiz(mod)
				if ok then
					local pe = r.Position - Vector3.new(0, (h.HipHeight or 0) + r.Size.Y / 2, 0)
					local dh = Vector3.new(r.Position.X - C.X, 0, r.Position.Z - C.Z).Magnitude
					local dy = math.abs(pe.Y - P.Y)
					if dh > L.raio then ok, por = false, string.format("fora_raio(%.1f)", dh)
					elseif dy > L.alturaMax then ok, por = false, string.format("altura(%.1f)", dy)
					else
						local o = C + Vector3.new(0, 1.5, 0)
						local hit = workspace:Raycast(o, r.Position - o, rp)
						if hit and not hit.Instance:IsDescendantOf(mod) then ok, por = false, "obstaculo(" .. hit.Instance.Name .. ")" end
					end
				end
				if ok then table.insert(lista, mod) end
				motivos[mod.Name] = ok and "ACERTO" or por
			end
		end
	end
	return lista, motivos
end

function M.golpeColossal(urso, quem)
	local L = M.LAB.GolpeColossal; local agora = workspace:GetServerTimeNow()
	local e = estado[urso] or {}; estado[urso] = e
	if urso:GetAttribute("Incapacitado") then registrar({ev = "recusado", motivo = "incapacitado"}); return false, "incapacitado" end
	if e.acao then registrar({ev = "recusado", motivo = "ocupado"}); return false, "ocupado" end
	if (e.recargaAte or 0) > agora then registrar({ev = "recusado", motivo = "recarga"}); return false, "recarga" end
	local en = urso:GetAttribute("EnergiaLab") or 100
	if en < L.energia then registrar({ev = "recusado", motivo = "energia"}); return false, "energia" end
	urso:SetAttribute("EnergiaLab", en - L.energia)
	local f, kfs = faixa(urso, "Urso_GolpeColossal")
	local tImp = kfs:GetAttribute("ImpactoS") or 1.10
	local tRug = kfs:GetAttribute("RugidoS")                 -- v2: rugido antes de bater (so apresentacao: som/efeito)
	local id = game:GetService("HttpService"):GenerateGUID(false)
	e.acao = "GolpeColossal"; e.faixa = f; e.recargaAte = agora + L.recarga; e.ataque = id; e.rugiu = false
	f:Play(0.12); registrar({ev = "inicio", id = id, quem = quem})
	Efeitos:FireAllClients({tipo = "GolpeColossal", fase = "inicio", urso = urso, id = id})
	local feito = false
	local con; con = RS.Stepped:Connect(function()
		if feito then return end
		if not f.IsPlaying or e.ataque ~= id then           -- interrompido antes do contato: sem dano e sem efeito
			feito = true; con:Disconnect(); registrar({ev = "interrompido", id = id, tp = f.TimePosition}); return
		end
		if tRug and not e.rugiu and f.TimePosition >= tRug then
			e.rugiu = true; Efeitos:FireAllClients({tipo = "GolpeColossal", fase = "rugido", urso = urso, id = id})
		end
		if f.TimePosition >= tImp then
			feito = true; con:Disconnect()
			if f.TimePosition > tImp + L.janelaAcerto / math.max(f.Speed, 0.05) + 0.05 then
				registrar({ev = "janela_perdida", id = id, tp = f.TimePosition}); return
			end
			local P, N, rp = pontoImpacto(urso)
			if not P then registrar({ev = "sem_chao", id = id}); return end
			local lista, motivos = alvos(urso, P, rp)
			local feridos = {}
			for _, mod in ipairs(lista) do
				local h = mod:FindFirstChildOfClass("Humanoid")
				if h and mod:GetAttribute("UltimoAtaqueUrso") ~= id then       -- trava por ataque: nunca 2x no mesmo modelo
					mod:SetAttribute("UltimoAtaqueUrso", id); h:TakeDamage(L.dano); table.insert(feridos, mod.Name)
				end
			end
			registrar({ev = "impacto", id = id, tp = f.TimePosition, velocidade = f.Speed, pos = P, feridos = feridos, motivos = motivos})
			Efeitos:FireAllClients({tipo = "GolpeColossal", fase = "impacto", urso = urso, id = id, pos = P, normal = N, raio = L.raio})
		end
	end)
	f.Stopped:Once(function() if e.ataque == id then e.acao = nil; e.faixa = nil end end)
	return true, id
end

function M.interromper(urso)                                -- ex.: atordoado/derrotado; o servidor chama
	local e = estado[urso]; if e and e.faixa then e.ataque = nil; e.faixa:Stop(0.15); e.acao = nil end
end

-- ================================================================== Etapa 2: RUGIDO PROTETOR (04/11)
-- Aprovado pelo usuario: o rugido concede VELOCIDADE, DEFESA e REGENERACAO ao URSO e ao TREINADOR (dono). Nao vale para
-- outros aliados. Numeros = LAB (provisorios). O servidor decide tudo; o cliente so mostra a onda e a aura.
--   * velocidade: treinador = Humanoid.WalkSpeed + delta (delta guardado e devolvido exatamente: outros bonus/penalidades
--     aplicados por outros sistemas durante o efeito ficam intactos); urso = atributo VelocidadeBonus_RugidoProtetor
--     (o urso ainda nao tem sistema de movimento no place);
--   * defesa: atributo DefesaBonus_RugidoProtetor; M.danoComDefesa(alvo, dano) aplica a soma dos DefesaBonus_* (teto 60%).
--     PENDENTE: nenhum sistema de dano do place le esse atributo ainda (integracao futura com o combate oficial);
--   * regeneracao GRADUAL (nunca cura instantanea): % da vida maxima por segundo, em ticks; nunca passa da vida maxima;
--     nao age em quem esta com vida 0 / incapacitado. Urso: atributos Vida/VidaMax (LAB; o urso nao tem Humanoid);
--   * renovar: novo rugido com o efeito ativo RENOVA a duracao (nao acumula delta nem soma bonus);
--   * remocao: fim da duracao, morte/incapacitacao do alvo, saida do jogador, personagem removido. Remove SO o deste poder.
M.LAB.RugidoProtetor = {
	recarga = 20.0, energia = 30, duracao = 10.0,
	alcanceTreinador = 40.0,      -- studs entre o urso e o treinador no instante do efeito
	velocidade = 0.20,            -- +20% de velocidade
	defesa = 0.25,                -- 25% menos dano (via M.danoComDefesa)
	regenPorSeg = 0.02,           -- 2% da vida maxima por segundo (10 s -> ate 20%)
	tick = 0.5,
	vidaUrsoLab = 600,            -- VidaMax de laboratorio do urso, se ainda nao houver
}
local ativos = {}                 -- [alvo] = {expira, delta, hum, cons}
M.ativos = ativos
local NOME = "RugidoProtetor"
local function removerBuff(alvo, motivo)
	local b = ativos[alvo]; if not b then return end
	ativos[alvo] = nil
	for _, c in ipairs(b.cons) do c:Disconnect() end
	if b.hum and b.hum.Parent then b.hum.WalkSpeed = math.max(0, b.hum.WalkSpeed - b.delta) end
	if alvo.Parent then alvo:SetAttribute("DefesaBonus_" .. NOME, nil); alvo:SetAttribute("VelocidadeBonus_" .. NOME, nil); alvo:SetAttribute("Buff_" .. NOME, nil) end
	registrar({ev = "rp_fim", alvo = alvo.Name, motivo = motivo})
	Efeitos:FireAllClients({tipo = NOME, fase = "fim", alvo = alvo})
end
M.removerBuff = removerBuff
local function aplicarBuff(alvo)
	local L = M.LAB.RugidoProtetor; local agora = workspace:GetServerTimeNow()
	local b = ativos[alvo]
	if b then b.expira = agora + L.duracao; registrar({ev = "rp_renovado", alvo = alvo.Name}); return "renovado" end
	b = {expira = agora + L.duracao, delta = 0, cons = {}}
	local hum = alvo:FindFirstChildOfClass("Humanoid")
	if hum then
		if hum.Health <= 0 then return "sem_vida" end
		b.hum = hum; b.delta = hum.WalkSpeed * L.velocidade; hum.WalkSpeed += b.delta
		table.insert(b.cons, hum.Died:Connect(function() removerBuff(alvo, "morte") end))
	else
		alvo:SetAttribute("VelocidadeBonus_" .. NOME, L.velocidade)
		if not alvo:GetAttribute("VidaMax") then alvo:SetAttribute("VidaMax", L.vidaUrsoLab); alvo:SetAttribute("Vida", L.vidaUrsoLab) end
	end
	table.insert(b.cons, alvo.AncestryChanged:Connect(function() if not alvo:IsDescendantOf(workspace) then removerBuff(alvo, "removido") end end))
	alvo:SetAttribute("DefesaBonus_" .. NOME, L.defesa); alvo:SetAttribute("Buff_" .. NOME, true)
	ativos[alvo] = b
	registrar({ev = "rp_aplicado", alvo = alvo.Name, delta = b.delta})
	return "aplicado"
end
-- dano com defesa (para os sistemas que vierem a usar; hoje so os testes)
function M.danoComDefesa(alvo, dano)
	local d = 0
	for k, v in pairs(alvo:GetAttributes()) do if string.sub(k, 1, 12) == "DefesaBonus_" and type(v) == "number" then d += v end end
	return dano * (1 - math.min(d, 0.6))
end
-- ticks de regeneracao e expiracao
local acum = 0
RS.Heartbeat:Connect(function(dt)
	acum += dt; local L = M.LAB.RugidoProtetor; if acum < L.tick then return end
	local passo = acum; acum = 0; local agora = workspace:GetServerTimeNow()
	for alvo, b in pairs(ativos) do
		if agora >= b.expira then removerBuff(alvo, "expirou")
		elseif b.hum then
			if b.hum.Health > 0 and b.hum.Health < b.hum.MaxHealth then b.hum.Health = math.min(b.hum.MaxHealth, b.hum.Health + b.hum.MaxHealth * L.regenPorSeg * passo) end
		else
			if alvo:GetAttribute("Incapacitado") then removerBuff(alvo, "incapacitado")
			else
				local v, mx = alvo:GetAttribute("Vida") or 0, alvo:GetAttribute("VidaMax") or L.vidaUrsoLab
				if v > 0 and v < mx then alvo:SetAttribute("Vida", math.min(mx, v + mx * L.regenPorSeg * passo)) end
			end
		end
	end
end)
Players.PlayerRemoving:Connect(function(plr)
	if plr.Character and ativos[plr.Character] then removerBuff(plr.Character, "desconexao") end
end)
function M.rugidoProtetor(urso, quem)
	local L = M.LAB.RugidoProtetor; local agora = workspace:GetServerTimeNow()
	local e = estado[urso] or {}; estado[urso] = e
	e.recRP = e.recRP or 0
	if urso:GetAttribute("Incapacitado") then registrar({ev = "recusado", motivo = "incapacitado"}); return false, "incapacitado" end
	if e.acao then registrar({ev = "recusado", motivo = "ocupado"}); return false, "ocupado" end
	if e.recRP > agora then registrar({ev = "recusado", motivo = "recarga"}); return false, "recarga" end
	local en = urso:GetAttribute("EnergiaLab") or 100
	if en < L.energia then registrar({ev = "recusado", motivo = "energia"}); return false, "energia" end
	urso:SetAttribute("EnergiaLab", en - L.energia)
	local f, kfs = faixa(urso, "Urso_RugidoProtetor")
	local tRug, tEf = kfs:GetAttribute("RugidoS") or 0.7, kfs:GetAttribute("EfeitoS") or 1.0
	local id = game:GetService("HttpService"):GenerateGUID(false)
	e.acao = NOME; e.faixa = f; e.recRP = agora + L.recarga; e.ataque = id
	f:Play(0.15); registrar({ev = "rp_inicio", id = id, quem = quem})
	local rugiu, feito = false, false
	local con; con = RS.Stepped:Connect(function()
		if feito then return end
		if not f.IsPlaying or e.ataque ~= id then feito = true; con:Disconnect(); registrar({ev = "rp_interrompido", id = id, tp = f.TimePosition}); return end
		if not rugiu and f.TimePosition >= tRug then rugiu = true; Efeitos:FireAllClients({tipo = NOME, fase = "rugido", urso = urso}) end
		if f.TimePosition >= tEf then
			feito = true; con:Disconnect()
			local alvos = {urso}; local res = {[urso.Name] = aplicarBuff(urso)}
			local dono = urso:GetAttribute("DonoUserId"); local plr = dono and Players:GetPlayerByUserId(dono)
			local ch = plr and plr.Character; local hr = ch and ch:FindFirstChild("HumanoidRootPart")
			if hr then
				local d = (hr.Position - urso:GetPivot().Position).Magnitude
				if d <= L.alcanceTreinador then res[ch.Name] = aplicarBuff(ch); table.insert(alvos, ch)
				else res[ch.Name] = string.format("fora_alcance(%.1f)", d) end
			end
			registrar({ev = "rp_efeito", id = id, tp = f.TimePosition, res = res})
			Efeitos:FireAllClients({tipo = NOME, fase = "efeito", urso = urso, alvos = alvos, duracao = L.duracao})
		end
	end)
	f.Stopped:Once(function() if e.ataque == id then e.acao = nil; e.faixa = nil end end)
	return true, id
end

-- pedido do cliente: so o DONO do urso; o servidor ignora qualquer dado alem do nome do poder e do urso
Pedido.OnServerEvent:Connect(function(plr, poder, urso)
	if typeof(urso) ~= "Instance" or not urso:IsDescendantOf(workspace) then return end
	if urso:GetAttribute("DonoUserId") ~= plr.UserId then registrar({ev = "recusado", motivo = "nao_dono", quem = plr.Name}); return end
	if poder == "GolpeColossal" then M.golpeColossal(urso, plr.Name) end
	if poder == "RugidoProtetor" then M.rugidoProtetor(urso, plr.Name) end
end)
return M
]=====]; s.Parent = pod
local lab = game.ReplicatedStorage:FindFirstChild("Urso_v2_Lab") or Instance.new("Folder"); lab.Name = "Urso_v2_Lab"; lab.Parent = game.ReplicatedStorage
local c = lab:FindFirstChild("EfeitosUrso_Cliente") or Instance.new("ModuleScript"); c.Name = "EfeitosUrso_Cliente"
c.Source = [=====[-- EfeitosUrso_Cliente (ModuleScript em ReplicatedStorage.Urso_v2_Lab) - so APRESENTA o que o servidor decidiu.
-- Golpe Colossal: rachaduras temporarias coladas ao chao + placas de chao quebradas + pedras + poeira + tremor local de
-- camera, no instante do contato (evento "impacto" do servidor). Nada aqui decide dano, alvo ou duracao de controle.
-- v2 (04/11, pedido do usuario: "rachaduras com maior alcance e mais reais"):
--   * alcance ~90% do raio do golpe (o servidor manda o raio), rachaduras que CRESCEM do centro para fora (~45 studs/s);
--   * tracado irregular (desvio por segmento), largura afinando ate a ponta, RAMIFICACOES;
--   * fenda escura com borda levantada na cor do chao (lida do raycast: cor da peca ou do material do Terrain);
--   * placas de chao quebradas e inclinadas em volta do centro, pedras que saltam e assentam, poeira ao longo das fendas.
-- Aderencia: cada segmento e posicionado por RAYCAST PARA BAIXO a partir de 2 studs acima do ponto ANTERIOR (segue a
-- inclinacao, nunca pega teto/outro andar); a fenda para em parede (raycast horizontal) ou degrau > 1,2 stud.
-- Nada colide, nada e consultado por raycast de jogo (CanCollide/CanQuery/CanTouch falsos); Terrain e mapa intactos.
-- Valores visuais = LABORATORIO. Qualidade grafica baixa so reduz a quantidade de pecas (regra de combate nao muda).
-- v3 (04/11, "rachaduras mais altas"): no capim da Floresta a fenda rente ao chao sumia. Agora a terra LEVANTA dos dois
--   lados da fenda (placas de solo inclinadas, ate ~1,3 stud perto do centro, baixando para a ponta), na cor de TERRA
--   exposta (marrom, misturada 20% com a cor do chao); placas centrais e pedras maiores; poeira mais alta.
--   A altura depende do chao: sobre Terrain Grass/LeafyGrass (capim de ~2 studs) as bordas sobem ate 2,4; nos demais
--   chaos (pedra, terra, pecas) ficam em 0,8, para nao virar um amontoado de placas.
-- v4 (04/11, "mais poeira e pedras"): ERUPCOES ao longo das fendas, no ritmo em que elas crescem: coluna de poeira
--   que sobe acima do capim + pedras arremessadas (2,5-4,5 studs de altura) que caem perto. Le o terremoto mesmo onde
--   o capim esconde o chao. Substitui a poeira fraca que havia ao longo das fendas.
-- v5 (04/11, "3x mais ... em volta de todo seu corpo"): as fendas saem de TODO o contorno do corpo (elipse em volta
--   do urso, alem do ponto das patas) e vao ~3x mais longe (alcance = 2,45 x raio do golpe, ~34 studs com raio 14);
--   o passo do segmento cresce com a distancia (menos pecas longe); erupcoes em volta do corpo inteiro (ate 32).
--   O raio de DANO do servidor passou a 38 a partir do CENTRO do corpo (pedido do usuario) e o visual acompanha.
--   04/11: "aumente 2x mais o alcance" -> raio 76 (~66 studs de fendas a partir do contorno).
--   Medido 04/11: Debris guarda no maximo ~1000 itens e APAGA os mais antigos -> com ~2300 pecas so 967 apareciam
--   (um lado sem fendas). Pecas agora saem por task.delay proprio (Debris so para os poucos Attachments) e o total
--   caiu (menos ramificacoes, segmentos maiores longe, fendas do corpo sem ramo de 2o nivel).
-- Som: NENHUM audio do urso existe no projeto (M0 04/11) -> ganchos SOM_RUGIDO / SOM_IMPACTO vazios, a preencher.
local RS = game:GetService("RunService")
local TS = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local M = {}
M.VIS = {                -- LABORATORIO (visual)
	alcance = 0.87,              -- fracao do raio do golpe, a partir do contorno do corpo (raio 38 -> ~33 studs)
	fendasCorpo = 14, contorno = {3.8, 7.2},   -- fendas saindo do contorno do corpo (semi-eixos lateral, longitudinal)
	passoLonge = 0.10,           -- o passo cresce 0,10 stud por stud de distancia (alcance 2x: menos pecas longe)
	fendas = 6, ramificar = 0.16, passo = 0.85, desvio = 0.38,
	largura0 = 0.95, larguraPonta = 0.10, espessura = 0.05,
	velocidade = 45,             -- studs/s de crescimento
	placas = 9, pedras = 14,
	levante = 0.8, levanteCapim = 2.4, levanteMin = 0.35, corTerra = Color3.fromRGB(96, 74, 52),   -- bordas levantadas (studs)
	materiaisCapim = {Grass = true, LeafyGrass = true},   -- chao com capim alto do terreno (cobre ~2 studs, medido 04/11)
	duracao = 6.0, sumir = 1.5,
	tremorMax = 0.35, tremorDur = 0.55, tremorAlcance = 160,
	erupcoes = 44, pedrasErupcao = 3, alturaErupcao = {2.5, 4.5}, espacoErupcao = 5.5,
	qualidadeBaixa = {fendas = 4, fendasCorpo = 8, ramificar = 0.10, placas = 5, pedras = 6, erupcoes = 12, pedrasErupcao = 2},
}
M.SOM_RUGIDO = nil       -- rbxassetid do rugido quando existir (PENDENTE)
M.SOM_IMPACTO = nil      -- rbxassetid do impacto quando existir (PENDENTE)
local pasta = workspace:FindFirstChild("Urso_v2_EfeitosLab") or Instance.new("Folder")
pasta.Name = "Urso_v2_EfeitosLab"; pasta.Parent = workspace
M.pasta = pasta

local function params(urso)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
	local ex = {pasta, urso}; for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(ex, p.Character) end end
	for _, m in ipairs(game:GetService("CollectionService"):GetTagged("AlvoTesteUrso")) do table.insert(ex, m) end
	rp.FilterDescendantsInstances = ex; return rp
end
local function corChao(hit)
	if not hit then return Color3.fromRGB(110, 96, 80) end
	if hit.Instance:IsA("Terrain") then
		local ok, c = pcall(function() return workspace.Terrain:GetMaterialColor(hit.Material) end); if ok then return c end
	elseif hit.Instance:IsA("BasePart") then return hit.Instance.Color end
	return Color3.fromRGB(110, 96, 80)
end
local function escurecer(c, k) return Color3.new(c.R * k, c.G * k, c.B * k) end
local function peca(nome, cor, mat)
	local p = Instance.new("Part"); p.Name = nome; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Material = mat or Enum.Material.Slate; p.Color = cor; p.TopSurface = Enum.SurfaceType.Smooth
	return p
end
-- um segmento da fenda: fenda escura no fundo + DUAS placas de terra levantadas e inclinadas para fora, uma de cada
-- lado (altura h, que diminui do centro para a ponta). Nas pontas finas (h pequeno) fica so uma borda baixa.
local function segmento(a, b, n, larg, h, corBorda, corFenda, partes, atraso)
	local d = b - a; local len = d.Magnitude; if len < 0.05 then return end
	local meio = (a + b) / 2
	local cf = CFrame.lookAt(meio, meio + d, n)
	local novas = {}
	local fenda = peca("Fenda", corFenda, Enum.Material.Basalt)
	fenda.Size = Vector3.new(larg, M.VIS.espessura, len + 0.15); fenda.CFrame = cf + n * 0.03
	table.insert(novas, fenda)
	if h >= M.VIS.levanteMin then
		for _, lado in ipairs({-1, 1}) do
			local pl = peca("Levante", corBorda:Lerp(escurecer(corBorda, 0.75), math.random() * 0.6), Enum.Material.Ground)
			local alt = h * (0.75 + 0.5 * math.random())
			local ang = math.rad(28 + math.random() * 22)                  -- inclinada para fora
			pl.Size = Vector3.new(0.22 + 0.12 * math.random(), alt / math.cos(ang), len + 0.25)
			-- base na beira da fenda, gira em torno do eixo da fenda e sobe
			pl.CFrame = cf * CFrame.new(lado * (larg / 2 + 0.06), 0, 0) * CFrame.Angles(0, 0, -lado * ang) * CFrame.new(0, pl.Size.Y / 2 - 0.08, 0)
			table.insert(novas, pl)
		end
	else
		local borda = peca("Borda", corBorda, Enum.Material.Ground)
		borda.Size = Vector3.new(larg * 1.9, M.VIS.espessura * 1.6 + h * 0.4, len + 0.12); borda.CFrame = cf + n * (borda.Size.Y / 2 - 0.02)
		table.insert(novas, borda)
	end
	for _, p in ipairs(novas) do
		table.insert(partes, p)
		task.delay(atraso, function() if pasta.Parent then p.Parent = pasta end end)     -- cresce do centro para fora
	end
end
local function fenda(P, dir, compr, larg0, rp, corBorda, corFenda, partes, nivel, distBase, cfg)
	local V = M.VIS; local atual, dist = P, distBase or 0; local feito, s = 0, 0
	while feito < compr and s < 80 do
		s += 1
		local k = feito / compr
		local giro = (math.random() - 0.5) * 2 * V.desvio
		dir = (CFrame.Angles(0, giro, 0) * dir).Unit
		local passo = V.passo + dist * V.passoLonge                           -- longe: segmentos maiores (menos pecas)
		local alvo = atual + dir * passo * (0.75 + 0.5 * math.random())
		if workspace:Raycast(atual + Vector3.new(0, 0.6, 0), Vector3.new(alvo.X - atual.X, 0, alvo.Z - atual.Z), rp) then break end   -- parede
		local hit = workspace:Raycast(Vector3.new(alvo.X, atual.Y + 2.0, alvo.Z), Vector3.new(0, -4.0, 0), rp)
		if not hit or math.abs(hit.Position.Y - atual.Y) > 1.2 then break end                                  -- sem chao ou degrau
		local larg = larg0 + (V.larguraPonta - larg0) * k
		local d = (hit.Position - atual).Magnitude; dist += d; feito += d
		local h = cfg.levante * (1 - k) ^ 0.8 * (nivel == 0 and 1 or 0.55)
		segmento(atual, hit.Position, hit.Normal, larg, h, corBorda, corFenda, partes, dist / V.velocidade)
		if s % 3 == 0 then table.insert(cfg.erup, {pos = hit.Position, n = hit.Normal, t = dist / V.velocidade, nivel = nivel}) end
		if nivel < 1 and s > 1 and k < 0.8 and math.random() < cfg.ramificar then
			local lado = math.random() < 0.5 and -1 or 1
			local dirR = (CFrame.Angles(0, lado * math.rad(30 + math.random() * 28), 0) * dir).Unit
			fenda(hit.Position, dirR, (compr - feito) * (0.35 + 0.25 * math.random()), larg * 0.6, rp, corBorda, corFenda, partes, nivel + 1, dist, cfg)
		end
		atual = hit.Position
	end
end
function M.rachaduras(P, N, urso, raio)
	local V = M.VIS; local rp = params(urso)
	local q = settings().Rendering.QualityLevel.Value
	local baixa = q > 0 and q <= 3
	local cfg = {fendas = baixa and V.qualidadeBaixa.fendas or V.fendas, ramificar = baixa and V.qualidadeBaixa.ramificar or V.ramificar,
		placas = baixa and V.qualidadeBaixa.placas or V.placas, pedras = baixa and V.qualidadeBaixa.pedras or V.pedras,
		fendasCorpo = baixa and V.qualidadeBaixa.fendasCorpo or V.fendasCorpo,
		erupcoes = baixa and V.qualidadeBaixa.erupcoes or V.erupcoes, pedrasErupcao = baixa and V.qualidadeBaixa.pedrasErupcao or V.pedrasErupcao, erup = {}}
	local hit0 = workspace:Raycast(P + Vector3.new(0, 1.0, 0), Vector3.new(0, -2.5, 0), rp)
	local base = corChao(hit0)
	local corBorda = V.corTerra:Lerp(base, 0.2)                     -- terra exposta (o capim nao 'racha' verde)
	local corFenda = escurecer(V.corTerra, 0.22)
	local partes = {}
	local alcance = (raio or 14) * V.alcance
	local capim = hit0 and hit0.Instance:IsA("Terrain") and V.materiaisCapim[hit0.Material.Name] or false
	cfg.levante = capim and V.levanteCapim or V.levante; M.ultimoChao = hit0 and hit0.Material.Name or "?"
	-- 1) fendas que saem do ponto das patas (mais curtas: o resto do alcance vem do contorno do corpo)
	for i = 1, cfg.fendas do
		local ang = (i / cfg.fendas) * math.pi * 2 + (math.random() - 0.5) * 0.6
		local compr = alcance * (0.35 + 0.2 * math.random())
		fenda(P, Vector3.new(math.cos(ang), 0, math.sin(ang)), compr, V.largura0 * (0.8 + 0.4 * math.random()), rp, corBorda, corFenda, partes, 0, 0, cfg)
	end
	-- 2) fendas que saem de TODO o contorno do corpo (elipse em volta do urso), apontando para fora
	if urso and urso.Parent then
		local cf = urso:GetPivot(); local la, lo = V.contorno[1], V.contorno[2]
		for i = 1, cfg.fendasCorpo do
			local th = (i / cfg.fendasCorpo) * math.pi * 2 + (math.random() - 0.5) * 0.3
			local loc = Vector3.new(math.cos(th) * la, 0, math.sin(th) * lo)
			local w = cf:PointToWorldSpace(loc)
			local normal = cf:VectorToWorldSpace(Vector3.new(math.cos(th) / la, 0, math.sin(th) / lo)); normal = Vector3.new(normal.X, 0, normal.Z).Unit
			local h0 = workspace:Raycast(Vector3.new(w.X, P.Y + 2.0, w.Z), Vector3.new(0, -4.0, 0), rp)
			if h0 and not workspace:Raycast(P + Vector3.new(0, 0.6, 0), Vector3.new(w.X - P.X, 0, w.Z - P.Z), rp) then
				local compr = alcance * (0.7 + 0.3 * math.random())
				fenda(h0.Position, normal, compr, V.largura0 * (0.9 + 0.4 * math.random()), rp, corBorda, corFenda, partes, 0, (h0.Position - P).Magnitude, cfg)
			end
		end
	end
	-- centro: afundamento escuro + placas de chao quebradas, inclinadas para fora
	local c = peca("Afundamento", corFenda, Enum.Material.Basalt)
	c.Shape = Enum.PartType.Cylinder; c.Size = Vector3.new(0.06, 2.6, 2.6)
	c.CFrame = CFrame.lookAt(P + N * 0.03, P + N * 1.03) * CFrame.Angles(0, math.rad(90), 0); c.Parent = pasta; table.insert(partes, c)
	for i = 1, cfg.placas do
		local ang = (i / cfg.placas) * math.pi * 2 + math.random() * 0.5
		local r = 1.4 + math.random() * 1.6
		local o = P + Vector3.new(math.cos(ang) * r, 0, math.sin(ang) * r)
		local h = not workspace:Raycast(P + Vector3.new(0, 0.6, 0), o - P, rp) and workspace:Raycast(o + Vector3.new(0, 2, 0), Vector3.new(0, -4, 0), rp)
		if h then
			local pl = peca("Placa", corBorda:Lerp(escurecer(corBorda, 0.7), math.random() * 0.5), Enum.Material.Ground)
			pl.Size = Vector3.new(1.2 + math.random() * 1.1, 0.35 + math.random() * 0.25, 1.0 + math.random() * 1.0)
			local fora = Vector3.new(math.cos(ang), 0, math.sin(ang))
			pl.CFrame = CFrame.lookAt(h.Position, h.Position + fora, h.Normal) * CFrame.Angles(math.rad(-(28 + math.random() * 26)), math.rad(math.random() * 40 - 20), 0) + h.Normal * 0.35
			pl.Parent = pasta; table.insert(partes, pl)
		end
	end
	-- pedras: saltam do centro e assentam no chao (so visual, ancoradas, animadas por tween)
	for i = 1, cfg.pedras do
		local ang = math.random() * math.pi * 2; local r = 2 + math.random() * 4.5
		local o = P + Vector3.new(math.cos(ang) * r, 0, math.sin(ang) * r)
		local h = not workspace:Raycast(P + Vector3.new(0, 0.6, 0), o - P, rp) and workspace:Raycast(o + Vector3.new(0, 2, 0), Vector3.new(0, -4, 0), rp)
		if h then
			local s = 0.4 + math.random() * 0.6
			local pd = peca("Pedra", escurecer(corBorda:Lerp(Color3.fromRGB(110, 105, 100), 0.5), 0.6 + math.random() * 0.3), Enum.Material.Slate)
			pd.Size = Vector3.new(s, s * 0.7, s * 1.1); pd.CFrame = CFrame.new(P + N * 0.4) * CFrame.Angles(math.random() * 3, math.random() * 3, 0)
			pd.Parent = pasta; table.insert(partes, pd)
			local topo = (P + h.Position) / 2 + Vector3.new(0, 1.2 + math.random() * 1.8, 0)
			local t1 = 0.18 + math.random() * 0.1
			TS:Create(pd, TweenInfo.new(t1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = CFrame.new(topo) * CFrame.Angles(math.random() * 3, math.random() * 3, 0)}):Play()
			task.delay(t1, function()
				if pd.Parent then TS:Create(pd, TweenInfo.new(t1 * 1.1, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = CFrame.lookAt(h.Position + h.Normal * s * 0.3, h.Position + h.Normal * s * 0.3 + Vector3.new(math.random() - 0.5, 0, math.random() - 0.5), h.Normal)}):Play() end
			end)
		end
	end
	-- poeira: no centro e em pontos ao longo das fendas
	local function poeira(pos, n, atraso)
		task.delay(atraso, function()
			local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain
			local pe = Instance.new("ParticleEmitter"); pe.Texture = "rbxasset://textures/particles/smoke_main.dds"
			pe.Color = ColorSequence.new(base:Lerp(Color3.fromRGB(170, 160, 145), 0.4))
			pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.2), NumberSequenceKeypoint.new(1, 4.5)})
			pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.4), NumberSequenceKeypoint.new(1, 1)})
			pe.Lifetime = NumberRange.new(0.8, 1.6); pe.Speed = NumberRange.new(5, 12); pe.SpreadAngle = Vector2.new(70, 20)
			pe.Drag = 3; pe.EmissionDirection = Enum.NormalId.Top; pe.Rate = 0; pe.Parent = a; pe:Emit(n)
			Debris:AddItem(a, 2.2)
		end)
	end
	poeira(P + N * 0.3, baixa and 14 or 30, 0)
	-- erupcoes: pontos ao longo das fendas (principais primeiro), espalhados; poeira alta + pedras arremessadas
	table.sort(cfg.erup, function(a, b) return a.nivel < b.nivel end)
	local escolhidos = {}
	for _, e in ipairs(cfg.erup) do
		local longe = true
		for _, o in ipairs(escolhidos) do if (o.pos - e.pos).Magnitude < V.espacoErupcao then longe = false; break end end
		if longe then table.insert(escolhidos, e) end
		if #escolhidos >= cfg.erupcoes then break end
	end
	local corPedra = escurecer(corBorda:Lerp(Color3.fromRGB(110, 105, 100), 0.4), 0.75)
	for _, e in ipairs(escolhidos) do
		task.delay(e.t, function()
			if not pasta.Parent then return end
			local a = Instance.new("Attachment"); a.WorldPosition = e.pos + e.n * 0.4; a.Parent = workspace.Terrain
			local pe = Instance.new("ParticleEmitter"); pe.Texture = "rbxasset://textures/particles/smoke_main.dds"
			pe.Color = ColorSequence.new(V.corTerra:Lerp(Color3.fromRGB(175, 160, 140), 0.45))
			pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.6), NumberSequenceKeypoint.new(1, 5.5)})
			pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.25), NumberSequenceKeypoint.new(0.6, 0.6), NumberSequenceKeypoint.new(1, 1)})
			pe.Lifetime = NumberRange.new(1.2, 2.2); pe.Speed = NumberRange.new(6, 11); pe.SpreadAngle = Vector2.new(25, 25)
			pe.Acceleration = Vector3.new(0, -3, 0); pe.Drag = 2; pe.EmissionDirection = Enum.NormalId.Top; pe.Rate = 0; pe.Parent = a
			pe:Emit(baixa and 5 or 10); Debris:AddItem(a, 2.6)
			for j = 1, cfg.pedrasErupcao do
				local ang = math.random() * math.pi * 2; local r = 0.8 + math.random() * 2.2
				local o = e.pos + Vector3.new(math.cos(ang) * r, 0, math.sin(ang) * r)
				local h = not workspace:Raycast(e.pos + Vector3.new(0, 0.6, 0), o - e.pos, rp) and workspace:Raycast(o + Vector3.new(0, 2, 0), Vector3.new(0, -4, 0), rp)
				if h then
					local s = 0.35 + math.random() * 0.45
					local pd = peca("Pedra", corPedra:Lerp(escurecer(corPedra, 0.6), math.random()), Enum.Material.Slate)
					pd.Size = Vector3.new(s, s * 0.75, s * 1.15); pd.CFrame = CFrame.new(e.pos + e.n * 0.3); pd.Parent = pasta; table.insert(partes, pd)
					local alt = V.alturaErupcao[1] + math.random() * (V.alturaErupcao[2] - V.alturaErupcao[1])
					local t1 = 0.22 + math.random() * 0.12
					TS:Create(pd, TweenInfo.new(t1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = CFrame.new((e.pos + h.Position) / 2 + Vector3.new(0, alt, 0)) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)}):Play()
					task.delay(t1, function()
						if pd.Parent then TS:Create(pd, TweenInfo.new(t1 * 1.15, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = CFrame.lookAt(h.Position + h.Normal * s * 0.3, h.Position + h.Normal * s * 0.3 + Vector3.new(math.random() - 0.5, 0, math.random() - 0.5), h.Normal)}):Play() end
					end)
					task.delay(V.duracao - V.sumir - e.t, function() if pd.Parent then TS:Create(pd, TweenInfo.new(V.sumir), {Transparency = 1}):Play() end end)
					task.delay(V.duracao + 0.1 - e.t, function() pd:Destroy() end)
				end
			end
		end)
	end
	M.ultimasErupcoes = #escolhidos
	for _, p in ipairs(partes) do
		task.delay(V.duracao - V.sumir, function() if p.Parent then TS:Create(p, TweenInfo.new(V.sumir), {Transparency = 1}):Play() end end)
		task.delay(V.duracao + 0.1, function() p:Destroy() end)          -- nao usar Debris (limite de ~1000 itens)
	end
	return #partes, alcance
end
function M.tremor(P)
	local cam = workspace.CurrentCamera; if not cam then return end
	local d = (cam.CFrame.Position - P).Magnitude; if d > M.VIS.tremorAlcance then return end
	local amp = M.VIS.tremorMax * (1 - d / M.VIS.tremorAlcance); local t0 = os.clock()
	local nome = "TremorUrso" .. tostring(t0)
	RS:BindToRenderStep(nome, Enum.RenderPriority.Camera.Value + 2, function()
		local k = (os.clock() - t0) / M.VIS.tremorDur
		if k >= 1 then RS:UnbindFromRenderStep(nome); return end
		local a = amp * (1 - k)
		cam.CFrame = cam.CFrame * CFrame.new(math.noise(k * 20, 1) * a, math.noise(k * 20, 2) * a, 0)
	end)
end
local function som(id, pos)                 -- som 3D no ponto (nao global), alcance limitado
	if not id then return end
	local at = Instance.new("Attachment"); at.WorldPosition = pos; at.Parent = workspace.Terrain
	local s = Instance.new("Sound"); s.SoundId = id; s.RollOffMaxDistance = 120; s.Parent = at; s:Play(); Debris:AddItem(at, 5)
end
-- ================================================================== Rugido Protetor (Etapa 2, 04/11) - so visual
-- [historico] v2 (04/11, pedido do usuario: "algo envolvendo particulas ... que sai do treinador e do urso, e efeito especial na
-- hora do rugido"). Cores ambar/douradas NEUTRAS (o elemento do urso continua PENDENTE: nada de folhas/raizes).
--   * RUGIDO: da boca saem ONDAS DE SOM (aneis translucidos que avancam e crescem, um a cada ~0,16 s enquanto ruge),
--     um sopro de particulas para a frente, um clarao curto na cabeca e poeira levantando em volta das patas;
--   * EFEITO (pico): onda no chao + coluna de particulas douradas que SOBE de cada alvo (urso e treinador);
--   * BONUS ATIVO: de cada alvo saem continuamente brasas douradas subindo em espiral, um brilho fraco e um anel
--     fino nos pes. Nada esconde os personagens (sem Highlight/neblina; transparencia alta). Sai no "fim" do bonus.
-- Qualidade grafica baixa: metade das particulas e menos ondas (so visual).
-- v3 (04/11, pedido do usuario: "aura saindo do rugido ... e quando estiver com a protecao, uma aura AZUL em volta dos
--   dois, nao um redondo em volta deles"): tudo em AZUL; sem anel nem disco no chao. A aura da protecao CONTORNA o
--   corpo (Highlight com contorno azul e preenchimento quase invisivel, so onde o alvo esta a vista: nao atravessa
--   paredes) + chamas de energia azul subindo em volta do corpo. No rugido, a aura sai da boca: ondas azuis, sopro de
--   energia e uma nuvem de energia que se espalha a partir do urso.
M.SOM_RUGIDO_PROTETOR = nil      -- rbxassetid do rugido protetor quando existir (PENDENTE)
M.VIS_RP = {cor = Color3.fromRGB(70, 160, 255), cor2 = Color3.fromRGB(175, 225, 255), raioOnda = 40, durOnda = 0.9,
	ondasSom = 9, intervaloSom = 0.16, alcanceSom = 16, brasas = 14, duracaoRugido = 1.5, focos = 6}   -- focos: pontos em volta do corpo de onde as particulas sobem
local auras = {}                 -- [alvo] = {pecas, at, emissores, luz, con}
local function baixaQ() local q = settings().Rendering.QualityLevel.Value; return q > 0 and q <= 3 end
local function pecaRP(nome)
	local p = Instance.new("Part"); p.Name = nome; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Material = Enum.Material.Neon; p.Color = M.VIS_RP.cor; p.Shape = Enum.PartType.Cylinder; return p
end
local function chaoSob(pos, ex)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = ex
	local h = workspace:Raycast(pos + Vector3.new(0, 1, 0), Vector3.new(0, -12, 0), rp); return h and h.Position or pos
end
local function emissor(pai, t)
	local pe = Instance.new("ParticleEmitter")
	for k, v in pairs(t) do pe[k] = v end
	pe.Parent = pai; return pe
end
local function tirarAura(alvo)
	local a = auras[alvo]; if not a then return end; auras[alvo] = nil
	if a.con then a.con:Disconnect() end
	for _, p in ipairs(a.pecas) do if p.Parent then TS:Create(p, TweenInfo.new(0.4), {Transparency = 1}):Play(); task.delay(0.45, function() p:Destroy() end) end end
	for _, e in ipairs(a.emissores) do e.Enabled = false end
	if a.luz then TS:Create(a.luz, TweenInfo.new(0.5), {Brightness = 0}):Play() end
	if a.hl then TS:Create(a.hl, TweenInfo.new(0.5), {OutlineTransparency = 1, FillTransparency = 1}):Play(); local h = a.hl; task.delay(0.55, function() h:Destroy() end) end
	task.delay(2.0, function() if a.at then a.at:Destroy() end; for _, f in ipairs(a.focos or {}) do f:Destroy() end end)
end
local function porAura(alvo, dur)
	tirarAura(alvo)
	local base = alvo:FindFirstChild("HumanoidRootPart") or alvo:FindFirstChild("Pelve", true) or alvo.PrimaryPart or alvo:FindFirstChildWhichIsA("BasePart", true)
	if not base then return end
	local V = M.VIS_RP; local baixa = baixaQ()
	local ext = alvo:GetExtentsSize(); local r = math.clamp(math.max(ext.X, ext.Z) * 0.55, 2.0, 6)
	local hl = Instance.new("Highlight"); hl.Adornee = alvo; hl.FillColor = V.cor; hl.FillTransparency = 0.76; hl.OutlineColor = V.cor
	hl.OutlineTransparency = 1; hl.DepthMode = Enum.HighlightDepthMode.Occluded; hl.Parent = pasta
	TS:Create(hl, TweenInfo.new(0.35), {OutlineTransparency = 0.15}):Play()
	-- focos de particulas em VOLTA do corpo (fora da malha: de dentro do urso nada apareceria), na altura dos pes
	local baixaF = baixa and math.ceil(V.focos / 2) or V.focos
	local ks = function(a, b) return NumberSequence.new({NumberSequenceKeypoint.new(0, a), NumberSequenceKeypoint.new(1, b)}) end
	local focos, emissores = {}, {}
	for i = 1, baixaF do
		local at = Instance.new("Attachment"); at.Parent = workspace.Terrain; focos[i] = at
		table.insert(emissores, emissor(at, {Texture = "rbxasset://textures/particles/sparkles_main.dds", Color = ColorSequence.new(V.cor2, V.cor),
			LightEmission = 1, LightInfluence = 0, Size = ks(0.7, 0.1), Transparency = ks(0, 1), Lifetime = NumberRange.new(1.0, 1.8),
			Rate = baixa and 6 or 10, Speed = NumberRange.new(3, 6), SpreadAngle = Vector2.new(12, 12), EmissionDirection = Enum.NormalId.Top,
			Acceleration = Vector3.new(0, 2, 0), RotSpeed = NumberRange.new(-180, 180)}))
		table.insert(emissores, emissor(at, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(V.cor),
			LightEmission = 0.8, LightInfluence = 0, Size = ks(1.0, 2.6), Transparency = ks(0.6, 1), Lifetime = NumberRange.new(0.9, 1.4),
			Rate = baixa and 3 or 6, Speed = NumberRange.new(2, 4), EmissionDirection = Enum.NormalId.Top}))
	end
	local altura = math.max(ext.Y, 4)
	local luzAt = Instance.new("Attachment"); luzAt.Parent = workspace.Terrain
	local luz = Instance.new("PointLight"); luz.Color = V.cor; luz.Range = r * 3; luz.Brightness = 1.4; luz.Shadows = false; luz.Parent = luzAt
	local a = {pecas = {}, at = luzAt, focos = focos, emissores = emissores, luz = luz, hl = hl}
	local t0 = os.clock()
	a.con = RS.RenderStepped:Connect(function()
		if not alvo.Parent then tirarAura(alvo); return end
		local piv = alvo:GetPivot(); local pos = chaoSob(piv.Position, {alvo, pasta})
		hl.OutlineTransparency = 0.15 + 0.25 * (0.5 + 0.5 * math.sin((os.clock() - t0) * 5))   -- aura pulsando
		local giro = (os.clock() - t0) * 1.2                                  -- os focos giram devagar em volta (espiral)
		for i, at in ipairs(focos) do
			local ang = giro + (i / #focos) * math.pi * 2
			at.WorldPosition = pos + Vector3.new(math.cos(ang) * r * 0.7, 0.3 + (i % 3) * altura * 0.3, math.sin(ang) * r * 0.7)
		end
		luzAt.WorldPosition = pos + Vector3.new(0, altura * 0.5, 0)
	end)
	auras[alvo] = a
	task.delay(dur + 2, function() if auras[alvo] == a then tirarAura(alvo) end end)        -- seguranca: nunca fica para sempre
end
-- explosao de particulas que sobe de um alvo no pico (coluna dourada)
local function coluna(alvo)
	local pos = alvo:GetPivot().Position
	local at = Instance.new("Attachment"); at.WorldPosition = chaoSob(pos, {alvo, pasta}) + Vector3.new(0, 0.3, 0); at.Parent = workspace.Terrain
	local V = M.VIS_RP; local n = baixaQ() and 40 or 90
	local pe = emissor(at, {Texture = "rbxasset://textures/particles/sparkles_main.dds", Color = ColorSequence.new(V.cor2, V.cor), LightEmission = 1,
		LightInfluence = 0, Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.9), NumberSequenceKeypoint.new(1, 0.1)}),
		Transparency = NumberSequence.new(0, 1), Lifetime = NumberRange.new(0.9, 1.5), Rate = 0, Speed = NumberRange.new(12, 22),
		SpreadAngle = Vector2.new(25, 25), EmissionDirection = Enum.NormalId.Top, Drag = 2, Acceleration = Vector3.new(0, 2, 0)})
	pe:Emit(n); Debris:AddItem(at, 2)
end
-- ondas de som saindo da boca enquanto o urso ruge
local function ondasDeSom(urso)
	local V = M.VIS_RP; local baixa = baixaQ()
	local mand = urso:FindFirstChild("Mandibula", true); local cab = urso:FindFirstChild("Cabeca", true)
	local n = baixa and math.ceil(V.ondasSom / 2) or V.ondasSom
	-- clarao curto na cabeca + sopro de particulas para a frente
	if cab then
		local at = Instance.new("Attachment"); at.Parent = workspace.Terrain
		local luz = Instance.new("PointLight"); luz.Color = V.cor; luz.Range = 18; luz.Brightness = 3; luz.Shadows = false; luz.Parent = at
		local sopro = emissor(at, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(V.cor2), LightEmission = 0.6,
			LightInfluence = 0.3, Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(1, 5)}),
			Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(1, 1)}), Lifetime = NumberRange.new(0.6, 1.0),
			Rate = baixa and 10 or 22, Speed = NumberRange.new(14, 22), SpreadAngle = Vector2.new(14, 14), Drag = 3})
		local t0 = os.clock()
		local con; con = RS.RenderStepped:Connect(function()
			if not urso.Parent or os.clock() - t0 > V.duracaoRugido then con:Disconnect(); sopro.Enabled = false; TS:Create(luz, TweenInfo.new(0.4), {Brightness = 0}):Play(); Debris:AddItem(at, 1.5); return end
			local p = (mand or cab).TransformedWorldCFrame.Position; local f = urso:GetPivot().LookVector
			at.CFrame = CFrame.lookAt(p, p + f) * CFrame.Angles(math.rad(-90), 0, 0)      -- a "frente" do emissor (Top) aponta para onde o urso olha
			luz.Brightness = 3 * (1 - (os.clock() - t0) / V.duracaoRugido) + 0.5
		end)
	end
	-- poeira levantando em volta das patas (o chao "treme" com o rugido)
	local pe0 = chaoSob(urso:GetPivot().Position, {urso, pasta})
	local atp = Instance.new("Attachment"); atp.WorldPosition = pe0 + Vector3.new(0, 0.3, 0); atp.Parent = workspace.Terrain
	local po = emissor(atp, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(Color3.fromRGB(170, 150, 120)),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.5), NumberSequenceKeypoint.new(1, 4)}), Transparency = NumberSequence.new(0.5, 1),
		Lifetime = NumberRange.new(0.8, 1.4), Rate = 0, Speed = NumberRange.new(6, 10), SpreadAngle = Vector2.new(85, 5), Drag = 3,
		EmissionDirection = Enum.NormalId.Top})
	po:Emit(baixa and 10 or 22); Debris:AddItem(atp, 2)
	-- aneis de som: cada um nasce na boca, avanca e cresce, e some
	for i = 1, n do
		task.delay((i - 1) * V.intervaloSom, function()
			if not urso.Parent then return end
			local p = ((mand or cab) and (mand or cab).TransformedWorldCFrame.Position) or urso:GetPivot().Position
			local f = urso:GetPivot().LookVector
			local anel = pecaRP("OndaSom"); anel.Material = Enum.Material.Neon; anel.Color = V.cor; anel.Transparency = 0.72   -- translucido: nao esconde o treinador
			anel.Size = Vector3.new(0.15, 1.2, 1.2); anel.CFrame = CFrame.lookAt(p, p + f) * CFrame.Angles(0, math.rad(90), 0); anel.Parent = pasta
			local fim = CFrame.lookAt(p + f * V.alcanceSom, p + f * (V.alcanceSom + 1)) * CFrame.Angles(0, math.rad(90), 0)
			TS:Create(anel, TweenInfo.new(0.7, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = fim, Size = Vector3.new(0.15, 11, 11), Transparency = 1}):Play()
			task.delay(0.75, function() anel:Destroy() end)
		end)
	end
end
function M.rugidoProtetorEfx(d)
	if d.fase == "rugido" and d.urso then
		local cab = d.urso:FindFirstChild("Cabeca", true); som(M.SOM_RUGIDO_PROTETOR, cab and cab.TransformedWorldCFrame.Position or d.urso:GetPivot().Position)
		ondasDeSom(d.urso); M.ultimoRugido = os.clock()
	elseif d.fase == "efeito" and d.urso then
		-- nuvem de energia azul que se espalha a partir do urso (a "aura" do rugido chegando ao treinador)
		local c = chaoSob(d.urso:GetPivot().Position, {d.urso, pasta})
		local atn = Instance.new("Attachment"); atn.WorldPosition = c + Vector3.new(0, 2.5, 0); atn.Parent = workspace.Terrain
		local nv = emissor(atn, {Texture = "rbxasset://textures/particles/smoke_main.dds", Color = ColorSequence.new(M.VIS_RP.cor2, M.VIS_RP.cor),
			LightEmission = 0.8, LightInfluence = 0, Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 2), NumberSequenceKeypoint.new(1, 7)}),
			Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(1, 1)}), Lifetime = NumberRange.new(0.8, 1.2),
			Rate = 0, Speed = NumberRange.new(16, 26), SpreadAngle = Vector2.new(180, 8), Drag = 4, EmissionDirection = Enum.NormalId.Top})
		nv:Emit(baixaQ() and 20 or 45); Debris:AddItem(atn, 2)
		for _, alvo in ipairs(d.alvos or {}) do coluna(alvo); porAura(alvo, d.duracao or 10) end
		M.ultimoRP = {alvos = #(d.alvos or {}), t = os.clock()}
	elseif d.fase == "fim" and d.alvo then
		tirarAura(d.alvo)
	end
end
M.auras = auras
function M.iniciar(remotos)
	if M.con then return end
	M.con = remotos.Efeitos.OnClientEvent:Connect(function(d)
		if d.tipo == "RugidoProtetor" then M.rugidoProtetorEfx(d); return end
		if d.tipo ~= "GolpeColossal" then return end
		if d.fase == "rugido" and d.urso then
			local cab = d.urso:FindFirstChild("Cabeca", true); som(M.SOM_RUGIDO, cab and cab.TransformedWorldCFrame.Position or d.urso:GetPivot().Position)
			M.rugidos = (M.rugidos or 0) + 1
		elseif d.fase == "impacto" and d.pos then
			local n, alc = M.rachaduras(d.pos, d.normal or Vector3.yAxis, d.urso, d.raio)
			M.ultimo = {n = n, alcance = alc, t = os.clock()}
			M.tremor(d.pos); som(M.SOM_IMPACTO, d.pos)
		end
	end)
end
return M
]=====]; c.Parent = lab
return string.format("KFS kf=%d poses=%d faltam=%s impacto=%s | dados=%d | modulos ok", #kfs:GetChildren(), np, table.concat(faltam, ","), tostring(kfs:GetAttribute("ImpactoS")), #P.Dados_Clipes.Urso_GolpeColossal.Value)
