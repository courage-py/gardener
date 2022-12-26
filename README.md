[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/courage-tci/gardener/build.yml?branch=pub)](https://github.com/courage-tci/gardener/actions/workflows/build.yml)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/courage-tci/gardener/test.yml?branch=pub&label=tests)](https://github.com/courage-tci/gardener/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/gardener)](https://pypi.org/project/gardener/)
![PyPI - Downloads](https://pepy.tech/badge/gardener)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gardener)
[![Coveralls](https://img.shields.io/coverallsCoverage/github/courage-tci/gardener?label=test%20coverage)](https://coveralls.io/github/courage-tci/gardener?branch=pub)
![License](https://img.shields.io/github/license/courage-tci/gardener)
![Badge Count](https://img.shields.io/badge/badges-8-important)

**gardener** is a simple tree manipulation module. It provides a hook-based tree transformation.

## Installation

`gardener` is available on PyPi:    

`python -m pip install gardener` (or any other package manager)

## Basic example

This is a simple example usage, a hook that transforms every `tag` node into a string:


```python
from gardener import make_node, register_hook, Node


@register_hook("tag")
def tag_hook(node: Node) -> str:
    return f"tag:{node['i']}{node['children', []]}"


x: str = make_node(
    "tag",
    children=[
        make_node("tag", i=i) 
        for i in range(10)
    ],
    i=99
)

print(x) # tag:99['tag:0[]', 'tag:1[]', 'tag:2[]', 'tag:3[]', 'tag:4[]', 'tag:5[]', 'tag:6[]', 'tag:7[]', 'tag:8[]', 'tag:9[]']
```

## Combining hooks and transforming nodes

```python
from gardener import make_node, register_hook, Node
from operator import add, sub, mul, truediv


operators = {
    "+": add,
    "-": sub,
    "*": mul,
    "/": truediv
}

@register_hook("+", "-", "*", "/")
def binary_expr(node: Node) -> float:
    op = node.key[0] # node.key is a 1-element tuple, e.g. ('+', )
    op_func = operators[op]
    
    parts = node["parts", []]
    
    if not parts:
        if op in "+-":
            return 0 # empty sum
        return 1 # empty product
    
    result = parts[0]
    
    for i in range(1, len(parts)):
        result = op_func(result, parts[i])
    
    return result


x: float = make_node(
    "+",
    parts=[
        3,
        make_node("*", parts=[5, 6]) # 30
    ]
)

print(x) # 33
```

Let's add exponentiation to this calculator. The trick is that power is right-associative (so that `2 ** 2 ** 3` equals `2 ** (2 ** 3)`, not `(2 ** 2) ** 3`).    
You can obviously write a separate hook for that, but we can just combine hooks:

```python
from gardener import make_node, register_hook, Node
from operator import add, sub, mul, truediv


operators = {
    "+": add,
    "-": sub,
    "*": mul,
    "/": truediv,
    "**": lambda x, y: pow(y, x) # reversing order there, so that we can reverse the order of all elements
}

"""

This hook, instead of producing a new non-node value, just edits the node contents.
This allows the hook chain to continue to `binary_expr` hook

Be aware that the order of hook apply is the same as their registration.

"""
@register_hook("**")
def power_reverse(node: Node) -> Node:
    node["parts"] = node["parts", []][::-1]
    return node


@register_hook("+", "-", "*", "/", "**")
def binary_expr(node: Node) -> float:
    op = node.key[0] # node.key is a 1-element tuple, e.g. ('+', )
    op_func = operators[op]
    
    parts = node["parts", []]
    
    if not parts:
        if op in "+-":
            return 0 # empty sum
        return 1 # empty product
    
    result = parts[0]
    
    for i in range(1, len(parts)):
        result = op_func(result, parts[i])
    
    return result


x: float = make_node(
    "+",
    parts=[
        3,
        make_node("*", parts=[5, 6]), # 30
        make_node("**", parts=[2, 2, 3]) # 256
    ]
)

print(x) # 289
```

This, of course, may not be the most efficient or obvious way, but `gardener` doesn't impose any restrictions on how you might approach a problem

## Node props

Examples above have shown how to set initial props of a `Node`. To get and edit those props, use bracket notation:


```python
from gardener import make_node

node = make_node("test")

node["a"] = 10 # accepts any type of value, but key must be a string
print(node["a"]) # prints 10
print(node["b", 0]) # prints 0 (default value)
print(node["b"]) # raises KeyError

```

## Hook evaluation order

Hook ordering is simple:

1. Hooks run at the node creation, there is no way to get a node that wasn't processed with relevant hooks (if there were any) 
    *except creating a `Node` object directly, which is discouraged*
2. Hooks are run in registration order, because when you register a hook, it's appended to the end of the list for that key. 
    *you can change the order by editing `scope.hooks[key]` directly (check Scopes below)*

## Scoping

Often it is convenient to have different trees in one project, using different hooks.    
While this can be done through namespacing (`make_node` actually also accepts node key as a `str | tuple[str, ...]`), that approach would force you to write long names in node creating and hook registration.    

`gardener` provides you with a more convenient approach: `Scope` objects. A scope is an isolated store with hooks:

```python
from gardener import Scope, Node


scope1 = Scope("scope1") # key is optional and it doesn't affect scope behaviour
scope2 = Scope("scope2")


@scope1.register_hook("i")
def print_stuff_1(node: Node) -> Node:
    print("this is the first scope")
    return node

@scope2.register_hook("i")
def print_stuff_2(node: Node) -> Node:
    print("this is the second scope")
    return node

@scope1.register_hook("i")
@scope2.register_hook("i")
def print_stuff_both(node: Node) -> Node:
    print("this is both scopes")
    return node


# prints "this is the first scope"
# prints "this is both scopes"
scope1.make_node("i")


# prints "this is the second scope"
# prints "this is both scopes"
scope2.make_node("i")
```

You can get all of the scope hooks with `scope.hooks`. It has type `dict[tuple[str, ...], list[HookType]]`.    
To get the scope of the current node (e.g. in a hook, use `node.scope`)    

Global `make_node` and `register_hook` are, in fact, methods of `gardener.core.default_scope`


## Applying hooks multiple times

To apply a hook to a node multiple times, call `node.transform()` — it would return the result of another chain of transformations.    
**Be careful about using it in hooks, as this could easily lead to infinite recursion if not handled properly.**    

## Node printing

If your node props are JSON-serializable, you can run `node.pretty(**dumps_kwargs)` to get a pretty indented JSON representation of the node.    
Node class itself is JSON-serializable (only with `NodeJSON` as an encoder).

To represent non-JSON-serializable data, you will need to provide an encoder class:

```python
from gardener import make_node
from gardener.core import NodeJSON
from typing import Any


class SomeCoolDataClass: # your custom class
    def __init__(self, x: int):
        self.x = x


class MyNodeJSON(NodeJSON):
    def default(self, obj: Any):
        if isinstance(obj, SomeCoolDataClass):
            return f"SomeCoolDataClass<{obj.x}>" # return any serializable data here (can contain nodes or, e.g. SomeCoolDataClass inside)
        return super().default(obj)


node = make_node(
    "cool_data_node",
    cool_data=SomeCoolDataClass(6)
)

print(
    node.pretty(cls=MyNodeJSON) # accepts same arguments (keyword-only) as json.dumps
)
"""
{
  "key": "cool_data_node",
  "props": {
    "cool_data": "SomeCoolDataClass<6>"
  }
}
"""
```