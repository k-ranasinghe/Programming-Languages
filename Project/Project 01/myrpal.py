import sys

# Importing lex function from scanner.py
from scanner import lex

# Importing parse function from parser1.py
# Had to name this file parser1.py because there exists a system file named parser.py 
from parser1 import parse

# Importing Print_AST function from AST.py
from AST import Print_AST

def main():
    if len(sys.argv) not in [2,3]:
        print("Usage: python scanner.py <filename> [-ast]")
        return

    # Read filename from command-line argument
    filename = sys.argv[1]

    # Check if the '-ast' switch is provided
    if len(sys.argv) == 3 and sys.argv[2] == "-ast":
        # Read tokens from the file using the lex function
        tokens = lex(filename)

        # Call the parse function to generate the Parse tree
        Parse_tree = parse(tokens)

        # Print the AST
        Print_AST(Parse_tree)
    else:
        # This section is yet to be implemented
        print("This is yet to be implemented. Please provide the '-ast' switch to print the AST.")


if __name__ == "__main__":
    main()
