import sys

# Importing lex function from scanner.py
from scanner import lex

# Importing parse function from parser1.py
# Had to name this file parser1.py because there exists a system file named parser.py 
from parser1 import parse

# Importing Print_AST function from AST.py
from AST import Print_AST, Build_Preorder_Tree

# Importing standardisation function from ST.py
from ST import standardize, build_tree, print_tree

# Importing create_control_structure function from ControlStructure.py
from ControlStructure import create_control_structure, print_dict

# Importing create_control_structure function from ControlStructure.py
from CSEM import evaluate

def main():
    try:
        if len(sys.argv) not in [2,3]:
            print("Usage: python scanner.py <filename> [-ast]")
            return

        # Read filename from command-line argument
        filename = sys.argv[1]

        # Read tokens from the file using the lex function
        tokens = lex(filename)

        # Call the parse function to generate the Parse tree
        Parse_tree = parse(tokens)

        # Next we will build the AST using the parse tree
        AST = Build_Preorder_Tree(Parse_tree)

        # We will standardize the generated AST using this function
        ST = standardize(build_tree(AST))

        # This will generate the control structures for CSE machine evaluation
        CS = create_control_structure(AST)
        control = []
        stack = []
        control.append('Ҽ0')
        stack.append('Ҽ0')
        for val in CS['δ_0']:
            control.append(val)

        env = {}


        if len(sys.argv) == 3:
            # if -ast switch is given we will print the AST
            if sys.argv[2] == "-ast":
                Print_AST(AST)

            # if -st switch is given we will print the standardized AST
            if sys.argv[2] == "-st":
                print_tree(ST)

            # if -cs switch is given we will print the control structures for the program
            if sys.argv[2] == "-cs":
                print_dict(CS)

            # if -cse switch is given we will print the CSE machine evaluation of the control structures
            if sys.argv[2] == "-cse":
                evaluate(control,stack, CS, env)

        # if no switch is given we will just output the result of the program
        else:
            evaluate(control,stack, CS, env, False)
    except:
        print()


if __name__ == "__main__":
    main()
