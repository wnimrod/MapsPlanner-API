import logging

tests_logger = logging.getLogger("tests")

api_handler = logging.StreamHandler()
api_formatter = logging.Formatter("%(levelname)s\t%(message)s")

api_handler.setFormatter(api_formatter)

tests_logger.addHandler(api_handler)
