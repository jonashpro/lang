#ifndef _LOADER_HXX
#define _LOADER_HXX 1

#include <vector>

#include "error.hxx"
#include "vm_types.hxx"

std::vector<vm_instr> load_program_from_file(char *file);

#endif

