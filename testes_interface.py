"""Verifica os elementos de demonstração sem depender da planilha remota."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class TestesInterface(unittest.TestCase):
    def test_codigo_do_dashboard_tem_sintaxe_python_valida(self):
        codigo = (ROOT / "app.py").read_text(encoding="utf-8")
        ast.parse(codigo, filename="app.py")

    def test_guia_e_rotas_de_navegacao(self):
        codigo = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('id="guia-uso"', codigo)
        self.assertIn("Ver o roteiro da demonstração", codigo)
        self.assertIn('href="#filtros"', codigo)
        self.assertIn('docs/GUIA_DEMONSTRACAO.md', codigo)
        self.assertIn("Não são vendas em tempo real", codigo)

    def test_campos_têm_rotulos_associados(self):
        codigo = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('htmlFor=getattr(componente, "id", None)', codigo)

    def test_estilos_do_guia_sao_responsivos(self):
        css = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".guide-panel", css)
        self.assertIn(".guide-details", css)
        self.assertIn("@media(max-width:650px)", css)
        self.assertTrue((ROOT / "docs" / "GUIA_DEMONSTRACAO.md").is_file())


if __name__ == "__main__":
    unittest.main()
