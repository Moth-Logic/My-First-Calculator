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

# === C++ Backend (optional performance optimization) ===
# If the C++ extension module is compiled, we use it for faster evaluation.
# If not, we fall back to pure Python (graceful degradation).
try:
    from ._evaluator_cpp import evaluate as _cpp_evaluate
    _HAS_CPP = True  # C++ backend available — use it!
except ImportError:
    _HAS_CPP = False  # No C++ module — use pure Python instead


class EvaluationError(Exception):
    """Raised when evaluation fails (division by zero, unknown node, etc.)."""


class Evaluator:
    # Map of function names to their Python implementations.
    # These are called when the evaluator encounters a FunctionCall node.
    # Note: trig functions input degrees (not radians) — we convert internally.
    _FUNCTIONS: ClassVar[dict[str, callable]] = {
        # Trigonometric functions (input in degrees, converted to radians internally)
        "sin": lambda x: math.sin(math.radians(x)),
        "cos": lambda x: math.cos(math.radians(x)),
        "tan": lambda x: math.tan(math.radians(x)),
        "asin": lambda x: math.degrees(math.asin(x)),
        "acos": lambda x: math.degrees(math.acos(x)),
        "atan": lambda x: math.degrees(math.atan(x)),
        # Hyperbolic functions (input in radians)
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        # Power and roots
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),  # Preserves sign for negatives
        "exp": math.exp,
        # Logarithms
        "log": math.log10,   # log base 10
        "ln": math.log,      # natural log (base e)
        # Rounding
        "ceil": math.ceil,
        "floor": math.floor,
        "round": round,
        # Other
        "abs": abs,
    }

    def evaluate(self, node: ASTNode) -> float:
        """Walk the AST recursively and compute the final numeric result.
        
        Each node type has its own handling:
        - Number: just return its value
        - UnaryOp: negate the operand (for -5, +3, etc.)
        - BinaryOp: evaluate both sides and apply the operator
        - FunctionCall: evaluate the argument, then apply the function
        """
        # Use the C++ backend if available (much faster for complex expressions)
        if _HAS_CPP:
            try:
                return _cpp_evaluate(node)
            except ValueError as exc:
                raise EvaluationError(str(exc)) from exc

        # === Pure Python fallback ===
        if isinstance(node, Number):
            return node.value  # Base case: numbers just return their value

        if isinstance(node, UnaryOp):
            value = self.evaluate(node.operand)  # Recursively evaluate the operand
            return -value if node.operator == TokenType.MINUS else value

        if isinstance(node, BinaryOp):
            left = self.evaluate(node.left)    # Evaluate the left side
            right = self.evaluate(node.right)  # Evaluate the right side
            return self._apply(node.operator, left, right)  # Apply the operator

        if isinstance(node, FunctionCall):
            return self._apply_function(node.name, node.argument)

        raise EvaluationError(f"Nodo AST desconocido: {node!r}")

    def _apply_function(self, name: str, argument: ASTNode) -> float:
        """Evaluate a scientific function on an AST node.
        
        Looks up the function name in the _FUNCTIONS map, evaluates
        the argument, and applies the function. Handles errors gracefully.
        """
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
        """Apply a binary operator to two numbers and return the result.
        
        Handles: +, -, *, /, ^ (power), % (modulo).
        Raises EvaluationError for division by zero or unknown operators.
        """
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
                raise EvaluationError("Resultado demasiado grande")  # e.g., 999^999
            return result
        if operator == TokenType.PERCENT:
            if right == 0:
                raise EvaluationError("Módulo por cero")
            return left % right
        raise EvaluationError(f"Operador desconocido: {operator}")
