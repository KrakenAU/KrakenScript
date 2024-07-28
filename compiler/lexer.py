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
        while self.position < len(self.source_code):
            if self.match(r'\s+'):
                self.skip_whitespace()
            elif self.match(r'//'):
                self.debug_log("Found single-line comment", token_type=TokenType.COMMENT)
                self.tokenize_single_line_comment(tokens)
            elif self.match(r'\(\*'):
                self.debug_log("Found comment", token_type=TokenType.COMMENT)
                self.tokenize_comment(tokens)
            elif self.match(r'@ink|let|const|if|else|for|return'):
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
                self.debug_log(f"Unexpected character: {self.source_code[self.position]}", color=colorama.Fore.RED)
                raise SyntaxError(f"Unexpected character: {self.source_code[self.position]} at line {self.line}, column {self.column}")

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
        start = self.position
        self.position += 1  # Skip opening quote
        self.column += 1
        while self.position < len(self.source_code):
            if self.source_code[self.position] == '"':
                self.position += 1
                self.column += 1
                tokens.append(self.create_token(TokenType.STRING, self.source_code[start:self.position]))
                return
            elif self.source_code[self.position:self.position+2] == '{{':
                if start < self.position:
                    tokens.append(self.create_token(TokenType.STRING, self.source_code[start:self.position]))
                self.position += 2
                self.column += 2
                interp_start = self.position
                interp_depth = 1
                while self.position < len(self.source_code) and interp_depth > 0:
                    if self.source_code[self.position:self.position+2] == '{{':
                        interp_depth += 1
                        self.position += 2
                        self.column += 2
                    elif self.source_code[self.position:self.position+2] == '}}':
                        interp_depth -= 1
                        self.position += 2
                        self.column += 2
                    else:
                        if self.source_code[self.position] == '\n':
                            self.line += 1
                            self.column = 1
                        else:
                            self.column += 1
                        self.position += 1
                if interp_depth > 0:
                    raise SyntaxError(f"Unterminated string interpolation starting at line {self.line}, column {self.column}. Expected '}}' to close the interpolation.")
                tokens.append(self.create_token(TokenType.IDENTIFIER, self.source_code[interp_start:self.position-2]))
                start = self.position
            else:
                if self.source_code[self.position] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.position += 1
        raise SyntaxError(f"Unterminated string starting at line {self.line}, column {self.column}")

    def tokenize_single_line_comment(self, tokens):
        start = self.position
        while self.position < len(self.source_code) and self.source_code[self.position] != '\n':
            self.position += 1
            self.column += 1
        comment = self.source_code[start:self.position]
        tokens.append(self.create_token(TokenType.COMMENT, comment))

    def create_token(self, token_type, value):
        if token_type == TokenType.STRING:
            # Strip quotes for string tokens
            value = value[1:-1]
        token = Token(token_type, value, self.line, self.column)
        if isinstance(value, str):
            lines = value.split('\n')
            if len(lines) > 1:
                self.line += len(lines) - 1
                self.column = len(lines[-1]) + 1
            else:
                self.column += len(value) + (2 if token_type == TokenType.STRING else 0)
        else:
            self.column += len(str(value))
        self.position += len(str(value)) + (2 if token_type == TokenType.STRING else 0)
        return token

def lex(source_code, debug=False):
    lexer = Lexer(source_code, debug)
    return lexer.tokenize()

# Example usage
if __name__ == "__main__":
    sample_code = """
    // This is a comment
    @ink calculate_pressure(depth: Float, gravity: Float = 9.8) -> Float ~
        (* Calculate pressure at given depth *)
        return depth * gravity * 1000;
    ~

    let depth = 5000.0;
    let pressure = calculate_pressure(depth);
    print("Pressure at {{depth}}m: {{pressure}} Pa");
    """

    print("Tokenizing with debug output:")
    tokens = lex(sample_code, debug=True)
    print("Tokenization complete.")