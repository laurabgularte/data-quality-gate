# Data Quality Gate

Validador de qualidade de dados em Python para rodar antes de cargas em banco ou atualização de dashboards de BI.

## O que faz
- Verifica colunas obrigatórias e duplicidade de chaves.
- Valida campos não nulos, datas, faixas numéricas e valores permitidos.
- Gera `validos.csv`, `erros_validacao.csv` e `relatorio_qualidade.json`.
- Retorna exit code `0` quando tudo passa ou `1` quando há falhas.

## Como executar

```bash
python -m dq_gate.cli validate exemplos/dados_exemplo.csv --schema config/schema_exemplo.json --out saida/

```
 ## Rodar testes

 ```bash
 
pytest -v

```