# Lang Compiler
# Author: Jonas

from error import IllegalCharacterError, UnclosedStringError
from position import Position
from token_ import TokenType, Token

BINARY_DIGITS = '01'
OCTAL_DIGITS = '01234567'
DECIMAL_DIGITS = '0123456789'
HEXADECIMAL_DIGITS = '0123456789abcdefABCDEF'

CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'


class Lexer:
	def __init__(self, file_name, source):
		self.file_name = file_name
		self.source = source

		self.tokens = []

		# the position starts at -1 because it is first incremented,
		# then used
		self.position = -1
		self.line = 1
		self.column = 1

		self.current_char = None
		self.update_position_and_current_char()

		self.keywords = [
			TokenType.KEYWORD_FN,
			TokenType.KEYWORD_WHILE,
			TokenType.KEYWORD_IF,
			TokenType.KEYWORD_ELSE,
			TokenType.KEYWORD_DO,
			TokenType.KEYWORD_FOR,
			TokenType.KEYWORD_LET,
			TokenType.KEYWORD_RETURN,
			TokenType.KEYWORD_BREAK,
			TokenType.KEYWORD_CONTINUE,
		]

		self.operators = [
			TokenType.OPERATOR_PLUS,
			TokenType.OPERATOR_MINUS,
			TokenType.OPERATOR_ASTERISK,
			TokenType.OPERATOR_SLASH,
			TokenType.OPERATOR_LPAREN,
			TokenType.OPERATOR_RPAREN,
			TokenType.OPERATOR_LBRACE,
			TokenType.OPERATOR_RBRACE,
			TokenType.OPERATOR_EQ,
			TokenType.OPERATOR_NE,
			TokenType.OPERATOR_LT,
			TokenType.OPERATOR_LE,
			TokenType.OPERATOR_GT,
			TokenType.OPERATOR_GE,
			TokenType.OPERATOR_ASSIGN,
			TokenType.OPERATOR_BTW_SHL,
			TokenType.OPERATOR_BTW_SHR,
			TokenType.OPERATOR_NOT,
			TokenType.OPERATOR_AND,
			TokenType.OPERATOR_OR,
			TokenType.OPERATOR_BTW_NOT,
			TokenType.OPERATOR_BTW_AND,
			TokenType.OPERATOR_BTW_OR,
			TokenType.OPERATOR_BTW_XOR,
			TokenType.OPERATOR_SEMICOLON,
			TokenType.OPERATOR_COMMA,
			TokenType.OPERATOR_INC,
			TokenType.OPERATOR_DEC,
		]

	def update_position(self):
		"""Update the position."""

		if self.current_char == '\n':
			self.line += 1
			self.column = 1

		elif self.current_char != None:
			self.column += 1

		self.position += 1
	
	def update_current_char(self):
		"""Update the current char."""

		if self.position < len(self.source):
			self.current_char = self.source[self.position]

		else:
			self.current_char = None

	def update_position_and_current_char(self):
		"""Update the position and the current char."""

		self.update_position()
		self.update_current_char()

	def peek_next_char(self):
		"""Returns the next char, but without updating the position and
		current char."""

		if self.position + 1 < len(self.source):
			return self.source[self.position + 1]

		else:
			return None

	def append_new_token(self, line, column, typ, value):
		"""Append a new token object in self.tokens."""

		self.tokens.append(Token(
			Position(
				self.file_name,
				line,
				column,
			),
			typ,
			value,
		))

	def lex(self):
		"""Return a list of tokens."""

		while self.current_char != None:
			token_line = self.line
			token_column = self.column
			token_value = None
			token_type = None

			if self.current_char in '\t\r\n ':
				self.update_position_and_current_char()
				continue

			elif self.current_char == '/' and self.peek_next_char() == '/':
				while not self.current_char in ('\n', None):
					self.update_position_and_current_char()

				continue

			# binary, octal and hexadecimal
			elif self.current_char == '0' and self.peek_next_char() in 'box':
				if self.peek_next_char() == 'b':
					base = 2
					digits = BINARY_DIGITS

				elif self.peek_next_char() == 'o':
					base = 8
					digits = OCTAL_DIGITS

				elif self.peek_next_char() == 'x':
					base = 16
					digits = HEXADECIMAL_DIGITS

				self.update_position_and_current_char()  # 0
				self.update_position_and_current_char()  # b, o, x

				token_type = TokenType.TYPE_INT
				token_value = self.get_int_token(digits, base)

			elif self.current_char in CHARACTERS:
				token_type = TokenType.TYPE_IDENTIFIER
				token_value = self.get_identifier_token()

				# the value is equal to the type
				if token_value in self.keywords:
					token_type = token_value

			elif self.current_char in DECIMAL_DIGITS:
				token_value, token_type = self.get_number_token()

			# operators with two characters
			elif self.current_char + self.peek_next_char() in self.operators:
				token_value = self.current_char + self.peek_next_char()
				
				# self.peek_next_char
				self.update_position_and_current_char()
				# self.current_char
				self.update_position_and_current_char()

				token_type = token_value

			# operators with one character
			elif self.current_char in self.operators:
				token_value = self.current_char
				self.update_position_and_current_char()
				token_type = token_value

			elif self.current_char == '"':
				token_type = TokenType.TYPE_STRING
				token_value = self.get_string_token()

			# illegal character
			else:
				error = IllegalCharacterError(
					Position(
						self.file_name,
						token_line,
						token_column,
					),
					self.current_char,
				)

				error.show_error_and_abort()

			self.append_new_token(
				token_line,
				token_column,
				token_type,
				token_value,
			)		

		# EOF
		self.append_new_token(
			token_line,
			token_column,
			TokenType.TYPE_EOF,
			TokenType.TYPE_EOF,
		)

		return self.tokens

	def get_identifier_token(self):
		"""Returns a token of type identifier."""

		token_value = ''

		while self.current_char in CHARACTERS + DECIMAL_DIGITS:
			token_value += self.current_char
			self.update_position_and_current_char()

		return token_value

	def get_number_token(self):
		"""Returns a token of type int or float and the type."""

		token_value = ''

		while (self.current_char in DECIMAL_DIGITS) \
				or (self.current_char == '.'):

			# if the current char is a ".", but there is already a "."
			# in the token
			if (self.current_char == '.') and ('.' in token_value):
				break

			token_value += self.current_char
			self.update_position_and_current_char()

		if '.' in token_value:
			token_type = TokenType.TYPE_FLOAT
			token_value = float(token_value)

		else:
			token_type = TokenType.TYPE_INT
			token_value = int(token_value)

		return token_value, token_type

	def get_string_token(self):
		"""Returns a token of type string."""

		# for possible errors
		start_position = self.column

		self.update_position_and_current_char()  # "
		token_value = ''

		escape_chars = {
			'a': '\a',
			'b': '\b',
			'f': '\f',
			'n': '\n',
			'r': '\r',
			't': '\t',
			'v': '\v',
			'\n': '\n',
			'"': '\"',
			'\\': '\\',
		}

		while self.current_char != '"':
			if self.current_char == '\\':
				self.update_position_and_current_char()  # \\
				
				if self.current_char in escape_chars:
					token_value += escape_chars[self.current_char]
					self.update_position_and_current_char()

				else:
					token_value += f'\\{self.current_char}'
					self.update_position_and_current_char()

			elif self.current_char == '\n':
				error = UnclosedStringError(
					Position(
						self.file_name,
						self.line,
						start_position,
					),
				)

				error.show_error_and_abort()

			else:
				token_value += self.current_char
				self.update_position_and_current_char()

		self.update_position_and_current_char()  # "
		return token_value

	def get_int_token(self, digits, base):
		"""Returns a token of type int, but using the digits paremeter
		and base parameter."""

		token_value = ''

		while self.current_char in digits:
			token_value += self.current_char
			self.update_position_and_current_char()

		return int(token_value, base=base)

