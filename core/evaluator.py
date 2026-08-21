"""
evaluator.py
------------
Recorre el AST (patrón Visitor simplificado) y produce el número final.

*** ESTE es el módulo que en el futuro migraremos a C++ ***
Cuando lleguen operaciones pesadas (matrices, cálculo numérico intensivo,
o simplemente cuando quieras optimizar), esta clase es el punto exacto
de reemplazo: mismo AST de entrada, mismo float de salida. El resto del
programa (lexer, parser, GUI) no se entera del cambio.
"""

from __future__ import annotations

from .lexer import TokenType
from .parser import ASTNode, BinaryOp, Number, UnaryOp


class EvaluationError(Exception):
    """División por cero, nodo desconocido, etc."""


class Evaluator:
    def evaluate(self, node: ASTNode) -> float:
        if isinstance(node, Number):
            return node.value

        if isinstance(node, UnaryOp):
            value = self.evaluate(node.operand)
            return -value if node.operator == TokenType.MINUS else value

        if isinstance(node, BinaryOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            return self._apply(node.operator, left, right)

        raise EvaluationError(f"Nodo AST desconocido: {node!r}")

    @staticmethod
    def _apply(operator: TokenType, left: float, right: float) -> float:
        if operator == TokenType.PLUS:
            return left + right
        if operator == TokenType.MINUS:
            return left - right
        if operator == TokenType.STAR:
            return left * right
        if operator == TokenType.SLASH:
            if right == 0:
                raise EvaluationError("División entre cero")
            return left / right
        raise EvaluationError(f"Operador desconocido: {operator}")
