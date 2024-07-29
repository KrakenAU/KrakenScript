import re
from enum import Enum, auto
import colorama

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    OPERATOR = auto()
    DELIMITER = auto()
    COMMENT = auto()
    EOF = auto()
    BLOCK_DELIMITER = auto()

class Token:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class Lexer:
    def __init__(self, source_code, debug=False):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source_code[0] if self.source_code else None
        self.debug = debug

    def debug_log(self, message, color=colorama.Fore.CYAN, token_type=None):
        if self.debug:
            token_color = colorama.Fore.WHITE
            if token_type:
                if token_type in [TokenType.KEYWORD, TokenType.BOOLEAN]:
                    token_color = colorama.Fore.GREEN
                elif token_type in [TokenType.STRING, TokenType.INTEGER, TokenType.FLOAT]:
                    token_color = colorama.Fore.YELLOW
                elif token_type in [TokenType.IDENTIFIER, TokenType.BLOCK_DELIMITER]:
                    token_color = colorama.Fore.MAGENTA
                elif token_type in [TokenType.OPERATOR, TokenType.DELIMITER]:
                    token_color = colorama.Fore.BLUE
                elif token_type == TokenType.COMMENT:
                    token_color = colorama.Fore.CYAN

            print(f"{color}Lexer - DEBUG: [{self.line}:{self.column}] {token_color}{message}{colorama.Fore.RESET}")
              
    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
            elif self.source_code[self.position:self.position+2] == '(*':
                self.tokenize_multi_line_comment(tokens)
            elif self.match(r'@ink'):
                self.debug_log(f"Found @ink keyword", token_type=TokenType.KEYWORD)
                tokens.append(self.create_token(TokenType.KEYWORD, self.current_match))
            elif self.match(r'let|const|if|else|for|return|print'):
                self.debug_log(f"Found keyword '{self.current_match}'", token_type=TokenType.KEYWORD)
                tokens.append(self.create_token(TokenType.KEYWORD, self.current_match))
            elif self.match(r'true|false'):
                self.debug_log(f"Found boolean '{self.current_match}'", token_type=TokenType.BOOLEAN)
                tokens.append(self.create_token(TokenType.BOOLEAN, self.current_match))
            elif self.match(r'"'):
                self.debug_log("Found string", token_type=TokenType.STRING)
                self.tokenize_string(tokens)
            elif self.match(r'\d+\.\d+'):
                self.debug_log(f"Found float '{self.current_match}'", token_type=TokenType.FLOAT)
                tokens.append(self.create_token(TokenType.FLOAT, float(self.current_match)))
            elif self.match(r'\d+'):
                self.debug_log(f"Found integer '{self.current_match}'", token_type=TokenType.INTEGER)
                tokens.append(self.create_token(TokenType.INTEGER, int(self.current_match)))
            elif self.match(r'[a-zA-Z_]\w*'):
                self.debug_log(f"Found identifier '{self.current_match}'", token_type=TokenType.IDENTIFIER)
                tokens.append(self.create_token(TokenType.IDENTIFIER, self.current_match))
            elif self.match(r'[+\-*/=<>!]=?'):
                self.debug_log(f"Found operator '{self.current_match}'", token_type=TokenType.OPERATOR)
                tokens.append(self.create_token(TokenType.OPERATOR, self.current_match))
            elif self.match(r'~'):
                self.debug_log(f"Found block delimiter '{self.current_match}'", token_type=TokenType.BLOCK_DELIMITER)
                tokens.append(self.create_token(TokenType.BLOCK_DELIMITER, self.current_match))
            elif self.match(r'[(),.:;{}]'):
                self.debug_log(f"Found delimiter '{self.current_match}'", token_type=TokenType.DELIMITER)
                tokens.append(self.create_token(TokenType.DELIMITER, self.current_match))
            else:
                self.debug_log(f"Unexpected character: {self.current_char}", color=colorama.Fore.RED)
                raise SyntaxError(f"Unexpected character: {self.current_char} at line {self.line}, column {self.column}")

        self.debug_log("Tokenization complete", color=colorama.Fore.GREEN)
        tokens.append(self.create_token(TokenType.EOF, ''))
        return tokens

    def match(self, pattern):
        regex = re.compile(pattern)
        match = regex.match(self.source_code, self.position)
        if match:
            self.current_match = match.group(0)
            return True
        return False

    def skip_whitespace(self):
        while self.position < len(self.source_code) and self.source_code[self.position].isspace():
            if self.source_code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def tokenize_comment(self, tokens):
        start = self.position
        self.position += 2  # Skip '(*'
        self.column += 2
        while self.position < len(self.source_code):
            if self.source_code[self.position:self.position+2] == '*)':
                self.position += 2
                self.column += 2
                comment = self.source_code[start:self.position]
                tokens.append(self.create_token(TokenType.COMMENT, comment))
                return
            if self.source_code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
        raise SyntaxError(f"Unterminated comment starting at line {self.line}, column {self.column}")

    def tokenize_string(self, tokens):
        start_line, start_column = self.line, self.column
        string_content = ""
        self.advance()  # Skip the opening quote
        while self.current_char is not None:
            if self.current_char == '"':
                self.advance()  # Skip the closing quote
                tokens.append(Token(TokenType.STRING, string_content, start_line, start_column))
                return
            elif self.current_char == '{' and self.peek() == '{':
                # Handle string interpolation
                self.advance()  # Skip first '{'
                self.advance()  # Skip second '{'
                string_content += "{{"
                while self.current_char is not None and (self.current_char != '}' or self.peek() != '}'):
                    string_content += self.current_char
                    self.advance()
                if self.current_char == '}' and self.peek() == '}':
                    self.advance()  # Skip first '}'
                    self.advance()  # Skip second '}'
                    string_content += "}}"
                else:
                    raise SyntaxError(f"Expected '}}}}' for string interpolation at line {self.line}, column {self.column}")
            else:
                string_content += self.current_char
                self.advance()
        raise SyntaxError(f"Unterminated string starting at line {start_line}, column {start_column}")

    def tokenize_multi_line_comment(self, tokens):
        start = self.position
        self.position += 2  # Skip (*
        while self.position < len(self.source_code) - 1 and self.source_code[self.position:self.position+2] != '*)':
            self.position += 1
        if self.position >= len(self.source_code) - 1:
            raise SyntaxError("Unclosed multi-line comment")
        self.position += 2  # Skip *)
        comment = self.source_code[start:self.position]
        self.debug_log(f"Found multi-line comment: {comment}", token_type=TokenType.COMMENT)
        tokens.append(self.create_token(TokenType.COMMENT, comment))

    def create_token(self, token_type, value):
        token = Token(token_type, value, self.line, self.column)
        if isinstance(value, str):
            lines = value.split('\n')
            if len(lines) > 1:
                self.line += len(lines) - 1
                self.column = len(lines[-1]) + 1
            else:
                self.column += len(value)
        else:
            self.column += len(str(value))
        self.position += len(str(value))
        return token

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
        if self.position < len(self.source_code):
            self.current_char = self.source_code[self.position]
        else:
            self.current_char = None

    def peek(self):
        peek_pos = self.position + 1
        if peek_pos < len(self.source_code):
            return self.source_code[peek_pos]
        return None

def lex(source_code, debug=False):
    lexer = Lexer(source_code, debug)
    return lexer.tokenize()

# Example usage
if __name__ == "__main__":
    sample_code = """
    @ink fibonacci(n: Int) -> Int ~
        if n <= 1 ~
            return n;
        ~
        return fibonacci(n - 1) + fibonacci(n - 2);
    ~

    @ink calculate_pressure(depth: Float, gravity: Float = 9.8) -> Float ~
        return depth * gravity / 1000;
    ~

    @ink complex_calculation(x: Float, y: Float, z: Float) -> Float ~
        let result = (x * y) / (z + 1);
        return result * fibonacci(5);
    ~

    let depth = 5000.0;
    let pressure = calculate_pressure(depth);

    let x = 10.5;
    let y = 20.7;
    let z = 3.14;

    let complex_result = complex_calculation(x, y, z);

    print("Fibonacci(10): {{fibonacci(10)}}");
    print("Pressure at {{depth}}m: {{pressure}} Pa");
    print("Complex calculation result: {{complex_result}}");

    let recursive_depth = 15;
    print("Fibonacci({{recursive_depth}}): {{fibonacci(recursive_depth)}}");
    """

    print("Tokenizing with debug output:")
    tokens = lex(sample_code, debug=True)
    print("Tokenization complete.")

    for token in tokens:
        print(f"{token.line}:{token.column} {token.type}: {repr(token.value)}")