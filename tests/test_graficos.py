import tempfile
import unittest

from raizes_numericas.graficos import gerar_figuras


class TesteGraficos(unittest.TestCase):
    def test_gera_as_tres_figuras(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminhos = gerar_figuras(pasta)
            self.assertEqual(len(caminhos), 3)
            for caminho in caminhos:
                self.assertEqual(caminho.read_bytes()[:4], b"\x89PNG", caminho.name)


if __name__ == "__main__":
    unittest.main()
