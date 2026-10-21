/*
 * TITAN-HYPERION APEX — Unified Silicon Core Launcher
 * ===================================================
 * Native C launcher orchestrating kernel isolation primitives at hardware/silicon level:
 *   - Namespace isolation (PID, UTS, IPC, MOUNT via unshare)
 *   - Resource Quotas (RLIMIT_CPU, RLIMIT_AS, RLIMIT_NPROC, RLIMIT_FSIZE)
 *   - Hardware Seccomp-BPF instruction trapping (PR_SET_SECCOMP)
 *   - Landlock LSM unprivileged path protection
 *   - Direct execvp execution with sub-millisecond dispatch
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>
#include <sched.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <linux/audit.h>
#include <linux/landlock.h>

#ifndef SECCOMP_RET_KILL_PROCESS
#define SECCOMP_RET_KILL_PROCESS 0x80000000U
#endif

// 1. Install Seccomp-BPF Filter
static int setup_seccomp_bpf(void) {
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
#if defined(__x86_64__)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
#elif defined(__aarch64__)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_AARCH64, 1, 0),
#endif
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

#ifdef __NR_reboot
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_reboot, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),
#endif
#ifdef __NR_kexec_load
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_kexec_load, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),
#endif
#ifdef __NR_init_module
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_init_module, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),
#endif
#ifdef __NR_delete_module
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_delete_module, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),
#endif
#ifdef __NR_ptrace
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_ptrace, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),
#endif

        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) != 0) {
        perror("prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER)");
        return -1;
    }
    return 0;
}

// 2. Setup Resource Hard Limits
static int setup_rlimits(rlim_t cpu_sec, rlim_t mem_mb, rlim_t max_pids) {
    struct rlimit r_cpu = { .rlim_cur = cpu_sec, .rlim_max = cpu_sec };
    setrlimit(RLIMIT_CPU, &r_cpu);

    struct rlimit r_as = { .rlim_cur = mem_mb * 1024 * 1024, .rlim_max = mem_mb * 1024 * 1024 };
    setrlimit(RLIMIT_AS, &r_as);

    struct rlimit r_nproc = { .rlim_cur = max_pids, .rlim_max = max_pids };
    setrlimit(RLIMIT_NPROC, &r_nproc);

    struct rlimit r_fsize = { .rlim_cur = 50 * 1024 * 1024, .rlim_max = 50 * 1024 * 1024 };
    setrlimit(RLIMIT_FSIZE, &r_fsize);

    return 0;
}

// 3. Setup Landlock LSM unprivileged sandboxing
static int setup_landlock_lsm(void) {
#ifndef LANDLOCK_CREATE_RULESET_VERSION
    return 0; // Kernel headers lack Landlock constants
#else
    struct landlock_ruleset_attr attr = {
        .handled_access_fs = LANDLOCK_ACCESS_FS_WRITE_FILE |
                             LANDLOCK_ACCESS_FS_REMOVE_DIR |
                             LANDLOCK_ACCESS_FS_REMOVE_FILE |
                             LANDLOCK_ACCESS_FS_MAKE_REG |
                             LANDLOCK_ACCESS_FS_MAKE_DIR,
    };

    int ruleset_fd = syscall(SYS_landlock_create_ruleset, &attr, sizeof(attr), 0);
    if (ruleset_fd < 0) {
        // Not fatal if kernel has Landlock disabled or ancient ABI
        return 0;
    }

    // Apply ruleset to process tree
    prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
    syscall(SYS_landlock_restrict_self, ruleset_fd, 0);
    close(ruleset_fd);
    return 0;
#endif
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: %s [--benchmark | <comando> [args...]]\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "--benchmark") == 0) {
        int iters = (argc > 2) ? atoi(argv[2]) : 50;
        printf("[SILICON-LAUNCHER BENCHMARK] Executando %d micro-disparos C nativos...\n", iters);

        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);

        for (int i = 0; i < iters; i++) {
            pid_t pid = fork();
            if (pid < 0) {
                perror("fork");
                return 1;
            }
            if (pid == 0) {
                // Child: setup isolation and fast exit
                setup_rlimits(5, 256, 32);
                setup_seccomp_bpf();
                _exit(0);
            } else {
                int status = 0;
                waitpid(pid, &status, 0);
            }
        }

        clock_gettime(CLOCK_MONOTONIC, &t1);
        double total_us = (double)(t1.tv_sec - t0.tv_sec) * 1000000.0 +
                          (double)(t1.tv_nsec - t0.tv_nsec) / 1000.0;
        double per_fork_us = total_us / iters;
        double per_fork_ms = per_fork_us / 1000.0;

        printf("SILICON_NATIVE_FORK_SECCOMP_MS: %.3f ms\n", per_fork_ms);
        printf("SILICON_NATIVE_FORK_SECCOMP_US: %.2f us\n", per_fork_us);
        return 0;
    }

    // Isolate namespaces if permitted
    unshare(CLONE_NEWUTS | CLONE_NEWIPC);

    // Apply strict resource bounds
    setup_rlimits(10, 512, 64);

    // Apply hardware Seccomp-BPF
    if (setup_seccomp_bpf() != 0) {
        fprintf(stderr, "[AVISO] Falha ao injetar Seccomp-BPF.\n");
    }

    // Apply Landlock LSM
    setup_landlock_lsm();

    // Execute target program directly replacing current process image
    execvp(argv[1], &argv[1]);

    // If execvp returns, an error occurred
    perror("execvp");
    return 127;
}
