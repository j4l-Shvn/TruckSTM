
challengename=AMP-Challenge-04-BBB-Address-Claim
# Make relative path from our root challenge dir
startloc=$(shell echo $(PWD) | sed -e 's@.*$(challengename)/@@' -e 's@[^/]\+/@../@g' -e 's@/[^/]\+$$@/..@')
munit_dir=$(startloc)/munit
munit_file=$(munit_dir)/munit
srcfiles=main.c bumper.c gpio.c
srcdir=$(shell find $(startloc) -type f -name $(word 2,$(srcfiles)) -exec dirname "{}" \;)
includedir=$(subst src,inc,$(srcdir))
list=$(subst /, ,$(shell echo $(PWD) | sed 's@.*$(challengename)/@@'))

CC=gcc
TESTENVIRONMENT:=
CFLAGS:=-I $(munit_dir) -I $(includedir) -g #-DTESTING
SRC:=$(addprefix $(srcdir)/,$(srcfiles))
OBJS:=$(patsubst %.c,%.o,$(SRC))
PATCH?=p_one_line

all: run

tests: $(munit_file).c $(OBJS) tests.c
	$(shell objcopy -N main $(srcdir)/main.o $(srcdir)/main.o)
	$(CC) $(CFLAGS) $^ -o $@

testspatched: mainpatch
	$(shell objcopy -N main $(srcdir)/main.o $(srcdir)/main.o)
	$(CC) $(CFLAGS) $(OBJS) $(munit_file).c tests.c -o $@

mainpatch: $(patsubst %main.o,,$(OBJS))
	$(shell cp $(srcdir)/main.c.$(PATCH) /tmp/main.c)
	$(CC) $(CFLAGS) $^ /tmp/main.c -c -o $(srcdir)/main.o

# Testing for this script
me:
	@echo PWD: $(PWD)
	@echo startloc: $(startloc)
	@echo SRC: $(SRC)
	@echo includedir: $(includedir)

clean:
	rm $(OBJS) tests testspatched
	
run: tests
	$(TESTENVIRONMENT) ./tests # --show-stderr --log-visible debug

.PHONY: all run me clean mainpatch
