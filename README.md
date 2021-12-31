# gardener - simple tree manipulation module

## Basic usage

```python
from gardener import Node, register_hook

@register_hook("child")
def child(node):
    return Node.another_child(
        values=[value * 2 for value in node.values]
    )


tree = Node.root(
    value=56,
    some_property=Node.child(
        values=[10, 20, 80]
    )
)


print(tree.pretty())
"""
{
  "key": "root",
  "props": {
    "value": 56,
    "some_property": {
      "key": "another_child",
      "props": {
        "values": [
          20,
          40,
          160
        ]
      }
    }
  }
}
"""
```

## Installation

`python -m pip install gardener`

## Getting started

Gardener is useful for tree manipulation (building and transforming complex trees)

To start working with it, you need to understand a few concepts:

*hook* is a function called on node creation. It can create a brand new node or change current one.    
*node* is an object with a *key* - string identifier and *props* - an arbitrary dictionary

## Building a tree

To build a tree, you can use `Node.name[.name2.name3...](**props)`:

```python
from gardener import Node


root = Node.root() # props={}, key="root"
oak = Node.tree.oak(age=23) # props={"age": 23}, key="tree:oak"
long_name = Node.very.long.node.key() # props={}, key="very:long:node:key"
```

Arbitrary name length makes it possible to create namespaces:

```python
from gardener import Node

tree = Node.tree

tree.oak(age=23) # props={"age": 23}, key="tree:oak"
tree.pine(age=2) # props={"age": 2}, key="tree:pine"

```

## Hooks

To transform your tree, you can define any number of hooks.    
Hooks are called on node creation, in order they were defined - hooks defined earlier would be called earlier.    

A hook is just a function getting node as argument and returning a transformed node.    
To define hook, use `register_hook(key)`:    

```python
from gardener import Node, register_hook

@register_hook("car")
def make_any_car_faster(node):
    node.engine.horsepower = node.engine.horsepower * 5
    return node

@register_hook("engine")
def engine_tweak(node):
    node.horsepower -= 1
    return node

@register_hook("car")
def no_red_cars(node):
    if node.color == "red":
        node.color = "black"
    return node

@register_hook("car")
def make_supercar(node):
    if node.engine.horsepower > 500:
        return Node.supercar(**node.props)
    return node

parking_lot = Node.lot(
    cars=[
        Node.car(
            engine=Node.engine(horsepower=100),
            color="red"
        ),
        Node.car(
            engine=Node.engine(horsepower=200),
            color="white"
        ),
        Node.car(
            engine=Node.engine(horsepower=205),
            color="red"
        ),
    ]
)
# notice how car.engine.horsepower is (x - 1) * 5 because engine is created before the car
print(parking_lot.pretty())
"""
{
  "key": "lot",
  "props": {
    "cars": [
      {
        "key": "car",
        "props": {
          "engine": {
            "key": "engine",
            "props": {
              "horsepower": 495
            }
          },
          "color": "black"
        }
      },
      {
        "key": "supercar",
        "props": {
          "engine": {
            "key": "engine",
            "props": {
              "horsepower": 995
            }
          },
          "color": "white"
        }
      },
      {
        "key": "supercar",
        "props": {
          "engine": {
            "key": "engine",
            "props": {
              "horsepower": 1020
            }
          },
          "color": "black"
        }
      }
    ]
  }
}
"""
```

*Important notes*:    
- if your hook changes existing node (but key remains the same) - use node.copy() or make changes in place.    
- if you change the key of the node, make a new node.    

First is needed to avoid infinite recursion (otherwise your hook would be called again and again on the same node).    
Second is needed to ensure hooks are called on the new node.    

## Pretty printing

Gardener uses built-in `json` module to make a pretty-printed tree:

```python
from gardener import Node

print(Node.tree.oak(age=23).pretty())
"""
{
  "key": "tree:oak",
  "props": {
    "age": 23
  }
}
"""
```

If your values are JSON serializable, this would work out-of-the-box.    
Otherwise you will need to extend GardenerJSON class:

```python
from gardener import Node, GardenerJSON

class MyGardenerJSON(GardenerJSON):
    def default(self, obj):
        if obj is Ellipsis:
            return "..." # return any JSON serializable object
        return super().default(obj)

# Ellipsis is not JSON serializable
print(Node.tree.oak(cool_object=Ellipsis).pretty(cls=MyGardenerJSON))
"""
{
  "key": "tree:oak",
  "props": {
    "cool_object": "..."
  }
}
"""

```

In fact, `Node.pretty` accepts any keyword argument of `json.dumps`