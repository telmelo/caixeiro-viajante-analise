// Caixeiro Viajante: FORÇA BRUTA com limitador de vizinhança.
//
// Parte da cidade 0 e testa todas as rotas possíveis, mas só anda por estradas
// que existem (só vai para cidades vizinhas da atual). Não há poda por custo.
//
// Compilar: g++ -O2 -std=c++17 -o bin/forca_bruta src/forca_bruta.cpp
// Uso:      ./bin/forca_bruta ENTRADA [--reps R]
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <sys/resource.h>
#include <utility>
#include <vector>

using namespace std;
using ll = long long;

static int n, m;
static vector<vector<pair<int, int>>> adj;   // (vizinha, distância)
static vector<int> volta;                    // distância até a cidade 0, ou -1
static vector<int> caminho, melhorRota;
static ll melhorCusto;
static uint64_t nos;

static void dfs(int u, ll custo, int tamanho, uint64_t visitadas) {
    ++nos;
    if (tamanho == n) {                      // visitou todas: tenta fechar o ciclo
        if (volta[u] >= 0) {
            ll total = custo + volta[u];
            if (melhorCusto < 0 || total < melhorCusto) {
                melhorCusto = total;
                melhorRota = caminho;
            }
        }
        return;
    }
    for (auto [v, w] : adj[u]) {             // LIMITADOR: só cidades vizinhas
        if (!(visitadas >> v & 1ULL)) {
            caminho.push_back(v);
            dfs(v, custo + w, tamanho + 1, visitadas | (1ULL << v));
            caminho.pop_back();
        }
    }
}

int main(int argc, char** argv) {
    if (argc < 2) { fprintf(stderr, "uso: %s ENTRADA [--reps R]\n", argv[0]); return 1; }
    int reps = 1;
    for (int i = 2; i + 1 < argc; ++i) if (!strcmp(argv[i], "--reps")) reps = stoi(argv[i + 1]);

    FILE* f = fopen(argv[1], "r");           // leitura fica FORA da medição
    if (!f || fscanf(f, "%d %d", &n, &m) != 2) { fprintf(stderr, "erro ao ler entrada\n"); return 1; }
    if (n > 64) { fprintf(stderr, "n > 64 nao suportado\n"); return 1; }
    adj.assign(n, {});
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        if (fscanf(f, "%d %d %d", &u, &v, &w) != 3) return 1;
        adj[u].push_back({v, w});
        adj[v].push_back({u, w});
    }
    fclose(f);
    for (auto& l : adj) sort(l.begin(), l.end());
    volta.assign(n, -1);
    for (auto [v, w] : adj[0]) volta[v] = w;

    vector<double> tempos;
    for (int r = 0; r < reps; ++r) {
        auto t0 = chrono::steady_clock::now();
        melhorCusto = -1; nos = 0; caminho.assign(1, 0); melhorRota.clear();
        dfs(0, 0, 1, 1ULL);
        auto t1 = chrono::steady_clock::now();
        tempos.push_back(chrono::duration<double>(t1 - t0).count());
    }

    rusage ru; getrusage(RUSAGE_SELF, &ru);
    printf("{\"algoritmo\": \"forca_bruta\", \"linguagem\": \"cpp\", \"n\": %d, \"m\": %d, \"custo\": %lld, \"rota\": ",
           n, m, melhorCusto);
    if (melhorRota.empty()) printf("null");
    else {
        printf("[");
        for (int c : melhorRota) printf("%d, ", c);
        printf("0]");
    }
    printf(", \"nos\": %llu, \"tempos_s\": [", (unsigned long long)nos);
    for (size_t i = 0; i < tempos.size(); ++i) printf(i ? ", %.9f" : "%.9f", tempos[i]);
    printf("], \"mem_kb\": %ld}\n", ru.ru_maxrss);
    return 0;
}
