import re

# Token definitions using regular expressions
TOKEN_REGEX = {
    'LAMBDA': r'\#',
    'DOT': r'\.',
    'VAR': r'[a-zA-Z]',
    'LPAREN': r'\(',
    'RPAREN': r'\)'
}

def lex(input_string):
    """
    Lexical analysis: convert input string into a list of tokens.

    Args:
        input_string (str): The input string to be lexed.

    Returns:
        list: A list of tuples containing token types and values.
    """
    # List to store tokens
    tokens = []
    # Current position in the input string
    position = 0

    # Loop through the input string
    while position < len(input_string):
        # Initialize match variable
        match = None

        # Try to match the current input string with each token definition
        for token_type, pattern in TOKEN_REGEX.items():
            regex = re.compile(pattern)
            match = regex.match(input_string, position)
            if match:
                # If a match is found, extract the value and add it to the tokens list
                value = match.group(0)
                tokens.append((token_type, value))
                # Update the position to the end of the matched string
                position = match.end()
                break

        # If no match is found, check if the character is whitespace
        if not match:
            if input_string[position].isspace():
                # If it is whitespace, move the position forward by 1 character
                position += 1
            else:
                # If it is not whitespace, raise an error
                raise ValueError(f"Unexpected character: {input_string[position]}")

    # Return the list of tokens
    return tokens
