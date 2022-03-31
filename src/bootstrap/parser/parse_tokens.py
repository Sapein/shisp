"""
This module contains most of the logic for the
initial pass of the parser, which builds a rather
basic and rudimentary AST. 

We only need to make sure things are syntatically correct
at this stage.
"""

import re

import shisp_ast as sast


from ast_data import Scope
from contextlib import suppress
from dataclasses import dataclass
from typing import Optional, Any
from tokens import Token


def is_number(tokens: str) -> bool:
    """
    Checks to see if a collection of tokens is a 'number'
    for Shisp purposes.
    """
    return re.match('[0-9]+', tokens)


def is_symbol(tokens: str) -> bool:
    """
    Checks to see if a collection of tokens is a 'string'
    for Shisp purposes.
    """
    return re.match('[a-zA-Z\+\-\*\/]+[a-zA-Z0-9]*', tokens)


@dataclass
class ParserState:
    """
    This class exists just for us to track parser state.
    """
    tokens: list[Token]
    base_node: sast.Node

def handle_tokens(state: ParserState) -> tuple[sast.Atom | sast.Symbol | sast.Number, ParserState]:
    """
    Handles contexts where we need to deal with multiple tokens.

    It returns both Parser State *and* and the new node.

    The node may be sast.Atom, sast.Symbol, or sast.Number
    """
    if len(state.tokens) == 0:
        raise IndexError()
    if is_number(''.join([c.char for c in state.tokens])):
            return sast.Number.from_tokens(state.tokens), state
    elif is_symbol(''.join([c.char for c in state.tokens])):
        return sast.Symbol.from_tokens(state.tokens), state
    else:
        return sast.Atom.from_tokens(state.tokens), state

def handle_token(token: Token, state: ParserState) -> ParserState:
    basestr = isinstance(state.base_node, sast.String)
    basecom = isinstance(state.base_node, sast.Comment)
    match token:
        case Token(char='\n') if basestr:
            raise SyntaxError(("Newline can't be in String!\n"
                               "TODO: Better Errors"))
        case Token(char='\n') if basecom:
            state.tokens.append(token)
            state.base_node.data = ''.join([c.char for c in state.tokens])
            state.base_node = state.base_node.parent
            state.tokens.clear()

        case Token(char='\n'):
            with suppress(IndexError):
                node, state = handle_tokens(state)
                state.base_node.add_child(node)
                state.tokens.clear()
            state.base_node.add_child(sast.NewLine.from_token(token))

        case Token(char=' ') if not (basestr or basecom):
            with suppress(IndexError):
                node, state = handle_tokens(state)
                state.base_node.add_child(node)
                state.tokens.clear()
            state.base_node.add_child(sast.Space.from_token(token))

        case Token(char="'") if not (basestr or basecom):
            node = sast.SingleQuote.from_token(token)
            state.base_node.add_child(node)
        case Token(char='`') if not (basestr or basecom):
            node = sast.Backtick.from_token(token)
            state.base_node.add_child(node)
        case Token(char=',') if not (basestr or basecom):
            node = sast.Comma.from_token(token)
            state.base_node.add_child(node)
        case Token(char='@') if not (basestr or basecom):
            node = sast.At.from_token(token)
            state.base_node.add_child(node)

        case Token(char='"') if basestr:
            state.tokens.append(token)
            state.base_node.data = ''.join([c.char for c in state.tokens])
            state.base_node = state.base_node.parent
            state.tokens.clear()
        case Token(char='"') if not basestr:
            state.tokens.append(node)
            state.base_node.add_child(sast.String.from_token(token))
            state.base_node = state.base_node.children[-1]

        case Token(char=';') if not (basestr or basecom):
            node = sast.Comment.from_token(token)
            state.base_node.add_child(node)
            state.base_node = node

        case Token(char='(') if not (basestr or basecom):
            with suppress(IndexError):
                node, state = handle_tokens(state)
                state.base_node.add_child(node)
                state.tokens.clear()
            state.base_node.add_child(sast.Expr.from_token(token))
            state.base_node = state.base_node.children[-1]
        case Token(char=')') if not (basestr or basecom):
            with suppress(IndexError):
                node, state = handle_tokens(state)
                state.base_node.add_child(node)
                state.tokens.clear()
            state.base_node.add_child(sast.EndExpr.from_token(token))
            state.base_node = state.base_node.parent

        case Token(_):
            state.tokens.append(token)
    return state


def parse_tokens(text: list[Token]) -> sast.AST:
    """
    Parse a list of tokens into an AST
    """
    base_node = sast.Expr(0, 0, list(), None)
    ast = sast.AST(base_node)
    state = ParserState([], base_node)
    for token in text:
        state = handle_token(token, state)
    return ast
