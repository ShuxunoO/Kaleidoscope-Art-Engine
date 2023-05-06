import logging

def setup_logger(logger_name: str, log_file_path: str, level: int = logging.INFO) -> logging.Logger:
    """
    设置一个日志记录器。

    @param logger_name: 日志记录器的名称
    @param log_file: 日志输出文件的路径
    @param level: 日志记录级别, 默认为logging.INFO
    @return: 配置好的日志记录器对象
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    handler = logging.FileHandler(log_file_path, encoding="UTF-8", mode = 'w')
    formatter = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger




class LoggerFactory:
    """定义了一个 LoggerFactory 类，
    它包含一个 create_logger 方法，该方法接受一个字符串参数 logger_name，并根据该参数返回一个相应的日志变量。
    在 create_logger 方法中，使用 Python 的内置 logging 模块来创建一个新的日志记录器对象，
    并为它添加一个控制台处理器和一个文件处理器。我们还可以设置日志记录器的日志级别和格式。
    """
    def __init__(self, log_level=logging.INFO):
        self.log_level = log_level

    def create_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(f"{logger_name}.log")
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger