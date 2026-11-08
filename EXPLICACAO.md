# Comparação de Métodos Numéricos para o Cálculo de Raízes de Funções Não Lineares: Uma Implementação em Python

**Autoria:** geovanni10a.

## Resumo

Este trabalho compara os métodos da Bisseção, de Newton-Raphson e da Secante na determinação de
raízes de três funções não lineares, por meio de uma implementação própria em Python com tolerância
de `1e-12`. A metodologia controla o critério de parada e o limite de iterações, mede iterações,
erro real, resíduo e ordem empírica de convergência, e avalia o comportamento em 200 condições
iniciais por função. Nos experimentos-base, a Bisseção exigiu 40 iterações, Newton-Raphson 4 e a
Secante 5 ou 6. As ordens estimadas foram de 0,98 a 0,99, de 2,00 a 2,02 e de 1,44 a 1,64,
respectivamente. Verificações automáticas confirmaram a existência de raiz junto a cada resultado,
a previsão teórica de iterações da Bisseção e as leis assintóticas de erro, com desvio máximo de
0,10%. Os resultados indicam que nenhum método é universalmente superior: o desempenho depende da
função e das condições iniciais.

**Palavras-chave:** cálculo numérico; raízes de funções; ordem de convergência; experimentação
computacional; Python.

## 1. Introdução

A determinação de raízes de equações não lineares é um problema central do Cálculo Numérico, pois
muitas equações não admitem solução por fórmula fechada de uso prático (BURDEN; FAIRES; BURDEN,
2016; ATKINSON, 1989). Métodos iterativos resolvem esse problema, mas diferem nas exigências sobre
a função, na velocidade e nas garantias de convergência.

O objetivo deste trabalho é comparar experimentalmente três métodos clássicos, confrontando as
medições com as previsões teóricas. A demonstração computacional é reprodutível: um único comando
repete os experimentos, verifica os resultados e exporta os dados brutos.

Todos os números citados vêm da execução de `python main.py`, com tolerância `tol = 1e-12`.

O código completo está nos arquivos do projeto:

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Ponto de entrada: executa experimentos, análise e gráficos |
| `raizes.py` | Os três métodos e as três funções estudadas |
| `analise.py` | Análise comparativa |
| `verificacao.py` | Verificação dos resultados e exportação para `resultados/` |
| `graficos.py` | Gráficos e tabela em imagem, gravados em `figuras/` |
| `interface.py` | Interface gráfica da demonstração |
| `construir_exe.bat` | Gera o executável `dist\RaizesNumericas.exe` |
| `teste_*.py` | Testes automáticos (`python -m unittest`) |
| `requirements.txt` | Versão do Matplotlib usada |

## 2. Funcionamento matemático de cada método

Encontrar uma raiz significa encontrar `r` tal que `f(r) = 0`. Para as funções estudadas não
existe uma fórmula elementar simples para `r`, então cada método constrói uma sequência
`x_0, x_1, x_2, ...` que se aproxima da raiz.

### Bisseção

O método parte de um intervalo `[a, b]` em que `f(a)` e `f(b)` têm sinais opostos. A cada
iteração:

1. calcula o ponto médio `c = (a + b) / 2`;
2. verifica em qual metade `f` ainda troca de sinal;
3. substitui `[a, b]` por essa metade.

O método usa apenas o sinal de `f`, e a raiz permanece sempre dentro do intervalo.

### Newton-Raphson

A partir de uma aproximação `x_k`, o método traça a reta tangente ao gráfico de `f` nesse ponto.
O próximo valor `x_(k+1)` é o ponto em que a tangente cruza o eixo x:

```
x_(k+1) = x_k − f(x_k) / f'(x_k)
```

### Secante

O método substitui a tangente pela reta que passa pelos dois últimos pontos da sequência:

```
x_(k+1) = x_k − f(x_k) · (x_k − x_(k−1)) / (f(x_k) − f(x_(k−1)))
```

## 3. Fundamentação das fórmulas

Os resultados teóricos desta seção são clássicos e podem ser consultados em Burden, Faires e Burden
(2016) e em Atkinson (1989).

### Bisseção: Teorema do Valor Intermediário

Se `f` é contínua em `[a, b]` e `f(a)` e `f(b)` têm sinais opostos, existe ao menos uma raiz em
`(a, b)`. Como o intervalo cai pela metade a cada iteração, o ponto médio `c_k` satisfaz:

```
|c_k − r| ≤ (b − a) / 2^k
```

Para garantir erro máximo `tol`, basta:

```
k ≥ log2((b − a) / tol)
```

### Newton-Raphson: série de Taylor

Expandindo `f` em torno de `x_k` e avaliando na raiz `r`, para algum `ξ` entre `x_k` e `r`:

```
0 = f(r) = f(x_k) + f'(x_k)(r − x_k) + ½ f''(ξ)(r − x_k)²
```

Desprezar o termo quadrático e isolar `r` produz a fórmula do método. Mantendo esse termo e
definindo o erro `e_k = x_k − r`, obtém-se, perto de uma raiz simples:

```
e_(k+1) ≈ C · e_k²,    com C = f''(r) / (2 f'(r))
```

Essa é a **convergência de ordem 2**: o número de casas decimais corretas tende a dobrar a cada
iteração. Em uma raiz de multiplicidade `m > 1`, a convergência passa a ser linear, com razão
`(m − 1) / m`.

### Secante: aproximação da derivada

A derivada é trocada pela diferença dividida:

```
f'(x_k) ≈ (f(x_k) − f(x_(k−1))) / (x_k − x_(k−1))
```

Perto de uma raiz simples, o erro satisfaz, com a mesma constante `C`:

```
e_(k+1) ≈ C · e_k · e_(k−1)
```

Supondo `e_(k+1) ≈ A · e_k^p`, a relação acima leva a `p = 1 + 1/p`, ou seja, `p² − p − 1 = 0`.
A solução positiva é a razão áurea, `p = (1 + √5) / 2 ≈ 1,618`.

### Verificação com os dados do projeto

Para `f(x) = x³ − x − 2`, temos `r ≈ 1,52138` e `C = 6r / (2(3r² − 1)) ≈ 0,768`. O erro real
medido em cada iteração foi:

| Iteração | Bisseção | Newton-Raphson | Secante |
|---|---|---|---|
| Valor inicial | não há | `2,14e-02` | `2,14e-02` e `4,79e-01` |
| 1 | `2,14e-02` | `3,59e-04` | `6,23e-03` |
| 2 | `2,29e-01` | `9,92e-08` | `1,80e-03` |
| 3 | `1,04e-01` | `7,55e-15` | `8,66e-06` |
| 4 | `4,11e-02` | `0` | `1,20e-08` |
| 5 | `9,87e-03` | | `7,99e-14` |
| 6 | `5,75e-03` | | `0` |

As fórmulas de erro preveem esses valores:

- Newton-Raphson: `0,768 · (9,92e-08)² ≈ 7,56e-15`, e o medido foi `7,55e-15`.
- Secante: `0,768 · (1,20e-08) · (8,66e-06) ≈ 7,98e-14`, e o medido foi `7,99e-14`.

O erro da Bisseção não diminui a cada passo: ele subiu de `2,14e-02` para `2,29e-01` na segunda
iteração. O que diminui sempre é o tamanho do intervalo, e é ele que limita o erro.

## 4. Metodologia experimental

### Hipóteses

- **H1:** o número de iterações da Bisseção é `teto(log2((b − a) / tol))`, independentemente da
  forma de `f`.
- **H2:** perto de raízes simples, os erros seguem `C · e_k²` em Newton-Raphson e
  `C · e_k · e_(k−1)` na Secante.
- **H3:** nenhum método apresenta o menor custo e a maior robustez em todos os cenários.

### Variáveis

| Tipo | Variáveis |
|---|---|
| Independentes | Método, função e condição inicial |
| Controladas | `tol = 1e-12`, `max_iter = 100`, critério de parada e ambiente de execução |
| Resposta | Iterações, erro real, resíduo, ordem empírica, iterações até erro `1e-6` e taxa de chegada à raiz |

### Condições iniciais dos experimentos-base

| Função | Intervalo (Bisseção) | `x0` (Newton-Raphson) | `x0` e `x1` (Secante) |
|---|---|---|---|
| `x³ − x − 2` | `[1, 2]` | `1,5` | `1,5` e `2` |
| `cos(x) − x` | `[0, 1]` | `0,5` | `0,5` e `1` |
| `e^(−x) − x` | `[0, 1]` | `0,5` | `0,5` e `1` |

### Procedimento

1. **Experimento-base:** executar os três métodos nas três funções, nas condições acima.
2. **Precisão e velocidade:** medir o erro real contra raízes de referência e estimar a ordem pela
   regressão linear de `ln e_(k+1)` contra `ln e_k`.
3. **Estabilidade:** repetir os métodos em 200 condições iniciais a até 10 unidades da raiz. Uma
   execução é um acerto se convergir e terminar a menos de `1e-9` da referência.
4. **Dependência do problema:** executar os métodos em dois casos desfavoráveis: `x³ − 2x + 2`
   com `x0 = 0` e `(x − 1)²`.
5. **Verificação:** confrontar os resultados com fatos matemáticos independentes (seção 9).

### Reprodução

O experimento não usa números aleatórios. Foi executado em Windows 11, com Python 3.12.10, números
em ponto flutuante de precisão dupla (IEEE, 2019) e Matplotlib 3.11.2 (HUNTER, 2007) para as
figuras. Para repetir tudo:

```
python -m pip install -r requirements.txt
python main.py
python -m unittest
```

## 5. Significado de cada variável

### Comuns aos métodos

| Variável | Significado |
|---|---|
| `f` | Função cuja raiz é procurada |
| `df` | Derivada de `f`, usada só em Newton-Raphson |
| `tol` | Tolerância de parada, `1e-12` |
| `max_iter` | Limite de iterações, `100` |
| `k` | Número da iteração atual |
| `erro` | Erro aproximado: último `|x_k − x_(k−1)|`; na Bisseção, a meia-largura do intervalo |
| `aproximacoes` | Lista dos valores gerados |
| `nome` | Nome do método registrado no resultado |

### Específicas de cada método

| Variável | Método | Significado |
|---|---|---|
| `a`, `b` | Bisseção | Extremos do intervalo atual |
| `c` | Bisseção | Ponto médio do intervalo |
| `fa`, `fb`, `fc` | Bisseção | Valores de `f` em `a`, `b` e `c` |
| `limite_f` | Bisseção | Maior `|f|` nos extremos iniciais, usado para detectar polos |
| `x0` | Newton e Secante | Valor inicial |
| `x`, `novo` | Newton | Aproximações atual e seguinte |
| `fx`, `dfx` | Newton | `f(x)` e `f'(x)` |
| `x1`, `x2` | Secante | Aproximação atual e seguinte; `x0` guarda a anterior |
| `f0`, `f1` | Secante | `f(x0)` e `f(x1)` |

### Campos de `Resultado`

| Campo | Significado |
|---|---|
| `metodo` | Nome do método |
| `raiz` | Melhor aproximação obtida |
| `iteracoes` | Iterações realizadas |
| `erro` | Erro aproximado final |
| `convergiu` | `True` se o método convergiu |
| `aproximacoes` | Histórico da sequência |
| `parada` | Motivo da parada |

### Variáveis da análise

| Variável | Significado |
|---|---|
| `referencia` | Raiz de referência, independente dos métodos |
| `e_k` (`erros`) | Erro real `|x_k − referencia|` |
| `desvio` | Distância com sinal entre o valor inicial e a raiz, na grade de estabilidade |

## 6. Função de cada parte do código

### `raizes.py`

| Parte | Função |
|---|---|
| `TOL`, `MAX_ITER` | Parâmetros numéricos do experimento |
| `FUNCOES` | Funções, derivadas, intervalos e valores iniciais |
| `PARADA_*` | Nomes dos motivos de parada |
| `Resultado` | Estrutura de saída comum aos três métodos |
| `_avaliar` | Calcula `f(x)` e devolve `NaN` em polo, fora do domínio ou overflow |
| `_validar` | Rejeita tolerância, limite de iterações ou pontos inválidos |
| `bissecao`, `newton_raphson`, `secante` | Implementação independente de cada método |
| `comparar` | Executa os três métodos em uma função |
| `executar_experimentos` | Executa a comparação nas três funções |
| `imprimir_tabela`, `imprimir_experimentos` | Mostram os resultados no terminal |

### `analise.py`

| Parte | Função |
|---|---|
| `RAIZES_REFERENCIA` | Valores usados para medir o erro real |
| `ordem_estimada` | Estima a ordem pela regressão de `ln e_(k+1)` contra `ln e_k` |
| `iteracoes_ate_erro` | Conta as iterações até o erro real chegar a `1e-6` |
| `estabilidade` | Repete os métodos em 200 condições iniciais |
| `CASOS_DEPENDENCIA` | Exemplos em que a função ou o valor inicial mudam o resultado |
| `VANTAGENS_LIMITACOES`, `CONCLUSAO` | Texto da análise |
| `imprimir_*` | Montam o relatório |

### `verificacao.py`, `graficos.py` e `main.py`

| Parte | Função |
|---|---|
| `certifica_raiz` | Prova, pela troca de sinal, que há raiz junto ao resultado |
| `constante_erro`, `desvio_lei_erro` | Comparam o erro medido com o previsto pela teoria |
| `verificar`, `imprimir_verificacao` | Executam e mostram as 22 verificações |
| `exportar_resultados` | Grava os dados em `resultados/` com todos os dígitos |
| `grafico_funcoes` | Desenha as funções e marca as raízes |
| `grafico_iteracoes` | Compara o número de iterações em barras |
| `tabela_comparativa` | Gera a tabela de resultados em imagem |
| `gerar_figuras` | Grava as três imagens em `figuras/` |
| `main` | Executa tudo; sem Matplotlib, pula as figuras; termina com erro se alguma verificação falhar |

### Proteções numéricas

- **Divisão por zero:** Newton-Raphson para se `f'(x) = 0`, e a Secante para se
  `f(x_k) = f(x_(k−1))`.
- **Domínio e overflow:** `_avaliar` transforma essas falhas em `NaN`, e o método termina com
  `f não calculável`.
- **Polo na Bisseção:** se `|f|` termina maior que nos extremos iniciais, o resultado é marcado
  como `possível descontinuidade`.
- **Laço sem fim:** `max_iter` interrompe ciclos e divergências lentas.

## 7. Como interpretar os resultados

### Colunas das tabelas

| Coluna | Como ler |
|---|---|
| Raiz | Aproximação final |
| Iterações | Passos realizados até a parada |
| Erro | Tamanho do último passo; estima o erro, mas não é o erro real |
| Erro real | Distância até a raiz de referência |
| `|f(raiz)|` | Resíduo: quanto `f` difere de zero na aproximação |
| Iter. p/ 1e-6 | Velocidade prática para atingir precisão intermediária |
| Ordem | Estimativa empírica da ordem de convergência |
| Parada | Motivo pelo qual o método terminou |

Três observações evitam erros de leitura:

- **`|f(raiz)| = 0` não prova que a raiz é exata.** Significa que o cálculo em ponto flutuante
  resultou em zero.
- **Erro real `0,00e+00` significa igualdade com a referência em precisão `double`.** Diferenças
  menores que cerca de `1e-16` não são representáveis nessa escala.
- **O `erro` pode passar de `tol` quando a parada é `f(x) = 0`.** Em `cos(x) − x`, Newton-Raphson
  mostra `7,06e-10`, que é o tamanho do último passo. O método parou porque `f` zerou.

### Resultados obtidos

| Função | Raiz | Iterações Bisseção | Iterações Newton | Iterações Secante |
|---|---|---|---|---|
| `x³ − x − 2` | `1,521379706805` | 40 | 4 | 6 |
| `cos(x) − x` | `0,739085133215` | 40 | 4 | 6 |
| `e^(−x) − x` | `0,567143290410` | 40 | 4 | 5 |

| Função | Ordem Bisseção (teoria 1) | Ordem Newton (teoria 2) | Ordem Secante (teoria 1,618) |
|---|---|---|---|
| `x³ − x − 2` | 0,99 | 2,01 | 1,44 |
| `cos(x) − x` | 0,98 | 2,02 | 1,64 |
| `e^(−x) − x` | 0,99 | 2,00 | 1,61 |

O valor 1,44 usa poucas iterações e inclui o início da sequência, quando a Secante ainda está
longe do comportamento assintótico.

### Estabilidade

| Função | Bisseção | Newton-Raphson | Secante |
|---|---|---|---|
| `x³ − x − 2` | 100% | 100% | 100% |
| `cos(x) − x` | 100% | 85,5% | 100% |
| `e^(−x) − x` | 100% | 100% | 100% |

Os percentuais indicam quantas das 200 condições iniciais chegaram à raiz. Em `cos(x) − x`,
Newton-Raphson falhou em 29 condições, todas por atingir o limite de 100 iterações. A derivada
`−sen(x) − 1` se anula em infinitos pontos, e passar perto deles produz saltos grandes, o que
ajuda a explicar esse comportamento.

### Dependência da função e das condições iniciais

- `x³ − 2x + 2` com `x0 = 0`: Newton-Raphson entra no ciclo `0, 1, 0, 1, ...` e não converge. A
  Bisseção converge em 41 iterações e a Secante em 82.
- `(x − 1)²`: a Bisseção não se aplica, pois não há troca de sinal. Newton-Raphson leva 40
  iterações, porque a raiz dupla reduz a ordem para 1, e a Secante leva 57.

Por isso **nenhum método é universalmente melhor**: o desempenho depende da função e das
condições iniciais.

## 8. Por que as quantidades de iterações são diferentes

**Cada método usa uma quantidade diferente de informação sobre `f`.**

- **Bisseção:** usa só o sinal de `f`, então o erro máximo cai pela metade a cada iteração. Com
  `b − a = 1`, a fórmula dá `k ≥ log2(1e12) ≈ 39,86`, ou seja, 40 iterações. O número é igual nas
  três funções porque todos os intervalos têm largura 1. Ele depende do intervalo e da tolerância,
  não da forma de `f`.
- **Newton-Raphson:** usa valor e derivada, o que produz ordem 2. Em `x³ − x − 2`, o erro passa
  por `2e-02`, `4e-04`, `1e-07` e `8e-15`.
- **Secante:** usa valor e uma estimativa da inclinação, com ordem de cerca de 1,618. Fica entre os
  outros dois.

Outros fatores também influenciam a contagem:

- **Pontos iniciais:** em `x³ − x − 2`, a Secante começa com `x1 = 2`, a `0,479` da raiz, mais
  longe que o `x0 = 1,5` de Newton-Raphson.
- **Critério de parada:** é preciso um passo pequeno para confirmar a convergência, então a última
  iteração costuma apenas confirmar uma aproximação que já era boa.

**Menos iterações não significa menos custo.** Newton-Raphson calcula `f` e `f'` por iteração,
enquanto a Secante calcula só um novo valor de `f`. Se `f` e `f'` custarem o mesmo, o ganho de
Newton-Raphson por avaliação é `2^(1/2) ≈ 1,41`, menor que o `1,618` da Secante.

## 9. Verificação dos resultados

Cada resultado é confrontado com um fato matemático que não depende do método que o produziu. O
limite de concordância de 10% para as leis de erro foi fixado antes da execução. `python main.py`
termina com erro se qualquer verificação falhar.

| Verificação | Quantidade | Resultado |
|---|---|---|
| `f` troca de sinal a até `1e-11` de cada raiz obtida (Teorema do Valor Intermediário) | 9 | Todas aprovadas |
| Iterações da Bisseção iguais a `teto(log2((b − a) / tol))` | 3 | 40 medidas, 40 previstas |
| `|c_k − r| ≤ (b − a) / 2^k` em todas as iterações da Bisseção | 3 | Todas aprovadas |
| Erro de Newton-Raphson segue `C · e_k²` | 3 | Desvio máximo de 0,04% |
| Erro da Secante segue `C · e_k · e_(k−1)` | 3 | Desvio máximo de 0,10% |
| Duas execuções produzem resultados idênticos | 1 | Aprovada |

Avaliação das hipóteses:

- **H1 foi confirmada** nas três funções.
- **H2 foi confirmada** nas três funções, no último erro acima do nível de arredondamento.
- **H3 foi sustentada pelos cenários testados:** Newton-Raphson teve menos iterações nos
  experimentos-base, mas não convergiu em 29 condições iniciais de `cos(x) − x` e entrou em ciclo em
  `x³ − 2x + 2`. A Bisseção foi a mais lenta, mas não se aplica a `(x − 1)²`. Esses exemplos não
  constituem uma prova geral.

Os dados brutos ficam em `resultados/resultados.csv` (resultado final de cada método) e
`resultados/historico.csv` (cada iteração). Os números são gravados com todos os dígitos, para que
qualquer leitor possa recalcular as tabelas deste texto.

## 10. Limitações do experimento

- **Amostra pequena:** são três funções, todas suaves, com uma única raiz real e raiz simples. As
  conclusões não se generalizam automaticamente para outras classes de funções.
- **Condições escolhidas manualmente:** intervalos e valores iniciais influenciam diretamente as
  iterações. Outras escolhas mudariam a contagem da Secante e de Newton-Raphson.
- **Grade de estabilidade não equivalente entre métodos:** os intervalos da Bisseção contêm a raiz
  por construção, então seus 100% eram esperados e não medem robustez nas mesmas condições dos
  outros métodos. A grade também tem só 200 pontos, raio 10 e um único afastamento na Secante.
- **Custo não medido:** o experimento compara iterações. Não mede tempo de execução nem número de
  avaliações de função.
- **Precisão finita:** com `double`, erros perto de `1e-16` são dominados pelo arredondamento
  (GOLDBERG, 1991). Abaixo disso, erro real e resíduo não têm significado.
- **Raízes de referência:** têm precisão `double`, e os testes confirmam que `f` troca de sinal a
  `1e-14` de cada uma. Isso não mede erros menores que essa distância.
- **Erro aproximado:** o tamanho do passo estima o erro real, mas não o garante em Newton-Raphson
  nem na Secante.
- **Ordem estimada:** Newton-Raphson e Secante geram poucos pontos, então a regressão tem
  incerteza e pode incluir a fase inicial. Pontos com erro abaixo de `1e-13` são descartados.
- **Detecção de polo:** é um critério heurístico e não identifica toda descontinuidade.
- **Ambiente:** a execução foi feita em Windows 11 com Python 3.12. Outros ambientes não foram
  testados, embora os resultados devam variar pouco ou nada.

## 11. Considerações finais

Os experimentos confirmaram o comportamento previsto pela teoria: convergência linear da Bisseção,
quadrática de Newton-Raphson e superlinear da Secante. A concordância entre as leis de erro e as
medições, com desvio máximo de 0,10%, indica que a implementação reproduz os métodos estudados.

A comparação também mostra que a escolha do método depende do problema. Newton-Raphson é vantajoso
quando a derivada está disponível e o valor inicial é adequado. A Secante dispensa a derivada, e a
Bisseção oferece previsibilidade quando há um intervalo com troca de sinal em função contínua.
Nenhum deles é universalmente superior. Trabalhos futuros podem ampliar o conjunto de funções, medir
o custo por avaliação e estudar métodos híbridos, que combinam as garantias da Bisseção com a
velocidade dos métodos de ordem superior.

## Referências

ATKINSON, K. E. **An introduction to numerical analysis**. 2. ed. New York: John Wiley & Sons, 1989.

BURDEN, R. L.; FAIRES, J. D.; BURDEN, A. M. **Numerical analysis**. 10. ed. Boston: Cengage
Learning, 2016.

GOLDBERG, D. What every computer scientist should know about floating-point arithmetic. **ACM
Computing Surveys**, v. 23, n. 1, p. 5-48, 1991.

HUNTER, J. D. Matplotlib: a 2D graphics environment. **Computing in Science & Engineering**, v. 9,
n. 3, p. 90-95, 2007.

IEEE. **IEEE Std 754-2019**: IEEE standard for floating-point arithmetic. New York: IEEE, 2019.
