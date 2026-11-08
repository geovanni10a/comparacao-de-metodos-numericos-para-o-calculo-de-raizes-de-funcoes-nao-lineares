# Como contribuir

Obrigado pelo interesse no projeto. Antes de participar, leia o
[código de conduta](CODE_OF_CONDUCT.md).

## Relatar um problema

Abra uma issue com os passos para reproduzir o problema, o resultado esperado, o resultado obtido e
as versões do Windows e do Python. Problemas de segurança seguem a [política de segurança](SECURITY.md).

## Propor uma mudança

Para mudanças grandes, abra uma issue antes, para discutir a ideia.

1. Faça um fork e crie um branch a partir de `main`.
2. Instale as dependências com `python -m pip install -e .`.
3. Faça a mudança e adicione testes para qualquer lógica nova.
4. Rode `python -m unittest discover -s tests` e `python -m raizes_numericas`. As 22 verificações precisam ser aprovadas.
5. Abra um pull request explicando o que mudou e por quê.

## Padrões do projeto

- Escreva código, comentários e mensagens de commit em português do Brasil.
- Mantenha os cálculos somente com a biblioteca padrão do Python.
- Use o Matplotlib apenas para figuras e interface.
- Se a mudança alterar resultados, atualize `resultados/`, `README.md` e `docs/EXPLICACAO.md`.
- Não adicione afirmações numéricas que não tenham sido obtidas pela execução do programa.
