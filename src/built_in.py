# Lang Compiler
# Author: Jonas

from opcodes import OpCodes


def built_in_function(number_of_arguments, instruction):
	return (number_of_arguments, instruction)


built_in_functions = {
	'write':   built_in_function(1, OpCodes.WRT),  # (value)
	'exit':    built_in_function(1, OpCodes.EXT),  # (exit_code)
	'append':  built_in_function(2, OpCodes.APD),  # (list, value)
	'pop':     built_in_function(2, OpCodes.LPP),  # (list, index)
	'length':  built_in_function(1, OpCodes.LEN),  # (list)
	'copy':    built_in_function(1, OpCodes.CPY),  # (list)
	'type':    built_in_function(1, OpCodes.TYP),  # (value)
	'set':     built_in_function(3, OpCodes.SET),  # (list,index,value)
	'fopen':   built_in_function(2, OpCodes.FOP),  # (filename, type)
	'fwrite':  built_in_function(2, OpCodes.FWT),  # (file, text)
	'fread':   built_in_function(1, OpCodes.FRD),  # (file)
	'fclose':  built_in_function(1, OpCodes.FCL),  # (file)
}

