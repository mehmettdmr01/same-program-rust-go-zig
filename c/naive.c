/* Procedural C: two buffers, nested loops, wrapping (toroidal) edges. */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

static int N, GENS;

static double now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

static void read_seed(const char *path, unsigned char *g) {
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(1); }
    size_t len = (size_t)(N + 1) * N;
    char *t = malloc(len);
    len = fread(t, 1, len, f);
    fclose(f);
    for (size_t i = 0, j = 0; i < len; i++) if (t[i] != '\n') g[j++] = t[i] == '1';
    free(t);
}

static void step(const unsigned char *cur, unsigned char *next) {
    for (int y = 0; y < N; y++) {
        int up = (y + N - 1) % N, dn = (y + 1) % N;          /* toroidal */
        for (int x = 0; x < N; x++) {
            int lf = (x + N - 1) % N, rt = (x + 1) % N;      /* toroidal */
            int n = cur[up * N + lf] + cur[up * N + x] + cur[up * N + rt]
                  + cur[y  * N + lf]                  + cur[y  * N + rt]
                  + cur[dn * N + lf] + cur[dn * N + x] + cur[dn * N + rt];
            next[y * N + x] = (n == 3) || (n == 2 && cur[y * N + x]);
        }
    }
}

int main(int argc, char **argv) {
    N = atoi(argv[1]); GENS = atoi(argv[2]);
    unsigned char *a = malloc(N * N), *b = malloc(N * N);
    read_seed(argv[3], a);
    double t0 = now();
    for (int g = 0; g < GENS; g++) { step(a, b); unsigned char *t = a; a = b; b = t; }
    double t1 = now();
    long alive = 0;
    for (int i = 0; i < N * N; i++) alive += a[i];
    printf("alive=%ld sim_ms=%.3f\n", alive, (t1 - t0) * 1e3);
    return 0;
}
