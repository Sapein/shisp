"""
This module is the 'main' module for the bootstrap compiler.
"""


import tokens
import parser
import scoping
import compiler


with open('test.shisp', 'r') as f:
    tokenized = tokens.parse_file(f.read())
    ast = parser.parse_tokens(tokenized)
    ast = scoping.add_globals(ast)
    ast = scoping.add_variables(ast)
    name, output = compiler.ast_to_shell(ast)
    print(output)
