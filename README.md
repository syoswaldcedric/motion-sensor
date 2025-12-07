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

- `app.py`: Main entry point of pyqt application.
- `tk_app.py`: Main entry point of the tkinter application.
- `requirements.txt`: List of Python dependencies.
- `*.ui`: User interface files designed with Qt Designer.

## Decisions

**UI Design:** QtCreator + PySide6

- unfortunately rasperypi 1b+ does not support pyqt6 and pyside6. We tried earlier versions of both pyqt and pyside but they did not work. so we decided to use tkinter.

pyqt_app.py is the main entry point for the pyqt application.

**Pros of Pyqt6:**

- Seamless integration with Qt Designer
- More features and customization

**Cons of Pyqt6:**

- Not supported on rasperypi 1b+

**TKinter:**
app.py is the main entry point for the tkinter application.

**Pros of Tkinter:**

- Supported on rasperypi 1b+

**Cons of Tkinter:**

- Less features and customization
- programming UI directly in code
- requires more code and time to achieve the same result

**Data Storage:**

1. Storage Format: (Excel/ Csv)

- Data is stored in a dictionary and then converted to a pandas DataFrame.
- The DataFrame is then saved to an Excel file using openpyxl.

Cons:

- Writing large files with thousands of rows may be slow or memory-heavy

2. Csv: if Excel format is not achievable, then we will save the data to a csv file.
