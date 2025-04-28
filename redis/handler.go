package main

func ping(args []Value) Value {
	return Value{typ: "string", str: "PONG"}
}

var Handlers = map[string]func([]Value) Value{
	"PING": ping,
}
