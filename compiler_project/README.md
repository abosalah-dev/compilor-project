# Compiler Simulation Project

This is a web-based educational simulation of compiler phases built with Python and Flask. It provides a GUI to input simple code and step through various phases of compilation and execution.

## Features

- **Lexical Analysis (Scanner)**: Tokenizes source code into identifiers, keywords, symbols, variables, strings, and numbers.
- **Semantic Analysis**: Performs type checking, variable declaration checks, and basic semantic validation.
- **Memory/Execution Simulator**: Simulates the execution of assignment statements and tracks memory states (variable values) step-by-step.
- **Web-based GUI**: A single-page application interface for interacting with the compiler phases.

## Project Structure

- `app.py`: The main Flask application exposing endpoints for the GUI and compiler phases (`/scan`, `/analyze`, `/execute`).
- `scanner.py`: Contains the lexical analyzer (`tokenize` and `scan` functions).
- `semantic.py`: Contains semantic analysis logic for the source code.
- `memory.py`: Simulates code execution and tracks memory states.
- `static/` & `templates/`: Contains the frontend assets (HTML, CSS, JS).

## Requirements

- Python 3.x
- Flask

## Installation

1. Ensure you have Python installed.
2. Install the required dependencies:
   ```bash
   pip install Flask
   ```

## Running the Project

1. Navigate to the project directory:
   ```bash
   cd "d:\my problems\compilor-project\compiler_project"
   ```
2. Start the Flask server:
   ```bash
   python app.py
   ```
3. Open your web browser and go to `http://127.0.0.1:5000/`.

## Language Syntax Supported

This simple compiler supports basic assignments and expressions:
- **Types**: `int`, `float`, `string`, `double`, `bool`, `char`
- **Keywords**: `for`, `while`, `if`, `do`, `return`, `break`, `continue`, `end`
- **Operators**: `+`, `-`, `/`, `%`, `*`, `<`, `>`, `=`, `!`, `&&`, `||`

Enjoy exploring how compilers work!
