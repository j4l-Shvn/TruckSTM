
# all: vuln one_liner recursive iterative
# 	@echo Compiling all binaries

all: vuln
	@echo Compiling all binaries

vuln:
	if [ ! -d build ]; then mkdir build; fi
	@echo Compiling vulnerable binaries
	$(MAKE) -C program_c main -e TYPE=.gcc.vuln
	$(MAKE) -C program_c clean
	$(MAKE) -C program_c main -e TYPE=.clang.vuln COMPILER=clang
	$(MAKE) -C program_c clean


one_liner:
	if [ ! -d build ]; then mkdir build; fi
	@echo Compiling one_liner patched binaries
	patch program_c/src/main.c program_c/src/one_line.patch
	$(MAKE) -C program_c main -e TYPE=.gcc.one_line
	$(MAKE) -C program_c clean
	$(MAKE) -C program_c main -e TYPE=.clang.one_line COMPILER=clang
	$(MAKE) -C program_c clean
	patch program_c/src/main.c program_c/src/one_line.patch -R

recursive:
	if [ ! -d build ]; then mkdir build; fi
	@echo Compiling recursive patched binaries
	patch program_c/src/main.c program_c/src/recursive.patch
	$(MAKE) -C program_c main -e TYPE=.gcc.recursive
	$(MAKE) -C program_c clean
	$(MAKE) -C program_c main -e TYPE=.clang.recursive COMPILER=clang
	$(MAKE) -C program_c clean
	patch program_c/src/main.c program_c/src/recursive.patch -R

iterative:
	if [ ! -d build ]; then mkdir build; fi
	@echo Compiling iterative patched binaries
	patch program_c/src/main.c program_c/src/iterative.patch
	$(MAKE) -C program_c main -e TYPE=.gcc.iterative
	$(MAKE) -C program_c clean
	$(MAKE) -C program_c main -e TYPE=.clang.iterative COMPILER=clang
	$(MAKE) -C program_c clean
	patch program_c/src/main.c program_c/src/iterative.patch -R

clean:
	rm build/*

.PHONY: all vuln patch clean
