import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'level': record.levelname,
            'time': self.formatTime(record),
            'message': record.getMessage(),
            'name': record.name,
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger(name: str = "paynsnapbot"):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
    # Ensure root logger is configured so all logs go to terminal
    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)
