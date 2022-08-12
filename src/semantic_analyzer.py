# Lang Compiler
# Author: Jonas

from built_in import built_in_functions
from error import UndefinedError
from error import VariableIsNotCallableError
from error import WrongNumberOfArgumentsError
from error import NoEntryPointError
from error import RedeclarationError
from node import *


class Variable:
	def __init__(self, position, used, initialized):
		self.position = position
		self.used = used
		self.initialized = initialized


class Function:
	def __init__(self, position, arguments):
		self.position = position
		self.arguments = arguments


class SemanticAnalyzer:
	def __init__(self, ast):
		self.ast = ast
		
		self.position = -1
		self.current_node = None
		self.update_current_node()

		# variables are stored in a stack. every time a new scope
		# begins, the top of the stack is duplicated, and when it ends,
		# removed
		self.variables = [{}]

		self.functions = {}
		self.call_nodes = []

	def update_current_node(self):
		"""Update the current node."""

		self.position += 1

		if self.position < len(self.ast):
			self.current_node = self.ast[self.position]

		else:
			self.current_node = None

	def new_scope(self):
		"""Create a new scope."""

		self.variables.append(self.variables[-1].copy())
	
	def end_scope(self):
		"""Return to last scope."""

		self.variables.pop()

	def add_variable(self, position, name, initialized):
		"""Add a new variable in current scope."""

		self.variables[-1][name] = Variable(position, False, initialized)

	def variable_exists_in_the_current_scope(self, name):
		"""Returns if a variable exists in the current scope."""

		return name in self.variables[-1]
	
	def mark_variable_as_used(self, name):
		"""Mark a variable as used."""

		self.variables[-1][name].used = True
	
	def mark_variable_as_initialized(self, name):
		"""Mark a variable as initialized."""

		self.variables[-1][name].initialized = True

	def function_exists(self, name):
		"""Returns is a function exists."""

		return name in self.functions

	def add_function(self, position, name, arguments):
		"""Add a new function."""

		self.functions[name] = Function(position, arguments)

	def get_function_arguments(self, name):
		"""Returns the arguments of a function."""

		return self.functions[name].arguments

	def is_built_in_function(self, name):
		"""Returns if a function is built in."""

		return name in built_in_functions

	def get_built_in_function_arguments(self, name):
		"""Returns the arguments of a built in function."""

		return built_in_functions[name][0]

	def analyze_node(self, node):
		"""Analyze the semantic of a node."""

		if isinstance(node, UnaryOperationNode):
			self.analyze_node(node.left)

		elif isinstance(node, BinaryOperationNode):
			self.analyze_node(node.left)
			self.analyze_node(node.right)

		elif isinstance(node, LetNode):
			if self.variable_exists_in_the_current_scope(node.name):
				error = RedeclarationError(node.position, node.name)
				error.show_error_and_abort()

			if node.value:
				self.analyze_node(node.value)

			self.add_variable(
				node.position,
				node.name,
				True if node.value else False,
			)

		elif isinstance(node, IdentifierNode):
			if not self.variable_exists_in_the_current_scope(node.name):
				error = UndefinedError(node.position, node.name)
				error.show_error_and_abort()

			self.mark_variable_as_used(node.name)

		elif isinstance(node, BlockNode):
			self.new_scope()

			for statement in node.body:
				self.analyze_node(statement)

			self.end_scope()

		elif isinstance(node, FnNode):
			self.add_function(node.position, node.name, node.arguments)

			self.new_scope()

			for argument in node.arguments:
				self.add_variable(
					argument.position,
					argument.name,
					True,
				)

			self.analyze_node(node.body)

			self.end_scope()

		elif isinstance(node, IfNode):
			self.analyze_node(node.condition)
			self.analyze_node(node.if_body)
			if node.else_body: self.analyze_node(node.else_body)

		elif isinstance(node, WhileNode):
			self.analyze_node(node.condition)
			self.analyze_node(node.body)

		elif isinstance(node, ReturnNode):
			self.analyze_node(node.value)

		elif isinstance(node, AssignNode):
			if not self.variable_exists_in_the_current_scope(node.name):
				error = UndefinedError(node.position, node.name)
				error.show_error_and_abort()

			self.analyze_node(node.value)

			self.mark_variable_as_initialized(node.name)

		elif isinstance(node, CallNode):
			for argument in node.arguments:
				self.analyze_node(argument)

			if self.is_built_in_function(node.name):
				arguments_length = self.get_built_in_function_arguments(
					node.name,
				)

				if len(node.arguments) != arguments_length:
					error = WrongNumberOfArgumentsError(
						node.position,
						node.name,
						arguments_length,
						len(node.arguments),
					)

					error.show_error_and_abort()

				return

			elif not self.function_exists(node.name):
				# call a variable
				if self.variable_exists_in_the_current_scope(node.name):
					error = VariableIsNotCallableError(
						node.position,
						node.name,
					)

					error.show_error_and_abort()

			self.call_nodes.append(node)

		elif isinstance(node, DoWhileNode):
			self.analyze_node(node.body)
			self.analyze_node(node.condition)

		elif isinstance(node, IntNode) \
				or isinstance(node, FloatNode) \
				or isinstance(node, StringNode):
			
			# do nothing
			pass

		else:
			raise NotImplementedError(type(node))

	def analyze(self):
		"""Analyze all nodes."""

		while self.current_node:
			self.analyze_node(self.current_node)
			self.update_current_node()

		# checks if the calls are valid
		for call in self.call_nodes:
			if not self.function_exists(call.name):
				error = UndefinedError(call.position, call.name)
				error.show_error_and_abort()

			arguments_length = len(self.get_function_arguments(call.name))

			if arguments_length != len(call.arguments):
				error = WrongNumberOfArgumentsError(
					call.position,
					call.name,
					arguments_length,
					len(call.arguments),
				)
				error.show_error_and_abort()

		# checks if have a main function (entry point)
		if not self.function_exists('main'):
			error = NoEntryPointError()
			error.show_error_and_abort()

