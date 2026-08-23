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

import math

from .lexer import TokenType
from .parser import ASTNode, BinaryOp, FunctionCall, Number, UnaryOp


class EvaluationError(Exception):
    """División por cero, nodo desconocido, etc."""


class Evaluator:
    # Mapa de funciones científicas: nombre -> callable(float) -> float
    _FUNCTIONS: dict[str, callable] = {
        # Trigonométricas (input en grados)
        "sin": lambda x: math.sin(math.radians(x)),
        "cos": lambda x: math.cos(math.radians(x)),
        "tan": lambda x: math.tan(math.radians(x)),
        "asin": lambda x: math.degrees(math.asin(x)),
        "acos": lambda x: math.degrees(math.acos(x)),
        "atan": lambda x: math.degrees(math.atan(x)),
        # Potencia / raíz
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
        "exp": math.exp,
        # Logaritmos
        "log": math.log10,   # log base 10
        "ln": math.log,     # logaritmo natural
        # Otros
        "abs": abs,
    }

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

        if isinstance(node, FunctionCall):
            return self._apply_function(node.name, node.argument)

        raise EvaluationError(f"Nodo AST desconocido: {node!r}")

    def _apply_function(self, name: str, argument: ASTNode) -> float:
        """Evalúa una función científica sobre un nodo AST."""
        value = self.evaluate(argument)
        func = self._FUNCTIONS.get(name)
        if func is None:
            raise EvaluationError(f"Función desconocida: {name}")
        try:
            result = func(value)
        except ValueError as exc:
            raise EvaluationError(f"Error en {name}({value}): {exc}") from exc
        except ZeroDivisionError as exc:
            raise EvaluationError(f"División por cero en {name}({value})") from exc
        return result

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
