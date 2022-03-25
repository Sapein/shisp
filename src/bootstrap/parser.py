"""
Parser
"""

import re

from shisp_ast import *
from ast_data import *
from dataclasses import dataclass
from typing import Optional, Any
from tokens import Token

def to_node(tokens: list[Token], in_string=False) -> Node:
    """
    Parses a list of Tokens to a singular Node.
    """
    symbol = ''.join([t.char for t in tokens])
    if re.match('[a-zA-Z\+\-\*\/]+[a-zA-Z0-9]*', symbol) and not in_string:
        return Symbol.from_tokens(tokens)
    elif re.match('[^\"]', symbol) and in_string:
        return Symbol.from_tokens(tokens)
    elif re.match('[0-9]+', symbol):
        return Number.from_tokens(tokens)
    return Node.from_tokens(tokens)


def match_tokens(token: Token, base_node: Node, context=(False, False, False), tokens_to_combine=None):
    in_symbol, in_comment, in_string = context
    if tokens_to_combine is None:
        tokens_to_combine = []
    match token:
        case Token(char='\n'):
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine, in_string)
                base_node.add_child(node)
                tokens_to_combine = []
            if in_comment == True:
                in_symbol = False
                in_comment = False
                if tokens_to_combine:
                    node = to_node(tokens_to_combine, in_string)
                    base_node.add_child(node)
                    tokens_to_combine = []
            if in_string == True:
                raise SyntaxError("String can not pass newline!\nTODO: Better Error")
            base_node.add_child(NewLine.from_token(token))
            match base_node:
                case Comment(_):
                    base_node = base_node.parent
        case Token(char=';') if in_comment == False:
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine, in_comment)
                base_node.add_child(node)
                tokens_to_combine = []

            node = Comment.from_token(token)
            base_node.add_child(node)
            base_node = node
            in_comment = True 
        case Token(char='"') if in_comment == False and in_string == False:
            if in_symbol == True:
                raise SyntaxError('{}" not a valid symbol!\nTODO: Better Error'.format(''.join(tokens_to_combine)))
            in_string = True
            tokens_to_combine.append(token)
        case Token(char='"') if in_string == True:
            in_string = False
            tokens_to_combine.append(token)
            base_node.add_child(String.from_tokens(tokens_to_combine))
            tokens_to_combine = []
        case Token(char='"') if in_comment == True:
            if tokens_to_combine:
                base_node.add_child(to_node(tokens_to_combine, in_comment))
                tokens_to_combine = []
            base_node.add_child(DoubleQuote.from_token(token))
        case Token(char="(") if in_comment == False and in_string == False:
            if in_symbol == True:
                raise SyntaxError("{}( not a valid symbol!\nTODO: Better Error".format(''.join(tokens_to_combine)))
            new_node = Expr.from_token(token)
            base_node.add_child(new_node)
            base_node = new_node
        case Token(char=")") if in_comment == False and in_string == False:
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine, in_comment)
                base_node.add_child(node)
                tokens_to_combine = []
            base_node.add_child(EndExpr.from_token(token))
            base_node = base_node.parent
        case Token(char=' ') if in_comment == False and in_string == False:
            if in_symbol == True:
                in_symbol = False
                node = to_node(tokens_to_combine, in_comment)
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
                base_node.add_child(to_node(tokens_to_combine, in_comment))
                tokens_to_combine = []
            base_node.add_child(Space.from_token(token))
        case Token(_) if in_comment == True:
            tokens_to_combine.append(token)
    return base_node, (in_symbol, in_comment, in_string), tokens_to_combine

def parse_tokens(text: list[Token], program_name="test.shisp") -> AST:
    """
    Parse a list of tokens into an AST
    """
    base_node = Expr(0, 0, list(), None, scope=Scope())
    ast = AST(program_name, base_node)
    tokens_to_combine = []
    context = (False, False, False)
    for token in text:
        base_node, context, tokens_to_combine = match_tokens(token, base_node, context, tokens_to_combine)
    if tokens_to_combine:
        node = to_node(tokens_to_combine, context[1])
        base_node.add_child(node)
    return ast
