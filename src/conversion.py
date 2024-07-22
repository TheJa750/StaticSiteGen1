import re
from textnode import TextNode
from htmlnode import HTMLNode, LeafNode, ParentNode

block_type_paragraph = "paragraph"
block_type_heading = "heading"
block_type_code = "code"
block_type_quote = "quote"
block_type_olist = "ordered"
block_type_ulist = "unordered"


def textnode_to_htmlnode(textnode: TextNode):
    if not isinstance(textnode, TextNode):
        raise TypeError("Input must be a TextNode type.")
    
    if textnode.text_type == "text":
        return LeafNode(textnode.text)
    elif textnode.text_type == "bold":
        return LeafNode(textnode.text, "b")
    elif textnode.text_type == "italic":
        return LeafNode(textnode.text, "i")
    elif textnode.text_type == "code":
        return LeafNode(textnode.text, "code")
    elif textnode.text_type == "link":
        return LeafNode(textnode.text, "a",{"href": textnode.url})
    elif textnode.text_type == "image":
        return LeafNode("Image", "img",
                        {"src": textnode.url,
                         "alt": textnode.text})
    else:
        raise Exception("Text type not supported.")
    
def split_nodes_delimiter(old_nodes, delimiter):
    new_nodes = []
    new_text_type = ""
    empty_node = TextNode("", "text")

    if delimiter == "`":
        new_text_type = "code"
    elif delimiter == "**":
        new_text_type = "bold"
    elif delimiter == "*":
        new_text_type = "italic"

    for node in old_nodes:
        if node.text_type == "text":
            temp = node.text.split(delimiter)
            i = 0
            for i in range(0, len(temp)):
                if i % 2 == 0:
                    new_nodes.append(TextNode(temp[i], "text"))
                else:
                    new_nodes.append(TextNode(temp[i], new_text_type))
        else:
            new_nodes.append(node)

    temp_nodes = new_nodes.copy()
    new_nodes = []
    
    for node in temp_nodes:
        if node != empty_node:
            new_nodes.append(node)

    return new_nodes 
    
def extract_markdown_images(text):
    pattern = r"!\[(.*?)\]\((.*?)\)"
    images = re.findall(pattern, text)
    return images

def extract_markdown_links(text):
    pattern = r"\[(.*?)\]\((.*?)\)"
    links = re.findall(pattern, text)
    return links

def split_nodes_image(old_nodes):
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type == "text":
            imgs = extract_markdown_images(node.text)
            while imgs != []:
                alt, link = imgs[0][0], imgs[0][1]
                temp = node.text.split(f"![{alt}]({link})", 1)
                if temp[0] != "":
                    new_nodes.append(TextNode(temp[0], "text"))
                new_nodes.append(TextNode(alt, "image", link))
                imgs.remove(imgs[0])
                node.text = temp[1]
            if node.text != "":
                new_nodes.append(node)   
        else:
            new_nodes.append(node)
    
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
        
    for node in old_nodes:
        if node.text_type == "text":
            links = extract_markdown_links(node.text)
            while links != []:
                text, link = links[0][0], links[0][1]
                temp = node.text.split(f"[{text}]({link})", 1)
                if temp[0] != "":
                    new_nodes.append(TextNode(temp[0], "text"))
                new_nodes.append(TextNode(text, "link", link))
                links.remove(links[0])
                node.text = temp[1]
            if node.text != "":
                new_nodes.append(node)
        else:
            new_nodes.append(node)
    
    return new_nodes

def text_to_textnodes(text):
    #Make into TextNode
    new_textnode = TextNode(text, "text")
    
    #Pull out all the links then images
    no_images = split_nodes_image([new_textnode])
    no_links = split_nodes_link(no_images)

    #Filter out Bold > Italic > Code fonts
    no_bold = split_nodes_delimiter(no_links, "**")
    no_italics = split_nodes_delimiter(no_bold, "*")
    final_list = split_nodes_delimiter(no_italics, "`")

    return final_list

def markdown_to_blocks(markdown):
    lines = markdown.split("\n")
    blocks, current_block = [], []
    
    def is_blank(line):
        return not line.strip()
    
    def append_current_block():
        if current_block:
            block_text = '\n'.join(current_block).strip()
            if block_text:
                blocks.append(block_text)
            current_block.clear()

    in_code_block = False

    for line in lines:
        if in_code_block:
            current_block.append(line)
            if line.strip().endswith("```"):
                in_code_block = False
        elif line.strip().startswith("```"):
            append_current_block()
            in_code_block = True
            current_block.append(line)
        elif is_blank(line):
            append_current_block()
        else:
            current_block.append(line)
    
    append_current_block()

    return blocks

def block_to_block_type(block):
    if block == "":
        raise ValueError("Block cannot be empty.")
    
    lines = block.split("\n")

    if (
        block.startswith("# ")
        or block.startswith("## ")
        or block.startswith("### ")
        or block.startswith("#### ")
        or block.startswith("##### ")
        or block.startswith("###### ")
    ):
        return block_type_heading              
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return block_type_code
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return block_type_paragraph
        return block_type_quote
    if block.startswith("* "):
        for line in lines:
            if not line.startswith("* "):
                return block_type_paragraph
        return block_type_ulist
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return block_type_paragraph
        return block_type_ulist
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return block_type_paragraph
            i += 1
        return block_type_olist
    return block_type_paragraph
    
def text_to_children(text):
    children = []

    textnodes = text_to_textnodes(text) 

    for node in textnodes:
        htmlnode = textnode_to_htmlnode(node)
        children.append(htmlnode)
    return children

def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == block_type_paragraph:
        return paragraph_to_html_node(block)
    if block_type == block_type_heading:
        return heading_to_html_node(block)
    if block_type == block_type_code:
        return code_to_html_node(block)
    if block_type == block_type_olist:
        return olist_to_html_node(block)
    if block_type == block_type_ulist:
        return ulist_to_html_node(block)
    if block_type == block_type_quote:
        return quote_to_html_node(block)
    raise ValueError("Invalid block type")

def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode(children, "p")

def heading_to_html_node(block):
    if block.startswith("######"):
        n = 6
    elif block.startswith("#####"):
        n = 5
    elif block.startswith("####"):
        n = 4
    elif block.startswith("###"):
        n = 3
    elif block.startswith("##"):
        n = 2
    elif block.startswith("#"):
        n = 1

    text = block[n+1:]
    children = text_to_children(text)
    return ParentNode(children, f"h{n}")

def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("Invalid code block")
    text = block[4:-3]
    children = text_to_children(text)
    code = ParentNode(children, "code")
    return ParentNode([code], "pre")

def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []

    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode(children, "li"))

    return ParentNode(html_items,"ol")

def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []

    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode(children, "li"))

    return ParentNode(html_items, "ul")

def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []

    for line in lines:
        if not line.startswith(">"):
            raise ValueError("Invalid quote block")
        new_lines.append(line.lstrip(">").strip())

    content = " ".join(new_lines)
    children = text_to_children(content)

    return ParentNode(children, "blockquote")

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode(children, "div")

def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == block_type_paragraph:
        return paragraph_to_html_node(block)
    if block_type == block_type_heading:
        return heading_to_html_node(block)
    if block_type == block_type_code:
        return code_to_html_node(block)
    if block_type == block_type_olist:
        return olist_to_html_node(block)
    if block_type == block_type_ulist:
        return ulist_to_html_node(block)
    if block_type == block_type_quote:
        return quote_to_html_node(block)
    raise ValueError("Invalid block type")