from enum import Enum, auto
from lexer import TokenType, Token
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax

console = Console()

class ASTNodeType(Enum):
    PROGRAM = auto()
    FUNCTION_DECLARATION = auto()
    VARIABLE_DECLARATION = auto()
    CONSTANT_DECLARATION = auto()
    IF_STATEMENT = auto()
    ELIF_STATEMENT = auto()
    ELSE_STATEMENT = auto()
    RETURN_STATEMENT = auto()
    EXPRESSION_STATEMENT = auto()
    BINARY_EXPRESSION = auto()
    UNARY_EXPRESSION = auto()
    FUNCTION_CALL = auto()
    PARAMETERS = auto()
    PARAMETER = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    BLOCK = auto()

class ASTNode:
    def __init__(self, node_type: ASTNodeType, children=None, value=None):
        self.type = node_type
        self.children = children or []
        self.value = value

    def add_child(self, child):
        self.children.append(child)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.debug_mode = False
        self.function_names = set()

    def parse(self):
        self.log_info("Starting parsing process")
        program = ASTNode(ASTNodeType.PROGRAM)
        
        while not self.is_at_end():
            statement = self.parse_statement()
            if statement:
                program.add_child(statement)
        
        self.log_info("Parsing complete")
        return program

    def parse_statement(self):
        while self.match(TokenType.NEWLINE):
            pass  # Skip empty lines

        if self.match(TokenType.COMMENT):
            return None  # Ignore comments

        if self.is_at_end():
            return None
        elif self.check(TokenType.IDENTIFIER) and self.peek().value == 'fun':
            return self.parse_function_declaration()
        elif self.match(TokenType.VAR):
            return self.parse_variable_declaration()
        elif self.match(TokenType.CONST):
            return self.parse_constant_declaration()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.RETURN):
            return self.parse_return_statement()
        elif self.check(TokenType.IDENTIFIER):
            expr = self.parse_expression()
            self.consume(TokenType.NEWLINE, "Expected newline after expression statement")
            return expr
        else:
            self.error(f"Unexpected token: {self.peek()}")
            
    def parse_expression_statement(self):
        expr = self.parse_expression()
        self.consume(TokenType.NEWLINE, "Expected newline after expression")
        return expr

    def parse_function_declaration(self):
        self.log_debug("Parsing function declaration")
        node = ASTNode(ASTNodeType.FUNCTION_DECLARATION)
        
        self.consume(TokenType.IDENTIFIER, "Expected 'fun' keyword")
        name = self.consume(TokenType.IDENTIFIER, "Expected function name")
        
        # Check if the function name already exists
        if name.value in self.function_names:
            self.error(f"Function '{name.value}' is already defined. Function overloading is not allowed.")
        else:
            self.function_names.add(name.value)
        
        node.add_child(ASTNode(ASTNodeType.IDENTIFIER, value=name.value))
        
        self.consume(TokenType.LPAREN, "Expected '(' after function name")
        parameters = self.parse_parameters()
        node.add_child(parameters)
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        if self.match(TokenType.ARROW):
            return_type = self.consume(TokenType.IDENTIFIER, "Expected return type after '->'")
            node.add_child(ASTNode(ASTNodeType.IDENTIFIER, value=return_type.value))
        
        body = self.parse_block()
        node.add_child(body)
        
        return node

    def parse_parameters(self):
        parameters = ASTNode(ASTNodeType.PARAMETERS)
        if not self.check(TokenType.RPAREN):
            while True:
                param = self.consume(TokenType.IDENTIFIER, "Expected parameter name")
                param_node = ASTNode(ASTNodeType.PARAMETER, value=param.value)
                if self.match(TokenType.COLON):
                    type_name = self.consume(TokenType.IDENTIFIER, "Expected parameter type")
                    param_node.add_child(ASTNode(ASTNodeType.IDENTIFIER, value=type_name.value))
                parameters.add_child(param_node)
                if not self.match(TokenType.COMMA):
                    break
        return parameters

    def parse_variable_declaration(self):
        self.log_debug("Parsing variable declaration")
        node = ASTNode(ASTNodeType.VARIABLE_DECLARATION)
        
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        node.add_child(ASTNode(ASTNodeType.IDENTIFIER, value=name.value))
        
        self.consume(TokenType.EQUALS, "Expected '=' after variable name")
        value = self.parse_expression()
        node.add_child(value)
        
        self.consume(TokenType.NEWLINE, "Expected newline after variable declaration")
        return node

    def parse_constant_declaration(self):
        self.log_debug("Parsing constant declaration")
        node = ASTNode(ASTNodeType.CONSTANT_DECLARATION)
        
        name = self.consume(TokenType.IDENTIFIER, "Expected constant name")
        node.add_child(ASTNode(ASTNodeType.IDENTIFIER, value=name.value))
        
        self.consume(TokenType.EQUALS, "Expected '=' after constant name")
        value = self.parse_expression()
        node.add_child(value)
        
        self.consume(TokenType.NEWLINE, "Expected newline after constant declaration")
        return node

    def parse_if_statement(self):
        self.log_debug("Parsing if statement")
        node = ASTNode(ASTNodeType.IF_STATEMENT)
        
        condition = self.parse_expression()
        node.add_child(condition)
        
        self.consume(TokenType.NEWLINE, "Expected newline after if condition")
        body = self.parse_block()
        node.add_child(body)
        
        while self.check(TokenType.ELIF):
            self.advance()  # Consume the ELIF token
            self.log_debug("Parsing elif statement")
            elif_node = ASTNode(ASTNodeType.ELIF_STATEMENT)
            elif_condition = self.parse_expression()
            elif_node.add_child(elif_condition)
            
            self.consume(TokenType.NEWLINE, "Expected newline after elif condition")
            elif_body = self.parse_block()
            elif_node.add_child(elif_body)
            node.add_child(elif_node)
        
        if self.check(TokenType.ELSE):
            self.advance()  # Consume the ELSE token
            self.log_debug("Parsing else statement")
            else_node = ASTNode(ASTNodeType.ELSE_STATEMENT)
            self.consume(TokenType.NEWLINE, "Expected newline after else")
            else_body = self.parse_block()
            else_node.add_child(else_body)
            node.add_child(else_node)
        
        return node

    def parse_return_statement(self):
        self.log_debug("Parsing return statement")
        node = ASTNode(ASTNodeType.RETURN_STATEMENT)
        
        value = self.parse_expression()
        node.add_child(value)
        
        self.consume(TokenType.NEWLINE, "Expected newline after return statement")
        return node
    
    def comment(self):
        while self.current_char != '\n' and self.current_char is not None:
            self.advance()
        return Token(TokenType.COMMENT, '', self.line, self.column)
    
    def consume_token(self, expected_type, error_message):
        if self.check(expected_type):
            return self.advance()
        self.error(error_message)

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        expr = self.parse_comparison()
        
        while self.match(TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous()
            right = self.parse_comparison()
            expr = ASTNode(ASTNodeType.BINARY_EXPRESSION, [expr, right], operator.type)
        
        return expr

    def parse_comparison(self):
        expr = self.parse_term()
        
        while self.match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL, TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.parse_term()
            expr = ASTNode(ASTNodeType.BINARY_EXPRESSION, [expr, right], operator.type)
        
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.parse_factor()
            expr = ASTNode(ASTNodeType.BINARY_EXPRESSION, [expr, right], operator.type)
        
        return expr

    def parse_factor(self):
        expr = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self.previous()
            right = self.parse_unary()
            expr = ASTNode(ASTNodeType.BINARY_EXPRESSION, [expr, right], operator.type)
        
        return expr

    def parse_unary(self):
        if self.match(TokenType.MINUS):
            operator = self.previous()
            right = self.parse_unary()
            return ASTNode(ASTNodeType.UNARY_EXPRESSION, [right], operator.type)
        
        return self.parse_primary()

    def parse_primary(self):
        if self.match(TokenType.NUM):
            return ASTNode(ASTNodeType.NUMBER, value=self.previous().value)
        elif self.match(TokenType.TEXT):
            return ASTNode(ASTNodeType.STRING, value=self.previous().value)
        elif self.match(TokenType.BOOL):
            return ASTNode(ASTNodeType.BOOLEAN, value=self.previous().value)
        elif self.match(TokenType.IDENTIFIER):
            if self.match(TokenType.LPAREN):
                return self.finish_function_call(self.previous())
            return ASTNode(ASTNodeType.IDENTIFIER, value=self.previous().value)
        elif self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        self.error(f"Unexpected token: {self.peek()}")
        
    def finish_function_call(self, callee):
        arguments = []
        if not self.check(TokenType.RPAREN):
            while True:
                arguments.append(self.parse_expression())
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RPAREN, "Expected ')' after function arguments")
        return ASTNode(ASTNodeType.FUNCTION_CALL, [callee] + arguments)
    
    def parse_block(self):
        self.log_debug("Parsing block")
        block = ASTNode(ASTNodeType.BLOCK)
        
        if not self.check(TokenType.NEWLINE):
            statement = self.parse_statement()
            if statement:
                block.add_child(statement)
            return block
        
        self.consume(TokenType.NEWLINE, "Expected newline after block start")
        while not self.is_at_end() and not self.check(TokenType.DEDENT):
            while self.match(TokenType.NEWLINE):
                pass  # Skip empty lines
            if self.is_at_end() or self.check(TokenType.DEDENT):
                break
            statement = self.parse_statement()
            if statement:
                block.add_child(statement)
        
        return block

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        self.error(message)

    def peek_next(self):
        if self.is_at_end():
            return self.tokens[-1]
        return self.tokens[self.current + 1]
    
    def error(self, expected, actual):
        token = self.peek()
        raise Exception(f"Parser error at line {token.line}, column {token.column}: "
                        f"Expected {expected}, but got {actual.type} '{actual.value}'")
    def error(self, message):
        raise Exception(f"Parser error: {message}")

    def log_info(self, message):
        if self.debug_mode:
            console.print(f"[bold blue]INFO:[/bold blue] {message}")

    def log_debug(self, message):
        if self.debug_mode:
            current_token = self.peek()
            console.print(f"[bold green]DEBUG:[/bold green] {message} - Current token: {current_token.type} '{current_token.value}'")

def parse_and_debug(tokens):
    console.print(Panel.fit("[bold cyan]Starting Parsing Process[/bold cyan]", border_style="cyan"))
    
    parser = Parser(tokens)
    parser.debug_mode = True
    ast = parser.parse()
    
    console.print(Panel.fit("[bold green]Parsing Complete[/bold green]", border_style="green"))
    print_ast(ast)
    
    return ast

def print_ast(node, indent=""):
    from rich.console import Console
    from rich.text import Text

    console = Console()

    def print_node(node, indent=""):
        if isinstance(node, ASTNode):
            text = Text()
            text.append(indent, style="dim")
            text.append(str(node.type), style="bold magenta")
            console.print(text)
            if node.value is not None:
                value_text = Text()
                value_text.append(indent + "  ", style="dim")
                value_text.append("Value: ", style="bold cyan")
                value_text.append(str(node.value), style="yellow")
                console.print(value_text)
            for child in node.children:
                print_node(child, indent + "  ")
        elif isinstance(node, Token):
            text = Text()
            text.append(indent, style="dim")
            text.append("Token: ", style="bold green")
            text.append(f"{node.type}", style="blue")
            text.append(" - ", style="dim")
            text.append(str(node.value), style="yellow")
            console.print(text)

    print_node(node)

if __name__ == "__main__":
    from lexer import lex_and_debug
    
    source_code = """
fun factorial(n: num) -> num
    if n <= 1
        return 1
    return n * factorial(n - 1)

fun fibonacci(n: num) -> num
    if n <= 0
        return 0
    elif n == 1
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)

var x = 10
var y = factorial(x)
print("Factorial of", x, "is", y)

const PI = 3.14159
var radius = 5
var area = PI * radius * radius
print("Area of the circle with radius", radius, "is", area)

if radius > 0
    print("Radius is positive")
elif radius == 0
    print("Radius is zero")
else
    print("Radius is negative")

fun greet(name: text) -> text
    return "Hello, " + name + "!"

var greeting = greet("World")
print(greeting)

fun add(a: num, b: num) -> num
    return a + b

var sum = add(5, 7)
print("Sum of 5 and 7 is", sum)

fun test()
    var a = 1
    var b = 2
    var result = add(a, b)
    print("Result of adding", a, "and", b, "is", result)
    
# This is a comment
test()
"""
    
    tokens = lex_and_debug(source_code)
    ast = parse_and_debug(tokens)
    tokens = lex_and_debug(source_code)
    ast = parse_and_debug(tokens)