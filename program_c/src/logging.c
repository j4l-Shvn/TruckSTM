// #include "logging.h"

// /* Globals */
// int num_added_frames = 0;  // TODO Should be removed from global, as it is specific to an mblock's state
// FILE * __WFD = NULL;  // TODO should be removed from global
// int num_elements_added = 0;  // "elements" are mblocks written to a file
// clock_t start_time;


// /* A 192 bit key (64 * 3) */
// unsigned char KEY[24];
// /* A 64 bit IV */
// unsigned char IV[8];

// /* Functions */



// void init_Mblock(Mblock* mblock) {
//     // TODO make real values/explain why these defaults
//     strcpy(mblock->generation, "CAN2");
//     strcpy(mblock->version, "TU2");
//     strcpy(mblock->logger_number, "12");
//     strcpy(mblock->file_number, "123");
//     strcpy(mblock->micro_of_sdcard, "ABC");
//     reset_mblock(mblock);
// }

// void reset_mblock(Mblock* mblock){
//     memset(mblock->frames, 0, (BUFFER_SIZE * sizeof(struct CAN_FRAME)));
//     memset(mblock->rx_counts, 0, member_size(Mblock, rx_counts));  // TODO should this be reset EACH time? Seems useless then
//     memset(mblock->can_rx_err_counts, 0, member_size(Mblock, can_rx_err_counts));
//     memset(mblock->can_tx_err_counts, 0, member_size(Mblock, can_tx_err_counts));
//     mblock->crc32 = 0;
// }


// // void crypto_setup (void) {
// //     /* Setup key and IV for DES3 */
// //     int key_size = sizeof(KEY);
// //     int iv_size = sizeof(IV);

// //     if (!RAND_bytes(KEY, key_size)) {
// //         handleErrors();
// //     }
// //     /* A 64 bit IV */
// //     if (!RAND_bytes(IV, iv_size)) {
// //         handleErrors();
// //     }
// //     // Write out key length & key
// //     if (fwrite(&key_size, 1, sizeof(key_size), __WFD) < 1) {
// //         error(1, "Unable to write key size: %d", key_size);
// //     }
// //     if (fwrite(KEY, 1, key_size, __WFD) < 1) {
// //         error(1, "Unable to write key to file");
// //     }
// //     // write out iv length & iv
// //     if (fwrite(&iv_size, 1, sizeof(iv_size), __WFD) < 1) {
// //         error(1, "Unable to write iv size: %d", iv_size);
// //     }
// //     if (fwrite(IV, 1, iv_size, __WFD) < 1) {
// //         error(1, "Unable to write IV");
// //     }
// // }


// // void new_iv (void) {
// //     int iv_size = sizeof(IV);
// //     if (!RAND_bytes(IV, iv_size)) {
// //         handleErrors();
// //     }
// //     if (fwrite(&iv_size, 1, sizeof(iv_size), __WFD) < 1) {
// //         error(1, "Unable to write iv size: %d", iv_size);
// //     }
// //     if (fwrite(IV, 1, iv_size, __WFD) < 1) {
// //         error(1, "Unable to write IV");
// //     }
// // }

// void logging_setup(char* log_file_name, int channel){
//     if (RECREATE_LOG_FILE_DESCRIPTOR == 0)
//         if ((__WFD = fopen(log_file_name, "wb")) == NULL)
//             error(1,"Could not create descriptor for %s", log_file_name);
//     //memcpy(rx_frame.channel, interface, strlen(interface)); 
//     rx_frame.channel = channel;
//     rx_frame.fracTiming = 0;//(float)1/CLOCKS_PER_SEC; //Set to a default for now
//     //TODO change fracTiming to what it should be, a 3 byte array?? Is this required?
//     start_time = clock();

//     // Initialize Crypto
//    // crypto_setup();
// }

// // void write_encrypted(Mblock* mblock) {
// //     int bytes_written = 0;
// //     // Allocate plaintext buffer, and fill with Mblock data
// //     unsigned char *plaintext = malloc(sizeof(Mblock));
// //     memcpy(plaintext, mblock, sizeof(Mblock));
// //     // Allocate buffer for returning ciphertext, plus some extra bytes
// //     unsigned char *ciphertext = malloc(sizeof(Mblock) + 16);  // TODO find better value for both des and aes
// //     // Pass plaintext to encryption algorithm
// //     bytes_written = encrypt(plaintext, sizeof(Mblock), KEY, IV, ciphertext);
// //     // Write Tag_length:Value
// //     if (fwrite(&bytes_written, sizeof(int), 1, __WFD) < 1) {
// //         error(1, "Could not write tag length of %d to %s", bytes_written, LOG_NAME);
// //     }
// //     if (fwrite(ciphertext, 1, bytes_written, __WFD) < 1) {
// //         error(1, "Could not write ciphertext of length %d to %s", bytes_written, LOG_NAME);
// //     }
// //     free(plaintext);
// //     free(ciphertext);
// //     new_iv();  // make new IV for each block
// // }

// void log_to_file(Mblock* mblock) {  // TODO fix LOG_NAME usage here and then in main
//     if (RECREATE_LOG_FILE_DESCRIPTOR == 1){
//         if ((__WFD = fopen(LOG_NAME, "wb")) == NULL)
//             error(1, "Could not create descriptor for %s", LOG_NAME);
//         if (fseek(__WFD, num_elements_added*sizeof (Mblock), SEEK_SET ))
//             error(1, "Could not seek to append location for file %s", LOG_NAME);
//     }

//     /* Patch */
//     //write_encrypted(mblock);
//     printf ("%s\n", mblock->generation);
//     if (fwrite((const void *)&mblock,sizeof (Mblock),1, __WFD) < 1){
//         error(1,"Could not log CAN data");
//     }

//     if (FLUSH_AT_RUNTIME == 1){
//         if (fflush(__WFD)){
//             error(1,"Could not flush CAN data log");
//         }
//     }

//     if (RECREATE_LOG_FILE_DESCRIPTOR == 1){
//         fclose(__WFD);
//     }
//     num_elements_added++;
// }

// void do_log(Mblock* mblock, struct can_frame read_frame) {  // TODO move rx to param to arg and not cross file global
//     // Copy the CAN info into an RX frame
//     rx_frame.canID = read_frame.can_id;
//     memset(rx_frame.data, 0xff, 8);
//     memcpy(rx_frame.data,read_frame.data,8);
//     rx_frame.dlc = read_frame.can_dlc;
//     rx_frame.timestamp = (unsigned)time(NULL);
//     rx_frame.systemTiming = (double)(clock() - start_time) / CLOCKS_PER_SEC;

//     // Copy the RXframe data into the MBLOCK array
//     memcpy(&mblock->frames[num_added_frames], &rx_frame, sizeof (struct CAN_FRAME));
//     mblock->rx_counts[rx_frame.channel]++;
//     //TODO error frame counts to be increased

//     num_added_frames++;
//     if (num_added_frames >= BUFFER_SIZE){
//         //Update CRC
//         crc32(mblock, sizeof (Mblock), &mblock->crc32);
//         // Dump into log
//         log_to_file(mblock);
//         // Refresh
//         reset_mblock(mblock);
//         num_added_frames = 0;
//         printf("Wrote to file\n");  // TODO remove from release
//     }
// }


// void terminate_logging_gracefully(Mblock* mblock){
//     log_to_file(mblock);
//     if (fflush(__WFD)){
//         error(1,"Could not flush to file");
//     }

//     if (RECREATE_LOG_FILE_DESCRIPTOR == 1)
//         fclose(__WFD);
// }

#include "logging.h"

/* Global temps */
long num_added_frames = 0;
FILE * wfd = NULL;
int num_elements_added = 0;
struct MBlock mblock = {
        . generation = "CAN2",
        . version = "TU2",
        . logger_number = "12",
        . file_number = "123",
        . micro_of_sdcard = "ABC"
};

///* A 192 bit key (64 * 3) */
//unsigned char KEY[24];
///* A 64 bit IV */
//unsigned char IV[8];

/* Supporting functions */

//FILE * __WFD = NULL;  // TODO should be removed from global

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

void reset_mblock(){
    memset(mblock.frames, 0, BUFFER_SIZE*sizeof(struct CAN_FRAME));
    memset(mblock.rx_counts, 0, sizeof (mblock.rx_counts));
    memset(mblock.rx_counts, 0, sizeof (mblock.can_rx_err_counts));
    memset(mblock.rx_counts, 0, sizeof (mblock.can_tx_err_counts));
    mblock.crc32 = 0;
    num_added_frames = 0;
}

void log_to_file(){
    if (RECREATE_LOG_FILE_DESCRIPTOR == 1){
        if ((wfd = fopen(LOG_NAME, "wb")) == NULL)
            error(1, "Could not create descriptor for %s", LOG_NAME);
        if (fseek( wfd, num_elements_added*sizeof (struct MBlock), SEEK_SET ))
            error(1, "Could not seek to append location for file %s", LOG_NAME);
    }
    if (fwrite((const void *)&mblock,sizeof (struct MBlock),1, wfd) < 1){
        error(1,"Could not CANlog to file");
    }
    if (FLUSH_AT_RUNTIME == 1){
        if (fflush(wfd)){
            error(1,"Could not flush CANlog to file");
        }
    }

    if (RECREATE_LOG_FILE_DESCRIPTOR == 1){
        fclose(wfd);
    }
    num_elements_added++;
}

void loging_setup(int channel){

    rx_frame.channel = channel;
    rx_frame.fracTiming = 0;//(float)1/CLOCKS_PER_SEC;
    //TODO change fracTiming to what it should be, a 3 byte array?? Is this required?
    start_time = clock();

    if (RECREATE_LOG_FILE_DESCRIPTOR == 0)
        if ((wfd = fopen(LOG_NAME, "wb")) == NULL)
            error(1,"Could not create descriptor for %s", LOG_NAME);

    //crypto_setup();
}

void loging_handler(struct can_frame read_frame){
    rx_frame.canID = read_frame.can_id;
    memset(rx_frame.data, 0xff, 8);
    memcpy(rx_frame.data,read_frame.data,8);
    rx_frame.dlc = read_frame.can_dlc;
    rx_frame.timestamp = (unsigned)time(NULL);
    rx_frame.systemTiming = (double)(clock() - start_time) / CLOCKS_PER_SEC;

    memcpy(&mblock.frames[num_added_frames], &rx_frame, sizeof (rx_frame));
    mblock.rx_counts[rx_frame.channel]++;
    //TODO error frame counts to be increased

    num_added_frames++;

    if (num_added_frames >= BUFFER_SIZE){
        //Update CRC
        crc32(&mblock, sizeof (mblock), &mblock.crc32);
        // Dump into log
        log_to_file(&mblock, sizeof (mblock));
        // Refresh
        reset_mblock();
    }
}

void terminate_loging_gracefully(){
    if (num_added_frames > 0)
        log_to_file(&mblock, sizeof (mblock));
    if (fflush(wfd)){
        error(1,"Could not flush to file %s", LOG_NAME);
    }

    if (RECREATE_LOG_FILE_DESCRIPTOR == 1)
        fclose(wfd);
}