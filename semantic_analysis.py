import string
from parser_1 import Var, Lambda, App

# Depth limit to avoid infinite recursion
DEPTH_LIMIT = 1000

def fresh_var(used_vars):
    """
    Generate a fresh variable name not in used_vars.

    Args:
        used_vars (set): Set of variable names already in use.

    Returns:
        str: A fresh variable name.

    Raises:
        Exception: If all lowercase letters are already in use.
    """
    # Iterate over all lowercase letters
    for char in string.ascii_lowercase:
        # If the letter is not in used_vars, it is a fresh variable
        if char not in used_vars:
            return char
    # If all lowercase letters are in use, raise an exception
    raise Exception("Ran out of fresh variables")

def alpha_convert(expr, old_var, new_var):
    """
    Perform alpha conversion by renaming variables.

    Args:
        expr (Expr): The expression to perform alpha conversion on.
        old_var (str): The variable to be renamed.
        new_var (str): The new variable name.

    Returns:
        Expr: The expression with variables renamed.
    """
    # If the expression is a variable, rename it if it matches the old variable
    if isinstance(expr, Var):
        return Var(new_var) if expr.name == old_var else expr
    # If the expression is a lambda, rename the variable if it matches the old variable
    elif isinstance(expr, Lambda):
        if expr.var == old_var:
            return Lambda(new_var, alpha_convert(expr.body, old_var, new_var))
        return Lambda(expr.var, alpha_convert(expr.body, old_var, new_var))
    # If the expression is an application, rename variables in the function and argument
    elif isinstance(expr, App):
        return App(alpha_convert(expr.func, old_var, new_var),
                   alpha_convert(expr.arg, old_var, new_var))
    # If the expression is not one of the above, return it as is
    return expr

def substitute(body, var, value):
    """
    Substitute occurrences of var in body with value.

    Args:
        body (Expr): The expression to substitute in.
        var (str): The variable to substitute for.
        value (Expr): The expression to substitute with.

    Returns:
        Expr: The expression with substitutions applied.
    """
    # If the body is a variable, substitute if it matches the variable to substitute for
    if isinstance(body, Var):
        return value if body.name == var else body
    # If the body is a lambda, substitute if the lambda variable matches the variable to substitute for
    elif isinstance(body, Lambda):
        if body.var == var:
            return body  # Shadowing prevents substitution
        # If the variable to substitute for is free in the value, alpha convert the lambda to avoid capture
        if body.var in free_vars(value):
            new_var = fresh_var(free_vars(body) | free_vars(value))
            body = alpha_convert(body, body.var, new_var)
        # Recursively substitute in the body of the lambda
        return Lambda(body.var, substitute(body.body, var, value))
    # If the body is an application, recursively substitute in the function and argument
    elif isinstance(body, App):
        return App(substitute(body.func, var, value), substitute(body.arg, var, value))
    # If the body is not one of the above, return it as is
    return body

def free_vars(expr):
    """
    Return the set of free variables in an expression.

    Args:
        expr (Expr): The expression to find free variables in.

    Returns:
        set: A set of variable names that are free in the expression.
    """
    # If the expression is a variable, return a set containing its name
    if isinstance(expr, Var):
        return {expr.name}
    # If the expression is a lambda, return the free variables in the body
    # minus the lambda variable
    elif isinstance(expr, Lambda):
        return free_vars(expr.body) - {expr.var}
    # If the expression is an application, return the union of the free variables
    # in the function and argument
    elif isinstance(expr, App):
        return free_vars(expr.func) | free_vars(expr.arg)
    # If the expression is none of the above, return an empty set
    return set()

def beta_reduce(expr):
    """
    Perform beta reduction.

    Args:
        expr (Expr): The expression to perform beta reduction on.

    Returns:
        Expr: The expression with beta reduction applied.
    """
    # Check if the expression is an application of a lambda function
    if isinstance(expr, App) and isinstance(expr.func, Lambda):
        # Print the expression before and after reduction
        print(f"Performing Beta Reduction: ({expr.func}) ({expr.arg})")
        # Perform substitution of the lambda variable with the argument
        # in the body of the lambda function
        return substitute(expr.func.body, expr.func.var, expr.arg)
    # If the expression is not an application of a lambda function, return it as is
    return expr

def eta_reduce(expr):
    """
    Perform eta reduction.

    This function checks if the given expression is a lambda expression and if it is
    an application of a function to a variable, where the variable is the only free
    variable in the function. If these conditions are met, the function performs eta
    reduction by removing the lambda abstraction.

    Args:
        expr (Expr): The expression to perform eta reduction on.

    Returns:
        Expr: The expression with eta reduction applied, if applicable. Otherwise, the
        original expression is returned.
    """
    # Check if the expression is a lambda expression
    if isinstance(expr, Lambda):
        # Check if the body of the lambda expression is an application
        if isinstance(expr.body, App):
            # Check if the argument of the application is a variable
            if isinstance(expr.body.arg, Var):
                # Check if the variable is the only free variable in the function
                if expr.body.arg.name == expr.var and not occurs_free(expr.body.func, expr.var):
                    # Perform eta reduction by removing the lambda abstraction
                    print(f"Performing Eta Reduction: {expr}")
                    return expr.body.func
    # If the conditions for eta reduction are not met, return the original expression
    return expr

def occurs_free(expr, var):
    """
    Check if var occurs free in expr.

    This function checks if the given variable occurs free in the given expression.

    Args:
        expr (Expr): The expression to check for the occurrence of the variable.
        var (str): The variable to check for in the expression.

    Returns:
        bool: True if the variable occurs free in the expression, False otherwise.
    """
    # If the expression is a variable, check if it matches the variable to check for
    if isinstance(expr, Var):
        return expr.name == var
    # If the expression is a lambda, check if the lambda variable matches the variable to check for
    # If they match, return False (lambda variable shadows the variable to check for)
    elif isinstance(expr, Lambda):
        if expr.var == var:
            return False
        # Recursively check if the variable occurs free in the body of the lambda
        return occurs_free(expr.body, var)
    # If the expression is an application, recursively check if the variable occurs free in the function and argument
    elif isinstance(expr, App):
        return occurs_free(expr.func, var) or occurs_free(expr.arg, var)
    # If the expression is not one of the above, return False
    return False

def is_normal_form(expr):
    """
    Check if the expression is in normal form.

    An expression is in normal form if it is a variable, or if it is an application
    where the function is not a lambda.

    Args:
        expr (Expr): The expression to check for normal form.

    Returns:
        bool: True if the expression is in normal form, False otherwise.
    """
    # If the expression is a variable, it is in normal form
    if isinstance(expr, Var):
        return True
    # If the expression is a lambda, check if the body is in normal form
    elif isinstance(expr, Lambda):
        return is_normal_form(expr.body)
    # If the expression is an application, check if the function is not a lambda
    # and if the function and argument are in normal form
    elif isinstance(expr, App):
        return not isinstance(expr.func, Lambda) and \
               is_normal_form(expr.func) and \
               is_normal_form(expr.arg)
    # If the expression is not one of the above, it is not in normal form
    return False

def is_recursive_comb(expr):
    """
    Check for self-application patterns like the Y combinator.

    Args:
        expr (Expr): The expression to check for recursive combinator patterns.

    Returns:
        bool: True if the expression matches a recursive combinator pattern, False otherwise.
    """
    # Check if the expression is an application
    if isinstance(expr, App):
        # Check if the function is a lambda
        if isinstance(expr.func, Lambda):
            # Check if the argument is a lambda
            if isinstance(expr.arg, Lambda):
                # Check if the argument's body is an application
                if isinstance(expr.arg.body, App):
                    # Check if the argument is self-applied
                    if expr.arg.body.arg == expr.arg:
                        return True
    return False

def evaluate(expr, depth=0):
    """
    Evaluate the expression by performing reductions until normal form is reached.

    Args:
        expr (Expr): The expression to evaluate.
        depth (int): The depth of the expression in the lambda calculus.

    Returns:
        Expr: The final result of evaluating the expression.
    """
    # Prevent infinite recursion by setting a depth limit
    if depth > DEPTH_LIMIT:
        print("Depth limit reached. This expression cannot be reduced to a normal form.")
        return expr
    
    # Print the expression before evaluation
    print(f"Evaluating: {expr}")
    
    # Check if the expression is a recursive combinator (e.g., Y combinator)
    if is_recursive_comb(expr):
        print("Detected a recursive combinator. This expression may not reduce to a normal form.")
        return expr
    
    # Perform reductions until normal form is reached
    while not is_normal_form(expr):
        # Perform beta reduction
        new_expr = beta_reduce(expr)
        if new_expr != expr:
            expr = new_expr
            continue
        
        # Perform eta reduction
        new_expr = eta_reduce(expr)
        if new_expr != expr:
            expr = new_expr
            continue
        
        # Check if the expression is an application or a lambda
        if isinstance(expr, App):
            # Recursively evaluate the function and argument
            expr.func = evaluate(expr.func, depth + 1)
            expr.arg = evaluate(expr.arg, depth + 1)
        elif isinstance(expr, Lambda):
            # Recursively evaluate the body
            expr.body = evaluate(expr.body, depth + 1)
    
    # Print the final result
    print(f"Final result: {expr}")
    
    return expr
