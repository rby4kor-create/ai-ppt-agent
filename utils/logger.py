import logging
import sys


_CONFIGURED = False


def _configure_root():
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                           datefmt="%H:%M:%S")
    )

    root = logging.getLogger("genai_report")
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    root.propagate = False

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """
    Returns a namespaced logger under the 'genai_report' root logger.
    Usage: logger = get_logger(__name__)
    """
    _configure_root()
    return logging.getLogger(f"genai_report.{name}")
