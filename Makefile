CXX ?= g++
CXXFLAGS = -O2 -std=c++17

all: bin/forca_bruta bin/held_karp

bin/forca_bruta: src/forca_bruta.cpp
	mkdir -p bin && $(CXX) $(CXXFLAGS) -o $@ $<

bin/held_karp: src/held_karp.cpp
	mkdir -p bin && $(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -rf bin
