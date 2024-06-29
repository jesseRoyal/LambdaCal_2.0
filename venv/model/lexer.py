import ply.lex as lex

tokens = (
    'LAMBDA',
    'DOT',
    'VAR',
    'LPAREN',
    'RPAREN',
)

t_LAMBDA = r'\#'
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_VAR(t):
    r'[a-zA-Z]'
    return t

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()
