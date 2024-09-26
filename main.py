import sys
import json
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QCheckBox, QHBoxLayout, QProgressBar, QSizePolicy, QDialog, QDialogButtonBox, QLabel, QMessageBox, QCalendarWidget, QFormLayout, QHeaderView
from PySide6.QtCore import Qt, QDate, QObject, Signal, Slot, QThread
from model import TaskModel

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Task")
        self.setGeometry(100, 100, 300, 250)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Enter task name")
        self.layout.addWidget(self.task_name_input)

        self.task_status_checkbox = QCheckBox("Completed")
        self.layout.addWidget(self.task_status_checkbox)

        self.due_date_label = QLabel(QDate.currentDate().toString("dd/MM/yyyy"))
        self.layout.addWidget(self.due_date_label)

        self.calendar_button = QPushButton("Select Due Date")
        self.calendar_button.clicked.connect(self.show_calendar)
        self.layout.addWidget(self.calendar_button)

        self.calendar = QCalendarWidget()
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.hide()
        self.layout.addWidget(self.calendar)

        self.task_description_input = QLineEdit()
        self.task_description_input.setPlaceholderText("Enter task description")
        self.layout.addWidget(self.task_description_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def show_calendar(self):
        self.calendar.show()

    def get_task_data(self):
        task_name = self.task_name_input.text()
        task_status = self.task_status_checkbox.isChecked()
        due_date = self.calendar.selectedDate().toString("dd/MM/yyyy")
        description = self.task_description_input.text()
        return task_name, task_status, due_date, description

class EditTaskDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task")
        self.setGeometry(100, 100, 300, 250)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.task_name_input = QLineEdit(task.name)
        self.layout.addWidget(self.task_name_input)

        self.task_status_checkbox = QCheckBox("Completed")
        self.task_status_checkbox.setChecked(task.status)
        self.layout.addWidget(self.task_status_checkbox)

        self.due_date_label = QLabel(task.due_date)
        self.layout.addWidget(self.due_date_label)

        self.calendar_button = QPushButton("Select Due Date")
        self.calendar_button.clicked.connect(self.show_calendar)
        self.layout.addWidget(self.calendar_button)

        self.calendar = QCalendarWidget()
        self.calendar.setSelectedDate(QDate.fromString(task.due_date, "dd/MM/yyyy"))
        self.calendar.hide()
        self.layout.addWidget(self.calendar)

        self.task_description_input = QLineEdit(task.description)
        self.layout.addWidget(self.task_description_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def show_calendar(self):
        self.calendar.show()

    def get_task_data(self):
        task_name = self.task_name_input.text()
        task_status = self.task_status_checkbox.isChecked()
        due_date = self.calendar.selectedDate().toString("dd/MM/yyyy")
        description = self.task_description_input.text()
        return task_name, task_status, due_date, description

class AsyncTest(QObject):
    finished = Signal(str)

    def run(self):
        try:
            # Download the file
            url = "https://raw.githubusercontent.com/json-iterator/test-data/master/large-file.json"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the JSON
            data = json.loads(response.text)

            # Get the first element as a string
            first_element = json.dumps(data[0], indent=2)

            # Emit the finished signal with the result
            self.finished.emit(first_element)
        except Exception as e:
            # If there's an error, emit the error message
            self.finished.emit(f"Error: {str(e)}")

class AsyncTestThread(QThread):
    def __init__(self, async_test):
        super().__init__()
        self.async_test = async_test

    def run(self):
        self.async_test.run()

class ToDoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List")
        self.setGeometry(100, 100, 600, 400)

        self.model = TaskModel()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.show_add_task_dialog)
        self.layout.addWidget(self.add_task_button)

        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels(["Name", "Completed", "Due Date", "Description", "", ""])
        self.task_table.horizontalHeader().setStretchLastSection(False)
        self.task_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.task_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.task_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.task_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.task_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.task_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.task_table.setSortingEnabled(True)
        self.layout.addWidget(self.task_table)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.progress_bar.setFixedHeight(30)  # Set the progress bar height to 30 pixels
        self.layout.addWidget(self.progress_bar)

        self.delete_all_button = QPushButton("Delete All Tasks")
        self.delete_all_button.clicked.connect(self.confirm_delete_all_tasks)
        self.layout.addWidget(self.delete_all_button)

        # Add the Async test button
        self.async_test_button = QPushButton("Async test")
        self.async_test_button.clicked.connect(self.on_async_test_clicked)
        self.layout.addWidget(self.async_test_button)

        self.load_tasks()

        # Create an instance of AsyncTest
        self.async_test = AsyncTest()
        self.async_test.finished.connect(self.on_async_test_finished)
        self.async_test_thread = AsyncTestThread(self.async_test)

    def load_tasks(self):
        self.task_table.setRowCount(0)
        for task in self.model.tasks:
            self.add_task_to_table(task)
        self.update_progress_bar()

    def show_add_task_dialog(self):
        dialog = AddTaskDialog(self)
        if dialog.exec() == QDialog.Accepted:
            task_name, task_status, due_date, description = dialog.get_task_data()
            if task_name:
                self.model.add_task(task_name, due_date, description)
                self.load_tasks()

    def show_edit_task_dialog(self, task):
        dialog = EditTaskDialog(task, self)
        if dialog.exec() == QDialog.Accepted:
            task_name, task_status, due_date, description = dialog.get_task_data()
            self.model.update_task(task.task_id, task_name, due_date, description, task_status)
            self.load_tasks()

    def add_task_to_table(self, task):
        row_position = self.task_table.rowCount()
        self.task_table.insertRow(row_position)

        name_item = QTableWidgetItem(task.name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.task_table.setItem(row_position, 0, name_item)

        completed_checkbox = QCheckBox()
        completed_checkbox.setChecked(task.status)
        completed_checkbox.stateChanged.connect(lambda state, task_id=task.task_id: self.update_task_status(task_id, state))
        self.task_table.setCellWidget(row_position, 1, completed_checkbox)

        due_date_item = QTableWidgetItem(task.due_date)
        due_date_item.setFlags(due_date_item.flags() & ~Qt.ItemIsEditable)
        self.task_table.setItem(row_position, 2, due_date_item)

        description_item = QTableWidgetItem(task.description)
        description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
        self.task_table.setItem(row_position, 3, description_item)

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda _, task=task: self.show_edit_task_dialog(task))
        edit_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        edit_button.setFixedWidth(edit_button.sizeHint().width())
        self.task_table.setCellWidget(row_position, 4, edit_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda _, task_id=task.task_id: self.confirm_delete_task(task_id))
        delete_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        delete_button.setFixedWidth(delete_button.sizeHint().width())
        self.task_table.setCellWidget(row_position, 5, delete_button)

    def update_task_status(self, task_id, state):
        self.model.update_task_status(task_id, state == 2)
        self.update_progress_bar()

    def confirm_delete_task(self, task_id):
        reply = QMessageBox.warning(self, "Delete Task", "Are you sure you want to delete this task?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.delete_task(task_id)

    def delete_task(self, task_id):
        self.model.delete_task(task_id)
        self.load_tasks()

    def confirm_delete_all_tasks(self):
        reply = QMessageBox.warning(self, "Delete All Tasks", "Are you sure you want to delete all tasks?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.delete_all_tasks()

    def delete_all_tasks(self):
        self.model.tasks = []
        self.model.save_tasks()
        self.load_tasks()

    def update_progress_bar(self):
        total_tasks = len(self.model.tasks)
        if total_tasks == 0:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("0%")
        else:
            completed_tasks = sum(task.status for task in self.model.tasks)
            progress = int((completed_tasks / total_tasks) * 100)
            self.progress_bar.setValue(progress)
            self.progress_bar.setFormat(f"{progress}%")

    def on_async_test_clicked(self):
        self.async_test_thread.start()

    @Slot(str)
    def on_async_test_finished(self, result):
        QMessageBox.information(self, "Async Test", f"Async test done\n\nFirst element:\n{result}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec())