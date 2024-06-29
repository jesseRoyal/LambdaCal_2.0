import tkinter as tk
from tkinter import messagebox

class LambdaCalcView:
    def __init__(self, root):
        self.root = root
        self.root.title("Lambda Calculus Interpreter")

        # Input frame
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)

        self.expr_label = tk.Label(input_frame, text="Lambda Expression:")
        self.expr_label.pack(side=tk.LEFT, padx=5)

        self.expr_entry = tk.Entry(input_frame, width=50)
        self.expr_entry.pack(side=tk.LEFT, padx=5)

        self.eval_button = tk.Button(input_frame, text="Evaluate")
        self.eval_button.pack(side=tk.LEFT, padx=5)

        # Output frame
        output_frame = tk.Frame(root)
        output_frame.pack(pady=10)

        self.tokens_label = tk.Label(output_frame, text="Tokens:")
        self.tokens_label.pack(anchor=tk.W)

        self.tokens_text = tk.Text(output_frame, height=5, width=80)
        self.tokens_text.pack(pady=5)

        self.ast_label = tk.Label(output_frame, text="AST:")
        self.ast_label.pack(anchor=tk.W)

        self.ast_text = tk.Text(output_frame, height=5, width=80)
        self.ast_text.pack(pady=5)

        self.evaluation_label = tk.Label(output_frame, text="Evaluation Steps:")
        self.evaluation_label.pack(anchor=tk.W)

        self.evaluation_text = tk.Text(output_frame, height=10, width=80)
        self.evaluation_text.pack(pady=5)

        self.explanation_label = tk.Label(output_frame, text="Explanations:")
        self.explanation_label.pack(anchor=tk.W)

        self.explanation_text = tk.Text(output_frame, height=10, width=80)
        self.explanation_text.pack(pady=5)

    def set_eval_button_command(self, command):
        self.eval_button.config(command=command)

    def get_expression(self):
        return self.expr_entry.get()

    def display_tokens(self, tokens):
        self.tokens_text.delete(1.0, tk.END)
        self.tokens_text.insert(tk.END, tokens)

    def display_ast(self, ast):
        self.ast_text.delete(1.0, tk.END)
        self.ast_text.insert(tk.END, ast)

    def display_evaluation(self, evaluation_steps):
        self.evaluation_text.delete(1.0, tk.END)
        for step in evaluation_steps:
            self.evaluation_text.insert(tk.END, step + "\n")

    def display_explanations(self, explanations):
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.insert(tk.END, explanations)

    def show_error(self, message):
        messagebox.showerror("Error", message)
