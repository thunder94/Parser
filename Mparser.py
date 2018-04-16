#!/usr/bin/python

import ply.yacc as yacc
import scanner

symtab = {}
tokens = scanner.tokens

precedence = (
   ("nonassoc", 'ONLYIF'),
   ("nonassoc", 'ELSE'),
   ("right", '='),
   ("left", '+', '-'),
   ("left", '*', '/'),
   ("right", 'UMINUS'),
   #("left", 'MASSIGN'),
)


def p_error(p):
    if p:
        print("Syntax error at line {0}: LexToken({1}, '{2}')".format(p.lineno, p.type, p.value))
    else:
        print("Unexpected end of input")


def p_start(p):
    """start : INSTRUCTION
             | INSTRUCTION start
             | FORLOOP
             | FORLOOP start
             | WHILELOOP
             | WHILELOOP start
             | IFELSE
             | IFELSE start
             """
    #print(p[1])
    #if   len(p)==3: print("p[1]=", p[1])
    #else:           print("p[2]=", p[2])


def p_instructions(p):
    """INSTRUCTIONS : INSTRUCTION
                    | INSTRUCTION INSTRUCTIONS"""
    p[0] = p[1]


def p_instruction(p):
    """INSTRUCTION : EXPRESSION ';'
                   | """
    if len(p) == 3:
        p[0] = p[1]


def p_expression_number(p):
    """EXPRESSION : INTNUM
                | FLOATNUM"""
    p[0] = p[1]


def p_expression_var(p):
    """EXPRESSION : ID"""
    val = symtab.get(p[1])
    if val:
        p[0] = val
    else:
        p[0] = 0
        print("%s not used" %p[1])


def p_expression_assignment(p):
    """EXPRESSION : ID '=' EXPRESSION"""
    p[0] = p[3]
    symtab[p[1]] = p[3]


def p_expression_sum(p):
    """EXPRESSION : EXPRESSION '+' EXPRESSION
                  | EXPRESSION '-' EXPRESSION"""
    if   p[2] == '+': p[0] = p[1] + p[3]
    elif p[2] == '-': p[0] = p[1] - p[3]


def p_expression_mul(p):
    """EXPRESSION : EXPRESSION '*' EXPRESSION
                  | EXPRESSION '/' EXPRESSION"""
    if   p[2] == '*': p[0] = p[1] * p[3]
    elif p[2] == '/': p[0] = p[1] / p[3]


def p_expression_group(p):
    """EXPRESSION : '(' EXPRESSION ')'"""
    p[0] = p[2]


def p_matrix_special_init(p):
    """EXPRESSION : ZEROS '(' INTNUM ')'
                  | ONES '(' INTNUM ')'
                  | EYE '(' INTNUM ')' """
    if   p[1] == 'zeros':
        p[0] = [[0 for x in range(p[3])] for y in range(p[3])]
    elif p[1] == 'ones':
        p[0] = [[1 for x in range(p[3])] for y in range(p[3])]
    elif p[1] == 'eye':
        matrix = [[0 for x in range(p[3])] for y in range(p[3])]
        for i in range(p[3]):
            matrix[i][i] = 1
        p[0] = matrix


def p_matrix_element_modify(p):
    """EXPRESSION : ID '[' INTNUM ',' INTNUM ']' '=' INTNUM"""
    p[0] = p[8]
    symtab[p[1]][p[3]][p[5]] = p[8]


def p_negation(p):
    """EXPRESSION : '-' EXPRESSION %prec UMINUS"""
    p[0] = -p[2]


def p_matrix_transpose(p):
    """EXPRESSION : ID TRANSPOSE"""
    matrix = symtab[p[1]]
    p[0] = [list(i) for i in zip(*matrix)]


def p_special_assignment(p):
    """EXPRESSION : ID ADDASSIGN ID
                  | ID SUBASSIGN ID
                  | ID MULASSIGN ID
                  | ID DIVASSIGN ID"""
    if   p[2] == '+=':
        p[0] = symtab[p[1]] + symtab[p[3]]
        symtab[p[1]] = symtab[p[1]] + symtab[p[3]]
    elif p[2] == '-=':
        p[0] = symtab[p[1]] - symtab[p[3]]
        symtab[p[1]] = symtab[p[1]] - symtab[p[3]]
    elif p[2] == '*=':
        p[0] = symtab[p[1]] * symtab[p[3]]
        symtab[p[1]] = symtab[p[1]] * symtab[p[3]]
    elif p[2] == '/=':
        p[0] = symtab[p[1]] / symtab[p[3]]
        symtab[p[1]] = symtab[p[1]] / symtab[p[3]]


def p_matrix_binary_operations(p):
    """EXPRESSION : ID DOTADD ID
                  | ID DOTSUB ID
                  | ID DOTMUL ID
                  | ID DOTDIV ID"""
    if len(symtab[p[1]]) != len(symtab[p[3]]):
        print('Cannot perform this operation on matrices of different size!')
        raise SyntaxError
    size = len(symtab[p[1]])
    result = [[] for i in range(size)]
    for row in range(size):
        for column in range(size):
            left = symtab[p[1]][row][column]
            right = symtab[p[3]][row][column]
            if   p[2] == '.+':
                result[row].append(left + right)
            elif p[2] == '.-':
                result[row].append(left - right)
            elif p[2] == '.*':
                result[row].append(left * right)
            elif p[2] == './':
                result[row].append(left / right)
    p[0] = result


#current_id = None
#current_matrix_row = None


'''def p_matrix_init(p):
    """EXPRESSION : '[' ROW %prec MASSIGN
       ROW        : INTNUM ',' ROW
                  | INTNUM ']' """
    global current_id
    if p[1] == '[':
        current_id = p[1]
        symtab[current_id] = [[]]
        p[0] = [[]]
        print(5, current_id)
    elif len(p) == 4:
        p[0] = p[1]
        print(4, current_id)
    elif len(p) == 3:
        p[0] = p[1]
        print(3, current_id)'''


def p_matrix_values(p):
    """MATRIX_VALUES : ROW
                     | ROW ';' MATRIX_VALUES
        """
    pass


def p_row(p):
    """ROW : EXPRESSION
           | EXPRESSION ',' ROW
           """
    pass


def p_matrix_init(p):
    """EXPRESSION : '[' MATRIX_VALUES ']'
        """
    pass


def p_complex_instruction(p):
    """COMPLEX_INS : FORLOOP
                    | WHILELOOP
                    | IFELSE
                    """
    pass


def p_instructions_block(p):
    """INSTR_BLOCK : COMPLEX_INS
                    | INSTRUCTIONS
                    """
    pass


def p_for_loop(p):
    """FORLOOP : FOR ID '=' INTNUM ':' INTNUM '{' INSTR_BLOCK  '}'
                  | FOR ID '=' INTNUM ':' ID '{' INSTR_BLOCK  '}'
                  | FOR ID '=' ID ':' INTNUM '{' INSTR_BLOCK  '}'
                  | FOR ID '=' ID ':' ID '{' INSTR_BLOCK  '}'
                  """
    pass


def p_relation_op(p):
    """RELATION_OP : E
                    | '<'
                    | '>'
                    | LE
                    | GE
                    | NE
                    """
    pass


def p_expression_relation(p):
    """RELATION_EXPR : EXPRESSION RELATION_OP EXPRESSION
        """
    pass


def p_while_loop(p):
    """WHILELOOP : WHILE '(' RELATION_EXPR ')' '{' INSTR_BLOCK  '}'
                    """
    pass


def p_if_else(p):
    """IFELSE : IF '(' RELATION_EXPR ')' INSTR_BLOCK %prec ONLYIF
                | IF '(' RELATION_EXPR ')' INSTR_BLOCK ELSE INSTR_BLOCK
                """
    pass


def p_ids(p):
    """IDS : ID ',' IDS
            | ID
            """
    pass


def p_print(p):
    """INSTRUCTION : PRINT IDS ';'
                  | PRINT STRING ';'
                  """


def p_jump_statement(p):
    """INSTRUCTION : JUMP_CONTINUE
                   | JUMP_BREAK
                   | JUMP_RETURN
                   """


def p_jump_statement_continue(p):
    """JUMP_CONTINUE : CONTINUE ';'"""
    pass


def p_jump_statement_break(p):
    """JUMP_BREAK : BREAK ';'"""
    pass


##czy tutaj tez powinno sie dodac   boola do expression  >> p_expression_relation
def p_jump_statement_return(p):
    """JUMP_RETURN : RETURN EXPRESSION ';'"""
    pass

parser = yacc.yacc()

#def p_program(p):
#    """program : instructions_opt"""


#def p_instructions_opt_1(p):
#    """instructions_opt : instructions """


#def p_instructions_opt_2(p):
#    """instructions_opt : """


#def p_instructions_1(p):
#    """instructions : instructions instruction """


#def p_instructions_2(p):
#    """instructions : instruction """


# to finish the grammar
# ....

