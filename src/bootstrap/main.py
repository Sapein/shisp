"""
This module is the 'main' module for the bootstrap compiler.
"""


import tokens
import parser


with open('test.shisp', 'r') as f:
    tokenized = tokens.parse_file(f.read())
    ast = parser.parse_tokens(tokenized)
    print(ast)
