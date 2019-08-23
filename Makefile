CPPFLAGS=-O3 -g -Wall -msse2 -msse -march=native -std=c++11 -maes
INCSRC=-I./src/cpp -I./lib/FiniteStateEntropy/lib
HELLMANSRC=-I./hellman_example/
INCTEST=-I./tests/cpp

# Compiled FiniteStateEntropy dependency
FSELIBDIR := ./lib/FiniteStateEntropy/lib
LIBFILES := $(wildcard $(FSELIBDIR)/*.h) $(wildcard $(FSELIBDIR)/*.c)
LIBOBJ := $(FSELIBDIR)/entropy_common.o $(FSELIBDIR)/fse_compress.o $(FSELIBDIR)/fse_decompress.o $(FSELIBDIR)/hist.o

SRCFILES := $(wildcard ./src/cpp/*.cpp) $(wildcard ./src/cpp/*.hpp)
TESTFILES := $(wildcard ./tests/cpp/*.cpp) $(wildcard ./tests/cpp/*.hpp)
HELLMANFILES := $(wildcard ./hellman_example/*.cpp) $(wildcard ./hellman_example/*.hpp)


main : $(SRCFILES) $(LIBFILES) $(LIBOBJ)
	g++ -o ProofOfSpace $(LIBOBJ) ./src/cpp/cli.cpp $(CPPFLAGS) $(INCSRC)

test : $(SRCFILES) $(TESTFILES) $(LIBFILES) ./tests/cpp/test-main.o $(LIBOBJ)
	g++ -o RunTests ./tests/cpp/test-main.o $(LIBOBJ) ./tests/cpp/test.cpp $(CPPFLAGS) $(INCSRC) $(INCTEST)

hellman: $(HELLMANFILES) $(LIBFILES) $(LIBOBJ)
	g++ -o HellmanAttacks $(LIBOBJ) ./hellman_example/cli.cpp $(CPPFLAGS) $(HELLMANSRC)

test-main : test-main.cpp
	g++ -o test-main.o ./tests/cpp/test-main.cpp $(CPPFLAGS) $(INCTEST)

lib/FiniteStateEntropy/lib/%.o : lib/FiniteStateEntropy/lib/%.c
	g++ -c -x c $< -o $@

clean :
	rm -f ./*.dat
	rm -f ./*.dat.tmp
	rm -rf ./*.o
	rm ./ProofOfSpace
	rm ./RunTests
	rm ./tests/cpp/test-main.o




