import string
from model.parser_1 import Var, Lambda, App

# Depth limit to avoid infinite recursion
DEPTH_LIMIT = 1000

class Logger:
    """Logger for keeping track of evaluation steps."""

    def __init__(self):
        """Initialize logger with an empty list of steps."""
        self.steps = []

    def log(self, *args):
        """Log a message with the current step number and args."""
        message = " ".join(map(str, args))
        self.steps.append(message)

    def get_steps(self):
        """Return the list of evaluation steps."""

    def log(self, *args):
        """
        Log a message with the current step number and args.

        Args:
            *args: Variable number of arguments to be concatenated into a string.
        """
        # Join the arguments into a single string
        message = " ".join(map(str, args))
        # Append the message to the list of steps
        self.steps.append(message)

    def get_steps(self):
        """
        Return the list of evaluation steps.

        This method returns the list of evaluation steps that have been logged
        by the logger. The list is returned as a copy to prevent modifications
        to the original list.

        Returns:
            list: A copy of the list of evaluation steps.
        """
        # Return a copy of the list of evaluation steps
        return self.steps.copy()

def fresh_var(used_vars):
    """Generate a fresh variable name not in used_vars."""
    for char in string.ascii_lowercase:
        if char not in used_vars:
            return char
    raise Exception("Ran out of fresh variables")

def alpha_convert(expr, old_var, new_var):
    """
    Perform alpha conversion by renaming variables.

    Args:
        expr (Expr): The expression to perform alpha conversion on.
        old_var (str): The variable to be renamed.
        new_var (str): The new name to give to the variable.

    Returns:
        Expr: The expression with all occurrences of old_var replaced by new_var.
    """
    # Base case: If the expression is a variable
    if isinstance(expr, Var):
        # If the variable is the one to be renamed, return a new variable with the new name
        return Var(new_var) if expr.name == old_var else expr
    # Base case: If the expression is a lambda abstraction
    elif isinstance(expr, Lambda):
        # If the variable is the one being abstracted, rename it and recursively alpha convert the body
        if expr.var == old_var:
            return Lambda(new_var, alpha_convert(expr.body, old_var, new_var))
        # If the variable is not the one being abstracted, recursively alpha convert the body and return the lambda abstraction with the new body
        return Lambda(expr.var, alpha_convert(expr.body, old_var, new_var))
    # Base case: If the expression is an application
    elif isinstance(expr, App):
        # Recursively alpha convert the function and argument expressions and return the new application
        return App(alpha_convert(expr.func, old_var, new_var), alpha_convert(expr.arg, old_var, new_var))
    # Base case: If the expression is neither a variable, lambda abstraction, nor application, return the expression as is
    return expr

def substitute(body, var, value):
    """
    Substitute occurrences of var in body with value.

    This function performs alpha conversion to avoid shadowing, which would
    prevent the substitution from being performed. It also handles the case
    where the value being substituted into the body contains a free variable
    that is already in use in the body.

    Args:
        body (Expr): The expression to perform substitution on.
        var (str): The variable to be substituted.
        value (Expr): The expression to substitute into the body.

    Returns:
        Expr: The expression with all occurrences of var replaced with value.
    """
    # Base case: If the expression is a variable
    if isinstance(body, Var):
        # If the variable is the one to be substituted, return the value
        # Otherwise, return the variable as is
        return value if body.name == var else body
    # Base case: If the expression is a lambda abstraction
    elif isinstance(body, Lambda):
        # If the variable is the one being abstracted, return the lambda abstraction as is
        if body.var == var:
            return body
        # If the variable is not the one being abstracted, check if the value contains a free variable
        # that is already in use in the body. If so, generate a fresh variable name and perform alpha conversion
        if body.var in free_vars(value):
            # Generate a fresh variable name not in use in the body or the value
            new_var = fresh_var(free_vars(body) | free_vars(value))
            # Perform alpha conversion on the lambda abstraction to rename the variable being abstracted
            # to the fresh variable name
            body = alpha_convert(body, body.var, new_var)
        # Recursively perform substitution on the body of the lambda abstraction
        return Lambda(body.var, substitute(body.body, var, value))
    # Base case: If the expression is an application
    elif isinstance(body, App):
        # Recursively perform substitution on the function and argument expressions of the application
        # and return the new application
        return App(substitute(body.func, var, value), substitute(body.arg, var, value))
    # Base case: If the expression is neither a variable, lambda abstraction, nor application, return the expression as is
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
    """
    Perform beta reduction.

    Beta reduction is the process of substituting a lambda abstraction's body with
    an expression that is being applied to the lambda abstraction.

    Args:
        expr (Expr): The expression to perform beta reduction on.
        logger (Logger): The logger object to log the steps of the beta reduction.

    Returns:
        Expr: The result of the beta reduction.
    """
    # Check if the expression is an application of a lambda abstraction
    if isinstance(expr, App) and isinstance(expr.func, Lambda):
        # Log the step of beta reduction
        logger.log(f"Performing Beta Reduction: ({expr.func}) ({expr.arg})")
        
        # Perform substitution on the lambda abstraction's body with the lambda abstraction's variable
        # and the expression being applied to the lambda abstraction
        return substitute(expr.func.body, expr.func.var, expr.arg)
    
    # If the expression is not an application of a lambda abstraction, return the expression as is
    return expr

def eta_reduce(expr, logger):
    """
    Perform eta reduction.

    Eta reduction is the process of removing the outermost lambda abstraction in a term
    if it is not necessary to determine the normal form of the term. This is done by
    checking if the lambda abstraction's body is an application of a variable to itself.
    If this is the case, the lambda abstraction can be safely removed.

    Args:
        expr (Expr): The expression to perform eta reduction on.
        logger (Logger): The logger object to log the steps of the eta reduction.

    Returns:
        Expr: The result of the eta reduction.
    """
    # Check if the expression is a lambda abstraction
    if isinstance(expr, Lambda):
        # Check if the lambda abstraction's body is an application of a variable
        if isinstance(expr.body, App) and isinstance(expr.body.arg, Var):
            # Check if the variable being applied is the same as the lambda abstraction's variable
            if expr.body.arg.name == expr.var:
                # Check if the variable being applied does not occur free in the function being applied to the variable
                if not occurs_free(expr.body.func, expr.var):
                    # Log the step of eta reduction
                    logger.log(f"Performing Eta Reduction: {expr}")
                    # Return the function being applied to the variable as the result of the eta reduction
                    return expr.body.func
    # If the expression is not a lambda abstraction or does not meet the conditions for eta reduction, return the expression as is
    return expr

def occurs_free(expr, var):
    """
    Check if the variable 'var' occurs free in the expression 'expr'.

    This function takes an expression and a variable as input and recursively checks
    if the variable occurs free within the expression. It returns a boolean value
    indicating whether the variable occurs free or not.

    Args:
        expr (Expr): The expression to check for the occurrence of the variable.
        var (str): The variable to check for its occurrence in the expression.

    Returns:
        bool: True if the variable occurs free in the expression, False otherwise.
    """

    # Base case: If the expression is a variable, check if its name matches the variable to check
    if isinstance(expr, Var):
        return expr.name == var
    
    # Base case: If the expression is a lambda abstraction, check if the variable being abstracted is the same as the variable to check
    elif isinstance(expr, Lambda):
        if expr.var == var:
            return False
        # Recursively call the occurs_free function on the body of the lambda abstraction with the variable to check
        return occurs_free(expr.body, var)
    
    # Base case: If the expression is an application, recursively call the occurs_free function on the function and argument expressions with the variable to check
    elif isinstance(expr, App):
        return occurs_free(expr.func, var) or occurs_free(expr.arg, var)
    
    # Base case: If the expression is neither a variable, lambda abstraction, nor application, the variable does not occur free in the expression
    return False

def is_normal_form(expr):
    """
    Check if the expression is in normal form.

    An expression is in normal form if it is either a variable, or it is an
    application of a function that is not a lambda abstraction, or it is an
    application of a lambda abstraction where the body of the lambda abstraction
    is also in normal form.

    Args:
        expr (Expr): The expression to check for normal form.

    Returns:
        bool: True if the expression is in normal form, False otherwise.
    """
    # Base case: If the expression is a variable, it is in normal form.
    if isinstance(expr, Var):
        return True
    
    # Base case: If the expression is a lambda abstraction, check if its body is in normal form.
    elif isinstance(expr, Lambda):
        return is_normal_form(expr.body)
    
    # Base case: If the expression is an application, check if the function is not a lambda abstraction, and if the function and argument are in normal form.
    elif isinstance(expr, App):
        return (not isinstance(expr.func, Lambda) and  # The function is not a lambda abstraction
                is_normal_form(expr.func) and  # The function is in normal form
                is_normal_form(expr.arg))  # The argument is in normal form
    
    # Base case: If the expression is neither a variable, lambda abstraction, nor application, it is not in normal form.
    return False

def is_recursive_comb(expr):
    """
    Check for self-application patterns like the Y combinator.

    This function takes an expression as input and checks if it is a recursive
    combinator. A recursive combinator is an expression that applies a lambda
    abstraction to itself. The Y combinator is a specific example of a recursive
    combinator.

    This function checks if the expression is a recursive combinator, which is an
    application of a lambda abstraction to itself. It returns True if it is a
    recursive combinator, False otherwise.

    Args:
        expr (Expr): The expression to check for self-application patterns.

    Returns:
        bool: True if the expression is a recursive combinator, False otherwise.
    """
    # Check if the expression is an application (App)
    if isinstance(expr, App):
        # Check if the function part of the application is a lambda abstraction (Lambda)
        if isinstance(expr.func, Lambda):
            # Check if the argument part of the application is also a lambda abstraction (Lambda)
            if isinstance(expr.arg, Lambda):
                # Check if the body of the argument lambda abstraction is an application (App)
                if isinstance(expr.arg.body, App):
                    # Check if the argument of the application is the same as the lambda abstraction itself
                    if expr.arg.body.arg == expr.arg:
                        return True
    # If none of the conditions are met, the expression is not a recursive combinator
    return False

def evaluate(expr, logger=None, depth=0):
    """
    Evaluate the expression by performing reductions until normal form is reached.

    Args:
        expr (Expr): The expression to evaluate.
        logger (Logger, optional): The logger object to log the steps of the evaluation.
            Defaults to None.
        depth (int, optional): The current depth of the evaluation. Defaults to 0.

    Returns:
        tuple: A tuple containing the final result of the evaluation and the logger object.
    """
    # If logger is not provided, create a new logger object
    if logger is None:
        logger = Logger()
    
    # Check if the depth limit has been reached
    if depth > DEPTH_LIMIT:
        # Log a message indicating that the depth limit has been reached
        logger.log("Depth limit reached. This expression cannot be reduced to a normal form.")
        # Return the expression and the logger object
        return expr, logger
    
    # Log the expression being evaluated
    logger.log(f"Evaluating: {expr}")
    
    # Check if the expression is a recursive combinator like the Y combinator
    if is_recursive_comb(expr):
        # Log a message indicating that a recursive combinator has been detected
        logger.log("Detected a recursive combinator (e.g., Y combinator). This expression may not reduce to a normal form.")
        # Return the expression and the logger object
        return expr, logger
    
    # While the expression is not in normal form, perform reductions
    while not is_normal_form(expr):
        # Perform beta reduction on the expression
        new_expr = beta_reduce(expr, logger)
        # If the new expression is different from the original expression, update the expression
        if new_expr != expr:
            expr = new_expr
            continue
        # Perform eta reduction on the expression
        new_expr = eta_reduce(expr, logger)
        # If the new expression is different from the original expression, update the expression
        if new_expr != expr:
            expr = new_expr
            continue
        # If the expression is an application
        if isinstance(expr, App):
            # Evaluate the function and the argument of the application
            expr.func, logger = evaluate(expr.func, logger, depth + 1)
            expr.arg, logger = evaluate(expr.arg, logger, depth + 1)
        # If the expression is a lambda abstraction
        elif isinstance(expr, Lambda):
            # Evaluate the body of the lambda abstraction
            expr.body, logger = evaluate(expr.body, logger, depth + 1)
    
    # Log the final result of the evaluation
    logger.log(f"Final result: {expr}")
    # Return the final result and the logger object
    return expr, logger
