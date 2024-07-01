import openai
from model.lexer import lexer
from model.parser_1 import parser
from model.semantic_analysis import evaluate, Logger
from config import OPENAI_API_KEY

class LambdaCalcController:
    def __init__(self, view):
        self.view = view
        self.view.set_eval_button_command(self.evaluate_expression)
        #openai.api_key = OPENAI_API_KEY

    def evaluate_expression(self):
        expression = self.view.get_expression()
        try:
            # Lexical analysis
            lexer.input(expression)
            tokens = []
            while True:
                tok = lexer.token()
                if not tok:
                    break
                tokens.append(tok)
            self.view.display_tokens(tokens)

            # Parsing
            ast = parser.parse(expression)
            self.view.display_ast(ast)

            # Evaluation with capturing output
            logger = Logger()
            result, logger = evaluate(ast, logger)
            evaluation_steps = logger.get_steps()
            evaluation_steps.append(f"Result: {result}")
            self.view.display_evaluation(evaluation_steps)

            # Get explanations from ChatGPT
            explanations = self.get_chatgpt_explanations(evaluation_steps)
            self.view.display_explanations(explanations)
        except Exception as e:
            self.view.show_error(str(e))

    def get_chatgpt_explanations(self, steps):
        # Construct a prompt with the evaluation steps
        prompt = "Explain the following lambda calculus evaluation steps:\n\n"
        for step in steps:
            prompt += step + "\n"
        
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=500
        )
        
        return response.choices[0].text.strip()
