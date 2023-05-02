import sys
import logging
sys.path.append(".")
from src.CONST_ENV import ENV_PATH as ENV

logging.basicConfig(filename=ENV.LOGGING_PATH.joinpath("exceptions.log"), level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s", filemode="w")
excplog = logging.getLogger("exceptions")

class PercentageError(Exception):
    def __init__(self, layer_name, percentage):
        self.layer_name = layer_name
        self.percentage = percentage

    def __str__(self):
        ERROR_INFO = f"The percentage of {self.layer_name} is {str(self.percentage)}, which is greater than 1.0"
        excplog.error(ERROR_INFO)
        return ERROR_INFO





