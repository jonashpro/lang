CXX=g++
CXXFLAGS=-Wall -Wextra

OBJ_FILES=main.o

vm: $(OBJ_FILES)
	$(CXX) $(CXXFLAGS) -o vm $(OBJ_FILES)

main.o: main.cxx
	$(CXX) $(CXXFLAGS) -c -o main.o main.cxx

