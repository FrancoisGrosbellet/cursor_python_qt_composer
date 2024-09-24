import json
import os
import uuid
from datetime import datetime

class Task:
    def __init__(self, name, due_date, description, status=False, task_id=None):
        self.task_id = task_id if task_id else str(uuid.uuid4())
        self.name = name
        self.due_date = due_date
        self.description = description
        self.status = status

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'name': self.name,
            'due_date': self.due_date,
            'description': self.description,
            'status': self.status
        }

class TaskModel:
    def __init__(self, json_file='tasks.json'):
        self.json_file = json_file
        self.tasks = self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as file:
                tasks_data = json.load(file)
                return [Task(**task) for task in tasks_data]
        return []

    def save_tasks(self):
        with open(self.json_file, 'w') as file:
            json.dump([task.to_dict() for task in self.tasks], file, indent=4)

    def add_task(self, name, due_date, description):
        task = Task(name, due_date, description)
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        self.save_tasks()

    def update_task(self, task_id, name, due_date, description, status):
        for task in self.tasks:
            if task.task_id == task_id:
                task.name = name
                task.due_date = due_date
                task.description = description
                task.status = status
                break
        self.save_tasks()

    def update_task_status(self, task_id, status):
        for task in self.tasks:
            if task.task_id == task_id:
                task.status = status
                break
        self.save_tasks()