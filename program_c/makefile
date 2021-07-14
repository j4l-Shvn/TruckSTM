CFLAGS=-s -static -O2
COMPILER=gcc

all: main

vuln: 
	if [ ! -d ../build ]; then mkdir ../build; fi
	./patch_unpatch_script vuln
	$(MAKE) main TYPE=

main: main.o gpio.o bumper.o logging.o
	$(COMPILER) $(CFLAGS) -o ../build/program_c${TYPE} main.o gpio.o bumper.o logging.o

util.o: src/util.c
	$(COMPILER) -c -Iinc $(CFLAGS) src/util.c

logging.o: src/logging.c
	$(COMPILER) -Wall -c -Iinc $(CFLAGS) src/logging.c

main.o: src/main.c
	$(COMPILER) -c -Iinc $(CFLAGS) src/main.c

gpio.o: src/gpio.c
	$(COMPILER) -c -Iinc $(CFLAGS) src/gpio.c

bumper.o: src/bumper.c
	$(COMPILER) -c -Iinc $(CFLAGS) src/bumper.c

clean:
	rm -f *.o

.PHONY: all vuln patch clean
