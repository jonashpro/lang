#ifndef _VM_HXX
#define _VM_HXX 1

#include <string>
#include <vector>
#include <iostream>
#include <cassert>
#include <map>

#include "stack.hxx"
#include "vm_types.hxx"
#include "error.hxx"
#include "opcodes.hxx"
#include "heap.hxx"

class VM
{
	private:
		std::vector<vm_instr> code_section;
		std::vector<std::string> data_section;
		std::vector<vm_instr> program;

		StackValue *stack[STACK_MAX];
		vm_int sp = 0;  // stack pointer

		// calls save: last pc, last sp
		vm_int call_stack[CALL_STACK_MAX];
		vm_int call_sp = 0;  // call stack pointer

		int pc = 0;  // program counter

		void check_and_remove_signature();
		void get_data_section();
		void get_code_section();

		void add_variable(vm_int name, vm_int address);
		bool variable_exists(vm_int variable_name);
		vm_int get_variable_address(vm_int variable_name);

		vm_int get_vm_int();
		vm_float get_vm_float();

		Heap *heap = new_heap();

		// when start a call, the top of variables stack is duplicated,
		// and when return, droped.
		// variables[escope][NAME OF VARIABLE] = ADDRESS OF VARIABLE
		std::vector<std::map<vm_int, vm_int>> variables;

	public:
		VM(std::vector<vm_instr> _program);
		vm_int run();

};

#endif

