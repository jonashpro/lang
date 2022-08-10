CXX=g++
CXXFLAGS=-Wall -Wextra -Wswitch-enum

all: vm.o
	$(CXX) $(CXXFLAGS) -o vm vm.o

vm.o: vm.cpp
	$(CXX) $(CXXFLAGS) -c -o vm.o vm.cpp

