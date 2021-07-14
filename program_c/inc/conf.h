#ifndef AMP_CHALLENGE_05_CAN_LOG_ENCRYPTION_CONF_H
#define AMP_CHALLENGE_05_CAN_LOG_ENCRYPTION_CONF_H

#define RECREATE_LOG_FILE_DESCRIPTOR 0 // Set this to 0 to enable opening of FD everytime a new block is written to the disk
#define FLUSH_AT_RUNTIME 1
#define LOG_NAME "/tmp/challenge05.log"
#define LOGGER_CHANNEL 0 //A default value to use for CANLOGGER channel
#define BUFFER_SIZE 2
#define IFACETYPE "vcan" //vcan, can
#define IFACENUM 0 //0,1...
#define LOGSELF 0 //Setting this to 1 implies this logger will log messages it sends out as well

/*
 * Alg and Alg mode can take the following options
 * ENC_ALG: 1> AES
 * -------
 * ENC_ALG_MODE:
 * 1> ECB
 * 2> CBC
 * 3> GCM
 */
#define BLK_ENC_ALG 1
#define BLK_ENC_ALG_MODE 1
#define BLK_ENC_KEYSIZE 128
#define BLK_ENC_BLOCKSIZE 128

#endif //AMP_CHALLENGE_05_CAN_LOG_ENCRYPTION_CONF_H
