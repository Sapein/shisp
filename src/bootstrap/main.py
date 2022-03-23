"""
This module is the 'main' module for the bootstrap compiler.
"""


import tokens

import parser
import pass2
import pass3
import pass4
import pass5
import pass6

import compiler


with open('test.shisp', 'r') as f:
    tokenized = tokens.parse_file(f.read())
    ast = parser.parse_tokens(tokenized)
    ast.print_ast()
    ast = pass2.squash_ast(ast)
    ast = pass3.resolve_metamacros(ast)
    ast = pass4.expand_macros(ast)
    ast = pass5.check_variables(ast)
    ast = pass6.replace_references(ast)
    output = compiler.compile(ast)
    with open('test.sh', 'w') as f:
        f.write(output)
