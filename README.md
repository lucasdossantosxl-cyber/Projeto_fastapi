# 🧠 Gerenciador de Conselhos API

API FastAPI que busca conselhos aleatórios de uma API externa, os transforma (gritando / sussurrando) e mantém um histórico persistente.

## 📁 Estrutura

```
.
├── app/
│   ├── core/           # Config, logging, exceptions
│   ├── models/         # Pydantic schemas
│   ├── services/       # Business logic (async)
│   ├── api/            # Routers & dependencies
│   │   └── routes/
│   └── main.py         # Entry point & factory
├── tests/              # Testes com pytest
├── pyproject.toml      # Dependências e metadados
└── .env.example        # Variáveis de ambiente
```

## 🚀 Execução

### 1. Instalar dependências

```bash
# Com uv (recomendado)
uv sync

# Ou com pip
pip install -e ".[dev]"
```

### 2. Rodar o servidor

```bash
# Modo desenvolvimento (reload automático)
uvicorn app.main:app --reload --port 8000

# Modo produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Testar manualmente (curl)

```bash
# Buscar um conselho e salvar no histórico
curl -s http://localhost:8000/advice | jq

# Buscar sem salvar
curl -s "http://localhost:8000/advice?save=false" | jq

# Ver histórico (últimas 15 entradas por padrão)
curl -s http://localhost:8000/historico | jq

# Ver histórico com limite customizado
curl -s "http://localhost:8000/historico?last=3" | jq
```

### 4. Documentação interativa

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testes

```bash
pytest -q
```

## 🔧 Variáveis de Ambiente

| Variável            | Padrão                                    | Descrição                     |
|---------------------|-------------------------------------------|-------------------------------|
| `DEBUG`             | `false`                                   | Modo debug do FastAPI         |
| `LOG_LEVEL`         | `INFO`                                    | Nível de log                  |
| `ADVICE_API_URL`    | `https://api.adviceslip.com/advice`       | URL da API externa            |
| `ADVICE_API_TIMEOUT`| `5.0`                                     | Timeout da requisição (seg)   |
| `HISTORICO_PATH`    | `./historico_conselhos.txt`               | Caminho do arquivo de histórico|

Copie `.env.example` para `.env` e ajuste conforme necessário.

## ✅ Checklist de Qualidade

```bash
# Lint + format
ruff check app tests
ruff format app tests

# Type check
mypy app

# Compilação
python -m py_compile app/main.py
```
