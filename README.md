# Lang

A simple compiler.

## Build
```
$ cd src/
$ make
```

## Hello World
```rust
fn main() {
	let message = "hello world!\n";
	write(message);
}
```

```
$ ./src/lang.py build hello.lang
$ ./src/vm hello.lang.vm
```

## TODO
- [ ] Virtual Machine
- [ ] Optimizer

