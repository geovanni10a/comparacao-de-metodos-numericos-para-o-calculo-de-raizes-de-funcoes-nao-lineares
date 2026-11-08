import contextlib
import io
import sys
import unittest
from unittest import mock

from raizes_numericas import __main__ as principal


class TesteMain(unittest.TestCase):
    def test_calculos_funcionam_sem_matplotlib(self):
        saida = io.StringIO()
        with mock.patch.dict(sys.modules, {"raizes_numericas.graficos": None}), contextlib.redirect_stdout(saida):
            principal.main()
        texto = saida.getvalue()
        self.assertIn("Nenhum método é universalmente melhor", texto)
        self.assertIn("Matplotlib não encontrado", texto)


if __name__ == "__main__":
    unittest.main()
