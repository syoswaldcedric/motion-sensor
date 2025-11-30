# Motion Sensor Python Application: GUI

A Python GUI application for motion sensor monitoring, built with **PyQt6**.

## Prerequisites

- Python 3.x installed on your system.

## Setup

It is recommended to use a virtual environment to manage dependencies.

1.  **Create a virtual environment:**

    ```bash
    # Windows
    python -m venv .venv

    # Linux/macOS
    python3 -m venv .venv
    ```

2.  **Activate the virtual environment:**

    ```bash
    # Windows (PowerShell)
    .\.venv\Scripts\Activate

    # Windows (Command Prompt)
    .\.venv\Scripts\activate.bat

    # Linux/macOS
    source .venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To start the application, execute the `app.py` file:

```bash
python app.py
```

## Project Structure

- `app.py`: Main entry point of the application.
- `requirements.txt`: List of Python dependencies.
- `*.ui`: User interface files designed with Qt Designer.

## Decisions

UI Design: QtCreator + PySide6
