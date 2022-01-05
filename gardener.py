from typing import Any, Dict
from json import dumps, JSONEncoder

hooks = {}


class GardenerJSON(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Node):
            return {
                "key": obj.key,
                "props": {key: value for key, value in obj.props.items()},
            }
        return super().default(obj)


class Namespace:
    def __init__(self, name):
        self.__NS_NAME__ = name

    def __call__(self, *keys, **props):
        return make_node(":".join([self.__NS_NAME__, *keys]), **props)

    def __getattr__(self, key):
        return Namespace(":".join([self.__NS_NAME__, key]))


class MetaNode(type):
    def __getattr__(self, attr):
        return Namespace(attr)


class Node(metaclass=MetaNode):
    def __init__(self, key: str, **props):
        self.key = key
        self.props: Dict[str, Any] = props.copy()

    def __getattr__(self, attr: str):
        return self[attr]

    def __getitem__(self, item: str):
        return self.props[item]

    def __setattr__(self, attr, value):
        if attr in ["key", "props"]:
            return super().__setattr__(attr, value)
        self[attr] = value

    def __setitem__(self, item: str, value):
        self.props[item] = value

    @staticmethod
    def render_prop(value):
        if isinstance(value, Node):
            return value.render()
        elif isinstance(value, list):
            return [Node.render_prop(v) for v in value]
        else:
            return value

    def pretty(self, **kwargs) -> str:
        kwargs = {"indent": 2, "cls": GardenerJSON, **kwargs}
        return dumps(self, **kwargs)

    def copy(self):
        return Node(self.key, **self.props)


def register_hook(key):
    def reg_hook_inner(func):
        hooks[key] = hooks.get(key, [])
        hooks[key].append(func)
        return func

    return reg_hook_inner


def make_node(key, **props):
    node = Node(key, **props)
    if key in hooks:
        for hook in hooks[key]:
            if key != node.key:
                return node
            node = hook(node)
    return node
