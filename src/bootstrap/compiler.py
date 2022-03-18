"""
Compiler
"""

from parser import Atom, Number, Text, String, Space, NewLine, Node, Comment, EndList, MacroCall, List

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

def handle_list(node) -> str:
    for child in node.children:
        match child:
            case Comment(_) | EndList(_) | Space(_):
                pass
            case List(_):
                handle_list(child)
            case MacroCall(_):
                return child.emit()
            case Node(_):
                return child.emit()

def base_node_(node) -> str:
    for child in node.children:
        match child:
            case Comment(_) | EndList(_):
                pass
            case List(_):
                return handle_list(child)
            case Node(_):
                return child.emit()

def ast_to_shell(ast) -> tuple[str, str]:
    base_node = ast.base_node
    output = str(Boilerplate())
    output = '{}{}'.format(output, base_node_(base_node))
    return ast.program_name, output

