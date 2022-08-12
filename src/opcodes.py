# Lang Compiler
# Author: Jonas

class OpCodes:
	HLT =  0  # halt
	LDI =  1  # load int <value>
	LDF =  2  # load float <value>
	LDS =  3  # load string <value>
	STO =  4  # store <name>
	LDV =  5  # load variable
	JMP =  6  # jump <address>
	JPT =  7  # jump true <address>
	JPF =  8  # jump false <address>
	CAL =  9  # call <address>
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
	LET = 31  # let <name>
	BNT = 32  # bitwise not
	SHL = 33  # shift left
	SHR = 34  # shift right
	XOR = 35  # xor
	BOR = 36  # bitwise or
	BND = 37  # bitwise and
	EXT = 38  # exit
	POP = 39  # pop
	LDL = 40  # load list <number of values>
	GET = 41  # get
	APD = 42  # append
	LPP = 43  # list pop
	LEN = 44  # length
	CPY = 45  # copy
	TYP = 46  # type
	SET = 47  # set
	FOP = 48  # file open
	FWT = 49  # file write
	FRD = 50  # file read
	FCL = 51  # file close
	FRL = 52  # read line

