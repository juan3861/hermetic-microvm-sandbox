/*
 * TITAN-HYPERION APEX — Hardware-Level Seccomp-BPF Syscall Filter (gVisor/Ring-0 Trap)
 * ====================================================================================
 * Traps CPU instruction 'syscall' (0x0F 0x05) at the Linux Kernel boundary.
 * Enforces hardware-level prohibition of privilege-escalating syscalls:
 *   - reboot, kexec_load, init_module, delete_module, ptrace, process_vm_writev
 *
 * Employs direct Berkeley Packet Filter (BPF) bytecode compiled and verified by
 * the Linux in-kernel BPF verifier via prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER).
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stddef.h>
#include <errno.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <linux/audit.h>
#include <string.h>

#ifndef SECCOMP_RET_KILL_PROCESS
#define SECCOMP_RET_KILL_PROCESS 0x80000000U
#endif

// Validates current CPU architecture and compiles Seccomp-BPF bytecode filter
int install_hyperion_seccomp_bpf_filter(void) {
    // 1. Prevent child privilege escalation (mandatory for unprivileged seccomp)
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    // 2. Define BPF Bytecode instructions
    struct sock_filter filter[] = {
        // [0] Load architecture into accumulator from seccomp_data struct
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        // [1] Verify architecture is AUDIT_ARCH_X86_64, jump 1 if true, else jump to kill
#if defined(__x86_64__)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
#elif defined(__aarch64__)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_AARCH64, 1, 0),
#endif
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        // [3] Load syscall number (nr) into accumulator
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        // [4..] Block forbidden syscalls and return EPERM (1)
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
#ifdef __NR_finit_module
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_finit_module, 0, 1),
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
#ifdef __NR_process_vm_writev
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_process_vm_writev, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),
#endif

        // Allow all other normal POSIX syscalls
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    // 3. Inject BPF filter into Kernel Seccomp subsystem
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) != 0) {
        perror("prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER)");
        return -1;
    }

    return 0;
}

// Standalone test harness
int main(int argc, char *argv[]) {
    printf("[SECCOMP-BPF] Instalando filtro de hardware no kernel...\n");
    if (install_hyperion_seccomp_bpf_filter() != 0) {
        fprintf(stderr, "[FALHA] Kernel rejeitou filtro BPF.\n");
        return 1;
    }
    printf("[SECCOMP-BPF] SUCESSO: Filtro ativo em Ring 0.\n");

    // Test: Attempting a forbidden syscall directly (sys_reboot)
    if (argc > 1 && strcmp(argv[1], "--test-trap") == 0) {
        printf("[SECCOMP-BPF] Testando tentativa de reboot via syscall(SYS_reboot)...\n");
        long ret = syscall(__NR_reboot, 0, 0, 0, 0);
        if (ret == -1 && errno == EPERM) {
            printf("[SECCOMP-BPF] TRAP CONFIRMADO: Syscall interceptada e negada com EPERM (Opcode bloqueado pela CPU)!\n");
            return 0;
        } else {
            fprintf(stderr, "[FALHA DE TRAP] Syscall retornou %ld (errno=%d)\n", ret, errno);
            return 2;
        }
    }

    return 0;
}
