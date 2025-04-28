package main

import "sync"

func ping(args []Value) Value {
	if len(args) == 0 {
		return Value{typ: "string", str: "PONG"}
	}

	return Value{typ: "string", str: args[0].bulk}
}

var (
	SETs   = map[string]string{}
	SETsMu = sync.RWMutex{}
)

func set(args []Value) Value {
	if len(args) != 2 {
		return Value{typ: "error", str: "ERR wrong number of arguments for 'set'"}
	}

	key := args[0].bulk
	value := args[1].bulk

	SETsMu.Lock()
	SETs[key] = value
	SETsMu.Unlock()

	return Value{typ: "string", str: "OK"}
}

func get(args []Value) Value {
	if len(args) != 1 {
		return Value{typ: "error", str: "ERR wrong number of arguments for 'get'"}
	}

	key := args[0].bulk

	SETsMu.Lock()
	value, ok := SETs[key]
	if !ok {
		return Value{typ: "null"}
	}
	SETsMu.Unlock()
	return Value{typ: "bulk", bulk: value}
}

var Handlers = map[string]func([]Value) Value{
	"PING": ping,
	"SET":  set,
	"GET":  get,
}
