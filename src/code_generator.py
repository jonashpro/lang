# Lang Compiler
# Author: Jonas

import struct

from built_in import built_in_functions, built_in_variables
from node import *
from opcodes import OpCodes
from token_ import TokenType

VM_SIGNATURE = [ord(ch) for ch in '.lng\0']


class CodeGenerator:
	def __init__(self, ast):
		self.ast = ast

		self.position = -1
		self.current_node = None
		self.update_current_node()

		self.data_section = []
		self.code_section = []
		self.current_address = 0

		self.unary_instructions = {
			TokenType.OPERATOR_MINUS: OpCodes.NEG,
			TokenType.OPERATOR_NOT: OpCodes.NOT,
			TokenType.OPERATOR_BTW_NOT: OpCodes.BNT,
		}

		self.binary_instructions = {
			TokenType.OPERATOR_PLUS: OpCodes.ADD,
			TokenType.OPERATOR_MINUS: OpCodes.SUB,
			TokenType.OPERATOR_ASTERISK: OpCodes.MUL,
			TokenType.OPERATOR_SLASH: OpCodes.DIV,
			TokenType.OPERATOR_EQ: OpCodes.EQ,
			TokenType.OPERATOR_NE: OpCodes.NE,
			TokenType.OPERATOR_LT: OpCodes.LT,
			TokenType.OPERATOR_LE: OpCodes.LE,
			TokenType.OPERATOR_GT: OpCodes.GT,
			TokenType.OPERATOR_GE: OpCodes.GE,
			TokenType.OPERATOR_BTW_AND: OpCodes.BND,
			TokenType.OPERATOR_BTW_OR: OpCodes.BOR,
			TokenType.OPERATOR_BTW_XOR: OpCodes.XOR,
			TokenType.OPERATOR_BTW_SHL: OpCodes.SHL,
			TokenType.OPERATOR_BTW_SHR: OpCodes.SHR,
		}

		# function: address
		self.functions_address = {}

		# address to link: function to link
		self.address_to_link = {}

	def update_current_node(self):
		"""Update the current node."""

		self.position += 1

		if self.position < len(self.ast):
			self.current_node = self.ast[self.position]

		else:
			self.current_node = None

	def emit_instruction(self, instruction, custom_address=None):
		"""If parameter custom_address is None, emit in current
		address, else, emit in custom_address."""

		if custom_address is not None:
			self.code_section[custom_address] = instruction

		else:
			self.code_section.append(instruction)
			self.current_address += 1

	def search_data(self, data_to_search):
		"""Returns the index of the parameter data_to_search in data
		section."""

		for position, data in enumerate(self.data_section):
			if data == data_to_search:
				return position

		return -1

	def emit_int32(self, int32, custom_address=None):
		"""Emit an integer number (32 bits)."""

		for byte in int32.to_bytes(4, byteorder='big', signed=True):
			self.emit_instruction(byte, custom_address)

			if custom_address is not None:
				custom_address += 1

	def emit_float(self, float_, custom_address=None):
		"""Emit a float number."""

		for byte in struct.pack('!d', float_):
			self.emit_instruction(byte, custom_address)

			if custom_address is not None:
				custom_address += 1

	def emit_string(self, string, custom_address=None):
		"""Emit a string."""

		if string in self.data_section:
			self.emit_int32(self.search_data(string), custom_address)

		else:
			self.data_section.append(string)
			self.emit_int32(len(self.data_section) - 1, custom_address)

	def generate_node(self, node, preserve_function_return=True):
		"""Generate the code of a node.

		:param preserve_function_return = if is False, pop function
		return, because is unecessary
		"""

		if isinstance(node, IntNode):
			self.emit_instruction(OpCodes.LDI)
			self.emit_int32(node.value)

		elif isinstance(node, FloatNode):
			self.emit_instruction(OpCodes.LDF)
			self.emit_float(node.value)

		elif isinstance(node, StringNode):
			self.emit_instruction(OpCodes.LDS)
			self.emit_string(node.value)

		elif isinstance(node, NilNode):
			self.emit_instruction(OpCodes.LDN)

		elif isinstance(node, UnaryOperationNode):
			self.generate_node(node.left)

			# +1 == 1, so ignore
			if node.operator == TokenType.OPERATOR_PLUS:
				return

			self.emit_instruction(self.unary_instructions[node.operator])

		elif isinstance(node, BinaryOperationNode):
			self.generate_node(node.left)
			self.generate_node(node.right)
			self.emit_instruction(self.binary_instructions[node.operator])

		elif isinstance(node, BlockNode):
			for statement in node.body:
				self.generate_node(statement, False)

		elif isinstance(node, LetNode) or isinstance(node, AssignNode):
			if isinstance(node, LetNode):
				self.emit_instruction(OpCodes.LET)
				self.emit_string(node.name)

			if node.value is not None:
				self.generate_node(node.value)
			
			else:
				# load nil
				self.emit_instruction(OpCodes.LDN)

			self.emit_instruction(OpCodes.STO)
			self.emit_string(node.name)

		elif isinstance(node, CallNode):
			node.arguments.reverse()

			for argument in node.arguments:
				self.generate_node(argument)


			if node.name in built_in_functions:
				self.emit_instruction(built_in_functions[node.name][1])
				return

			self.emit_instruction(OpCodes.CAL)

			if node.name in self.functions_address:
				self.emit_int32(self.functions_address[node.name])

			else:
				self.address_to_link[self.current_address] = node.name
				self.emit_int32(0)  # temporary address

			if not preserve_function_return:
				self.emit_instruction(OpCodes.POP)

		elif isinstance(node, FnNode):
			self.emit_instruction(OpCodes.JMP)
			jump_to_end_address = self.current_address
			self.emit_int32(0)  # temporary address

			self.functions_address[node.name] = self.current_address

			for argument in node.arguments:
				self.emit_instruction(OpCodes.LET)
				self.emit_string(argument.name)
				self.emit_instruction(OpCodes.STO)
				self.emit_string(argument.name)

			self.generate_node(node.body)

			if self.code_section[-1] != OpCodes.RET:
				self.emit_instruction(OpCodes.RET)

			self.emit_int32(self.current_address, jump_to_end_address)

		elif isinstance(node, IdentifierNode):
			self.emit_instruction(OpCodes.LDV)
			self.emit_string(node.name)

		elif isinstance(node, WhileNode):
			condition_address = self.current_address

			self.generate_node(node.condition)
			self.emit_instruction(OpCodes.JPF)
			jump_to_end_address = self.current_address
			self.emit_int32(0)  # temporary address

			self.generate_node(node.body)
			self.emit_instruction(OpCodes.JMP)
			self.emit_int32(condition_address)

			self.emit_int32(self.current_address, jump_to_end_address)

		elif isinstance(node, IfNode):
			self.generate_node(node.condition)

			self.emit_instruction(OpCodes.JPF)
			jump_false_address = self.current_address
			self.emit_int32(0)  # temporary address

			self.generate_node(node.if_body)

			if node.else_body is not None:
				self.emit_instruction(OpCodes.JMP)
				jump_to_end_address = self.current_address
				self.emit_int32(0)  # temporary address

				self.emit_int32(self.current_address, jump_false_address)
				
				self.generate_node(node.else_body)

				self.emit_int32(self.current_address, jump_to_end_address)

			else:
				self.emit_int32(self.current_address, jump_false_address)

		elif isinstance(node, ReturnNode):
			self.generate_node(node.value)
			self.emit_instruction(OpCodes.RET)

		elif isinstance(node, DoWhileNode):
			body_address = self.current_address
			self.generate_node(node.body)

			self.generate_node(node.condition)
	
			self.emit_instruction(OpCodes.JPT)
			self.emit_int32(body_address)

		elif isinstance(node, ListNode):
			node.value.reverse()

			for value in node.value:
				self.generate_node(value)

			self.emit_instruction(OpCodes.LDL)
			self.emit_int32(len(node.value))

		elif isinstance(node, ListAccessNode):
			self.generate_node(node.list)
			self.generate_node(node.index)

			self.emit_instruction(OpCodes.GET)

		else:
			raise NotImplementedError(node)

	def link_addresses(self):
		"""Link the addresses of functions."""

		for address in self.address_to_link:
			self.emit_int32(
				self.functions_address[self.address_to_link[address]],
				address,
			)

	def generate(self):
		"""Generate all code."""

		while self.current_node:
			self.generate_node(self.current_node, False)
			self.update_current_node()

		# call the entry point
		self.emit_instruction(OpCodes.CAL)
		self.emit_int32(self.functions_address['main'])

		# emit a halt instruction
		self.emit_instruction(OpCodes.EXT)

		# link all addresses
		self.link_addresses()

		# generate the bytes of data section
		bytes_of_data_section = []

		for data in self.data_section:
			for ch in data:
				bytes_of_data_section.append(ord(ch))

			bytes_of_data_section.append(0)

		bytes_of_data_section.append(0)

		# return all code
		return VM_SIGNATURE + bytes_of_data_section + self.code_section

