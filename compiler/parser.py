import re
from enum import Enum, auto
from lexer import TokenType, Token, lex
import colorama

class ASTNodeType(Enum):
    PROGRAM = auto()
    FUNCTION_DECLARATION = auto()
    NON_RETURNING_FUNCTION_DECLARATION = auto()
    VARIABLE_DECLARATION = auto()
    CONSTANT_DECLARATION = auto()
    RETURN_STATEMENT = auto()
    EXPRESSION = auto()
    IF_STATEMENT = auto()
    FOR_LOOP = auto()
    PRINT_STATEMENT = auto()
    BLOCK = auto()
    FUNCTION_CALL = auto()

class ASTNode:
    def __init__(self, node_type, value=None):
        self.type = node_type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"ASTNode({self.type}, {self.value}, children={self.children})"

class Parser:
    def __init__(self, tokens, debug=False):
        self.tokens = tokens
        self.position = 0
        self.debug = debug
        self.indent_level = 0

    def debug_log(self, message, color=colorama.Fore.CYAN):
        if self.debug:
            indent = "  " * self.indent_level
            print(f"{color}Parser - DEBUG: {indent}{message}{colorama.Fore.RESET}")

    def current_token(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def next_token(self):
        self.position += 1
        return self.current_token()

    def match(self, token_type):
        if self.current_token() and self.current_token().type == token_type:
            token = self.current_token()
            self.next_token()
            self.debug_log(f"Matched {token_type}: '{token.value}'")
            return token
        self.debug_log(f"Failed to match {token_type}")
        return None

    def parse(self):
        self.debug_log("Starting parse")
        self.indent_level += 1
        result = self.parse_program()
        self.indent_level -= 1
        self.debug_log("Parsing complete")
        return result

    def parse_program(self):
        self.debug_log("Parsing program")
        self.indent_level += 1
        program_node = ASTNode(ASTNodeType.PROGRAM)
        while self.current_token():
            if self.current_token().type == TokenType.COMMENT:
                self.next_token()  # Skip comments
            elif self.current_token().type == TokenType.KEYWORD:
                if self.current_token().value == "@ink":
                    program_node.add_child(self.parse_function_declaration())
                elif self.current_token().value in ["let", "const"]:
                    program_node.add_child(self.parse_variable_declaration())
                elif self.current_token().value == "return":
                    program_node.add_child(self.parse_return_statement())
                elif self.current_token().value == "if":
                    program_node.add_child(self.parse_if_statement())
                elif self.current_token().value == "for":
                    program_node.add_child(self.parse_for_loop())
                elif self.current_token().value == "print":
                    program_node.add_child(self.parse_print_statement())
            else:
                self.next_token()
        self.indent_level -= 1
        return program_node

    def parse_function_declaration(self):
        self.debug_log("Parsing function declaration")
        self.indent_level += 1
        self.match(TokenType.KEYWORD)  # @ink
        name = self.match(TokenType.IDENTIFIER)
        if not name:
            raise SyntaxError("Expected function name after @ink")
        name = name.value
        self.match(TokenType.DELIMITER)  # (
        params = self.parse_parameters()
        self.match(TokenType.DELIMITER)  # )
        
        return_type = None
        if self.current_token() and self.current_token().type == TokenType.OPERATOR and self.current_token().value == '-':
            self.match(TokenType.OPERATOR)  # -
            self.match(TokenType.OPERATOR)  # >
            return_type = self.match(TokenType.IDENTIFIER)
            if not return_type:
                raise SyntaxError("Expected return type after '->'")
            return_type = return_type.value

        self.match(TokenType.BLOCK_DELIMITER)  # ~
        body = self.parse_block()
        self.match(TokenType.BLOCK_DELIMITER)  # ~
        
        node = ASTNode(ASTNodeType.FUNCTION_DECLARATION if return_type else ASTNodeType.NON_RETURNING_FUNCTION_DECLARATION, name)
        node.add_child(params)
        if return_type:
            node.add_child(ASTNode(ASTNodeType.EXPRESSION, return_type))
        node.add_child(body)

        param_str = ", ".join([f"{p.value}: {p.children[0].value}{' = ' + str(p.children[1].value) if len(p.children) > 1 else ''}" for p in params.children])
        self.debug_log(f"Parsed function: {name}({param_str}) -> {return_type or 'None'}")
        self.indent_level -= 1
        return node

    def parse_parameters(self):
        self.debug_log("Parsing parameters")
        self.indent_level += 1
        params = ASTNode(ASTNodeType.EXPRESSION)
        while self.current_token() and (self.current_token().type != TokenType.DELIMITER or self.current_token().value != ")"):
            param_name = self.match(TokenType.IDENTIFIER)
            if not param_name:
                break
            self.match(TokenType.DELIMITER)  # :
            param_type = self.match(TokenType.IDENTIFIER)
            if not param_type:
                raise SyntaxError(f"Expected type for parameter {param_name.value}")
            default_value = None
            if self.current_token() and self.current_token().type == TokenType.OPERATOR and self.current_token().value == "=":
                self.match(TokenType.OPERATOR)  # =
                default_value = self.parse_expression()
            param_node = ASTNode(ASTNodeType.EXPRESSION, param_name.value)
            param_node.add_child(ASTNode(ASTNodeType.EXPRESSION, param_type.value))
            if default_value:
                param_node.add_child(default_value)
            params.add_child(param_node)
            self.debug_log(f"Parsed parameter: {param_name.value}: {param_type.value}{' = ' + str(default_value.value) if default_value else ''}")
            if self.current_token() and self.current_token().type == TokenType.DELIMITER and self.current_token().value == ",":
                self.match(TokenType.DELIMITER)  # ,
        self.indent_level -= 1
        return params

    def parse_block(self):
        self.debug_log("Parsing block")
        self.indent_level += 1
        block_node = ASTNode(ASTNodeType.BLOCK)
        while self.current_token() and self.current_token().type != TokenType.BLOCK_DELIMITER:
            if self.current_token().type == TokenType.COMMENT:
                self.next_token()  # Skip comments
            elif self.current_token().type == TokenType.KEYWORD:
                if self.current_token().value == "return":
                    block_node.add_child(self.parse_return_statement())
                elif self.current_token().value == "if":
                    block_node.add_child(self.parse_if_statement())
                elif self.current_token().value == "for":
                    block_node.add_child(self.parse_for_loop())
                elif self.current_token().value == "print":
                    block_node.add_child(self.parse_print_statement())
                elif self.current_token().value in ["let", "const"]:
                    block_node.add_child(self.parse_variable_declaration())
            else:
                self.next_token()
        self.indent_level -= 1
        return block_node

    def parse_variable_declaration(self):
        self.debug_log("Parsing variable declaration")
        self.indent_level += 1
        keyword = self.match(TokenType.KEYWORD).value
        name = self.match(TokenType.IDENTIFIER).value
        self.match(TokenType.OPERATOR)  # =
        value = self.parse_expression()
        node_type = ASTNodeType.VARIABLE_DECLARATION if keyword == "let" else ASTNodeType.CONSTANT_DECLARATION
        node = ASTNode(node_type, name)
        node.add_child(value)
        self.debug_log(f"Parsed variable declaration: {name} = {value.value}")
        self.indent_level -= 1
        return node

    def parse_return_statement(self):
        self.debug_log("Parsing return statement")
        self.indent_level += 1
        self.match(TokenType.KEYWORD)  # return
        value = self.parse_expression()
        self.debug_log(f"Parsed return statement: return {value.value}")
        self.indent_level -= 1
        return ASTNode(ASTNodeType.RETURN_STATEMENT, value)

    def parse_if_statement(self):
        self.debug_log("Parsing if statement")
        self.indent_level += 1
        self.match(TokenType.KEYWORD)  # if
        condition = self.parse_expression()
        self.match(TokenType.BLOCK_DELIMITER)  # ~
        body = self.parse_block()
        self.match(TokenType.BLOCK_DELIMITER)  # ~
        self.debug_log(f"Parsed if statement: if {condition.value} {{ ... }}")
        self.indent_level -= 1
        node = ASTNode(ASTNodeType.IF_STATEMENT)
        node.add_child(condition)
        node.add_child(body)
        return node

    def parse_for_loop(self):
        self.debug_log("Parsing for loop")
        self.indent_level += 1
        self.match(TokenType.KEYWORD)  # for
        variable = self.match(TokenType.IDENTIFIER).value
        self.match(TokenType.KEYWORD)  # in
        collection = self.parse_expression()
        self.match(TokenType.BLOCK_DELIMITER)  # ~
        body = self.parse_block()
        self.match(TokenType.BLOCK_DELIMITER)  # ~
        self.debug_log(f"Parsed for loop: for {variable} in {collection.value} {{ ... }}")
        self.indent_level -= 1
        node = ASTNode(ASTNodeType.FOR_LOOP)
        node.add_child(variable)
        node.add_child(collection)
        node.add_child(body)
        return node

    def parse_print_statement(self):
        self.debug_log("Parsing print statement")
        self.indent_level += 1
        self.match(TokenType.KEYWORD)  # print
        self.match(TokenType.DELIMITER)  # (
        value = self.parse_expression()
        self.match(TokenType.DELIMITER)  # )
        self.debug_log(f"Parsed print statement: print({value.value})")
        self.indent_level -= 1
        node = ASTNode(ASTNodeType.PRINT_STATEMENT)
        node.add_child(value)
        return node

    def parse_expression(self):
        self.debug_log("Parsing expression")
        self.indent_level += 1
        token = self.current_token()
        if token.type == TokenType.IDENTIFIER:
            self.next_token()
            if self.current_token() and self.current_token().type == TokenType.DELIMITER and self.current_token().value == "(":
                result = self.parse_function_call(token.value)
            else:
                result = ASTNode(ASTNodeType.EXPRESSION, token.value)
        elif token.type in [TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING, TokenType.BOOLEAN]:
            self.next_token()
            result = ASTNode(ASTNodeType.EXPRESSION, token.value)
        elif token.type == TokenType.DELIMITER and token.value == "(":
            self.next_token()
            result = self.parse_expression()
            if not self.match(TokenType.DELIMITER) or self.current_token().value != ")":
                raise SyntaxError("Expected closing parenthesis")
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")
        self.debug_log(f"Parsed expression: {result.value}")
        self.indent_level -= 1
        return result

    def parse_function_call(self, function_name):
        self.debug_log(f"Parsing function call to {function_name}")
        self.indent_level += 1
        node = ASTNode(ASTNodeType.FUNCTION_CALL, function_name)
        self.match(TokenType.DELIMITER)  # (
        args = []
        while self.current_token() and (self.current_token().type != TokenType.DELIMITER or self.current_token().value != ")"):
            arg = self.parse_expression()
            node.add_child(arg)
            args.append(str(arg.value))
            if self.current_token() and self.current_token().type == TokenType.DELIMITER and self.current_token().value == ",":
                self.match(TokenType.DELIMITER)  # ,
        self.match(TokenType.DELIMITER)  # )
        self.debug_log(f"Parsed function call: {function_name}({', '.join(args)})")
        self.indent_level -= 1
        return node

def pretty_print_ast(node, indent=0):
    indent_str = "  " * indent
    if node.type == ASTNodeType.RETURN_STATEMENT:
        print(f"{indent_str}{node.type}:")
        if node.children:
            pretty_print_ast(node.children[0], indent + 1)
        else:
            print(f"{indent_str}  {node.value}")
    else:
        print(f"{indent_str}{node.type}: {node.value}")
        for child in node.children:
            pretty_print_ast(child, indent + 1)

def parse(source_code, debug=False):
    tokens = lex(source_code, debug)
    parser = Parser(tokens, debug)
    return parser.parse()

# Example usage
if __name__ == "__main__":
    sample_code = """
    // This is a comment
    @ink calculate_pressure(depth: Float, gravity: Float = 9.8) -> Float ~
        (* Calculate pressure at given depth *)
        return depth * gravity * 1000;
    ~

    @ink test1() ~
    ~

    @ink test2(test: Float) -> Float ~
        return test;
    ~

    let depth = 5000.0;
    let pressure = calculate_pressure(depth);
    print("Pressure at {{depth}}m: {{pressure}} Pa");
    """

    print("Parsing with debug output:")
    ast = parse(sample_code, debug=True)
    print("\nParsing complete. AST:")
    pretty_print_ast(ast)