# logger_config.py
import logging

# Create a logger for your app
logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)  # Or INFO in production

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
ch.setFormatter(formatter)

# Add handler
logger.addHandler(ch)

# Silence other noisy libraries
for lib in ["httpx", "pdfminer", "openai", "supabase_py", "urllib3"]:
    logging.getLogger(lib).setLevel(logging.WARNING)

# Shortcut for easy use
log = logger.debug
