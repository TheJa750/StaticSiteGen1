class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        prop_dict = self.props
        html_str = ""

        if self.props != None:
            for key in prop_dict:
                html_str += f" {key}='{prop_dict[key]}'"
        
        return html_str

    
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    
class LeafNode(HTMLNode):
    def __init__(self, value, tag=None, props=None):
        super().__init__(tag, value, None, props)
        if self.value == None or self.value == "":
            raise ValueError("LeafNode must have value")

    def to_html(self):
        if self.tag == None or self.tag == "":
            return self.value
        html_str = ""

        html_str += f"<{self.tag}"

        if self.props != None and self.props != {}:
            html_str += f"{self.props_to_html()}"
        
        html_str += f">{self.value}</{self.tag}>"
        return html_str
    
    # def __repr__(self):
    #     return f"LeafNode({self.tag}, {self.value}, {self.props})"
    
class ParentNode(HTMLNode):
    def __init__(self,children, tag, props=None):
        super().__init__(tag, None, children, props)
        if self.children == None:
            raise ValueError("ParentNode must have children")
        if self.tag == None or self.tag == "":
            raise ValueError("ParentNode must have tag")
        
    def to_html(self):
        if self.tag is None:
            raise ValueError("Invalid HTML: no tag")
        if self.children is None:
            raise ValueError("Invalid HTML: no children")
        children_html = ""
        for child in self.children:
            children_html += child.to_html()
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>" 
    
    def add_child(self, node):
        self.children.append(node)

    # def __repr__(self):
    #     return f"ParentNode({self.tag}, children: {self.children}, {self.props})"