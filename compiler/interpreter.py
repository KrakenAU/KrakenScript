from ast_nodes import ASTNodeType

class Interpreter:
    def __init__(self):
        self.global_scope = {}
        self.functions = {}

    def interpret(self, ast):
        self.visit(ast)

    def visit(self, node):
        method_name = f'visit_{node.type.name.lower()}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        print(f"No visit method for {node.type}")

    def visit_program(self, node):
        for child in node.children:
            self.visit(child)

    def visit_function_declaration(self, node):
        function_name = node.value
        self.functions[function_name] = node

    def visit_variable_declaration(self, node):
        var_name = node.value
        value = self.visit(node.children[0])
        self.global_scope[var_name] = value

    def visit_expression(self, node):
        if node.value in self.global_scope:
            return self.global_scope[node.value]
        try:
            return float(node.value)
        except ValueError:
            return node.value

    def visit_function_call(self, node):
        function_name = node.value
        if function_name not in self.functions:
            raise NameError(f"Function '{function_name}' is not defined")
        
        function_node = self.functions[function_name]
        parameters = function_node.children[0].children
        arguments = node.children

        local_scope = {}
        for i, param in enumerate(parameters):
            if i < len(arguments):
                local_scope[param.value] = self.visit(arguments[i])
            else:
                # Use default value if provided, otherwise raise an error
                if len(param.children) > 1:
                    local_scope[param.value] = self.visit(param.children[1])
                else:
                    raise ValueError(f"Missing argument for parameter '{param.value}'")

        # Save current global scope
        old_global_scope = self.global_scope.copy()
        
        # Update global scope with local scope for function execution
        self.global_scope.update(local_scope)

        # Execute function body
        body = function_node.children[2]
        result = None
        for statement in body.children:
            result = self.visit(statement)
            if isinstance(result, tuple) and result[0] == 'return':
                result = result[1]
                break

        # Restore old global scope
        self.global_scope = old_global_scope

        return result

    def visit_return_statement(self, node):
        value = self.visit(node.children[0])
        return ('return', value)

    def visit_print_statement(self, node):
        value = self.visit(node.children[0])
        print(self.interpolate_string(value))

    def visit_binary_operation(self, node):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])
        left = float(left) if isinstance(left, str) else left
        right = float(right) if isinstance(right, str) else right
        if node.value == '*':
            return left * right
        elif node.value == '/':
            return left / right
        elif node.value == '+':
            return left + right
        elif node.value == '-':
            return left - right

    def interpolate_string(self, string):
        result = string
        for var_name, var_value in self.global_scope.items():
            placeholder = f"{{{{{var_name}}}}}"
            result = result.replace(placeholder, str(var_value))
        return result