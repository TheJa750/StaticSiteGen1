import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props(self):
        node = HTMLNode(None,None,None,{"href":"https://www.google.com",
                                        "target": "_blank"})
        node1 = HTMLNode(None,None,None,None)
        node2 = HTMLNode(None,None,None,{})
        test_str = " href='https://www.google.com' target='_blank'"
        self.assertEqual(node.props_to_html(), test_str)
        self.assertEqual(node1.props_to_html(), "")
        self.assertEqual(node2.props_to_html(), "")
    
    def test_repr(self):
        node = HTMLNode()
        node1 = HTMLNode("h1","Hello World!")
        self.assertEqual(repr(node), "HTMLNode(None, None, None, None)")
        self.assertEqual(repr(node1),"HTMLNode(h1, Hello World!, None, None)")

    def test_children(self):
        child1 = HTMLNode(tag="span",value="Child 1")
        child2 = HTMLNode(tag="span",value="Child 2",props={"class": "highlight"})
        parent = HTMLNode(tag="div", value=None,children=[child1, child2],props={"id": "container"})

        child1_repr = "HTMLNode(span, Child 1, None, None)"
        child2_repr = "HTMLNode(span, Child 2, None, {'class': 'highlight'})"
        parent_repr = "HTMLNode(div, None, [{}, {}], {{'id': 'container'}})".format(child1_repr,child2_repr)

        self.assertEqual(repr(child1), child1_repr)
        self.assertEqual(repr(child2), child2_repr)
        self.assertEqual(repr(parent), parent_repr)

        self.assertEqual(child1.props_to_html(), "")
        self.assertEqual(child2.props_to_html(), " class='highlight'")
        self.assertEqual(parent.props_to_html(), " id='container'")

    def test_leafnode(self):
        node = LeafNode("Hello World!", "b")
        node_html = "<b>Hello World!</b>"
        node1 = LeafNode("Click here.", "a", {"href": "https://www.google.com"})
        node1_html = "<a href='https://www.google.com'>Click here.</a>"
        node2 = LeafNode("I have no tag")
        node3 = LeafNode("Fancy & <Characters>", "h1")

        self.assertEqual(node.to_html(), node_html)
        self.assertEqual(node1.to_html(), node1_html)
        self.assertEqual(node2.to_html(), "I have no tag")
        self.assertEqual(node3.to_html(), "<h1>Fancy & <Characters></h1>")

    def test_empty_None_leafnode(self):
        for invalid in [None, ""]:
            with self.assertRaises(ValueError):
                LeafNode(invalid)

    def test_parentnode_normal(self):
        child = LeafNode("Hello World!", "b")
        child1 = LeafNode("Click here.", "a", {"href": "https://www.google.com"})
        child2 = LeafNode("Fancy & <Characters>", "h1")
        node = ParentNode([child, child1, child2], "p")
        node_str = f"<p>{child.to_html()}{child1.to_html()}{child2.to_html()}</p>"

        self.assertEqual(node.to_html(), node_str)

    def test_parentnode_emptyNone_children(self):
        for invalid in [None]:
            with self.assertRaises(ValueError):
                ParentNode(invalid, "p")

    def test_parentnode_emptyNone_tag(self):
        child = LeafNode("Hello World!", "b")
        for invalid in [None, ""]:
            with self.assertRaises(ValueError):
                ParentNode([child], invalid)
    
    def test_nested_parentnode(self):
        child = LeafNode("Hello World!", "b")
        child1 = LeafNode("Click here.", "a", {"href": "https://www.google.com"})
        child2 = LeafNode("Fancy & <Characters>", "h1")
        node = ParentNode([child, child1], "p")
        node1 = ParentNode([node, child2], "h1")
        node1_str = f"<h1>{node.to_html()}{child2.to_html()}</h1>"

        self.assertEqual(node1.to_html(), node1_str)

if __name__ == "__main__":
    unittest.main()