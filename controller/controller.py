from model.lexer import lex
from model.parser_1 import parse
from model.semantic_analysis import evaluate, Logger

class LambdaCalcController:
    def __init__(self, view):
        self.view = view
        self.view.set_eval_button_command(self.evaluate_expression)

    def evaluate_expression(self):
        expression = self.view.get_expression()
        try:
            # Lexical analysis
            tokens = lex(expression)
            self.view.display_tokens(tokens)

            # Parsing
            ast = parse(tokens)
            self.view.display_ast(ast)

            # Evaluation with capturing output
            logger = Logger()
            result, logger = evaluate(ast, logger)
            evaluation_steps = logger.get_steps()
            evaluation_steps.append(f"Result: {result}")
            self.view.display_evaluation(evaluation_steps)
        except Exception as e:
            self.view.show_error(str(e))
