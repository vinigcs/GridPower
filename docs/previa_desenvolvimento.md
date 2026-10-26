# Prévia de desenvolvimento — GridPower

## 1. Apresentação
O GridPower é uma proposta acadêmica para apoiar a otimização de conexões em uma infraestrutura urbana. O problema é modelado por um grafo não direcionado e ponderado, no qual os vértices representam pontos da rede e as arestas representam conexões possíveis com seus respectivos custos.

## 2. Problema e objetivo
O objetivo matemático é encontrar uma Árvore Geradora Mínima (AGM): um conjunto de conexões que conecta todos os vértices de um grafo conectado, sem ciclos e com custo total mínimo.

## 3. Abordagem proposta
A prévia apresenta dois algoritmos clássicos:
- **Prim:** começa em um vértice e acrescenta, a cada etapa, a aresta de menor custo que conecta a parte já visitada a um vértice ainda não visitado.
- **Kruskal:** ordena as arestas por custo e seleciona as menores que não formam ciclos. A estrutura Union-Find auxilia na identificação de componentes e na prevenção de ciclos.

## 4. Protótipo inicial
O protótipo acompanha este documento em `main.py`. Ele usa uma rede ilustrativa de quatro vértices e cinco arestas, executa Prim e Kruskal e exibe as conexões escolhidas e o custo total. Os custos do exemplo são apresentados em milhares de reais; a solução mínima esperada é R$ 9.000,00.

Este protótipo é uma demonstração inicial com dados fixos. Não deve ser confundido com a versão completa do sistema.

## 5. Validação inicial
Uma verificação importante é comparar os custos totais obtidos pelos dois algoritmos no mesmo grafo. Para um grafo conectado e uma implementação correta, Prim e Kruskal devem encontrar o mesmo custo mínimo, embora possam escolher arestas diferentes quando existem várias árvores geradoras mínimas.

O programa também identifica o caso em que o grafo é desconectado e, portanto, não existe uma árvore que conecte todos os vértices.

## 6. Próximas etapas
- Organizar o projeto em módulos;
- Adicionar entrada de dados pelo usuário;
- Criar testes automatizados para casos comuns e casos extremos;
- Medir tempo de execução em grafos de diferentes tamanhos;
- Documentar a complexidade dos algoritmos;
- Integrar e revisar o trabalho de todos os integrantes.

## 7. Limitações desta prévia
A aplicação usa dados fixos, não possui interface gráfica, persistência de dados nem relatório automatizado. Essas funcionalidades não são apresentadas como concluídas.
