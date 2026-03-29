import logging
import contextvars

# Context variable for the current request's API name (route/path)
api_name_var: contextvars.ContextVar[str] = contextvars.ContextVar("api_name", default="System")

class APIContextFilter(logging.Filter):
    """Injects the `api_name` from the contextvar into the log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.api_name = api_name_var.get()
        return True

def _setup_logger() -> logging.Logger:
    _logger = logging.getLogger("triptracks")
    _logger.setLevel(logging.INFO)

    # Prevent duplicating handlers
    if not _logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format string with filename, lineno, funcName, and our custom api_name
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(filename)s:%(lineno)d (%(funcName)s) | [API: %(api_name)s] | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        
        _logger.addFilter(APIContextFilter())
        _logger.addHandler(console_handler)
        
    return _logger

# Global logger instance
logger = _setup_logger()
