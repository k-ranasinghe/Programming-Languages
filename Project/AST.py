def Build_Preorder_Tree(AST):
    # Create a copy of the AST and reverse it to obtain a postorder traversal
    Postorder_AST = AST.copy()
    Postorder_AST.reverse()

    # Initialize the preorder AST with a list containing None
    Preorder_AST = [None]
    i = 0
    depth = 0
    # Traverse the postorder AST to build the preorder AST
    for node in Postorder_AST:
        num_child = node[1]
        node_val = node[0]

        # Add the node value with appropriate indentation to the preorder AST
        Preorder_AST[i] = "." * depth + node_val
        depth += 1
        # Insert None values for the children of the current node
        for j in range(num_child):
            i += 1
            Preorder_AST.insert(i, None)

        # Adjust depth and index if the current node has no children
        if num_child == 0:
            depth -= 1
            i -= 1
            while Preorder_AST[i] != None and i > -1:
                depth -= 1
                i -= 1
    return Preorder_AST


# This function prints the AST using the parse tree
def Print_AST(Preorder_AST):
    for node in Preorder_AST:
        print(node)


if __name__ == "__main__":
    
    Parse_tree = [('<ID:Sum>', 0), ('<ID:A>', 0), ('<ID:Psum>', 0), ('<ID:A>', 0), ('<ID:Order>', 0), 
           ('<ID:A>', 0), ('gamma', 2), ('tau', 2), ('gamma', 2), ('<ID:Psum>', 0), ('<ID:T>', 0), 
           ('<ID:N>', 0), (',', 2), ('<ID:N>', 0), ('<INT:0>', 0), ('eq', 2), ('<INT:0>', 0), 
           ('<ID:Psum>', 0), ('<ID:T>', 0), ('<ID:N>', 0), ('<INT:1>', 0), ('-', 2), ('tau', 2), 
           ('gamma', 2), ('<ID:T>', 0), ('<ID:N>', 0), ('gamma', 2), ('+', 2), ('->', 3), ('fcn_form', 3), 
           ('rec', 1), ('where', 2), ('fcn_form', 3), ('<ID:Print>', 0), ('<ID:Sum>', 0), ('<INT:1>', 0), 
           ('<INT:2>', 0), ('<INT:3>', 0), ('<INT:4>', 0), ('<INT:5>', 0), ('tau', 5), ('gamma', 2), ('gamma', 2), ('let', 2)]
    
    Preorder_AST = Build_Preorder_Tree(Parse_tree)
    Print_AST(Preorder_AST)
