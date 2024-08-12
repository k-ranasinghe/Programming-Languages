Next_Token_Type = ""  # To track next token type
Next_Token = ""  # to track next token
Curr_Token = ""  # to track current token befor asign next value to token. This is important to save token for token type identifier, integer and string temporaly.
Parse_tree = []  # To save abstract syntax tree post order manner


# This function check that tokens are matched and assign new token to New_token and handle errors
def Read(Token):
    # Declare global variables to track the next token type, current token, and next token
    global Next_Token_Type
    global Curr_Token
    global Next_Token
    # Check if the token list is empty
    if len(tokens) == 0:
        return
    # Check if the current token matches the expected token
    if Token == Next_Token_Type:
        # If the expected token is an identifier, integer, or string, update the current token.
        # It is track the value of identifier, integer, or string
        if Token in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:
            Curr_Token = Next_Token
        # Get the next token from the token list
        Next_Token_Type, Next_Token = tokens.pop(0)
    else:
        # Error handling
        if Next_Token_Type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:
            # Check for specific error cases based on the type of expected token
            if Token not in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:
                print(
                    "Error: Error occurs near ",
                    Token,
                    ". IDENTIFIER or INTEGER or STRING expected",
                )
            elif Next_Token_Type == "<IDENTIFIER>":
                print("Type Error: IDENTIFIER expected but got ", Token)
            elif Next_Token_Type == "<INTEGER>":
                print("Type Error: INTEGER expected but got ", Token)
            elif Next_Token_Type == "<STRING>":
                print("Type Error: STRING expected but got ", Token)
            else:
                print("Error: Unknown error occurs near ", Token)
        else:
            # Print a generic error message if the expected token type is not an identifier, integer, or string
            print(
                "Error: Missing",
                Token,
                "near",
                Next_Token,
                "or got some unknown Character",
            )


# This function save Parse tree node in postorder mannar
def Build_Tree(node_type, num_children):
    # Check if the node type is an identifier, integer, or string
    if node_type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:
        # If the node type is an identifier, construct the corresponding token
        if node_type == "<IDENTIFIER>":
            Token = "<ID:" + Curr_Token + ">"
        # If the node type is an integer, convert the current token to string and construct the token
        if node_type == "<INTEGER>":
            Token = "<INT:" + str(Curr_Token) + ">"
        # If the node type is a string, construct the corresponding token
        if node_type == "<STRING>":
            Token = "<STR:" + Curr_Token + ">"
        # Append the constructed token to the Parse tree along with the number of children
        Parse_tree.append((Token, num_children))
    else:
        # If the node type is not an identifier, integer, or string, append it to the Parse tree along with the number of children
        Parse_tree.append((node_type, num_children))


def E():
    # E -> ’let’ D ’in’ E => ’let’
    if Next_Token_Type == "let":
        Read("let")
        D()
        Read("in")
        E()
        Build_Tree("let", 2)
    # E -> ’fn’ Vb+ ’.’ E => ’lambda’
    elif Next_Token_Type == "fn":
        Read("fn")
        Vb()
        n = 1
        while Next_Token_Type in ["<IDENTIFIER>", "("]:
            Vb()
            n += 1
        Read(".")
        E()
        Build_Tree("lambda", n + 1)
    # E -> Ew
    else:
        Ew()


def Ew():
    T()  # E -> T
    # Ew -> T ’where’ Dr => ’where’
    if Next_Token_Type == "where":
        Read("where")
        Dr()
        Build_Tree("where", 2)


def T():
    Ta()  # E -> Ta
    # T -> Ta ( ’,’ Ta )+ => ’tau’
    if Next_Token_Type == ",":
        Read(",")
        Ta()
        n = 1  # track the number pf repitition
        while Next_Token_Type == ",":
            n += 1
            Read(",")
            Ta()
        Build_Tree("tau", n + 1)


def Ta():
    Tc()  # E -> Tc
    # Ta -> Ta ’aug’ Tc => ’aug’
    while Next_Token_Type == "aug":
        Read("aug")
        Tc()
        Build_Tree("aug", 2)


def Tc():
    B()  # E -> B
    # Tc -> B ’->’ Tc ’|’ Tc => ’->’
    if Next_Token_Type == "->":
        Read("->")
        Tc()
        Read("|")
        Tc()
        Build_Tree("->", 3)


def B():
    Bt()  # E -> Bt
    # B ->B’or’ Bt => ’or’
    while Next_Token_Type == "or":
        Read("or")
        Bt()
        Build_Tree("or", 2)


def Bt():
    Bs()  # E -> Bs
    # Bt -> Bt ’&’ Bs => ’&’
    while Next_Token_Type == "&":
        Read("&")
        Bs()
        Build_Tree("&", 2)


def Bs():
    # Bs -> ’not’ Bp => ’not’
    if Next_Token_Type == "not":
        Read("not")
        Bp()
        Build_Tree("not", 1)
    else:
        # E -> Bp
        Bp()


def Bp():
    A()  # E -> A
    # Bp -> A (’gr’ | ’>’ ) A => ’gr’
    if Next_Token_Type in ["gr", ">"]:
        Read(Next_Token_Type)
        A()
        Build_Tree("gr", 2)
    # Bp -> A (’ge’ | ’>=’) A => ’ge’
    elif Next_Token_Type in ["ge", ">="]:
        Read(Next_Token_Type)
        A()
        Build_Tree("ge", 2)
    # Bp -> A (’ls’ | ’<’ ) A => ’ls’
    elif Next_Token_Type in ["ls", "<"]:
        Read(Next_Token_Type)
        A()
        Build_Tree("ls", 2)
    # Bp -> A (’le’ | ’<=’) A => ’le’
    elif Next_Token_Type in ["le", "<="]:
        Read(Next_Token_Type)
        A()
        Build_Tree("le", 2)
    # Bp -> A ’eq’ A => ’eq’
    elif Next_Token_Type == "eq":
        Read(Next_Token_Type)
        A()
        Build_Tree("eq", 2)
    # Bp -> A ’ne’ A => ’ne’
    elif Next_Token_Type == "ne":
        Read(Next_Token_Type)
        A()
        Build_Tree("ne", 2)


def A():
    # A -> ’+’ At
    if Next_Token_Type == "+":
        Read("+")
        At()
    # A -> ’-’ At => ’neg’
    elif Next_Token_Type == "-":
        Read("-")
        At()
        Build_Tree("neg", 1)
    else:
        At()  # A -> At
        while Next_Token_Type in ["+", "-"]:
            # A ->A’+’ At => ’+’
            if Next_Token_Type == "+":
                Read("+")
                At()
                Build_Tree("+", 2)
            # A -> A ’-’ At => ’-’
            elif Next_Token_Type == "-":
                Read("-")
                At()
                Build_Tree("-", 2)


def At():
    Af()  # A -> Af
    while Next_Token_Type in ["*", "/"]:
        # At -> At ’*’ Af => ’*’
        if Next_Token_Type == "*":
            Read("*")
            Af()
            Build_Tree("*", 2)
        # At -> At ’/’ Af => ’/’
        elif Next_Token_Type == "/":
            Read("/")
            Af()
            Build_Tree("/", 2)


def Af():
    Ap()  # Af -> Ap
    # Af -> Ap ’**’ Af => ’**’
    if Next_Token_Type == "**":
        Read("**")
        Af()
        Build_Tree("**", 2)


def Ap():
    R()  # Ap -> R
    # Ap -> Ap ’@’ ’<IDENTIFIER>’ R => ’@’
    while Next_Token_Type == "@":
        Read("@")
        Read("<IDENTIFIER>")
        Build_Tree("<IDENTIFIER>", 0)
        R()
        Build_Tree("@", 2)


def R():
    Rn()  # R -> Rn
    # R ->R Rn => ’gamma’
    while Next_Token_Type in [
        "<IDENTIFIER>",
        "<INTEGER>",
        "<STRING>",
        "true",
        "false",
        "nil",
        "(",
        "dummy",
    ]:
        Rn()
        Build_Tree("gamma", 2)


def Rn():
    # Rn -> ’<IDENTIFIER>’
    if Next_Token_Type == "<IDENTIFIER>":
        Read("<IDENTIFIER>")
        Build_Tree("<IDENTIFIER>", 0)
    # Rn -> ’<INTEGER>’
    elif Next_Token_Type == "<INTEGER>":
        Read("<INTEGER>")
        Build_Tree("<INTEGER>", 0)
    # Rn -> ’<STRING>’
    elif Next_Token_Type == "<STRING>":
        Read("<STRING>")
        Build_Tree("<STRING>", 0)
    # Rn -> ’true’ => ’true’
    elif Next_Token_Type == "true":
        Read("true")
        Build_Tree("true", 0)
    # Rn -> ’false’ => ’false’
    elif Next_Token_Type == "false":
        Read("false")
        Build_Tree("false", 0)
    # Rn -> ’nil’ => ’nil’
    elif Next_Token_Type == "nil":
        Read("nil")
        Build_Tree("nil", 0)
    # Rn -> ’(’ E ’)’
    elif Next_Token_Type == "(":
        Read("(")
        E()
        Read(")")
    # Rn -> ’dummy’ => ’dummy’
    elif Next_Token_Type == "dummy":
        Read("dummy")
        Build_Tree("dummy", 0)


def D():
    Da()  # D -> Da
    # D -> Da ’within’ D => ’within’
    while Next_Token_Type == "within":
        Read("within")
        D()
        Build_Tree("within", 2)


def Da():
    Dr()  # Da -> Dr
    n = 0  # keep track of repitation of Dr
    # Da -> Dr ( ’and’ Dr )+ => ’and’
    while Next_Token_Type == "and":
        Read("and")
        Dr()
        n += 1
    if n > 0:
        Build_Tree("and", n + 1)


def Dr():
    # Dr -> ’rec’ Db => ’rec’
    if Next_Token_Type == "rec":
        Read("rec")
        Db()
        Build_Tree("rec", 1)
    else:
        # Dr -> Db
        Db()


def Db():
    # Db -> ’(’ D ’)’
    if Next_Token_Type == "(":
        Read("(")
        D()
        Read(")")
        n = 0
    if Next_Token_Type == "<IDENTIFIER>":
        # Db -> Vl ’=’ E => ’=’
        Vl()
        if Next_Token_Type == "=":
            Read("=")
            E()
            Build_Tree("=", 2)
        else:
            # Db-> ’<IDENTIFIER>’ Vb+ ’=’ E => ’function_form’
            Vb()
            n = 1
            while Next_Token_Type in ["<IDENTIFIER>", "("]:
                Vb()
                n += 1
            Read("=")
            E()
            Build_Tree("function_form", n + 2)
    else:
        print("Error:error occurs near", Next_Token, " '(' or IDENTIFIER expected.")


def Vb():
    # Vb -> ’<IDENTIFIER>’
    if Next_Token_Type == "<IDENTIFIER>":
        Read("<IDENTIFIER>")
        Build_Tree("<IDENTIFIER>", 0)
    elif Next_Token_Type == "(":
        Read("(")
        # Vb -> ’(’ Vl ’)’
        if Next_Token_Type == "<IDENTIFIER>":
            Vl()
            Read(")")
        # Vb -> ’(’ ’)’
        else:
            Read(")")
            Build_Tree("()", 0)
    else:
        # Handle Error
        print("Error:error occurs near", Next_Token, " .IDENTIFIER or ')' expected.")


def Vl():
    # Vl -> ’<IDENTIFIER>’ list ’,’ => ’,’?
    if Next_Token_Type == "<IDENTIFIER>":
        Read("<IDENTIFIER>")
        Build_Tree("<IDENTIFIER>", 0)
        n = 0
        while Next_Token_Type == ",":
            Read(",")
            Read("<IDENTIFIER>")
            Build_Tree("<IDENTIFIER>", 0)
            n += 1
        if n > 0:
            Build_Tree(",", n + 1)
    else:
        # handle error
        print("Error:error occurs near ", Next_Token, " .IDENTIFIER expected.")

# Main function parses the token list and returns the parsed tree
def parse(TokenList):
    global tokens 
    tokens = TokenList
    Read("")
    E()
    
    return Parse_tree


if __name__ == "__main__":
    
    TokenList = [
    ("let", "let"),
    ("<IDENTIFIER>", "Sum"),
    ("(", "("),
    ("<IDENTIFIER>", "A"),
    (")", ")"),
    ("=", "="),
    ("<IDENTIFIER>", "Psum"),
    ("(", "("),
    ("<IDENTIFIER>", "A"),
    (",", ","),
    ("<IDENTIFIER>", "Order"),
    ("<IDENTIFIER>", "A"),
    (")", ")"),
    ("where", "where"),
    ("rec", "rec"),
    ("<IDENTIFIER>", "Psum"),
    ("(", "("),
    ("<IDENTIFIER>", "T"),
    (",", ","),
    ("<IDENTIFIER>", "N"),
    (")", ")"),
    ("=", "="),
    ("<IDENTIFIER>", "N"),
    ("eq", "eq"),
    ("<INTEGER>", "0"),
    ("->", "->"),
    ("<INTEGER>", "0"),
    ("|", "|"),
    ("<IDENTIFIER>", "Psum"),
    ("(", "("),
    ("<IDENTIFIER>", "T"),
    (",", ","),
    ("<IDENTIFIER>", "N"),
    ("-", "-"),
    ("<INTEGER>", "1"),
    (")", ")"),
    ("+", "+"),
    ("<IDENTIFIER>", "T"),
    ("<IDENTIFIER>", "N"),
    ("in", "in"),
    ("<IDENTIFIER>", "Print"),
    ("(", "("),
    ("<IDENTIFIER>", "Sum"),
    ("(", "("),
    ("<INTEGER>", "1"),
    (",", ","),
    ("<INTEGER>", "2"),
    (",", ","),
    ("<INTEGER>", "3"),
    (",", ","),
    ("<INTEGER>", "4"),
    (",", ","),
    ("<INTEGER>", "5"),
    (")", ")"),
    (")", ")"),
]

    Parse_tree = parse(TokenList)
    print(Parse_tree)