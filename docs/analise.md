# Análise manual e refatoração

## Smells identificados no original

O arquivo original está em `test/userService.smelly.test.js`; a nova suíte fica em
`tests/userService.clean.test.js`, conforme o caminho pedido na atividade.

1. **Eager Test:** o primeiro teste cria e busca um usuário, intercalando ações e
   asserções. Uma falha na criação impede avaliar a busca e dificulta localizar a
   responsabilidade defeituosa. A nova suíte separa criação e consulta.
2. **Conditional Test Logic:** o teste de desativação percorre dois usuários e
   escolhe as asserções com `if/else`. O fluxo do teste pode esconder cenários.
   Foram criados casos independentes para usuário comum e administrador.
3. **Teste frágil:** o relatório é comparado com uma linha que exige pontuação,
   ordem dos campos e quebra de linha, além de um cabeçalho exato. Uma alteração
   visual pode quebrar o teste sem alterar a informação entregue. A nova suíte
   verifica os dados relevantes sem exigir esse layout.
4. **Asserção condicional / falso positivo:** o teste de menor de idade só verifica
   o erro dentro de `catch`. Se nenhuma exceção for lançada, passa sem verificar
   nada. `expect(acao).toThrow(...)` exige a rejeição efetiva.
5. **Teste desabilitado:** `test.skip` não verifica o cenário vazio. O serviço não
   oferece uma API de listagem: o novo teste verifica a mensagem do relatório vazio.

Não há evidência de Convidado Misterioso externo: o banco é uma estrutura em memória
do próprio módulo. O estado compartilhado requer limpeza a cada teste; `_clearDB()`
é usado apenas no setup, pois é o mecanismo fornecido pelo projeto para isolamento.

## Decisões

Cada caso usa Arrange, Act, Assert, separados por linhas em branco: dados locais e
setup, ação principal e asserções. A consulta posterior à desativação é observação
do estado público. Não há `if`, `for`, `try/catch` ou testes ignorados na suíte limpa.
IDs aleatórios são obtidos do retorno da API, sem fixar valor ou algoritmo.

O original é preservado, inclusive seu teste ignorado. Portanto, a suíte completa
pode passar mantendo um caso ignorado, e `npx eslint .` deve continuar denunciando
os problemas originais. A validação sem avisos se aplica ao novo arquivo.

## Ferramenta

A configuração solicitada utiliza o formato legado `.eslintrc.json`. O projeto fixa
ESLint 8.57.1 para que `npx eslint .` leia esse arquivo diretamente. Versões modernas
usam configuração flat por padrão. O arquivo de lock registra as dependências.

`jest/no-conditional-expect` detecta asserções nos ramos e no `catch`;
`jest/no-disabled-tests` denuncia o teste ignorado. `jest/no-identical-title` está
habilitada, mas não há títulos duplicados no original. Eager Test e fragilidade
da formatação exigem análise humana: ausência de alertas não prova ausência de smells.

Referências:
- https://github.com/jest-community/eslint-plugin-jest
- https://eslint.org/docs/latest/use/configure/migration-guide

## Conclusão

Testes focados tornam falhas mais fáceis de diagnosticar e mudanças mais seguras.
Asserções incondicionais evitam sucesso sem verificação; o isolamento reduz a
dependência entre cenários. A análise estática oferece feedback repetível, mas
complementa a revisão humana de intenção, cobertura e acoplamento dos testes.
