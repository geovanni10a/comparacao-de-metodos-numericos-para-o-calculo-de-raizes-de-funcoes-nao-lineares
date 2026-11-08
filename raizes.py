"""Comparação de Métodos Numéricos para o Cálculo de Raízes de Funções Não Lineares:
Uma Implementação em Python.

Implementa os métodos da Bisseção, de Newton-Raphson e da Secante.

Critérios de parada, comuns aos três para a comparação ser justa:
- |x_k - x_(k-1)| <= tol (na Bisseção, a meia-largura do intervalo), ou f(x_k) == 0: convergiu;
- limite de iterações ou falha numérica: não convergiu, com o motivo em Resultado.parada.

Reprodução: o programa é determinístico. Rodar `python raizes.py` repete todos os
experimentos com os parâmetros fixos em TOL, MAX_ITER e FUNCOES.

Este módulo usa só a biblioteca padrão do Python.
"""

import math
import platform
from dataclasses import dataclass
from typing import Callable

Funcao = Callable[[float], float]

TOL = 1e-12  # tolerância do critério de parada
MAX_ITER = 100  # impede laço sem fim em casos divergentes ou cíclicos

# Para cada função: derivada, intervalo [a, b] (Bisseção) e chutes x0 (Newton) e x0, x1 (Secante).
FUNCOES = {
    "x**3 - x - 2": dict(f=lambda x: x**3 - x - 2, df=lambda x: 3 * x**2 - 1, a=1, b=2, x0=1.5, x1=2),
    "cos(x) - x": dict(f=lambda x: math.cos(x) - x, df=lambda x: -math.sin(x) - 1, a=0, b=1, x0=0.5, x1=1),
    "exp(-x) - x": dict(f=lambda x: math.exp(-x) - x, df=lambda x: -math.exp(-x) - 1, a=0, b=1, x0=0.5, x1=1),
}

# Motivos de parada registrados em Resultado.parada.
PARADA_ERRO = "erro <= tol"
PARADA_F_ZERO = "f(x) = 0"
PARADA_LIMITE = "limite de iterações"
PARADA_DERIVADA_NULA = "derivada nula"
PARADA_SECANTE_HORIZONTAL = "secante horizontal"
PARADA_NAO_CALCULAVEL = "f não calculável"
PARADA_DESCONTINUIDADE = "possível descontinuidade"


@dataclass
class Resultado:
    """Saída comum aos três métodos."""

    metodo: str
    raiz: float  # melhor aproximação obtida, mesmo quando não há convergência
    iteracoes: int
    erro: float  # erro aproximado: última estimativa de |x_k - raiz|
    convergiu: bool
    aproximacoes: list[float]  # em Newton e Secante, inclui os valores iniciais
    parada: str  # uma das constantes PARADA_*


def _avaliar(f, x):
    """Devolve f(x), ou NaN quando f não é calculável em x (polo, domínio, overflow)."""
    try:
        y = float(f(x))
    except (ArithmeticError, ValueError):
        return math.nan
    return y if math.isfinite(y) else math.nan


def _validar(tol, max_iter, *pontos):
    """Levanta ValueError se os parâmetros numéricos forem inválidos."""
    if tol <= 0 or max_iter < 1:
        raise ValueError("É preciso tol > 0 e max_iter >= 1.")
    if not all(math.isfinite(p) for p in pontos):
        raise ValueError("Intervalos e valores iniciais precisam ser números finitos.")


def bissecao(f: Funcao, a: float, b: float, tol: float = TOL, max_iter: int = MAX_ITER) -> Resultado:
    """Método da Bisseção: divide ao meio o intervalo em que f troca de sinal.

    Exige a < b, f calculável nos extremos e troca de sinal; senão, levanta ValueError.
    """
    _validar(tol, max_iter, a, b)
    nome = "Bisseção"
    if a >= b:
        raise ValueError("É preciso a < b.")
    fa, fb = _avaliar(f, a), _avaliar(f, b)
    if math.isnan(fa) or math.isnan(fb):
        raise ValueError("f não pode ser calculada nos extremos do intervalo.")
    if fa == 0:
        return Resultado(nome, a, 0, 0.0, True, [a], PARADA_F_ZERO)
    if fb == 0:
        return Resultado(nome, b, 0, 0.0, True, [b], PARADA_F_ZERO)
    if (fa > 0) == (fb > 0):
        raise ValueError("f(a) e f(b) precisam ter sinais opostos.")

    # Perto de uma raiz |f| diminui; se terminar maior que nos extremos, o alvo era um polo.
    limite_f = max(abs(fa), abs(fb))
    aproximacoes = []
    for k in range(1, max_iter + 1):
        c = a + (b - a) / 2  # evita o overflow de (a + b) / 2
        erro = (b - a) / 2
        fc = _avaliar(f, c)
        aproximacoes.append(c)
        if math.isnan(fc):
            return Resultado(nome, c, k, erro, False, aproximacoes, PARADA_NAO_CALCULAVEL)
        if fc == 0:
            return Resultado(nome, c, k, erro, True, aproximacoes, PARADA_F_ZERO)
        if erro <= tol:
            if abs(fc) > limite_f:
                return Resultado(nome, c, k, erro, False, aproximacoes, PARADA_DESCONTINUIDADE)
            return Resultado(nome, c, k, erro, True, aproximacoes, PARADA_ERRO)
        # Mantém a metade em que f ainda troca de sinal.
        if (fa > 0) == (fc > 0):
            a, fa = c, fc
        else:
            b = c
    return Resultado(nome, c, max_iter, erro, False, aproximacoes, PARADA_LIMITE)


def newton_raphson(f: Funcao, df: Funcao, x0: float, tol: float = TOL, max_iter: int = MAX_ITER) -> Resultado:
    """Método de Newton-Raphson: x_(k+1) = x_k - f(x_k) / f'(x_k).

    Levanta ValueError se x0 for inválido. Falhas durante as iterações voltam em Resultado.parada.
    """
    _validar(tol, max_iter, x0)
    nome = "Newton-Raphson"
    x, fx, dfx = x0, _avaliar(f, x0), _avaliar(df, x0)
    if math.isnan(fx) or math.isnan(dfx):
        raise ValueError("f e f' precisam ser calculáveis em x0.")
    if fx == 0:
        return Resultado(nome, x, 0, 0.0, True, [x], PARADA_F_ZERO)

    erro, aproximacoes = math.inf, [x0]
    for k in range(1, max_iter + 1):
        if math.isnan(dfx):
            return Resultado(nome, x, k - 1, erro, False, aproximacoes, PARADA_NAO_CALCULAVEL)
        if dfx == 0:  # evita a divisão por zero do passo de Newton
            return Resultado(nome, x, k - 1, erro, False, aproximacoes, PARADA_DERIVADA_NULA)
        novo = x - fx / dfx
        erro = abs(novo - x)
        x = novo
        aproximacoes.append(x)
        fx, dfx = _avaliar(f, x), _avaliar(df, x)
        if math.isnan(fx):
            return Resultado(nome, x, k, erro, False, aproximacoes, PARADA_NAO_CALCULAVEL)
        if fx == 0:
            return Resultado(nome, x, k, erro, True, aproximacoes, PARADA_F_ZERO)
        if erro <= tol:
            return Resultado(nome, x, k, erro, True, aproximacoes, PARADA_ERRO)
    return Resultado(nome, x, max_iter, erro, False, aproximacoes, PARADA_LIMITE)


def secante(f: Funcao, x0: float, x1: float, tol: float = TOL, max_iter: int = MAX_ITER) -> Resultado:
    """Método da Secante: x_(k+1) = x_k - f(x_k) (x_k - x_(k-1)) / (f(x_k) - f(x_(k-1))).

    Levanta ValueError se x0 ou x1 forem inválidos. Falhas durante as iterações voltam em Resultado.parada.
    """
    _validar(tol, max_iter, x0, x1)
    nome = "Secante"
    if x0 == x1:
        raise ValueError("x0 e x1 precisam ser diferentes.")
    f0, f1 = _avaliar(f, x0), _avaliar(f, x1)
    if math.isnan(f0) or math.isnan(f1):
        raise ValueError("f precisa ser calculável em x0 e x1.")
    if f0 == 0:
        return Resultado(nome, x0, 0, 0.0, True, [x0], PARADA_F_ZERO)
    if f1 == 0:
        return Resultado(nome, x1, 0, 0.0, True, [x0, x1], PARADA_F_ZERO)

    erro, aproximacoes = abs(x1 - x0), [x0, x1]
    for k in range(1, max_iter + 1):
        if f1 == f0:  # evita a divisão por zero do passo da Secante
            return Resultado(nome, x1, k - 1, erro, False, aproximacoes, PARADA_SECANTE_HORIZONTAL)
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        erro = abs(x2 - x1)
        x0, f0, x1 = x1, f1, x2
        f1 = _avaliar(f, x1)
        aproximacoes.append(x1)
        if math.isnan(f1):
            return Resultado(nome, x1, k, erro, False, aproximacoes, PARADA_NAO_CALCULAVEL)
        if f1 == 0:
            return Resultado(nome, x1, k, erro, True, aproximacoes, PARADA_F_ZERO)
        if erro <= tol:
            return Resultado(nome, x1, k, erro, True, aproximacoes, PARADA_ERRO)
    return Resultado(nome, x1, max_iter, erro, False, aproximacoes, PARADA_LIMITE)


def comparar(f, df, a, b, x0, x1, tol=TOL, max_iter=MAX_ITER):
    """Roda os três métodos na mesma função, com a mesma tolerância."""
    return [
        bissecao(f, a, b, tol, max_iter),
        newton_raphson(f, df, x0, tol, max_iter),
        secante(f, x0, x1, tol, max_iter),
    ]


def executar_experimentos(tol=TOL, max_iter=MAX_ITER):
    """Roda a comparação em todas as funções de FUNCOES."""
    return {nome: comparar(**p, tol=tol, max_iter=max_iter) for nome, p in FUNCOES.items()}


def imprimir_tabela(f, resultados):
    """Imprime os resultados de uma função em colunas alinhadas."""
    print(f"{'Método':<16}{'Raiz':>18}{'Iterações':>11}{'Erro':>12}{'|f(raiz)|':>12}  {'Convergiu':<11}Parada")
    for r in resultados:
        print(
            f"{r.metodo:<16}{r.raiz:>18.14f}{r.iteracoes:>11}{r.erro:>12.2e}"
            f"{abs(_avaliar(f, r.raiz)):>12.2e}  {'sim' if r.convergiu else 'não':<11}{r.parada}"
        )


def imprimir_experimentos():
    """Imprime a configuração usada e a tabela de resultados de cada função."""
    print(f"Python {platform.python_version()} | tol = {TOL:g} | max_iter = {MAX_ITER}")
    for nome, resultados in executar_experimentos().items():
        p = FUNCOES[nome]
        print(f"\nf(x) = {nome} | [a, b] = [{p['a']}, {p['b']}] | x0 = {p['x0']} | x1 = {p['x1']}\n")
        imprimir_tabela(p["f"], resultados)


if __name__ == "__main__":
    imprimir_experimentos()
