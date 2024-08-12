import sys
import re

# Token types
IDENTIFIER = '<IDENTIFIER>'
INTEGER = '<INTEGER>'
OPERATOR = '<OPERATOR>'
STRING = '<STRING>'
PUNCTUATION = ['(', ')', ';', ',']
DELETE = '<DELETE>'

# Special keywords based the grammer provided
SPECIAL = ['let', 'in', 'fn', 'where', 'aug', 'or', 
           'and', 'not', 'eq', 'ne', 'rec', 'within', 
           'true', 'false', 'nil', 'dummy', 'gr', 'ge', 'ls', 'le']

# Regular expressions for lexicon rules
identifier_pattern = r'[a-zA-Z_][a-zA-Z0-9_]*'
integer_pattern = r'\d+'
operator_pattern = r'[+\-*<>&.@/:=˜|$\#!%^_[\]{}“?]'
string_pattern = r"'(?:\\[tn\\';,() ]|\\['“?]|[a-zA-Z0-9_+\-*<>&.@/:=˜|$\#!%^_[\]{}‘”])+'"
spaces_pattern = r'[ \t]+'
comment_pattern = r'//.*'
newline_pattern = r'\n'

# Special patterns given in the grammer
special_pattern = r'->'
special_pattern1 = r'\*\*'         

# Tokenization function
def tokenize(program):
    tokens = []
    pos = 0

    while pos < len(program):
        match = None

        # Matching patterns
        for pattern, token_type in [
            (identifier_pattern, IDENTIFIER),
            (integer_pattern, INTEGER),
            (comment_pattern, DELETE),          # comment is given higher precedence than Operator for it to be deleted
            (special_pattern, OPERATOR),        # Precendence of special_pattern and special_pattern1 is higher than operator_pattern
            (special_pattern1, OPERATOR),       # Same as above is done here. Otherwise the two characters will be read as 2 tokens
            (operator_pattern, OPERATOR),
            (string_pattern, STRING),
            (spaces_pattern, DELETE),
            (newline_pattern, DELETE),   
        ]:
            regex = re.compile(pattern)
            match = regex.match(program, pos)
            if match:
                value = match.group(0)
                if token_type != DELETE:
                    if value in SPECIAL:                # Checking if the token is a special keyword before other types
                        tokens.append((value, value))
                    elif token_type == OPERATOR:        # Checking if the token is an operator as they are appended in a different way
                        tokens.append((value, value))
                    else:
                        tokens.append((token_type, value))
                break
        # Characters which were not handled above wiil be taken care of here. Specificaly, punctuations and newlines
        if not match:
            char = program[pos]
            if char in PUNCTUATION:
                tokens.append((char, char))
                pos += 1
            elif char == '\n':
                tokens.append(('NEWLINE', '\n'))
                pos += 1
            elif char+program[pos+1] == "''":
                tokens.append((STRING, "''"))
                pos += 2
            else:
                raise SyntaxError(f"Invalid character '{char}' at position {pos}")
        else:
            pos = match.end(0)

    return tokens

# Main function reads the input file and tokenize and return the token list
def lex(filename):
    try:
        with open(filename, 'r') as file:
            program = file.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return []

    # Tokenize the program
    tokens = tokenize(program)

    return tokens
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scanner.py <filename>")

    # Read filename from command-line argument
    filename = sys.argv[1]

    # Call lex function with filename
    tokens = lex(filename)

    # Print the tokens
    for token in tokens:
        print(token)
