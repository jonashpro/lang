#ifndef _STACK_HXX
#define _STACK_HXX 1

#include <cstdlib>
#include <string>

#include "vm_types.hxx"

#define STACK_MAX      4096
#define CALL_STACK_MAX 1024

typedef enum
{
	TYPE_NIL,
	TYPE_INT,
	TYPE_FLOAT,
	TYPE_STRING
} StackValueType;

struct StackValue
{
	StackValueType type;

	vm_int int_value;
	vm_float float_value;
	std::string string_value;
};

StackValue *new_stack_value(StackValueType type);
StackValue *new_int_stack_value(vm_int value);
StackValue *new_float_stack_value(vm_float value);
StackValue *new_string_stack_value(std::string value);

#endif

