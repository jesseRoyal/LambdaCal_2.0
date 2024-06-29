import string
from model.parser_1 import Var, Lambda, App

# Depth limit to avoid infinite recursion
DEPTH_LIMIT = 1000

class Logger:
    def __init__(self):
        self.steps = []

    def log(self, *args):
        message = " ".join(map(str, args))
        self.steps.append(message)

    def get_steps(self):
        return self.steps

def fresh_var(used_vars):
    """Generate a fresh variable name not in used_vars."""
    for char in string.ascii_lowercase:
        if char not in used_vars:
            return char
    raise Exception("Ran out of fresh variables")

def alpha_convert(expr, old_var, new_var):
    """Perform alpha conversion by renaming variables."""
    if isinstance(expr, Var):
        return Var(new_var) if expr.name == old_var else expr
    elif isinstance(expr, Lambda):
        if expr.var == old_var:
            return Lambda(new_var, alpha_convert(expr.body, old_var, new_var))
        return Lambda(expr.var, alpha_convert(expr.body, old_var, new_var))
    elif isinstance(expr, App):
        return App(alpha_convert(expr.func, old_var, new_var), alpha_convert(expr.arg, old_var, new_var))
    return expr

def substitute(body, var, value):
    """Substitute occurrences of var in body with value."""
    if isinstance(body, Var):
        return value if body.name == var else body
    elif isinstance(body, Lambda):
        if body.var == var:
            return body  # Shadowing prevents substitution
        if body.var in free_vars(value):
            new_var = fresh_var(free_vars(body) | free_vars(value))
            body = alpha_convert(body, body.var, new_var)
        return Lambda(body.var, substitute(body.body, var, value))
    elif isinstance(body, App):
        return App(substitute(body.func, var, value), substitute(body.arg, var, value))
    return body

def free_vars(expr):
    """Return the set of free variables in an expression."""
    if isinstance(expr, Var):
        return {expr.name}
    elif isinstance(expr, Lambda):
        return free_vars(expr.body) - {expr.var}
    elif isinstance(expr, App):
        return free_vars(expr.func) | free_vars(expr.arg)
    return set()

def beta_reduce(expr, logger):
    """Perform beta reduction."""
    if isinstance(expr, App) and isinstance(expr.func, Lambda):
        logger.log(f"Performing Beta Reduction: ({expr.func}) ({expr.arg})")
        return substitute(expr.func.body, expr.func.var, expr.arg)
    return expr

def eta_reduce(expr, logger):
    """Perform eta reduction."""
    if isinstance(expr, Lambda):
        if isinstance(expr.body, App) and isinstance(expr.body.arg, Var) and expr.body.arg.name == expr.var:
            if not occurs_free(expr.body.func, expr.var):
                logger.log(f"Performing Eta Reduction: {expr}")
                return expr.body.func
    return expr

def occurs_free(expr, var):
    """Check if var occurs free in expr."""
    if isinstance(expr, Var):
        return expr.name == var
    elif isinstance(expr, Lambda):
        if expr.var == var:
            return False
        return occurs_free(expr.body, var)
    elif isinstance(expr, App):
        return occurs_free(expr.func, var) or occurs_free(expr.arg, var)
    return False

def is_normal_form(expr):
    """Check if the expression is in normal form."""
    if isinstance(expr, Var):
        return True
    elif isinstance(expr, Lambda):
        return is_normal_form(expr.body)
    elif isinstance(expr, App):
        return not isinstance(expr.func, Lambda) and is_normal_form(expr.func) and is_normal_form(expr.arg)
    return False

def is_recursive_comb(expr):
    """Check for self-application patterns like the Y combinator."""
    if isinstance(expr, App):
        if isinstance(expr.func, Lambda):
            if isinstance(expr.arg, Lambda):
                if isinstance(expr.arg.body, App):
                    if expr.arg.body.arg == expr.arg:
                        return True
    return False

def evaluate(expr, logger=None, depth=0):
    """Evaluate the expression by performing reductions until normal form is reached."""
    if logger is None:
        logger = Logger()

    if depth > DEPTH_LIMIT:
        logger.log("Depth limit reached. This expression cannot be reduced to a normal form.")
        return expr, logger
    logger.log(f"Evaluating: {expr}")
    if is_recursive_comb(expr):
        logger.log("Detected a recursive combinator (e.g., Y combinator). This expression may not reduce to a normal form.")
        return expr, logger
    while not is_normal_form(expr):
        new_expr = beta_reduce(expr, logger)
        if new_expr != expr:
            expr = new_expr
            continue
        new_expr = eta_reduce(expr, logger)
        if new_expr != expr:
            expr = new_expr
            continue
        if isinstance(expr, App):
            expr.func, logger = evaluate(expr.func, logger, depth + 1)
            expr.arg, logger = evaluate(expr.arg, logger, depth + 1)
        elif isinstance(expr, Lambda):
            expr.body, logger = evaluate(expr.body, logger, depth + 1)
    logger.log(f"Final result: {expr}")
    return expr, logger
