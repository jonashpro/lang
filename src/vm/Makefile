CXX=g++
CXXFLAGS=-Wall -Wextra

OBJ_FILES=main.o vm.o loader.o stack.o heap.o

all: $(OBJ_FILES)
	$(CXX) $(CXXFLAGS) -o vm $(OBJ_FILES)

main.o: main.cxx
	$(CXX) $(CXXFLAGS) -c -o main.o main.cxx

vm.o: vm.cxx
	$(CXX) $(CXXFLAGS) -c -o vm.o vm.cxx

loader.o: loader.cxx
	$(CXX) $(CXXFLAGS) -c -o loader.o loader.cxx

stack.o: stack.cxx
	$(CXX) $(CXXFLAGS) -c -o stack.o stack.cxx

heap.o: heap.cxx
	$(CXX) $(CXXFLAGS) -c -o heap.o heap.cxx

clean: *.o
	rm *.o

