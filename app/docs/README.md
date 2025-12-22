# App: Contadores de Impressoras

Estrutura organizada do projeto e instruções.

Pasta `app/`:
- `src/`: scripts Python principais.
- `data/`: arquivos de exemplo e evidências (ips, e-mails, mappings, rascunhos).
- `gui/`: código da interface gráfica (launcher e telas).
- `docs/`: documentação adicional.

Como rodar (Windows):

1. Instale dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Iniciar via `start_app.bat` (na raiz do repositório).

Testes:
- Instale `pytest` (já incluído em `app/requirements.txt`).
- Rode a suíte de testes a partir da raiz do repositório:

```powershell
cd D:\Contadores Impressoras
.\.venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
pytest -q app/tests
```

Credenciais SMTP:
- Use `app/src/store_smtp_creds.py set <user>` para salvar sua senha de forma segura no keyring do sistema.
- A GUI tenta buscar a senha no keyring se o campo senha estiver vazio.

Validações e Execução:
- A GUI agora valida campos obrigatórios antes de executar ações (e-mail, IPs).
- SMTP: validação de porta numérica ao salvar configuração.

Observações:
- O `start_app.bat` foi projetado para permanecer na raiz; todo o resto está em `app/`.
- A GUI adiciona opções para executar consultas SNMP, gerar rascunhos e visualizar mapping.
