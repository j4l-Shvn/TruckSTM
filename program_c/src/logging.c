#include "logging.h"

void init_logging(struct Logger* logger) {
    logger->fd = open("/tmp/challenge05.log", O_RDWR | O_CREAT | O_TRUNC, 0666);
    logger->ID = 1;
    logger->pos = 0;
    logger->buffer = malloc(MAX_BUFF);
    logger->buffer_index = 0;
    logger->iv = (unsigned char *)"0123456789012345";
    memcpy(logger->key, (unsigned char *)"01234567890123456789012345678901", 32);
}

void kill_logging(struct Logger* logger) {
    flush_buffer(logger);
    close(logger->fd);
    free(logger);
}


// The **main** function of this file. Will take in a CAN frame and call other functions to transform and log the
// data. (CAN frame in) -> (Transform data) -> (Write to buffer system)
void log_can(struct Logger* logger, unsigned char frame[], uint8_t size, uint32_t j1939_id) {
    // Meta Data
    // Make a string with ID and date
    char id_date_buff[100];
    time_t now;
    time(&now);
    int meta_size = snprintf(id_date_buff, 50, "%i: %s:", logger->ID, ctime(&now));
    id_date_buff[meta_size - 2] = 0x20;  // remove newline
    logger->ID++;
    // Create new memory pointer and copy CAN frame just after our meta-data string
    unsigned char* data = malloc(size + meta_size);  // +1 for newline
    memcpy(data, id_date_buff, meta_size);
    memcpy(data+meta_size, frame, size);
    size = size + meta_size + 1;
    data[size - 2] = 0x0A;
    // Encrypt the data
    unsigned char* ciphertext = malloc(size*2);  // No idea how much larger this should be from plaintext
    unsigned char tag[16];
    unsigned char* additional = (unsigned char*)"We won't use this";
    int ciphertext_len;
    ciphertext_len = gcm_encrypt(data, size,
                                additional, 0,
                                logger->key,
                                logger->iv, IV_LEN,
                                ciphertext, tag);

    // Allocate hex conversion buffer  // TODO This part could probably be removed, just make the log file binary
    //int hex_length;
    //char* hex_dump = convert_to_hex(data, size, &hex_length);

    // Write out the buffer
    write_buffer(logger, (char *)data, size - 1);  // remove null term from file write
    free(data);
    //free(hex_dump);
}


/** @brief This function will take an unsigned char buffer and convert it to a hexadecimal representation. It will
  *        append a null terminator to the resulting string
  *
  * @param src: This is the unsigned char buffer that stores the information to be converted to hex
  * @param src_size: How many bytes of the src buffer will be read and converted to hex
  * @param dest_size: return parameter, the hex string size
  * @return This function will return a char buffer with the hex string + null term
  */
char* convert_to_hex(unsigned char src[], int src_size, int* dest_size) {
    // Expand by factor of 2, plus newline and end null
    *dest_size = (src_size * 2) + 2;
    char *dest = malloc(*dest_size);
    for (int i = 0; i < src_size; i++){
        sprintf(&dest[i*2], "%02x", src[i]);
    }
    dest[*dest_size - 2] = 0x0A;  // new line
    dest[*dest_size - 1] = 0x00;  // null
    *dest_size = *dest_size - 1;  // TODO decide if this makes sense. Only counts data as size, null term not included
    return dest;
}


/** @brief Pushes the data to the logging buffer. If the buffer were to fill, then flush the current buffer and write the
  *        data to the flushed buffer.
  *
  * @param logger: The struct used for logging related variables
  * @param data: char pointer to the data
  * @param data_size: size of the data to write
  */
void write_buffer(struct Logger* logger, char *data, int data_size) {
    if ((data_size < 0) || (data_size > MAX_BUFF)) {
        // TODO write current buffer, then this data instead?
        puts("Cannot write data!");
        return;
    }
    // Check if buffer would overflow, flush if it would.
    int updated_index = logger->buffer_index + data_size;
    if (updated_index > MAX_BUFF) {
        flush_buffer(logger);
        updated_index = data_size;
    }
    // Push new data onto the buffer
    memcpy(logger->buffer + logger->buffer_index, data, data_size);
    // Update where the buffer offset is
    logger->buffer_index = updated_index;
}


/** @brief Function that flushes the buffer and resets the index to be 0
  *
  * @param logger: The struct used for logging related variables
  */
void flush_buffer(struct Logger* logger) {  // didn't like this being inlined during linking?
    write(logger->fd, logger->buffer, logger->buffer_index);
    // [DEV] Could add free then malloc here to increase processing
    // [DEV] Could also zero out memory here
    logger->buffer_index = 0;
}


int test_logging() {
    // example usage
    struct Logger* logger = (struct Logger*) malloc(sizeof(struct Logger));
    init_logging(logger);
    unsigned char src[] = "123456789";
    /*
    puts("Logging 1");
    log_can(logger, src, 10, 01);
    puts("Logging 2");
    log_can(logger, src, 10, 01);
    puts("Logging 3");
    log_can(logger, src, 10, 01);
    puts("Logging 4");
    log_can(logger, src, 10, 01);
    puts("Logging 5");
    log_can(logger, src, 10, 01);
    */
    for (int i = 0; i < 10; i++) {
        log_can(logger, src, 10, 01);
    }
    kill_logging(logger);
    return 0;
}
