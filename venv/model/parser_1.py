import ply.yacc as yacc
from model.lexer import tokens

class Expr:
    pass

class Var(Expr):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Lambda(Expr):
    def __init__(self, var, body):
        self.var = var
        self.body = body

    def __repr__(self):
        return f"(λ{self.var}.{self.body})"

class App(Expr):
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

    def __repr__(self):
        return f"({self.func} {self.arg})"

def p_expr_var(p):
    'expr : VAR'
    p[0] = Var(p[1])

def p_expr_lambda(p):
    'expr : LAMBDA VAR DOT expr'
    p[0] = Lambda(p[2], p[4])

def p_expr_app(p):
    'expr : expr expr'
    p[0] = App(p[1], p[2])

def p_expr_paren(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_error(p):
    print(f"Syntax error at '{p.value}'")

parser = yacc.yacc()
