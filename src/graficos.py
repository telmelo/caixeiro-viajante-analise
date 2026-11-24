#!/usr/bin/env python3
"""
Gera os gráficos e as tabelas a partir de resultados/resultados.csv e resultados/limites.csv.
Saída em graficos/.

  1_tempo_<mapa>.png             tempo x n, os 4 (algoritmo x linguagem), escala log
  2_teorico_x_medido.png         razões T(n)/f(n), que devem tender a uma constante
  3_algoritmo_x_algoritmo.png    quantas vezes a força bruta é mais lenta (ou mais rápida) que o Held-Karp
  4_linguagem_x_linguagem.png    quantas vezes Python é mais lento que C++
  5_melhor_medio_pior.png        efeito do mapa (anel / vizinhos / completo) em cada algoritmo
  6_memoria_held_karp.png        memória medida x Theta(n * 2^n)   (bônus)
  tabela_resultados.md, tabela_limites.md

Uso: python3 src/graficos.py
"""
import csv
import math
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")
OUT = os.path.join(RAIZ, "graficos")

NOME_ALG = {"forca_bruta": "Força bruta", "held_karp": "Held-Karp"}
NOME_LING = {"cpp": "C++", "python": "Python"}
NOME_MAPA = {"anel": "anel (melhor caso)", "vizinhos": "vizinhos (caso médio)", "completo": "completo (pior caso)"}
COR = {("forca_bruta", "cpp"): "#1f77b4", ("forca_bruta", "python"): "#9ecae1",
       ("held_karp", "cpp"): "#d62728", ("held_karp", "python"): "#fc9272"}
COR_MAPA = {"anel": "#2ca02c", "vizinhos": "#ff7f0e", "completo": "#7f3c8d"}
MARCA = {"cpp": "o", "python": "s"}


def carregar():
    dados = defaultdict(list)                  # (mapa, alg, ling) -> lista de linhas
    with open(os.path.join(RES, "resultados.csv")) as f:
        for r in csv.DictReader(f):
            r["n"] = int(r["n"])
            r["media_s"] = float(r["media_s"])
            r["desvio_s"] = float(r["desvio_s"])
            r["mem_kb"] = int(r["mem_kb"])
            r["nos"] = int(r["nos"]) if r["nos"] else None
            dados[(r["mapa"], r["algoritmo"], r["linguagem"])].append(r)
    for v in dados.values():
        v.sort(key=lambda r: r["n"])
    return dados


def serie(dados, mapa, alg, ling, minimo=1e-6):
    """Ignora tempos abaixo de 1 microssegundo: são ruído do relógio."""
    pts = [r for r in dados.get((mapa, alg, ling), []) if r["media_s"] >= minimo]
    return [r["n"] for r in pts], [r["media_s"] for r in pts], [r["desvio_s"] for r in pts], pts


def barras(t, d):
    """Barra de erro inferior cortada em 90% do valor, para não sumir do eixo log."""
    return [[min(di, 0.9 * ti) for ti, di in zip(t, d)], d]


def salvar(fig, nome):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, nome), dpi=150)
    plt.close(fig)


def g1_tempo(dados, mapas):
    for mapa in mapas:
        fig, ax = plt.subplots(figsize=(8, 5))
        for (alg, ling), cor in COR.items():
            n, t, d, _ = serie(dados, mapa, alg, ling)
            if n:
                ax.errorbar(n, t, yerr=barras(t, d), color=cor, marker=MARCA[ling], ms=4, capsize=3,
                            label=f"{NOME_ALG[alg]} ({NOME_LING[ling]})")
        ax.axhline(60, color="gray", ls=":", lw=1)
        ax.text(ax.get_xlim()[0], 60, " limite oficial de 60 s", va="bottom", color="gray", fontsize=8)
        ax.set_yscale("log")
        ax.set_xlabel("n (número de cidades)")
        ax.set_ylabel("tempo médio (s), escala log")
        ax.set_title(f"Tempo de execução: mapa {NOME_MAPA.get(mapa, mapa)}")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        salvar(fig, f"1_tempo_{mapa}.png")


def g2_teorico(dados):
    fig, axs = plt.subplots(2, 2, figsize=(12, 9))

    ax = axs[0][0]
    for ling in ("cpp", "python"):
        for mapa in ("vizinhos", "completo"):
            n, t, _, _ = serie(dados, mapa, "held_karp", ling, minimo=1e-4)
            if n:
                ax.plot(n, [ti / (ni ** 2 * 2 ** ni) for ni, ti in zip(n, t)], marker=MARCA[ling],
                        color=COR[("held_karp", ling)], ls="-" if mapa == "vizinhos" else "--",
                        label=f"{NOME_LING[ling]}, mapa {mapa}")
    ax.set_yscale("log")
    ax.set_title("Held-Karp: T(n) / (n²·2ⁿ)  → deve ficar constante")
    ax.set_xlabel("n")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)

    ax = axs[0][1]
    for ling in ("cpp", "python"):
        n, t, _, _ = serie(dados, "completo", "forca_bruta", ling, minimo=1e-4)
        if n:
            ax.plot(n, [ti / math.factorial(ni - 1) for ni, ti in zip(n, t)], marker=MARCA[ling],
                    color=COR[("forca_bruta", ling)], label=NOME_LING[ling])
    ax.set_yscale("log")
    ax.set_title("Força bruta, mapa completo: T(n) / (n−1)!  → deve ficar constante")
    ax.set_xlabel("n")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)

    ax = axs[1][0]
    for ling in ("cpp", "python"):
        for mapa in ("vizinhos", "completo"):
            n, t, _, pts = serie(dados, mapa, "forca_bruta", ling, minimo=1e-4)
            if n:
                ax.plot(n, [r["media_s"] / r["nos"] for r in pts], marker=MARCA[ling],
                        color=COR[("forca_bruta", ling)], ls="-" if mapa == "vizinhos" else "--",
                        label=f"{NOME_LING[ling]}, mapa {mapa}")
    ax.set_yscale("log")
    ax.set_title("Força bruta: tempo por nó visitado  → constante\n(o tempo é proporcional ao tamanho da árvore de busca)")
    ax.set_xlabel("n")
    ax.set_ylabel("segundos por nó")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)

    ax = axs[1][1]
    for mapa in ("anel", "vizinhos", "completo"):
        pts = dados.get((mapa, "forca_bruta", "cpp"), [])
        if pts:
            ax.plot([r["n"] for r in pts], [r["nos"] for r in pts], marker="o", color=COR_MAPA[mapa],
                    label=f"nós visitados, mapa {mapa}")
    todos_n = sorted({r["n"] for v in dados.values() for r in v})
    if todos_n:
        ref = [ni for ni in todos_n if ni <= 20]
        ax.plot(ref, [math.factorial(ni - 1) for ni in ref], "k--", lw=1, label="(n−1)! (sem limitador)")
        ax.plot(todos_n, [ni ** 2 * 2 ** ni for ni in todos_n], "k:", lw=1, label="n²·2ⁿ (Held-Karp)")
    ax.set_yscale("log")
    ax.set_title("Efeito do limitador de vizinhança na força bruta")
    ax.set_xlabel("n")
    ax.set_ylabel("operações (escala log)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    salvar(fig, "2_teorico_x_medido.png")


def razao(dados, mapa, a1, l1, a2, l2):
    p1 = {r["n"]: r["media_s"] for r in dados.get((mapa, a1, l1), []) if r["media_s"] >= 1e-6}
    p2 = {r["n"]: r["media_s"] for r in dados.get((mapa, a2, l2), []) if r["media_s"] >= 1e-6}
    ns = sorted(set(p1) & set(p2))
    return ns, [p1[n] / p2[n] for n in ns]


def g3_algoritmos(dados, mapas):
    fig, ax = plt.subplots(figsize=(8, 5))
    for mapa in mapas:
        for ling in ("cpp", "python"):
            n, r = razao(dados, mapa, "forca_bruta", ling, "held_karp", ling)
            if n:
                ax.plot(n, r, marker=MARCA[ling], color=COR_MAPA[mapa], ls="-" if ling == "cpp" else "--",
                        label=f"mapa {mapa}, {NOME_LING[ling]}")
    ax.axhline(1, color="black", lw=1)
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("tempo força bruta / tempo Held-Karp")
    ax.set_title("Algoritmo × algoritmo (mesmas entradas, mesma linguagem)\n"
                 "acima de 1: Held-Karp mais rápido · abaixo de 1: força bruta mais rápida", fontsize=10)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    salvar(fig, "3_algoritmo_x_algoritmo.png")


def g4_linguagens(dados):
    fig, ax = plt.subplots(figsize=(8, 5))
    for alg, mapa in (("forca_bruta", "vizinhos"), ("forca_bruta", "completo"), ("held_karp", "vizinhos")):
        n, r = razao(dados, mapa, alg, "python", alg, "cpp")
        n2 = [ni for ni, ti in zip(n, r)]
        if n:
            ax.plot(n2, r, marker="o", color=COR[(alg, "cpp")], ls="-" if mapa == "vizinhos" else "--",
                    label=f"{NOME_ALG[alg]}, mapa {mapa}")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("tempo Python / tempo C++")
    ax.set_title("Linguagem × linguagem: quantas vezes Python é mais lento")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    salvar(fig, "4_linguagem_x_linguagem.png")


def g5_casos(dados, mapas):
    fig, axs = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, alg in zip(axs, ("forca_bruta", "held_karp")):
        for mapa in mapas:
            n, t, d, _ = serie(dados, mapa, alg, "cpp")
            if n:
                ax.errorbar(n, t, yerr=barras(t, d), marker="o", ms=4, capsize=3, color=COR_MAPA[mapa],
                            label=NOME_MAPA.get(mapa, mapa))
        ax.set_yscale("log")
        ax.set_xlabel("n")
        ax.set_title(f"{NOME_ALG[alg]} (C++): efeito do mapa")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    axs[0].set_ylabel("tempo médio (s), escala log")
    salvar(fig, "5_melhor_medio_pior.png")


def g6_memoria(dados):
    fig, ax = plt.subplots(figsize=(8, 5))
    for ling in ("cpp", "python"):
        pts = dados.get(("vizinhos", "held_karp", ling), [])
        if not pts:
            continue
        base = min(r["mem_kb"] for r in pts)
        pts = [r for r in pts if (r["mem_kb"] - base) / 1024 >= 1]   # abaixo de 1 MB é ruído do processo
        n = [r["n"] for r in pts]
        mb = [(r["mem_kb"] - base) / 1024 for r in pts]
        ax.plot(n, mb, marker=MARCA[ling], color=COR[("held_karp", ling)],
                label=f"medido, {NOME_LING[ling]} (pico − base)")
    todos = sorted({r["n"] for r in dados.get(("vizinhos", "held_karp", "cpp"), [])})
    if todos:
        teo = [(2 ** (ni - 1)) * (ni - 1) * 4 / 2 ** 20 for ni in todos]
        ax.plot(todos, teo, "k--", label="teórico C++: 2ⁿ⁻¹·(n−1)·4 bytes")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("memória (MB), escala log")
    ax.set_title("Held-Karp: memória medida × Θ(n·2ⁿ)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    salvar(fig, "6_memoria_held_karp.png")


def tabelas(dados):
    with open(os.path.join(OUT, "tabela_resultados.md"), "w") as f:
        f.write("| Mapa | n | Algoritmo | Linguagem | Tempo médio (s) | Desvio (s) | Reps | Custo ótimo |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for (mapa, alg, ling), pts in sorted(dados.items()):
            for r in pts:
                f.write(f"| {mapa} | {r['n']} | {NOME_ALG[alg]} | {NOME_LING[ling]} | {r['media_s']:.6g} | "
                        f"{r['desvio_s']:.3g} | {r['reps']} | {r['custo']} |\n")
    caminho = os.path.join(RES, "limites.csv")
    if os.path.exists(caminho):
        with open(caminho) as f, open(os.path.join(OUT, "tabela_limites.md"), "w") as g:
            g.write("| Mapa | Algoritmo | Linguagem | Maior n viável | Por que parou |\n|---|---|---|---|---|\n")
            for r in csv.DictReader(f):
                g.write(f"| {r['mapa']} | {NOME_ALG[r['algoritmo']]} | {NOME_LING[r['linguagem']]} | "
                        f"{r['maior_n_viavel']} | {r['motivo_da_parada']} |\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    dados = carregar()
    mapas = [m for m in ("anel", "vizinhos", "completo") if any(k[0] == m for k in dados)]
    g1_tempo(dados, mapas)
    g2_teorico(dados)
    g3_algoritmos(dados, mapas)
    g4_linguagens(dados)
    g5_casos(dados, mapas)
    g6_memoria(dados)
    tabelas(dados)
    print(f"Gráficos e tabelas em {OUT}/")


if __name__ == "__main__":
    main()
