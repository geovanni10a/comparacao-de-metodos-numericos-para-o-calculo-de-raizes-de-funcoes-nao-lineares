import math
import unittest

from raizes_numericas.analise import RAIZES_REFERENCIA
from raizes_numericas.metodos import (
    FUNCOES,
    PARADA_DERIVADA_NULA,
    PARADA_DESCONTINUIDADE,
    PARADA_F_ZERO,
    PARADA_LIMITE,
    PARADA_NAO_CALCULAVEL,
    PARADA_SECANTE_HORIZONTAL,
    TOL,
    bissecao,
    comparar,
    executar_experimentos,
    newton_raphson,
    secante,
)


class TesteRaizes(unittest.TestCase):
    def test_tres_metodos_acham_raizes_conhecidas(self):
        self.assertEqual(RAIZES_REFERENCIA.keys(), FUNCOES.keys())
        for nome, esperado in RAIZES_REFERENCIA.items():
            for r in comparar(**FUNCOES[nome]):
                self.assertTrue(r.convergiu, f"{nome}: {r.metodo}")
                self.assertAlmostEqual(r.raiz, esperado, places=11, msg=f"{nome}: {r.metodo}")
                if r.parada != PARADA_F_ZERO:  # com f(x) = 0 exato, o último passo pode exceder tol
                    self.assertLessEqual(r.erro, TOL)

    def test_tolerancia_pedida(self):
        self.assertEqual(TOL, 1e-12)

    def test_experimentos_sao_reproduziveis(self):
        self.assertEqual(executar_experimentos(), executar_experimentos())

    def test_bissecao_rejeita_intervalo_invalido(self):
        f = lambda x: x**2 + 1
        with self.assertRaises(ValueError):
            bissecao(f, -1, 1)  # sem troca de sinal
        with self.assertRaises(ValueError):
            bissecao(lambda x: x, 1, -1)  # a > b
        with self.assertRaises(ValueError):
            bissecao(lambda x: x, -1, math.inf)
        with self.assertRaises(ValueError):
            bissecao(math.log, -1, 2)  # f não calculável no extremo

    def test_bissecao_raiz_no_extremo(self):
        r = bissecao(lambda x: x - 1, 1, 2)
        self.assertEqual((r.raiz, r.iteracoes, r.convergiu, r.parada), (1, 0, True, PARADA_F_ZERO))

    def test_bissecao_para_no_limite_de_iteracoes(self):
        r = bissecao(lambda x: x - 0.3, 0, 1, max_iter=3)
        self.assertEqual((r.iteracoes, r.convergiu, r.parada), (3, False, PARADA_LIMITE))

    def test_bissecao_detecta_polo(self):
        r = bissecao(math.tan, 1, 2)
        self.assertEqual((r.convergiu, r.parada), (False, PARADA_DESCONTINUIDADE))

    def test_bissecao_polo_exato_no_ponto_medio(self):
        r = bissecao(lambda x: 1 / x, -1, 1)
        self.assertEqual((r.convergiu, r.parada), (False, PARADA_NAO_CALCULAVEL))

    def test_newton_derivada_nula_nao_converge(self):
        r = newton_raphson(lambda x: x**2 - 2, lambda x: 2 * x, 0)
        self.assertEqual((r.convergiu, r.parada), (False, PARADA_DERIVADA_NULA))

    def test_newton_raiz_dupla_no_chute(self):
        r = newton_raphson(lambda x: x**2, lambda x: 2 * x, 0)
        self.assertTrue(r.convergiu)

    def test_newton_divergente_nao_levanta_excecao(self):
        r = newton_raphson(math.atan, lambda x: 1 / (1 + x**2), 2)
        self.assertFalse(r.convergiu)

    def test_newton_ciclo_atinge_limite(self):
        r = newton_raphson(lambda x: x**3 - 2 * x + 2, lambda x: 3 * x**2 - 2, 0)
        self.assertEqual((r.iteracoes, r.convergiu, r.parada), (100, False, PARADA_LIMITE))

    def test_secante_reta_horizontal_nao_converge(self):
        r = secante(lambda x: 1.0, 0, 1)
        self.assertEqual((r.convergiu, r.parada), (False, PARADA_SECANTE_HORIZONTAL))

    def test_sair_do_dominio_durante_iteracoes_nao_levanta_excecao(self):
        for r in (newton_raphson(math.log, lambda x: 1 / x, 3), secante(math.log, 3, 4)):
            self.assertEqual((r.convergiu, r.parada), (False, PARADA_NAO_CALCULAVEL), r.metodo)

    def test_valores_iniciais_invalidos(self):
        with self.assertRaises(ValueError):
            newton_raphson(math.log, lambda x: 1 / x, -1)  # fora do domínio
        with self.assertRaises(ValueError):
            newton_raphson(lambda x: x, lambda x: 1.0, math.nan)
        with self.assertRaises(ValueError):
            secante(lambda x: x - 1, 2, 2)  # x0 == x1
        with self.assertRaises(ValueError):
            secante(math.log, -2, -1)  # fora do domínio

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            secante(lambda x: x, 0, 1, tol=0)
        with self.assertRaises(ValueError):
            bissecao(lambda x: x, -1, 1, max_iter=0)


if __name__ == "__main__":
    unittest.main()
