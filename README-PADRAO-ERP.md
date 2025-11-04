# Padronização ERP v1 (simples)

Este pacote adiciona:
- `.gitignore` (não enviar `venv` para o Git)
- Qualidade: `pre-commit` (ruff/black/isort/mypy)
- Docker e Docker Compose para rodar local
- `Makefile` com comandos rápidos
- Logs estruturados e erros padronizados

## Como usar (passo a passo, sem código)

1. Baixe o arquivo ZIP que te enviei.
2. Entre no seu repositório no GitHub: `fisgarone/fisgarone_erp`.
3. Clique em **Add file** → **Upload files**.
4. Arraste **todo o conteúdo do ZIP** para a raiz do repositório.
5. No rodapé, em **Commit changes**, escolha **Create a new branch** e nomeie `chore/padrao-erp-v1`.
6. Clique em **Propose changes** e depois **Create pull request**.
7. Revise o PR e clique em **Merge** quando estiver tudo certo.

### Depois do merge
- No computador:
  ```bash
  pip install -r requirements.txt
  pre-commit install
  cp .env.example .env
  docker compose up -d --build
  docker compose run --rm migrate
  ```

### Dica
- Renomear `app/models/init.py` para `app/models/__init__.py` (no GitHub, abra o arquivo, clique no ícone de **lápis**, depois no **...** e **Rename**).

Pronto! Seu projeto fica com padrão de ERP profissional sem mudar sua lógica atual.
