import sys
import logging
sys.path.append(".")
import logging_factory as log
from src.CONST_ENV import ENV_PATH as ENV

logging.basicConfig(filename=ENV.LOGGING_PATH.joinpath("exceptions.log"), level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s", filemode="w")
exceptions = logging.getLogger("exceptions")





