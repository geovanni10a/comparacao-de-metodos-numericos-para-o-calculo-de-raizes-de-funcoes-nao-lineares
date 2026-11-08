"""Verificação automática dos resultados e exportação dos dados brutos.

As verificações confrontam cada resultado com um fato matemático que não depende
do método que o produziu. Rodar `python -m raizes_numericas.verificacao` repete todas elas.
"""

import csv
import math
from pathlib import Path

from .analise import LIMITE_ARREDONDAMENTO, RAIZES_REFERENCIA
from .metodos import FUNCOES, MAX_ITER, TOL, executar_experimentos

SEGUNDAS_DERIVADAS = {
    "x**3 - x - 2": lambda x: 6 * x,
    "cos(x) - x": lambda x: -math.cos(x),
    "exp(-x) - x": lambda x: math.exp(-x),
}
DELTA_CERTIFICADO = 1e-11  # meia-largura do intervalo que deve conter a raiz
DESVIO_MAXIMO_LEI_ERRO = 0.10  # concordância exigida entre erro medido e previsto
# Relativa à pasta de execução: um pacote instalado não deve gravar dentro de si mesmo.
PASTA_RESULTADOS = Path("resultados") / "dados"


def certifica_raiz(f, x, delta=DELTA_CERTIFICADO):
    """Pelo Teorema do Valor Intermediário, a troca de sinal prova que há raiz em (x - delta, x + delta)."""
    return f(x - delta) * f(x + delta) < 0


def constante_erro(nome):
    """Constante C = |f''(r) / (2 f'(r))| das leis de erro de Newton-Raphson e da Secante."""
    r = RAIZES_REFERENCIA[nome]
    return abs(SEGUNDAS_DERIVADAS[nome](r) / (2 * FUNCOES[nome]["df"](r)))


def desvio_lei_erro(resultado, referencia, constante, atraso):
    """Desvio relativo entre e_k medido e C * e_(k-1) * e_(k-atraso).

    atraso = 1 é a lei de Newton-Raphson; atraso = 2, a da Secante. Usa o último
    erro acima do arredondamento, onde a lei assintótica é mais precisa.
    """
    erros = [abs(x - referencia) for x in resultado.aproximacoes]
    k = max(i for i in range(atraso, len(erros)) if erros[i] > LIMITE_ARREDONDAMENTO)
    previsto = constante * erros[k - 1] * erros[k - atraso]
    return abs(erros[k] / previsto - 1)


def verificar():
    """Devolve uma lista de (descrição, aprovado, detalhe)."""
    experimentos = executar_experimentos()
    verificacoes = []
    for nome, (bissecao, newton, secante) in experimentos.items():
        p = FUNCOES[nome]
        referencia = RAIZES_REFERENCIA[nome]
        largura = p["b"] - p["a"]

        for r in (bissecao, newton, secante):
            verificacoes.append(
                (f"{nome} | {r.metodo}: há raiz a até {DELTA_CERTIFICADO:g}", certifica_raiz(p["f"], r.raiz), f"x = {r.raiz!r}")
            )

        previstas = math.ceil(math.log2(largura / TOL))
        verificacoes.append(
            (
                f"{nome} | Bisseção: iterações = teto(log2((b - a) / tol))",
                bissecao.iteracoes == previstas,
                f"{bissecao.iteracoes} medidas, {previstas} previstas",
            )
        )

        dentro_do_limite = all(abs(c - referencia) <= largura / 2**k for k, c in enumerate(bissecao.aproximacoes, 1))
        verificacoes.append((f"{nome} | Bisseção: |c_k - r| <= (b - a) / 2^k em todas as iterações", dentro_do_limite, ""))

        constante = constante_erro(nome)
        for r, atraso, lei in ((newton, 1, "C e_k^2"), (secante, 2, "C e_k e_(k-1)")):
            desvio = desvio_lei_erro(r, referencia, constante, atraso)
            verificacoes.append(
                (f"{nome} | {r.metodo}: erro segue {lei}", desvio <= DESVIO_MAXIMO_LEI_ERRO, f"desvio de {100 * desvio:.2f}%")
            )

    verificacoes.append(("Duas execuções produzem resultados idênticos", executar_experimentos() == experimentos, ""))
    return verificacoes


def imprimir_verificacao():
    """Imprime cada verificação e devolve True se todas foram aprovadas."""
    verificacoes = verificar()
    print("\n6. VERIFICAÇÃO DOS RESULTADOS\n")
    for descricao, aprovado, detalhe in verificacoes:
        print(f"[{'OK' if aprovado else 'FALHOU'}] {descricao}" + (f" ({detalhe})" if detalhe else ""))
    aprovadas = sum(aprovado for _, aprovado, _ in verificacoes)
    print(f"\n{aprovadas} de {len(verificacoes)} verificações aprovadas.")
    return aprovadas == len(verificacoes)


def exportar_resultados(pasta=PASTA_RESULTADOS):
    """Grava resultados.csv e historico.csv e devolve os caminhos.

    Os números usam repr, que preserva todos os dígitos do double. O separador ";"
    e a codificação utf-8-sig permitem abrir os arquivos no Excel em português.
    """
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    caminho_resultados, caminho_historico = pasta / "resultados.csv", pasta / "historico.csv"

    with open(caminho_resultados, "w", newline="", encoding="utf-8-sig") as arquivo_resultados, open(
        caminho_historico, "w", newline="", encoding="utf-8-sig"
    ) as arquivo_historico:
        resultados = csv.writer(arquivo_resultados, delimiter=";")
        historico = csv.writer(arquivo_historico, delimiter=";")
        resultados.writerow(
            ["funcao", "metodo", "raiz", "iteracoes", "erro_aproximado", "erro_real", "residuo", "convergiu", "parada",
             "a", "b", "x0", "x1", "tol", "max_iter"]
        )
        # k <= 0 identifica os valores iniciais de Newton-Raphson e da Secante.
        historico.writerow(["funcao", "metodo", "k", "x_k", "erro_real"])
        for nome, lista in executar_experimentos().items():
            p = FUNCOES[nome]
            referencia = RAIZES_REFERENCIA[nome]
            for r in lista:
                resultados.writerow(
                    [nome, r.metodo, repr(r.raiz), r.iteracoes, repr(r.erro), repr(abs(r.raiz - referencia)),
                     repr(abs(p["f"](r.raiz))), r.convergiu, r.parada, p["a"], p["b"], p["x0"], p["x1"], TOL, MAX_ITER]
                )
                primeira = r.iteracoes - len(r.aproximacoes) + 1
                for k, x in enumerate(r.aproximacoes, primeira):
                    historico.writerow([nome, r.metodo, k, repr(x), repr(abs(x - referencia))])
    return [caminho_resultados, caminho_historico]


if __name__ == "__main__":
    imprimir_verificacao()
