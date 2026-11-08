"""Gráficos e tabela comparativa, salvos em resultados/figuras/. Rodar: `python -m raizes_numericas.graficos`."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # só grava arquivos: funciona sem janela gráfica
import matplotlib.pyplot as plt

from .metodos import FUNCOES, executar_experimentos

# Paleta validada para daltonismo; cada método mantém a mesma cor em todos os gráficos.
SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_SECUNDARIO = "#52514e"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"
CURVA = "#2a78d6"
DESTAQUE = "#eb6834"
CORES_METODOS = {"Bisseção": "#2a78d6", "Newton-Raphson": "#eb6834", "Secante": "#1baf7a"}
TITULOS = {"x**3 - x - 2": "f(x) = x³ − x − 2", "cos(x) - x": "f(x) = cos(x) − x", "exp(-x) - x": "f(x) = e⁻ˣ − x"}
# Relativa à pasta de execução: um pacote instalado não deve gravar dentro de si mesmo.
PASTA_FIGURAS = Path("resultados") / "figuras"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
        "font.size": 11,
        "figure.facecolor": SUPERFICIE,
        "axes.facecolor": SUPERFICIE,
        "axes.edgecolor": EIXO,
        "axes.labelcolor": TEXTO_SECUNDARIO,
        "axes.titlecolor": TEXTO,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": TEXTO_SECUNDARIO,
        "ytick.color": TEXTO_SECUNDARIO,
        "savefig.dpi": 200,
    }
)


def grafico_funcoes(experimentos, destino):
    """Um painel por função, com a raiz encontrada em destaque."""
    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.4), layout="constrained")
    for ax, (nome, resultados) in zip(eixos, experimentos.items()):
        p = FUNCOES[nome]
        inicio, fim = p["a"] - 1, p["b"] + 1
        xs = [inicio + (fim - inicio) * i / 400 for i in range(401)]
        # Os três métodos diferem em menos de 1e-11: um marcador só representa todos.
        raiz = resultados[1].raiz
        ax.axhline(0, color=EIXO, linewidth=1)
        ax.grid(color=GRADE, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.plot(xs, [p["f"](x) for x in xs], color=CURVA, linewidth=2)
        ax.plot(raiz, 0, "o", color=DESTAQUE, markersize=9, markeredgecolor=SUPERFICIE, markeredgewidth=2, zorder=5)
        # O rótulo vai para o lado acima do eixo em que a curva não passa.
        crescente = p["df"](raiz) > 0
        ax.annotate(
            f"raiz ≈ {raiz:.8f}",
            (raiz, 0),
            xytext=(-10 if crescente else 10, 12),
            textcoords="offset points",
            ha="right" if crescente else "left",
            color=TEXTO,
            fontweight="bold",
        )
        ax.set_title(TITULOS[nome], loc="left", fontsize=13, fontweight="bold")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
    fig.savefig(destino)
    plt.close(fig)


def grafico_iteracoes(experimentos, destino):
    """Barras agrupadas: iterações de cada método em cada função."""
    fig, ax = plt.subplots(figsize=(9.5, 5), layout="constrained")
    largura = 0.25
    for j, metodo in enumerate(CORES_METODOS):
        valores = [resultados[j].iteracoes for resultados in experimentos.values()]
        posicoes = [i + (j - 1) * largura for i in range(len(experimentos))]
        barras = ax.bar(
            posicoes, valores, largura - 0.03, color=CORES_METODOS[metodo], label=metodo, zorder=3
        )
        ax.bar_label(barras, padding=3, color=TEXTO, fontweight="bold")
    ax.set_xticks(range(len(experimentos)), [TITULOS[nome] for nome in experimentos])
    ax.set_ylabel("Iterações até a parada")
    ax.set_ylim(0, 46)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Número de iterações por método (tol = 1e-12)", loc="left", fontsize=13, fontweight="bold")
    ax.legend(frameon=False, ncols=3, loc="upper right", labelcolor=TEXTO)
    fig.savefig(destino)
    plt.close(fig)


def tabela_comparativa(experimentos, destino):
    """Tabela com o resultado dos três métodos em cada função."""
    colunas = ["Função", "Método", "Raiz", "Iterações", "Erro aproximado", "|f(raiz)|", "Parada"]
    linhas = []
    for nome, resultados in experimentos.items():
        f = FUNCOES[nome]["f"]
        for i, r in enumerate(resultados):
            linhas.append(
                [
                    TITULOS[nome] if i == 0 else "",
                    r.metodo,
                    f"{r.raiz:.12f}",
                    str(r.iteracoes),
                    f"{r.erro:.2e}",
                    f"{abs(f(r.raiz)):.2e}",
                    r.parada,
                ]
            )

    fig, ax = plt.subplots(figsize=(12.5, 4.6), layout="constrained")
    ax.axis("off")
    ax.set_title("Comparação dos métodos (tol = 1e-12)", loc="left", fontsize=13, fontweight="bold")
    tabela = ax.table(
        cellText=linhas,
        colLabels=colunas,
        colWidths=[0.2, 0.15, 0.16, 0.09, 0.14, 0.1, 0.13],
        cellLoc="left",
        colLoc="left",
        loc="center",
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(11)
    tabela.scale(1, 1.75)
    for (linha, _), celula in tabela.get_celld().items():
        celula.visible_edges = "horizontal"
        celula.set_edgecolor(GRADE)
        celula.set_facecolor(SUPERFICIE)
        celula.set_text_props(color=TEXTO, fontweight="bold" if linha == 0 else "normal")
    fig.savefig(destino)
    plt.close(fig)


def gerar_figuras(pasta=PASTA_FIGURAS):
    """Grava as três figuras na pasta indicada e devolve os caminhos."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    experimentos = executar_experimentos()
    caminhos = [pasta / "funcoes_e_raizes.png", pasta / "iteracoes.png", pasta / "tabela_comparativa.png"]
    grafico_funcoes(experimentos, caminhos[0])
    grafico_iteracoes(experimentos, caminhos[1])
    tabela_comparativa(experimentos, caminhos[2])
    return caminhos


if __name__ == "__main__":
    for caminho in gerar_figuras():
        print(caminho)
