from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.Qsci import QsciScintilla

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = parent.editor if parent else QsciScintilla()
        self.last_find_pos = -1

        self.initUI()

    def initUI(self):
        self.find_input = QLineEdit(self)
        self.replace_input = QLineEdit(self)
        self.find_button = QPushButton('Find', self)
        self.replace_button = QPushButton('Replace', self)
        self.replace_all_button = QPushButton('Replace All', self)

        self.find_button.clicked.connect(self.find_text)
        self.replace_button.clicked.connect(self.replace_text)
        self.replace_all_button.clicked.connect(self.replace_all_text)

        find_layout = QHBoxLayout()
        find_layout.addWidget(self.find_input)
        find_layout.addWidget(self.find_button)

        replace_layout = QHBoxLayout()
        replace_layout.addWidget(self.replace_input)
        replace_layout.addWidget(self.replace_button)
        replace_layout.addWidget(self.replace_all_button)

        layout = QVBoxLayout()
        layout.addLayout(find_layout)
        layout.addLayout(replace_layout)

        self.setLayout(layout)

        self.populate_find_input()

    def populate_find_input(self):
        line_from, index_from, line_to, index_to = self.editor.getSelection()
        if line_from != line_to or index_from != index_to:  # There is a selection
            selected_text = self.editor.selectedText()
            self.find_input.setText(selected_text)

    def find_text(self):
        target = self.find_input.text()
        if not target:
            return
        # Start search from the current position if last find was successful
        found = self.editor.findFirst(target, False, False, False, True)
        if found:
            self.last_find_pos = self.editor.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        else:
            self.last_find_pos = -1  # Reset to start new search from beginning
            self.show_message("Text not found or end of document reached")

    def replace_text(self):
        target = self.find_input.text()
        replacement = self.replace_input.text()
        if not target:
            return

        # Get current selection and ensure it's the target text
        line_from, index_from, line_to, index_to = self.editor.getSelection()
        selected_text = self.editor.selectedText()
        if selected_text == target:
            self.editor.replaceSelectedText(replacement)
            # Re-select the replaced text
            self.editor.setSelection(line_from, index_from, line_from, index_from + len(replacement))
        else:
            # Find the target text
            found = self.editor.findFirst(target, False, False, False, True)
            if found:
                line_from, index_from, line_to, index_to = self.editor.getSelection()
                self.editor.replaceSelectedText(replacement)
                # Re-select the replaced text
                self.editor.setSelection(line_from, index_from, line_from, index_from + len(replacement))
            else:
                self.show_message("Text not found")

    def replace_all_text(self):
        target = self.find_input.text()
        replacement = self.replace_input.text()
        if not target:
            return
        replaced_count = 0
        while self.editor.findFirst(target, False, False, False, True):
            line_from, index_from, line_to, index_to = self.editor.getSelection()
            self.editor.replaceSelectedText(replacement)
            # Re-select the replaced text
            self.editor.setSelection(line_from, index_from, line_from, index_from + len(replacement))
            replaced_count += 1
        if replaced_count == 0:
            self.show_message("Text not found")

    def show_message(self, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle("Find and Replace")
        msg_box.exec_()
