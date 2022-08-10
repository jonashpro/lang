#ifndef _ERROR_HXX
#define _ERROR_HXX

#include <cstdio>
#include <cstdlib>

#define ERROR(fmt, ...) { \
	fprintf(stderr, fmt, ##__VA_ARGS__); \
	exit(1); \
}

#define PANIC(fmt, ...) { \
	fprintf(stderr, "panic: "); \
	ERROR(fmt, ##__VA_ARGS__); \
}

#define INVALID_FILE_FORMAT_ERROR PANIC("invalid file format\n")

#define NO_SUCH_FILE_ERROR(file)  ERROR("no such file %s\n", file)

#define UNKNOWN_INSTRUCTION_ERROR(instr) { \
	PANIC("unknown instruction 0x%.2x\n", instr); \
}

#define STACK_OVERFLOW_ERROR PANIC("stack overflow\n")
#define STACK_UNDERFLOW_ERROR PANIC("stack underflow\n")

#define MEMORY_OVERFLOW_ERROR PANIC("memory overflow\n")

#endif

