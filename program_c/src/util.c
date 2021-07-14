//
// Created by subhojeet on 6/15/21.
//

#include "util.h"


/* The CRC functions are obtained from http://home.thep.lu.se/~bjorn/crc/
 * This is siply becasue it is better this is a simplitic (possibly non-critical)
 * method and using linked headers like zlib that may not be installed on the BB
 * may not be worth it.
 */
uint32_t crc32_for_byte(uint32_t r) {
    for(int j = 0; j < 8; ++j)
        r = (r & 1? 0: (uint32_t)0xEDB88320L) ^ r >> 1;
    return r ^ (uint32_t)0xFF000000L;
}

void crc32(const void *data, size_t n_bytes, uint32_t* crc) {
    static uint32_t table[0x100];
    if(!*table)
        for(size_t i = 0; i < 0x100; ++i)
            table[i] = crc32_for_byte(i);
    for(size_t i = 0; i < n_bytes; ++i)
        *crc = table[(uint8_t)*crc ^ ((uint8_t*)data)[i]] ^ *crc >> 8;
}

void error(int doexit, char *format_template_msg, ...)
{
    char prnt[256];
    memset(prnt, 0, 100);
    va_list args;
    va_start (args, format_template_msg);
    vsprintf (prnt, format_template_msg, args);
    perror(prnt);
    va_end (args);

    if (doexit == 1){exit(-1);}
}


// void install_signal(int sig, void (*handler)(int sig, siginfo_t *info, void *vp))
// {
//     int ret;
//     struct sigaction sigact = {
//             .sa_sigaction = handler,
//             .sa_flags = SA_SIGINFO,
//     };

//     sigfillset(&sigact.sa_mask);
//     ret = sigaction(sig, &sigact, NULL);
//     if (ret < 0)
//         error(1, "sigaction for signal %i", sig);
// }
