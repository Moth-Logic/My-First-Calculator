"""
gui/app.py
----------
Interfaz gráfica. Sabe DIBUJAR botones y leer clics; no sabe nada de
tokens, AST ni precedencia de operadores. Toda la aritmética se delega
al Calculator (core.calculator.Calculator).

Separar esto así es lo que nos permite, a futuro, cambiar toda esta
capa por una web app en JavaScript sin tocar core/ para nada.
"""

from __future__ import annotations

import customtkinter as ctk

from core import Calculator, CalculatorError

# --- Configuración visual global -----------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_BUTTON_LAYOUT = [
    ["sin", "cos", "tan", "π"],
    ["√", "log", "ln", "e"],
    ["asin", "acos", "atan", "^"],
    ["(", ")", "C", "←"],
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
]

_OPERATORS = {"/", "*", "-", "+", "^"}

# Mapeo de botones de la UI -> texto que se inserta en la expresión
_BTN_TEXT = {
    "sin": "sin(",
    "cos": "cos(",
    "tan": "tan(",
    "asin": "asin(",
    "acos": "acos(",
    "atan": "atan(",
    "√": "sqrt(",
    "log": "log(",
    "ln": "ln(",
    "π": "pi",
    "e": "e",
}


class CalculatorApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self._calculator = Calculator()
        self._expression = ""

        self.title("My First Calculator")
        self.geometry("320x640")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        self._build_display()
        self._build_buttons()
        self._bind_keyboard()

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_display(self) -> None:
        self._display = ctk.CTkLabel(
            self,
            text="0",
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="e",
            height=90,
            fg_color="#1e1e1e",
            corner_radius=12,
        )
        self._display.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="nsew")

    def _build_buttons(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, padx=16, pady=8, sticky="nsew")

        for r, row in enumerate(_BUTTON_LAYOUT):
            frame.grid_rowconfigure(r, weight=1)
            for c, label in enumerate(row):
                frame.grid_columnconfigure(c, weight=1)
                btn = ctk.CTkButton(
                    frame,
                    text=label,
                    font=ctk.CTkFont(size=20),
                    height=64,
                    fg_color=self._color_for(label),
                    command=lambda l=label: self._on_button(l),
                )
                btn.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")

    @staticmethod
    def _color_for(label: str) -> str:
        if label == "=":
            return "#2fa572"
        if label in ("C", "←"):
            return "#b3413a"
        if label in ("sin", "cos", "tan", "asin", "acos", "atan", "√", "log", "ln", "π", "e"):
            return "#5a3a8a"  # púrpura para funciones científicas
        if label in _OPERATORS or label in ("(", ")"):
            return "#3a3a3a"
        return "#4a4a4a"

    def _bind_keyboard(self) -> None:
        self.bind("<Return>", lambda _e: self._evaluate())
        self.bind("<BackSpace>", lambda _e: self._backspace())
        for char in "0123456789.+-*/()^":
            self.bind(char, lambda e, c=char: self._append(c))

    # ------------------------------------------------------------------
    # Lógica de interacción (delega TODO el cálculo al core)
    # ------------------------------------------------------------------

    def _on_button(self, label: str) -> None:
        if label == "C":
            self._clear()
        elif label == "←":
            self._backspace()
        elif label == "=":
            self._evaluate()
        elif label in _BTN_TEXT:
            self._append(_BTN_TEXT[label])
        else:
            self._append(label)

    def _append(self, char: str) -> None:
        self._expression += char
        self._display.configure(text=self._expression)

    def _clear(self) -> None:
        self._expression = ""
        self._display.configure(text="0")

    def _backspace(self) -> None:
        self._expression = self._expression[:-1]
        self._display.configure(text=self._expression or "0")

    def _evaluate(self) -> None:
        if not self._expression:
            return
        try:
            result = self._calculator.evaluate(self._expression)
            formatted = self._format_result(result)
            self._display.configure(text=formatted)
            self._expression = formatted
        except CalculatorError:
            self._display.configure(text="Error")
            self._expression = ""

    @staticmethod
    def _format_result(value: float) -> str:
        # Si el resultado es un entero exacto (ej. 4.0), muéstralo sin
        # decimales para que se sienta como una calculadora real.
        if value == int(value):
            return str(int(value))
        return f"{value:.10g}"


def main() -> None:
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
