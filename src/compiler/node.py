# Lang Compiler
# Author: Jonas

class Node:
	def __init__(self, position):
		self.position = position
	

class UnaryOperationNode(Node):
	def __init__(self, position, operator, left):
		super().__init__(position)
		self.operator = operator
		self.left = left
	
	def __repr__(self):
		return f'({self.operator} {self.left})'


class BinaryOperationNode(Node):
	def __init__(self, position, operator, left, right):
		super().__init__(position)
		self.operator = operator
		self.left = left
		self.right = right
	
	def __repr__(self):
		return f'({self.operator} {self.left} {self.right})'


class LiteralNode(Node):
	def __init__(self, position, value):
		super().__init__(position)
		self.value = value
	
	def __repr__(self):
		return f'{self.value}'


class IntNode(LiteralNode):
	def __init__(self, position, value):
		super().__init__(position, value)
		self.value = value
		

class FloatNode(LiteralNode):
	def __init__(self, position, value):
		super().__init__(position, value)
		self.value = value

		
class StringNode(LiteralNode):
	def __init__(self, position, value):
		super().__init__(position, value)
		self.value = value

	def __repr__(self):
		return f'"{self.value}"'


class LetNode(Node):
	def __init__(self, position, name, value):
		super().__init__(position)
		self.name = name
		self.value = value
	
	def __repr__(self):
		return f'(let {self.name} {self.value})'


class IdentifierNode(Node):
	def __init__(self, position, name):
		super().__init__(position)
		self.name = name
	
	def __repr__(self):
		return f'{self.name}'


class FnNode(Node):
	def __init__(self, position, name, arguments, body):
		super().__init__(position)
		self.name = name
		self.arguments = arguments
		self.body = body
	
	def __repr__(self):
		arguments_as_lisp_notation = '(' \
						+ str(self.arguments)[1:-1].replace(',', '') \
						+ ')'

		return f'(fn {self.name} {arguments_as_lisp_notation} {self.body})'


class BlockNode(Node):
	def __init__(self, position, body):
		super().__init__(position)
		self.body = body
	
	def __repr__(self):
		return f'{self.body}'


class IfNode(Node):
	def __init__(self, position, condition, if_body, else_body):
		super().__init__(position)
		self.condition = condition
		self.if_body = if_body
		self.else_body = else_body
	
	def __repr__(self):
		return f'(if {self.condition} {self.if_body} {self.else_body})'


class WhileNode(Node):
	def __init__(self, position, condition, body):
		super().__init__(position)
		self.condition = condition
		self.body = body
	
	def __repr__(self):
		return f'(while {self.condition} {self.body})'


class CallNode(Node):
	def __init__(self, position, name, arguments):
		super().__init__(position)
		self.name = name
		self.arguments = arguments
	
	def __repr__(self):
		return f'(call {self.name} {self.arguments})'


class ReturnNode(Node):
	def __init__(self, position, value):
		super().__init__(position)
		self.value = value
	
	def __repr__(self):
		return f'(return {self.value})'


class AssignNode(Node):
	def __init__(self, position, name, value):
		super().__init__(position)
		self.name = name
		self.value = value
	
	def __repr__(self):
		return f'(= {self.name} {self.value})'


class IncrementLeftNode(Node):
	def __init__(self, position, name):
		super().__init__(position)
		self.name = name
	
	def __repr__(self):
		return f'++{self.name}'


class IncrementRightNode(Node):
	def __init__(self, position, name):
		super().__init__(position)
		self.name = name
	
	def __repr__(self):
		return f'{self.name}++'


class DecrementLeftNode(Node):
	def __init__(self, position, name):
		super().__init__(position)
		self.name = name
	
	def __repr__(self):
		return f'--{self.name}'


class DecrementRightNode(Node):
	def __init__(self, position, name):
		super().__init__(position)
		self.name = name
	
	def __repr__(self):
		return f'{self.name}--'

