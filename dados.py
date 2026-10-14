"""Tratamento da planilha original de vendas do ano de 2020."""
from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.request import urlopen
import pandas as pd

PASTA_RAIZ = Path(__file__).resolve().parent
CAMINHO_PADRAO = PASTA_RAIZ / "data" / "1 - Base de Dados.xlsx"
URL_BASE = "https://raw.githubusercontent.com/mramgti/api_dashboard/main/1%20-%20Base%20de%20Dados.xlsx"
COLUNAS_OBRIGATORIAS = {
    "Data_Pedido", "Valor_Total_Venda", "Nome_Representante",
    "Nome_Produto", "Regional", "Estado_Cliente", "Cidade_Cliente"
}
COLUNAS_TEXTUAIS = (
    "Nome_Representante", "Nome_Produto", "Regional",
    "Estado_Cliente", "Cidade_Cliente", "Nome_Cliente"
)
MESES = dict(enumerate(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul",
                       "Ago", "Set", "Out", "Nov", "Dez"], 1))


def baixar_base(caminho: Path = CAMINHO_PADRAO) -> Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(URL_BASE, timeout=30) as resposta:
            conteudo = resposta.read()
    except Exception as exc:
        raise FileNotFoundError(
            "Não foi possível baixar a planilha original. Acesse "
            "https://github.com/mramgti/api_dashboard e copie "
            "'1 - Base de Dados.xlsx' para a pasta data/."
        ) from exc
    if not conteudo.startswith(b"PK"):
        raise ValueError("A resposta recebida não é uma planilha XLSX válida.")
    tmp = caminho.with_suffix(".download")
    tmp.write_bytes(conteudo)
    tmp.replace(caminho)
    return caminho


def numero_monetario(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = re.sub(r"[^0-9,.\\-]", "", str(valor).strip())
    if not texto or texto == "-":
        return None
    if "," in texto and "." in texto:
        texto = (texto.replace(".", "").replace(",", ".")
                 if texto.rfind(",") > texto.rfind(".") else texto.replace(",", ""))
    elif "," in texto:
        texto = texto.replace(",", ".")
    elif texto.count(".") > 1:
        texto = texto.replace(".", "")
    try:
        return float(texto)
    except ValueError:
        return None


def preparar_dados(brutos: pd.DataFrame) -> pd.DataFrame:
    df = brutos.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.match(r"^Unnamed(?::|$)", case=False)]
    faltantes = COLUNAS_OBRIGATORIAS - set(df.columns)
    if faltantes:
        raise ValueError("Colunas ausentes: " + ", ".join(sorted(faltantes)))
    if pd.api.types.is_numeric_dtype(df["Data_Pedido"]):
        df["Data_Pedido"] = pd.to_datetime(
            df["Data_Pedido"], unit="D", origin="1899-12-30", errors="coerce")
    else:
        df["Data_Pedido"] = pd.to_datetime(
            df["Data_Pedido"], format="mixed", dayfirst=True, errors="coerce")
    df["Valor_Total_Venda"] = df["Valor_Total_Venda"].map(numero_monetario)
    df = df.dropna(subset=["Data_Pedido", "Valor_Total_Venda"])
    df = df[df["Data_Pedido"].dt.year == 2020].copy()
    df["Mes_Num"] = df["Data_Pedido"].dt.month.astype(int)
    df["Mes"] = df["Mes_Num"].map(MESES)
    for col in COLUNAS_TEXTUAIS:
        if col in df.columns:
            df[col] = df[col].astype("string").fillna("Não informado").str.strip()
            df.loc[df[col].eq(""), col] = "Não informado"
    return df.reset_index(drop=True)


def carregar_dados() -> pd.DataFrame:
    caminho = Path(os.environ.get("DASHBOARD_DATA_PATH") or CAMINHO_PADRAO)
    if not caminho.exists() and caminho == CAMINHO_PADRAO:
        baixar_base(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {caminho}")
    brutos = pd.read_csv(caminho) if caminho.suffix.lower() == ".csv" else pd.read_excel(caminho)
    return preparar_dados(brutos)


def valores_unicos(df: pd.DataFrame, coluna: str) -> list[str]:
    if coluna not in df:
        return []
    return sorted(df[coluna].dropna().astype(str).unique().tolist(), key=str.casefold)


def cidades_do_estado(df: pd.DataFrame, estado: str | None) -> list[str]:
    if not estado:
        return []
    return valores_unicos(df.loc[df["Estado_Cliente"].eq(estado)], "Cidade_Cliente")


def filtrar_vendas(df, meses=None, representantes=None, regionais=None,
                   produtos=None, clientes=None, estado=None, cidades=None):
    filtrado = df
    for coluna, selecao in (
        ("Mes_Num", meses), ("Nome_Representante", representantes),
        ("Regional", regionais), ("Nome_Produto", produtos),
        ("Nome_Cliente", clientes)
    ):
        if selecao and coluna in filtrado:
            filtrado = filtrado.loc[filtrado[coluna].isin(selecao)]
    if estado:
        filtrado = filtrado.loc[filtrado["Estado_Cliente"].eq(estado)]
        if cidades:
            validas = set(cidades_do_estado(df, estado)).intersection(cidades)
            if validas:
                filtrado = filtrado.loc[filtrado["Cidade_Cliente"].isin(validas)]
    return filtrado


def agrupar_vendas(df, coluna, quantidade=None):
    grupos = df.groupby(coluna, dropna=False, as_index=False)["Valor_Total_Venda"].sum()
    grupos = grupos.sort_values("Valor_Total_Venda", ascending=False)
    return grupos.head(quantidade) if quantidade else grupos


def formatar_real(numero):
    return "R$ " + f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
