import unittest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import montar_grafo_exemplo, prim, kruskal, custo_total, Grafo


class TestGridPower(unittest.TestCase):
    def test_prim_e_kruskal_tem_mesmo_custo(self):
        grafo = montar_grafo_exemplo()
        self.assertEqual(custo_total(prim(grafo)), custo_total(kruskal(grafo)))
        self.assertEqual(custo_total(prim(grafo)), 9)

    def test_grafo_desconectado(self):
        grafo = Grafo()
        grafo.adicionar_vertice("A")
        grafo.adicionar_vertice("B")
        with self.assertRaises(ValueError):
            prim(grafo)
        with self.assertRaises(ValueError):
            kruskal(grafo)


if __name__ == "__main__":
    unittest.main()
