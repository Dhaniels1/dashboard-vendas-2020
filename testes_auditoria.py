"""Testes automatizados do tratamento de dados e filtros (dados sintéticos)."""
import unittest
import pandas as pd
from dados import (
    preparar_dados, filtrar_vendas, cidades_do_estado, agrupar_vendas,
    formatar_real, numero_monetario
)

class TestesAuditoria(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = preparar_dados(pd.DataFrame([
            dict(Data_Pedido="2020-01-10", Valor_Total_Venda=100, Nome_Representante="A",
                 Nome_Produto="Notebook", Regional="Sudeste", Estado_Cliente="MG",
                 Cidade_Cliente="Muriaé", Nome_Cliente="1"),
            dict(Data_Pedido="2020-03-12", Valor_Total_Venda=300, Nome_Representante="B",
                 Nome_Produto="Mouse", Regional="Sudeste", Estado_Cliente="MG",
                 Cidade_Cliente="Juiz de Fora", Nome_Cliente="2"),
            dict(Data_Pedido="2020-03-13", Valor_Total_Venda=250, Nome_Representante="A",
                 Nome_Produto="Mouse", Regional="Sul", Estado_Cliente="PR",
                 Cidade_Cliente="Curitiba", Nome_Cliente="3"),
            dict(Data_Pedido="2021-01-01", Valor_Total_Venda=900, Nome_Representante="C",
                 Nome_Produto="Mouse", Regional="Sul", Estado_Cliente="PR",
                 Cidade_Cliente="Curitiba", Nome_Cliente="4"),
        ]))

    def test_apenas_2020(self):
        self.assertEqual(len(self.df), 3)
        self.assertEqual(self.df.Valor_Total_Venda.sum(), 650)

    def test_meses_ordenados(self):
        self.assertEqual(self.df.Mes_Num.tolist(), [1, 3, 3])

    def test_cidades_por_estado(self):
        self.assertEqual(cidades_do_estado(self.df, "MG"), ["Juiz de Fora", "Muriaé"])
        self.assertEqual(cidades_do_estado(self.df, None), [])

    def test_filtro_cascata(self):
        self.assertEqual(filtrar_vendas(self.df, estado="MG", cidades=["Muriaé"]).Valor_Total_Venda.sum(), 100)

    def test_filtros_combinados(self):
        x = filtrar_vendas(self.df, meses=[3], representantes=["B"], regionais=["Sudeste"],
                          produtos=["Mouse"], clientes=["2"], estado="MG")
        self.assertEqual(x.Valor_Total_Venda.sum(), 300)

    def test_filtro_sem_resultados(self):
        self.assertTrue(filtrar_vendas(self.df, produtos=["Inexistente"]).empty)

    def test_agregacao_produtos(self):
        x = agrupar_vendas(self.df, "Nome_Produto")
        self.assertEqual(x.loc[x.Nome_Produto.eq("Mouse"), "Valor_Total_Venda"].iloc[0], 550)

    def test_moeda_formatada_e_convertida(self):
        self.assertEqual(formatar_real(1234567.89), "R$ 1.234.567,89")
        self.assertEqual(numero_monetario("R$ 1.234,56"), 1234.56)
        self.assertEqual(numero_monetario("R$ 1,234.56"), 1234.56)

    def test_colunas_obrigatorias_e_valor_invalido(self):
        with self.assertRaises(ValueError):
            preparar_dados(self.df.drop(columns=["Regional"]))
        self.assertIsNone(numero_monetario("sem valor"))

    def test_cidade_obsoleta_ignorada_ate_atualizacao_do_dropdown(self):
        self.assertEqual(len(filtrar_vendas(self.df, estado="MG", cidades=["Curitiba"])), 2)

if __name__ == "__main__":
    unittest.main()
