# Dashboard de Vendas 2020

Painel gerencial interativo desenvolvido para a disciplina de **Visualização de Dados**, utilizando **Python, Dash, Plotly e Pandas**. O projeto permite analisar as vendas registradas em 2020 por período, representante, cliente, produto e localização geográfica.

**Aplicação publicada:** https://dashboard-vendas-2020.onrender.com

**Código-fonte:** https://github.com/Dhaniels1/dashboard-vendas-2020

## Guia de demonstração

Para apresentar o projeto a professores ou recrutadores, consulte o **[roteiro visual, o diagrama de funcionamento e as verificações sugeridas](docs/GUIA_DEMONSTRACAO.md)**.

## Funcionalidades

- **Indicadores:** faturamento total, quantidade de vendas, valor médio por registro e estados atendidos.
- **Filtros combinados:** mês, representante, regional, produto, cliente e estado.
- **Filtro Estado → Cidade:** o estado selecionado determina as cidades disponíveis no filtro seguinte.
- **Gráficos interativos:** evolução mensal, faturamento por regional, por representante, por estado e por cidade.
- **Ranking de produtos:** tabela com faturamento e participação percentual.
- **Exportação:** download dos dados filtrados.
- **Interface:** layout responsivo com painéis e estados vazios quando não há resultados.

## Tecnologias e organização

| Tecnologia / arquivo | Papel |
| --- | --- |
| Python | Linguagem principal |
| Dash | Interface web e callbacks |
| Plotly Express e Graph Objects | Visualizações interativas |
| Pandas | Limpeza, filtragem e agregações |
| `app.py` | Layout, callbacks e servidor web |
| `dados.py` | Preparação e filtros da planilha |
| `baixar_base.py` | Download dos dados |
| `testes_auditoria.py` | Testes com dados sintéticos |
| `testes_interface.py` | Verificação estática do guia e da sintaxe do painel |
| `docs/GUIA_DEMONSTRACAO.md` | Roteiro visual de apresentação e arquitetura |
| `assets/` | Estilos e recursos visuais |
| `render.yaml` | Configuração de hospedagem Render |

## Fonte e tratamento dos dados

A planilha utilizada na atividade é disponibilizada no repositório [mramgti/api_dashboard](https://github.com/mramgti/api_dashboard) e não está versionada aqui.

O arquivo `dados.py` trata os dados de origem: valida colunas, converte datas e valores monetários, remove registros inválidos e mantém somente vendas do ano **2020**. O filtro de cidades é dependente do estado selecionado.

O processo de preparação exige acesso à planilha original na primeira execução. Se o arquivo remoto estiver indisponível, copie `1 - Base de Dados.xlsx` para a pasta `data/` (sem versioná-lo no GitHub).

## Executar localmente

**Pré-requisitos:** Python 3.11 ou versão compatível com as dependências especificadas em `requirements.txt` e acesso à internet para obter a planilha.

```bash
git clone https://github.com/Dhaniels1/dashboard-vendas-2020.git
cd dashboard-vendas-2020
python -m venv .venv
```

Ative o ambiente virtual:

- Windows PowerShell: `\.venv\Scripts\Activate.ps1`
- Linux/macOS: `source .venv/bin/activate`

Instale as dependências, obtenha os dados e inicie o servidor:

```bash
python -m pip install -r requirements.txt
python baixar_base.py
python app.py
```

Acesse `http://127.0.0.1:8050`.

Você também pode definir `DASHBOARD_DATA_PATH` para indicar um arquivo Excel ou CSV compatível, sem alterar o código.

## Testes

A suíte utiliza uma pequena base de vendas **sintética**, sem depender da planilha externa:

```bash
python -m unittest -v testes_auditoria testes_interface
```

Os testes verificam também a estrutura do guia e a sintaxe do aplicativo, além da seleção de vendas do ano 2020, filtro Estado → Cidade, filtros combinados, agregações, formatação monetária, tratamento de dados inválidos e o comportamento de cidades obsoletas durante a atualização de filtros.

Um workflow em `.github/workflows/testes.yml` executa a suíte em pushes e pull requests. O código do site e os dados reais podem ser verificados separadamente acessando o serviço publicado.

## Deploy no Render

O serviço gratuito está publicado em:

**https://dashboard-vendas-2020.onrender.com**

O arquivo `render.yaml` define:

- ambiente Python;
- instalação de dependências e download inicial da base no build;
- inicialização por Gunicorn, usando `app:server`;
- porta dinâmica fornecida pelo Render.

O plano gratuito pode suspender o serviço após inatividade, causando demora no primeiro acesso. Se a fonte externa da planilha deixar de estar disponível, um novo build também pode falhar na etapa de obtenção de dados.

## Contexto acadêmico

Projeto desenvolvido em dupla para a disciplina de Visualização de Dados do IF Sudeste MG, com entrega prevista em **19/10/2026**.

Este repositório demonstra tratamento de dados, modelagem de indicadores, interação por filtros encadeados, visualização e publicação de uma aplicação Python na nuvem.
