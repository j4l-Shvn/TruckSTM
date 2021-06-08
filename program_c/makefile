CFLAGS=-O2
COMPILER=clang

all: main

vuln: 
	if [ ! -d ../build ]; then mkdir ../build; fi
	./patch_unpatch_script vuln
	$(MAKE) main TYPE=

log_testing: logging.o Evp-gcm-encrypt.o
	$(COMPILER) $(CFLAGS) -o a.out -lcrypto logging.o Evp-gcm-encrypt.o

main: main.o gpio.o bumper.o logging.o Evp-gcm-encrypt.o
	$(COMPILER) $(CFLAGS) -o main -lcrypto main.o gpio.o bumper.o logging.o Evp-gcm-encrypt.o

main.o: src/main.c
	$(COMPILER) -c -Iinc $(CFLAGS) src/main.c

gpio.o: src/gpio.c
	$(COMPILER) -c -Iinc $(CFLAGS) src/gpio.c

bumper.o: src/bumper.c
	$(COMPILER) -c -Iinc $(CFLAGS) src/bumper.c

logging.o: src/logging.c
	$(COMPILER) -Wall -c -Iinc $(CFLAGS) src/logging.c

Evp-gcm-encrypt.o: src/Evp-gcm-encrypt.c
	$(COMPILER) -Wall -c -Iinc $(CFLAGS) src/Evp-gcm-encrypt.c

clean:
	rm -f *.o

.PHONY: all vuln patch clean
