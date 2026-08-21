"""
calculator.py
-------------
Fachada (Facade pattern). Une Lexer -> Parser -> Evaluator en una sola
función pública. La GUI (o cualquier futuro cliente: CLI, API web, tests)
solo necesita conocer esta clase, nunca los detalles internos.

Esto es lo que te permite, a futuro, tener:
    - GUI en JavaScript/Electron llamando a este core por subprocess o API
    - Evaluator reescrito en C++ vía pybind11
sin que el código que USA la calculadora tenga que cambiar una sola línea.
"""

from __future__ import annotations

from .evaluator import EvaluationError, Evaluator
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError

CalculatorError = (LexerError, ParserError, EvaluationError)


class Calculator:
    def __init__(self) -> None:
        self._evaluator = Evaluator()

    def evaluate(self, expression: str) -> float:
        """
        Evalúa un string matemático y devuelve el resultado como float.

        Lanza LexerError, ParserError o EvaluationError (todas
        capturables juntas como CalculatorError) si la expresión es
        inválida.
        """
        tokens = Lexer(expression).tokenize()
        ast = Parser(tokens).parse()
        return self._evaluator.evaluate(ast)
