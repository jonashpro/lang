#include "include/stack.hxx"

StackValue *new_stack_value(StackValueType type)
{
	StackValue *stack_value = (StackValue*)malloc(sizeof(StackValue));
	stack_value->type = type;

	return stack_value;
}

StackValue *new_int_stack_value(vm_int value)
{
	StackValue *stack_value = new_stack_value(TYPE_INT);
	stack_value->int_value = value;

	return stack_value;
}

StackValue *new_float_stack_value(vm_float value)
{
	StackValue *stack_value = new_stack_value(TYPE_FLOAT);
	stack_value->float_value = value;

	return stack_value;
}

StackValue *new_string_stack_value(std::string value)
{
	StackValue *stack_value = new_stack_value(TYPE_STRING);
	stack_value->string_value = value;

	return stack_value;
}

