# Lang Compiler
# Author: Jonas

class Position:
	def __init__(self, file_name, line, column):
		self.file_name = file_name
		self.line = line
		self.column = column
	
	def __repr__(self):
		return f'{self.file_name}:{self.line}:{self.column}'

