class Expr:
    """Base class for expressions."""
    pass

class Var(Expr):
    """Class for variables."""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Lambda(Expr):
    """Class for lambda abstractions."""
    def __init__(self, var, body):
        self.var = var
        self.body = body

    def __repr__(self):
        return f"(λ{self.var}.{self.body})"

class App(Expr):
    """Class for function applications."""
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

    def __repr__(self):
        return f"({self.func} {self.arg})"

def parse(tokens):
    """
    Parse tokens into an abstract syntax tree (AST) based on the grammar.

    Args:
        tokens (list): A list of tuples containing token types and values.

    Returns:
        Expr: The parsed abstract syntax tree.
    """

    def parse_expr(index):
        """
        Parse an expression.

        Args:
            index (int): The index of the current token.

        Returns:
            tuple: A tuple containing the parsed expression and the index of the next token.
        """
        # Check if the current token is a lambda expression
        if tokens[index][0] == 'LAMBDA':
            # Parse the variable name
            var = tokens[index + 1][1]

            # Check if the next token is a dot
            if tokens[index + 2][0] != 'DOT':
                raise SyntaxError("Expected '.'")

            # Parse the body of the lambda expression
            body, next_index = parse_expr(index + 3)

            # Return the parsed lambda expression and the index of the next token
            return Lambda(var, body), next_index
        else:
            # Parse a function
            return parse_func(index)

    def parse_func(index):
        """
        Parse a function.

        A function can be an argument followed by zero or more arguments.

        Args:
            index (int): The index of the current token.

        Returns:
            tuple: A tuple containing the parsed function and the index of the next token.
        """
        # Parse the first argument
        expr, index = parse_arg(index)

        # Parse zero or more arguments
        while index < len(tokens) and tokens[index][0] in ['VAR', 'LPAREN', 'LAMBDA']:
            # Parse the next argument
            arg, index = parse_arg(index)

            # Apply the function to the argument
            expr = App(expr, arg)

        # Return the parsed function and the index of the next token
        return expr, index

    def parse_arg(index):
        """
        Parse an argument.

        Args:
            index (int): The index of the current token.

        Returns:
            tuple: A tuple containing the parsed argument and the index of the next token.
        """
        # Get the token type and value of the current token
        token_type, value = tokens[index]

        # Parse a variable
        if token_type == 'VAR':
            return Var(value), index + 1  # Return the parsed variable and the next index

        # Parse an expression in parentheses
        elif token_type == 'LPAREN':
            expr, index = parse_expr(index + 1)  # Parse the expression inside the parentheses

            # Check if the next token is a closing parenthesis
            if tokens[index][0] != 'RPAREN':
                raise SyntaxError("Expected ')'")

            return expr, index + 1  # Return the parsed expression and the next index

        # Parse a lambda expression
        elif token_type == 'LAMBDA':
            return parse_expr(index)  # Parse the lambda expression recursively

        # Raise an exception for unexpected expressions
        raise SyntaxError("Unexpected expression")

    ast, _ = parse_expr(0)
    return ast
