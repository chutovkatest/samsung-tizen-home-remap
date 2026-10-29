/*
 * Minimal inert ARMv7 native entry point for the Tizen rule carrier.
 * Does not read files, access a network, hook a key, or run a daemon.
 * The Tizen package manager registers the manifest rule.
 */
__attribute__((naked, noreturn)) void _start(void) {
    __asm__ volatile(
        "mov r0, #0\n"
        "mov r7, #1\n"
        "svc #0\n"
    );
}
