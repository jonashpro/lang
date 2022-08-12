# Lang Compiler
# Author: Jonas

from error import ExpectedError
from error import InvalidSyntaxError
from error import UnexpectedError
from error import UnreachableStatementError
from node import *
from token_ import TokenType


class Parser:
	def __init__(self, tokens):
		self.tokens = tokens

		self.position = -1
		self.current_token = None
		self.update_current_token()
	
		self.ast = []

		self.literal_nodes = {
			TokenType.TYPE_INT: IntNode,
			TokenType.TYPE_FLOAT: FloatNode,
			TokenType.TYPE_STRING: StringNode,
		}

		# +=, -=, *=, /=
		# example: key: +=, value: +
		self.assign_operators = {
			TokenType.OPERATOR_PLUS_ASSIGN: TokenType.OPERATOR_PLUS,
			TokenType.OPERATOR_MINUS_ASSIGN: TokenType.OPERATOR_MINUS,
			TokenType.OPERATOR_ASTERISK_ASSIGN: TokenType.OPERATOR_ASTERISK,
			TokenType.OPERATOR_SLASH_ASSIGN: TokenType.OPERATOR_SLASH,
		}

	def update_current_token(self):
		"""Update the current token."""

		self.position += 1

		if self.position < len(self.tokens):
			self.current_token = self.tokens[self.position]

		else:
			self.current_token = self.tokens[-1]  # EOF

	def peek_next_token(self):
		"""Returns the next token, but without advance."""

		if self.position + 1 < len(self.tokens):
			return self.tokens[self.position + 1]

		else:
			return self.tokens[-1]

	def match(self, typ):
		"""If the current token type is equal to the typ parameter,
		update current token, else, show an error."""

		if self.current_token.type == typ:
			self.update_current_token()

		else:
			error = ExpectedError(self.current_token.position, typ)
			error.show_error_and_abort()
	
	def parse(self):
		"""Returns an AST."""

		while self.current_token.type != TokenType.TYPE_EOF:
			self.ast.append(self.declaration())

		return self.ast
	
	def declaration(self):
		""""
		<declaration> ::= <fn_statement> | <let_statement>
		"""

		if self.current_token.type == TokenType.KEYWORD_LET:
			return self.let_statement()

		elif self.current_token.type == TokenType.KEYWORD_FN:
			return self.fn_statement()
	
		else:
			error = UnexpectedError(
				self.current_token.position,
				self.current_token.value,
			)

			error.show_error_and_abort()

	def statement(self):
		"""
		<statement> ::= <block_statement>
		             |  <let_statement>
		             |  <if_statement>
		             |  <while_statement>
		             |  <function_call> ';'
		             |  <return_statement>
		             |  <assign_statement>
		             |  <do_while_statement>
		"""

		if self.current_token.type == TokenType.KEYWORD_LET:
			return self.let_statement()

		elif self.current_token.type == TokenType.OPERATOR_LBRACE:
			return self.block_statement()

		elif self.current_token.type == TokenType.KEYWORD_IF:
			return self.if_statement()

		elif self.current_token.type == TokenType.KEYWORD_WHILE:
			return self.while_statement()

		elif self.current_token.type == TokenType.TYPE_IDENTIFIER:
			if self.peek_next_token().type == TokenType.OPERATOR_LPAREN:
				node = self.function_call()
				self.match(TokenType.OPERATOR_SEMICOLON)
				return node

			else:
				return self.assign_statement()

		elif self.current_token.type == TokenType.KEYWORD_RETURN:
			return self.return_statement()

		elif self.current_token.type == TokenType.KEYWORD_DO:
			return self.do_while_statement()

		else:
			error = UnexpectedError(
				self.current_token.position,
				self.current_token.value,
			)
			error.show_error_and_abort()

	def do_while_statement(self):
		"""
		<do_while_statement> ::=
			'do'
				<statement>
			'while' <condition> ';'
		"""

		position = self.current_token.position

		self.match(TokenType.KEYWORD_DO)
		body = self.statement()
		self.match(TokenType.KEYWORD_WHILE)
		condition = self.condition()
		self.match(TokenType.OPERATOR_SEMICOLON)

		return DoWhileNode(position, condition, body)

	def assign_statement(self):
		"""
		<assign_statement> ::=
			<identifier> ('=' | '+= ' | '-=' | '*=' | '/=')
				<expression> ';'
		"""

		position = self.current_token.position

		name = self.current_token.value
		self.match(TokenType.TYPE_IDENTIFIER)

		if self.current_token.type == TokenType.OPERATOR_ASSIGN:
			self.match(TokenType.OPERATOR_ASSIGN)
			value = self.expression()

		# +=, -=, *=, /=
		elif self.current_token.type in self.assign_operators:
			operator = self.assign_operators[self.current_token.type]
			self.match(self.current_token.type)
		
			value = BinaryOperationNode(
				position,
				operator,
				IdentifierNode(position, name),
				self.expression(),
			)

		else:
			error = ExpectedError(position, '= += -= *= or /=')
			error.show_error_and_abort()
		
		self.match(TokenType.OPERATOR_SEMICOLON)
		return AssignNode(position, name, value)

	def return_statement(self):
		"""
		<return_statement> ::= 'return' <expression> ';'
		"""
		
		position = self.current_token.position
		
		self.match(TokenType.KEYWORD_RETURN)
		expression = self.expression()
		self.match(TokenType.OPERATOR_SEMICOLON)

		return ReturnNode(position, expression)

	def while_statement(self):
		"""
		<while_statement> ::=
			'while' <condition>
				<statement>
		"""

		position = self.current_token.position

		self.match(TokenType.KEYWORD_WHILE)
		condition = self.condition()
		body = self.statement()

		return WhileNode(position, condition, body)

	def condition(self):
		"""
		<condition> ::= '(' <expression> ')'
		"""

		self.match(TokenType.OPERATOR_LPAREN)
		condition = self.expression()
		self.match(TokenType.OPERATOR_RPAREN)

		return condition

	def if_statement(self):
		"""
		<if_statement> ::=
			'if' <condition>
				<statement>
			('else' <statement>)?
		"""

		position = self.current_token.position
		
		self.match(TokenType.KEYWORD_IF)
		condition = self.condition()
		if_body = self.statement()
		else_body = None

		if self.current_token.type == TokenType.KEYWORD_ELSE:
			self.match(TokenType.KEYWORD_ELSE)
			else_body = self.statement()
	
		return IfNode(position, condition, if_body, else_body)

	def block_statement(self):
		"""
		<block_statement> ::= '{' <statement>* '}'
		"""

		position = self.current_token.position

		self.match(TokenType.OPERATOR_LBRACE)
		body = []

		while self.current_token.type != TokenType.OPERATOR_RBRACE:
			node = self.statement()
			body.append(node)

			if isinstance(node, ReturnNode):
				# return 0;
				# another statement
				if self.current_token.type != TokenType.OPERATOR_RBRACE:
					error = UnreachableStatementError(
						self.current_token.position
					)
					error.show_error_and_abort()

		self.match(TokenType.OPERATOR_RBRACE)

		return BlockNode(position, body)

	def fn_statement(self):
		"""
		<fn_statement> ::=
			'fn' <identifier> '('(<identifier>(',' <identifier>)*)?')'
				<statement>
		"""

		position = self.current_token.position
		
		self.match(TokenType.KEYWORD_FN)
		name = self.current_token.value
		self.match(TokenType.TYPE_IDENTIFIER)
		self.match(TokenType.OPERATOR_LPAREN)

		arguments = []

		while self.current_token.type != TokenType.OPERATOR_RPAREN:
			arguments.append(IdentifierNode(
				self.current_token.position,
				self.current_token.value,
			))

			self.match(TokenType.TYPE_IDENTIFIER)

			if self.current_token.type == TokenType.OPERATOR_COMMA:
				self.match(TokenType.OPERATOR_COMMA)

			else:
				break

		self.match(TokenType.OPERATOR_RPAREN)
		body = self.statement()

		return FnNode(position, name, arguments, body)

	def let_statement(self):
		"""
		<let_statement> ::= 'let' <identifier> ('=' <expression>)? ';'
		"""

		position = self.current_token.position

		self.match(TokenType.KEYWORD_LET)
		name = self.current_token.value
		self.match(TokenType.TYPE_IDENTIFIER)
		value = None

		if self.current_token.type == TokenType.OPERATOR_ASSIGN:
			self.match(TokenType.OPERATOR_ASSIGN)
			value = self.expression()

		self.match(TokenType.OPERATOR_SEMICOLON)

		return LetNode(position, name, value)
	
	def expression(self):
		"""Calls the expression the least precedence."""
		
		return self.bitwise_or_xor_expression()

	def bitwise_or_xor_expression(self):
		"""Returns a binary expression with '|' or '^'."""

		return self.binary_operation(self.bitwise_and_expression, (
			TokenType.OPERATOR_BTW_OR,
			TokenType.OPERATOR_BTW_XOR,
		))
	
	def bitwise_and_expression(self):
		"""Returns a binary expression with '&'."""

		return self.binary_operation(self.bitwise_shift_expression, (
			TokenType.OPERATOR_BTW_AND,
		))
	
	def bitwise_shift_expression(self):
		"""Returns a binary expression with '<<' or '>>'."""

		return self.binary_operation(self.and_or_expression, (
			TokenType.OPERATOR_BTW_SHL,
			TokenType.OPERATOR_BTW_SHR,
		))

	def and_or_expression(self):
		"""Returns a binary expression with '&&' or '||'."""

		return self.binary_operation(self.comp_expression, (
			TokenType.OPERATOR_AND,
			TokenType.OPERATOR_OR,
		))

	def comp_expression(self):
		"""Returns a binary expression with '==', '!=', '<', '<=', '>'
		or '>='."""

		return self.binary_operation(self.add_sub_expression, (
			TokenType.OPERATOR_EQ,
			TokenType.OPERATOR_NE,
			TokenType.OPERATOR_LT,
			TokenType.OPERATOR_LE,
			TokenType.OPERATOR_GT,
			TokenType.OPERATOR_GE,
		))

	def add_sub_expression(self):
		"""Returns a binary expression with '+' or '-'."""

		return self.binary_operation(self.mul_div_expression, (
			TokenType.OPERATOR_PLUS,
			TokenType.OPERATOR_MINUS,
		))
	
	def mul_div_expression(self):
		"""Returns a binary expression with '*' or '/'."""

		return self.binary_operation(self.factor, (
			TokenType.OPERATOR_ASTERISK,
			TokenType.OPERATOR_SLASH,
		))
	
	def factor(self):
		"""
		<factor> ::= <int>
		          |  <float>
		          |  <string>
		          |  <identifier>
		          |  '(' <expression> ')'
		          |  '+' <factor>
		          |  '-' <factor>
		          |  '!' <expression>
		          |  <function_call>
		          |  '~' <factor>
		          |  <list_declaration>
		          |  <list_access>
		"""

		# <int> | <float> | <string>
		if self.current_token.type in self.literal_nodes:
			node = self.literal_nodes[self.current_token.type](
				self.current_token.position,
				self.current_token.value
			)

			self.match(self.current_token.type)

			return node
		
		# '(' <expression> ')'
		elif self.current_token.type == TokenType.OPERATOR_LPAREN:
			self.match(TokenType.OPERATOR_LPAREN)
			expression = self.expression()
			self.match(TokenType.OPERATOR_RPAREN)
			
			return expression

		# '+' <factor> | '-' <factor>
		elif self.current_token.type \
				in (TokenType.OPERATOR_PLUS, TokenType.OPERATOR_MINUS):

			position = self.current_token.position 
			operator = self.current_token.type
			self.match(operator)

			factor = self.factor()

			return UnaryOperationNode(position, operator, factor)

		# '!' <expression>
		elif self.current_token.type == TokenType.OPERATOR_NOT:
			position = self.current_token.position
			operator = self.current_token.type
			self.match(operator)

			expression = self.expression()

			node = UnaryOperationNode(
				position,
				operator,
				expression,
			)

			return node

		# <identifier> | <function_call> | <list_access>
		elif self.current_token.type == TokenType.TYPE_IDENTIFIER:
			if self.peek_next_token().type == TokenType.OPERATOR_LPAREN:
				return self.function_call()

			elif self.peek_next_token().type == TokenType.OPERATOR_LBRACKET:
				return self.list_access()

			else:
				position = self.current_token.position
				name = self.current_token.value
				self.match(TokenType.TYPE_IDENTIFIER)

				return IdentifierNode(position, name)

		# '~' <factor>
		elif self.current_token.type == TokenType.OPERATOR_BTW_NOT:
			position = self.current_token.position
			operator = self.current_token.type

			self.match(TokenType.OPERATOR_BTW_NOT)

			return UnaryOperationNode(position, operator, self.factor())

		# <list_declaration>
		elif self.current_token.type == TokenType.OPERATOR_LBRACKET:
			return self.list_declaration()

		# invalid syntax
		else:
			error = InvalidSyntaxError(
				self.current_token.position,
				self.current_token.value,
			)

			error.show_error_and_abort()

	def list_declaration(self):
		"""
		<list_declaration> ::= '['(<expression>(',' <expression>)*)?']'
		"""

		position = self.current_token.position
		
		self.match(TokenType.OPERATOR_LBRACKET)
		values = []

		while self.current_token.type != TokenType.OPERATOR_RBRACKET:
			values.append(self.expression())

			if self.current_token.type == TokenType.OPERATOR_COMMA:
				self.match(TokenType.OPERATOR_COMMA)

			else:
				break

		self.match(TokenType.OPERATOR_RBRACKET)

		return ListNode(position, values)

	def function_call(self):
		"""
		<function_call> ::=
			<identifier> '(' (<expression> (',' <expression>)*)? ')'
		"""

		position = self.current_token.position
		
		name = self.current_token.value
		self.match(TokenType.TYPE_IDENTIFIER)
		self.match(TokenType.OPERATOR_LPAREN)
		arguments = []

		while self.current_token.type != TokenType.OPERATOR_RPAREN:
			arguments.append(self.expression())

			if self.current_token.type == TokenType.OPERATOR_COMMA:
				self.match(TokenType.OPERATOR_COMMA)

			else:
				break

		self.match(TokenType.OPERATOR_RPAREN)

		return CallNode(position, name, arguments)

	def list_access(self):
		"""
		<list_access> ::= <identifier> ('[' <expression> ']')+
		"""

		position = self.current_token.position

		name = self.current_token.value
		self.match(TokenType.TYPE_IDENTIFIER)
		
		node = IdentifierNode(position, name)

		while self.current_token.type == TokenType.OPERATOR_LBRACKET:
			position = self.current_token.position

			self.match(TokenType.OPERATOR_LBRACKET)
			index = self.expression()
			self.match(TokenType.OPERATOR_RBRACKET)
			node = ListAccessNode(position, node, index)

		return node

	def binary_operation(self, next_precedence, operators):
		"""
		<binary_operation> ::=
			<next_precedence> (<operators> <next_precedence>)*
		"""
		
		left = next_precedence()

		while self.current_token.type in operators:
			position = self.current_token.position

			operator = self.current_token.type
			self.match(operator)
			
			right = next_precedence()
			left = BinaryOperationNode(position, operator, left, right)

		return left

