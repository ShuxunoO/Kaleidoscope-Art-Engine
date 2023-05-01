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

