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
    base_node: "Node"

@dataclass
class Node:
    row: int | tuple[int] 
    column: int | tuple[int]
    children: list["Node"] = None
    parent: Optional["Node"] = None

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

    @classmethod
    def from_token(cls, token: Token) -> "Node":
        """ Turns a Token into a Node. """
        return cls(token.row, token.column, list(), None)

    @classmethod
    def from_tokens(cls, tokens: list[Token]) -> "Node":
        row = (tokens[0].row, tokens[-1].row)
        col = (tokens[0].column, tokens[-1].column)
        return cls(row, col, list(), None)

    def add_child(self, child: "Node"):
        """ Adds a child to a node. """
        self.children.append(child)
        child.parent = self


@dataclass
class List(Node):
    pass


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
class NewLine(Space):
    data = '\n'


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
                node = to_node(tokens_to_combine)
                base_node.add_child(node)
                tokens_to_combine = []
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
        case Token(char='"') if in_comment == False:
            pass
        case Token(char="(") if in_comment == False:
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine)
                base_node.add_child(node)
                tokens_to_combine = []
            new_node = List.from_token(token)
            base_node.add_child(new_node)
            base_node = new_node
        case Token(char=")") if in_comment == False:
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine)
                base_node.add_child(node)
                tokens_to_combine = []
            base_node.add_child(EndList.from_token(token))
            base_node = base_node.parent
        case Token(char=' ') if in_comment == False:
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine)
                base_node.add_child(node)
                tokens_to_combine = []
            base_node.add_child(Space.from_token(token))
        case Token(_) if in_comment == False:
            if not in_symbol:
                in_symbol = True
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
    base_node = Node(0, 0, list(), None)
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
    return ast.base_node
