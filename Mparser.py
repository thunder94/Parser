#!/usr/bin/python

import ply.yacc as yacc
import scanner

symtab = {}
tokens = scanner.tokens

precedence = (
   ("nonassoc", 'ONLYIF'),
   ("nonassoc", 'ELSE'),
   ("right", '=', 'ADDASSIGN', 'SUBASSIGN', 'MULASSIGN', 'DIVASSIGN'),
   ("nonassoc", '<', '>', 'E', 'NE', 'GE', 'LE'),
   ("left", '+', '-', 'DOTADD', 'DOTSUB'),
   ("left", '*', '/', 'DOTMUL', 'DOTDIV'),
   ("left", "TRANSPOSE"),
   ("right", 'UMINUS'),
)


def p_error(p):
    if p:
        print("Syntax error at line {0}: LexToken({1}, '{2}')".format(p.lineno, p.type, p.value))
    else:
        print("Unexpected end of input")


def p_start(p):
    """start : INSTRUCTION
             | INSTRUCTION start
             | COMPLEX_INS start
             | COMPLEX_INS"""
    #print(p[1])


def p_instructions(p):
    """INSTRUCTIONS : INSTRUCTION
                    | INSTRUCTION INSTRUCTIONS"""
    p[0] = p[1]


def p_instruction_end(p):
    """INSTRUCTION : INSTRUCTION ';'"""
    p[0] = p[1]


def p_print(p):
    """INSTRUCTION : PRINT IDS ';'
                  | PRINT STRING ';'
                  """


def p_ids(p):
    """IDS : ID ',' IDS
            | ID
            """
    pass


def p_jump_statement(p):
    """INSTRUCTION : JUMP_CONTINUE
                   | JUMP_BREAK
                   | JUMP_RETURN"""


def p_jump_statement_continue(p):
    """JUMP_CONTINUE : CONTINUE ';'"""
    pass


def p_jump_statement_break(p):
    """JUMP_BREAK : BREAK ';'"""
    pass


def p_jump_statement_return(p):
    """JUMP_RETURN : RETURN EXPRESSION ';'"""
    pass


def p_complex_instruction(p):
    """COMPLEX_INS : FORLOOP
                   | WHILELOOP
                   | IFELSE """
    pass


def p_for_loop(p):
    """FORLOOP : FOR ID '=' INTNUM ':' INTNUM '{' INSTR_BLOCK  '}'
                  | FOR ID '=' INTNUM ':' ID '{' INSTR_BLOCK  '}'
                  | FOR ID '=' ID ':' INTNUM '{' INSTR_BLOCK  '}'
                  | FOR ID '=' ID ':' ID '{' INSTR_BLOCK  '}'
                  """
    pass


def p_while_loop(p):
    """WHILELOOP : WHILE '(' RELATION_EXPR ')' '{' INSTR_BLOCK  '}' """
    pass


def p_if_else(p):
    """IFELSE : IF '(' RELATION_EXPR ')' INSTR_BLOCK %prec ONLYIF
                | IF '(' RELATION_EXPR ')' INSTR_BLOCK ELSE INSTR_BLOCK """
    pass


def p_instructions_block(p):
    """INSTR_BLOCK : COMPLEX_INS
                    | INSTRUCTIONS """
    pass


def p_number(p):
    """NUMBER : INTNUM
              | FLOATNUM"""
    p[0] = p[1]


def p_expression_number(p):
    """EXPRESSION : NUMBER"""
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
    """INSTRUCTION : ID '=' EXPRESSION"""
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
    """INSTRUCTION : ID '[' INTNUM ',' INTNUM ']' '=' NUMBER"""
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
    """INSTRUCTION : ID ADDASSIGN ID
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


def p_matrix_init(p):
    """EXPRESSION : '[' MATRIX_VALUES ']'
        """
    pass


def p_matrix_values(p):
    """MATRIX_VALUES : ROW
                     | ROW ';' MATRIX_VALUES
        """
    pass


def p_row(p):
    """ROW : NUMBER
           | NUMBER ',' ROW
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


parser = yacc.yacc()

