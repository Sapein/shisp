"""
Compiler
"""

class Boilerplate:
    """
    Contains Boilerplate for compilization to POSIX Shell.

    shebang: the shebang line to output. (Default: #!/bin/sh)
    ifs: what to set the IFS too.
    """
    a_shebang = '#!/bin/sh'
    ifs='unset IFS\nIFS=":"'

    def __str__(self):
        output = ''
        for attr in dir(self.__class__):
            if "__" in attr:
                continue
            output = '{}{}\n'.format(output, getattr(self, attr))
        return output


from shisp_ast import AST, Node, ListNode, Number, String, VariableRef, MacroCall, Comment, FunctionCall, ReturnNode

def compile_return(node: ReturnNode) -> str:
    actual = node.children[0]
    if node.parent.macro_name == "defun":
        # IF we are defun
        fname = node.parent.children[0].data
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
            case ListNode(_):
                if len(actual.children) == 0:
                    return '__{}_RVAL=nil'.format(fname)
                elif len(actual.children) >= 1:
                    raise SyntaxError("")


def compile_defun(node: MacroCall) -> str:
    name = node.children[0].data
    args = node.args
    body = compile_children(node.body)

    definition = '\n{}() {{\n'.format(name)
    new_body = ['\t{}\n'.format(l) for l in body.split('\n')]
    body = ''.join(new_body).replace('\t\n', '')[:-1]


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

    return '{}{}\n{}\n{}\n}}\n'.format(definition,
                                   compiled_args,
                                   body,
                                   arg_cleanup)

def compile_node(node: Node) -> str:
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
            return '"${{{}}}"'.format(node.data.name)
        case ListNode(_):
            return compile_list(node)
        case ReturnNode(_):
            return compile_return(node)
    print(node)
    raise SyntaxError("Unknown Node!")


def compile_list(node: ListNode) -> str:
    list_call = [(isinstance(c, ListNode) or
                  isinstance(c, FunctionCall) or
                  isinstance(c, MacroCall))
                 for c in node.children]
    for b in list_call:
        if b:
            output = compile_children(node)
            return '{}'.format(output)
    if len(node.children) > 1:
        return '"{}"'.format(':'.join([compile_node(c) for c in node.children]))
    else:
        return compile_node(node.children[0])

def compile_children(node: Node) -> str:
    output = ''
    for child in node.children:
        match child:
            case MacroCall(macro_name='let'):
                asmnt = '{name}={value}\n'
                asmnt = asmnt.format(name=child.args.data,
                                     value=compile_node(child.body))
                output = '{}{}'.format(output, asmnt)
            case MacroCall(macro_name='defun'):
                output = '{}{}'.format(output, compile_defun(child))
            case ListNode(_):
                output = '{}{}\n'.format(output, compile_list(child))
            case Node(_):
                output = '{}{}'.format(output, compile_node(child))
    return output


def compile(ast: AST) -> str:
    """
    Compiles the AST to POSIX Shell
    """
    return '{}\n{}'.format(Boilerplate(),
                         compile_children(ast.base_node))
