from enum import Enum, auto
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from parser import ASTNode, ASTNodeType

console = Console()

class SemanticError(Exception):
    pass

class SymbolType(Enum):
    VARIABLE = auto()
    CONSTANT = auto()
    FUNCTION = auto()

class Symbol:
    def __init__(self, name: str, symbol_type: SymbolType, data_type: str = None):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type

class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def add_symbol(self, symbol: Symbol):
        if symbol.name in self.symbols:
            raise SemanticError(f"Symbol '{symbol.name}' is already defined")
        self.symbols[symbol.name] = symbol

    def get_symbol(self, name: str) -> Symbol:
        return self.symbols.get(name)

class SemanticGenerator:
    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.symbol_table = SymbolTable()
        self.debug_mode = False
        self.initialize_built_ins()
            
    def initialize_built_ins(self):
        built_ins = ["print"]
        for func_name in built_ins:
            self.symbol_table.add_symbol(Symbol(func_name, SymbolType.FUNCTION))

    def generate(self):
        self.log_info("Starting semantic analysis")
        self.visit(self.ast)
        self.log_info("Semantic analysis complete")

    def visit(self, node: ASTNode):
        method_name = f"visit_{node.type.name.lower()}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ASTNode):
        for child in node.children:
            self.visit(child)

    def visit_program(self, node: ASTNode):
        self.log_debug("Visiting program node")
        self.generic_visit(node)

    def visit_function_declaration(self, node: ASTNode):
        self.log_debug(f"Visiting function declaration: {node.children[0].value}")
        name = node.children[0].value
        return_type = node.children[-2].value if len(node.children) > 3 else None
        symbol = Symbol(name, SymbolType.FUNCTION, return_type)
        self.symbol_table.add_symbol(symbol)
        self.generic_visit(node)

    def visit_variable_declaration(self, node: ASTNode):
        self.log_debug(f"Visiting variable declaration: {node.children[0].value}")
        name = node.children[0].value
        data_type = node.children[1].value if len(node.children) > 2 else None
        symbol = Symbol(name, SymbolType.VARIABLE, data_type)
        self.symbol_table.add_symbol(symbol)

    def visit_constant_declaration(self, node: ASTNode):
        self.log_debug(f"Visiting constant declaration: {node.children[0].value}")
        name = node.children[0].value
        data_type = node.children[1].value if len(node.children) > 2 else None
        symbol = Symbol(name, SymbolType.CONSTANT, data_type)
        self.symbol_table.add_symbol(symbol)

    def visit_if_statement(self, node: ASTNode):
        self.log_debug("Visiting if statement")
        self.generic_visit(node)

    def visit_return_statement(self, node: ASTNode):
        self.log_debug("Visiting return statement")
        self.generic_visit(node)
        
    def visit_function_call(self, node: ASTNode):
        self.log_debug("Visiting function call node:")
        self.log_node_info(node)
        
        function_name = None
        for child in node.children:
            if isinstance(child, ASTNode) and child.type == ASTNodeType.IDENTIFIER:
                function_name = child.value
                break
        
        if function_name is None:
            self.log_debug("Could not find function name in children, checking node value")
            function_name = node.value

        self.log_debug(f"Function name: {function_name}")
        
        if function_name and function_name != 'None' and not self.symbol_table.get_symbol(function_name):
            raise SemanticError(f"Function '{function_name}' is not defined")
        
        self.generic_visit(node)
    
    def log_node_info(self, node: ASTNode):
        self.log_debug(f"Node type: {node.type}")
        self.log_debug(f"Node value: {node.value}")
        self.log_debug("Node children:")
        for i, child in enumerate(node.children):
            if isinstance(child, ASTNode):
                self.log_debug(f"  Child {i}: {child.type} - {child.value}")
            else:
                self.log_debug(f"  Child {i}: {child}")

    def log_info(self, message):
        if self.debug_mode:
            console.print(f"[bold blue]INFO:[/bold blue] {message}")

    def log_debug(self, message):
        if self.debug_mode:
            console.print(f"[bold green]DEBUG:[/bold green] {message}")

def generate_and_debug(ast):
    console.print(Panel.fit("[bold cyan]Starting Semantic Analysis[/bold cyan]", border_style="cyan"))
    
    generator = SemanticGenerator(ast)
    generator.debug_mode = True
    generator.generate()
    
    console.print(Panel.fit("[bold green]Semantic Analysis Complete[/bold green]", border_style="green"))
    print_symbol_table(generator.symbol_table)
    
    return generator.symbol_table

def print_symbol_table(symbol_table):
    from rich.table import Table

    table = Table(title="Symbol Table")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Data Type", style="yellow")

    for name, symbol in symbol_table.symbols.items():
        table.add_row(name, str(symbol.symbol_type.name), str(symbol.data_type))

    console.print(table)

if __name__ == "__main__":
    from parser import parse_and_debug
    from lexer import lex_and_debug
    
    source_code = """
fun factorial(n: num) -> num
    if n <= 1
        return 1
    return n * factorial(n - 1)

var x = 10
const PI: float = 3.14159
var result = factorial(x)
print("Factorial of", x, "is", result)
"""
    
    tokens = lex_and_debug(source_code)
    ast = parse_and_debug(tokens)
    symbol_table = generate_and_debug(ast)