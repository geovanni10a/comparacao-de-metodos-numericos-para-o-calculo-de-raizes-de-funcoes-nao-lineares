import unittest

from matplotlib.figure import Figure

from interface import (
    desenhar_convergencia,
    desenhar_funcao,
    desenhar_iteracoes,
    executar_metodos,
    ler_parametros,
    linha_da_tabela,
    texto_da_analise,
)

NOME = "x**3 - x - 2"
TEXTOS = {"a": "1", "b": "2", "x0": "1,5", "x1": "2", "tol": "1e-12", "max_iter": "100"}


class TesteInterface(unittest.TestCase):
    def test_le_numeros_com_virgula_decimal(self):
        self.assertEqual(ler_parametros(TEXTOS)["x0"], 1.5)

    def test_rejeita_entradas_invalidas(self):
        for campo, valor in (("a", "abc"), ("tol", ""), ("max_iter", "1.5"), ("max_iter", "0"), ("max_iter", "100001")):
            with self.assertRaises(ValueError, msg=f"{campo}={valor}"):
                ler_parametros({**TEXTOS, campo: valor})

    def test_intervalo_invalido_nao_impede_os_outros_metodos(self):
        saidas = executar_metodos(NOME, ler_parametros({**TEXTOS, "a": "3", "b": "4"}))
        self.assertIsNone(saidas[0][1])
        self.assertIn("sinais opostos", linha_da_tabela(NOME, *saidas[0])[-1])
        self.assertTrue(saidas[1][1].convergiu)
        self.assertTrue(saidas[2][1].convergiu)

    def test_graficos_aceitam_todos_os_casos(self):
        for mudancas in ({}, {"a": "3", "b": "4"}, {"a": "nan", "x0": "inf", "x1": "inf", "b": "inf"}, {"tol": "-1"}):
            numeros = ler_parametros({**TEXTOS, **mudancas})
            saidas = executar_metodos(NOME, numeros)
            for desenhar in (
                lambda fig: desenhar_funcao(fig, NOME, numeros, saidas),
                lambda fig: desenhar_convergencia(fig, NOME, numeros, saidas),
                lambda fig: desenhar_iteracoes(fig, NOME, saidas),
            ):
                fig = Figure()
                desenhar(fig)
                fig.canvas.draw()

    def test_relatorio_tem_analise_e_verificacao(self):
        texto = texto_da_analise()
        self.assertIn("Nenhum método é universalmente melhor", texto)
        self.assertIn("22 de 22 verificações aprovadas", texto)


if __name__ == "__main__":
    unittest.main()
