#ifndef _HEAP_HXX
#define _HEAP_HXX 1

#include <cstdint>

#include "error.hxx"
#include "stack.hxx"
#include "vm_types.hxx"

#define HEAP_MAX 8192
#define HEAP_RESERVED 1

#define HEAP_FREE 0
#define HEAP_NULL 0 // null address in heap memory

struct Heap
{
	StackValue *heap[HEAP_MAX];
	uint8_t heap_table[HEAP_MAX];

	void start();
	vm_int alloc();
	void free(vm_int address);
};

Heap *new_heap();

#endif

