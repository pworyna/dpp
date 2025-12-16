import csv
import os
import uuid
from datetime import datetime

FILE_NAME = 'tasks.csv'
FIELDNAMES = ['task_id', 'status', 'created_at', 'updated_at']

def add_task():
    file_exists = os.path.isfile(FILE_NAME)

    with open(FILE_NAME, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)

        if not file_exists or os.path.getsize(FILE_NAME) == 0:
            writer.writeheader()

        now = datetime.now().isoformat()
        task = {
            'task_id': str(uuid.uuid4()),
            'status': 'pending',
            'created_at': now,
            'updated_at': now
        }
        writer.writerow(task)
        print(f"Dodano zadanie: {task['task_id']}")

if __name__ == "__main__":
    num_tasks = 100
    print(f"--- Rozpoczynam dodawanie {num_tasks} zadań ---")
    for i in range(num_tasks):
        add_task()
    print(f"--- Zakończono dodawanie zadań ---")
