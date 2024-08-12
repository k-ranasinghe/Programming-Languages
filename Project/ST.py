# Previously we were using a list to store the AST. Now we will create a tree struct for ease of use
# add_child method allows the nodes to keep track of their children as well as their parents
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
    root = ASTNode(ast_list[0]) 
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

# using this method we can print the tree in the required format
def print_tree(root, indent=0):
    print("." * indent + root.type)
    for child in root.children:
        print_tree(child, indent + 1)

# this method recursivelt standardizes the tree and returns the root of the tree
def standardize(node):
    # Standardize the children first
    if node.children:
        for child_node in node.children:
            standardize(child_node)

    # All children standardized. Now standardize this node
    if node.type == 'let':
        #       let              gamma
        #     /     \           /     \
        #     =      P   ->   lambda   E
        #   /   \             /    \
        #  X     E           X      P
        equal_node = node.children[0]
        e = equal_node.children[1]
        equal_node.children[1] = node.children[1]
        node.children[1] = e
        equal_node.type = 'lambda'
        node.type = 'gamma'

    elif node.type == 'where':
        #       where              gamma
        #       /   \             /     \
        #      P      =    ->   lambda   E
        #           /   \       /   \
        #          X     E     X     P
        equal_node = node.children[1]
        node.children[1] = node.children[0]
        node.children[0] = equal_node
        e = equal_node.children[1]
        equal_node.children[1] = node.children[1]
        node.children[1] = e
        equal_node.type = 'lambda'
        node.type = 'gamma'

    elif node.type == 'function_form':
        #       fcn_form                  =
        #       /   |   \               /   \
        #      P    V+   E     ->      P    +lambda
        #                                    /     \
        #                                    V     .E
        equal_node = ASTNode('=')
        equal_node.children.append(node.children[0])
        equal_node.children.append(ASTNode('lambda'))
        node.children.pop(0) 
        last_child = node.remove_last_child()
        curr_node = equal_node.children[1]
        while node.children:
            curr_node.add_child(node.children[0])
            node.children.pop(0)
            if node.children:
                curr_node.add_child(ASTNode('lambda'))
            else:
                curr_node.add_child(last_child)
            curr_node = curr_node.children[1]
        node.type = equal_node.type
        node.children = equal_node.children

    elif node.type == 'within':
        #           within                  =
        #          /      \              /     \
        #         =        =     ->     X2     gamma
        #       /   \    /   \                 /    \
        #      X1   E1  X2   E2              lambda  E1
        #                                    /    \
        #                                   X1    E2
        e = node.children[0].children[1]
        node.children[0].children[1] = node.children[1].children[1]
        equal_node = ASTNode('=')
        equal_node.add_child(node.children[1].children[0])
        equal_node.add_child(ASTNode('gamma'))
        equal_node.children[1].add_child(node.children[0])
        equal_node.children[1].add_child(e)
        equal_node.children[1].children[0].type = 'lambda'
        node.type = equal_node.type
        node.children = equal_node.children

    elif node.type == '@':
        #         @               gamma
        #       / | \     ->      /   \
        #      E1 N E2         gamma   E2
        #                      /   \
        #                     N     E1
        gamma_node = ASTNode('gamma')
        gamma_node.add_child(ASTNode('gamma'))
        gamma_node.add_child(node.children[2])
        gamma_node.children[0].add_child(node.children[1])
        gamma_node.children[0].add_child(node.children[0])
        node.type = gamma_node.type
        node.children = gamma_node.children

    elif node.type == 'lambda':
        #     lambda       ++lambda
        #      /   \   ->   /    \
        #     V++   E      V     .E
        lambda_node = ASTNode('lambda')
        last_child = node.remove_last_child()
        curr_node = lambda_node
        while node.children:
            curr_node.add_child(node.children[0])
            node.children.pop(0)
            if node.children:
                curr_node.add_child(ASTNode('lambda'))
            else:
                curr_node.add_child(last_child)
            curr_node = curr_node.children[1]
        node.type = lambda_node.type
        node.children = lambda_node.children

    elif node.type == 'and':
        #            and                =
        #             |               /   \
        #            =++      ->      ,   tau
        #           /   \             |    |
        #          X     E           X++  E++
        equal_node = ASTNode('=')
        equal_node.add_child(ASTNode(','))
        equal_node.add_child(ASTNode('tau'))
        for child in node.children:
            equal_node.children[0].add_child(child.children[0])
            equal_node.children[1].add_child(child.children[1])
        node.type = equal_node.type
        node.children = equal_node.children

    elif node.type == 'rec':
        #        rec                 =
        #         |                /   \
        #         =      ->       X    gamma
        #       /   \                  /   \
        #      X     E              Ystar  lambda
        #                                  /     \
        #                                 X       E
        equal_node = ASTNode('=')
        equal_node.add_child(node.children[0].children[0])
        equal_node.add_child(ASTNode('gamma'))
        equal_node.children[1].add_child(ASTNode('Ystar'))
        equal_node.children[1].add_child(node.children[0])
        equal_node.children[1].children[1].type = 'lambda'
        node.type = equal_node.type
        node.children = equal_node.children

    return node


if __name__ == "__main__":

    ast_list = ['and', '.=', '..a', '..w', '.=', '..b', '..x', '.=', '..c', '..y', '.=', '..d', '..z']
    print_tree(standardize(build_tree(ast_list)))

    # Example usage
    # ast_list = ['let', '.fcn_form', '..<ID:Sum>', '..<ID:A>', '..where', '...gamma', '....<ID:Psum>', '....tau', 
    #             '.....<ID:A>', '.....gamma', '......<ID:Order>', '......<ID:A>', '...rec', '....fcn_form', '.....<ID:Psum>', 
    #             '.....,', '......<ID:T>', '......<ID:N>', '.....->', '......eq', '.......<ID:N>', '.......<INT:0>', '......<INT:0>', 
    #             '......+', '.......gamma', '........<ID:Psum>', '........tau', '.........<ID:T>', '.........-', '..........<ID:N>', 
    #             '..........<INT:1>', '.......gamma', '........<ID:T>', '........<ID:N>', '.gamma', '..<ID:Print>', '..gamma', 
    #             '...<ID:Sum>', '...tau', '....<INT:1>', '....<INT:2>', '....<INT:3>', '....<INT:4>', '....<INT:5>']

    # print_tree(standardize(build_tree(ast_list)))


