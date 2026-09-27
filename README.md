# Gerenciador de Conselhos API

Projeto de estudo com FastAPI. Consulta a API pública Advice Slip, transforma o conselho em
maiúsculas/minúsculas e mantém um histórico local em SQLite. A integração não utiliza chave.
Precisa de internet para buscar novos conselhos; o histórico funciona localmente.

## Começar no Windows (PowerShell / terminal do VS Code)

Instale Python 3.11 ou superior e Git. Abra o terminal na pasta que contém `pyproject.toml`.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Copie o `.env` apenas se ainda não tiver um; preserve configurações existentes.
Os comandos usam diretamente o Python do ambiente virtual, sem precisar ativar scripts
ou mudar a política de execução do PowerShell. Se `py` não existir, use `python`.

Abra http://localhost:8000/docs para testar. Encerre com Ctrl+C. O banco é criado no
primeiro início, em `data/conselhos.db`. A raiz `/` não tem página; utilize `/docs`.

### Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
cp -n .env.example .env
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

### Alternativa com uv

O `uv.lock` registra as versões resolvidas. Para reproduzir esse ambiente:

```bash
uv sync --frozen --extra dev
uv run --frozen --extra dev uvicorn app.main:app --reload --port 8000
```

`pip install -e ".[dev]"` respeita as faixas do pyproject; não utiliza o uv.lock.
Para só executar, sem ferramentas de desenvolvimento, use `pip install -e .`.

## Bibliotecas e para que servem

| Biblioteca | Função |
| --- | --- |
| FastAPI | Rotas HTTP, validação de parâmetros e documentação `/docs`. |
| Uvicorn | Servidor que executa a aplicação. |
| HTTPX | Requisições assíncronas para a API Advice Slip. |
| Pydantic | Validação dos conselhos recebidos e modelos das respostas. |
| pydantic-settings | Configuração por variáveis de ambiente e `.env`. |
| pytest (dev) | Executa os testes automatizados. |
| Ruff (dev) | Verifica estilo, imports e formatação. |
| mypy (dev) | Verifica a tipagem. |
| sqlite3 | Banco SQLite; já vem com Python, sem instalação separada. |

As dependências transitivas são instaladas automaticamente. `pytest-mock` e
`pytest-asyncio` não são necessários: os testes usam TestClient, MockTransport e
fixtures nativas do pytest. Se a sua rede usa proxy SOCKS, instale opcionalmente
`python -m pip install "httpx[socks]"` no mesmo ambiente.

## Rotas e compatibilidade

| Requisição | Resultado |
| --- | --- |
| `GET /advice` | Busca, transforma e salva o conselho. |
| `GET /advice?save=false` | Busca e transforma sem salvar. |
| `GET /historico` | Últimos 15 registros, exibidos do mais antigo ao mais novo. |
| `GET /historico?last=3` | Últimos 3; aceita limites de 1 a 100. |

As rotas, parâmetros e campos das respostas anteriores foram preservados.
`fetched_at` agora inclui explicitamente o fuso UTC. O histórico continua retornando
`{"last": 15, "content": "..."}` como texto para preservar o contrato.

No PowerShell, use `curl.exe` para evitar o alias de versões antigas:

```powershell
curl.exe "http://localhost:8000/advice?save=false"
curl.exe "http://localhost:8000/historico?last=3"
```

Erros retornam `{"detail": "mensagem"}`:

| Status | Significado |
| --- | --- |
| 422 | Parâmetro inválido. |
| 502 | Falha de conexão, status não 200 ou resposta inválida do fornecedor. |
| 504 | Timeout da API externa. |
| 500 | Falha local ao acessar o histórico. |

A API mantém `GET /advice` com gravação por compatibilidade. Para uma futura versão
pública, considere uma rota POST para a operação que altera o histórico.

## Configuração

| Variável | Padrão | Uso |
| --- | --- | --- |
| `DEBUG` | `false` | Debug do FastAPI; mantenha false em produção. |
| `LOG_LEVEL` | `INFO` | Nível de log. |
| `ADVICE_API_URL` | `https://api.adviceslip.com/advice` | Endereço do fornecedor. |
| `ADVICE_API_TIMEOUT` | `5.0` | Timeout HTTP em segundos, maior que zero. |
| `DATABASE_PATH` | `./data/conselhos.db` | Arquivo SQLite. |
| `HISTORICO_PATH` | `./historico_conselhos.txt` | TXT usado apenas pela migração. |

Caminhos relativos partem do diretório onde o comando é executado.
O `.env`, o banco, caches e o ambiente virtual são ignorados pelo Git.

## Migrar um histórico antigo

A migração é opcional e nunca apaga o TXT. Faça uma cópia de segurança do banco
antes de importar. Pare o servidor e execute, antes de buscar novos conselhos:

```powershell
.\.venv\Scripts\python.exe -m app.migrate_history .\historico_conselhos.txt
```

O arquivo deve seguir o formato antigo: Original, Gritando, Sussurrando e separador
com 30 hífens. A importação valida o arquivo inteiro e usa uma transação.
Reexecutar sobre o mesmo conteúdo importa zero registros, mesmo se o arquivo foi copiado
para outro caminho. Duplicatas que já existiam dentro do TXT são preservadas.
Um arquivo alterado no mesmo caminho após a importação é recusado para evitar
reimportação parcial e duplicação; use o snapshot original, sem editar nem renomear
uma versão alterada para forçar nova importação.

O TXT não tinha datas: registros importados recebem `fetched_at = NULL`, sem inventar
horários. Novas consultas recebem UTC. O histórico é ordenado pelo ID de inserção;
por isso, importe o legado antes de gerar novos registros.

## Funções principais

| Arquivo / função | Responsabilidade |
| --- | --- |
| `app/main.py`: `create_application` | Monta a aplicação, rotas e tratamento de erros. |
| `app/main.py`: `lifespan` | Inicializa o banco e abre/fecha o cliente HTTP compartilhado. |
| `app/api/deps.py`: `get_http_client` | Entrega o cliente HTTP para a rota e permite substituí-lo nos testes. |
| `app/api/routes/advice.py`: `get_advice` | Coordena busca e gravação opcional. |
| `app/services/advice_service.py`: `fetch_advice` | Consulta o fornecedor, valida os dados e trata falhas. |
| `app/models/advice.py`: `from_raw_text` | Cria as versões original, maiúscula e minúscula com data UTC. |
| `app/services/history_service.py`: `database` | Abre uma conexão/transação e garante seu fechamento. |
| `app/services/history_service.py`: `initialize_database` | Cria as tabelas se não existirem. |
| `app/services/history_service.py`: `save_to_history` | Persiste um conselho com SQL parametrizado. |
| `app/services/history_service.py`: `read_history` | Consulta apenas a quantidade solicitada e formata a resposta. |
| `app/migrate_history.py`: `migrate_history` | Importa o TXT de forma explícita e controlada. |

As operações SQLite são síncronas e executadas em threads nas rotas, evitando bloquear
o event loop. Cada operação tem sua própria conexão; nenhuma conexão SQLite é compartilhada
entre threads. O cliente HTTP é reutilizado e fechado ao encerrar a aplicação.

Foram removidos imports sem uso, o modelo duplicado HistoryEntry, a dependência que apenas
repassava o parâmetro `last` e dependências de teste desnecessárias. Os arquivos `__init__.py`
foram mantidos por fazerem parte da organização dos pacotes.

## Testes e qualidade

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m ruff format --check app tests
.\.venv\Scripts\python.exe -m mypy app
```

Os testes usam respostas HTTP simuladas e banco temporário, sem internet nem dados reais.
Cobrem sucesso, persistência, timeout, conexão, payloads inválidos, limites, ordenação,
migração, importação concorrente e fechamento do cliente HTTP.
O workflow do GitHub Actions está configurado para executar essas verificações em
Python 3.11, 3.12 e 3.13 após o push. Consulte `VALIDACAO.md` para os resultados locais.

## Enviar as alterações ao GitHub

Se já tem o repositório clonado, abra essa pasta, confira `git status` e preserve
qualquer trabalho local antes de copiar os arquivos atualizados. Crie uma branch:

```bash
git switch -c melhorias/fastapi-sqlite
```

Se ainda não tem uma cópia local:

```bash
git clone https://github.com/lucasdossantosxl-cyber/Projeto_fastapi.git
cd Projeto_fastapi
git switch -c melhorias/fastapi-sqlite
```

Copie o CONTEÚDO da pasta `Projeto_fastapi` do ZIP para dentro do clone, substituindo
os arquivos correspondentes. Inclua `.github`, `.gitignore` e `.env.example`.
Não crie uma pasta `Projeto_fastapi` dentro de outra. Preserve sua pasta `.git`.
O ZIP não contém `.git`, `.env`, banco ou ambiente virtual.

Instale as dependências, execute os testes e revise:

```bash
git status
git diff --stat
git diff
```

Depois envie a branch:

```bash
git add app tests pyproject.toml uv.lock README.md VALIDACAO.md .env.example .gitignore .github
git commit -m "Melhora API com SQLite, validacao e testes"
git push -u origin melhorias/fastapi-sqlite
```

Entre no GitHub, abra o Pull Request da branch para `main` e confira o resultado do Actions.
O push pode pedir autenticação. Nenhuma alteração foi enviada automaticamente.
Enviar ao GitHub não hospeda a API: ela funciona enquanto o servidor estiver rodando.

## Limites do projeto

Esta versão é uma aplicação local de estudo. O histórico é global, sem contas ou autenticação.
Não foi adicionada infraestrutura de produção. Para hospedar, será necessário armazenamento
persistente para o SQLite e planejamento de acesso e concorrência. Não use `--reload` em produção.
