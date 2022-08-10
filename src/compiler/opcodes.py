# Lang Compiler
# Author: Jonas

class OpCodes:
	HLT =  0  # halt
	LDI =  1  # load int
	LDF =  2  # load float
	LDS =  3  # load string
	STO =  4  # store
	LDV =  5  # load variable
	JMP =  6  # jump
	JPT =  7  # jump true
	JPF =  8  # jump false
	CAL =  9  # call
	RET = 10  # return
	LDN = 11  # load nil
	NOP = 12  # noop
	WRT = 13  # write
	ADD = 14  # add
	SUB = 15  # sub
	MUL = 16  # mul
	DIV = 17  # div
	EQ  = 18  # equal
	NE  = 19  # not equal
	LT  = 20  # less than
	LE  = 21  # less or equal than
	GT  = 22  # greater than
	GE  = 23  # greate or equal than
	AND = 24  # and
	OR  = 25  # or
	NOT = 26  # not
	NEG = 27  # negate
	DUP = 28  # duplicate
	INC = 29  # increment
	DEC = 30  # decrement

