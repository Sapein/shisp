"""
Compiler
"""

from functools import reduce
from operator import or_

class Boilerplate:
    """
    Contains Boilerplate for compilization to POSIX Shell.

    shebang: the shebang line to output. (Default: #!/bin/sh)
    ifs: what to set the IFS too.
    """
    a_shebang = '#!/bin/sh'
    ifs='unset IFS\nIFS=" "'

    def __str__(self):
        output = ''
        for attr in dir(self.__class__):
            if "__" in attr:
                continue
            output = '{}{}\n'.format(output, getattr(self, attr))
        return output


from shisp_ast import AST, Node, Expr, Number, String, VariableRef, MacroCall, Comment, FunctionCall, ReturnNode, Symbol


def compile_return(node: ReturnNode) -> str:
    actual = node.children[0]
    if node.parent.parent.macro_name == "defun":
        # IF we are defun
        fname = node.parent.parent.children[0].escape_data()
        match actual:
            case Number(_) | String(_) | VariableRef(_):
                return ('__{}_RVAL={}'
                ).format(fname,
                         compile_node(actual))
            case FunctionCall(_):
                return ('{}'
                 '__{}_RVAL="${{__{}_RVAL}}"'
                ).format(compile_node(actual),
                         fname,
                         actual.data.name)
            case Expr(_):
                return '{} | read __{}_RVAL'.format(compile_expr(actual), fname)
    elif node.parent.parent.macro_name == 'depun':
        # IF we are depun
        fname = node.parent.parent.children[0].escape_data()
        match actual:
            case Number(_) | String(_):
                return ("printf -- {}'\\n'"
                       ).format(compile_node(actual))
            case VariableRef(_):
                return ("printf -- {}'\\n'"
                       ).format(compile_node(actual))
            case FunctionCall(_):
                if actual.pure:
                    return ("printf -- $({})'\\n'"
                           ).format(compile_node(actual))
                else:
                    return ('{}'
                            "printf -- ${{__{}_RVAL}}'\\n'"
                           ).format(compile_node(actual),
                                    actual.data.name)
            case Expr(_):
                return ("printf -- $({})'\\n'").format(compile_expr(actual))

def compile_depun(node: MacroCall) -> str:
    name = node.children[0].escape_data()
    args = node.args
    body = compile_children(node.body[0])

    definition = '\n{}() (\n'.format(name)
    body = ['\t{}'.format(l) for l in body]

    compiled_args = ""
    arg_cleanup = "\n\tunset "
    if args:
        for index, arg in enumerate(args.children, 1):
            compiled_args = ('{}\t{}="${}"\n'
                            ).format(compiled_args,
                                     arg.data,
                                     index)

        for arg in args.children:
            arg_cleanup = '{}{} '.format(arg_cleanup,
                                         arg.data)

    return '{}{}\n{}{}\n)\n'.format(definition,
                                   compiled_args,
                                   ''.join(body),
                                   arg_cleanup)



def compile_defun(node: MacroCall) -> str:
    name = node.children[0].data
    args = node.args
    body = compile_children(node.body[0])

    definition = '\n{}() {{\n'.format(name)
    body = ['\t{}'.format(l) for l in body]

    compiled_args = ""
    arg_cleanup = "\n\tunset "
    if args:
        for index, arg in enumerate(args.children, 1):
            compiled_args = ('{}\t{}="${}"\n'
                            ).format(compiled_args,
                                     arg.data,
                                     index)

        for arg in args.children:
            arg_cleanup = '{}{} '.format(arg_cleanup,
                                         arg.data)

    return '{}{}\n{}{}\n}}\n'.format(definition,
                                   compiled_args,
                                   ''.join(body),
                                   arg_cleanup)

def compile_node(node: Node, escaped=True) -> str:
    match node:
        case Comment(_):
            return ''
        case Number(_):
            return node.data
        case String(_):
            return node.data
        case FunctionCall(_):
            return '{}'.format(node.data.name)
        case VariableRef(_):
            return '${{{}}}'.format(node.data.name)
        case Expr(_):
            return compile_expr(node)
        case ReturnNode(_):
            return compile_return(node)
        case Symbol(_) if escaped == True:
            return node.escape_data()
        case Symbol(_):
            return node.data
    print(node)
    raise SyntaxError("Unknown Node!")


def compile_expr(node: Expr) -> str:
    has_expr = reduce(or_, [isinstance(c, Expr) for c in node.children])
    has_fcal = reduce(or_, [isinstance(c, FunctionCall) for c in node.children])
    has_mcal = reduce(or_, [isinstance(c, MacroCall) for c in node.children])

    if has_expr or has_fcal or has_mcal:
        return ' '.join(compile_children(node))
    elif len(node.children) == 0:
        return '"nil"'
    else:
        return ' '.join(compile_children(node))

def compile_quote(body: list[Node]) -> str:
    def _compile_node(node: Node) -> str:
        match node:
            case Expr(_):
                output = []
                for child in node.children:
                    output.append(_compile_node(child))
                return '({})'.format(' '.join(output))
            case Node(_):
                return node.data
        raise SyntaxError
    output = []
    for node in body:
        output.append(_compile_node(node))
    return "'{}'".format(' '.join(output))

def compile_quasiquote(body: list[Node]) -> str:
    raise NotImplementedError
    def _compile_node(node: Node) -> str:
        match node:
            case Expr(_):
                output = []
                for child in node.children:
                    output.append(_compile_node(child))
                return '({})'.format(' '.join(output))
            case Node(_):
                return node.data
        raise SyntaxError
    output = []
    for node in body:
        output.append(_compile_node(node))
    return "'{}'".format(' '.join(output))


def compile_children(node: Node) -> list[str]:
    output = []
    for child in node.children:
        match child:
            case MacroCall(macro_name='quasi-quote'):
                raise NotImplementedError
            case MacroCall(macro_name='quote'):
                output.append(compile_quote(child.body))
            case MacroCall(macro_name='shell-literal'):
                output.append(' '.join([compile_node(c, False) for c in child.body]))
            case MacroCall(macro_name='let'):
                match child.body[0]:
                    case FunctionCall(_):
                        if not child.body[0].is_pure:
                            asmnt = ('{{value}}\n'
                                     '{{name}}="${{{{__{}_RVAL}}}}"\n'
                                    ).format(child.body[0].data.name)
                        else:
                            asmnt = ('{name}=$({value})\n')
                    case Node(_):
                        asmnt = '{name}={value}\n'
                asmnt = asmnt.format(name=child.args.data,
                                     value=compile_node(child.body[0]))
                output.append(asmnt)
            case MacroCall(macro_name='defun'):
                output.append(compile_defun(child))
            case MacroCall(macro_name='depun'):
                output.append(compile_depun(child))
            case Expr(_):
                output.append('{}\n'.format(compile_expr(child)))
            case Node(_):
                output.append(compile_node(child))
    return output


def compile(ast: AST) -> str:
    """
    Compiles the AST to POSIX Shell
    """
    return '{}\n{}\n'.format(Boilerplate(),
                           ''.join(compile_children(ast.base_node)))
