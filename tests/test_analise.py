import unittest

from raizes_numericas.analise import (
    RAIZES_REFERENCIA,
    estabilidade,
    iteracoes_ate_erro,
    ordem_estimada,
)
from raizes_numericas.metodos import FUNCOES, Resultado


def resultado_com(aproximacoes, iteracoes):
    return Resultado("teste", aproximacoes[-1], iteracoes, 0.0, True, aproximacoes, "teste")


class TesteAnalise(unittest.TestCase):
    def test_referencias_cercam_a_raiz_real(self):
        delta = 1e-14
        for nome, raiz in RAIZES_REFERENCIA.items():
            f = FUNCOES[nome]["f"]
            self.assertLess(f(raiz - delta) * f(raiz + delta), 0, nome)

    def test_ordem_quadratica_sintetica(self):
        r = resultado_com([1e-1, 1e-2, 1e-4, 1e-8], 3)
        self.assertAlmostEqual(ordem_estimada(r, 0.0), 2.0, places=9)

    def test_ordem_linear_sintetica(self):
        r = resultado_com([1 / 2**k for k in range(1, 8)], 7)
        self.assertAlmostEqual(ordem_estimada(r, 0.0), 1.0, places=9)

    def test_ordem_sem_dados_suficientes(self):
        r = resultado_com([1e-1, 1e-2], 1)
        self.assertNotEqual(ordem_estimada(r, 0.0), ordem_estimada(r, 0.0))  # NaN

    def test_iteracoes_ate_erro_desconta_valores_iniciais(self):
        # x0, x1 (Secante) e depois as iterações 1, 2 e 3.
        r = resultado_com([1.0, 0.5, 1e-2, 1e-7, 1e-12], 3)
        self.assertEqual(iteracoes_ate_erro(r, 0.0), 2)

    def test_iteracoes_ate_erro_nunca_alcancado(self):
        self.assertIsNone(iteracoes_ate_erro(resultado_com([1.0, 0.5], 1), 0.0))

    def test_estabilidade_bissecao_sempre_chega_na_raiz(self):
        for nome, parametros in FUNCOES.items():
            resumo = estabilidade(parametros, RAIZES_REFERENCIA[nome], pontos=40)
            self.assertEqual(resumo["Bisseção"][0], 100.0, nome)
            for percentual, _, _ in resumo.values():
                self.assertTrue(0 <= percentual <= 100)


if __name__ == "__main__":
    unittest.main()
