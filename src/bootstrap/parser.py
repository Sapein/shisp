"""
Parser
"""

import re

from dataclasses import dataclass
from typing import Optional, Any
from tokens import Token


@dataclass
class AST:
    program_name: str
    base_node: "List"

@dataclass
class BaseNode:
    row: int | tuple[int] 
    column: int | tuple[int]
    children: list["Node"]
    parent: Optional["Node"]

    def _stringify_children(self, *args, **kwargs):
        children_text = []
        for child in self.children:
            c_text = str(child).split('\n')
            new_c_text = ''
            for line in c_text:
                new_c_text = '{old}|-- {line}\n'.format(old=new_c_text, line=line).replace('\n\t\n\t', '')
                new_c_text = new_c_text.replace('|-- |--', '       ')
            children_text.append(new_c_text)
        return '{children}'.format(children=''.join(children_text)).replace('|-- \n', '')
 
    def __str__(self, *args, **kwargs):
        output = ('Type: {type}\n'
                  'Row:  {row}\n'
                  'Col:  {col}\n'
                  '{extra}')
        extra = ''
        if self.children:
            child_text = self._stringify_children(*args, **kwargs)
            extra = '{extra}{children}'.format(extra=extra, children=child_text)
        return output.format(type=self.__class__.__name__, row=self.row, col=self.column, extra=extra)


@dataclass
class Node(BaseNode):
    children: list["Node"] = None
    parent: Optional["Node"] = None

    @classmethod
    def from_token(cls, token: Token) -> "Node":
        """ Turns a Token into a Node. """
        return cls(token.row, token.column, list(), None)

    @classmethod
    def from_tokens(cls, tokens: list[Token]) -> "Node":
        row = (tokens[0].row, tokens[-1].row)
        col = (tokens[0].column, tokens[-1].column)
        return cls(row, col, list(), None)

    def replace_child(self, child, replacement):
        """ Replaces a child with another one """
        index = self.children.index(child)
        self.children.insert(index, replacement)
        self.children.remove(child)
        replacement.parent = self
        replacement.children = child.children
        for _child in child.children:
            _child.replace_parent(replacement)
        child.children.clear()
        child.parent = None

    def replace(self, replacement):
        self.parent.replace_child(self, replacement)

    def replace_parent(self, new_parent):
        self.parent = new_parent

    def add_child(self, child: "Node"):
        """ Adds a child to a node. """
        self.children.append(child)
        child.parent = self


@dataclass
class Scope(Node):
    variables: dict = None

    def __init__(self, *args, variables=None, **kwargs):
        if variables is None:
            variables = {}
        self.variables = variables
        super().__init__(*args, **kwargs)

    def add_variable(self, variable: "Variable"):
        self.variables[variable.name] = variable

    def __str__(self, *args, **kwargs):
        _str = '\n'
        for var in self.variables.values():
            _str = "{}\t{}\n".format(_str, var)
        return _str
        return str(self.variables)

@dataclass
class List(Node):
    scope: "Scope" = None

    def __init__(self, *args, scope=None, **kwargs):
        if scope is None:
            scope = Scope(0,0)
        self.scope = scope
        super().__init__(*args, **kwargs)


    def __str__(self, *args, **kwargs):
        output = ('Type: {type}\n'
                  'Row:  {row}\n'
                  'Col:  {col}\n'
                  'Scope: {scope}\n'
                  '{extra}')
        extra = ''
        if self.children:
            child_text = self._stringify_children(*args, **kwargs)
            extra = '{extra}{children}'.format(extra=extra, children=child_text)
        return output.format(type=self.__class__.__name__, row=self.row, col=self.column, extra=extra,
                            scope=self.scope)
    
    def emit(self):
        list_output = "'"
        for child in self.children:
            match child:
                case List(_):
                    raise SyntaxError("Nested Lists Aren't Allowed at this time!")
                case Space(_):
                    pass
                case Text(_):
                    pass
                case Node(_):
                    list_output="{}{}:".format(list_output, child.emit())
        return "{}'".format(list_output).replace(":'", "'").replace("':", "'")

@dataclass
class Atom(Node):
    data: Optional[Any] = None
    

    @classmethod
    def from_token(cls, token: Token) -> "Node":
        """ Turns a Token into a Node. """
        return cls(token.row, token.column, list(), None, token.char)


    @classmethod
    def from_tokens(cls, tokens: list[Token]) -> "Node":
        if not tokens:
            raise Exception("Tokens is empty!")
        symbol = ''.join([t.char for t in tokens])
        row = (tokens[0].row, tokens[-1].row)
        col = (tokens[0].column, tokens[-1].column)
        return cls(row, col, list(), None, symbol)


    def __str__(self, *args, **kwargs):
        output = ('Type: {type}\n'
                  'Row:  {row}\n'
                  'Col:  {col}\n'
                  '{extra}\n')
        extra = ''

        if self.data:
            extra = '{extra}Data: {data}\n'.format(extra=extra, data=self.data)
        if self.children:
            child_text = self._stringify_children(*args, **kwargs)
            extra = '{extra}{children}\n'.format(extra=extra, children=child_text)
        return output.format(type=self.__class__.__name__, row=self.row, col=self.column, extra=extra)


    def emit(self):
        return self.data


@dataclass
class Space(Node):

    data = ' '


    def __str__(self, *args, **kwargs):
        output = ('Type: {type}\n'
                  'Row:  {row}\n'
                  'Col:  {col}\n'
                  '{extra}\n')
        extra = ''

        if self.data:
            extra = '{extra}Data: {data}\n'.format(extra=extra, data=self.data)
        return output.format(type=self.__class__.__name__, row=self.row, col=self.column, extra=extra)

    def emit(self):
        return self.data


@dataclass
class Comment(Atom):
    pass


@dataclass
class Text(Atom):
    data: Optional[str] = None


@dataclass
class Number(Atom):
    data: Optional[int] = None


@dataclass
class EndList(Space):
    data = ')'

@dataclass
class MacroCall(BaseNode):
    macro: Node
    macro_name :str
    args: list
    body: "list"

    def __str__(self, *args, **kwargs):
        print(1)
        output = ('Type: {type}\n'
                  'Row:  {row}\n'
                  'Col:  {col}\n'
                  'Name: {name}\n')

        return output.format(type=self.__class__.__name__, row=self.row, col=self.column, name=self.macro_name)

    def emit(self):
        return self.macro.emit(self)


@dataclass
class NewLine(Space):
    data = '\n'

@dataclass
class DoubleQuote(Space):
    data = '"'

@dataclass
class String(Text):
    pass

def to_node(tokens: list[Token]):
    symbol = ''.join([t.char for t in tokens])
    if re.match('[a-zA-Z\+\-\*\/]+[a-zA-Z0-9]*', symbol):
        return Atom.from_tokens(tokens)
    elif re.match('[0-9]+', symbol):
        return Number.from_tokens(tokens)
    return Node.from_tokens(tokens)


def match_tokens(token: Token, base_node: Node, in_symbol=False, in_comment=False, in_string=False, tokens_to_combine=None):
    if tokens_to_combine is None:
        tokens_to_combine = []
    match token:
        case Token(char='\n'):
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine)
                base_node.add_child(node)
                tokens_to_combine = []
            if in_comment == True:
                in_symbol = False
                in_comment = False
                if tokens_to_combine:
                    node = to_node(tokens_to_combine)
                    base_node.add_child(node)
                    tokens_to_combine = []
            if in_string == True:
                raise SyntaxError("String can not pass newline!")
            base_node.add_child(NewLine.from_token(token))
            match base_node:
                case Comment(_):
                    base_node = base_node.parent
        case Token(char=';') if in_comment == False:
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine)
                base_node.add_child(node)
                tokens_to_combine = []

            node = Comment.from_token(token)
            base_node.add_child(node)
            base_node = node
            in_comment = True 
        case Token(char='"') if in_comment == False and in_string == False:
            if in_symbol == True:
                raise SyntaxError('{}" not a valid symbol!'.format(''.join(tokens_to_combine)))
            in_string = True
            tokens_to_combine.append(token)
        case Token(char='"') if in_string == True:
            in_string = False
            tokens_to_combine.append(token)
            base_node.add_child(String.from_tokens(tokens_to_combine))
            tokens_to_combine = []
        case Token(char='"') if in_comment == True:
            if tokens_to_combine:
                base_node.add_child(to_node(tokens_to_combine))
                tokens_to_combine = []
            base_node.add_child(DoubleQuote.from_token(token))
        case Token(char="(") if in_comment == False:
            if in_symbol == True:
                raise SyntaxError("{}( not a valid symbol!".format(''.join(tokens_to_combine)))
            new_node = List.from_token(token)
            base_node.add_child(new_node)
            base_node = new_node
        case Token(char=")") if in_comment == False and in_string == False:
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine)
                base_node.add_child(node)
                tokens_to_combine = []
            base_node.add_child(EndList.from_token(token))
            base_node = base_node.parent
        case Token(char=' ') if in_comment == False and in_string == False:
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine)
                base_node.add_child(node)
                tokens_to_combine = []
            base_node.add_child(Space.from_token(token))
        case Token(_) if in_comment == False and in_string == False:
            if not in_symbol:
                in_symbol = True
            tokens_to_combine.append(token)
        case Token(_) if in_string == True:
            tokens_to_combine.append(token)
        case Token(char=' ') if in_comment == True:
            if tokens_to_combine:
                base_node.add_child(to_node(tokens_to_combine))
                tokens_to_combine = []
            base_node.add_child(Space.from_token(token))
        case Token(_) if in_comment == True:
            tokens_to_combine.append(token)
    return base_node, in_symbol, in_comment, in_string, tokens_to_combine

def parse_tokens(text: list[Token]):
    base_node = List(0, 0, list(), None, scope=Scope(0,0))
    ast = AST("test", base_node)
    tokens_to_combine = []
    in_symbol = False
    in_comment = False
    in_string = False
    for token in text:
        base_node, in_symbol, in_comment, in_string, tokens_to_combine = match_tokens(token, base_node, in_symbol, in_comment, in_string, tokens_to_combine)
    if tokens_to_combine:
        node = to_node(tokens_to_combine)
        base_node.add_child(node)
    return ast
