"""Análise comparativa dos métodos: iterações, precisão, velocidade e estabilidade.

Rodar `python analise.py` repete toda a análise. Nada aqui usa números aleatórios.
"""

import math
from statistics import linear_regression, median

from raizes import FUNCOES, bissecao, executar_experimentos, newton_raphson, secante

# Raízes de referência, independentes dos métodos comparados.
# teste_analise.py confirma que f troca de sinal em volta de cada uma.
RAIZES_REFERENCIA = {
    "x**3 - x - 2": 1.5213797068045676,
    "cos(x) - x": 0.7390851332151607,
    "exp(-x) - x": 0.5671432904097838,
}

# Abaixo disso o erro é dominado pelo arredondamento e distorce a ordem estimada.
LIMITE_ARREDONDAMENTO = 1e-13
ERRO_ALVO = 1e-6  # erro usado para comparar a velocidade em iterações
PONTOS_GRADE = 200  # condições iniciais testadas por função
RAIO_GRADE = 10.0  # maior distância entre a condição inicial e a raiz
TOLERANCIA_ACERTO = 1e-9  # distância máxima para considerar que chegou à raiz

# Casos fora das três funções do estudo, que mudam o resultado da comparação.
CASOS_DEPENDENCIA = [
    (
        "x**3 - 2*x + 2, com x0 = 0 (condição inicial desfavorável)",
        dict(f=lambda x: x**3 - 2 * x + 2, df=lambda x: 3 * x**2 - 2, a=-3, b=-1, x0=0, x1=0.5),
    ),
    (
        "(x - 1)**2 (raiz dupla, sem troca de sinal)",
        dict(f=lambda x: (x - 1) ** 2, df=lambda x: 2 * (x - 1), a=0, b=3, x0=2, x1=3),
    ),
]

VANTAGENS_LIMITACOES = {
    "Bisseção": (
        "convergência garantida se f for contínua e trocar de sinal em [a, b]; não usa derivada.",
        "convergência lenta (ordem 1, o intervalo cai pela metade a cada iteração); "
        "exige troca de sinal, logo não encontra raízes de multiplicidade par.",
    ),
    "Newton-Raphson": (
        "ordem 2 perto de raiz simples; precisa de um único valor inicial.",
        "exige a derivada e duas avaliações por iteração; pode divergir, entrar em ciclo "
        "ou parar se f'(x) = 0; a ordem cai para 1 em raiz múltipla.",
    ),
    "Secante": (
        "ordem de cerca de 1,618 perto de raiz simples; não usa derivada e faz uma avaliação nova por iteração.",
        "exige dois valores iniciais e não tem convergência garantida; "
        "para se f(x_k) = f(x_(k-1)); também perde velocidade em raiz múltipla.",
    ),
}

CONCLUSAO = (
    "Nenhum método é universalmente melhor. O desempenho depende da função (derivada disponível, "
    "multiplicidade da raiz, continuidade) e das condições iniciais (distância até a raiz, região de "
    "derivada pequena). Newton-Raphson e Secante tendem a exigir menos iterações perto de raízes simples, "
    "mas podem falhar longe delas. A Bisseção é mais lenta, mas é previsível quando há troca de sinal em "
    "um intervalo de função contínua. Iterações também não medem o custo total, pois o custo por iteração "
    "muda de método para método."
)


def ordem_estimada(resultado, referencia):
    """Inclinação da regressão de ln e_(k+1) contra ln e_k; NaN se houver dados insuficientes.

    Usa a sequência inteira porque a razão entre erros vizinhos oscila muito na Bisseção.
    """
    erros = [abs(x - referencia) for x in resultado.aproximacoes]
    logs = [math.log(e) for e in erros if e > LIMITE_ARREDONDAMENTO]
    if len(set(logs[:-1])) < 2:
        return math.nan
    return linear_regression(logs[:-1], logs[1:]).slope


def iteracoes_ate_erro(resultado, referencia, alvo=ERRO_ALVO):
    """Primeira iteração com |x_k - referência| <= alvo; None se nunca chegar lá."""
    aproximacoes = resultado.aproximacoes
    for i, x in enumerate(aproximacoes):
        if abs(x - referencia) <= alvo:
            return max(0, resultado.iteracoes - (len(aproximacoes) - 1 - i))
    return None


def estabilidade(parametros, referencia, pontos=PONTOS_GRADE, raio=RAIO_GRADE):
    """Repete cada método numa grade de condições iniciais em volta da raiz.

    Devolve, por método: % de execuções que chegaram à raiz, mediana e máximo de iterações.
    A grade só serve para funções com uma única raiz real, com f < 0 de um lado e f > 0 do outro.
    """
    f, df = parametros["f"], parametros["df"]
    execucoes = {"Bisseção": [], "Newton-Raphson": [], "Secante": []}
    for i in range(pontos):
        desvio = raio * (2 * i / (pontos - 1) - 1)
        x0 = referencia + desvio
        # Margens desiguais evitam que o primeiro ponto médio caia exatamente na raiz.
        execucoes["Bisseção"].append(bissecao(f, referencia - abs(desvio) - 0.3, referencia + abs(desvio) + 0.7))
        execucoes["Newton-Raphson"].append(newton_raphson(f, df, x0))
        execucoes["Secante"].append(secante(f, x0, x0 + 0.5))

    resumo = {}
    for metodo, resultados in execucoes.items():
        acertos = [r.iteracoes for r in resultados if r.convergiu and abs(r.raiz - referencia) < TOLERANCIA_ACERTO]
        resumo[metodo] = (
            100 * len(acertos) / pontos,
            median(acertos) if acertos else math.nan,
            max(acertos) if acertos else math.nan,
        )
    return resumo


def _tentar(chamada):
    """Devolve o Resultado, ou None se as condições do método não forem atendidas."""
    try:
        return chamada()
    except ValueError:
        return None


def imprimir_comparacao():
    """Imprime iterações, precisão e velocidade de cada método."""
    print("1. ITERAÇÕES, PRECISÃO E VELOCIDADE")
    print("Erro real = |x - raiz de referência|; ordem = estimativa empírica a partir das iterações.")
    for nome, resultados in executar_experimentos().items():
        referencia = RAIZES_REFERENCIA[nome]
        f = FUNCOES[nome]["f"]
        print(f"\nf(x) = {nome}")
        print(f"{'Método':<16}{'Iterações':>10}{'Erro real':>12}{'|f(x)|':>12}{'Iter. p/ 1e-6':>15}{'Ordem':>8}")
        for r in resultados:
            print(
                f"{r.metodo:<16}{r.iteracoes:>10}{abs(r.raiz - referencia):>12.2e}{abs(f(r.raiz)):>12.2e}"
                f"{iteracoes_ate_erro(r, referencia):>15}{ordem_estimada(r, referencia):>8.2f}"
            )


def imprimir_estabilidade():
    """Imprime o comportamento na grade de condições iniciais."""
    print(f"\n2. ESTABILIDADE: {PONTOS_GRADE} condições iniciais a até {RAIO_GRADE:g} da raiz")
    print("Newton: x0 na grade. Secante: x0 e x0 + 0,5. Bisseção: intervalo que aumenta com a distância.")
    for nome, parametros in FUNCOES.items():
        print(f"\nf(x) = {nome}")
        print(f"{'Método':<16}{'Chegou à raiz':>15}{'Iter. mediana':>15}{'Iter. máxima':>14}")
        for metodo, (percentual, mediana, maximo) in estabilidade(parametros, RAIZES_REFERENCIA[nome]).items():
            print(f"{metodo:<16}{percentual:>14.1f}%{mediana:>15.1f}{maximo:>14}")


def imprimir_casos_dependencia():
    """Imprime os casos em que a função ou o chute muda o resultado da comparação."""
    print("\n3. O RESULTADO DEPENDE DA FUNÇÃO E DAS CONDIÇÕES INICIAIS")
    for descricao, p in CASOS_DEPENDENCIA:
        print(f"\nf(x) = {descricao}")
        chamadas = (
            ("Bisseção", lambda: bissecao(p["f"], p["a"], p["b"])),
            ("Newton-Raphson", lambda: newton_raphson(p["f"], p["df"], p["x0"])),
            ("Secante", lambda: secante(p["f"], p["x0"], p["x1"])),
        )
        for metodo, chamada in chamadas:
            r = _tentar(chamada)
            if r is None:
                print(f"{metodo:<16}não se aplica: condições do método não atendidas")
            else:
                situacao = "convergiu" if r.convergiu else "não convergiu"
                print(f"{metodo:<16}{situacao}, {r.iteracoes} iterações, x = {r.raiz:.10f}, parada: {r.parada}")


def imprimir_vantagens_e_conclusao():
    """Imprime as vantagens, as limitações e a conclusão."""
    print("\n4. VANTAGENS E LIMITAÇÕES")
    for metodo, (vantagens, limitacoes) in VANTAGENS_LIMITACOES.items():
        print(f"\n{metodo}\n  Vantagens: {vantagens}\n  Limitações: {limitacoes}")
    print(f"\n5. CONCLUSÃO\n{CONCLUSAO}")


def imprimir_analise():
    """Imprime a análise comparativa completa."""
    imprimir_comparacao()
    imprimir_estabilidade()
    imprimir_casos_dependencia()
    imprimir_vantagens_e_conclusao()


if __name__ == "__main__":
    imprimir_analise()
