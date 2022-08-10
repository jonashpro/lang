// Lang Virtual Machine
// Author: Jonas

#include <iostream>
#include <vector>
#include <string>
#include <cstdio>
#include <cassert>

#define VM_INT int32_t
#define VM_FLOAT float

#define STACK_MAX      4096
#define CALL_STACK_MAX 1024

#define ARRAY_SIZE(array) (sizeof(array) * sizeof((array)[0]))

// error
#define ERROR(fmt, ...) { \
	fprintf(stderr, "PANIC ERROR: "); \
	fprintf(stderr, fmt, ##__VA_ARGS__); \
	exit(1); \
}

void invalid_file_format_error()
{
	ERROR("invalid file format\n");
}

void stack_overflow_error()
{
	ERROR("stack overflow\n");
}

void stack_underflow_error()
{
	ERROR("stack underflow\n");
}

// opcodes
typedef enum
{
	HLT = 0x00,
	LDI = 0x01,
	LDF = 0x02,
	LDS = 0x03,
	STO = 0x04,
	LDV = 0x05,
	JMP = 0x06,
	JPT = 0x07,
	JPF = 0x08,
	CAL = 0x09,
	RET = 0x0a,
	LDN = 0x0b,
	NOP = 0x0c,
	WRT = 0x0d
} OpCode;

// stack
typedef enum
{
	ST_NIL,
	ST_INT,
	ST_FLOAT,
	ST_STRING
} StackType;

struct StackValue
{
	StackType type;

	VM_INT int_value;
	VM_FLOAT float_value;
	std::string string_value;

	void print()
	{
		switch (type)
		{
			case ST_NIL:
				std::cout << "nil";
				break;

			case ST_INT:
				std::cout << int_value;
				break;

			case ST_FLOAT:
				std::cout << float_value;
				break;

			case ST_STRING:
				std::cout << string_value;
				break;

			default:
				assert(false && "unreachable");
		}
	}

	bool to_bool()
	{
		switch (type)
		{
			case ST_NIL:
				return false;

			case ST_INT:
				return int_value != 0 ? true : false;

			case ST_FLOAT:
				return float_value != 0 ? true : false;

			case ST_STRING:
				return string_value.length() > 0 ? true : false;

			default:
				assert(false && "unreachable");
		}
	}
};

StackValue *new_stack_value(StackType type)
{
	StackValue *value = (StackValue*)malloc(sizeof(StackValue));
	value->type = type;
	return value;
}

StackValue *new_int_stack_value(VM_INT int_value)
{
	StackValue *value = new_stack_value(ST_INT);
	value->int_value = int_value;
	return value;
}

StackValue *new_string_stack_value(std::string string_value)
{
	StackValue *value = new_stack_value(ST_STRING);
	value->string_value = string_value;
	return value;
}

// vm
class VM
{
	private:
		std::vector<uint8_t> code;
		std::vector<std::string> data_section;
	
		StackValue *stack[STACK_MAX];
		VM_INT sp = 0;  // stack pointer

		// last_address, last_sp
		VM_INT call_stack[CALL_STACK_MAX];
		VM_INT call_sp = 0;  // call stack pointer

		bool running = false;

		VM_INT pc = 0;  // program counter

		// index: variable name -> address
		std::vector<std::vector<VM_INT>> variables;

		void check_and_remove_signature()
		{
			uint8_t signature[] = {'.', 'l', 'n', 'g', 0};

			if (code.size() < ARRAY_SIZE(signature))
				invalid_file_format_error();

			for (uint8_t byte: signature)
			{
				if (code[0] != byte)
					invalid_file_format_error();

				code.erase(code.begin());
			}
		}

		void get_data_section()
		{
			// 0 -> end of data section
			while (code[0] != 0)
			{
				std::string current_data = "";

				// 0 -> end of data
				while (code[0] != 0)
				{
					current_data += code[0];
					code.erase(code.begin());
				}

				code.erase(code.begin()); // 0
				data_section.push_back(current_data);
			}

			code.erase(code.begin()); // 0
		}

		VM_INT get_int()
		{
			uint8_t byte1 = code[pc++];
			uint8_t byte2 = code[pc++];
			uint8_t byte3 = code[pc++];
			uint8_t byte4 = code[pc++];

			return (byte1 * 256 * 256 * 256) \
					+ (byte2 * 256 * 256) \
					+ (byte3 * 256) \
					+ (byte4);
		}

		void add_variable(VM_INT name, VM_INT address)
		{
			if ((size_t)name >= variables[variables.size() - 1].size())
				variables[variables.size() - 1].push_back(address);
		
			else
				variables[variables.size() - 1][name] = address;
		}

	public:
		VM(std::vector<uint8_t> _code)
		{
			code = _code;
			check_and_remove_signature();
			get_data_section();
		}

		int run()
		{
			running = true;
			pc = 0;

			while (running)
			{
				OpCode instr = (OpCode)code[pc++];

				switch (instr)
				{
					case HLT:
					{
						running = false;
						break;
					}

					case LDI:
					{
						if (sp == STACK_MAX)
							stack_overflow_error();

						stack[sp++] = new_int_stack_value(get_int());
						break;
					}

					case LDF:
					{
						assert(false && "not implemented");
						break;
					}

					case LDS:
					{
						if (sp == STACK_MAX)
							stack_overflow_error();

						stack[sp++] = new_string_stack_value(
							data_section[get_int()]
						);
						break;
					}

					case STO:
					{
						add_variable(get_int(), sp - 1);
						break;
					}

					case LDV:
					{
						stack[sp++] = (
							stack[variables[variables.size() - 1][get_int()]]
						);
						break;
					}

					case JMP:
					{
						pc = get_int();
						break;
					}

					case JPT:
					{
						StackValue *condition = stack[--sp];
						VM_INT new_address = get_int();

						if (condition->to_bool())
							pc = new_address;

						break;
					}

					case JPF:
					{
						StackValue *condition = stack[--sp];
						VM_INT new_address = get_int();

						if (!condition->to_bool())
							pc = new_address;

						break;
					}

					case CAL:
					{
						std::vector<VM_INT> new_scope;

						if (variables.size() != 0)
						{
							std::copy(
								variables[variables.size() - 1].begin(),
								variables[variables.size() - 1].end(),
								std::back_inserter(new_scope)
							);
						}

						variables.push_back(new_scope);

						VM_INT new_address = get_int();
						call_stack[call_sp++] = pc;
						call_stack[call_sp++] = sp;

						pc = new_address;
						break;
					}

					case RET:
					{
						StackValue *return_value = stack[--sp];
						sp = call_stack[--call_sp];
						pc = call_stack[--call_sp];

						stack[sp++] = return_value;
						break;
					}

					case LDN:
					{
						stack[sp++] = new_stack_value(ST_NIL);
						break;
					}

					case NOP:
						break;

					case WRT:
					{
						stack[--sp]->print();
						break;
					}

					default:
						assert(false && "unreachable");
				}
			}

			return 0;
		}
};

// load program
std::vector<uint8_t> load_program(char *file_name)
{
	std::vector<uint8_t> code;

	FILE *fp = fopen(file_name, "rb");

	if (fp == NULL)
	{
		std::cerr << "no such file " << file_name << std::endl;
		exit(1);
	}

	char byte;

	while ((byte = getc(fp)) != EOF)
		code.push_back((uint8_t)byte);
	
	return code;
}

int main(int argc, char **argv)
{
	if (argc < 2)
	{
		std::cerr << "usage: " << argv[0] << " <file>" << std::endl;
		exit(1);
	}
	
	VM vm(load_program(argv[1]));
	return vm.run();
}

