CC ?= gcc
CFLAGS ?= -O3 -Wall -Wextra

TARGETS = hyperion_seccomp_bpf hyperion_mmu_cow_forker hyperion_silicon_launcher

all: $(TARGETS)

hyperion_seccomp_bpf: hyperion_seccomp_bpf.c
	$(CC) $(CFLAGS) $< -o $@

hyperion_mmu_cow_forker: hyperion_mmu_cow_forker.c
	$(CC) $(CFLAGS) $< -o $@

hyperion_silicon_launcher: hyperion_silicon_launcher.c
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -f $(TARGETS)

.PHONY: all clean
