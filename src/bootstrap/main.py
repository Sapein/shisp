"""
This module is the 'main' module for the bootstrap compiler.
"""

from sys import argv
from typing import Optional

import tokens

import parser
import pass2
import pass3
import pass4
import pass5
import pass6

import compiler


def run_compiler(file_name: str, output_file: Optional[str] = None):
    try:
        with open(file_name, 'r') as f:
            tokenized = tokens.parse_file(f.read())
    except FileNotFoundError:
        print("File {} not found!".format(file_name))
        return
    ast = parser.parse_tokens(tokenized, '.'.join(file_name.split('.')[:-1]))
    ast = pass2.squash_ast(ast)
    ast = pass3.resolve_metamacros(ast)
    ast = pass4.expand_macros(ast)
    ast = pass5.check_variables(ast)
    ast = pass6.replace_references(ast)
    output = compiler.compile(ast)
    print(ast.program_name)
    if not output_file:
        output_file = '{}.sh'.format(ast.program_name)
    with open(output_file,'w') as f:
        f.write(output)

def compiler_help():
    return 'usage: python3 main.py in_file (out_file)'

match argv:
    case [a, b]:
        run_compiler(b)
    case [a, b, c]:
        run_compiler(b, c)
    case [_] | _:
        print(compiler_help())
