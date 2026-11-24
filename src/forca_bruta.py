#!/usr/bin/env python3
"""
Caixeiro Viajante: FORÇA BRUTA com limitador de vizinhança.

Parte da cidade 0 e testa todas as rotas possíveis, mas só anda por estradas
que existem (só vai para cidades vizinhas da atual). Não há poda por custo:
toda rota válida é percorrida até o fim. Isso continua sendo força bruta.

Uso: python3 forca_bruta.py ENTRADA [--reps R]
Saída: uma linha JSON com custo, rota, tempos (só do algoritmo), nós visitados e memória.
"""
import json
import resource
import sys
import time

sys.setrecursionlimit(10000)
SEM_ROTA = -1


def ler(caminho):
    with open(caminho) as f:
        n, m = map(int, f.readline().split())
        adj = [[] for _ in range(n)]
        for _ in range(m):
            u, v, w = map(int, f.readline().split())
            adj[u].append((v, w))
            adj[v].append((u, w))
    for lista in adj:
        lista.sort()
    return n, m, adj


def forca_bruta(n, adj):
    volta = [None] * n                     # volta[u] = distância de u até a cidade 0
    for v, w in adj[0]:
        volta[v] = w

    visitada = [False] * n
    visitada[0] = True
    caminho = [0]
    melhor_custo = SEM_ROTA
    melhor_rota = None
    nos = 0

    def dfs(u, custo, tamanho):
        nonlocal melhor_custo, melhor_rota, nos
        nos += 1
        if tamanho == n:                   # visitou todas: tenta fechar o ciclo
            if volta[u] is not None:
                total = custo + volta[u]
                if melhor_custo == SEM_ROTA or total < melhor_custo:
                    melhor_custo = total
                    melhor_rota = caminho + [0]
            return
        for v, w in adj[u]:                # LIMITADOR: só cidades vizinhas
            if not visitada[v]:
                visitada[v] = True
                caminho.append(v)
                dfs(v, custo + w, tamanho + 1)
                caminho.pop()
                visitada[v] = False

    dfs(0, 0, 1)
    return melhor_custo, melhor_rota, nos


def main():
    arquivo = sys.argv[1]
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 1
    n, m, adj = ler(arquivo)               # leitura fica FORA da medição

    tempos = []
    for _ in range(reps):
        t0 = time.perf_counter()
        custo, rota, nos = forca_bruta(n, adj)
        tempos.append(time.perf_counter() - t0)

    print(json.dumps({
        "algoritmo": "forca_bruta", "linguagem": "python", "n": n, "m": m,
        "custo": custo, "rota": rota, "nos": nos, "tempos_s": tempos,
        "mem_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }))


if __name__ == "__main__":
    main()
