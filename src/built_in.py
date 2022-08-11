# Lang Compiler
# Author: Jonas

from opcodes import OpCodes


def built_in_function(number_of_arguments, instruction):
	return (number_of_arguments, instruction)


built_in_functions = {
	'write':   built_in_function(1, OpCodes.WRT),
	'exit':    built_in_function(1, OpCodes.EXT),
}

