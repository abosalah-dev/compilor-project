"""Lexical analyzer for a tiny compiler project language."""

import re

IDENTIFIER_TYPES = {"int", "float", "string", "double", "bool", "char"}
RESERVED_WORDS = {"for", "while", "if", "do", "return", "break", "continue", "end"}

MULTI_CHAR_SYMBOLS = {"&&": "And", "||": "Or"}
SINGLE_CHAR_SYMBOLS = {
    "+": "Operator",
    "-": "Operator",
    "/": "Operator",
    "%": "Operator",
    "*": "Operator",
    "(": "Open Bracket",
    ")": "Close Bracket",
    "{": "Open Curly Bracket",
    "}": "Close Curly Bracket",
    ",": "Comma",
    ";": "Semicolon",
    "<": "Less than",
    ">": "Greater than",
    "=": "Equal",
    "!": "Not",
}


def _classify_token(token):
    """Classify a raw token into a project-specific token type."""
    if token in IDENTIFIER_TYPES:
        return "Identifier"
    if token in RESERVED_WORDS:
        return "Reserved"
    if token in MULTI_CHAR_SYMBOLS:
        return MULTI_CHAR_SYMBOLS[token]
    if token in SINGLE_CHAR_SYMBOLS:
        return SINGLE_CHAR_SYMBOLS[token]
    if re.fullmatch(r"\d+(\.\d+)?", token):
        return "Number"
    if re.fullmatch(r"\".*?\"", token):
        return "String"
    if re.fullmatch(r"[A-Za-z_]\w*", token):
        return "Variable"
    return "Unknown"


def tokenize(code):
    """Tokenize source code and preserve line numbers for downstream phases."""
    if not code or not code.strip():
        return []

    tokens = []
    token_pattern = re.compile(
        r'"[^"\n]*"'  # string literals
        r"|&&|\|\|"  # multi-char symbols
        r"|\d+\.\d+|\d+"  # numbers
        r"|[A-Za-z_]\w*"  # identifiers and variables
        r"|[+\-/*%(){};,<>=!]"  # single-char symbols
        r"|[^\s]",  # unknown non-whitespace
    )

    for line_number, line in enumerate(code.splitlines(), start=1):
        for match in token_pattern.finditer(line):
            raw = match.group(0)
            tokens.append(
                {
                    "value": raw,
                    "type": _classify_token(raw),
                    "line": line_number,
                }
            )
    return tokens


def scan(code):
    """Public scanner API used by Flask route."""
    tokens = tokenize(code)
    # Keep external response minimal while semantic/memory can still call tokenize().
    return {"tokens": [{"value": t["value"], "type": t["type"]} for t in tokens]}
