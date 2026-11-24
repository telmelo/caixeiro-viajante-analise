#!/usr/bin/env python3
"""
Script de medição. Roda as 4 implementações sobre AS MESMAS entradas e salva:
  resultados/resultados.csv   -> média e desvio-padrão do tempo por (mapa, n, algoritmo, linguagem)
  resultados/limites.csv      -> maior n viável em até LIMITE segundos e o motivo da parada

Para cada combinação, em cada n:
  1. roda uma vez (sondagem / aquecimento) com limite de tempo;
  2. se passou do limite ou faltou memória, aquela combinação para ali;
  3. senão, roda REPS vezes e guarda média e desvio.
Só o algoritmo é cronometrado (leitura do arquivo fica fora, dentro de cada programa).

Uso:
  python3 src/medir.py                      # experimento completo (pode levar horas: deixe de noite)
  python3 src/medir.py --rapido             # prévia: 3 repetições, limite de 10 s
"""
import argparse
import csv
import json
import os
import statistics
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from gerar_entradas import escrever, gerar_instancia  # noqa: E402

IMPLEMENTACOES = {
    ("forca_bruta", "cpp"): [os.path.join(RAIZ, "bin", "forca_bruta")],
    ("held_karp", "cpp"): [os.path.join(RAIZ, "bin", "held_karp")],
    ("forca_bruta", "python"): [sys.executable, os.path.join(AQUI, "forca_bruta.py")],
    ("held_karp", "python"): [sys.executable, os.path.join(AQUI, "held_karp.py")],
}


def compilar():
    subprocess.run(["make", "-s", "-C", RAIZ], check=True)


def rodar(cmd, entrada, reps, timeout):
    try:
        p = subprocess.run(cmd + [entrada, "--reps", str(reps)], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "tempo"
    if p.returncode == 3:
        return None, "memoria"
    if p.returncode != 0:
        if p.returncode < 0 or "MemoryError" in p.stderr:
            return None, "memoria"
        raise RuntimeError(f"falhou: {' '.join(cmd)} {entrada}\n{p.stderr}")
    return json.loads(p.stdout), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipos", default="anel,vizinhos,completo")
    ap.add_argument("--nmin", type=int, default=5)
    ap.add_argument("--nmax", type=int, default=40)
    ap.add_argument("--reps", type=int, default=15)
    ap.add_argument("--limite", type=float, default=60.0, help="segundos por execução")
    ap.add_argument("--rapido", action="store_true", help="prévia: 3 repetições, limite 10 s")
    args = ap.parse_args()
    if args.rapido:
        args.reps, args.limite = 3, 10.0

    compilar()
    pasta_ent = os.path.join(RAIZ, "entradas")
    pasta_res = os.path.join(RAIZ, "resultados")
    os.makedirs(pasta_ent, exist_ok=True)
    os.makedirs(pasta_res, exist_ok=True)

    linhas, limites = [], []
    inicio = time.time()
    for tipo in args.tipos.split(","):
        vivos = {chave: True for chave in IMPLEMENTACOES}
        ultimo_ok = {chave: None for chave in IMPLEMENTACOES}
        for n in range(args.nmin, args.nmax + 1):
            if not any(vivos.values()):
                break
            entrada = os.path.join(pasta_ent, f"{tipo}_n{n:02d}.txt")
            n_, arestas = gerar_instancia(n, tipo)
            escrever(entrada, n_, arestas)
            custos = {}
            for chave, cmd in IMPLEMENTACOES.items():
                if not vivos[chave]:
                    continue
                algoritmo, linguagem = chave
                sonda, motivo = rodar(cmd, entrada, 1, args.limite)
                if sonda is None:
                    vivos[chave] = False
                    limites.append([tipo, algoritmo, linguagem, ultimo_ok[chave], motivo])
                    print(f"  [{tipo}] {algoritmo}/{linguagem} parou em n={n} ({motivo})")
                    continue
                dados, motivo = rodar(cmd, entrada, args.reps, args.reps * args.limite * 1.5 + 30)
                if dados is None:
                    vivos[chave] = False
                    limites.append([tipo, algoritmo, linguagem, ultimo_ok[chave], motivo])
                    continue
                ultimo_ok[chave] = n
                t = dados["tempos_s"]
                custos[chave] = dados["custo"]
                linhas.append([tipo, n, len(arestas), algoritmo, linguagem, dados["custo"],
                               statistics.mean(t), statistics.stdev(t) if len(t) > 1 else 0.0,
                               len(t), dados.get("nos", ""), dados["mem_kb"]])
                print(f"[{tipo}] n={n:2d} {algoritmo:11s} {linguagem:6s} "
                      f"{statistics.mean(t):12.6f} s   custo={dados['custo']}")
            if len(set(custos.values())) > 1:
                raise RuntimeError(f"RESPOSTAS DIFERENTES em {entrada}: {custos}")
            with open(os.path.join(pasta_res, "resultados.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["mapa", "n", "estradas", "algoritmo", "linguagem", "custo",
                            "media_s", "desvio_s", "reps", "nos", "mem_kb"])
                w.writerows(linhas)
        for chave in IMPLEMENTACOES:
            if vivos[chave]:
                limites.append([tipo, chave[0], chave[1], ultimo_ok[chave], f"chegou em nmax={args.nmax}"])

    with open(os.path.join(pasta_res, "limites.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mapa", "algoritmo", "linguagem", "maior_n_viavel", "motivo_da_parada"])
        w.writerows(limites)
    print(f"\nPronto em {(time.time() - inicio) / 60:.1f} min. Agora rode: python3 src/graficos.py")


if __name__ == "__main__":
    main()
