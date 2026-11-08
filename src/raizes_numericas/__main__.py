"""Comparação de Métodos Numéricos para o Cálculo de Raízes de Funções Não Lineares:
Uma Implementação em Python.

Ponto de entrada: repete os experimentos, a análise comparativa, a verificação,
a exportação dos dados e os gráficos.

Requisitos: Python 3.11 ou superior, por exigência do Matplotlib fixado em
pyproject.toml. Os cálculos usam só a biblioteca padrão; o Matplotlib é
necessário apenas para gerar as figuras.

Uso:
    python -m pip install -e .
    python -m raizes_numericas
"""

import sys

from .analise import imprimir_analise
from .metodos import imprimir_experimentos
from .verificacao import exportar_resultados, imprimir_verificacao


def gerar_figuras_se_possivel():
    # Importado aqui para os cálculos continuarem funcionando sem o Matplotlib.
    try:
        from .graficos import gerar_figuras
    except ImportError:
        print("\nMatplotlib não encontrado: figuras não geradas.")
        print("Para instalar: python -m pip install -e .")
        return

    print("\nFiguras geradas:")
    for caminho in gerar_figuras():
        print(caminho)


def main():
    imprimir_experimentos()
    print()
    imprimir_analise()
    aprovado = imprimir_verificacao()

    print("\nDados exportados:")
    for caminho in exportar_resultados():
        print(caminho)
    gerar_figuras_se_possivel()

    if not aprovado:
        sys.exit("Há verificações reprovadas: os resultados não devem ser usados.")


if __name__ == "__main__":
    main()
