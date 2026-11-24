#!/usr/bin/env python3
"""
Caixeiro Viajante: HELD-KARP (programação dinâmica com bitmask).

dp[S][j] = menor custo para sair da cidade 0, visitar exatamente o conjunto S
           (cidades 1..n-1) e terminar na cidade j (j pertence a S).

  dp[{j}][j] = w(0, j)
  dp[S][j]   = min_{i em S - {j}} dp[S - {j}][i] + w(i, j)
  resposta   = min_j dp[todas][j] + w(j, 0)

Estrada que não existe tem custo infinito. O algoritmo sempre preenche a tabela
inteira, por isso o tempo é Theta(n^2 * 2^n) com ou sem limitador.

Uso: python3 held_karp.py ENTRADA [--reps R]
"""
import json
import os
import resource
import sys
import time

INF = 10 ** 15
SEM_ROTA = -1
BYTES_POR_ESTADO = 40          # estimativa para lista de inteiros em CPython


def ler(caminho):
    with open(caminho) as f:
        n, m = map(int, f.readline().split())
        W = [[INF] * n for _ in range(n)]
        for _ in range(m):
            u, v, w = map(int, f.readline().split())
            W[u][v] = W[v][u] = w
    return n, m, W


def held_karp(n, W):
    N = n - 1                              # bit b representa a cidade b+1
    total = 1 << N
    dp = [INF] * (total * N)               # dp[S * N + j]
    # w_[i][j] = peso entre as cidades i+1 e j+1 (já deslocado para os bits)
    w_ = [[W[i + 1][j + 1] for j in range(N)] for i in range(N)]

    for S in range(1, total):
        base = S * N
        resto = S
        while resto:
            bit = resto & -resto
            j = bit.bit_length() - 1
            resto ^= bit
            anterior = S ^ bit
            if anterior == 0:
                dp[base + j] = W[0][j + 1]
                continue
            pb = anterior * N
            melhor = INF
            r2 = anterior
            while r2:
                b2 = r2 & -r2
                i = b2.bit_length() - 1
                r2 ^= b2
                c = dp[pb + i] + w_[i][j]
                if c < melhor:
                    melhor = c
            dp[base + j] = melhor if melhor < INF else INF

    final = (total - 1) * N
    resposta = min(dp[final + j] + W[j + 1][0] for j in range(N))
    return resposta if resposta < INF else SEM_ROTA


def main():
    arquivo = sys.argv[1]
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 1
    n, m, W = ler(arquivo)

    necessario = (1 << (n - 1)) * (n - 1) * BYTES_POR_ESTADO
    ram = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    if necessario > 0.7 * ram:
        print(json.dumps({"algoritmo": "held_karp", "linguagem": "python", "n": n,
                          "erro": "memoria", "bytes_necessarios": necessario}))
        sys.exit(3)

    tempos = []
    for _ in range(reps):
        t0 = time.perf_counter()
        custo = held_karp(n, W)
        tempos.append(time.perf_counter() - t0)

    print(json.dumps({
        "algoritmo": "held_karp", "linguagem": "python", "n": n, "m": m,
        "custo": custo, "tempos_s": tempos,
        "mem_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }))


if __name__ == "__main__":
    main()
