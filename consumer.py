# consumer.py
import csv
import os
import time
from datetime import datetime

FILE_NAME = 'tasks.csv'
LOCK_FILE = 'tasks.csv.lock'
FIELDNAMES = ['task_id', 'status', 'created_at', 'updated_at']
WORK_DURATION_SECONDS = 30
CHECK_INTERVAL_SECONDS = 5


def acquire_lock():
    try:
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL)
        os.close(fd)
        return True
    except FileExistsError:
        return False


def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def find_and_process_task():
    if not acquire_lock():
        return

    task_to_process = None
    updated_rows = []

    try:
        if not os.path.isfile(FILE_NAME) or os.path.getsize(FILE_NAME) == 0:
            return

        with open(FILE_NAME, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

        for i, row in enumerate(rows):
            if row['status'] == 'pending':
                task_to_process = row
                rows[i]['status'] = 'in_progress'
                rows[i]['updated_at'] = datetime.now().isoformat()
                break

        updated_rows = rows

        if task_to_process:
            with open(FILE_NAME, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(updated_rows)
    finally:
        release_lock()

    if task_to_process:
        task_id = task_to_process['task_id']
        print(f"[{os.getpid()}] Pobrano zadanie {task_id}. Rozpoczynam pracę (30s)...")
        time.sleep(WORK_DURATION_SECONDS)
        print(f"[{os.getpid()}] Zakończono zadanie {task_id}.")

        while not acquire_lock():
            time.sleep(0.1)

        try:
            with open(FILE_NAME, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

            for i, row in enumerate(rows):
                if row['task_id'] == task_id:
                    rows[i]['status'] = 'done'
                    rows[i]['updated_at'] = datetime.now().isoformat()
                    break

            with open(FILE_NAME, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(rows)
        finally:
            release_lock()


if __name__ == "__main__":
    print(f"--- Consumer (PID: {os.getpid()}) uruchomiony. Sprawdzanie co {CHECK_INTERVAL_SECONDS}s ---")
    while True:
        find_and_process_task()
        time.sleep(CHECK_INTERVAL_SECONDS)
