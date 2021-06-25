#include "EVP_des_ede3_cbc.h"


int main (void)
{
    /* Setup key and IV for DES3 */
    /* A 192 bit key (64 * 3) */
    unsigned char key[24];
    if (!RAND_bytes(key, sizeof key)) {
        handleErrors();
    }
    /* A 64 bit IV */
    unsigned char iv[8];
    if (!RAND_bytes(iv, sizeof iv )) {
        handleErrors();
    }
    /* Message to be encrypted */
    unsigned char *plaintext =
        (unsigned char *)"The quick brown fox jumps over the lazy dog";

    /*
    * Buffer for ciphertext. 8 bytes are added to the size to account for
    * alignment.
    */
    unsigned char ciphertext[strlen((char *)plaintext) + 8];

    /* Buffer for the decrypted text */
    unsigned char decryptedtext[strlen((char *)plaintext) + 8];

    int decryptedtext_len, ciphertext_len;

    /* Encrypt the plaintext */
    ciphertext_len = des_encrypt(plaintext, strlen ((char *)plaintext),
                                 key,
                                 iv,
                                 ciphertext);

    /* Do something useful with the ciphertext here */
    printf("Ciphertext of length %d is:\n", ciphertext_len);
    BIO_dump_fp (stdout, (const char *)ciphertext, ciphertext_len);

    /* Decrypt the ciphertext */
    decryptedtext_len = des_decrypt(ciphertext, ciphertext_len,
                                    key, iv,
                                    decryptedtext);

    if (decryptedtext_len >= 0) {
        /* Add a NULL terminator. We are expecting printable text */
        decryptedtext[decryptedtext_len] = '\0';

        /* Show the decrypted text */
        printf("Decrypted text of length %d is:\n", decryptedtext_len);
        printf("%s\n", decryptedtext);
    } else {
        printf("Decryption failed\n");
    }

    return 0;
}


void handleErrors(void)
{
    ERR_print_errors_fp(stderr);
    abort();
}


int des_encrypt(unsigned char *plaintext, int plaintext_len,
                unsigned char *key,
                unsigned char *iv,
                unsigned char *ciphertext)
{
    EVP_CIPHER_CTX *ctx;

    int len;
    int ciphertext_len;

    /* Create and initialise the context */
    if(!(ctx = EVP_CIPHER_CTX_new()))
        handleErrors();

    /* Initialise the encryption operation. */
    // TODO EVP_CIPHER_CTX_ctrl with key and iv length
    if(1 != EVP_EncryptInit_ex(ctx, EVP_des_ede3_cbc(), NULL, key, iv))
        handleErrors();

    /*
     * Provide the message to be encrypted, and obtain the encrypted output.
     * EVP_EncryptUpdate can be called multiple times if necessary
     */
    if(1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len))
        handleErrors();
    ciphertext_len = len;

    /*
     * Finalise the encryption. Normally ciphertext bytes may be written at
     * this stage, but this does not occur in GCM mode
     */
    if(1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len))
        handleErrors();
    ciphertext_len += len;

    /* Clean up */
    EVP_CIPHER_CTX_free(ctx);

    return ciphertext_len;
}


int des_decrypt(unsigned char *ciphertext, int ciphertext_len,
                unsigned char *key, unsigned char *iv,
                unsigned char *plaintext)
{
    EVP_CIPHER_CTX *ctx;
    int len;
    int plaintext_len;
    int ret;

    /* Create and initialise the context */
    if(!(ctx = EVP_CIPHER_CTX_new()))
        handleErrors();

    /* Initialise the decryption operation. */
    if(!EVP_DecryptInit_ex(ctx, EVP_des_ede3_cbc(), NULL, key, iv))
        handleErrors();

    /* Initialise key and IV */
    if(!EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv))
        handleErrors();

    /*
     * Provide the message to be decrypted, and obtain the plaintext output.
     * EVP_DecryptUpdate can be called multiple times if necessary
     */
    if(!EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len))
        handleErrors();
    plaintext_len = len;

    /*
     * Finalise the decryption. A positive return value indicates success,
     * anything else is a failure - the plaintext is not trustworthy.
     */
    ret = EVP_DecryptFinal_ex(ctx, plaintext + len, &len);

    /* Clean up */
    EVP_CIPHER_CTX_free(ctx);

    if(ret > 0) {
        /* Success */
        plaintext_len += len;
        return plaintext_len;
    } else {
        /* Verify failed */
        return -1;
    }
}
