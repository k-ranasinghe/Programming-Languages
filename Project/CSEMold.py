from ST import standardize

lambda_symbol = '\u03BB'
gamma_symbol = '\u03B3'
delta_symbol = '\u03B4'
beta_symbol = '\u03B2'
eta_symbol = '\u03B7'

i = 0

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

def build_tree(ast_list):
    root = ASTNode(ast_list[0])  # Assuming the first element is the root node
    stack = [root]  # Stack to keep track of parent nodes

    for item in ast_list[1:]:
        level = item.count('.')
        node_type = item[level:]

        node = ASTNode(node_type)

        # Pop nodes from stack until the proper parent is found
        while level <= len(stack) - 1:
            stack.pop()

        parent = stack[-1]
        parent.add_child(node)  # Use the add_child method to set the parent of the node
        stack.append(node)

    return root

def print_tree(root, indent=0):
    print("." * indent + root.type)
    for child in root.children:
        print_tree(child, indent + 1)

def preorder_traversal(node, control_stack, lambda_stacks):
    global i
    if node is None:
        return

    if node.type == 'lambda':
        node.type = 'lambda' + str(i)
        i += 1
        control_stack.append(node)
        lambda_stack = []
        preorder_traversal(node, lambda_stack, lambda_stacks)
        lambda_stacks.append(lambda_stack)

    elif node.type == '->':
        control_stack.append(node)
        preorder_traversal(node.children[0], control_stack, lambda_stacks)
        lambda_stack = []
        preorder_traversal(node.children[1], lambda_stack, lambda_stacks)
        lambda_stacks.append(lambda_stack)
        lambda_stack = []
        preorder_traversal(node.children[2], lambda_stack, lambda_stacks)
        lambda_stacks.append(lambda_stack)

    else:
        if node.type.startswith('<ID:'):
            node.type = node.type[4:-1]
        elif node.type.startswith('<INT:'):
            node.type = node.type[5:-1]
        # Add the current node to the control stack
        control_stack.append(node)
        for child in node.children:
            preorder_traversal(child, control_stack, lambda_stacks)


def operate(result_stack, control_stack, lambda_stacks):
    # Traverse the control stack
    for item in control_stack:
        if item.type == 'gamma':
            eval = result_stack.pop()
            if eval.type.startswith('lambda'):
                # Find the corresponding lambda stack
                lambda_stack = None
                for stack in lambda_stacks:
                    if stack[-1].type == eval.type:
                        lambda_stack = stack
                        break

                if lambda_stack:
                    # Get the second value from the lambda stack
                    val = lambda_stack[-2]
                    if val.type == ',':
                        i = -2
                        for child in val.children:
                            # print(child.type, 'afgajf')
                            # Search for the second value in the lambda stack and replace it with the top value from the result stack
                            # for node in lambda_stack:
                            #     if node.type == child.type:
                            #         print(node.type)
                            #         node.type = result_stack[-1].children[0].type
                            #         node.children = result_stack[-1].children[0].children
                            #         print(node.type)

                            for stack in lambda_stacks:
                                for node in stack:
                                    # print("Current Node Type:", node.type)
                                    # print("Value Type:", child.type)
                                    if node.type == child.type:
                                        print(stack[-1].type, node.type)
                                        node.type = result_stack[-1].children[0].type
                                        node.children = result_stack[-1].children[0].children
                                        print(node.type)
                            
                            result_stack[-1].children = result_stack[-1].children[1:]
                            i -= 1
                        lambda_stack = lambda_stack[:i]
                    
                    else:
                        lambda_stack = lambda_stack[:-2]
                        val = val.type
                        # Search for the second value in the lambda stack and replace it with the top value from the result stack
                        # for node in lambda_stack:
                        #     if node.type == val.type:
                        #         print(node.type)
                        #         node.type = result_stack[-1].type
                        #         node.children = result_stack[-1].children
                        #         print(node.type)

                        for stack in lambda_stacks:
                            # print(stack[-1].type)
                            # for node in stack:
                            #     print(node.type, end=',')
                            # print()
                            for node in stack[:-1]:
                                # print("Current Node Type:", node.type)
                                # print("Value Type:", val)
                                if node.type == val:
                                    print(stack[-1].type ,node.type)
                                    node.type = result_stack[-1].type
                                    node.children = result_stack[-1].children
                                    print(node.type)
                        # for item in lambda_stack:
                        #     print(item.type, end=',')
                        # print()
                    result_stack.pop()
                    operate(result_stack, lambda_stack, lambda_stacks)

            elif eval.type == 'Ystar':
                eta_node = ASTNode('eta')
                rec = result_stack.pop()
                lambda_stack = None
                for stack in lambda_stacks:
                    if stack[-1].type == rec.type:
                        lambda_stack = stack
                        break
                rec.children.clear()
                for item in lambda_stack:
                    rec.children.append(item) 
                eta_node.children.append(rec)
                result_stack.append(eta_node)  
            
            elif eval.type == 'Order':
                if result_stack[-1].type == 'tup':
                    tup = result_stack.pop()
                    result_stack.append(tup.children[-1])

            

        # CSE Optimization Rule 6 (binops)
        elif item.type == '+':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                result = int(operand1) + int(operand2)
                result_stack.append(ASTNode(str(result)))
        elif item.type == '-':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                result = int(operand1) - int(operand2)
                result_stack.append(ASTNode(str(result)))
        elif item.type == '*':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                result = int(operand1) * int(operand2)
                result_stack.append(ASTNode(str(result)))
        elif item.type == '/':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                result = int(operand1) / int(operand2)
                result_stack.append(ASTNode(str(result)))
        elif item.type == '**':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                result = int(operand1) ** int(operand2)
                result_stack.append(ASTNode(str(result)))
        elif item.type == 'gr':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                if int(operand1) > int(operand2):
                    result_stack.append(ASTNode('true'))
                else:
                    result_stack.append(ASTNode('false'))
        elif item.type == 'ge':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                if int(operand1) >= int(operand2):
                    result_stack.append(ASTNode('true'))
                else:
                    result_stack.append(ASTNode('false'))
        elif item.type == 'ls':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                if int(operand1) < int(operand2):
                    result_stack.append(ASTNode('true'))
                else:
                    result_stack.append(ASTNode('false'))
        elif item.type == 'le':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                if int(operand1) <= int(operand2):
                    result_stack.append(ASTNode('true'))
                else:
                    result_stack.append(ASTNode('false'))
        elif item.type == 'eq':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                if int(operand1) == int(operand2):
                    result_stack.append(ASTNode('true'))
                else:
                    result_stack.append(ASTNode('false'))
        elif item.type == 'ne':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                if int(operand1) != int(operand2):
                    result_stack.append(ASTNode('true'))
                else:
                    result_stack.append(ASTNode('false'))
        elif item.type == 'or':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                if operand1 == 'true' or operand2 == 'true':
                    result_stack.append(ASTNode('true'))
                else:
                    result_stack.append(ASTNode('false'))
        elif item.type == '&':
                operand1 = result_stack.pop().type
                operand2 = result_stack.pop().type
                if operand1 == 'true' and operand2 == 'true':
                    result_stack.append(ASTNode('true'))
                else:
                    result_stack.append(ASTNode('false'))

        # CSE Optimization Rule 7 (unops)
        elif item.type == 'not':
                operand = result_stack.pop().type
                if operand == 'true':
                    result_stack.append(ASTNode('false'))
                else:
                    result_stack.append(ASTNode('true'))
        elif item.type == 'neg':
                operand = result_stack.pop().type
                result = -1 * int(operand)
                result_stack.append(ASTNode(str(result)))

        elif item.type == '->':
                operand = result_stack.pop().type
                if operand == 'true':
                    val = item.children[1].type
                    result_stack.append(item.children[2])
                    break
                    
                else:
                    val = item.children[2].type
                    
                lambda_stack = []
                for stack in lambda_stacks:
                    for node in stack:
                        if node.type == val:
                            lambda_stack = stack
                operate(result_stack, lambda_stack, lambda_stacks)

        elif item.type == 'tau':
                tup_node = ASTNode('tup')
                tau = []
                for child in item.children:
                    tup_node.add_child(result_stack.pop())
                result_stack.append(tup_node)

        elif item.type == 'eta':
            result_stack.append(item.children[0])
            for item in result_stack:
                print(item.type, end=',')
            print()
            val = result_stack.pop()
            result_stack.append(val.children[0])

        else:
                result_stack.append(item)
                for item in result_stack:
                    print(item.type, end=',')
                print()

def flatten_list(nested_list):
    """Flatten a nested list."""
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened

def create_dict(control_stack, lambda_stacks):
    result_dict = {'control_stack': control_stack.copy()}

    for i, stack in enumerate(lambda_stacks):
        result_dict[f'lambda_{i}'] = stack.copy()

    # Replace occurrences of specific strings with their corresponding symbols
    symbol_map = {'lambda': 'λ', 'gamma': 'γ', 'delta': 'δ', 'beta': 'β', 'eta': 'η'}
    for key, value in result_dict.items():
        for i, item in enumerate(value):
            for word, symbol in symbol_map.items():
                if word in item:
                    result_dict[key][i] = item.replace(word, symbol)

    return result_dict



if __name__ == "__main__":

    # Example usage
    ast_list = ['let', '.fcn_form', '..<ID:Sum>', '..<ID:A>', '..where', '...gamma', '....<ID:Psum>', '....tau', 
                '.....<ID:A>', '.....gamma', '......<ID:Order>', '......<ID:A>', '...rec', '....fcn_form', '.....<ID:Psum>', 
                '.....,', '......<ID:T>', '......<ID:N>', '.....->', '......eq', '.......<ID:N>', '.......<INT:0>', '......<INT:0>', 
                '......+', '.......gamma', '........<ID:Psum>', '........tau', '.........<ID:T>', '.........-', '..........<ID:N>', 
                '..........<INT:1>', '.......gamma', '........<ID:T>', '........<ID:N>', '.gamma', '..<ID:Print>', '..gamma', 
                '...<ID:Sum>', '...tau', '....<INT:1>', '....<INT:2>', '....<INT:3>', '....<INT:4>', '....<INT:5>']

    # examples given in lecture 12
    # ast_list = ['gamma', '.gamma', '..*', '..gamma', '...lambda', '....x', '....gamma', '.....gamma', '......-', '......x', '.....1', '...4', '.2']
    # ast_list = ['gamma', '.gamma', '..lambda', '...x', '...lambda', '....w', '....gamma', '.....gamma', '......+', '......x', '.....w', '..5', '.6']
    # ast_list = ['gamma', '.lambda', '..x', '..gamma', '...gamma', '....+', '....1', '...gamma', '....lambda', '.....w', '.....gamma', '......neg', '......w',
    #             '....x', '.gamma', '..lambda', '...z', '...gamma', '....gamma', '.....*', '.....2', '....z', '..7']
    # ast_list = ['gamma', '.lambda', '..,', '...x', '...y', '..gamma', '...gamma', '....+', '....x', '...y', '.tau', '..5', '..6']

    root = standardize(build_tree(ast_list))

    # Create the control stack and lambda stacks
    control_stack = []
    lambda_stacks = []

    # Traverse the tree in preorder and create the control stack and lambda stacks
    preorder_traversal(root, control_stack, lambda_stacks)

    env = []
    c_stack = []
    
    for item in control_stack:
        c_stack.append(item.type)
    # env.append(c_stack)

    for i, stack in enumerate(lambda_stacks):
        l_stack = []
        for item in stack:
            l_stack.append(item.type)
        env.append(l_stack)

    for i in env:
        print(i)

    # Example usage
    result_dict = create_dict(c_stack, env)
    print(result_dict)
    print(lambda_symbol,gamma_symbol,delta_symbol,beta_symbol,eta_symbol)
    # Reverse control_stack
    control_stack.reverse()

    # Reverse the lists inside lambda_stacks
    for stack in lambda_stacks:
        stack.reverse()

    result_stack = []
    # operate(result_stack, control_stack, lambda_stacks)
    # print("Result Stack:")
    # for item in result_stack:
    #     print(item.type)