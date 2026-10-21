"""Dashboard interativo de vendas 2020 — V2 Clean Premium."""
from __future__ import annotations

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html, dash_table
from dash.exceptions import PreventUpdate
from dados import (
    MESES, carregar_dados, agrupar_vendas, filtrar_vendas,
    cidades_do_estado, formatar_real, valores_unicos,
)

DADOS = carregar_dados()
AZUL, VERDE, ROXO, AMARELO = "#2563fa", "#25b99c", "#8b72ef", "#f5b748"
PALETA = [AZUL, "#a6c3ff", "#cddcfb", VERDE, ROXO, AMARELO]
CONFIG = {"displayModeBar": False, "displaylogo": False, "responsive": True}
app = Dash(__name__, title="Performance de Vendas | 2020", update_title=None)
server = app.server


def menu(codigo, coluna, titulo, multi=True):
    return dcc.Dropdown(
        id=codigo,
        options=[{"label": x, "value": x} for x in valores_unicos(DADOS, coluna)],
        value=[] if multi else None, multi=multi, searchable=True,
        placeholder=titulo, className="filter-select"
    )


def campo(nome, componente, nota=None):
    return html.Div([
        html.Label(nome, htmlFor=getattr(componente, "id", None), className="filter-label"),
        componente,
        html.Span(nota, className="filter-hint") if nota else None,
    ], className="filter-field")


def indicador(codigo, rotulo, icone, classe, subtitulo):
    return html.Article([
        html.Div([
            html.Span(icone, className="kpi-icon"),
            html.Span(rotulo, className="kpi-label")
        ], className="kpi-heading"),
        html.Div(id=codigo, className="kpi-value"),
        html.Div(subtitulo, className="kpi-detail"),
    ], className="kpi-card " + classe)


def painel(codigo, titulo, descricao, classe=""):
    return html.Section([
        html.Div([
            html.Div([html.H3(titulo), html.P(descricao)]),
            html.Span("↗", className="panel-corner"),
        ], className="panel-heading"),
        dcc.Loading(dcc.Graph(id=codigo, config=CONFIG, className="plot-area"),
                    type="circle", color=AZUL),
    ], className="panel " + classe)


FILTROS = [
    campo("Mês", dcc.Dropdown(
        id="filtro-mes", options=[{"label": nome, "value": numero}
        for numero, nome in MESES.items()], multi=True, value=[],
        placeholder="Todos os meses", className="filter-select")),
    campo("Representante", menu("filtro-representante", "Nome_Representante", "Todos os representantes")),
    campo("Regional", menu("filtro-regional", "Regional", "Todas as regionais")),
    campo("Produto", menu("filtro-produto", "Nome_Produto", "Todos os produtos")),
    campo("Cliente", menu("filtro-cliente", "Nome_Cliente", "Todos os clientes")
          if "Nome_Cliente" in DADOS.columns else
          dcc.Dropdown(id="filtro-cliente", value=[], multi=True, disabled=True)),
]

app.layout = html.Div([
    dcc.Download(id="download-vendas"),
    html.Div([
        html.Header([
            html.Div([html.Div("◉", className="brand-logo"),
                      html.Div([html.Strong("DATA INSIGHTS"),
                                html.Small("INTELIGÊNCIA COMERCIAL")])], className="brand"),
            html.Nav([
                html.A("▦  Visão geral", href="#visao-geral", className="nav-link nav-link-active"),
                html.A("↗  Performance", href="#graficos", className="nav-link"),
                html.A("◫  Geografia", href="#geografia", className="nav-link"),
                html.A("▣  Produtos", href="#produtos", className="nav-link"),
            ], className="navigation"),
            html.Div("●  Dados de 2020", className="period-chip"),
        ], className="topbar"),

        html.Main([
            html.Div([
                html.Div([
                    html.P("RELATÓRIO ANUAL DE VENDAS", className="eyebrow"),
                    html.H1("Performance de Vendas"),
                    html.P("Explore o faturamento, compare representantes e descubra como as vendas se distribuem em 2020.",
                           className="hero-copy"),
                ]),
                html.Div([
                    html.Span("▦  Exercício de 2020", className="year-chip"),
                    html.Button("⇩  Exportar dados", id="exportar-dados",
                                n_clicks=0, className="export-button"),
                ], className="hero-actions"),
            ], className="hero", id="visao-geral"),

            html.Section([
                html.Div([
                    html.P("GUIA DE EXPLORAÇÃO", className="guide-kicker"),
                    html.H2("Entenda o painel em poucos passos"),
                    html.P("Acesse os indicadores, altere um filtro e observe como os gráficos "
                           "respondem à sua seleção. Esta é uma análise acadêmica de 2020, "
                           "não um acompanhamento de vendas em tempo real."),
                ], className="guide-copy"),
                html.Details([
                    html.Summary("Ver o roteiro da demonstração"),
                    html.Ol([
                        html.Li("Confira o faturamento e a média por registro na visão geral."),
                        html.Li("Escolha mês ou representante e compare os indicadores."),
                        html.Li("Selecione um estado: as cidades disponíveis serão atualizadas."),
                        html.Li("Explore o ranking de produtos e exporte os dados filtrados."),
                        html.Li("Use Limpar filtros para retornar à visão consolidada."),
                    ]),
                    html.P("Média por registro = faturamento ÷ quantidade de vendas. "
                           "Estados atendidos = quantidade de estados distintos na seleção.",
                           className="guide-note"),
                ], className="guide-details"),
                html.Div([
                    html.A("Explorar filtros ↓", href="#filtros", className="guide-action"),
                    html.A("Ler guia técnico ↗",
                           href="https://github.com/Dhaniels1/dashboard-vendas-2020/blob/main/docs/GUIA_DEMONSTRACAO.md",
                           target="_blank", rel="noopener noreferrer",
                           className="guide-secondary"),
                ], className="guide-links"),
            ], className="guide-panel", id="guia-uso"),

            html.Div([
                html.Span("Overview", className="tab-label"),
                html.Span("•  Visão consolidada das vendas de 2020", className="tab-description"),
            ], className="section-intro"),

            html.Div([
                indicador("kpi-vendas", "Faturamento total", "↗", "blue", "Soma das vendas selecionadas"),
                indicador("kpi-registros", "Vendas registradas", "▤", "mint", "Registros encontrados na base"),
                indicador("kpi-ticket", "Média por registro", "◈", "purple", "Faturamento ÷ registros"),
                indicador("kpi-estados", "Estados atendidos", "⌖", "amber", "Estados distintos no filtro"),
            ], className="kpi-grid"),

            html.Section([
                html.Div([
                    html.Div([html.H2("Filtros de análise"),
                              html.P("Altere as opções para atualizar todos os gráficos.")]),
                    html.Button("↺  Limpar filtros", id="limpar-filtros",
                                n_clicks=0, className="clear-button"),
                ], className="filter-toolbar"),
                html.Div(FILTROS, className="filter-grid"),
                html.Div(className="filter-separator"),
                html.Div([
                    campo("Estado do cliente", menu(
                        "filtro-estado", "Estado_Cliente", "Todos os estados", multi=False),
                        "Selecione um estado para habilitar as cidades."),
                    campo("Cidade do cliente", dcc.Dropdown(
                        id="filtro-cidade", options=[], value=[], multi=True,
                        disabled=True, placeholder="Selecione um estado",
                        className="filter-select")),
                ], className="geographic-filters"),
            ], className="filters-panel", id="filtros"),

            html.Div(id="resumo-filtros", className="results-caption"),
            html.Section([
                painel("grafico-mensal", "Evolução das vendas",
                       "Faturamento mensal de janeiro a dezembro", "panel-trend"),
                painel("grafico-regional", "Participação por regional",
                       "Distribuição do faturamento", "panel-donut"),
                painel("grafico-representante", "Vendas por representante",
                       "Comparativo de desempenho comercial", "panel-reps"),
                painel("grafico-estado", "Vendas por estado",
                       "Receita por localização do cliente", "panel-states"),
            ], className="chart-grid", id="graficos"),

            html.Section([
                html.Div([html.Div([html.H2("Análise geográfica"),
                                    html.P("Selecione um estado e depois uma cidade.")]),
                          html.A("↑ Ajustar filtros", href="#filtros",
                                 className="section-action")], className="section-heading"),
                painel("grafico-cidade", "Detalhamento por cidade",
                       "Estado → Cidade · Filtros encadeados", "panel-city"),
            ], className="geo-section", id="geografia"),

            html.Section([
                html.Div([html.Div([html.H2("Ranking de produtos"),
                                    html.P("Faturamento e participação percentual no filtro atual.")]),
                          html.Span("2020", className="table-chip")], className="section-heading"),
                dash_table.DataTable(
                    id="tabela-produtos",
                    columns=[{"name": "Produto", "id": "Produto"},
                             {"name": "Faturamento", "id": "Faturamento"},
                             {"name": "Participação", "id": "Participação"}],
                    data=[], page_action="native", page_size=10,
                    style_as_list_view=True, style_table={"overflowX": "auto"},
                    style_cell={"backgroundColor": "white", "color": "#263348",
                                "fontFamily": "DM Sans, Segoe UI, Arial", "fontSize": "13px",
                                "border": "none", "padding": "16px", "textAlign": "left"},
                    style_header={"backgroundColor": "#f4f7fc", "fontWeight": "700",
                                  "color": "#72809a", "borderBottom": "1px solid #e9eef6"},
                    style_data_conditional=[{"if": {"row_index": "odd"},
                                             "backgroundColor": "#fafcff"}],
                ),
            ], className="products-panel panel", id="produtos"),
            html.Footer([
                "Projeto acadêmico · Dados de 2020 · Não são vendas em tempo real · ",
                html.A("Fonte dos dados", href="https://github.com/mramgti/api_dashboard",
                       target="_blank", rel="noopener noreferrer"),
            ], className="footer"),
        ], className="container"),
    ], className="workspace"),
], className="app-shell")


def estilo(fig, altura=350, monetario=None):
    fig.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=altura,
        margin=dict(l=18, r=21, t=18, b=27),
        font=dict(family="DM Sans, Segoe UI, Arial", color="#586579", size=12),
        showlegend=False, separators=",.",
        hoverlabel=dict(bgcolor="#1b2537", font_color="#fff"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#e9eef7")
    fig.update_yaxes(gridcolor="#eef2f8", zeroline=False)
    if monetario == "x":
        fig.update_xaxes(tickprefix="R$ ", tickformat="~s")
    if monetario == "y":
        fig.update_yaxes(tickprefix="R$ ", tickformat="~s")
    return fig


def vazio(mensagem):
    fig = go.Figure()
    fig.add_annotation(x=0.5, y=0.5, xref="paper", yref="paper",
                       text=mensagem, showarrow=False,
                       font=dict(size=14, color="#94a3b8"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return estilo(fig)


def figura_mensal(df):
    if df.empty:
        return vazio("Não há vendas para os filtros selecionados")
    serie = df.groupby("Mes_Num")["Valor_Total_Venda"].sum().reindex(range(1, 13), fill_value=0)
    dados = pd.DataFrame({"Mês": list(MESES.values()), "Vendas": serie.values})
    fig = px.line(dados, x="Mês", y="Vendas", markers=True,
                  color_discrete_sequence=[AZUL],
                  category_orders={"Mês": list(MESES.values())})
    fig.update_traces(line=dict(width=3.5), marker=dict(size=7),
                      fill="tozeroy", fillcolor="rgba(37,99,250,.08)",
                      hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>")
    fig.update_xaxes(title=None)
    return estilo(fig, 375, "y")


def figura_representantes(df):
    if df.empty:
        return vazio("Nenhum representante corresponde ao filtro")
    base = agrupar_vendas(df, "Nome_Representante").sort_values("Valor_Total_Venda")
    fig = px.bar(base, x="Valor_Total_Venda", y="Nome_Representante",
                 orientation="h", color_discrete_sequence=[VERDE])
    fig.update_traces(marker=dict(cornerradius=5),
                      hovertemplate="<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>")
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return estilo(fig, min(700, max(350, len(base) * 29 + 80)), "x")


def figura_regionais(df):
    if df.empty:
        return vazio("Nenhuma regional corresponde ao filtro")
    base = agrupar_vendas(df, "Regional")
    fig = px.pie(base, names="Regional", values="Valor_Total_Venda",
                 hole=0.62, color_discrete_sequence=PALETA)
    fig.update_traces(textposition="outside", textinfo="percent+label",
                      textfont_size=11, marker=dict(line=dict(color="white", width=4)),
                      hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>")
    return estilo(fig, 370)


def figura_estados(df):
    if df.empty:
        return vazio("Nenhum estado corresponde ao filtro")
    base = agrupar_vendas(df, "Estado_Cliente")
    fig = px.bar(base, x="Estado_Cliente", y="Valor_Total_Venda",
                 color_discrete_sequence=[ROXO])
    fig.update_traces(marker=dict(cornerradius=5),
                      hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>")
    fig.update_xaxes(title=None, categoryorder="total descending")
    fig.update_yaxes(title=None)
    return estilo(fig, 350, "y")


def figura_cidades(df, estado):
    if not estado:
        return vazio("Selecione um Estado para visualizar as cidades")
    if df.empty:
        return vazio("Nenhuma cidade corresponde aos filtros selecionados")
    base = agrupar_vendas(df, "Cidade_Cliente", 12).sort_values("Valor_Total_Venda")
    fig = px.bar(base, x="Valor_Total_Venda", y="Cidade_Cliente",
                 orientation="h", color_discrete_sequence=[AMARELO])
    fig.update_traces(marker=dict(cornerradius=5),
                      hovertemplate="<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>")
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return estilo(fig, 350, "x")


def linhas_produtos(df):
    if df.empty:
        return []
    total = float(df["Valor_Total_Venda"].sum())
    base = agrupar_vendas(df, "Nome_Produto")
    return [{
        "Produto": str(row.Nome_Produto),
        "Faturamento": formatar_real(float(row.Valor_Total_Venda)),
        "Participação": f"{100 * float(row.Valor_Total_Venda) / total:.1f}%".replace(".", ",")
            if total else "0,0%",
    } for row in base.itertuples(index=False)]


@app.callback(
    Output("filtro-cidade", "options"),
    Output("filtro-cidade", "value"),
    Output("filtro-cidade", "disabled"),
    Output("filtro-cidade", "placeholder"),
    Input("filtro-estado", "value"),
    State("filtro-cidade", "value"),
)
def atualizar_cidades(estado, selecionadas):
    if not estado:
        return [], [], True, "Selecione primeiro um estado"
    cidades = cidades_do_estado(DADOS, estado)
    return ([{"label": nome, "value": nome} for nome in cidades],
            [c for c in (selecionadas or []) if c in cidades],
            False, "Todas as cidades do estado")


@app.callback(
    Output("filtro-mes", "value"),
    Output("filtro-representante", "value"),
    Output("filtro-regional", "value"),
    Output("filtro-produto", "value"),
    Output("filtro-cliente", "value"),
    Output("filtro-estado", "value"),
    Input("limpar-filtros", "n_clicks"),
    prevent_initial_call=True,
)
def limpar_filtros(_):
    return [], [], [], [], [], None


@app.callback(
    Output("kpi-vendas", "children"),
    Output("kpi-registros", "children"),
    Output("kpi-ticket", "children"),
    Output("kpi-estados", "children"),
    Output("resumo-filtros", "children"),
    Output("grafico-mensal", "figure"),
    Output("grafico-representante", "figure"),
    Output("grafico-regional", "figure"),
    Output("grafico-estado", "figure"),
    Output("grafico-cidade", "figure"),
    Output("tabela-produtos", "data"),
    Input("filtro-mes", "value"),
    Input("filtro-representante", "value"),
    Input("filtro-regional", "value"),
    Input("filtro-produto", "value"),
    Input("filtro-cliente", "value"),
    Input("filtro-estado", "value"),
    Input("filtro-cidade", "value"),
)
def atualizar_dashboard(meses, representantes, regionais, produtos, clientes, estado, cidades):
    df = filtrar_vendas(DADOS, meses, representantes, regionais,
                        produtos, clientes, estado, cidades)
    total, qtd = float(df["Valor_Total_Venda"].sum()), len(df)
    return (
        formatar_real(total), f"{qtd:,}".replace(",", "."),
        formatar_real(total / qtd if qtd else 0),
        str(df["Estado_Cliente"].nunique()),
        f"Exibindo {qtd:,} registros de vendas de 2020".replace(",", "."),
        figura_mensal(df), figura_representantes(df), figura_regionais(df),
        figura_estados(df), figura_cidades(df, estado), linhas_produtos(df)
    )


@app.callback(
    Output("download-vendas", "data"),
    Input("exportar-dados", "n_clicks"),
    State("filtro-mes", "value"),
    State("filtro-representante", "value"),
    State("filtro-regional", "value"),
    State("filtro-produto", "value"),
    State("filtro-cliente", "value"),
    State("filtro-estado", "value"),
    State("filtro-cidade", "value"),
    prevent_initial_call=True,
)
def exportar_dados(n, meses, representantes, regionais, produtos, clientes, estado, cidades):
    if not n:
        raise PreventUpdate
    df = filtrar_vendas(DADOS, meses, representantes, regionais,
                        produtos, clientes, estado, cidades)
    return dcc.send_data_frame(df.to_csv, "vendas_2020_filtradas.csv",
                               sep=";", index=False, encoding="utf-8-sig", decimal=",")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8050")),
            debug=os.environ.get("DASH_DEBUG") == "1")
