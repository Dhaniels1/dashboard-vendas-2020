# Dashboard de Vendas 2020

Projeto acadêmico de Visualização de Dados desenvolvido com Python, Dash e Plotly Express, com filtros interativos, análises por mês, representante, produto, regional e estado, além de filtro encadeado Estado → Cidade.

## Executar localmente

```bash
python -m pip install -r requirements.txt
python baixar_base.py
python app.py
```

Acesse `http://127.0.0.1:8050`.

Os dados originais estão no repositório [api_dashboard](https://github.com/mramgti/api_dashboard) e são obtidos pelo script `baixar_base.py`. A planilha não foi incluída neste repositório.

## Publicação

O projeto inclui `render.yaml` e a entrada WSGI `app:server` para hospedagem. A URL pública será adicionada após o deploy.

## Disciplina

Visualização de Dados — IF Sudeste MG. Trabalho em dupla, entrega em 19/10/2026.
