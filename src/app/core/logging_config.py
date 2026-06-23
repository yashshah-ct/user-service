import logging
import re
import sys
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_ctx.get()
        return True


_SENSITIVE_PATTERNS = [
    (re.compile(r"(?i)(authorization|cookie|x-api-key|password|token|secret)\s*[:=]\s*[\w\-\.]+", re.IGNORECASE), r"\1=[REDACTED]"),
    (re.compile(r"Bearer\s+[\w\-\.]+", re.IGNORECASE), "Bearer [REDACTED]"),
]


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, "msg", None) and isinstance(record.msg, str):
            msg = record.msg
            for pattern, repl in _SITIVE_PATTERNS:
                msg = pattern.sub(repl, msg)
            record.msg = msg
        return True


def setup_logging(log_level: str = "INFO") -> None:
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(SensitiveDataFilter())
    handler.addFilter(CorrelationFilter())
    handler.setFormatter(jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(correlation_id)s"
    ))
    logger.handlers = [handler]
