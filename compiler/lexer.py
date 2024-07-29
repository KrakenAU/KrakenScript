from enum import Enum, auto
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

class TokenType(Enum):
    # Keywords
    VAR = auto()
    CONST = auto()
    FUNC = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    RETURN = auto()
    DEDENT = auto()
    COMMENT = auto()

    
    # Data types
    NUM = auto()
    TEXT = auto()
    BOOL = auto()
    
    # Operators
    EQUALS = auto()
    ARROW = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    GREATER_THAN = auto()
    LESS_THAN = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    EQUAL_EQUAL = auto()
    NOT_EQUAL = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    COLON = auto()
    
    # Other
    IDENTIFIER = auto()
    NEWLINE = auto()
    EOF = auto()

class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[self.position] if self.position < len(self.source) else None
        self.debug_mode = False

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        self.position += 1
        self.current_char = self.source[self.position] if self.position < len(self.source) else None

    def peek(self):
        peek_pos = self.position + 1
        return self.source[peek_pos] if peek_pos < len(self.source) else None

    def tokenize(self):
        tokens = []
        if self.debug_mode:
            console.print(Panel.fit("🔍 [bold cyan]Starting Lexical Analysis[/bold cyan]", border_style="cyan"))
        
        while self.current_char is not None:
            if self.current_char.isspace():
                if self.current_char == '\n':
                    tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                    if self.debug_mode:
                        console.print(f"[dim]Line {self.line}: Newline detected[/dim]")
                self.advance()
            elif self.current_char == '#':
                token = self.comment()
                tokens.append(token)
                if self.debug_mode:
                    console.print(f"[dim]Line {self.line}: Comment detected[/dim]")
            elif self.current_char.isalpha() or self.current_char == '_':
                token = self.identifier()
                tokens.append(token)
                if self.debug_mode:
                    console.print(f"[green]Identified: {token}[/green]")
            elif self.current_char.isdigit():
                token = self.number()
                tokens.append(token)
                if self.debug_mode:
                    console.print(f"[yellow]Number: {token}[/yellow]")
            elif self.current_char == '"':
                token = self.string()
                tokens.append(token)
                if self.debug_mode:
                    console.print(f"[blue]String: {token}[/blue]")
            elif self.current_char in '+-*/=(),:<>!?:':
                token = self.operator_or_delimiter()
                tokens.append(token)
                if self.debug_mode:
                    console.print(f"[magenta]Operator or Delimiter: {token}[/magenta]")
            else:
                self.error(f"Unexpected character: {self.current_char}")
        
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        
        if self.debug_mode:
            self.print_token_table(tokens)
            console.print(Panel.fit("✅ [bold green]Lexical Analysis Complete[/bold green]", border_style="green"))
        
        return tokens

    def identifier(self):
        start_column = self.column
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            self.advance()
        
        value = self.source[self.position - (self.column - start_column):self.position]
        
        token_type = {
            "var": TokenType.VAR,
            "const": TokenType.CONST,
            "func": TokenType.FUNC,
            "if": TokenType.IF,
            "elif": TokenType.ELIF,
            "else": TokenType.ELSE,
            "return": TokenType.RETURN,
            "true": TokenType.BOOL,
            "false": TokenType.BOOL
        }.get(value, TokenType.IDENTIFIER)
        
        return Token(token_type, value, self.line, start_column)

    def number(self):
        start_column = self.column
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return Token(TokenType.NUM, result, self.line, start_column)

    def string(self):
        start_column = self.column
        self.advance()  # Skip the opening quote
        result = ""
        while self.current_char is not None:
            if self.current_char == '"':
                self.advance()  # Skip the closing quote
                return Token(TokenType.TEXT, result, self.line, start_column)
            elif self.current_char == '\n':
                self.line += 1
                self.column = 1
            result += self.current_char
            self.advance()
        self.error("Unterminated string literal")

    def operator_or_delimiter(self):
        start_column = self.column
        char = self.current_char
        self.advance()
        
        if char == '-' and self.current_char == '>':
            self.advance()
            return Token(TokenType.ARROW, '->', self.line, start_column)
        elif char == '>' and self.current_char == '=':
            self.advance()
            return Token(TokenType.GREATER_EQUAL, '>=', self.line, start_column)
        elif char == '<' and self.current_char == '=':
            self.advance()
            return Token(TokenType.LESS_EQUAL, '<=', self.line, start_column)
        elif char == '=' and self.current_char == '=':
            self.advance()
            return Token(TokenType.EQUAL_EQUAL, '==', self.line, start_column)
        elif char == '!' and self.current_char == '=':
            self.advance()
            return Token(TokenType.NOT_EQUAL, '!=', self.line, start_column)
        
        token_type = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '=': TokenType.EQUALS,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            '>': TokenType.GREATER_THAN,
            '<': TokenType.LESS_THAN
        }.get(char)
        
        return Token(token_type, char, self.line, start_column)
    
    def comment(self):
        start_column = self.column
        self.advance()  # Skip the opening quote
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        self.advance()  # Skip the closing quote
        return Token(TokenType.COMMENT, '', self.line, start_column)

    def error(self, message):
        raise Exception(f"Lexer error on line {self.line}, column {self.column}: {message}")

    def print_token_table(self, tokens):
        table = Table(title="Token Stream")
        table.add_column("Type", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Line", style="green")
        table.add_column("Column", style="yellow")

        for token in tokens:
            table.add_row(str(token.type), token.value, str(token.line), str(token.column))

        console.print(table)

def lex_and_debug(source_code):
    console.print(Panel(Syntax(source_code, "python", theme="monokai", line_numbers=True), 
                        title="[bold]Source Code[/bold]", border_style="red"))
    
    lexer = Lexer(source_code)
    lexer.debug_mode = True
    tokens = lexer.tokenize()
    
    return tokens

if __name__ == "__main__":
    source_code = """
fun main()
    greet("Coder")
    
    if is_coffee_needed()
        print("Alert: Low energy detected! Brew coffee!")
    else
        print("All systems go. Keep coding!")

fun hello() 
    print("Hello, world!")
    let multiline = "
        This is a multiline string
        with multiple lines
    "

fun add(a, b) -> num
    return a + b

fun subtract(a: Float, b: Float) -> Float
    return a - b
    
    # This is a comment
    
#* testttting 

fun comment_test()
    # This is a comment
    print("Hello, world!")
"""
    lex_and_debug(source_code)
    