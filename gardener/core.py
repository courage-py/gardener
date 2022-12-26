from __future__ import annotations
from json import JSONEncoder, dumps
from typing import Any, Callable, Tuple


NodeKey = Tuple[str, ...]
HookType = Callable[["Node"], Any]


class Scope:
    def __init__(self, key: str = ""):
        self.key = key
        self.hooks: dict[NodeKey, list[HookType]] = {}

    def register_hook(self, *keys: NodeKey | str) -> Callable[[HookType], HookType]:
        def reg_hook_inner(func: HookType):
            for key in keys:
                if isinstance(key, str):
                    key = (key,)
                self.hooks[key] = self.hooks.get(key, [])
                self.hooks[key].append(func)
            return func

        return reg_hook_inner

    def apply_hooks(self, node: Node) -> Any:
        if node.key in self.hooks:
            for hook in self.hooks[node.key]:
                old_key = node.key
                new_node = hook(node)

                if not isinstance(new_node, Node):
                    return new_node

                if new_node.key != old_key:
                    return self.apply_hooks(new_node)

                node = new_node
        return node

    def make_node(self, key: NodeKey | str, **props: Any) -> Any:
        node = Node(key, props, self)
        return self.apply_hooks(node)


class NodeJSON(JSONEncoder):
    def default(self, obj: Any):
        if isinstance(obj, Node):
            key = ":".join(obj.key)

            return {
                "key": key,
                "props": obj.props,
            }
        return super().default(obj)


class Node:
    key: NodeKey

    def __init__(self, key: NodeKey | str, props: dict[str, Any], scope: Scope):
        self.set_key(key)
        self.props = props
        self.scope = scope

    def pretty(self, **kwargs) -> str:
        kwargs = {"indent": 2, "cls": NodeJSON, **kwargs}
        return dumps(self, **kwargs)

    def __getitem__(self, item: str | tuple[str, Any]):
        if isinstance(item, str):
            return self.props[item]
        return self.props.get(*item)

    def __setitem__(self, item: str, value: Any):
        self.props[item] = value

    def transform(self) -> Any:
        return self.scope.apply_hooks(self)

    def set_key(self, key: str | NodeKey):
        if isinstance(key, str):
            key = (key,)

        self.key = key


default_scope = Scope("default")
register_hook = default_scope.register_hook
make_node = default_scope.make_node
