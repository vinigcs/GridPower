
"""GridPower - protótipo inicial para demonstrar a Árvore Geradora Mínima.

Execução: python main.py
Este protótipo usa um grafo de exemplo fixo e implementa Prim e Kruskal.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Aresta:
    origem: str
    destino: str
    peso: float


class Grafo:
    def __init__(self):
        self.vertices = set()
        self.arestas = []

    def adicionar_vertice(self, nome):
        nome = str(nome).strip()
        if not nome:
            raise ValueError("O nome do vértice não pode ser vazio.")
        self.vertices.add(nome)

    def adicionar_aresta(self, origem, destino, peso):
        if origem == destino:
            raise ValueError("Não é permitido conectar um vértice a ele mesmo.")
        if origem not in self.vertices or destino not in self.vertices:
            raise ValueError("Os dois vértices precisam estar cadastrados.")
        if isinstance(peso, bool) or not isinstance(peso, (int, float)) or peso < 0:
            raise ValueError("O custo deve ser um número não negativo.")
        self.arestas.append(Aresta(origem, destino, float(peso)))


def custo_total(arestas):
    return sum(aresta.peso for aresta in arestas)


def comparar_resultados(grafo, resultado_prim, resultado_kruskal):
    """Compara os resultados dos algoritmos de Prim e Kruskal."""

    if not grafo.vertices:
        raise ValueError("Não é possível comparar um grafo vazio.")

    quantidade_esperada = len(grafo.vertices) - 1

    if len(resultado_prim) != quantidade_esperada:
        raise ValueError(
            "O resultado de Prim não forma uma árvore geradora."
        )

    if len(resultado_kruskal) != quantidade_esperada:
        raise ValueError(
            "O resultado de Kruskal não forma uma árvore geradora."
        )

    custo_prim = custo_total(resultado_prim)
    custo_kruskal = custo_total(resultado_kruskal)

    return {
        "custo_prim": custo_prim,
        "custo_kruskal": custo_kruskal,
        "custos_iguais": abs(custo_prim - custo_kruskal) < 1e-9,
        "arestas_prim": len(resultado_prim),
        "arestas_kruskal": len(resultado_kruskal)
    }


def prim(grafo):
    """Retorna uma árvore geradora mínima usando Prim."""

    if not grafo.vertices:
        return []

    inicio = sorted(grafo.vertices)[0]
    visitados = {inicio}
    selecionadas = []

    while len(visitados) < len(grafo.vertices):
        candidatas = [
            a for a in grafo.arestas
            if (a.origem in visitados and a.destino not in visitados)
            or (a.destino in visitados and a.origem not in visitados)
        ]

        if not candidatas:
            raise ValueError(
                "O grafo é desconectado; não existe árvore geradora."
            )

        escolhida = min(
            candidatas,
            key=lambda a: (a.peso, a.origem, a.destino)
        )

        selecionadas.append(escolhida)
        visitados.add(escolhida.origem)
        visitados.add(escolhida.destino)

    return selecionadas


class UnionFind:
    def __init__(self, elementos):
        self.pai = {x: x for x in elementos}
        self.rank = {x: 0 for x in elementos}

    def find(self, x):
        if self.pai[x] != x:
            self.pai[x] = self.find(self.pai[x])
        return self.pai[x]

    def union(self, a, b):
        raiz_a = self.find(a)
        raiz_b = self.find(b)

        if raiz_a == raiz_b:
            return False

        if self.rank[raiz_a] < self.rank[raiz_b]:
            self.pai[raiz_a] = raiz_b
        elif self.rank[raiz_a] > self.rank[raiz_b]:
            self.pai[raiz_b] = raiz_a
        else:
            self.pai[raiz_b] = raiz_a
            self.rank[raiz_a] += 1

        return True


def kruskal(grafo):
    """Retorna uma árvore geradora mínima usando Kruskal."""

    if not grafo.vertices:
        return []

    uf = UnionFind(grafo.vertices)
    selecionadas = []

    for aresta in sorted(
        grafo.arestas,
        key=lambda a: (a.peso, a.origem, a.destino)
    ):
        if uf.union(aresta.origem, aresta.destino):
            selecionadas.append(aresta)

            if len(selecionadas) == len(grafo.vertices) - 1:
                break

    if len(selecionadas) != len(grafo.vertices) - 1:
        raise ValueError(
            "O grafo é desconectado; não existe árvore geradora."
        )

    return selecionadas


def montar_grafo_exemplo():
    grafo = Grafo()

    for vertice in ["A", "B", "C", "D"]:
        grafo.adicionar_vertice(vertice)

    # Custos ilustrativos em milhares de reais.
    grafo.adicionar_aresta("A", "B", 4)
    grafo.adicionar_aresta("A", "C", 2)
    grafo.adicionar_aresta("B", "C", 5)
    grafo.adicionar_aresta("B", "D", 3)
    grafo.adicionar_aresta("C", "D", 6)

    return grafo


def exibir_resultado(nome, arestas):
    print(f"\nResultado de {nome}:")

    for a in arestas:
        print(
            f"  {a.origem} -- {a.destino}: "
            f"R$ {a.peso * 1000:,.2f}"
        )

    print(f"Custo total: R$ {custo_total(arestas) * 1000:,.2f}")


def main():
    grafo = montar_grafo_exemplo()

    print("GRIDPOWER — protótipo de Árvore Geradora Mínima")
    print("Rede demonstrativa com quatro pontos e cinco conexões.")

    resultado_prim = prim(grafo)
    resultado_kruskal = kruskal(grafo)

    exibir_resultado("Prim", resultado_prim)
    exibir_resultado("Kruskal", resultado_kruskal)

    comparacao = comparar_resultados(
        grafo,
        resultado_prim,
        resultado_kruskal
    )

    print("\nComparação dos resultados:")
    print(
        f"Custo do Prim: "
        f"R$ {comparacao['custo_prim'] * 1000:,.2f}"
    )
    print(
        f"Custo do Kruskal: "
        f"R$ {comparacao['custo_kruskal'] * 1000:,.2f}"
    )
    print(f"Arestas do Prim: {comparacao['arestas_prim']}")
    print(f"Arestas do Kruskal: {comparacao['arestas_kruskal']}")

    if comparacao["custos_iguais"]:
        print("Os algoritmos encontraram o mesmo custo mínimo.")
    else:
        print("Atenção: os custos são diferentes.")

    print("\nObservação: este é um protótipo inicial com dados de exemplo.")


if __name__ == "__main__":
    main()
