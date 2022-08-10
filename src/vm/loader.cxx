#include "include/loader.hxx"

std::vector<vm_instr> load_program_from_file(char *file)
{
	std::vector<vm_instr> program;

	FILE *fp = fopen(file, "rb");

	if (fp == NULL)
		NO_SUCH_FILE_ERROR(file);

	vm_instr instr;

	while ((char)(instr = getc(fp)) != EOF)
		program.push_back(instr);

	return program;
}

