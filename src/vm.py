# Lang VM
# Author: Jonas

# This VM is only temporary.

import struct
import sys

from built_in import built_in_variables
from code_generator import VM_SIGNATURE
from opcodes import OpCodes

MEMORY_SIZE = 1024

# errors
ILLEGAL_OPERATION_ERROR = 'illegal operation: %s %s %s'
DIVISION_BY_ZERO_ERROR = 'division by zero'
NEGATIVE_SHIFT_COUNT_ERROR = 'negative shift count'
VALUE_IS_NOT_SUBSCRIPTABLE = '%s value is not subscriptable'
INVALID_INDEX_ERROR = 'invalid index'
LIST_INDEX_OUT_OF_RANGE_ERROR = 'list index out of range error'


class VM:
	def __init__(self, code):
		self.code = code
		self.data = []

		self.check_and_remove_signature()
		self.get_data()
		self.pc = 0
		self.stack = []
		self.call_stack = []

		self.memory = [0] * MEMORY_SIZE
		self.memory_table = [False] * MEMORY_SIZE

		self.variables = [{}]

		self.file_name = None
		self.line = None

		self.binary_operations = {
			OpCodes.ADD: lambda a, b: a + b,
			OpCodes.SUB: lambda a, b: a - b,
			OpCodes.MUL: lambda a, b: a * b,
			OpCodes.DIV: lambda a, b: a / b,
			OpCodes.EQ: lambda a, b: int(a == b),
			OpCodes.LT: lambda a, b: int(a < b),
			OpCodes.LE: lambda a, b: int(a <= b),
			OpCodes.GT: lambda a, b: int(a > b),
			OpCodes.GE: lambda a, b: int(a >= b),
			OpCodes.AND: lambda a, b: int(a and b),
			OpCodes.OR: lambda a, b: int(a or b),
			OpCodes.XOR: lambda a, b: a ^ b,
			OpCodes.SHL: lambda a, b: a << b,
			OpCodes.SHR: lambda a, b: a >> b,
			OpCodes.BOR: lambda a, b: a | b,
			OpCodes.BND: lambda a, b: a & b,
			OpCodes.NE: lambda a, b: a != b,
		}

		self.binary_operations_as_str = {
			OpCodes.ADD: '+',
			OpCodes.SUB: '-',
			OpCodes.MUL: '*',
			OpCodes.DIV: '/',
			OpCodes.EQ: '==',
			OpCodes.LT: '<',
			OpCodes.LE: '<=',
			OpCodes.GT: '>',
			OpCodes.GE: '>=',
			OpCodes.AND: '&&',
			OpCodes.OR: '||',
			OpCodes.XOR: '^',
			OpCodes.SHL: '<<',
			OpCodes.SHR: '>>',
			OpCodes.BOR: '|',
			OpCodes.BND: '&',
			OpCodes.NE: '!=',
		}

		self.unary_operations = {
			OpCodes.NOT: lambda a: not a,
			OpCodes.NEG: lambda a: -a,
			OpCodes.BNT: lambda a: ~a,
		}

		self.files = {
			'stdout': sys.stdout,
			'stdin': sys.stdin,
			'stderr': sys.stderr,
		}
	
	def check_and_remove_signature(self):
		if self.code[:len(VM_SIGNATURE)]:
			self.code = self.code[len(VM_SIGNATURE):]

		else:
			print('invalid file format', file=sys.stderr)
			exit(1)

	def get_free_address(self):
		address = 0
		
		while address < MEMORY_SIZE:
			if self.memory_table[address] == False:
				self.memory_table[address] = True
				return address

			address += 1

		self.panic_error('memory overflow')

	def free(self, address):
		self.memory_table[address] = False

	def get_data(self):
		while self.code[0] != 0:
			current_data = ''

			while self.code[0] != 0:
				current_data += chr(self.code[0])
				self.code.pop(0)

			self.code.pop(0)

			self.data.append(current_data)

		self.code.pop(0)
	
	def get_instruction(self):
		self.pc += 1
		return self.code[self.pc-1]

	def get_int32(self):
		byte1 = self.get_instruction()
		byte2 = self.get_instruction()
		byte3 = self.get_instruction()
		byte4 = self.get_instruction()

		return (byte1 * 256 * 256 * 256) \
		     + (byte2 * 256 * 256      ) \
		     + (byte3 * 256            ) \
		     + (byte4                  )
	
	def get_float(self):
		bytes_ = []

		for byte in range(8):
			bytes_.append(self.get_instruction())

		return struct.unpack('!d', bytes(bytes_))[0]

	def panic_error(self, error):
		"""Emit a panic error and exit."""

		print(
			f'{self.file_name}:%.2d: panic: {error}' %self.line,
			file=sys.stderr,
		)

		while self.call_stack:
			self.call_stack.pop()  # sp
			self.call_stack.pop()  # pc
			line = self.call_stack.pop()
			file_name = self.call_stack.pop()
			function = self.call_stack.pop()
			print(f'  {file_name}:%.2d: call function {function}' %line)

		exit(1)

	def protected_run(self):
		"""Runs with exceptions handling."""

		try:
			self.run()

		except (KeyboardInterrupt, EOFError):
			exit(0)

	def get_list(self, number_of_values):
		list_ = []

		for _ in range(number_of_values):
			list_.append(self.stack.pop())

		return list_

	def run(self):
		while True:
			instr = self.get_instruction()
			
			if instr == OpCodes.HLT:
				break

			elif instr == OpCodes.POS:
				self.file_name = self.data[self.get_int32()]
				self.line = self.get_int32()

			elif instr == OpCodes.LDI:
				self.stack.append(self.get_int32())

			elif instr == OpCodes.LDF:
				self.stack.append(self.get_float())

			elif instr == OpCodes.LDS:
				self.stack.append(self.data[self.get_int32()])

			elif instr == OpCodes.LDL:
				self.stack.append(self.get_list(self.get_int32()))

			elif instr == OpCodes.JMP:
				self.pc = self.get_int32()

			elif instr == OpCodes.JPT:
				address = self.get_int32()
				if self.stack.pop(): self.pc = address

			elif instr == OpCodes.JPF:
				address = self.get_int32()
				if not self.stack.pop(): self.pc = address

			elif instr == OpCodes.LDN:
				self.stack.append(None)

			elif instr == OpCodes.NOP:
				continue

			elif instr == OpCodes.CAL:
				self.variables.append(self.variables[-1].copy())
				name = self.data[self.get_int32()]
				address = self.get_int32()
				self.call_stack.append(name)
				self.call_stack.append(self.file_name)
				self.call_stack.append(self.line)
				self.call_stack.append(self.pc)
				self.call_stack.append(len(self.stack))
				self.pc = address

			elif instr == OpCodes.RET:
				for variable in self.variables[-1]:
					self.free(self.variables[-1][variable])

				self.variables.pop()
		
				# if the function no return
				if not self.stack:
					return_value = None

				else:
					return_value = self.stack.pop()

				sp = self.call_stack.pop()
				self.pc = self.call_stack.pop()
				line = self.call_stack.pop()
				file_name = self.call_stack.pop()
				name = self.call_stack.pop()

				while len(self.stack) > sp:
					self.stack.pop()

				self.stack.append(return_value)

			elif instr == OpCodes.WRT:
				value = self.stack.pop()

				if value is None:
					value = 'nil'

				print(value)

			elif instr == OpCodes.LET:
				name = self.get_int32()
				self.variables[-1][name] = self.get_free_address()

			elif instr == OpCodes.STO:
				name = self.get_int32()
				value = self.stack.pop()
				self.memory[self.variables[-1][name]] = value

			elif instr == OpCodes.LDV:
				name = self.get_int32()

				if self.data[name] in built_in_variables:
					self.stack.append(built_in_variables[self.data[name]])
				else:
					self.stack.append(self.memory[self.variables[-1][name]])

			elif instr in self.binary_operations:
				b = self.stack.pop()
				a = self.stack.pop()

				# check if operation is valid
				try:
					a + b
				except TypeError:
					self.panic_error(ILLEGAL_OPERATION_ERROR %(
						type(a).__name__,
						self.binary_operations_as_str[instr],
						type(b).__name__,
					))

				if instr == OpCodes.DIV and b == 0:
					self.panic_error(DIVISION_BY_ZERO_ERROR)

				elif instr in (OpCodes.SHL, OpCodes.SHR) and b < 0:
					self.panic_error(NEGATIVE_SHIFT_COUNT_ERROR)

				self.stack.append(self.binary_operations[instr](a, b))

			elif instr in self.unary_operations:
				a = self.stack.pop()
				self.stack.append(self.unary_operations[instr](a))

			elif instr == OpCodes.DUP:
				self.stack.append(self.stack[-1])

			elif instr == OpCodes.INC:
				self.stack[-1] += 1

			elif instr == OpCodes.DEC:
				self.stack[-1] -= 1

			elif instr == OpCodes.EXT:
				exit(self.stack.pop())

			elif instr == OpCodes.POP:
				self.stack.pop()

			elif instr == OpCodes.GET:
				index = self.stack.pop()
				list_ = self.stack.pop()

				if not isinstance(list_, list):
					self.panic_error(VALUE_IS_NOT_SUBSCRIPTABLE %(
						type(list_).__name__
					))

				if not isinstance(index, int):
					self.panic_error(INVALID_INDEX_ERROR)

				if index > len(list_) - 1:
					self.panic_error(LIST_INDEX_OUT_OF_RANGE_ERROR)

				self.stack.append(list_[index])

			elif instr == OpCodes.APD:
				list_ = self.stack.pop()
				value = self.stack.pop()
				list_.append(value)

			elif instr == OpCodes.LPP:
				list_ = self.stack.pop()
				index = self.stack.pop()
				list_.pop(index)

			elif instr == OpCodes.LEN:
				self.stack.append(len(self.stack.pop()))

			elif instr == OpCodes.CPY:
				self.stack.append(self.stack.pop().copy())

			elif instr == OpCodes.TYP:
				value = self.stack.pop()
				typ = type(value).__name__
				self.stack.append(typ)

			elif instr == OpCodes.SET:
				list_ = self.stack.pop()
				index = self.stack.pop()
				value = self.stack.pop()
				list_[index] = value

			elif instr == OpCodes.FOP:
				file_name = self.stack.pop()
				open_type = self.stack.pop()

				try:
					self.stack.append(open(file_name, open_type))

				except FileNotFoundError:
					self.stack.append(None)

			elif instr == OpCodes.FWT:
				file = self.stack.pop()
				text = self.stack.pop()
				file.write(text)

			elif instr == OpCodes.FRD:
				file = self.stack.pop()
				self.stack.append(file.read())

			elif instr == OpCodes.FCL:
				file = self.stack.pop()
				file.close()

			elif instr == OpCodes.FRL:
				file = self.stack.pop()
				self.stack.append(file.readline())

			else:
				raise NotImplementedError(f'INSTRUCTION: {instr}')		

	def disassemble(self):
		opcodes_as_string = {
			OpCodes.HLT: 'halt   ',
			OpCodes.LDI: 'iload  ',
			OpCodes.LDF: 'fload  ',
			OpCodes.LDS: 'sload  ',
			OpCodes.STO: 'store  ',
			OpCodes.LDV: 'vload  ',
			OpCodes.JMP: 'jump   ',
			OpCodes.JPT: 'jumpt  ',
			OpCodes.JPF: 'jumpf  ',
			OpCodes.CAL: 'call   ',
			OpCodes.RET: 'ret    ',
			OpCodes.LDN: 'nload  ',
			OpCodes.NOP: 'nop    ',
			OpCodes.WRT: 'write  ',
			OpCodes.ADD: 'add    ',
			OpCodes.SUB: 'sub    ',
			OpCodes.MUL: 'mul    ',
			OpCodes.DIV: 'div    ',
			OpCodes.EQ:  'eq     ',
			OpCodes.NE:  'ne     ',
			OpCodes.LT:  'lt     ',
			OpCodes.LE:  'le     ',
			OpCodes.GT:  'gt     ',
			OpCodes.GE:  'ge     ',
			OpCodes.NOT: 'not    ',
			OpCodes.AND: 'and    ',
			OpCodes.OR:  'or     ',
			OpCodes.NEG: 'neg    ',
			OpCodes.DUP: 'dup    ',
			OpCodes.INC: 'inc    ',
			OpCodes.DEC: 'dec    ',
			OpCodes.LET: 'let    ',
			OpCodes.BNT: 'btw_not',
			OpCodes.SHL: 'shl    ',
			OpCodes.SHR: 'shr    ',
			OpCodes.XOR: 'xor    ',
			OpCodes.BOR: 'btw_or ',
			OpCodes.BND: 'btw_and',
			OpCodes.EXT: 'exit   ',
			OpCodes.POP: 'pop    ',
			OpCodes.LDL: 'lload  ',
			OpCodes.GET: 'get    ',
			OpCodes.APD: 'append ',
			OpCodes.LPP: 'lpop   ',
			OpCodes.LEN: 'length ',
			OpCodes.CPY: 'copy   ',
			OpCodes.TYP: 'type   ',
			OpCodes.SET: 'set    ',
			OpCodes.FOP: 'fopen  ',
			OpCodes.FWT: 'fwrite ',
			OpCodes.FRD: 'fread  ',
			OpCodes.FCL: 'fclose ',
			OpCodes.FRL: 'freadln',
			OpCodes.POS: 'pos    ',
		}
	
		while self.pc < len(self.code):
			instr = self.get_instruction()

			pc = self.pc - 1  # pc points to next instr

			if pc < 10:
				pc_as_str = f'  {pc}'

			elif pc < 100:
				pc_as_str = f' {pc}'

			else:
				pc_as_str = f'{pc}'

			if instr == OpCodes.POS:
				self.file_name = self.data[self.get_int32()]
				self.line = self.get_int32()
				print(f'\033[1;32m{self.file_name}:%.2d:\033[0;0m' %self.line)
				continue

			else:
				print(f'  {pc_as_str}: {opcodes_as_string[instr]} ', end='')

			if instr in (
					OpCodes.LDI,
					OpCodes.JMP,
					OpCodes.JPT,
					OpCodes.JPF,
				):

				print(self.get_int32())

			elif instr == OpCodes.LDS:
				string = self.data[self.get_int32()]
				string = string.replace('\n', '\\n')
				string = string.replace('\r', '\\r')
				print('"' + string + '"')

			elif instr == OpCodes.CAL:
				name = self.data[self.get_int32()]
				address = self.get_int32()
				print(f'{name} // address {address}')

			elif instr == OpCodes.LDF:
				print(self.get_float())

			elif instr == OpCodes.LDL:
				print(self.get_int32())

			elif instr in (OpCodes.STO, OpCodes.LDV, OpCodes.LET):
				print(self.data[self.get_int32()])

			else:
				print()

