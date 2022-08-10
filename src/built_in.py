# Lang Compiler
# Author: Jonas

from opcodes import OpCodes

#                 number of arguments, instruction
BUILT_IN_WRITE = (1,                   OpCodes.WRT)

built_in_functions = {
	'write': BUILT_IN_WRITE,
}

