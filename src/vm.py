# Lang VM
# Author: Jonas

# This VM is only temporary.

import struct
import sys

from built_in import built_in_variables
from code_generator import VM_SIGNATURE
from opcodes import OpCodes

MEMORY_SIZE = 1024


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

		print(f'panic: {error}', file=sys.stderr)
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
				address = self.get_int32()
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

				try:
					self.stack.append(self.binary_operations[instr](a, b))

				except Exception as err:
					self.panic_error(err)

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

				try:
					self.stack.append(list_[index])

				except IndexError:
					self.panic_error('invalid index')

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

				if isinstance(value, str):
					typ = 'string'

				elif isinstance(value, int):
					typ = 'int'

				elif isinstance(value, float):
					typ = 'float'

				elif isinstance(value, list):
					typ = 'list'

				else:
					typ = type(value)

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

			else:
				raise NotImplementedError(f'INSTRUCTION: {instr}')		

	def disassemble(self):
		opcodes_as_string = {
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
			OpCodes.EXT: 'ext',
			OpCodes.POP: 'pop',
			OpCodes.LDL: 'ldl',
			OpCodes.GET: 'get',
			OpCodes.APD: 'apd',
			OpCodes.LPP: 'lpp',
			OpCodes.LEN: 'len',
			OpCodes.CPY: 'cpy',
			OpCodes.TYP: 'typ',
			OpCodes.SET: 'set',
			OpCodes.FOP: 'fop',
			OpCodes.FWT: 'fwt',
			OpCodes.FRD: 'frd',
			OpCodes.FCL: 'fcl',
		}
	
		while self.pc < len(self.code):
			instr = self.get_instruction()

			pc = self.pc - 1  # pc points to the next instruction
			if pc < 10:
				pc_as_str = f' {pc}'
			else:
				pc_as_str = f'{pc}'

			print(f' {pc_as_str}: {opcodes_as_string[instr]} ', end='')

			if instr in (
					OpCodes.LDI,
					OpCodes.JMP,
					OpCodes.JPT,
					OpCodes.JPF,
					OpCodes.CAL,
				):

				print(self.get_int32())

			elif instr == OpCodes.LDS:
				string = self.data[self.get_int32()]
				string = string.replace('\n', '\\n')
				string = string.replace('\r', '\\r')
				print('"' + string + '"')

			elif instr == OpCodes.LDF:
				print(self.get_float())

			elif instr == OpCodes.LDL:
				print(self.get_int32())

			elif instr in (OpCodes.STO, OpCodes.LDV, OpCodes.LET):
				print(self.data[self.get_int32()])

			else:
				print()

