# Lang Compiler
# Author: Jonas

# TODO:
# - Move disassembler to VM as method

import struct

from code_generator import VM_SIGNATURE
from opcodes import OpCodes


class Disassembler:
	def __init__(self, code):
		self.code = code

		self.check_and_remove_signature()

		self.data_section = self.get_data_section()

		self.opcodes_as_string = {
			OpCodes.HLT: 'hlt',
			OpCodes.LDI: 'ldi',
			OpCodes.LDF: 'ldf',
			OpCodes.LDS: 'lds',
			OpCodes.STO: 'sto',
			OpCodes.LDV: 'ldv',
			OpCodes.JMP: 'jmp',
			OpCodes.JPT: 'jpt',
			OpCodes.JPF: 'jpf',
			OpCodes.CAL: 'cal',
			OpCodes.RET: 'ret',
			OpCodes.LDN: 'ldn',
			OpCodes.NOP: 'nop',
			OpCodes.WRT: 'wrt',
			OpCodes.ADD: 'add',
			OpCodes.SUB: 'sub',
			OpCodes.MUL: 'mul',
			OpCodes.DIV: 'div',
			OpCodes.EQ: 'eq',
			OpCodes.NE: 'ne',
			OpCodes.LT: 'lt',
			OpCodes.LE: 'le',
			OpCodes.GT: 'gt',
			OpCodes.GE: 'ge',
			OpCodes.NOT: 'not',
			OpCodes.AND: 'and',
			OpCodes.OR: 'or',
			OpCodes.NEG: 'neg',
			OpCodes.DUP: 'dup',
			OpCodes.INC: 'inc',
			OpCodes.DEC: 'dec',
			OpCodes.LET: 'let',
			OpCodes.BNT: 'bnt',
			OpCodes.SHL: 'shl',
			OpCodes.SHR: 'shr',
			OpCodes.XOR: 'xor',
			OpCodes.BOR: 'bor',
			OpCodes.BND: 'bnd',
			OpCodes.EXT: 'ext'
		}

		self.current_address = -1

	def check_and_remove_signature(self):
		if self.code[:len(VM_SIGNATURE)] == VM_SIGNATURE:
			self.code = self.code[len(VM_SIGNATURE):]

		else:
			print('invalid file format', file=sys.stderr)
			exit(1)

	def get_instruction(self):
		self.current_address += 1
		return self.code.pop(0)

	def get_data_section(self):
		data_section = []

		while self.code[0] != 0:
			current_data = ''

			while self.code[0] != 0:
				current_data += chr(self.code[0])
				self.code.pop(0)

			self.code.pop(0)

			data_section.append(current_data)

		self.code.pop(0)

		return data_section
	
	def get_int32(self):
		byte1 = self.get_instruction()
		byte2 = self.get_instruction()
		byte3 = self.get_instruction()
		byte4 = self.get_instruction()

		return (byte1 * 256 * 256 * 256) \
			+  (byte2 * 256 * 256)        \
			+  (byte3 * 256)              \
			+  (byte4)

	def get_float(self):
		bytes_ = []

		for byte in range(8):
			bytes_.append(self.get_instruction())

		return struct.unpack('!d', bytes(bytes_))[0]

	def formated_number(self, number):
		if number < 10:
			number = f'  {number}'

		elif number < 100:
			number = f' {number}'

		else:
			number = f'{number}'

		return f' \033[1;32m{number}\033[0;0m'

	def formated_comment(self, comment):
		return f'\033[1;30m// {comment}\033[0;0m'

	def disassemble(self):
		print(self.code)
		if self.data_section:
			print('DATA')

			for number, data in enumerate(self.data_section):
				print(f' {self.formated_number(number)}  {data}')

			print()
		
		print('CODE')
		while self.code:
			instruction = self.get_instruction()

			print(
				f' {self.formated_number(self.current_address)}  ',
				end='',
			)

			if instruction in (
					OpCodes.LDI,
					OpCodes.JMP,
					OpCodes.JPT,
					OpCodes.JPF,
					OpCodes.CAL,
				):

				print(self.opcodes_as_string[instruction], end=' ')
				int32 = self.get_int32()
				print(self.formated_number(int32))

			elif instruction == OpCodes.LDS:
				print(self.opcodes_as_string[instruction], end=' ')
				data_number = self.get_int32()
				print(self.formated_number(data_number), end=' ')
				print(
					self.formated_comment(
						f'string "{self.data_section[data_number]}"'
					),
				)

			elif instruction in (OpCodes.STO, OpCodes.LDV, OpCodes.LET):
				print(self.opcodes_as_string[instruction], end=' ')
				data_number = self.get_int32()
				print(self.formated_number(data_number), end=' ')
				print(
					self.formated_comment(
						f'variable {self.data_section[data_number]}',
					),
				)

			else:
				print(self.opcodes_as_string[instruction])

