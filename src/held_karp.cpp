// Caixeiro Viajante: HELD-KARP (programação dinâmica com bitmask).
//
// dp[S][j] = menor custo para sair da cidade 0, visitar exatamente o conjunto S
//            (cidades 1..n-1) e terminar na cidade j (j pertence a S).
//   dp[{j}][j] = w(0, j)
//   dp[S][j]   = min_{i em S - {j}} dp[S - {j}][i] + w(i, j)
//   resposta   = min_j dp[todas][j] + w(j, 0)
// Estrada que não existe tem custo infinito. A tabela é sempre preenchida
// inteira: Theta(n^2 * 2^n) de tempo e Theta(n * 2^n) de memória.
//
// Compilar: g++ -O2 -std=c++17 -o bin/held_karp src/held_karp.cpp
// Uso:      ./bin/held_karp ENTRADA [--reps R]
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <sys/resource.h>
#include <unistd.h>
#include <vector>

using namespace std;
using ll = long long;
static const uint32_t INF = 0x3f3f3f3f;

int main(int argc, char** argv) {
    if (argc < 2) { fprintf(stderr, "uso: %s ENTRADA [--reps R]\n", argv[0]); return 1; }
    int reps = 1;
    for (int i = 2; i + 1 < argc; ++i) if (!strcmp(argv[i], "--reps")) reps = stoi(argv[i + 1]);

    int n, m;
    FILE* f = fopen(argv[1], "r");           // leitura fica FORA da medição
    if (!f || fscanf(f, "%d %d", &n, &m) != 2) { fprintf(stderr, "erro ao ler entrada\n"); return 1; }
    vector<vector<uint32_t>> W(n, vector<uint32_t>(n, INF));
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        if (fscanf(f, "%d %d %d", &u, &v, &w) != 3) return 1;
        W[u][v] = W[v][u] = (uint32_t)w;
    }
    fclose(f);

    const int N = n - 1;                     // bit b representa a cidade b+1
    const uint64_t total = 1ULL << N;
    const uint64_t bytes = total * (uint64_t)N * sizeof(uint32_t);
    const uint64_t ram = (uint64_t)sysconf(_SC_PAGE_SIZE) * (uint64_t)sysconf(_SC_PHYS_PAGES);
    if (bytes > 0.7 * ram) {
        printf("{\"algoritmo\": \"held_karp\", \"linguagem\": \"cpp\", \"n\": %d, \"erro\": \"memoria\", "
               "\"bytes_necessarios\": %llu}\n", n, (unsigned long long)bytes);
        return 3;
    }

    vector<uint32_t> w_(N * N);              // pesos já deslocados para os bits
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j) w_[i * N + j] = W[i + 1][j + 1];

    vector<uint32_t> dp(total * N, INF);
    vector<double> tempos;
    ll resposta = -1;

    for (int r = 0; r < reps; ++r) {
        auto t0 = chrono::steady_clock::now();
        for (uint64_t S = 1; S < total; ++S) {
            uint32_t* linha = &dp[S * N];
            for (uint64_t resto = S; resto; resto &= resto - 1) {
                int j = __builtin_ctzll(resto);
                uint64_t anterior = S ^ (1ULL << j);
                if (anterior == 0) { linha[j] = W[0][j + 1]; continue; }
                const uint32_t* prev = &dp[anterior * N];
                ll melhor = INF;
                for (uint64_t r2 = anterior; r2; r2 &= r2 - 1) {
                    int i = __builtin_ctzll(r2);
                    ll c = (ll)prev[i] + w_[i * N + j];
                    if (c < melhor) melhor = c;
                }
                linha[j] = (uint32_t)min<ll>(melhor, INF);
            }
        }
        const uint32_t* fim = &dp[(total - 1) * N];
        ll best = INF;
        for (int j = 0; j < N; ++j) best = min<ll>(best, (ll)fim[j] + W[j + 1][0]);
        resposta = best >= INF ? -1 : best;
        auto t1 = chrono::steady_clock::now();
        tempos.push_back(chrono::duration<double>(t1 - t0).count());
    }

    rusage ru; getrusage(RUSAGE_SELF, &ru);
    printf("{\"algoritmo\": \"held_karp\", \"linguagem\": \"cpp\", \"n\": %d, \"m\": %d, \"custo\": %lld, \"tempos_s\": [",
           n, m, resposta);
    for (size_t i = 0; i < tempos.size(); ++i) printf(i ? ", %.9f" : "%.9f", tempos[i]);
    printf("], \"mem_kb\": %ld}\n", ru.ru_maxrss);
    return 0;
}
