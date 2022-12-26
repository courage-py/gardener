from typing import NoReturn
from gardener import Scope, Node, register_hook


class TestClass:
    def test_basic(self):

        basic_scope = Scope("basic")

        @register_hook("basic")
        def _(_) -> NoReturn:
            raise ValueError("shouldn't run")

        @basic_scope.register_hook("basic")
        def _(node: Node) -> Node:
            node["x"] += 1
            return node

        node = basic_scope.make_node("basic", x=16545)
        assert node["x"] == 16546
        assert node.scope is basic_scope
