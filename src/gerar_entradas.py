#!/usr/bin/env python3
"""
Gerador de instâncias do Caixeiro Viajante com VIZINHANÇA LIMITADA.

Cada cidade é um ponto aleatório num mapa 1000 x 1000 (semente fixa).
Só existe estrada entre cidades vizinhas: não dá para ir de Recife a Natal
direto, é preciso passar por João Pessoa.

Tipos de mapa (mesmas cidades para o mesmo n, muda só quais estradas existem):
  anel      -> só o anel de estradas (cada cidade tem 2 vizinhas). Melhor caso da força bruta.
  vizinhos  -> anel + estradas para as K cidades mais próximas.        Caso médio (mapa realista).
  completo  -> estrada entre todo par de cidades (sem limitador).      Pior caso da força bruta.

O anel é formado ordenando as cidades pelo ângulo em volta do centro do mapa.
Ele garante que sempre existe pelo menos uma rota que passa por todas as cidades.

Formato do arquivo:
  n m
  u v w      (m linhas: estrada entre u e v com distância w, sem direção)
"""
import argparse
import math
import os
import random

SEMENTE_BASE = 20261124
K_VIZINHOS = 3


def gerar_cidades(n, semente=SEMENTE_BASE):
    rng = random.Random(semente * 1000 + n)
    return [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(n)]


def gerar_instancia(n, tipo, semente=SEMENTE_BASE, k=K_VIZINHOS):
    if n < 3:
        raise ValueError("n precisa ser pelo menos 3")
    pts = gerar_cidades(n, semente)

    def dist(i, j):
        return max(1, round(math.dist(pts[i], pts[j])))

    arestas = set()
    if tipo == "completo":
        for i in range(n):
            for j in range(i + 1, n):
                arestas.add((i, j))
    elif tipo in ("anel", "vizinhos"):
        cx = sum(p[0] for p in pts) / n
        cy = sum(p[1] for p in pts) / n
        ordem = sorted(range(n), key=lambda i: math.atan2(pts[i][1] - cy, pts[i][0] - cx))
        for a, b in zip(ordem, ordem[1:] + ordem[:1]):
            arestas.add((min(a, b), max(a, b)))
        if tipo == "vizinhos":
            for i in range(n):
                proximas = sorted((j for j in range(n) if j != i), key=lambda j: (dist(i, j), j))[:k]
                for j in proximas:
                    arestas.add((min(i, j), max(i, j)))
    else:
        raise ValueError(f"tipo desconhecido: {tipo}")

    return n, sorted((i, j, dist(i, j)) for i, j in arestas)


def escrever(caminho, n, arestas):
    with open(caminho, "w") as f:
        f.write(f"{n} {len(arestas)}\n")
        for u, v, w in arestas:
            f.write(f"{u} {v} {w}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tipos", default="anel,vizinhos,completo")
    ap.add_argument("--nmin", type=int, default=5)
    ap.add_argument("--nmax", type=int, default=30)
    ap.add_argument("--saida", default="entradas")
    ap.add_argument("--semente", type=int, default=SEMENTE_BASE)
    args = ap.parse_args()
    os.makedirs(args.saida, exist_ok=True)
    for tipo in args.tipos.split(","):
        for n in range(args.nmin, args.nmax + 1):
            n_, arestas = gerar_instancia(n, tipo, args.semente)
            escrever(os.path.join(args.saida, f"{tipo}_n{n:02d}.txt"), n_, arestas)
    print(f"Entradas geradas em {args.saida}/")


if __name__ == "__main__":
    main()
