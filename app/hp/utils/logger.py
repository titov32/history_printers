import logging


def init_logger(name):
    logger = logging.getLogger(name)
    FORMAT = '%(asctime)s ::: %(name)s:%(lineno)s ::: %(levelname)s ::: %(message)s'
    logger.setLevel((logging.DEBUG))
    shell = logging.StreamHandler()
    shell.setFormatter(logging.Formatter(FORMAT))
    shell.setLevel(logging.DEBUG)
    file = logging.FileHandler(filename='logs/test.log')
    file.setFormatter((logging.Formatter(FORMAT)))
    file.setLevel(logging.INFO)
    logger.addHandler(shell)
    logger.addHandler(file)


init_logger('app')
logger = logging.getLogger("app.main")
log_html_route = logging.getLogger("app.hp.html_router")
logger.info('logger info')