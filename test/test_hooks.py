from gardener import Node, make_node, register_hook


class TestClass:
    def test_basic_transform(self):
        @register_hook("basic_transform")
        def _(node: Node) -> str:
            return f"{node.key[0]}:{node['x']}"

        node = make_node("basic_transform", x=16545)
        assert node == "basic_transform:16545"

    def test_order(self):
        @register_hook("order")
        def _(node: Node) -> Node:
            node["xs"].append(1)
            return node

        @register_hook("order")
        def _(node: Node) -> Node:
            node["xs"].append(2)
            return node

        @register_hook("order")
        def _(node: Node) -> Node:
            node["xs"].append(3)
            return node

        @register_hook("order")
        def _(node: Node) -> Node:
            node["xs"].append(4)
            return node

        node = make_node("order", xs=[])

        assert node["xs"] == [1, 2, 3, 4]

    def test_edit(self):
        @register_hook("edit")
        def _(node: Node) -> Node:
            node["x"] += 1
            return node

        @register_hook("edit")
        def _(node: Node) -> str:
            return f"{node.key[0]}:{node['x']}"

        node = make_node("edit", x=16545)
        assert node == "edit:16546"

    def test_new_node(self):
        @register_hook("type_a")
        def _(node: Node) -> Node:
            node.set_key("type_b")
            return node

        @register_hook("type_b")
        def _(node: Node) -> float:
            return node["x"]

        value = make_node("type_a", x=67)

        assert value == 67

    def test_multiple_transform(self):
        @register_hook("multiple_transform")
        def _(node: Node) -> Node:
            node["x"] = node["x", 0] + 1
            return node

        node = make_node("multiple_transform")

        assert node["x"] == 1

        node = node.transform().transform().transform()

        assert node["x"] == 4
