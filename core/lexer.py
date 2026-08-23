"""
lexer.py
--------
Responsabilidad única (SRP): convertir un string crudo ("3 + (4 * 2)")
en una lista de Tokens. No sabe nada de precedencia ni de aritmética.

Diseñado para ser reemplazado/extendido sin tocar el resto del sistema:
si mañana agregas potencias (^), módulo (%) o funciones (sin, cos),
el cambio vive aquí y en nada más.
"""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    LPAREN = auto()
    RPAREN = auto()
    FUNCTION = auto()  # sin, cos, tan, etc.
    COMMA = auto()
    CARET = auto()
    PERCENT = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: float | None = None  # solo relevante para NUMBER

    def __repr__(self) -> str:
        if self.value is not None:
            return f"Token({self.type.name}, {self.value})"
        return f"Token({self.type.name})"


class LexerError(Exception):
    """Se lanza cuando aparece un carácter que el lexer no reconoce."""


_SINGLE_CHAR_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ",": TokenType.COMMA,
    "^": TokenType.CARET,
    "%": TokenType.PERCENT,
}

# Funciones científicas y constantes reconocidas por el lexer
_SCIENTIFIC_FUNCTIONS = frozenset({
    # Trigonométricas
    "sin", "cos", "tan",
    "asin", "acos", "atan",
    # Hiperbólicas
    "sinh", "cosh", "tanh",
    # Potencia / raíz
    "sqrt", "cbrt",
    # Logaritmos
    "log", "ln",
    # Otros
    "abs", "exp", "ceil", "floor", "round",
})

_SCIENTIFIC_CONSTANTS = {
    "pi": 3.141592653589793,
    "e": 2.718281828459045,
}


class Lexer:
    def __init__(self, source: str) -> None:
        self._source = source
        self._pos = 0
        self._length = len(source)

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self._pos < self._length:
            char = self._source[self._pos]

            if char.isspace():
                self._pos += 1
                continue

            if char.isdigit() or char == ".":
                tokens.append(self._read_number())
                continue

            if char.isalpha() or char == "_":
                tokens.append(self._read_identifier())
                continue

            if char in _SINGLE_CHAR_TOKENS:
                tokens.append(Token(_SINGLE_CHAR_TOKENS[char]))
                self._pos += 1
                continue

            raise LexerError(f"Carácter inesperado '{char}' en la posición {self._pos}")

        tokens.append(Token(TokenType.EOF))
        return tokens

    def _read_identifier(self) -> Token:
        """Lee un identificador: puede ser una función (sin, cos...) o una
        constante (pi, e). El tipo de token resultante depende del nombre."""
        start = self._pos
        while self._pos < self._length and (
            self._source[self._pos].isalnum() or self._source[self._pos] == "_"
        ):
            self._pos += 1
        name = self._source[start:self._pos]
        name_lower = name.lower()

        if name_lower in _SCIENTIFIC_FUNCTIONS:
            return Token(TokenType.FUNCTION, name_lower)

        if name_lower in _SCIENTIFIC_CONSTANTS:
            return Token(TokenType.NUMBER, _SCIENTIFIC_CONSTANTS[name_lower])

        raise LexerError(f"Identificador desconocido '{name}' en la posición {start}")

    def _read_number(self) -> Token:
        start = self._pos
        seen_dot = False

        while self._pos < self._length:
            char = self._source[self._pos]
            if char.isdigit():
                self._pos += 1
            elif char == "." and not seen_dot:
                seen_dot = True
                self._pos += 1
            else:
                break

        raw = self._source[start:self._pos]
        return Token(TokenType.NUMBER, float(raw))
