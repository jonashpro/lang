# Lang Compiler
# Author: Jonas

class TokenType:
	TYPE_EOF = 'eof'
	TYPE_INT = 'int'
	TYPE_FLOAT = 'float'
	TYPE_BOOL = 'bool'
	TYPE_STRING = 'string'
	TYPE_IDENTIFIER = 'identifier'

	KEYWORD_FN = 'fn'
	KEYWORD_WHILE = 'while'
	KEYWORD_IF = 'if'
	KEYWORD_ELSE = 'else'
	KEYWORD_DO = 'do'
	KEYWORD_FOR = 'for'
	KEYWORD_LET = 'let'
	KEYWORD_RETURN = 'return'
	KEYWORD_BREAK = 'break'
	KEYWORD_CONTINUE = 'continue'
	KEYWORD_INCLUDE = 'include'

	OPERATOR_PLUS = '+'
	OPERATOR_MINUS = '-'
	OPERATOR_ASTERISK = '*'
	OPERATOR_SLASH = '/'
	OPERATOR_LPAREN = '('
	OPERATOR_RPAREN = ')'
	OPERATOR_LBRACE = '{'
	OPERATOR_RBRACE = '}'
	OPERATOR_EQ = '=='
	OPERATOR_NE = '!='
	OPERATOR_LT = '<'
	OPERATOR_LE = '<='
	OPERATOR_GT = '>'
	OPERATOR_GE = '>='
	OPERATOR_ASSIGN = '='
	OPERATOR_BTW_SHL = '<<'
	OPERATOR_BTW_SHR = '>>'
	OPERATOR_NOT = '!'
	OPERATOR_AND = '&&'
	OPERATOR_OR = '||'
	OPERATOR_BTW_NOT = '~'
	OPERATOR_BTW_AND = '&'
	OPERATOR_BTW_OR = '|'
	OPERATOR_BTW_XOR = '^'
	OPERATOR_SEMICOLON = ';'
	OPERATOR_COMMA = ','
	OPERATOR_PLUS_ASSIGN = '+='
	OPERATOR_MINUS_ASSIGN = '-='
	OPERATOR_ASTERISK_ASSIGN = '*='
	OPERATOR_SLASH_ASSIGN = '/='
	OPERATOR_LBRACKET = '['
	OPERATOR_RBRACKET = ']'


class Token:
	def __init__(self, position, typ, value):
		self.position = position
		self.type = typ
		self.value = value
	
	def __repr__(self):
		return f'{self.position}: {self.value}, {self.type}'

