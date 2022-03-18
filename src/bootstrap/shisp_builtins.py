"""
This handles the coding for shisp-builtins for compilation
purposes
"""

from scoping import Builtin, Variable
from parser import List, Scope, Comment
from dataclasses import dataclass


@dataclass
class Let(Builtin):
    """
    This defines a basic little builtin for 
    let to allow for variable definition.
    """
    def _find_scope(self, node):
        pass

    def find_scope(self, node):
        match node.parent:
            case List(_):
                return node.parent.scope
            case Comment(_):
                return None
            case Node(_):
                return node.parent

    def emit(self) -> str:
        return 

    def meta_eval(self, node):
        """
        Evaluate when parsing. 
        Takes in the node that is used with let.
        """
        #(let {NAME} {BODY})
        name = node.parent.children[2].data
        body = node.parent.children[4]
        var = Variable(node.row, node.column, name, [body])
        scope_p = node.parent.parent
        while True:
            scope_p = self.find_scope(node.parent)
            if isinstance(scope_p, Scope):
                scope_p.add_variable(var)
                break
            elif isinstance(scope_p, Comment):
                break


class defun:
    name = 'defun'

class depun:
    name = 'depun'

class read:
    name = 'read'

class eval:
    name = 'eval'

class _print:
    name = 'print'
