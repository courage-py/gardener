from gardener import Node, make_node
import pytest


class TestClass:
    def test_node_creation(self):
        node = make_node("node_basic", a=1, b=2)

        assert isinstance(node, Node)
        assert node.key == ("node_basic",)
        assert node.props["a"] == 1
        assert node.props["b"] == 2

    def test_props(self):
        node = make_node("node_props", a=1)

        assert node["a"] == 1
        assert node["b", 68] == 68
        node["b"] = 93
        assert node["b"] == 93

    def test_pretty(self):
        node = make_node("node_pretty", a=834, b="test")
        assert (
            node.pretty()
            == '{\n  "key": "node_pretty",\n  "props": {\n    "a": 834,\n    "b": "test"\n  }\n}'
        )

        node2 = make_node("node_pretty2", a=set())

        with pytest.raises(TypeError):
            node2.pretty()
