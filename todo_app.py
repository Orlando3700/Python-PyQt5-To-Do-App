import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QFrame, QGraphicsDropShadowEffect, QDesktopWidget
)
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import QDate

# Calls methods to set up the UI, center the window, and load existing tasks.
class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elegant To-Do List")
        self.setMinimumSize(600, 700)
        self.init_ui()
        self.center_window()
        self.load_tasks()

    # Centers the application on the screen.
    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    # ertical layout for the outer part of the app with padding.
    def init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(40, 40, 40, 40)

        # Card Container
        # QFrame used as a container ("card-style") with its own layout.
        card = QFrame()
        card.setObjectName("MainCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        # Drop shadow
        # Adds a drop shadow effect for visual style.
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 50))
        card.setGraphicsEffect(shadow)

        # Section Label
        title = QLabel("📝 Your Tasks")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 600;")

        # Input & Add Button
        # Horizontal layout containing a text input for new tasks
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a new task...")
        
        # Adds a date picker for task due date, defaulted to today.
        from PyQt5.QtWidgets import QDateEdit
        from PyQt5.QtCore import QDate

        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate())

        add_button = QPushButton("Add")
        add_button.setObjectName("AddTask")
        add_button.clicked.connect(self.add_task)

        # Adds input widgets to the layout.
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.due_date_input)
        input_layout.addWidget(add_button)

        # Task List
        # A list widget for showing tasks. Reacts when a task's checkbox is changed.
        self.task_list = QListWidget()
        self.task_list.itemChanged.connect(self.update_task_status)

        # Buttons for Edit/Delete
        buttons_layout = QHBoxLayout()
        
        mark_all_button = QPushButton("Mark All Completed")
        mark_all_button.setObjectName("MarkAllCompleted")
        mark_all_button.clicked.connect(self.mark_all_completed)
        
        unmark_all_button = QPushButton("Mark All Incomplete")
        unmark_all_button.setObjectName("MarkAllIncomplete")
        unmark_all_button.clicked.connect(self.mark_all_incomplete)
        
        delete_button = QPushButton("Delete")
        delete_button.setObjectName("DeleteTask")
        delete_button.clicked.connect(self.delete_task)

        edit_button = QPushButton("Edit")
        edit_button.setObjectName("EditTask")
        edit_button.clicked.connect(self.edit_task)
        
        buttons_layout.addWidget(mark_all_button)
        buttons_layout.addWidget(unmark_all_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)

        # Assembling
        # Assembles widgets into the main layout.
        card_layout.addWidget(title)
        card_layout.addLayout(input_layout)
        card_layout.addWidget(self.task_list)
        card_layout.addLayout(buttons_layout)
        outer_layout.addWidget(card)

        # Apply stylesheet
        try:
            self.setStyleSheet(open("style.qss").read())  # make sure the stylesheet is saved
        except Exception:
            print("No stylesheet found or failed to load.")    

    # Gets input text and selected date.
    def add_task(self):
        task_text = self.task_input.text().strip()
        due_date = self.due_date_input.date().toString("yyyy-MM-dd")
        # Creates a list item with a checkbox and stores task metadata in UserRole.
        if task_text:
            display_text = f"{task_text} (Due: {due_date})"
            item = QListWidgetItem(task_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
            item.setCheckState(Qt.Unchecked)
            # self.task_list.addItem(QListWidgetItem(task_text))
            item.setData(Qt.UserRole, {"task": task_text, "due": due_date})
            self.task_list.addItem(item)
            self.task_input.clear()
            self.save_tasks()

    def delete_task(self):
        selected = self.task_list.currentRow()
        if selected >= 0:
            self.task_list.takeItem(selected)
            self.save_tasks()

    def edit_task(self):
        selected = self.task_list.currentItem()
        if selected:
            new_text = self.task_input.text().strip()
            if new_text:
                selected.setText(new_text)
                self.task_input.clear()
                self.save_tasks()
    
    # Strikes through completed tasks and colors overdue tasks red.
    def update_task_status(self, item):
        font = item.font()
        font.setStrikeOut(item.checkState() == Qt.Checked)
        item.setFont(font)

        # Check overdue status
        data = item.data(Qt.UserRole)
        if data:
            due_date = QDate.fromString(data["due"], "yyyy-MM-dd")
            today = QDate.currentDate()
            if item.checkState() == Qt.Unchecked and due_date.isValid() and due_date < today:
                item.setForeground(QBrush(Qt.red))
            else:
                item.setForeground(QBrush(Qt.black))

        self.save_tasks()
    
    # Converts task list to a JSON format and saves it.
    def save_tasks(self, filename="tasks.json"):
        tasks_data = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            data = item.data(Qt.UserRole)
            if data:  # make sure the task has metadata
                task_entry = {
                    "task": data["task"],
                    "due": data["due"],
                    "completed": item.checkState() == Qt.Checked
                    }
                tasks_data.append(task_entry)
            with open(filename, "w") as file:
                json.dump(tasks_data, file, indent=4)
            
    def mark_all_completed(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            item.setCheckState(Qt.Checked)
            # Apply strike-through immediately
            font = item.font()
            font.setStrikeOut(True)
            item.setFont(font)
            self.save_tasks()
            
    def mark_all_incomplete(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            item.setCheckState(Qt.Unchecked)
            font = item.font()
            font.setStrikeOut(False)
            item.setFont(font)
            self.save_tasks()


    # Loads task data from a file, supporting both legacy and modern formats.
    # Tasks are recreated with appropriate due dates, check status, and overdue highlighting.
    def load_tasks(self, filename="tasks.json"):
        try:
            with open(filename, "r") as file:
                data = json.load(file)

                if isinstance(data, dict):
                    for task, completed in data.items():
                        display_text = f"{task} (Due: N/A)"
                        item = QListWidgetItem(display_text)
                        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
                        item.setCheckState(Qt.Checked if completed else Qt.Unchecked)
                        item.setData(Qt.UserRole, {"task": task, "due": "N/A"})
                        self.task_list.addItem(item)

                elif isinstance(data, list):
                    today = QDate.currentDate()
                    for entry in data:
                        task = entry["task"]
                        due = entry["due"]
                        completed = entry["completed"]

                        display_text = f"{task} (Due: {due})"
                        item = QListWidgetItem(display_text)
                        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
                        item.setCheckState(Qt.Checked if completed else Qt.Unchecked)
                        item.setData(Qt.UserRole, {"task": task, "due": due})
                        
                        # Check if overdue
                        due_date = QDate.fromString(due, "yyyy-MM-dd")
                        if not completed and due_date.isValid() and due_date < today:
                            item.setForeground(QBrush(Qt.red))
                            
                        self.task_list.addItem(item)
        except FileNotFoundError:
            pass

# Starts the PyQt5 application and shows the main window
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec_())


