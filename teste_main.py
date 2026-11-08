import contextlib
import io
import sys
import unittest
from unittest import mock

import main


class TesteMain(unittest.TestCase):
    def test_calculos_funcionam_sem_matplotlib(self):
        saida = io.StringIO()
        with mock.patch.dict(sys.modules, {"graficos": None}), contextlib.redirect_stdout(saida):
            main.main()
        texto = saida.getvalue()
        self.assertIn("Nenhum método é universalmente melhor", texto)
        self.assertIn("Matplotlib não encontrado", texto)


if __name__ == "__main__":
    unittest.main()
