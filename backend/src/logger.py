import logging
import os

# Ensure logs folder exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# logging.basicConfig(
#     filename="logs/backend.log",
#     level=logging.INFO,  # Change to DEBUG for more verbosity
#     format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
# )

# Get a logger instance
logger = logging.getLogger("RemindAI")
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler("logs/backend.log")
file_handler.setLevel(logging.INFO)

# Console handler (optional, helpful for dev)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# --------------------------
# SYNCHRONIZATION LOGGER
# --------------------------
sync_logger = logging.getLogger("RemindAI.Sync")
sync_logger.setLevel(logging.INFO)

sync_handler = logging.FileHandler("logs/sync_errors.log")
sync_handler.setLevel(logging.INFO)
sync_handler.setFormatter(formatter)

sync_logger.addHandler(sync_handler)
sync_logger.addHandler(console_handler)