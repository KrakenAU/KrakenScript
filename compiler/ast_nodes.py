from enum import Enum, auto

class ASTNodeType(Enum):
    PROGRAM = auto()
    FUNCTION_DECLARATION = auto()
    PARAMETERS = auto()
    PARAMETER = auto()
    TYPE = auto()
    RETURN_TYPE = auto()
    VARIABLE_DECLARATION = auto()
    CONSTANT_DECLARATION = auto()
    RETURN_STATEMENT = auto()
    EXPRESSION = auto()
    IF_STATEMENT = auto()
    FOR_LOOP = auto()
    PRINT_STATEMENT = auto()
    BLOCK = auto()
    FUNCTION_CALL = auto()
    BINARY_OPERATION = auto()

class ASTNode:
    def __init__(self, node_type, value=None):
        self.type = node_type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"ASTNode({self.type}, {self.value}, children={self.children})"

def pretty_print_ast(node, indent=0):
    indent_str = "  " * indent
    if node.type == ASTNodeType.FUNCTION_DECLARATION:
        print(f"{indent_str}{node.type}: {node.value}")
        for child in node.children:
            pretty_print_ast(child, indent + 1)
    elif node.type == ASTNodeType.PARAMETERS:
        print(f"{indent_str}{node.type}")
        for child in node.children:
            pretty_print_ast(child, indent + 1)
    elif node.type == ASTNodeType.PARAMETER:
        param_type = node.children[0].value
        default_value = f" = {node.children[1].value}" if len(node.children) > 1 else ""
        print(f"{indent_str}{node.type}: {node.value}: {param_type}{default_value}")
    elif node.type == ASTNodeType.RETURN_TYPE:
        print(f"{indent_str}{node.type}: {node.value}")
    elif node.type == ASTNodeType.BLOCK:
        print(f"{indent_str}{node.type}")
        if node.children:
            for child in node.children:
                pretty_print_ast(child, indent + 1)
        else:
            print(f"{indent_str}  Empty")
    elif node.type == ASTNodeType.RETURN_STATEMENT:
        print(f"{indent_str}{node.type}")
        for child in node.children:
            pretty_print_ast(child, indent + 1)
    elif node.type == ASTNodeType.BINARY_OPERATION:
        print(f"{indent_str}{node.type}: {node.value}")
        for child in node.children:
            pretty_print_ast(child, indent + 1)
    elif node.type == ASTNodeType.EXPRESSION:
        print(f"{indent_str}{node.type}: {node.value}")
    elif node.type in [ASTNodeType.VARIABLE_DECLARATION, ASTNodeType.CONSTANT_DECLARATION]:
        print(f"{indent_str}{node.type}: {node.value}")
        for child in node.children:
            pretty_print_ast(child, indent + 1)
    elif node.type == ASTNodeType.PRINT_STATEMENT:
        print(f"{indent_str}{node.type}")
        for child in node.children:
            pretty_print_ast(child, indent + 1)
    else:
        print(f"{indent_str}{node.type}: {node.value}")
        for child in node.children:
            pretty_print_ast(child, indent + 1)