# Lang Compiler
# Author: Jonas

from built_in import built_in_functions
from error import UndefinedError
from error import VariableWasUsedButNotInitializedWarning
from error import VariableIsNotCallableError
from error import WrongNumberOfArgumentsError
from error import NoEntryPointError
from node import *


class Variable:
	def __init__(self, position, name, used, initialized):
		self.position = position
		self.name = name
		self.used = used
		self.initialized = initialized

	def __repr__(self):
		return self.name

class SemanticAnalyzer:
	def __init__(self, ast):
		self.ast = ast
		
		self.position = -1
		self.current_node = None
		self.update_current_node()

		# variabels are stored in a stack. every time a new scope
		# begins, the top of the stack is duplicated, and when it ends,
		# removed
		self.variables = [[]]

		self.functions = []
		self.call_nodes = []

	def update_current_node(self):
		self.position += 1

		if self.position < len(self.ast):
			self.current_node = self.ast[self.position]

		else:
			self.current_node = None

	def new_scope(self):
		self.variables.append(self.variables[-1].copy())
	
	def end_scope(self):
		self.variables.pop()

	def add_variable(self, variable):
		self.variables[-1].append(variable)

	def variable_exists_in_the_current_scope(self, variable_name):
		for variable in self.variables[-1]:
			if variable.name == variable_name:
				return True

		return False
	
	def mark_variable_as_used(self, variable_name):
		for variable in self.variables[-1]:
			if variable.name == variable_name:
				if variable.initialized == False:
					warning = VariableWasUsedButNotInitializedWarning(
						variable.position,
						variable.name,
					)

					warning.show_error()

				variable.used = True

	def function_exists(self, function_name):
		for function in self.functions:
			if function.name == function_name:
				return True

		return False

	def get_function_arguments(self, function_name):
		for function in self.functions:
			if function.name == function_name:
				return function.arguments

	def is_built_in_function(self, name):
		return name in built_in_functions

	def get_built_in_function_arguments(self, name):
		return built_in_functions[name][0]

	def analyze_node(self, node):
		if isinstance(node, UnaryOperationNode):
			self.analyze_node(node.left)

		elif isinstance(node, BinaryOperationNode):
			self.analyze_node(node.left)
			self.analyze_node(node.right)

		elif isinstance(node, LetNode):
			self.analyze_node(node.value)
			self.add_variable(Variable(
				node.position,
				node.name,
				False,
				True if node.value else False,
			))

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
			self.functions.append(node)

			self.new_scope()

			for argument in node.arguments:
				self.add_variable(Variable(
					argument.position,
					argument.name,
					False,
					True,
				))

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

	def analyze(self):
		while self.current_node:
			self.analyze_node(self.current_node)
			self.update_current_node()

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

		if not self.function_exists('main'):
			error = NoEntryPointError()
			error.show_error_and_abort()

