import threading
import queue
import time
import uuid
from datetime import datetime
from modules.logger import log_info, log_error

class TaskPriority:
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class AutonomousTask:
    """Represents a discrete executable background task within Nova."""
    def __init__(self, name: str, action, priority: int = TaskPriority.MEDIUM, *args, **kwargs):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.action = action
        self.priority = priority  # Lower number = higher priority in Python Queue
        self.args = args
        self.kwargs = kwargs
        self.status = "PENDING"
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error_message = None

    def execute(self):
        """Runs the payload action with safety boundaries."""
        self.status = "RUNNING"
        self.started_at = datetime.now()
        try:
            log_info("TaskQueue", f"Executing Task [{self.id}] - '{self.name}'")
            # Execute the function payload
            result = self.action(*self.args, **self.kwargs)
            self.status = "COMPLETED"
            return result
        except Exception as e:
            self.status = "FAILED"
            self.error_message = str(e)
            log_error("TaskQueue", f"Task [{self.id}] failed: {e}")
            return None
        finally:
            self.completed_at = datetime.now()

class TaskQueueEngine:
    """Thread-safe background execution engine that polls and drains task units."""
    def __init__(self):
        self._queue = queue.PriorityQueue()
        self.task_registry = {}  # Tracks task lifecycle telemetry
        self._worker_thread = None
        self._running = False

    def start(self):
        """Starts the background consumer loop."""
        if self._running:
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, name="NovaTaskWorker", daemon=True)
        self._worker_thread.start()
        log_info("TaskQueue", "Autonomous Task Queue worker started.")

    def _worker_loop(self):
        """Continuously pulls and executes prioritized tasks."""
        while self._running:
            try:
                # Polling loop with timeout to avoid locking the thread on shutdown
                priority, task_id = self._queue.get(timeout=1.0)
                task = self.task_registry.get(task_id)
                if task and task.status == "PENDING":
                    task.execute()
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                log_error("TaskQueue", f"Error in background worker loop: {e}")

    def add_task(self, name: str, action, priority: int = TaskPriority.MEDIUM, *args, **kwargs) -> str:
        """Enqueues a new background task."""
        task = AutonomousTask(name, action, priority, *args, **kwargs)
        self.task_registry[task.id] = task
        # Format for PriorityQueue sorting: (priority_level, unique_id)
        self._queue.put((priority, task.id))
        log_info("TaskQueue", f"Queued background task [{task.id}]: '{name}'")
        return task.id

    def get_status_report(self) -> dict:
        """Compiles active and historical task statuses."""
        report = {"PENDING": 0, "RUNNING": 0, "COMPLETED": 0, "FAILED": 0, "tasks": []}
        for task in self.task_registry.values():
            report[task.status] += 1
            report["tasks"].append({
                "id": task.id,
                "name": task.name,
                "status": task.status,
                "priority": "HIGH" if task.priority == 1 else "MEDIUM" if task.priority == 2 else "LOW"
            })
        return report

# Global task queue runner
engine = TaskQueueEngine()