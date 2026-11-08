import csv
import tempfile
import unittest

from analise import RAIZES_REFERENCIA
from raizes import Resultado, executar_experimentos
from verificacao import certifica_raiz, desvio_lei_erro, exportar_resultados, verificar


class TesteVerificacao(unittest.TestCase):
    def test_todas_as_verificacoes_aprovadas(self):
        for descricao, aprovado, detalhe in verificar():
            self.assertTrue(aprovado, f"{descricao} {detalhe}")

    def test_certificado_rejeita_ponto_longe_da_raiz(self):
        self.assertTrue(certifica_raiz(lambda x: x - 1, 1.0))
        self.assertFalse(certifica_raiz(lambda x: x - 1, 1.001))

    def test_lei_de_erro_detecta_sequencia_incompativel(self):
        def resultado(aproximacoes):
            return Resultado("teste", aproximacoes[-1], 2, 0.0, True, aproximacoes, "teste")

        self.assertAlmostEqual(desvio_lei_erro(resultado([1e-2, 1e-4, 1e-8]), 0.0, 1.0, 1), 0.0, places=9)
        self.assertGreater(desvio_lei_erro(resultado([1e-2, 1e-3, 1e-4]), 0.0, 1.0, 1), 0.10)

    def test_csv_preserva_os_valores(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho_resultados, caminho_historico = exportar_resultados(pasta)
            with open(caminho_resultados, newline="", encoding="utf-8-sig") as arquivo:
                linhas = list(csv.DictReader(arquivo, delimiter=";"))
            with open(caminho_historico, newline="", encoding="utf-8-sig") as arquivo:
                historico = list(csv.DictReader(arquivo, delimiter=";"))

        experimentos = executar_experimentos()
        esperados = [r for lista in experimentos.values() for r in lista]
        self.assertEqual(len(linhas), 9)
        for linha, r in zip(linhas, esperados):
            self.assertEqual((float(linha["raiz"]), int(linha["iteracoes"])), (r.raiz, r.iteracoes))

        self.assertEqual(len(historico), sum(len(r.aproximacoes) for r in esperados))
        ultima_newton = [h for h in historico if h["funcao"] == "x**3 - x - 2" and h["metodo"] == "Newton-Raphson"]
        self.assertEqual((ultima_newton[0]["k"], ultima_newton[-1]["k"]), ("0", "4"))
        self.assertEqual(abs(float(ultima_newton[0]["x_k"]) - RAIZES_REFERENCIA["x**3 - x - 2"]), float(ultima_newton[0]["erro_real"]))


if __name__ == "__main__":
    unittest.main()
