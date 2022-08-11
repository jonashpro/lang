# Lang VM
# Author: Jonas

# This VM is only temporary.

import sys

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

	def run(self):
		while True:
			instr = self.get_instruction()

			if instr == OpCodes.HLT:
				break

			elif instr == OpCodes.LDI:
				self.stack.append(self.get_int32())

			elif instr == OpCodes.LDF:
				raise NotImplementedError

			elif instr == OpCodes.LDS:
				self.stack.append(self.data[self.get_int32()])

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

				sp = self.call_stack.pop()
				self.pc = self.call_stack.pop()

				while len(self.stack) != sp:
					self.stack.pop()

			elif instr == OpCodes.WRT:
				print(self.stack.pop())

			elif instr == OpCodes.LET:
				name = self.get_int32()
				self.variables[-1][name] = self.get_free_address()

			elif instr == OpCodes.STO:
				name = self.get_int32()
				self.memory[self.variables[-1][name]] = self.stack.pop()

			elif instr == OpCodes.LDV:
				name = self.get_int32()
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

			else:
				raise NotImplementedError(f'INSTRUCTION: {instr}')		

