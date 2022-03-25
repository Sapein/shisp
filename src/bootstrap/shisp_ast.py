"""
Contains all AST related stuff
"""

from typing import Optional, Any
from dataclasses import dataclass 

from tokens import Token


@dataclass
class AST:
    """
    Represents the Abstract Syntax Tree for the Shisp Program.
    """
    program_name: str
    base_node: "Expr"


    def print_children(self, node, indent=0):
        """
        Prints out the children of a node.
        """
        output = ''
        for child in node.children:
            for line in str(child).split('\n'):
                output = '{}{}|-- {}\n'.format(output, ' ' * indent, line)
            
            if child.children:
                response = self.print_children(child, indent+1)
                new_response = response
                output = '{}{}'.format(output, new_response)

        return output.replace('|-- \n', '|\n')[:-1]


    def print_ast(self):
        """
        Prints out the ast
        """
        base_node = str(self.base_node)
        base_node = '{}{}'.format(self.base_node,
                                    self.print_children(self.base_node))
        print(base_node)


@dataclass
class BaseNode:
    row: int | tuple[int] 
    column: int | tuple[int]
    children: list["Node"]
    parent: Optional["Node"]
 
    def __str__(self, *args, **kwargs):
        output = ('Type: {type}\n'
                  'Row:  {row}\n'
                  'Col:  {col}\n')
        return output.format(type=self.__class__.__name__, row=self.row, col=self.column)

@dataclass
class Node(BaseNode):
    data: Optional[Any] = None

    @classmethod
    def from_node(cls, node: "Node") -> "Node":
        return cls(node.row, node.column, list(), None, data=node.data)

    @classmethod
    def from_token(cls, token: Token) -> "Node":
        """ Turns a Token into a Node. """
        return cls(token.row, token.column, list(), None, data=token.char)

    @classmethod
    def from_tokens(cls, tokens: list[Token]) -> "Node":
        row = (tokens[0].row, tokens[-1].row)
        col = (tokens[0].column, tokens[-1].column)
        return cls(row, col, list(), None, data=''.join([t.char for t in tokens]))

    def replace_child(self, child, replacement):
        """ Replaces a child with another one """
        index = self.children.index(child)
        self.children.insert(index, replacement)
        self.children.remove(child)
        replacement.parent = self
        if not replacement.children:
            replacement.children = [c for c in child.children]
        for _child in child.children:
            _child.replace_parent(replacement)
        child.children.clear()

    def replace(self, replacement):
        self.parent.replace_child(self, replacement)

    def replace_parent(self, new_parent):
        self.parent = new_parent

    def add_child(self, child: "Node"):
        """ Adds a child to a node. """
        self.children.append(child)
        child.parent = self

    def add_children(self, children: list["Node"]):
        """ Adds children to a node. """
        for child in children:
            self.add_child(child)

@dataclass
class Expr(Node):
    scope: Optional["Scope"] = None
    def __str__(self, *args, **kwargs):
        base = super().__str__(*args, **kwargs)
        if self.scope is not None:
            return ('{}'
                    'Scope: {}\n'
                   ).format(base, list(self.scope.variables.keys()))
        return base

@dataclass
class MacroCall(BaseNode):
    macro: Node
    macro_name :str
    args: list
    body: "list"

    def __str__(self, *args, **kwargs):
        base = super().__str__(*args, **kwargs)
        output = ('{}'
                  'Name: {}\n'
                  'Args: {}\n')
        output = ('Type: {type}\n'
                  'Row:  {row}\n'
                  'Col:  {col}\n'
                  'Name: {name}\n')

        return output.format(type=self.__class__.__name__, row=self.row, col=self.column, name=self.macro_name)

    def switch_body(self):
        t = self.body
        self.body = self.children
        self.children = t

    def replace_child(self, child, replacement):
        """ Replaces a child with another one """
        match self.body:
            case [_]:
                if len(self.body) == 1:
                    self.body = [replacement]
                    replacement.parent = self
                elif len(self.body) > 1:
                    index = self.body.index(child)
                    self.body.insert(index, replacement)
                    self.body.remove(child)
                    replacement.parent = self

        if child in self.children:
            index = self.children.index(child)
            self.children.insert(index, replacement)
            self.children.remove(child)
            replacement.parent = self
            if not replacement.children:
                replacement.children = [c for c in child.children]
            for _child in child.children:
                _child.replace_parent(replacement)
            child.children.clear()


@dataclass
class Atom(Node):
    data: Optional[Any] = None

    def __str__(self, *args, **kwargs):
        base = super().__str__(*args, **kwargs)
        output = ('{}'
                  'Data: {}\n'
                 ).format(base, self.data)
        return output
    

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


@dataclass
class Space(Node):
    data = ' '


@dataclass
class Symbol(Atom):
    pass


@dataclass
class Comment(Atom):
    def __str__(self, *args, **kwargs):
        general = super().__str__(*args, **kwargs)
        general = '{}{}'.format(general, 'Data: {}'.format(self.data))
        return general


@dataclass
class Text(Atom):
    data: Optional[str] = None


@dataclass
class Number(Atom):
    data: Optional[int] = None


@dataclass
class DoubleQuote(Space):
    data = '"'


@dataclass
class NewLine(Space):
    data = '\n'


@dataclass
class String(Text):
    pass


@dataclass
class EndExpr(Space):
    data = ')'


@dataclass
class VariableRef(Node):
    pass

@dataclass
class FunctionCall(Node):
    is_pure: bool = False

@dataclass
class ReturnNode(Node):
    pass
