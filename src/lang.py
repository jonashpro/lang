#!/usr/bin/env python3

# Lang Compiler
# Author: Jonas

# TODO:
# - Optimizer

import sys

from lexer import Lexer
from parser_ import Parser
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
from disassembler import Disassembler


def read_file(file_name):
	with open(file_name, 'r') as f:
		source = f.read()
	
	return source


def compile_from_file(file_name):
	try:
		source = read_file(file_name)

	except FileNotFoundError:
		print(f'no such file {file_name}')
		exit(1)

	# lexer
	lexer = Lexer(file_name, source)
	tokens = lexer.lex()

	# parser
	parser = Parser(tokens)
	ast = parser.parse()

	# semantic analyzer
	sa = SemanticAnalyzer(ast)
	sa.analyze()

	# code generator
	cg = CodeGenerator(ast)
	code = cg.generate()

	return code


def usage():
	print(f'usage: {sys.argv[0]} <option> [file]')
	print('<option>')
	print('  build <file>      compile <file>')
	print('  asm   <file>      show assembly code of <file>')
	print('  help              this message')


def main():
	if len(sys.argv) < 2:
		usage()
		exit(1)

	option = sys.argv[1]

	if option == 'build':
		if len(sys.argv) < 3:
			print('build need <file>')
			usage()
			exit(1)

		file_name = sys.argv[2]
		code = compile_from_file(file_name)

		with open(file_name + '.vm', 'wb') as f:
			f.write(bytearray(code))

	elif option == 'asm':
		if len(sys.argv) < 3:
			print('asm need <file>')
			usage()
			exit(1)

		file_name = sys.argv[2]
		code = compile_from_file(file_name)
		disassembler = Disassembler(code)
		disassembler.disassemble()

	elif option == 'help':
		usage()

	else:
		print(f'unknown option: {option}')
		usage()
		exit(1)

if __name__ == '__main__':
	main()

