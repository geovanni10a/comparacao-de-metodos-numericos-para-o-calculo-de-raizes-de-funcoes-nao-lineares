"""Interface gráfica da demonstração. Rodar: `python interface.py`.

Permite escolher a função, alterar intervalos, valores iniciais e tolerância,
e ver os resultados, os gráficos e a análise completa.
"""

import contextlib
import ctypes
import io
import math
import tkinter as tk
from tkinter import scrolledtext, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from analise import RAIZES_REFERENCIA, imprimir_analise
from graficos import CORES_METODOS, CURVA, DESTAQUE, EIXO, GRADE, SUPERFICIE, TEXTO, TEXTO_SECUNDARIO, TITULOS
from raizes import FUNCOES, MAX_ITER, TOL, _avaliar, bissecao, newton_raphson, secante
from verificacao import imprimir_verificacao

TITULO = "Comparação de Métodos Numéricos para o Cálculo de Raízes de Funções Não Lineares"
SUBTITULO = "Uma Implementação em Python"
COR_ERRO = "#d03b3b"
MARCADORES = {"Bisseção": "o", "Newton-Raphson": "s", "Secante": "^"}
LIMITE_MAX_ITER = 100_000  # acima disso a janela poderia travar durante o cálculo
ROTULOS = {
    "a": "a (Bisseção)",
    "b": "b (Bisseção)",
    "x0": "x0 (Newton e Secante)",
    "x1": "x1 (Secante)",
    "tol": "Tolerância",
    "max_iter": "Máximo de iterações",
}
COLUNAS = {
    "Método": 130,
    "Raiz": 150,
    "Iterações": 75,
    "Erro aproximado": 115,
    "|f(raiz)|": 85,
    "Convergiu": 100,
    "Parada": 280,
}


def ler_parametros(textos):
    """Converte os campos digitados em números. Aceita vírgula decimal; levanta ValueError."""
    numeros = {}
    for campo in ("a", "b", "x0", "x1", "tol"):
        try:
            numeros[campo] = float(textos[campo].strip().replace(",", "."))
        except ValueError:
            raise ValueError(f"Valor inválido em {ROTULOS[campo]}.") from None
    try:
        numeros["max_iter"] = int(textos["max_iter"].strip())
    except ValueError:
        raise ValueError(f"{ROTULOS['max_iter']} precisa ser um número inteiro.") from None
    if not 1 <= numeros["max_iter"] <= LIMITE_MAX_ITER:
        raise ValueError(f"{ROTULOS['max_iter']} precisa estar entre 1 e {LIMITE_MAX_ITER}.")
    return numeros


def executar_metodos(nome, n):
    """Roda cada método separadamente: uma condição inválida não impede os outros dois.

    Devolve uma lista de (método, Resultado ou None, mensagem de erro ou None).
    """
    f, df = FUNCOES[nome]["f"], FUNCOES[nome]["df"]
    chamadas = (
        ("Bisseção", lambda: bissecao(f, n["a"], n["b"], n["tol"], n["max_iter"])),
        ("Newton-Raphson", lambda: newton_raphson(f, df, n["x0"], n["tol"], n["max_iter"])),
        ("Secante", lambda: secante(f, n["x0"], n["x1"], n["tol"], n["max_iter"])),
    )
    saidas = []
    for metodo, chamada in chamadas:
        try:
            saidas.append((metodo, chamada(), None))
        except ValueError as erro:
            saidas.append((metodo, None, str(erro)))
    return saidas


def linha_da_tabela(nome, metodo, resultado, mensagem):
    """Monta os textos de uma linha da tabela de resultados."""
    if resultado is None:
        return (metodo, "—", "—", "—", "—", "não se aplica", mensagem)
    residuo = abs(_avaliar(FUNCOES[nome]["f"], resultado.raiz))
    return (
        metodo,
        f"{resultado.raiz:.12f}",
        resultado.iteracoes,
        f"{resultado.erro:.2e}",
        f"{residuo:.2e}",
        "sim" if resultado.convergiu else "não",
        resultado.parada,
    )


def _estilizar_eixos(ax):
    ax.set_facecolor(SUPERFICIE)
    ax.grid(color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def desenhar_funcao(fig, nome, n, saidas):
    """Desenha a função no trecho dos dados digitados e destaca a raiz encontrada."""
    fig.clear()
    ax = fig.add_subplot()
    _estilizar_eixos(ax)
    p = FUNCOES[nome]
    pontos = [RAIZES_REFERENCIA[nome]] + [n[c] for c in ("a", "b", "x0", "x1") if math.isfinite(n[c])]
    inicio, fim = min(pontos) - 1, max(pontos) + 1
    xs = [inicio + (fim - inicio) * i / 500 for i in range(501)]
    ax.axhline(0, color=EIXO, linewidth=1)
    ax.plot(xs, [_avaliar(p["f"], x) for x in xs], color=CURVA, linewidth=2)

    # Quem converge chega à mesma raiz dentro da tolerância: um marcador só representa todos.
    raiz = next((r.raiz for _, r, _ in saidas if r is not None and r.convergiu), None)
    if raiz is not None:
        ax.plot(raiz, 0, "o", color=DESTAQUE, markersize=9, markeredgecolor=SUPERFICIE, markeredgewidth=2, zorder=5)
        crescente = p["df"](raiz) > 0  # o rótulo vai para o lado em que a curva não passa
        ax.annotate(
            f"raiz ≈ {raiz:.8f}",
            (raiz, 0),
            xytext=(-10 if crescente else 10, 12),
            textcoords="offset points",
            ha="right" if crescente else "left",
            color=TEXTO,
            fontweight="bold",
        )
    ax.set_title(TITULOS[nome], loc="left", fontsize=13, fontweight="bold", color=TEXTO)
    ax.set_xlabel("x", color=TEXTO_SECUNDARIO)
    ax.set_ylabel("f(x)", color=TEXTO_SECUNDARIO)


def desenhar_convergencia(fig, nome, n, saidas):
    """Desenha o erro real a cada iteração, em escala logarítmica."""
    fig.clear()
    ax = fig.add_subplot()
    _estilizar_eixos(ax)
    referencia = RAIZES_REFERENCIA[nome]
    for metodo, r, _ in saidas:
        if r is None:
            continue
        primeira = r.iteracoes - len(r.aproximacoes) + 1
        # Erro zero não existe em escala logarítmica; k < 0 é o primeiro chute da Secante.
        pontos = [
            (k, abs(x - referencia))
            for k, x in enumerate(r.aproximacoes, primeira)
            if k >= 0 and 0 < abs(x - referencia) < math.inf
        ]
        if pontos:
            ax.semilogy(
                *zip(*pontos),
                color=CORES_METODOS[metodo],
                marker=MARCADORES[metodo],
                markersize=6,
                linewidth=2,
                label=metodo,
            )
    if n["tol"] > 0:
        ax.axhline(n["tol"], color=TEXTO_SECUNDARIO, linewidth=1, linestyle="--", label="Tolerância")
    ax.set_title(f"Erro real por iteração: {TITULOS[nome]}", loc="left", fontsize=13, fontweight="bold", color=TEXTO)
    ax.set_xlabel("Iteração", color=TEXTO_SECUNDARIO)
    ax.set_ylabel("|x_k − raiz|", color=TEXTO_SECUNDARIO)
    if ax.get_legend_handles_labels()[0]:
        ax.legend(frameon=False, labelcolor=TEXTO)


def desenhar_iteracoes(fig, nome, saidas):
    """Desenha uma barra por método com o número de iterações."""
    fig.clear()
    ax = fig.add_subplot()
    _estilizar_eixos(ax)
    ax.grid(False, axis="x")
    validas = [(metodo, r) for metodo, r, _ in saidas if r is not None]
    barras = ax.bar(
        [metodo for metodo, _ in validas],
        [r.iteracoes for _, r in validas],
        width=0.5,
        color=[CORES_METODOS[metodo] for metodo, _ in validas],
        zorder=3,
    )
    ax.bar_label(barras, padding=3, color=TEXTO, fontweight="bold")
    ax.margins(y=0.12)
    ax.set_title(f"Número de iterações: {TITULOS[nome]}", loc="left", fontsize=13, fontweight="bold", color=TEXTO)
    ax.set_ylabel("Iterações até a parada", color=TEXTO_SECUNDARIO)


def texto_da_analise():
    """Devolve o relatório completo que o programa imprime no terminal."""
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        imprimir_analise()
        imprimir_verificacao()
    return saida.getvalue()


class Aplicacao:
    """Janela principal: painel de parâmetros à esquerda e abas de resultados à direita."""

    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title(f"{TITULO}: {SUBTITULO}")
        raiz.geometry("1280x800")
        raiz.minsize(1000, 640)
        raiz.configure(background=SUPERFICIE)
        self.dpi = raiz.winfo_fpixels("1i")
        self._configurar_estilos()

        cabecalho = ttk.Frame(raiz, padding=(20, 14, 20, 8))
        cabecalho.pack(fill="x")
        ttk.Label(cabecalho, text=TITULO, style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(cabecalho, text=SUBTITULO, style="Secundario.TLabel").pack(anchor="w")

        corpo = ttk.Frame(raiz, padding=(20, 4, 20, 16))
        corpo.pack(fill="both", expand=True)
        self._criar_painel(corpo)
        self._criar_abas(corpo)
        self.aplicar_funcao()

    def _configurar_estilos(self):
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")
        fonte = ("Segoe UI", 10)
        estilo.configure(".", background=SUPERFICIE, foreground=TEXTO, font=fonte)
        estilo.configure("Titulo.TLabel", font=("Segoe UI Semibold", 15))
        estilo.configure("Secundario.TLabel", foreground=TEXTO_SECUNDARIO)
        estilo.configure("Erro.TLabel", foreground=COR_ERRO)
        estilo.configure("Secao.TLabel", font=("Segoe UI Semibold", 11))
        estilo.configure("TEntry", fieldbackground="white", bordercolor=EIXO, padding=5)
        estilo.configure("TCombobox", fieldbackground="white", bordercolor=EIXO, padding=5)
        estilo.map("TCombobox", fieldbackground=[("readonly", "white")], foreground=[("readonly", TEXTO)])
        estilo.configure("Acao.TButton", background=CURVA, foreground="white", bordercolor=CURVA, padding=9)
        estilo.map("Acao.TButton", background=[("active", "#256abf")])
        estilo.configure("TButton", background="#f0efec", bordercolor=EIXO, padding=7)
        estilo.configure("TNotebook", background=SUPERFICIE, bordercolor=GRADE)
        estilo.configure("TNotebook.Tab", background="#f0efec", padding=(14, 7), bordercolor=GRADE)
        estilo.map("TNotebook.Tab", background=[("selected", SUPERFICIE)])
        estilo.configure("Treeview", background=SUPERFICIE, fieldbackground=SUPERFICIE, rowheight=30, bordercolor=GRADE)
        estilo.configure("Treeview.Heading", background="#f0efec", font=("Segoe UI Semibold", 10), bordercolor=GRADE)

    def _criar_painel(self, corpo):
        painel = ttk.Frame(corpo, width=270, padding=(0, 8, 20, 0))
        painel.pack(side="left", fill="y")
        painel.pack_propagate(False)

        ttk.Label(painel, text="Função", style="Secao.TLabel").pack(anchor="w")
        self.nomes_por_titulo = {TITULOS[nome]: nome for nome in FUNCOES}
        self.funcao = tk.StringVar(value=next(iter(self.nomes_por_titulo)))
        seletor = ttk.Combobox(painel, textvariable=self.funcao, values=list(self.nomes_por_titulo), state="readonly")
        seletor.pack(fill="x", pady=(4, 14))
        seletor.bind("<<ComboboxSelected>>", lambda _: self.aplicar_funcao())

        ttk.Label(painel, text="Parâmetros", style="Secao.TLabel").pack(anchor="w")
        self.campos = {}
        for campo, rotulo in ROTULOS.items():
            ttk.Label(painel, text=rotulo, style="Secundario.TLabel").pack(anchor="w", pady=(6, 1))
            self.campos[campo] = tk.StringVar()
            entrada = ttk.Entry(painel, textvariable=self.campos[campo])
            entrada.pack(fill="x")
            entrada.bind("<Return>", lambda _: self.calcular())

        ttk.Button(painel, text="Calcular", style="Acao.TButton", command=self.calcular).pack(fill="x", pady=(16, 6))
        ttk.Button(painel, text="Restaurar valores", command=self.aplicar_funcao).pack(fill="x")
        self.mensagem = ttk.Label(painel, style="Erro.TLabel", wraplength=240, justify="left")
        self.mensagem.pack(anchor="w", pady=(10, 0))

    def _criar_abas(self, corpo):
        abas = ttk.Notebook(corpo)
        abas.pack(side="left", fill="both", expand=True)

        aba_resultados = ttk.Frame(abas, padding=10)
        abas.add(aba_resultados, text="Resultados")
        self.tabela = ttk.Treeview(aba_resultados, columns=list(COLUNAS), show="headings", height=3, selectmode="none")
        for coluna, largura in COLUNAS.items():
            self.tabela.heading(coluna, text=coluna, anchor="w")
            self.tabela.column(coluna, width=largura, minwidth=60, stretch=coluna == "Parada", anchor="w")
        self.tabela.pack(fill="x")
        self.fig_funcao = self._criar_grafico(aba_resultados)

        self.fig_convergencia = self._criar_grafico(self._nova_aba(abas, "Convergência"))
        self.fig_iteracoes = self._criar_grafico(self._nova_aba(abas, "Iterações"))

        aba_analise = self._nova_aba(abas, "Análise e verificação")
        texto = scrolledtext.ScrolledText(aba_analise, wrap="none", font=("Consolas", 10), relief="flat")
        texto.configure(background=SUPERFICIE, foreground=TEXTO)
        texto.insert("1.0", texto_da_analise())
        texto.configure(state="disabled")  # relatório somente para leitura
        texto.pack(fill="both", expand=True)

    def _nova_aba(self, abas, titulo):
        aba = ttk.Frame(abas, padding=10)
        abas.add(aba, text=titulo)
        return aba

    def _criar_grafico(self, pai):
        fig = Figure(dpi=self.dpi, layout="constrained", facecolor=SUPERFICIE)
        canvas = FigureCanvasTkAgg(fig, master=pai)
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=(10, 0))
        return fig

    def aplicar_funcao(self):
        """Preenche os campos com os valores do experimento-base e recalcula."""
        p = FUNCOES[self.nomes_por_titulo[self.funcao.get()]]
        for campo in ("a", "b", "x0", "x1"):
            self.campos[campo].set(p[campo])
        self.campos["tol"].set(f"{TOL:g}")
        self.campos["max_iter"].set(MAX_ITER)
        self.calcular()

    def calcular(self):
        """Lê os campos, roda os métodos e atualiza a tabela e os gráficos."""
        nome = self.nomes_por_titulo[self.funcao.get()]
        try:
            numeros = ler_parametros({campo: var.get() for campo, var in self.campos.items()})
        except ValueError as erro:
            self.mensagem.configure(text=f"Erro: {erro}")
            return
        self.mensagem.configure(text="")

        saidas = executar_metodos(nome, numeros)
        self.tabela.delete(*self.tabela.get_children())
        for metodo, resultado, mensagem in saidas:
            self.tabela.insert("", "end", values=linha_da_tabela(nome, metodo, resultado, mensagem))

        desenhar_funcao(self.fig_funcao, nome, numeros, saidas)
        desenhar_convergencia(self.fig_convergencia, nome, numeros, saidas)
        desenhar_iteracoes(self.fig_iteracoes, nome, saidas)
        for fig in (self.fig_funcao, self.fig_convergencia, self.fig_iteracoes):
            fig.canvas.draw_idle()


def main():
    # Sem isto, o Windows amplia a janela e o texto fica borrado em telas com escala acima de 100%.
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
    raiz = tk.Tk()
    Aplicacao(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
