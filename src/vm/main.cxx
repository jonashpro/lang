// Lang VM
// Author: Jonas

#include <iostream>
#include <vector>

#include "include/opcodes.hxx"
#include "include/vm.hxx"
#include "include/vm_types.hxx"
#include "include/loader.hxx"

void usage()
{
	std::cerr << "usage: vm <file>" << std::endl;
}

int main(int argc, char **argv)
{
	if (argc < 2)
	{
		usage();
		exit(1);
	}

	VM vm(load_program_from_file(argv[1]));

	return vm.run();
}

