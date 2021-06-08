#ifndef SRC_LOGGING_H_
#define SRC_LOGGING_H_

#include <stdlib.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include "Evp-gcm-encrypt.h"


#define MAX_BUFF 1024
#define IV_LEN 16

struct Logger {
    int fd;
    int ID;
    uint32_t pos; // Unknown if this will be needed, file pos
    char *buffer;
    int buffer_index;
    unsigned char *iv;
    unsigned char key[32];
};

void init_logging(struct Logger* logger);
void kill_logging(struct Logger* logger);
void log_can(struct Logger* logger, unsigned char frame[], uint8_t size, uint32_t j1939_id);
char* convert_to_hex(unsigned char src[], int src_size, int* dest_size);
void write_buffer(struct Logger* logger, char *data, int data_size);
void flush_buffer(struct Logger* logger);
#endif /* SRC_LOGGING_H_ */