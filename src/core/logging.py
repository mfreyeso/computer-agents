import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger("computer_use_control_plane")
    # Tame Uvicorn/FastAPI access logs slightly for clarity
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    return logger

logger = setup_logging()
