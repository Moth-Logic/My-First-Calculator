"""
parser.py
---------
Parser recursivo-descendente clásico. Convierte la lista de Tokens en un
AST (Abstract Syntax Tree). Esta es la pieza que hace que "2 + 3 * 4"
se evalúe correctamente como 14 y no como 20, y que "(2 + 3) * 4" respete
los paréntesis.

Gramática (de menor a mayor precedencia):

    expression -> term ( ("+" | "-") term )*
    term       -> factor ( ("*" | "/") factor )*
    power      -> factor ("^" power)?
    factor     -> NUMBER | FUNCTION "(" expression ")" | "(" expression ")" | ("-" | "+") factor

Nota de diseño: el AST (Number, BinaryOp, UnaryOp) es el "contrato" entre
el Parser y el Evaluator. El día que reemplacemos el Evaluator por una
versión en C++ (vía pybind11), este árbol es la estructura de datos que
cruza la frontera Python <-> C++. Por eso vive separado y no mezcla
lógica de evaluación aquí.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from .lexer import Token, TokenType


class ParserError(Exception):
    """Error de sintaxis: paréntesis sin cerrar, token inesperado, etc."""


# ---------------------------------------------------------------------
# Nodos del AST
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class Number:
    value: float


@dataclass(frozen=True)
class BinaryOp:
    left: "ASTNode"
    operator: TokenType
    right: "ASTNode"


@dataclass(frozen=True)
class UnaryOp:
    operator: TokenType
    operand: "ASTNode"


@dataclass(frozen=True)
class FunctionCall:
    name: str
    argument: "ASTNode"


ASTNode = Union[Number, BinaryOp, UnaryOp, FunctionCall]


# ---------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------

class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    def parse(self) -> ASTNode:
        node = self._expression()
        if self._current().type != TokenType.EOF:
            raise ParserError(f"Token inesperado al final: {self._current()}")
        return node

    # expression -> term ( ("+" | "-") term )*
    def _expression(self) -> ASTNode:
        node = self._term()
        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self._advance().type
            node = BinaryOp(node, op, self._term())
        return node

    # term -> power ( ("*" | "/") power )*
    def _term(self) -> ASTNode:
        node = self._power()
        while self._current().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._advance().type
            node = BinaryOp(node, op, self._power())
        return node

    # power -> factor ("^" power)?  — right-associative (2^3^2 = 2^9)
    def _power(self) -> ASTNode:
        node = self._factor()
        if self._current().type == TokenType.CARET:
            self._advance()
            node = BinaryOp(node, TokenType.CARET, self._power())
        return node

    # factor -> NUMBER | FUNCTION "(" expression ")" | "(" expression ")" | ("-" | "+") factor
    def _factor(self) -> ASTNode:
        token = self._current()

        if token.type in (TokenType.PLUS, TokenType.MINUS):
            self._advance()
            return UnaryOp(token.type, self._factor())

        if token.type == TokenType.NUMBER:
            self._advance()
            return Number(token.value)  # type: ignore[arg-type]

        if token.type == TokenType.FUNCTION:
            func_name = token.value  # type: ignore[assignment]
            self._advance()
            self._expect(TokenType.LPAREN, f"Se esperaba '(' después de {func_name}")
            argument = self._expression()
            self._expect(TokenType.RPAREN, f"Se esperaba ')' después del argumento de {func_name}")
            return FunctionCall(func_name, argument)  # type: ignore[arg-type]

        if token.type == TokenType.LPAREN:
            self._advance()
            node = self._expression()
            self._expect(TokenType.RPAREN, "Se esperaba ')'")
            return node

        raise ParserError(f"Token inesperado: {token}")

    # -- helpers ---------------------------------------------------------

    def _current(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def _expect(self, type_: TokenType, message: str) -> Token:
        if self._current().type != type_:
            raise ParserError(f"{message} (encontrado: {self._current()})")
        return self._advance()
