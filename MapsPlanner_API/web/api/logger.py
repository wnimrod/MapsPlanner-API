import logging

logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

api_handler = logging.StreamHandler()
api_formatter = logging.Formatter("%(levelname)s:\t[%(funcName)s]: %(message)s")

api_handler.setFormatter(api_formatter)

logger.addHandler(api_handler)
