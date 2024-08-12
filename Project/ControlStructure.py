from ST import standardize,build_tree

# these values are used for naming purposes for lambda and delta nodes
i=1
j=1

# This is same as the struct defined in ST.py
class ASTNode:
    def __init__(self, type, parent=None):
        self.type = type
        self.children = []
        self.parent = parent

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_last_child(self):
        if self.children:
            return self.children.pop()
        else:
            return None

# this method traverses the standardized tree and create lists containing the control structures
# control_stack contains the starting structure
# the other structures are in lambda_stacks
def preorder_traversal(node, control_stack, lambda_stacks):
    global i,j
    if node is None:
        return

# if we come across a lambda node we add an identifier(number) and create a seperate control
# structure for it's children
    if node.type == 'lambda':
        node.type = 'lambda' + str(i)
        i += 1
        control_stack.append(node)
        lambda_stack = []
        preorder_traversal(node, lambda_stack, lambda_stacks)
        lambda_stacks.append(lambda_stack)

# if we have a conditional we replace it with a beta symbol then add two delta nodes for
# the conditions and create seperate structures for those delta nodes. The naming system 
#for both delta and lambda nodes act as a pointer system to their control structures.
    elif node.type == '->':
        node.type = 'β'
        control_stack.append(ASTNode('delta' + str(j)))
        control_stack.append(ASTNode('delta' + str(j+1)))
        control_stack.append(node)
        preorder_traversal(node.children[0], control_stack, lambda_stacks)
        
        lambda_stack = []
        k = j
        j +=2
        lambda_stack.append(ASTNode('delta' + str(k)))
        preorder_traversal(node.children[1], lambda_stack, lambda_stacks)
        lambda_stacks.append(lambda_stack)

        lambda_stack = []
        lambda_stack.append(ASTNode('delta' + str(k+1)))
        preorder_traversal(node.children[2], lambda_stack, lambda_stacks)
        lambda_stacks.append(lambda_stack)
        

# if it a tau node we add the number of children it has to it's name
    elif node.type == 'tau':
        x=0
        for child in node.children:
            x +=1
        node.type = 'tau' + '[' + str(x) + ']'
        control_stack.append(node)
        for child in node.children:
            preorder_traversal(child, control_stack, lambda_stacks)

# we have to remove token types from the names here as they are of no use here on.
    else:
        if node.type.startswith('<ID:'):
            node.type = node.type[4:-1]
        elif node.type.startswith('<INT:'):
            node.type = node.type[5:-1]
        elif node.type.startswith('<STR:'):
            if node.type == "<STR:''>":
                node.type = "''"
            else:
                node.type = node.type[5:-1]
        control_stack.append(node)
        for child in node.children:
            preorder_traversal(child, control_stack, lambda_stacks)

# this function uses the lists created in the previous method and create a dictionary
# containing all the control structures snd return it.
def create_control_structure(ast_list):
    root = standardize(build_tree(ast_list))

    control_stack = []
    lambda_stacks = []

    # Traverse the tree in preorder and create the control stack and lambda stacks
    preorder_traversal(root, control_stack, lambda_stacks)

    env = []
    c_stack = []
    
    # we are removing the tree struct from all the nodes in control_stack. now they
    # are just strings
    for item in control_stack:
        c_stack.append(item.type)

    # we are removing the tree struct from all the nodes in lambda_stacks. now they
    # are just strings. then we will add the control structures to env
    for i, stack in enumerate(lambda_stacks):
        l_stack = []
        for j, item in enumerate(stack):
            if item.type == ',':
                tau = []
                k = j + 1
                for child in item.children:
                    tau.append(stack.pop(k).type)
                l_stack.append(tau)
            else:
                l_stack.append(item.type)
        env.append(l_stack)

    # this list keeps track of all the lambda nodes
    l_stack = []
    i = 1
    for stack in env:
        for stack in env:
            if stack[0].startswith('lambda'):
                if stack[0].endswith(str(i)):
                    l_stack.append(stack)
                    i += 1

    for stack in env:
        if stack[0].startswith('lambda'):
            continue
        else:
            l_stack.append(stack)

    # this is a dictionary with the lambda node set as key and the variable set as value
    # λ1[x] -> lambda_values[λ1] = x
    lambda_values = {}

    # Iterate over each lambda stack
    for stack in l_stack:
        if stack[0].startswith('lambda'):
            lambda_values[stack[0]] = stack[1]  # Store the lambda node and its value

    # Iterate over each lambda stack again to modify the nodes with their values
    for stack in l_stack:
        for i, node in enumerate(stack):
            if isinstance(node, list):
                continue
            else:
                if node in lambda_values:
                    if isinstance(lambda_values[node], list):
                        stack[i] = f"{node}{lambda_values[node]}"
                    else:
                        stack[i] = f"{node}['{lambda_values[node]}']"

    # we can remove lambda and the variable from the control structures now as it is stored 
    # in the previously created dictionary
    for stack in l_stack:
        if stack[0].startswith('lambda'):
            stack.pop(0)
            stack.pop(0)

    # this sets the way we want the lambda node to look like -> λ_1['x']
    for index, value in enumerate(c_stack):
        if value in lambda_values:
            c_stack[index] = f"{value}['{lambda_values[value]}']"

    # now we will create the main dictionary for storing all the control structures
    result_dict = {'δ_0': c_stack.copy()}

    for i, stack in enumerate(l_stack):
        result_dict[f'δ_{i+1}'] = stack.copy()

    # Replace occurrences of specific strings with their corresponding symbols
    # This was done to look good and easy to read
    symbol_map = {'lambda': 'λ_', 'gamma': 'γ', 'delta': 'δ', 'beta': 'β', 'eta': 'η'}
    for key, value in result_dict.items():
        for i, item in enumerate(value):
            for word, symbol in symbol_map.items():
                if word in item:
                    result_dict[key][i] = item.replace(word, symbol)

    # In here we are pairing the delta nodes in case of conditionals
    for key, value in result_dict.items():
        for i in value:
            if i == 'β':
                for j in value:
                    if j.startswith('δ'):
                        for key1, value1 in result_dict.items():
                            if value1 != value:
                                if j in value1:
                                    index = value.index(j)
                                    value[index] = key1

    # if there are additional  redundant nodes remove them
    for key, value in result_dict.items():
        for i in value:
            if i.startswith('δ'):
                if i.startswith('δ_'):
                    continue
                else:
                    value.remove(i)


    return result_dict

# this function prints the dictionary containing the control structures
def print_dict(result_dict):
    for key, value in result_dict.items():
        print(key, end=' : ')
        for i in value:
            print(i, end='  ')
        print()

if __name__ == "__main__":

    # Example usage
    ast_list = ['let', '.fcn_form', '..<ID:Sum>', '..<ID:A>', '..where', '...gamma', '....<ID:Psum>', '....tau', 
                '.....<ID:A>', '.....gamma', '......<ID:Order>', '......<ID:A>', '...rec', '....fcn_form', '.....<ID:Psum>', 
                '.....,', '......<ID:T>', '......<ID:N>', '.....->', '......eq', '.......<ID:N>', '.......<INT:0>', '......<INT:0>', 
                '......+', '.......gamma', '........<ID:Psum>', '........tau', '.........<ID:T>', '.........-', '..........<ID:N>', 
                '..........<INT:1>', '.......gamma', '........<ID:T>', '........<ID:N>', '.gamma', '..<ID:Print>', '..gamma', 
                '...<ID:Sum>', '...tau', '....<INT:1>', '....<INT:2>', '....<INT:3>', '....<INT:4>', '....<INT:5>']
    

    result_dict = create_control_structure(ast_list)
    print_dict(result_dict)
