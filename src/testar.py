#!/usr/bin/env python3
"""
Testes de corretude: as 4 implementações precisam dar o MESMO custo ótimo
nas mesmas entradas. Também compara com um oráculo independente
(itertools.permutations) nos n pequenos e testa um mapa SEM rota possível.

Uso: python3 src/testar.py
"""
import itertools
import os
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from gerar_entradas import escrever, gerar_instancia  # noqa: E402
from medir import IMPLEMENTACOES, compilar, rodar      # noqa: E402


def oraculo(n, arestas):
    W = {}
    for u, v, w in arestas:
        W[(u, v)] = W[(v, u)] = w
    melhor = -1
    for perm in itertools.permutations(range(1, n)):
        rota = (0,) + perm + (0,)
        if all((a, b) in W for a, b in zip(rota, rota[1:])):
            c = sum(W[(a, b)] for a, b in zip(rota, rota[1:]))
            if melhor < 0 or c < melhor:
                melhor = c
    return melhor


def main():
    compilar()
    casos = [(n, tipo, gerar_instancia(n, tipo)[1]) for tipo in ("anel", "vizinhos", "completo")
             for n in range(4, 11)]
    # mapa em linha reta (0-1-2-3-4-5): não existe rota que volte sem repetir cidade
    casos.append((6, "sem_rota", [(i, i + 1, 10) for i in range(5)]))
    # estrela: tudo passa pela cidade 0
    casos.append((5, "sem_rota", [(0, i, 7) for i in range(1, 5)]))

    falhas = 0
    with tempfile.TemporaryDirectory() as tmp:
        for n, tipo, arestas in casos:
            arq = os.path.join(tmp, f"{tipo}_{n}.txt")
            escrever(arq, n, arestas)
            custos = {f"{a}/{l}": rodar(cmd, arq, 1, 120)[0]["custo"] for (a, l), cmd in IMPLEMENTACOES.items()}
            if n <= 9:
                custos["oraculo"] = oraculo(n, arestas)
            ok = len(set(custos.values())) == 1
            falhas += not ok
            print(f"{'OK  ' if ok else 'FALHA'} {tipo:9s} n={n:2d}  {custos}")
    print(f"\n{len(casos) - falhas}/{len(casos)} testes passaram.")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
