#ifndef AMP_CHALLENGE_05_CAN_LOG_ENCRYPTION_LOGGING_H
#define AMP_CHALLENGE_05_CAN_LOG_ENCRYPTION_LOGGING_H

// credit: https://stackoverflow.com/a/3553321
#define member_size(type, member) sizeof(((type *)0)->member)

#include "conf.h"
//#include "util.h"
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <linux/can.h>
#include <time.h>
#include <stdint.h>
//#include "EVP_des_ede3_cbc.h"

/* CANLogger3 structs */
struct CAN_FRAME{
    uint8_t channel;
    uint32_t timestamp;
    uint32_t systemTiming;
    uint32_t canID;
    uint8_t dlc;
    uint8_t fracTiming; //Using a float instead of a three byte array
    uint8_t data[8];
}rx_frame;
clock_t start_time;

struct MBlock{
    char generation[4];
    struct CAN_FRAME frames[BUFFER_SIZE];
    uint32_t rx_counts[3]; // Essentially the same, but uses the channel no. as index instead
    uint8_t can_rx_err_counts[3]; // Essentially the same, but uses the channel no. as index instead
    uint8_t can_tx_err_counts[3]; // Essentially the same, but uses the channel no. as index instead
    char version[3];
    char logger_number[2];
    char file_number[3];
    char micro_of_sdcard[3];
    uint32_t crc32;
};

/* Functions */
void loging_setup(int channel);
void loging_handler(struct can_frame read_frame);
void terminate_loging_gracefully();
void log_to_file();
void reset_mblock();
uint32_t crc32_for_byte(uint32_t r);
void crc32(const void *data, size_t n_bytes, uint32_t* crc);

#endif //AMP_CHALLENGE_05_CAN_LOG_ENCRYPTION_LOGGING_H