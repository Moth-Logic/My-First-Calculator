"""
evaluator.py
------------
Recorre el AST (patrón Visitor simplificado) y produce el número final.

Este módulo intenta usar la implementación C++ (_evaluator_cpp) para
obtener máximo rendimiento. Si el módulo C++ no está compilado, cae
graciosamente al evaluator puro en Python.
"""

from __future__ import annotations

import math
from typing import ClassVar

from .lexer import TokenType
from .parser import ASTNode, BinaryOp, FunctionCall, Number, UnaryOp

# Intentar importar el backend C++
try:
    from ._evaluator_cpp import evaluate as _cpp_evaluate
    _HAS_CPP = True
except ImportError:
    _HAS_CPP = False


class EvaluationError(Exception):
    """División por cero, nodo desconocido, etc."""


class Evaluator:
    # Mapa de funciones científicas: nombre -> callable(float) -> float
    _FUNCTIONS: ClassVar[dict[str, callable]] = {
        # Trigonométricas (input en grados)
        "sin": lambda x: math.sin(math.radians(x)),
        "cos": lambda x: math.cos(math.radians(x)),
        "tan": lambda x: math.tan(math.radians(x)),
        "asin": lambda x: math.degrees(math.asin(x)),
        "acos": lambda x: math.degrees(math.acos(x)),
        "atan": lambda x: math.degrees(math.atan(x)),
        # Hiperbólicas
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        # Potencia / raíz
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
        "exp": math.exp,
        # Logaritmos
        "log": math.log10,   # log base 10
        "ln": math.log,     # logaritmo natural
        # Redondeo
        "ceil": math.ceil,
        "floor": math.floor,
        "round": round,
        # Otros
        "abs": abs,
    }

    def evaluate(self, node: ASTNode) -> float:
        # Usar el backend C++ si está disponible
        if _HAS_CPP:
            try:
                return _cpp_evaluate(node)
            except ValueError as exc:
                raise EvaluationError(str(exc)) from exc

        # Fallback: evaluador puro en Python
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
        if operator == TokenType.CARET:
            try:
                result = left ** right
            except OverflowError:
                raise EvaluationError("Resultado demasiado grande")
            return result
        if operator == TokenType.PERCENT:
            if right == 0:
                raise EvaluationError("Módulo por cero")
            return left % right
        raise EvaluationError(f"Operador desconocido: {operator}")
