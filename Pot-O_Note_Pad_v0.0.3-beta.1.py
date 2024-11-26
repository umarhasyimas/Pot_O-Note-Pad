import subprocess
import sys
from pathlib import Path
import os
import textwrap
from PyQt5.QtCore import QSize, Qt, QCoreApplication, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QMenu, QMessageBox, QFontDialog, QPushButton, QVBoxLayout, QWidget, QDialog, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QIcon, QColor, QFont, QImage
from PyQt5.Qsci import QsciDocument, QsciPrinter, QsciScintilla, QsciLexerPython, QsciLexerCSS, QsciLexerHTML, QsciLexerJavaScript, QsciLexerBatch, QsciLexerXML, QsciLexerCustom
import win32print
import win32api
from enum import Enum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from find_replace_dialog import FindReplaceDialog

# Get the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent

class FoldingStyle(Enum):
    EXTENDED_FOLDING_STYLE = QsciScintilla.SC_FOLDACTION_EXPAND
    FOLDING_STYLE = QsciScintilla.SCI_FOLDDISPLAYTEXTSETSTYLE
    BOXED_TREE_FOLDING_STYLE = QsciScintilla.SC_FOLDDISPLAYTEXT_BOXED
    NO_FOLDING_STYLE = QsciScintilla.SC_FOLDDISPLAYTEXT_HIDDEN

class LexerVaraq(QsciLexerCustom):
    def __init__(self, parent=None):
        super(LexerVaraq, self).__init__(parent)
        self.keywords = set([
            "woD", "latlh", "tam", "chImmoH", "qaw", "qawHa'", "Hotlh", "pong", "cher", "HIja'",
            "chugh", "ghobe'", "wIv", "chov", "nargh", "vangqa'", "SIj", "muv", "ghorqu'", "chIm'",
            "tlheghrar", "naQmoH", "tlheghrap", "tlheghpe'", "tlheghjuv", "jor", "boq", "boqHa'",
            "boq'egh", "HabboqHa'egh", "chuv", "boqHa'", "qa'", "loS'ar", "wa'", "boq", "wa'boqHa'",
            "joq", "joqHa'", "qojmI'", "qojHa'", "ghurtaH", "maHghurtaH", "wejghurtaH", "poD",
            "Hab'ar", "mIScher", "mIS", "HeHmI'", "ghurmI'", "HabmI'", "mI'", "mI'", "mI'",
            "moH", "mobmoH", "DuD", "tlhoch", "Qo'moH", "nIHghoS", "poSghoS", "law'", "puS'",
            "rap'", "law'rap'", "rapbe'", "pagh'", "taH", "je", "joq", "ghap", "ghobe'", "cha'",
            "'Ij", "bep", "chu'", "DonwI'", "chu'tut", "nuqDaq_jIH", "pongmI'", "taghDe'"
            # Add Python keywords
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else",
            "except", "finally", "for", "from", "global", "if", "import",
            "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise",
            "return", "try", "while", "with", "yield"
        ])

    def language(self):
        return "Varaq"

    def description(self, style):
        if style == 1:
            return "Keyword"
        elif style == 2:
            return "Comment"
        elif style == 3:
            return "String"
        elif style == 4:
            return "Number"
        elif style == 5:
            return "Identifier"
        return "Default"

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        text = bytearray(end - start)
        editor.SendScintilla(editor.SCI_GETTEXTRANGE, start, end, text)

        i = 0
        state = 0
        length = len(text)

        while i < length:
            ch = chr(text[i])

            if state == 0:
                if ch.isdigit() or (ch == '-' and i + 1 < length and chr(text[i + 1]).isdigit()):
                    editor.SendScintilla(editor.SCI_STARTSTYLING, start + i, 0xFF)
                    editor.SendScintilla(editor.SCI_SETSTYLING, 1, 4)
                    state = 4
                elif ch == '"':
                    editor.SendScintilla(editor.SCI_STARTSTYLING, start + i, 0xFF)
                    editor.SendScintilla(editor.SCI_SETSTYLING, 1, 3)
                    state = 3
                elif ch.isalpha() or ch == "'":
                    editor.SendScintilla(editor.SCI_STARTSTYLING, start + i, 0xFF)
                    editor.SendScintilla(editor.SCI_SETSTYLING, 1, 5)
                    state = 5
                elif ch == '(' and i + 1 < length and chr(text[i + 1]) == '*':
                    editor.SendScintilla(editor.SCI_STARTSTYLING, start + i, 0xFF)
                    editor.SendScintilla(editor.SCI_SETSTYLING, 1, 2)
                    state = 2
                else:
                    editor.SendScintilla(editor.SCI_STARTSTYLING, start + i, 0xFF)
                    editor.SendScintilla(editor.SCI_SETSTYLING, 1, 0)
            elif state == 4:
                if not ch.isdigit() and ch != '.':
                    state = 0
                    continue
                editor.SendScintilla(editor.SCI_SETSTYLING, 1, 4)
            elif state == 3:
                editor.SendScintilla(editor.SCI_SETSTYLING, 1, 3)
                if ch == '"':
                    state = 0
            elif state == 5:
                if not (ch.isalpha() or ch == "'"):
                    word = text[start:i].decode('utf-8')
                    if word in self.keywords:
                        editor.SendScintilla(editor.SCI_STARTSTYLING, start + i - len(word), 0xFF)
                        editor.SendScintilla(editor.SCI_SETSTYLING, len(word), 1)
                    state = 0
                    continue
                editor.SendScintilla(editor.SCI_SETSTYLING, 1, 5)
            elif state == 2:
                editor.SendScintilla(editor.SCI_SETSTYLING, 1, 2)
                if ch == '*' and i + 1 < length and chr(text[i + 1]) == ')':
                    i += 1
                    editor.SendScintilla(editor.SCI_SETSTYLING, 1, 2)
                    state = 0
            i += 1

    def fold(self, start, end, initStyle, bufferAccess):
        editor = self.editor()
        if editor is None:
            return

        # Get the line of the current position
        lineCurrent = editor.SendScintilla(editor.SCI_LINEFROMPOSITION, start)

        levelPrev = editor.SendScintilla(editor.SCI_GETFOLDLEVEL, lineCurrent) & 0xFFFF
        levelCurrent = levelPrev

        # Check lines for foldable blocks based on keywords or indentation
        for line in range(lineCurrent, editor.lines()):
            line_text = editor.text(line).strip()

            # Increase fold level if a function, class, or control statement starts
            if line_text.startswith(("def", "class", "if", "else", "elif", "for", "while", "try", "except")):
                levelCurrent += 1
                editor.SendScintilla(editor.SCI_SETFOLDLEVEL, line, levelCurrent | QsciScintilla.SC_FOLDLEVELHEADERFLAG)
            elif line_text == "":
                # Decrease fold level for empty lines (which usually indicate block end in Python)
                levelCurrent -= 1
                editor.SendScintilla(editor.SCI_SETFOLDLEVEL, line, levelCurrent)

            levelPrev = levelCurrent

class PotONotePad(QMainWindow):
    def __init__(self, file_path=None):
        super().__init__()
        self.current_file = file_path
        self.unsaved_changes = False  # Track unsaved changes
        self.initUI()
        if self.current_file:
            self.open_file(self.current_file)

    def initUI(self):
        # Initialize editor widget
        self.editor = QsciScintilla()
        self.setCentralWidget(self.editor)
        self.findReplaceDialog = FindReplaceDialog(self)
        
        self.current_file = None
        
        # Setup folding
        self.setup_folding()

        # Set default font for editor
        font = QFont('Consolas', 12)  # Example: Consolas, 10 points
        self.editor.setFont(font)
        font.setFixedPitch(True)

        # Initialize lexers for different languages
        self.initLexers()

        # Set up additional features
        self.editor.setUtf8(True)
        self.editor.setMargins(1)
        self.setup_folding()
        self.setup_line_numbering()
        self.setup_auto_indentation()
        self.editor.setMarginWidth(1, 25)
        self.editor.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        lexer = LexerVaraq()
        self.editor.setLexer(lexer)

        # Create actions and menu
        self.create_actions()
        self.create_menu()

        # Set window properties
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Pot-O Note Pad v0.0.3-beta.3')
        self.setWindowIcon(QIcon(str(BASE_DIR / 'images' / 'pea.png')))
        
        # Calculate center position of the screen
        screen_geometry = QCoreApplication.instance().desktop().availableGeometry()
        x = int((screen_geometry.width() - self.width()) / 2)
        y = int((screen_geometry.height() - self.height()) / 2)
        self.move(x, y)  # Move the window to the calculated center position
        
        self.editor.textChanged.connect(self.on_text_changed)
        
        # Connect the textChanged signal to update the title
        self.editor.textChanged.connect(self.update_title_bar)

        # Status bar
        self.statusBar()

        # Connect signals
        self.editor.textChanged.connect(self.update_status_bar)
        self.editor.cursorPositionChanged.connect(self.update_status_bar)

        self.update_status_bar()  # Initial update
        
    def initLexers(self):
        # Initialize lexers
        self.lexer_python = QsciLexerPython(self)
        self.lexer_js = QsciLexerJavaScript(self)
        self.lexer_html = QsciLexerHTML(self)
        self.lexer_css = QsciLexerCSS(self)
        self.lexer_batch = QsciLexerBatch(self)
        self.lexer_xml = QsciLexerXML(self)

    def setup_folding(self):
        # Enable folding with BoxedTree style
        self.editor.setFolding(QsciScintilla.BoxedTreeFoldStyle)

        # Define folding margin width (the space where the fold markers will appear)
        self.editor.setMarginWidth(2, 20)

        # Set fold margin colors
        self.editor.setFoldMarginColors(QColor("#99CC99"), QColor("#D3D3D3"))

        # Define markers for folding (folding plus and minus signs)
        self.editor.markerDefine(QsciScintilla.SC_MARKNUM_FOLDER, QsciScintilla.SC_MARK_PLUS)
        self.editor.markerDefine(QsciScintilla.SC_MARKNUM_FOLDEROPEN, QsciScintilla.SC_MARK_MINUS)

        # Assign the custom lexer for Varaq
        lexer = LexerVaraq(self.editor)
        self.editor.setLexer(lexer)

    def set_language(self, language):
        if language == "Python":
            lexer = QsciLexerPython()
        elif language == "JavaScript":
            lexer = QsciLexerJavaScript()
        elif language == "Batch":
            lexer = QsciLexerBatch()
        elif language == "HTML":
            lexer = QsciLexerHTML()
        elif language == "CSS":
            lexer = QsciLexerCSS()
        elif language == "XML":
            lexer = QsciLexerXML()
        else:
            lexer = None  # Default lexer

        if lexer:
            lexer.setFoldComments(True)
            lexer.setFoldCompact(False)
            self.editor.setLexer(lexer)
            
    def create_lexer_actions(self):
        lexers = {
            "Python": QsciLexerPython,
            "JavaScript": QsciLexerJavaScript,
            "Batch": QsciLexerBatch,
            "HTML": QsciLexerHTML,
            "CSS": QsciLexerCSS,
            "XML": QsciLexerXML
        }

        for language, lexer_class in lexers.items():
            action = QAction(QIcon(str(BASE_DIR / f'images/{language.lower()}-48.png')), language, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, l=lexer_class: self.set_language(language))
            self.menuBar().addMenu('&Lexer').addAction(action)

    def setup_line_numbering(self):
        # Enable line numbers
        self.editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.editor.setMarginWidth(0, 40)
        self.editor.setMarginsForegroundColor(QColor("#000000"))
        self.editor.setMarginsBackgroundColor(QColor("#D3D3D3"))

    def setup_auto_indentation(self):
        self.editor.setAutoIndent(True)
        self.editor.setIndentationsUseTabs(True)  # Use spaces for indentation
        self.editor.setTabWidth(4)  # Set tab width to 4 spaces
        self.editor.setBackspaceUnindents(True)
        
    def on_margin_clicked(self, margin, line, modifiers):
        print(f"Margin clicked: {margin}, Line: {line}, Modifiers: {modifiers}")
        self.editor.foldLine(line)

    def create_actions(self):
        self.new_action = QAction(QIcon(str(BASE_DIR / 'images' / 'new-document-48.png')), 'New', self)
        self.new_action.setShortcut('Ctrl+N')
        self.new_action.setStatusTip('Create a new file')
        self.new_action.triggered.connect(self.new_file)

        self.open_action = QAction(QIcon(str(BASE_DIR / 'images' / 'opened-folder-48.png')), 'Open', self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.setStatusTip('Open an existing file')
        self.open_action.triggered.connect(self.open_file_dialog)

        self.save_action = QAction(QIcon(str(BASE_DIR / 'images' / 'save-48.png')), 'Save', self)
        self.save_action.setShortcut('Ctrl+S')
        self.save_action.setStatusTip('Save the current file')
        self.save_action.triggered.connect(self.save_file)
        
        # Print action
        self.print_action = QAction(QIcon(str(BASE_DIR / 'images' / 'print-48.png')), 'Print', self)
        self.print_action.setShortcut('Ctrl+P')
        self.print_action.setStatusTip('Print the current file')
        self.print_action.triggered.connect(self.print_dialog)

        self.exit_action = QAction(QIcon(str(BASE_DIR / 'images' / 'close-window-48.png')), 'Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit application')
        self.exit_action.triggered.connect(self.exit_app)
        
        self.undo_action = QAction(QIcon(str(BASE_DIR / 'images' / 'undo-48.png')), 'Undo', self)
        self.undo_action.setShortcut('Ctrl+Z')
        self.undo_action.setStatusTip('Undo')
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction(QIcon(str(BASE_DIR / 'images' / 'redo-48.png')), 'Redo', self)
        self.redo_action.setShortcut('Ctrl+Y')
        self.redo_action.setStatusTip('Redo')
        self.redo_action.triggered.connect(self.editor.redo)
        
        self.find_replace_action = QAction(QIcon(str(BASE_DIR / 'images' / 'find-and-replace-48.png')), 'Find and Replace', self)
        self.find_replace_action.setShortcut('Ctrl+F')
        self.find_replace_action.setStatusTip('Find and Replace')
        self.find_replace_action.triggered.connect(self.showFindReplaceDialog)
        
        self.change_font_action = QAction(QIcon(str(BASE_DIR / 'images' / 'choose-font-48.png')), 'Change Font', self)
        self.change_font_action.setStatusTip('Change the editor font')
        self.change_font_action.triggered.connect(self.change_font)

        self.toggle_wrap_action = QAction(QIcon(str(BASE_DIR / 'images' / 'hide-sidepanel-48.png')), 'Toggle Line Wrapping', self)
        self.toggle_wrap_action.setStatusTip('Toggle line wrapping')
        self.toggle_wrap_action.setCheckable(True)
        self.toggle_wrap_action.triggered.connect(self.toggle_line_wrapping)
        
        # Create actions for line wrapping
        self.wrap_none_action = QAction('No Wrap', self, checkable=True)
        self.wrap_none_action.triggered.connect(self.set_wrap_mode_none)

        self.wrap_word_action = QAction('Wrap Word', self, checkable=True)
        self.wrap_word_action.triggered.connect(self.set_wrap_mode_word)

        self.wrap_character_action = QAction('Wrap Character', self, checkable=True)
        self.wrap_character_action.triggered.connect(self.set_wrap_mode_character)

        self.wrap_whitespace_action = QAction('Wrap Whitespace', self, checkable=True)
        self.wrap_whitespace_action.triggered.connect(self.set_wrap_mode_whitespace)
        
        self.cut_action = QAction(QIcon(str(BASE_DIR / 'images' / 'cut-48.png')), 'Cut', self)
        self.cut_action.setShortcut('Ctrl+X')
        self.cut_action.setStatusTip('Cut selected text')
        self.cut_action.triggered.connect(self.editor.cut)

        self.copy_action = QAction(QIcon(str(BASE_DIR / 'images' / 'copy-48.png')), 'Copy', self)
        self.copy_action.setShortcut('Ctrl+C')
        self.copy_action.setStatusTip('Copy selected text')
        self.copy_action.triggered.connect(self.editor.copy)

        self.paste_action = QAction(QIcon(str(BASE_DIR / 'images' / 'paste-48.png')), 'Paste', self)
        self.paste_action.setShortcut('Ctrl+V')
        self.paste_action.setStatusTip('Paste text from clipboard')
        self.paste_action.triggered.connect(self.editor.paste)

        self.lexer_python_action = QAction(QIcon(str(BASE_DIR / 'images' / 'python-48.png')), 'Python', self)
        self.lexer_python_action.setStatusTip('Set lexer to Python')
        self.lexer_python_action.setCheckable(True)
        self.lexer_python_action.triggered.connect(lambda: self.set_lexer("Python"))

        self.lexer_js_action = QAction(QIcon(str(BASE_DIR / 'images' / 'javascript-48.png')), 'JavaScript', self)
        self.lexer_js_action.setStatusTip('Set lexer to JavaScript')
        self.lexer_js_action.setCheckable(True)
        self.lexer_js_action.triggered.connect(lambda: self.set_lexer("JavaScript"))
        
        self.lexer_batch_action = QAction(QIcon(str(BASE_DIR / 'images' / 'batch-script-48.png')), 'Batch', self)
        self.lexer_batch_action.setStatusTip('Set lexer to Batch')
        self.lexer_batch_action.setCheckable(True)
        self.lexer_batch_action.triggered.connect(lambda: self.set_lexer("Batch"))
        
        self.lexer_xml_action = QAction(QIcon(str(BASE_DIR / 'images' / 'xml-file-48.png')), 'XML', self)
        self.lexer_xml_action.setStatusTip('Set lexer to XML')
        self.lexer_xml_action.setCheckable(True)
        self.lexer_xml_action.triggered.connect(lambda: self.set_lexer("XML"))

        self.lexer_html_action = QAction(QIcon(str(BASE_DIR / 'images' / 'html-48.png')), 'HTML', self)
        self.lexer_html_action.setStatusTip('Set lexer to HTML')
        self.lexer_html_action.setCheckable(True)
        self.lexer_html_action.triggered.connect(lambda: self.set_lexer("HTML"))

        self.lexer_css_action = QAction(QIcon(str(BASE_DIR / 'images' / 'css-48.png')), 'CSS', self)
        self.lexer_css_action.setStatusTip('Set lexer to CSS')
        self.lexer_css_action.setCheckable(True)
        self.lexer_css_action.triggered.connect(lambda: self.set_lexer("CSS"))

        self.show_info_action = QAction(QIcon(str(BASE_DIR / 'images' / 'info-48.png')), 'Show Data Info', self)
        self.show_info_action.setStatusTip('Show text information')
        self.show_info_action.triggered.connect(self.show_text_info)

        self.fold_all_action = QAction(QIcon(str(BASE_DIR / 'images' / 'fold-48.png')), 'Fold All', self)
        self.fold_all_action.setStatusTip('Fold all code blocks')
        self.fold_all_action.triggered.connect(self.fold_all)

        self.unfold_all_action = QAction(QIcon(str(BASE_DIR / 'images' / 'more-details-48.png')), 'Unfold All', self)
        self.unfold_all_action.setStatusTip('Unfold all code blocks')
        self.unfold_all_action.triggered.connect(self.unfold_all)
        
        # Action to show software information
        self.software_info_action = QAction(QIcon(str(BASE_DIR / 'images' / 'lifebuoy-48.png')),'Software Information', self)
        self.software_info_action.setStatusTip('Show software information')
        self.software_info_action.triggered.connect(self.show_software_info)

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('&File')
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        edit_menu = menubar.addMenu('&Edit')
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_replace_action)
        edit_menu.addSeparator()  # Separator before edit actions
        edit_menu.addAction(self.change_font_action)

        # Add these actions to the View menu
        view_menu = menubar.addMenu('&View')
        view_menu.addAction(self.toggle_wrap_action)
        view_menu.addSeparator()
        view_menu.addAction(self.wrap_none_action)
        view_menu.addAction(self.wrap_word_action)
        view_menu.addAction(self.wrap_character_action)
        view_menu.addAction(self.wrap_whitespace_action)
        view_menu.addSeparator()
        view_menu.addAction(self.fold_all_action)
        view_menu.addAction(self.unfold_all_action)
        view_menu.addSeparator()
        view_menu.addAction(self.show_info_action)

        lexer_menu = menubar.addMenu('&Lexer')
        lexer_menu.addAction(self.lexer_python_action)
        lexer_menu.addAction(self.lexer_js_action)
        lexer_menu.addAction(self.lexer_batch_action)
        lexer_menu.addAction(self.lexer_xml_action)
        lexer_menu.addAction(self.lexer_html_action)
        lexer_menu.addAction(self.lexer_css_action)
        
        # Action to set editor to plain text
        self.plain_text_action = QAction(QIcon('images/text-48.png'), 'Plain Text', self)
        self.plain_text_action.triggered.connect(self.clear_lexer)
        lexer_menu.addAction(self.plain_text_action)
        
        # Create About menu with Software Information action
        about_menu = menubar.addMenu('&About')
        about_menu.addAction(self.software_info_action)
        
    def on_text_changed(self):
        # Mark as unsaved and update the title
        self.unsaved_changes = True
        self.update_title_bar()
        
    def print_dialog(self):
        # Display options to Print to File (PDF) or Print to Printer
        choice = QMessageBox.question(
            self,
            "Print Options",
            "Would you like to print to PDF file?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )

        if choice == QMessageBox.Yes:
            self.print_to_pdf()
        elif choice == QMessageBox.No:
            # Do nothing if No is selected (cancel the print process)
            return

    def print_to_pdf(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save as PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            text = self.editor.text()  # Get text from editor
            text_lines = text.splitlines()
            
            y = 750  # Y position to start drawing text
            for line in text_lines:
                c.drawString(100, y, line)
                y -= 12  # Move down line by line
                if y < 40:
                    c.showPage()
                    y = 750
            
            c.save()
            QMessageBox.information(self, "PDF Created", f"PDF has been saved to: {file_path}")

    def print_to_printer(self):
        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        
        try:
            hdc = win32print.StartDocPrinter(hprinter, 1, ("Pot-O Note Pad Print", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            text = self.editor.text()
            win32print.WritePrinter(hprinter, text.encode("utf-8"))
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)
            QMessageBox.information(self, "Print Job", "Document has been sent to the printer.")
        
    def toggle_line_wrapping(self):
        current_mode = self.editor.wrapMode()
        if current_mode == QsciScintilla.WrapNone:
            self.editor.setWrapMode(QsciScintilla.WrapWord)
            self.toggle_wrap_action.setChecked(True)
        elif current_mode == QsciScintilla.WrapWord:
            self.editor.setWrapMode(QsciScintilla.WrapCharacter)
            self.toggle_wrap_action.setChecked(True)
        elif current_mode == QsciScintilla.WrapCharacter:
            self.editor.setWrapMode(QsciScintilla.WrapWhitespace)
            self.toggle_wrap_action.setChecked(True)
        else:
            self.editor.setWrapMode(QsciScintilla.WrapNone)
            self.toggle_wrap_action.setChecked(False)
            
    def uncheck_all_wrap_modes(self):
        self.wrap_none_action.blockSignals(True)
        self.wrap_word_action.blockSignals(True)
        self.wrap_character_action.blockSignals(True)
        self.wrap_whitespace_action.blockSignals(True)
        
        self.wrap_none_action.setChecked(False)
        self.wrap_word_action.setChecked(False)
        self.wrap_character_action.setChecked(False)
        self.wrap_whitespace_action.setChecked(False)
        
        self.wrap_none_action.blockSignals(False)
        self.wrap_word_action.blockSignals(False)
        self.wrap_character_action.blockSignals(False)
        self.wrap_whitespace_action.blockSignals(False)

    def set_wrap_mode_none(self):
        self.uncheck_all_wrap_modes()
        if self.editor.wrapMode() != QsciScintilla.WrapNone:
            self.editor.setWrapMode(QsciScintilla.WrapNone)
            self.wrap_none_action.setChecked(True)
        else:
            self.wrap_none_action.setChecked(False)

    def set_wrap_mode_word(self):
        self.uncheck_all_wrap_modes()
        if self.editor.wrapMode() != QsciScintilla.WrapWord:
            self.editor.setWrapMode(QsciScintilla.WrapWord)
            self.wrap_word_action.setChecked(True)
        else:
            self.wrap_word_action.setChecked(False)

    def set_wrap_mode_character(self):
        self.uncheck_all_wrap_modes()
        if self.editor.wrapMode() != QsciScintilla.WrapCharacter:
            self.editor.setWrapMode(QsciScintilla.WrapCharacter)
            self.wrap_character_action.setChecked(True)
        else:
            self.wrap_character_action.setChecked(False)

    def set_wrap_mode_whitespace(self):
        self.uncheck_all_wrap_modes()
        if self.editor.wrapMode() != QsciScintilla.WrapWhitespace:
            self.editor.setWrapMode(QsciScintilla.WrapWhitespace)
            self.wrap_whitespace_action.setChecked(True)
        else:
            self.wrap_whitespace_action.setChecked(False)
            
    def showFindReplaceDialog(self):
        self.findReplaceDialog.populate_find_input()
        self.findReplaceDialog.show()
                
    def change_font(self):
        font, ok = QFontDialog.getFont(self.editor.font(), self)
        if ok:
            self.editor.setFont(font)
            
    def create_software_info_menu(self):
        software_info_menu = QMenu('Software Information', self)
        software_info_menu.addAction(self.software_info_action)
        return software_info_menu

    def set_lexer(self, language):
        lexer = None
        if language == "Python":
            lexer = self.lexer_python
            self.lexer_python_action.setCheckable(True)  # Make the action checkable
            self.lexer_python_action.setChecked(True)
            self.lexer_batch_action.setChecked(False)
            self.lexer_js_action.setChecked(False)
            self.lexer_xml_action.setChecked(False)
            self.lexer_html_action.setChecked(False)
            self.lexer_css_action.setChecked(False)
            self.lexer_python_action.triggered.connect(lambda: self.set_lexer("Python"))
        elif language == "JavaScript":
            lexer = self.lexer_js
            self.lexer_python_action.setChecked(False)
            self.lexer_js_action.setCheckable(True)  # Make the action checkable
            self.lexer_js_action.setChecked(True)
            self.lexer_batch_action.setChecked(False)
            self.lexer_xml_action.setChecked(False)
            self.lexer_html_action.setChecked(False)
            self.lexer_css_action.setChecked(False)
            self.lexer_python_action.triggered.connect(lambda: self.set_lexer("JavaScript"))
        elif language == "Batch":
            lexer = self.lexer_batch
            self.lexer_python_action.setChecked(False)
            self.lexer_batch_action.setCheckable(True)  # Make the action checkable
            self.lexer_batch_action.setChecked(True)
            self.lexer_js_action.setChecked(False)
            self.lexer_xml_action.setChecked(False)
            self.lexer_html_action.setChecked(False)
            self.lexer_css_action.setChecked(False)
            self.lexer_python_action.triggered.connect(lambda: self.set_lexer("Batch"))
        elif language == "XML":
            lexer = self.lexer_xml
            self.lexer_python_action.setChecked(False)
            self.lexer_js_action.setChecked(False)
            self.lexer_batch_action.setChecked(False)
            self.lexer_xml_action.setCheckable(True)  # Make the action checkable
            self.lexer_xml_action.setChecked(True)
            self.lexer_html_action.setChecked(False)
            self.lexer_css_action.setChecked(False)
            self.lexer_python_action.triggered.connect(lambda: self.set_lexer("XML"))
        elif language == "HTML":
            lexer = self.lexer_html
            self.lexer_python_action.setChecked(False)
            self.lexer_batch_action.setChecked(False)
            self.lexer_js_action.setChecked(False)
            self.lexer_xml_action.setChecked(False)
            self.lexer_html_action.setCheckable(True)  # Make the action checkable
            self.lexer_html_action.setChecked(True)
            self.lexer_css_action.setChecked(False)
            self.lexer_python_action.triggered.connect(lambda: self.set_lexer("HTML"))
        elif language == "CSS":
            lexer = self.lexer_css
            self.lexer_python_action.setChecked(False)
            self.lexer_batch_action.setChecked(False)
            self.lexer_js_action.setChecked(False)
            self.lexer_xml_action.setChecked(False)
            self.lexer_html_action.setChecked(False)
            self.lexer_css_action.setCheckable(True)  # Make the action checkable
            self.lexer_css_action.setChecked(True)
            self.lexer_python_action.triggered.connect(lambda: self.set_lexer("CSS"))

        self.editor.setLexer(lexer)
        
    def clear_lexer(self):
        self.editor.setLexer(None)

    def show_text_info(self):
        text = self.editor.text()
        lines = text.split('\n')
        num_lines = len(lines)
        num_words = sum(len(line.split()) for line in lines)
        num_chars = len(text)
        cursor_pos = self.editor.getCursorPosition()
        line, index = cursor_pos
        selection_length = len(self.editor.selectedText())

        info_message = (
            f"Lines: {num_lines}\n"
            f"Words: {num_words}\n"
            f"Characters: {num_chars}\n"
            f"Cursor Position: Line {line+1}, Column {index+1}\n"
            f"Selection Length: {selection_length}\n"
        )
        QMessageBox.information(self, 'Text Information', info_message)

    def update_status_bar(self):
        text = self.editor.text()
        num_chars = len(text)
        num_lines = text.count('\n') + 1
        cursor_pos = self.editor.getCursorPosition()
        line, index = cursor_pos
        self.statusBar().showMessage(f"Lines: {num_lines}, Characters: {num_chars}, Line: {line+1}, Column: {index+1}")

    def fold_all(self):
        self.editor.foldAll(True)

    def unfold_all(self):
        self.editor.foldAll(False)

    def new_file(self):
        self.editor.clear()
        self.currentFile = None
        self.setWindowTitle("Untitled - Pot-O Note Pad v0.0.3-beta.3")

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Open File', '',
            'Text Files (*.txt);;Python Files (*.py);;Batch Files (*.bat);;HTML Files (*.html *.htm);;XML Files (*.xml);;CSS Files (*.css);;JavaScript Files (*.js);;All Files (*)'
        )
        if file_name:
            self.open_file(file_name)

    def open_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.editor.setText(content)
                self.current_file = file_path
                self.update_title_bar()
        except Exception as e:
            print(f"Error opening file: {e}")

    def update_title_bar(self):
        if self.current_file:
            file_name = Path(self.current_file).name
            title = f"{'*' if self.unsaved_changes else ''}{file_name} - Pot-O Note Pad v0.0.3-beta.3"
        else:
            title = f"{'*' if self.unsaved_changes else ''}Untitled - Pot-O Note Pad v0.0.3-beta.3"
        self.setWindowTitle(title)

    def save_file(self):
        options = QFileDialog.Options()
        file_types = "Text Files (*.txt);;Python Files (*.py);;JavaScript Files (*.js);;Batch Files (*.bat);;XML Files (*.xml);;HTML Files (*.html);;CSS Files (*.css);;All Files (*)"
        default_name = "Untitled" if not self.current_file else self.current_file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", default_name, file_types, options=options)
        
        if file_name:
            # Determine the lexer language and save with appropriate extension
            if self.editor.lexer() is not None:
                if isinstance(self.editor.lexer(), QsciLexerPython):
                    file_name += '.py'
                elif isinstance(self.editor.lexer(), QsciLexerJavaScript):
                    file_name += '.js'
                elif isinstance(self.editor.lexer(), QsciLexerBatch):
                    file_name += '.bat'
                elif isinstance(self.editor.lexer(), QsciLexerXML):
                    file_name += '.xml'
                elif isinstance(self.editor.lexer(), QsciLexerHTML):
                    file_name += '.html'
                elif isinstance(self.editor.lexer(), QsciLexerCSS):
                    file_name += '.css'
            
            # Ensure the file name has an extension
            if '.' not in file_name:
                file_name += '.txt'

            with open(file_name, 'w') as file:
                file.write(self.editor.text())
            self.current_file = file_name
            self.unsaved_changes = False  # Clear unsaved flag
            self.update_title_bar()

    def exit_app(self):
        # Create a confirmation dialog with a question
        reply = QMessageBox.question(
            self,
            'Pot-O Note Pad v0.0.3-beta.3',
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # Check the user's response
        if reply == QMessageBox.Yes:
            # Quit the application
            QApplication.instance().quit()

    def show_software_info(self):
        # Create a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle('Software Information')
        dialog.setFixedSize(400, 300)  # Set the size of the dialog

        # Create a text edit widget to show the information
        text_edit = QTextEdit(dialog)
        text_edit.setReadOnly(True)

        # Set the text with the software information and MIT License
        info_text = (
            "Pot-O Note Pad v0.0.3-beta.3\n\n"
            "Developed by Pot-O Software <Muhammad Umar Hasyim Ashari>\n\n"
            "Copyright © 2024 <Muhammad Umar Hasyim Ashari>\n\n"
            "License: MIT License\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files (the 'Software'), to deal "
            "in the Software without restriction, including without limitation the rights "
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
            "copies of the Software, and to permit persons to whom the Software is "
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in "
            "all copies or substantial portions of the Software.\n\n"
            "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
            "SOFTWARE."
        )
        text_edit.setText(info_text)

        # Create a layout and add the text edit widget to it
        layout = QVBoxLayout()
        layout.addWidget(text_edit)

        # Add an OK button to close the dialog
        ok_button = QPushButton('OK', dialog)
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)

        # Set the layout to the dialog
        dialog.setLayout(layout)
        
        # Show the dialog
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Check if a file path was passed via command line arguments (right-click context menu)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]  # Get the file path from command line args
        if Path(file_path).exists():
            editor = PotONotePad(file_path)
        else:
            QMessageBox.warning(None, "Error", f"The file {file_path} does not exist.")
            sys.exit(1)
    app.setStyle('Fusion')  # Set Fusion style for consistent appearance
    editor = PotONotePad()
    editor.show()
    sys.exit(app.exec_())
