# Pot_O-Note-Pad - a simple Notepad replacement written in Python

Pot_O-Note-Pad is a simple text editor built using Python 3.12, PyQt5, and QScintilla.

## Dependencies

To run Pot_O-Note-Pad, you need to install the following dependencies:

- Python 3.12
- PyQt5
- QScintilla

You can install these dependencies using pip:

```bash
pip install PyQt5 QScintilla
```

## Running the Software

To run Pot_O-Note-Pad, clone the repository:

```bash
git clone https://github.com/umarhasyimas/Pot_O-Note-Pad.git
cd Pot_O_Note_Pad_v0.0.1-beta.py
```

Then, execute the main Python script:

```bash
python Pot_O_Note_Pad_v0.0.1-beta.py
```

## Compiling the Software

To compile Pot_O-Note-Pad into a standalone executable, you can use PyInstaller. First, install PyInstaller if you haven't already:

```bash
pip install pyinstaller
```

Navigate to the directory containing your Pot_O-Note-Pad scripts and run PyInstaller:

```bash
pyinstaller --onefile Pot_O_Note_Pad_v0.0.1-beta.py
```

This will create a `dist` directory containing the standalone executable.

## Example

For example, assuming your main script is `Pot_O_Note_Pad_v0.0.1-beta.py`, the command to compile it with PyInstaller would be:

```bash
pyinstaller --onefile Pot_O_Note_Pad_v0.0.1-beta.py
```

---

Feel free to adjust the README to include more details about features, usage instructions, or any other relevant information specific to your software.
