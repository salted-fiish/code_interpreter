import logging

logger_instance = logging.getLogger("code_runner")
logger_instance.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger_instance.addHandler(ch)
