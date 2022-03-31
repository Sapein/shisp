"""
This module is the 'main' module for the bootstrap compiler.
"""

from sys import argv
from typing import Optional

import lexer.tokens
import parser
import state
import errors


def run_compiler(file_name: str, output_file: Optional[str] = None):
    file_name='test.shisp'
    try:
        with open(file_name, 'r') as f:
            tokens = lexer.tokens.parse_file(f.read())
    except FileNotFoundError:
        print("File {} not found!".format(file_name))
        return

    _state = state.GlobalState([file_name], {}, {}, [], file_name)
    try:
        ast = parser.parse_tokens.parse_tokens(tokens, _state)
        ast = parser.desugar_source.combine_ast(ast)
        ast = parser.simplify_ast.squash_ast(ast)
        ast = parser.expand_metamacros.resolve_metamacros(ast)
        ast = parser.handle_varrefs.check_variables(ast)
        ast = parser.handle_functions.replace_references(ast)
    except errors.AbortParse:
        for k in _state.errors:
            print("{}:\n".format(k))
            for err in _state.errors[k]:
                print(err.output)
                print('\n')
        return

    output = compiler.compiler.compile(ast)

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
