# Caixeiro Viajante: força bruta × Held-Karp (C++ e Python)

Projeto de Complexidade, Teoria da Computação (Prof. Daniel Bezerra).
Dois algoritmos × duas linguagens = 4 implementações, todas rodando sobre as mesmas entradas.

## Limitador de vizinhança

Só existe estrada entre cidades vizinhas. Não dá para ir de Recife a Natal direto: é preciso passar por João Pessoa.

- O limitador está **no mapa (na entrada)**, então os 4 programas recebem exatamente as mesmas estradas e precisam dar a mesma resposta.
- A **força bruta** só tenta ir para cidades vizinhas da atual (é aqui que o limitador corta trabalho).
- O **Held-Karp** trata estrada inexistente como custo infinito e continua preenchendo a tabela inteira.
- Cada cidade é visitada exatamente uma vez (TSP clássico). Se não existir rota, a resposta é `-1`.

Três mapas, sempre com as mesmas cidades para o mesmo `n` (muda só quais estradas existem):

| Mapa | Estradas | Papel no experimento |
|---|---|---|
| `anel` | só o anel (2 vizinhas por cidade) | melhor caso da força bruta |
| `vizinhos` | anel + 3 cidades mais próximas | caso médio (mapa realista) |
| `completo` | todo par de cidades (sem limitador) | pior caso da força bruta |

## Estrutura

```
src/forca_bruta.cpp   src/forca_bruta.py    força bruta com limitador (DFS só por vizinhas, sem poda por custo)
src/held_karp.cpp     src/held_karp.py      Held-Karp (DP com bitmask)
src/gerar_entradas.py                       gerador com semente fixa (20261124)
src/medir.py                                script de medição
src/testar.py                               testes de corretude
src/graficos.py                             gráficos e tabelas
Makefile                                    compila o C++ com -O2
```

## Como reproduzir

Requisitos (Fedora): `sudo dnf install gcc-c++ make python3 python3-matplotlib`

```bash
make                          # compila (g++ -O2 -std=c++17)
python3 src/testar.py         # 1. corretude: os 4 + oráculo dão o mesmo custo
python3 src/medir.py --rapido # 2a. prévia (~10 min): 3 repetições, limite de 10 s
python3 src/medir.py          # 2b. experimento oficial: 15 repetições, limite de 60 s (deixe a noite toda)
python3 src/graficos.py       # 3. gera graficos/*.png e as tabelas em Markdown
```

Saídas:
- `resultados/resultados.csv`: média e desvio-padrão por mapa, n, algoritmo e linguagem.
- `resultados/limites.csv`: maior n viável em até 60 s e o motivo da parada (tempo ou memória).
- `graficos/`: 1 a 6 em PNG, mais `tabela_resultados.md` e `tabela_limites.md`.

Metodologia seguida:
- Mesmas entradas para os 4 programas.
- Só o algoritmo é cronometrado (a leitura do arquivo fica fora).
- 15 repetições por tamanho, com média e desvio.
- Uma execução de sondagem antes das repetições.
- O `medir.py` aborta se alguma implementação der resposta diferente.

Para a seção de ambiente do relatório:

```bash
lscpu | grep "Model name"; free -h; cat /etc/os-release | head -2; g++ --version | head -1; python3 --version
```

## Complexidade (com o limitador)

| | Tempo | Espaço |
|---|---|---|
| Força bruta, mapa completo | Θ((n−1)!) nós na árvore de busca | Θ(n) |
| Força bruta, grafo com grau máximo d | O((d−1)ⁿ), cotada por O((n−1)!) | Θ(n) |
| Força bruta, anel | Θ(n) | Θ(n) |
| Held-Karp (qualquer mapa) | Θ(n²·2ⁿ) | Θ(n·2ⁿ) |

O limitador muda a força bruta: melhor, médio e pior caso **passam a ser diferentes** (dependem do mapa).
O Held-Karp não muda, porque preenche a tabela inteira de qualquer jeito.
O programa da força bruta conta os nós visitados (`nos`), e o gráfico 2 mostra que o tempo é proporcional a eles.
