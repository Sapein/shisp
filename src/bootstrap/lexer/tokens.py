"""
Shisp Tokenizer. 
"""

from dataclasses import dataclass

@dataclass(frozen=True, repr=True)
class Token:
    """
    A basic dataclass representing a token.
    """
    row: int
    column: int
    char: str


def parse_file(text: str) -> list[Token]:
    """
    Parse a file into a list of tokens.
    """
    text = text.replace('\r', '').replace('\n', '\n\r')
    lines = text.split('\r')
    tokenized = []
    for row, line in enumerate(lines, start=1):
        for column, char in enumerate(line, start=1):
            tokenized.append(Token(row, column, char))

    return tokenized
