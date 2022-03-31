"""
This is the tokenizer.
"""

from dataclasses import dataclass

@dataclass(frozen=True, repr=True)
class Token:
    row: int
    column: int
    char: str

def parse_file(text: str):
    text = text.replace('\r', '').replace('\n', '\n\r')
    lines = text.split('\r')
    tokenized = []
    for row, line in enumerate(lines, start=1):
        for column, char in enumerate(line, start=1):
            tokenized.append(Token(row, column, char))
    return tokenized
