"""
Compiler
"""

from parser import Atom, Number, Text, String, Space, NewLine, Node, Comment, EndList

class Boilerplate:
    shebang = '#!/bin/sh'
    shell_stuff = 'unset IFS'
    ifs='IFS=":"'

    def __str__(self):
        output = ''
        for attr in dir(Boilerplate):
            if "__" in attr:
                continue
            output = '{}{}\n'.format(output, getattr(Boilerplate, attr))
        return output

def ast_to_shell(ast) -> tuple[str, str]:
    base_node = ast.base_node
    output = str(Boilerplate())
    for node in base_node.children:
        match node:
            case Comment(_) | EndList(_):
                pass
            case Node(_):
                output = "{}{}".format(output, node.emit())

    return ast.program_name, output

