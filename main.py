from lexer import lex
from parser_1 import parse
from semantic_analysis import evaluate

def main():
    """
    Main function providing a command-line interface for the LambdaPy interpreter.
    This function reads user input, tokenizes it, parses it, and evaluates it.
    """
    print("Welcome to LambdaPy Interpreter. Enter expressions or type 'exit' to quit.")

    while True:
        try:
            # Read user input
            input_expr = input("LambdaPy> ")

            # Exit if user types 'exit'
            if input_expr.lower() == 'exit':
                break

            # Tokenize user input
            tokens = lex(input_expr)

            # Print tokens
            print("Tokens:", tokens)

            # Parse tokens into an abstract syntax tree (AST)
            ast = parse(tokens)

            # Print AST
            print("AST:", ast)

            # Evaluate the AST to get the result in normal form
            result = evaluate(ast)

            # Print the result in normal form
            print("Result in normal form:", result)

        except Exception as e:
            # Print any errors that occur during the process
            print("Error:", e)

if __name__ == "__main__":
    main()
