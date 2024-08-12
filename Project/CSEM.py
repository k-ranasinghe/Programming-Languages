import shutil

from ControlStructure import create_control_structure, print_dict

global count
# this will evaluate the control structures to get the result.
# control and stack is defined outside of this function. they are the lists 
# for evaluating in CSE machine as mentioned in the notes.
# result_dict contains the control structures.
# out is a parameter used to output the evaluation of the CSE machine. if it is true
# the evaluation will be outputed. else only the result will be outputed
def evaluate(control, stack, result_dict, env, out=True):
    # these definitions are used to handle CSE rules 6 and 7
    unops = ['not', 'neg']
    binops = ['+', '-', '*', '/', '**', 'gr', 'ge', 'ls', 'le', 'eq', 'ne', 'or', '&']

    # if out is true we will be outputing the evaluation process
    if out:
        # Get the width of the terminal window
        terminal_width, _ = shutil.get_terminal_size()

        # Define the content for the left and right sides
        left_content = "CONTROL"
        right_content = "STACK"

        # Calculate the length of the space between the left and right content
        space_length = terminal_width - len(left_content) - len(right_content)

        # Combine the left and right content with the appropriate spacing
        formatted_string = left_content + ' ' * space_length + right_content

        print(formatted_string)
        print('-' * terminal_width)

    count = 1
    # we will be evaluating the control until it becomes empty
    while control:
        # RULE 1 - get the top element from the control
        val = control.pop()
        rule = ''
        

        # RULE 3 - handling stack incase of a gamma node
        if val == 'γ':  
            rule = '3'
            # we take the top value from the stack for evaluation    
            rator = stack.pop(0)
            # RULE 10 - handling lists in the stack
            # if rator is a list we need to pop the top value(n) form stack again
            # and get the nth instance from the rator list and add to the stack
            if isinstance(rator, list):
                rule = '10'
                i = int(stack.pop(0))
                stack.insert(0,rator[i-1])
                continue

            # RULE 4 - handling lambda node in the top of stack
            if rator.startswith('λ_'):
                rule = '4'
                num = rator[2]
                var = rator[5:-2]
                rep = stack.pop(0)
                var_list = []
                # this is the case when the lambda node carries multiple variables
                if ',' in var:
                    if var.startswith('['):
                        var = var[2:-2]
                    var_list = var.split("', '")
                    for i in range(0,len(var_list)):
                        env[var_list[i]] = rep[i]
                else:
                    env[var] = rep
                    for i in range(0,len(control)):
                        if control[i] == var:
                            control[i] = rep

                # this can be used to print the environment transitions
                # for i in stack:
                #     if i.startswith('Ҽ'):
                #         num1 = i[1]
                #         en = 'Ҽ{}=[{}/{}]Ҽ{}'.format(num, rep, var,num1)
                #         print(en)
                #         break

                # this represents the change in environment
                control.append('Ҽ' + str(count))
                stack.insert(0, 'Ҽ' + str(count))
                for item in result_dict['δ_' + num]:
                    control.append(item)
                count = count + 1
                

            # We will handle the built in functions of RPAL here
            # RULE 3 - handling stack incase of a gamma node
            elif rator == 'Order':
                val = stack.pop(0)
                if isinstance(val, list):
                    num = len(val)
                    stack.insert(0,str(num))

            elif rator == 'Print':
                val = stack.pop(0)
                # the output format is not the same as what we have in the control structures.
                # they are hanlded here
                formatted_list = str(val).replace('[', '(').replace(']', ')').replace("'", '').replace('"', '')
                print(formatted_list)

            elif rator == 'Isinteger':
                val = stack.pop(0)
                try:
                    int(val)
                    stack.insert(0,'true')
                except ValueError:
                    stack.insert(0,'false')

            elif rator == 'Istruthvalue':
                val = stack.pop(0)
                if val in ('true', 'false'):
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')

            elif rator == 'Isstring':
                val = stack.pop(0)
                try:
                    int(val)
                    stack.insert(0,'false')
                except ValueError:
                    stack.insert(0,'true')

            elif rator == 'Istuple':
                val = stack.pop(0)
                if isinstance(val, list):
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')

            elif rator == 'Isfunction':
                val = stack.pop(0)
                if var.startswith('λ_'):
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')

            elif rator == 'Isdummy':
                val = stack.pop(0)
                if val == 'dummy':
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')

            # The definitions Stem and Stern are different in different sources.
            # we applied the same functionality shown in the RPAL interpreter provided
            # Stern removes the first element from a string
            elif rator == 'Stern':
                val = stack.pop(0)
                val = val[2:]
                val = "'" + val
                stack.insert(0,val)

            # Stem returns the first element of a string
            elif rator == 'Stem':
                val = stack.pop(0)
                s = val[:2] + "'"
                stack.insert(0,s)

            # Conc concatenates two strings
            elif rator == 'Conc':
                val1 = stack.pop(0)
                val2 = stack.pop(0)
                control.pop()
                res = val1[:-1] + val2[1:]
                stack.insert(0,res)

            # RULE 12 - defining the functionality of Ystar node
            elif rator == 'Ystar':
                rule = '12'
                var = stack.pop(0)
                eta = 'η' + var[1:]
                stack.insert(0,eta)

            # RULE 13 - defining the functionality of eta node 
            elif rator.startswith('η'):
                rule = '13'
                stack.insert(0,rator)
                lamda = 'λ' + rator[1:]
                stack.insert(0,lamda)
                control.append('γ')
                control.append('γ')

        # RULE 1 - when moving a variable from control to stack change value if
        #          if we have already assigned a value to it.
        elif val in env:
            rule = '1'
            stack.insert(0,env[val])
            if isinstance(env[val], list):
                i = env[val][0]       
            else:
                for i in range(0,len(control)):
                    if control[i] == val:
                        control[i] = env[val]

        # RULE 6 - handling binops
        elif val in binops:
            rule = '6'
            rand1 = stack.pop(0)
            rand2 = stack.pop(0)
            
            if val == 'or':
                if rand1 == 'true' or rand2 == 'true':
                    stack.insert(0,'true')
                elif rand1 and rand2 not in ('true', 'false'):
                    error = 'Error: Cannot apply bolean operations on given value:  ({}, {})'.format(rand1, rand2)
                    print(error)
                    raise ValueError
                else:
                    stack.insert(0,'false')
            elif val == '&':
                if rand1 == 'true' and rand2 == 'true':
                    stack.insert(0,'true')
                elif rand1 and rand2 not in ('true', 'false'):
                    error = 'Error: Cannot apply bolean operations on given value:  ({}, {})'.format(rand1, rand2)
                    print(error)
                    raise ValueError
                else:
                    stack.insert(0,'false')
            elif val == 'eq':
                if rand1 == rand2:
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')
            elif val == 'ne':
                if rand1 != rand2:
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')
            elif val not in ('or', '&', 'eq', 'ne'):
                try:
                    rand1 = int(rand1)
                    rand2 = int(rand2)
                except ValueError:
                    error = 'Error: Cannot convert string to int:  ({}, {})'.format(rand1, rand2)
                    print(error)
                    raise ValueError
            if val == '+':
                eval = rand1 + rand2
                stack.insert(0,str(eval))
            elif val == '-':
                eval = rand1 - rand2
                stack.insert(0,str(eval))
            elif val == '*':
                eval = rand1 * rand2
                stack.insert(0,str(eval))
            elif val == '/':
                eval = rand1 / rand2
                stack.insert(0,str(eval))
            elif val == '**':
                eval = rand1 ** rand2
                stack.insert(0,str(eval))
            elif val == 'gr':
                if rand1 > rand2:
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')
            elif val == 'ge':
                if rand1 >= rand2:
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')
            elif val == 'ls':
                if rand1 < rand2:
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')
            elif val == 'le':
                if rand1 <= rand2:
                    stack.insert(0,'true')
                else:
                    stack.insert(0,'false')

        # RULE 7 - handling unops
        elif val in unops:
            rule = '7'
            if val == 'not':
                rand = stack.pop(0)
                if rand == 'true':
                    stack.insert(0,'false')
                else:
                    stack.insert(0,'true')
            if val == 'neg':
                rand = stack.pop(0)
                result = -1 * int(rand)
                stack.insert(0,str(result))

        # RULE 8 - handling conditional
        elif val == 'β':
            rule = '8'
            rand = stack.pop(0)
            if rand == 'true':
                control.pop()           # this holds the false case
                var = control.pop()     # this holds the true case
            else:
                var = control.pop()     # this holds the false case
                control.pop()           # this holds the true case
            # based on the case we choose we find the control structure relevant
            # to it and add it to the control
            for item in result_dict[var]:
                control.append(item)

        # RULE 9 - formation of tuple
        elif val.startswith('tau'):
            rule = '9'
            num = val[4]
            tup = []
            for i in range(0,int(num)):
                tup.append(stack.pop(0))
            stack.insert(0,tup)

        # this is also a built in function of RPAL
        # using this we can add elements to tuples
        elif val.startswith('aug'):
            rule = '6'
            var = stack.pop(0)
            if isinstance(var, list):
                var.append(stack.pop(0))
                stack.insert(0,var)
            # if there is no tuple we create a tuple with only one element
            else:
                tup = [stack.pop(0)]
                stack.insert(0,tup)


        # RULE 5 - handling the environment values
        elif val.startswith('Ҽ'):
            rule = '5'
            for item in stack:
                if item == val:
                    stack.remove(val)
                    break

        # RULE 1 - moving elements from control to stack
        else:
            rule = '1'
            stack.insert(0, val)
            if val.startswith('λ_'):
                rule = '2'

        # Output the evaluation when set to True
        if out:
            print_control_stack(control, stack)

# this method prints the control and the stack in operation as mentioned in the lecture notes.
def print_control_stack(control, stack):
    # Get the width of the terminal window
    terminal_width, _ = shutil.get_terminal_size()

    # Calculate the maximum length of the content (to determine the padding)
    max_length = max(len(' '.join(control)), len(' '.join(str(item) for item in stack)))

    # Calculate the total length of the concatenated strings
    total_length = max_length * 2 + 1  # Total length includes the space between the lists

    # Calculate the number of spaces needed to fill the remaining width
    num_spaces = int(max(terminal_width - total_length, 0) * 0.5)  # Ensure it's non-negative

    # Construct the formatted string with the two lists separated by spaces
    formatted_string = ' '.join(control).ljust(max_length) + ' ' * num_spaces + '|' + ' ' * num_spaces + ' '.join(str(item) for item in stack).rjust(max_length)

    print(formatted_string)
    print(terminal_width * '-')

if __name__ == "__main__":

    # Example usage
    ast_list = ['let', '.fcn_form', '..<ID:Sum>', '..<ID:A>', '..where', '...gamma', '....<ID:Psum>', '....tau', 
                '.....<ID:A>', '.....gamma', '......<ID:Order>', '......<ID:A>', '...rec', '....fcn_form', '.....<ID:Psum>', 
                '.....,', '......<ID:T>', '......<ID:N>', '.....->', '......eq', '.......<ID:N>', '.......<INT:0>', '......<INT:0>', 
                '......+', '.......gamma', '........<ID:Psum>', '........tau', '.........<ID:T>', '.........-', '..........<ID:N>', 
                '..........<INT:1>', '.......gamma', '........<ID:T>', '........<ID:N>', '.gamma', '..<ID:Print>', '..gamma', 
                '...<ID:Sum>', '...tau', '....<INT:1>', '....<INT:2>', '....<INT:3>', '....<INT:4>', '....<INT:5>']
    

    result_dict = create_control_structure(ast_list)

    control = []
    stack = []
    control.append('Ҽ0')
    stack.append('Ҽ0')
    for val in result_dict['δ_0']:
        control.append(val)

    env = {}
    evaluate(control,stack, result_dict, env)
