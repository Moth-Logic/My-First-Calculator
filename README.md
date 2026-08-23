# My First Calculator

Calculadora de escritorio con interfaz gráfica moderna, hecha en Python.
Empieza simple (`+ - * /` con paréntesis) y hoy incluye funciones
científicas completas (trig, log, potencias, hiperbólicas, redondeo).
Está diseñada para seguir creciendo — próximas entregas van a sumar
memoria, historial, y piezas escritas en C++.

---

## Tabla de contenidos

1. [Requisitos previos](#1-requisitos-previos)
2. [Descargar el proyecto](#2-descargar-el-proyecto)
3. [Instalación](#3-instalación)
4. [Uso — correr la app desde código fuente](#4-uso--correr-la-app-desde-código-fuente)
5. [Cómo usar la calculadora](#5-cómo-usar-la-calculadora)
6. [Generar el .exe standalone](#6-generar-el-exe-standalone)
7. [Estructura del proyecto](#7-estructura-del-proyecto)
8. [Solución de problemas](#8-solución-de-problemas)
9. [Roadmap](#9-roadmap)

---

## 1. Requisitos previos

Necesitás **Python 3.10 o superior** instalado en Windows.

1. Descargalo de [python.org/downloads](https://www.python.org/downloads/).
2. Al instalar, **marcá la casilla "Add Python to PATH"** en la primera
   pantalla del instalador — si no la marcás, los comandos de abajo no
   van a funcionar desde la terminal.
3. Verificá la instalación abriendo **PowerShell** (o CMD) y corriendo:

   ```powershell
   python --version
   ```

   Deberías ver algo como `Python 3.12.x`. Si el comando no se reconoce,
   reiniciá la terminal (o la PC) después de instalar Python.

---

## 2. Descargar el proyecto

Si lo descargaste como `.zip`: extraelo en cualquier carpeta, por ejemplo
`C:\Users\TuUsuario\Documents\my_first_calculator`.

Si lo vas a manejar como repositorio Git desde el inicio:

```powershell
cd Documents
git init my_first_calculator
cd my_first_calculator
# copiá el contenido del zip acá dentro
git add .
git commit -m "Primera version: calculadora basica con GUI"
```

---

## 3. Instalación

Abrí PowerShell **dentro de la carpeta del proyecto** (click derecho →
"Abrir en Terminal", o `cd` hasta ahí) y corré:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Qué hace cada línea:

- `python -m venv venv` — crea un entorno virtual aislado (una copia
  local de Python solo para este proyecto, para no ensuciar tu Python
  global con dependencias).
- `venv\Scripts\activate` — activa ese entorno. Vas a ver `(venv)` al
  inicio de la línea de la terminal si funcionó.
- `pip install -r requirements.txt` — instala `customtkinter` (la
  librería de la interfaz) y `pyinstaller` (para generar el `.exe`).

> **Nota:** cada vez que abras una terminal nueva para trabajar en este
> proyecto, tenés que volver a correr `venv\Scripts\activate` primero.

---

## 4. Uso — correr la app desde código fuente

Con el entorno virtual activado (`(venv)` visible en la terminal):

```powershell
python main.py
```

Se abre la ventana de la calculadora. Cerrala como cualquier ventana de
Windows (la X de la esquina) para terminar el programa.

---

## 5. Cómo usar la calculadora

- **Botones numéricos** (`0`-`9`) y **`.`** para decimales.
- **Operadores**: `+`, `-`, `*`, `/`, `^` (potencia), `%` (módulo).
- **Paréntesis** `(` `)`: para agrupar operaciones, ej. `(2 + 3) * 4`.
- **Funciones científicas** (botones púrpura):
  - Trigonométricas: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
    (todas trabajan en **grados**).
  - Hiperbólicas: `sinh`, `cosh`, `tanh` (trabajan en radianes).
  - Raíces: `√` (raíz cuadrada).
  - Logaritmos: `log` (base 10), `ln` (natural).
  - Redondeo: `ceil`, `floor`, `round`.
  - Otros: `abs` (valor absoluto).
- **Constantes**: `π` (pi), `e` (euler).
- **`=`**: evalúa la expresión completa y muestra el resultado.
- **`C`**: borra todo (empezar de cero).
- **`←`**: borra el último carácter escrito.
- **Teclado físico**: todos los botones también funcionan con el
  teclado — números, `+ - * / ( ) ^ %`, `Enter` (=) y `Backspace` (←).

**Ejemplos de expresiones válidas:**

| Escribís                      | Resultado |
|-------------------------------|-----------|
| `2 + 3 * 4`                   | `14`      |
| `(2 + 3) * 4`                 | `20`      |
| `10 / 2 / 5`                  | `1`       |
| `2 * (3 + (4 - 1))`           | `12`      |
| `2^10`                         | `1024`    |
| `sin(30)`                      | `0.5`     |
| `cos(60)`                      | `0.5`     |
| `sqrt(16) + log(100)`          | `6`       |
| `ceil(3.2) * floor(4.8)`      | `12`      |
| `pi * 2`                       | `6.28...` |
| `10 % 3`                       | `1`       |
| `2^3^2`                        | `512`     |

Si escribís algo inválido (ej. `5 / 0` o paréntesis sin cerrar), la
pantalla muestra `Error` — apretá `C` y volvé a intentar.

---

## 6. Generar el .exe standalone

Esto empaqueta la app en **un solo archivo `.exe`** que corre en
cualquier PC con Windows, **sin necesidad de tener Python instalado**.
Ideal para compartir el programa con alguien más o entregarlo como
proyecto.

Con el entorno virtual activado:

```powershell
pyinstaller build.spec
```

Al terminar, el ejecutable queda en:

```
dist\MyFirstCalculator.exe
```

Podés mover ese único archivo a cualquier lado (Escritorio, un USB,
otra PC) y correrlo con doble click — no necesita el resto de la
carpeta del proyecto ni Python instalado.

> Este `.spec` ya fue probado (build + arranque de la GUI) antes de
> entregarte el proyecto, así que no debería haber sorpresas. Si algo
> falla, mirá la sección [Solución de problemas](#8-solución-de-problemas).

---

## 7. Estructura del proyecto

```
my_first_calculator/
├── core/                   <- 100% Python, sin dependencias de GUI
│   ├── lexer.py             string -> Tokens
│   ├── parser.py            Tokens -> AST (recursive descent, respeta precedencia)
│   ├── evaluator.py         AST -> float  (candidato a migrar a C++ a futuro)
│   └── calculator.py        Facade: une lexer + parser + evaluator
├── gui/
│   └── app.py                CustomTkinter — solo dibuja, delega todo el cálculo a core.Calculator
├── main.py                    Punto de entrada (python main.py)
├── build.spec                 Config de PyInstaller para generar el .exe
├── requirements.txt            Dependencias (customtkinter, pyinstaller)
└── README.md                   Este archivo
```

**Por qué está partido así (y no todo en un solo archivo):**

- `core/` no importa nada de `gui/`. El día de mañana se puede escribir
  un CLI, una API web, o correr tests sobre el core sin abrir ninguna
  ventana.
- `evaluator.py` está aislado a propósito: es el punto exacto donde,
  cuando llegue el momento de optimizar (matrices grandes, cálculo
  numérico pesado), se reemplaza por un módulo en C++ compilado con
  `pybind11`. El AST que produce `parser.py` es el "contrato" que cruza
  esa frontera — el resto del programa no se entera del cambio.
- El parser es recursive-descent real (no `eval()` de Python), porque
  `eval()` es un riesgo de seguridad y no enseña nada reusable para
  cursos de compiladores o para AXIOMA.

---

## 8. Solución de problemas

**"python no se reconoce como un comando"**
Python no quedó en el PATH. Reinstalalo marcando "Add Python to PATH",
o buscá "Python" en el instalador de Microsoft Store como alternativa.

**`pip install` falla con errores de permisos**
Asegurate de haber activado el entorno virtual (`venv\Scripts\activate`)
antes de instalar — así no necesitás permisos de administrador.

**La ventana no abre / se cierra sola al hacer doble click en el .exe**
Corré el `.exe` desde una terminal (`cmd` o PowerShell) en vez de doble
click, para ver el error real:
```powershell
cd dist
.\MyFirstCalculator.exe
```
Si no muestra nada porque `console=False` en `build.spec`, cambialo
temporalmente a `console=True`, volvé a correr `pyinstaller build.spec`,
y ejecutá de nuevo — ahí vas a ver el traceback completo.

**Antivirus/Windows Defender marca el .exe como sospechoso**
Es un falso positivo común con ejecutables generados por PyInstaller
(el empaquetado se parece, en estructura, al de algunos droppers de
malware, aunque el contenido sea inofensivo). Si pasa, agregá una
excepción para `dist\MyFirstCalculator.exe` en Windows Defender.

---

## 9. Roadmap

- [x] Potencias (`^`) —右结合, precedencia sobre `*` y `/`
- [x] Funciones científicas: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `sqrt`, `cbrt`, `log`, `ln`, `abs`, `exp`, `ceil`, `floor`, `round`
- [x] Constantes: `pi`, `e`
- [x] Modo "científica" (filas de botones púrpura)
- [x] Operador módulo (`%`) — misma precedencia que `*` y `/`
- [ ] Historial de operaciones
- [ ] Migrar `Evaluator` a C++ vía `pybind11`, benchmarking Python vs C++
- [ ] Variables/memoria (`M+`, `M-`, `MR`) — requiere una tabla de símbolos
- [ ] Números complejos / fracciones exactas (`Fraction` en vez de `float`)
- [ ] Modo grados / radianes toggle para funciones trigonométricas
