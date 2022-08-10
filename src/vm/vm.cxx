#include "include/vm.hxx"

#define ARRAY_SIZE(array) (sizeof(array) * sizeof((array)[0]))

VM::VM(std::vector<vm_instr> _program)
{
	program = _program;
	check_and_remove_signature();

	get_data_section();
	get_code_section();

	heap->start();
}

vm_int VM::run()
{
	pc = 0;
	bool running = true;

	while (running)
	{
		vm_instr instr = code_section[pc++];

		std::cout << instr;

		if (instr == OP_HLT)
			running = false;

		else if (instr == OP_LDI)
		{
			if (sp == STACK_MAX)
				STACK_OVERFLOW_ERROR;

			stack[sp++] = new_int_stack_value(get_vm_int());
		}

		else if (instr == OP_LDF)
		{
			if (sp == STACK_MAX)
					STACK_OVERFLOW_ERROR;

			stack[sp++] = new_float_stack_value(get_vm_float());
		}

		else if (instr == OP_LDS)
		{
			if (sp == STACK_MAX)
				STACK_OVERFLOW_ERROR;

			stack[sp++] = new_string_stack_value(data_section[get_vm_int()]);
		}

		else if (instr == OP_STO)
		{
			if (sp == 0)
				STACK_UNDERFLOW_ERROR;

			vm_int variable_name = get_vm_int();

			if (!variable_exists(variable_name))
			{
				vm_int variable_address = heap->alloc();
				add_variable(variable_name, variable_address);
			}

			heap->heap[
				variables[variables.size() - 1][variable_name]
			] = stack[--sp];
		}

		else if (instr == OP_LDV)
		{
			stack[sp++] = heap->heap[
				variables[variables.size() - 1][get_vm_int()]
			];
		}

		else if (instr == OP_JMP)
		{
			pc = get_vm_int();
		}

		else if (instr == OP_NOP)
		{
			// do nothing
			continue;
		}

		else
			UNKNOWN_INSTRUCTION_ERROR(instr);
	}

	return 0;
}

void VM::check_and_remove_signature()
{
	vm_instr signature[] = {'.', 'l', 'n', 'g', 0};

	// security check
	if (program.size() < ARRAY_SIZE(signature))
		INVALID_FILE_FORMAT_ERROR;

	for (vm_instr byte: signature)
	{
		if (byte != program[0])
			INVALID_FILE_FORMAT_ERROR;

		program.erase(program.begin());
	}
}

void VM::get_data_section()
{
	// the data section ends with 0 (NULL) char. each data stored
	// also ends with 0.

	// example of data section:
	// 0 hello
	// 1 hi
	// |---> hello0hi00
	//            ^  ^^--- end of data section
	//            |  |--- end of string hi
	//            |--- end of string hello

	// end of data section
	while (program[0] != 0)
	{
		std::string current_data = "";

		// end of current data
		while (program[0] != 0)
		{
			current_data += program[0];
			program.erase(program.begin());
		}

		program.erase(program.begin());
		data_section.push_back(current_data);
	}

	program.erase(program.begin());
}

void VM::get_code_section()
{
	// the others program informations has already been removed
	code_section = program;
}

vm_int VM::get_vm_int()
{
	vm_instr byte1 = code_section[pc++];
	vm_instr byte2 = code_section[pc++];
	vm_instr byte3 = code_section[pc++];
	vm_instr byte4 = code_section[pc++];

	return (byte1 * 256 * 256 * 256)
	     + (byte2 * 256 * 256)
	     + (byte3 * 256)
	     + (byte4);
}

void VM::add_variable(vm_int name, vm_int address)
{
	variables[variables.size() - 1][name] = address;
}

vm_float VM::get_vm_float()
{
	assert(false && "NOT IMPLEMENTED");
	return 0.0;
}

bool VM::variable_exists(vm_int variable_name)
{
	return variables[variables.size() - 1].count(variable_name);
}

vm_int VM::get_variable_address(vm_int variable_name)
{
	return variables[variables.size() - 1][variable_name];
}

