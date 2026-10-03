import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Any, Optional
import queue

# Create an in-memory queue to capture log records for SSE live streaming
log_queue: queue.Queue = queue.Queue(maxsize=1000)


class SSEHandler(logging.Handler):
    """Logging handler that pushes formatted log messages to an in-memory queue for SSE."""
    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            log_data = {
                "asctime": getattr(record, "asctime", record.created),
                "levelname": record.levelname,
                "name": record.name,
                "run_id": getattr(record, "run_id", "-"),
                "file_path": getattr(record, "file_path", "-"),
                "message": record.getMessage()
            }
            if log_queue.full():
                try:
                    log_queue.get_nowait()
                except queue.Empty:
                    pass
            log_queue.put_nowait(log_data)
        except Exception:
            self.handleError(record)


def setup_logger(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("deptwise")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    # Prevent duplicate handlers if re-initialized
    if logger.handlers:
        return logger

    # Ensure logs dir exists
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "app.log")

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
    ))

    # Rotating file handler (10MB max, 5 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s | run=%(run_id)s | file=%(file_path)s | %(message)s"
    ))

    # SSE handler
    sse_handler = SSEHandler()
    sse_handler.setFormatter(file_handler.formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.addHandler(sse_handler)

    return logger


def update_logger_level(level_name: str):
    logger = logging.getLogger("deptwise")
    logger.setLevel(getattr(logging, level_name.upper(), logging.INFO))


def get_logger(run_id: Optional[Any] = None, file_path: Optional[str] = None) -> logging.LoggerAdapter:
    base_logger = logging.getLogger("deptwise")
    extra = {
        "run_id": str(run_id) if run_id is not None else "-",
        "file_path": file_path or "-"
    }
    return logging.LoggerAdapter(base_logger, extra)
