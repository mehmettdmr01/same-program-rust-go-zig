/* wall: runs a child process, passes its stdout through, then appends
   seconds=<wall-clock time> maxrss_kb=<peak memory>. */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/wait.h>
#include <sys/resource.h>
int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: wall cmd args...\n"); return 2; }
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    pid_t pid = fork();
    if (pid == 0) { execvp(argv[1], argv + 1); perror("execvp"); _exit(127); }
    int status; struct rusage ru;
    wait4(pid, &status, 0, &ru);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double s = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
    /* on macOS ru_maxrss is in bytes */
    printf("seconds=%.4f maxrss_kb=%ld\n", s, (long)(ru.ru_maxrss / 1024));
    return WEXITSTATUS(status);
}
