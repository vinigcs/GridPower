# GridPower — Prévia da aplicação

## Objetivo
Protótipo acadêmico para demonstrar como grafos ponderados podem representar pontos de uma infraestrutura urbana e como Prim e Kruskal encontram uma Árvore Geradora Mínima (AGM).

## Estado desta entrega
Esta é uma **prévia funcional inicial**, com um grafo fixo de exemplo. Não representa ainda o sistema completo nem todas as funcionalidades planejadas no enunciado.

## Requisitos
- Python 3.10 ou superior
- Nenhuma biblioteca externa necessária

## Como executar
No terminal, dentro da pasta do projeto:

```bash
python main.py
```

## O que demonstra
- Representação de vértices e arestas com custo;
- Algoritmo de Prim;
- Algoritmo de Kruskal;
- Estrutura Union-Find com compressão de caminho e união por rank;
- Soma e comparação dos custos totais;
- Tratamento de grafo desconectado.

## Exemplo
O programa usa quatro vértices (A, B, C e D) e cinco arestas. Os custos do exemplo estão em milhares de reais. O custo mínimo esperado é 9 unidades, isto é, R$ 9.000,00.

## Próximas etapas
1. Separar o código em módulos;
2. Permitir cadastrar vértices e conexões pela interface;
3. Criar testes automatizados;
4. Documentar a complexidade e medir desempenho;
5. Revisar a integração com o restante do grupo.

## Nota
Antes da entrega, o grupo deve executar o programa no próprio ambiente, compreender o código e adequar o conteúdo às orientações do professor.
