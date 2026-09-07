# TODO - Refatoração nível senior (FastAPI)

- [ ] Criar estrutura `app/` (core, api, services, models)
- [ ] Migrar endpoint `/advice` e `/historico` mantendo comportamento
- [ ] Trocar `requests` por `httpx` (async) e declarar timeouts/config
- [ ] Declarar dependências no `pyproject.toml`
- [ ] Implementar logging e tratamento robusto de erros
- [ ] Melhorar gerenciamento do arquivo de histórico
- [ ] Atualizar `README.md` com comandos de execução
- [ ] Rodar validações (ex: `python -m py_compile`/`uvicorn`) e testes manuais via curl

