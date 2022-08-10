#include "include/heap.hxx"

void Heap::start()
{
	for (vm_int address = 0; address < HEAP_MAX; address++)
	{
		if (address == HEAP_NULL)
			heap_table[address] = HEAP_RESERVED;

		else
			heap_table[address] = HEAP_FREE;
	}
}

vm_int Heap::alloc()
{
	for (vm_int address = 0; address < HEAP_MAX; address++)
	{
		if (heap_table[address] == HEAP_FREE)
			return address;
	}

	MEMORY_OVERFLOW_ERROR;
	return 0;
}

void Heap::free(vm_int address)
{
	heap_table[address] = HEAP_FREE;
}

Heap *new_heap()
{
	Heap *heap = (Heap*)malloc(sizeof(Heap));
	return heap;
}

