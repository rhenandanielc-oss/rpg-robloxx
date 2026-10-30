---
name: roblox-patch
description: Mudar scripts do jogo Roblox deste RPG com segurança - editar em src/ (Rojo) ou, sem Rojo conectado, aplicar patch tudo-ou-nada no Studio com âncoras únicas, checagem de compilação e backup em ServerStorage. Use sempre que for alterar um script do jogo (IA, combate, montaria, VFX, sons, câmera).
---

# Patch de scripts do RPG (Roblox)

Antes de tudo: CLAUDE.md exige autorização do usuário para mexer no Studio na tarefa atual. Inspecione primeiro (somente leitura).

## Caminho preferido: Rojo
1. O código do jogo vive em `src/` (mapeado por `default.project.json`; todos os nós com `$ignoreUnknownInstances: true`, então o Rojo não apaga clipes, sons nem backups).
2. Edite o arquivo em `src/`, confira com `rojo build default.project.json -o %TEMP%\teste.rbxl` (compila o projeto) e faça commit no git com mensagem clara.
3. O usuário conecta o plugin Rojo no Studio (`rojo serve` na raiz) para sincronizar. Nunca rode `rojo serve` + sincronização sem avisar: a sincronização substitui no Studio os scripts mapeados.
4. Script novo: crie o arquivo em `src/` e rode `python -I tools/gerar_projeto_rojo.py .` para atualizar o projeto.
5. Se o Studio foi editado fora do Rojo, reexporte antes de editar arquivos (`tools/montar_src_rojo.py`), senão o arquivo sobrescreve a mudança do Studio.

## Sem Rojo: patch tudo-ou-nada no Studio (modo Edit, Play parado)
- Arquivo `.luau` local servido em `http://127.0.0.1:8766` e aplicado com `loadstring(HttpService:GetAsync(url))()`.
- Estrutura obrigatória:
  - marcador `PATCH_<NOME>` → se já existir no Source, `return "ja aplicado"`;
  - `troca(src, antigo, novo)` com `string.find(..., 1, true)`, `assert` de âncora encontrada e ÚNICA (não repetida); prefira âncoras de uma linha;
  - `assert(loadstring(novoSource))` para cada script antes de gravar;
  - backup único `ServerStorage.Backup_<Nome>` com `:Clone()` dos scripts (não sobrescrever backup existente);
  - só então atribuir `.Source`.
- Use strings longas `[=[ ... ]=]` (código terminando em `]` quebra `[[ ]]`).
- Chamadas `execute_luau` curtas (< ~25 s) ou a conexão MCP cai.
- Depois de aplicar no Studio, reexporte para `src/` e faça commit (o git é a fonte da verdade).

## Regras do jogo que todo patch respeita
- Servidor valida tudo (dano, moedas, inventário, loot, montaria); cliente só envia intenção.
- Números experimentais marcados `NAO_APROVADO`; não inventar habilidades nem regras oficiais.
- Teste em Play com evidência (log/captura) antes de dizer que funciona; registre em PROJECT-STATE.
