import logging

logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

api_handler = logging.StreamHandler()
api_formatter = logging.Formatter("%(levelname)s\t%(message)s")

api_handler.setFormatter(api_formatter)

logger.addHandler(api_handler)

logger.debug("--- Initialized api logger ---")
