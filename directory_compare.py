from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QTreeWidget, QTreeWidgetItem, QErrorMessage, QLabel, QInputDialog
from PyQt5.QtCore import QUrl, Qt, QSettings
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHeaderView

import os
import sys


class DirectoryChoiceDialog(QDialog):
    # Define a custom signal that emits the chosen directory
    directory_chosen = pyqtSignal(str)

    def __init__(self, parent=None):
        super(DirectoryChoiceDialog, self).__init__(parent)

        self.setWindowTitle("Choose a Directory")

        layout = QVBoxLayout(self)

        # Add QLabel for descriptive text
        description_label = QLabel("Would you like to open Dir1 or Dir2?", self)
        layout.addWidget(description_label)

        dir1_button = QPushButton("Dir 1", self)
        dir1_button.clicked.connect(lambda: self.directory_chosen.emit("Open in Dir 1"))
        layout.addWidget(dir1_button)

        dir2_button = QPushButton("Dir 2", self)
        dir2_button.clicked.connect(lambda: self.directory_chosen.emit("Open in Dir 2"))
        layout.addWidget(dir2_button)

        self.setLayout(layout)
        
from PyQt5.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox

class ResultWidget(QWidget):
    def __init__(self, parent=None, directory_comparator=None):
        super(ResultWidget, self).__init__(parent)
        
        self.directory_comparator = directory_comparator

        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderLabels(["File", "Size in Dir 1", "Size in Dir 2"])
        self.tree_widget.setColumnWidth(0, 300)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_widget)

        self.tree_widget.itemDoubleClicked.connect(self.open_folder)  # Connect double click to open folder

        # Add checkboxes
        self.add_checkboxes()

        # Add "Hide Selected" button
        self.add_hide_selected_button()

    def add_result(self, file, size_dir1, size_dir2):
        item = QTreeWidgetItem([file, str(size_dir1), str(size_dir2)])
        self.tree_widget.addTopLevelItem(item)

        # Add checkbox to each item
        checkbox = QCheckBox(self)
        self.tree_widget.setItemWidget(item, 3, checkbox)

    def add_checkboxes(self):
        # Add a checkbox column to the tree widget
        self.tree_widget.headerItem().setTextAlignment(3, Qt.AlignHCenter)
        self.tree_widget.headerItem().setText(3, "")
        

    def add_hide_selected_button(self):
        # Add "Hide Selected" button
        hide_selected_button = QPushButton("Hide Selected", self)
        hide_selected_button.clicked.connect(self.hide_selected_items)

        # Create a layout for the "Hide Selected" button
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(hide_selected_button)

        # Add the button layout to the main layout
        layout = self.layout()
        layout.addLayout(button_layout)

    def hide_selected_items(self):
        # Hide selected items
        for row in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(row)
            checkbox = self.tree_widget.itemWidget(item, 3)  # Get checkbox widget from the item

            if checkbox.isChecked():
                item.setHidden(True)

    def open_folder(self, item):
        if item:
            relative_path = item.text(0)  # Index 0 corresponds to the "File" column
            filepath = os.path.join(self.directory_comparator.dir1 if self.directory_comparator else "", relative_path)
            filepath = filepath.replace('/', '\\')  # Replace forward slashes with backslashes

            # Show custom directory choice dialog
            dialog = DirectoryChoiceDialog(self)
            
            # Connect the custom signal to a handler method
            dialog.directory_chosen.connect(lambda choice: self.handle_directory_choice(choice, relative_path))

            # Exec the dialog
            result = dialog.exec_()

    def handle_directory_choice(self, choice, relative_path):
        if choice == "Open in Dir 1":
            # Handle opening in Dir 1
            full_path = os.path.join(self.directory_comparator.dir1, relative_path).replace('/', '\\')
            os.system(f'explorer /select, "{full_path}"')
        elif choice == "Open in Dir 2":
            # Handle opening in Dir 2
            full_path = os.path.join(self.directory_comparator.dir2, relative_path).replace('/', '\\')
            os.system(f'explorer /select, "{full_path}"')





class DirectoryComparator(QWidget):
    def __init__(self):
        super().__init__()

        # Load last opened directories from QSettings
        self.settings = QSettings("YourCompany", "DirectoryComparator")
        self.dir1 = self.settings.value("LastDirectory1", "")
        self.dir2 = self.settings.value("LastDirectory2", "")
        

        self.init_ui()
        self.dir1_label.setText(f"Directory 1: {self.dir1}")
        self.dir2_label.setText(f"Directory 2: {self.dir2}")

        # Update the DirectoryComparator instance in ResultWidget
        self.result_widget.directory_comparator = self

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Directory Compare')
        

        self.result_widget = ResultWidget(self, directory_comparator=self)  # Pass the DirectoryComparator instance
        self.extension_filter = QLineEdit(self)
        self.extension_filter.setPlaceholderText("Enter file extension filter (e.g., txt)")

        self.name_filter = QLineEdit(self)
        self.name_filter.setPlaceholderText("Enter file name or path filter")

        self.dir1_label = QLabel(self)
        self.dir2_label = QLabel(self)

        compare_button = QPushButton('Compare Directories', self)
        compare_button.clicked.connect(self.compare_directories)

        select_button1 = QPushButton('Select Directory 1', self)
        select_button1.clicked.connect(self.select_directory1)

        select_button2 = QPushButton('Select Directory 2', self)
        select_button2.clicked.connect(self.select_directory2)
        self.extension_filter.textChanged.connect(self.compare_directories)
        self.name_filter.textChanged.connect(self.compare_directories)


        layout = QVBoxLayout()
        layout.addWidget(select_button1)
        layout.addWidget(self.dir1_label)
        layout.addWidget(select_button2)
        layout.addWidget(self.dir2_label)
        layout.addWidget(self.extension_filter)
        layout.addWidget(self.name_filter)
        layout.addWidget(compare_button)
        layout.addWidget(self.result_widget)

        self.setLayout(layout)

    def select_directory1(self):
        
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory 1', self.dir1)
        if directory:
            self.dir1 = directory
            self.dir1_label.setText(f"Directory 1: {directory}")
            self.result_widget.directory_comparator = self  # Update the DirectoryComparator instance in ResultWidget

            # Save the last opened directory in QSettings
            self.settings.setValue("LastDirectory1", directory)

    def select_directory2(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory 2', self.dir2)
        if directory:
            self.dir2 = directory
            self.dir2_label.setText(f"Directory 2: {directory}")
            self.result_widget.directory_comparator = self  # Update the DirectoryComparator instance in ResultWidget

            # Save the last opened directory in QSettings
            self.settings.setValue("LastDirectory2", directory)

    def compare_directories(self):
        try:
            dir1_files = self.get_file_sizes(self.dir1, self.extension_filter.text(), self.name_filter.text())
            dir2_files = self.get_file_sizes(self.dir2, self.extension_filter.text(), self.name_filter.text())
    
            self.result_widget.tree_widget.clear()
    
            all_files = set(dir1_files.keys()) | set(dir2_files.keys())
    
            for file in all_files:
                size_dir1 = dir1_files.get(file, "")
                size_dir2 = dir2_files.get(file, "")
    
                if size_dir1 != size_dir2:
                    self.result_widget.add_result(file, size_dir1, size_dir2)
    
        except Exception as e:
            self.result_widget.tree_widget.clear()
            self.show_error_message(f"Error: {str(e)}")


    def get_file_sizes(self, directory, extension_filter, name_filter):
        file_sizes = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                if extension_filter and not file.lower().endswith(extension_filter):
                    continue

                if name_filter and name_filter not in file.lower() and name_filter not in os.path.join(root, file).lower():
                    continue

                file_path = os.path.join(root, file)
                try:
                    relative_path = os.path.relpath(file_path, directory)
                    file_sizes[relative_path] = os.path.getsize(file_path)
                except OSError:
                    pass
        return file_sizes

    def show_error_message(self, message):
        error_dialog = QErrorMessage(self)
        error_dialog.setWindowTitle("Error")
        error_dialog.showMessage(message)

if __name__ == '__main__':
    app = QApplication([])
    comparator = DirectoryComparator()
    comparator.show()
    app.exec_()