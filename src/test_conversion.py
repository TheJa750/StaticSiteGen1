from conversion import textnode_to_htmlnode, split_nodes_delimiter, \
                  extract_markdown_images, extract_markdown_links, \
                  split_nodes_image, split_nodes_link, text_to_textnodes, \
                  markdown_to_blocks, block_to_block_type, markdown_to_html_node, \
                  block_type_paragraph, block_type_heading, block_type_code, \
                  block_type_olist, block_type_ulist, block_type_quote
from htmlnode import LeafNode, ParentNode, HTMLNode
from textnode import TextNode

import unittest

class ConvertNode(unittest.TestCase):
    def test_simple_node(self):
        node = TextNode("Hello World!", "text")
        conv_node = textnode_to_htmlnode(node)
        html_repr = "HTMLNode(None, Hello World!, None, None)"

        self.assertEqual(repr(conv_node),html_repr)

    def test_link_node(self):
        node = TextNode("Click me!", "link", "http://www.google.com")
        conv_node = textnode_to_htmlnode(node)
        html_repr = "HTMLNode(a, Click me!, None, {'href': 'http://www.google.com'})"

        self.assertEqual(repr(conv_node),html_repr)

    def test_wrong_type(self):
        node = TextNode("Hello World!", "txt")

        with self.assertRaises(Exception) as context:
            textnode_to_htmlnode(node)

        self.assertTrue("Text type not supported." in str(context.exception))

class SplitNodeDelimiter(unittest.TestCase):
    def test_splitting_code(self):
        delimiter = "`"
        old_nodes = [TextNode("Hello World!", "text"),
                     TextNode("This is text with a `code block` word", "text"),
                     TextNode("Hopefully `print(Hello World)` works as I hoped", "text"),
                     TextNode("This is a **bold** word and an *italic* word", "text")
                    ]
        expected = [TextNode("Hello World!", "text"),
                    TextNode("This is text with a ", "text"),
                    TextNode("code block", "code"),
                    TextNode(" word", "text"),
                    TextNode("Hopefully ", "text"),
                    TextNode("print(Hello World)", "code"),
                    TextNode(" works as I hoped", "text"),
                    TextNode("This is a **bold** word and an *italic* word", "text")
                    ]
        self.assertEqual(split_nodes_delimiter(old_nodes,delimiter), expected)

    def test_splitting_bold(self):
        delimiter = "**"
        old_nodes = [TextNode("Hello World!", "text"),
                     TextNode("This is text with a **bold** word", "text"),
                     TextNode("Hopefully **my code** works as I hoped", "text")
                    ]
        expected = [TextNode("Hello World!", "text"),
                    TextNode("This is text with a ", "text"),
                    TextNode("bold", "bold"),
                    TextNode(" word", "text"),
                    TextNode("Hopefully ", "text"),
                    TextNode("my code", "bold"),
                    TextNode(" works as I hoped", "text")
                    ]
        self.assertEqual(split_nodes_delimiter(old_nodes,delimiter), expected)

    def test_splitting_italic(self):
        delimiter = "*"
        old_nodes = [TextNode("Hello World!", "text"),
                     TextNode("This is text with an *italic* word", "text"),
                     TextNode("Hopefully *my code* works as I hoped", "text")
                    ]
        expected = [TextNode("Hello World!", "text"),
                    TextNode("This is text with an ", "text"),
                    TextNode("italic", "italic"),
                    TextNode(" word", "text"),
                    TextNode("Hopefully ", "text"),
                    TextNode("my code", "italic"),
                    TextNode(" works as I hoped", "text")
                    ]
        new_nodes = split_nodes_delimiter(old_nodes, delimiter)
        self.assertEqual(new_nodes, expected)

    def test_delim_bold_and_italic(self):
        node = TextNode("**bold** and *italic*", "text")
        new_nodes = split_nodes_delimiter([node], "**")
        expected = [TextNode("bold", "bold"),
                    TextNode(" and *italic*", "text")
                    ]
        self.assertEqual(new_nodes, expected)
        new_nodes = split_nodes_delimiter(new_nodes, "*")
        expected1 = [TextNode("bold", "bold"),
                    TextNode(" and ", "text"),
                    TextNode("italic", "italic")
        ]
        self.assertEqual(new_nodes, expected1)

class ExtractMarkdown(unittest.TestCase):
    def test_extract_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev)"
        )
        self.assertListEqual(
            [
                ("link", "https://boot.dev"),
                ("another link", "https://blog.boot.dev"),
            ],
            matches,
        )

class ExtractLinksImages(unittest.TestCase):
    def test_no_links_images(self):
        node1 = TextNode("This is plain text.", "text")
        node2 = TextNode("This is plain text.", "text")
        new_nodes1 = split_nodes_link([node1])
        new_nodes2 = split_nodes_image([node2])
        
        self.assertEqual([node1], new_nodes1)
        self.assertEqual([node2], new_nodes2)

    def test_links_no_images(self):
        node1 = TextNode("This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)", "text")
        node2 = TextNode("This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)", "text")
        new_nodes1 = split_nodes_link([node1])
        new_nodes2 = split_nodes_image([node2])
        expected = [TextNode("This is text with a link ", "text"),
                    TextNode("to boot dev", "link", "https://www.boot.dev"),
                    TextNode(" and ", "text"),
                    TextNode("to youtube", "link", "https://www.youtube.com/@bootdotdev")
                    ]
        
        self.assertEqual(new_nodes1, expected)
        self.assertEqual([node2], new_nodes2)

    def test_images_no_links(self):
       #node1 = TextNode(
    #"This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
    #"text")
       node2 = TextNode(
    "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
    "text")
       #new_nodes1 = split_nodes_link([node1])
       new_nodes2 = split_nodes_image([node2])
       expected = [TextNode("This is text with a ", "text"),
                   TextNode("rick roll", "image", "https://i.imgur.com/aKaOqIh.gif"),
                   TextNode(" and ", "text"),
                   TextNode("obi wan", "image", "https://i.imgur.com/fJRm4Vk.jpeg")
                   ]
       
       #self.assertEqual([node1], new_nodes1)
       self.assertEqual(new_nodes2, expected)

    def test_links_and_images(self):
        #node1 = TextNode(
        #    "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and a link [to boot dev](https://www.boot.dev)", "text"
        #)
        node2 = TextNode(
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and a link [to boot dev](https://www.boot.dev)", "text"
        )
        #new_nodes1 = split_nodes_link([node1])
        new_nodes2 = split_nodes_image([node2])
        #expected1 = [TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and a link ", "text"),
        #             TextNode("to boot dev", "link", "https://www.boot.dev")
        #             ]
        expected2 = [TextNode("This is text with a ", "text"),
                     TextNode("rick roll", "image", "https://i.imgur.com/aKaOqIh.gif"),
                     TextNode(" and a link [to boot dev](https://www.boot.dev)", "text")
                     ]
        
        #self.assertEqual(new_nodes1, expected1)
        self.assertEqual(new_nodes2, expected2)

class TextToTextNodes(unittest.TestCase):
    def given_text(self):
        text = "This is **text** with an *italic* word and a `code block` and an \
            ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        textnodes = text_to_textnodes(text)
        expected = [
                    TextNode("This is ", "text"),
                    TextNode("text", "bold"),
                    TextNode(" with an ", "text"),
                    TextNode("italic", "italic"),
                    TextNode(" word and a ", "text"),
                    TextNode("code block", "code"),
                    TextNode(" and an ", "text"),
                    TextNode("obi wan image", "image", "https://i.imgur.com/fJRm4Vk.jpeg"),
                    TextNode(" and a ", "text"),
                    TextNode("link", "link", "https://boot.dev"),
                    ]
        self.assertEqual(textnodes, expected)

class MarkdownToBlocks(unittest.TestCase):
    def test_given_example(self):
        markdown = """# This is a heading

                    This is a paragraph of text. It has some **bold** and *italic* words inside of it.

                    * This is the first list item in a list block
                    * This is a list item
                    * This is another list item"""
        blocks = markdown_to_blocks(markdown)
        expected = ["# This is a heading",
                    "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
                    """* This is the first list item in a list block
                    * This is a list item
                    * This is another list item"""
                    ]
        
        self.assertEqual(blocks, expected)
    
    def test_no_content(self):
        markdown = ""
        blocks = markdown_to_blocks(markdown)
        expected = []
        self.assertEqual(blocks, expected)

    def test_multiple_blank_lines(self):
        markdown = """# Heading
        
        
        Paragraph with excessive blank lines.



        Just for good measure here is another."""
        blocks = markdown_to_blocks(markdown)
        expected = ["# Heading",
                    "Paragraph with excessive blank lines.",
                    "Just for good measure here is another."]
        self.assertEqual(blocks, expected)

    def test_no_blank_lines(self):
        markdown = "# Just a single line with no blank lines."
        blocks = markdown_to_blocks(markdown)
        expected = ["# Just a single line with no blank lines."]
        self.assertEqual(blocks, expected)

class BlockToBlockType(unittest.TestCase):
    def test_all_types(self):
        blocks = ["Hello World!",
               "# Heading",
               "Another text line.",
               "```\nLong\nCode\nBlock\n```",
               "* Unordered list",
               "> Quote Block",
               "1. Ordered list"]
        expected = ["paragraph", "heading", "paragraph", "code","unordered", "quote", "ordered"]
        results = []
        for block in blocks:
            results.append(block_to_block_type(block))
        
        self.assertEqual(results, expected)
    
    def test_empty_string(self):
        blocks = ""
        with self.assertRaises(ValueError) as context:
            block_to_block_type(blocks)

        self.assertTrue("Block cannot be empty." in str(context.exception))

    # def test_long_ordered_list(self):
    #     blocks = ["1. Hello", "2. world,", "3. are", "4. you", "5. listening",
    #               "6. I know", "7. you", "8. can", "9. hear", "10. me"]
    #     expected = ["ordered", "ordered", "ordered", "ordered", "ordered", "ordered",
    #                 "ordered", "ordered", "ordered", "ordered"]
    #     results = []
    #     for block in blocks:
    #         results.append(block_to_block_type(block))

    #     self.assertEqual(results, expected)

    def test_long_number_text(self):
        block = "100 Reasons not to leave your house"
        expected = "paragraph"
        results = block_to_block_type(block)
        self.assertEqual(results, expected)

class TestMarkdownToHTML(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
                "* This is a list\n* with items",
            ],
        )

    def test_markdown_to_blocks_newlines(self):
        md = """
This is **bolded** paragraph




This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
                "* This is a list\n* with items",
            ],
        )

    def test_block_to_block_types(self):
        block = "# heading"
        self.assertEqual(block_to_block_type(block), block_type_heading)
        block = "```\ncode\n```"
        self.assertEqual(block_to_block_type(block), block_type_code)
        block = "> quote\n> more quote"
        self.assertEqual(block_to_block_type(block), block_type_quote)
        block = "* list\n* items"
        self.assertEqual(block_to_block_type(block), block_type_ulist)
        block = "1. list\n2. items"
        self.assertEqual(block_to_block_type(block), block_type_olist)
        block = "paragraph"
        self.assertEqual(block_to_block_type(block), block_type_paragraph)

    def test_paragraph(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p></div>",
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with *italic* text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_lists(self):
        md = """
- This is a list
- with items
- and *more* items

1. This is an `ordered` list
2. with items
3. and more items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is a list</li><li>with items</li><li>and <i>more</i> items</li></ul><ol><li>This is an <code>ordered</code> list</li><li>with items</li><li>and more items</li></ol></div>",
        )

    def test_headings(self):
        md = """
# this is an h1

this is paragraph text

## this is an h2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>this is an h1</h1><p>this is paragraph text</p><h2>this is an h2</h2></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

this is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a blockquote block</blockquote><p>this is paragraph text</p></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

this is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a blockquote block</blockquote><p>this is paragraph text</p></div>",
        )


if __name__ == "__main__":
    unittest.main()