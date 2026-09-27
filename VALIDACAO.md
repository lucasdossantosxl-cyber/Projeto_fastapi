# Validação da versão 0.3.0

Revisão sobre o commit original `f459158` do repositório Projeto_fastapi.
Executada em 26/09/2026 (horário de São Paulo), Linux, Python 3.12.14.

## Resultados executados

- Instalação editable em ambiente virtual novo, via `uv pip install -e ".[dev]"`: sucesso.
- `uv lock`: sucesso; lockfile com registros públicos do PyPI.
- `uv run --frozen --extra dev python -m pytest -q`: **34 testes passaram**.
- `python -m ruff check app tests`: passou.
- `python -m ruff format --check app tests`: 24 arquivos já formatados.
- `python -m mypy app`: sem problemas nos 18 arquivos da aplicação.
- Servidor Uvicorn real em localhost, com banco temporário: iniciou e encerrou normalmente.
- `GET /docs`: HTTP 200.
- `GET /historico`: HTTP 200.
- `GET /advice?save=false` com fornecedor real: HTTP 504 por timeout.

A busca real de um conselho não foi confirmada neste ambiente. Os testes de sucesso
usam HTTPX MockTransport e os testes de falha confirmam o tratamento dos erros.
A suíte automatizada não usa internet nem modifica banco ou TXT do usuário.
Para o smoke test real, foi instalado socksio apenas no ambiente de execução,
porque a rede deste ambiente utiliza proxy SOCKS; não é dependência obrigatória do projeto.

## Aviso observado

Starlette emite um aviso de depreciação sobre o uso de HTTPX em TestClient e indica
httpx2 como alternativa futura. Isso não impediu nenhum teste; o aviso não foi ocultado.

## Limites da validação

- Os comandos Windows estão documentados, mas não foram executados em Windows.
- Python 3.11 e 3.13 estão na matriz do GitHub Actions; a execução local foi em 3.12.
- O workflow foi criado, mas ainda não rodou no GitHub porque não houve push.
- Não houve deploy, commit automático, push ou alteração da branch main remota.
- A API continua sendo um projeto de estudo com histórico global e sem autenticação.
