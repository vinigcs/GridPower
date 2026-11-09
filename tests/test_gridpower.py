
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import (
    montar_grafo_exemplo,
    prim,
    kruskal,
    custo_total,
    comparar_resultados,
    Grafo,
    Aresta
)


class TestGridPower(unittest.TestCase):

    def test_prim_e_kruskal_tem_mesmo_custo(self):
        grafo = montar_grafo_exemplo()

        resultado_prim = prim(grafo)
        resultado_kruskal = kruskal(grafo)

        self.assertEqual(
            custo_total(resultado_prim),
            custo_total(resultado_kruskal)
        )
        self.assertEqual(custo_total(resultado_prim), 9)

    def test_grafo_desconectado(self):
        grafo = Grafo()
        grafo.adicionar_vertice("A")
        grafo.adicionar_vertice("B")

        with self.assertRaises(ValueError):
            prim(grafo)

        with self.assertRaises(ValueError):
            kruskal(grafo)

    def test_comparacao_dos_resultados(self):
        grafo = montar_grafo_exemplo()

        resultado_prim = prim(grafo)
        resultado_kruskal = kruskal(grafo)

        comparacao = comparar_resultados(
            grafo,
            resultado_prim,
            resultado_kruskal
        )

        self.assertTrue(comparacao["custos_iguais"])
        self.assertEqual(comparacao["custo_prim"], 9)
        self.assertEqual(comparacao["custo_kruskal"], 9)
        self.assertEqual(comparacao["arestas_prim"], 3)
        self.assertEqual(comparacao["arestas_kruskal"], 3)

    def test_arvores_diferentes_com_mesmo_custo(self):
        grafo = Grafo()

        for vertice in ["A", "B", "C"]:
            grafo.adicionar_vertice(vertice)

        resultado_prim = [
            Aresta("A", "B", 1),
            Aresta("A", "C", 1)
        ]

        resultado_kruskal = [
            Aresta("A", "B", 1),
            Aresta("B", "C", 1)
        ]

        comparacao = comparar_resultados(
            grafo,
            resultado_prim,
            resultado_kruskal
        )

        self.assertTrue(comparacao["custos_iguais"])
        self.assertEqual(comparacao["custo_prim"], 2)
        self.assertEqual(comparacao["custo_kruskal"], 2)

    def test_resultado_com_quantidade_incorreta_de_arestas(self):
        grafo = montar_grafo_exemplo()

        resultado_incompleto = [
            Aresta("A", "C", 2)
        ]

        resultado_kruskal = kruskal(grafo)

        with self.assertRaises(ValueError):
            comparar_resultados(
                grafo,
                resultado_incompleto,
                resultado_kruskal
            )


if __name__ == "__main__":
    unittest.main()
