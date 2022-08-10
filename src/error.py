# Lang Compiler
# Author: Jonas

import sys

ERROR = 'error'
WARNING = 'warning'


class Error:
	def __init__(self, position, error_type, message):
		self.position = position
		self.error_type = error_type
		self.message = message
	
	def show_error(self):
		print(
			f'%s{self.error_type}: {self.message}' %(f'{self.position}: ' if self.position else ''),
			file=sys.stderr,
		)
	
	def show_error_and_abort(self):
		self.show_error()
		exit(1)
	

class IllegalCharacterError(Error):
	def __init__(self, position, character):
		super().__init__(position, ERROR, f'illegal character "{character}"')


class UnclosedStringError(Error):
	def __init__(self, position):
		super().__init__(position, ERROR, f'unclosed string')


class ExpectedError(Error):
	def __init__(self, position, token):
		super().__init__(position, ERROR, f'"{token}" expected')


class InvalidSyntaxError(Error):
	def __init__(self, position, token):
		super().__init__(position, ERROR, f'invalid syntax: "{token}"')


class UnexpectedError(Error):
	def __init__(self, position, token):
		super().__init__(position, ERROR, f'unexpected "{token}"')


class UndefinedError(Error):
	def __init__(self, position, name):
		super().__init__(position, ERROR, f'{name} is undefined')


class WrongNumberOfArgumentsError(Error):
	def __init__(self, position, function, expected, got):
		super().__init__(
			position,
			ERROR,
			f'function {function} expected {expected} argument(s),' \
				+ f' but {got} are given'
		)


class VariableIsNotCallableError(Error):
	def __init__(self, position, variable):
		super().__init__(
			position,
			ERROR,
			f'variable {variable} is not callable',
		)


class NoEntryPointError(Error):
	def __init__(self):
		super().__init__(None, ERROR, 'no entry point')


class RedeclarationError(Error):
	def __init__(self, position, name):
		super().__init__(position, ERROR, f'redeclaration of {name}')

