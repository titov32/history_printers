import logging
FORMAT = '%(asctime)s ::: %(name)s:%(lineno)s ::: %(levelname)s ::: %(message)s'

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    shell = logging.StreamHandler()
    shell.setFormatter(logging.Formatter(FORMAT))
    shell.setLevel(logging.DEBUG)
    logger.addHandler(shell)
    return logger



logger = setup_logger('app', 'logs/test.log', level=logging.INFO)
log_api_route = setup_logger("db", 'logs/db.log', level=logging.DEBUG)
logger.info('logger info')
