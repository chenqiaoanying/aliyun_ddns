import logging


logger = logging.getLogger()

fm = logging.Formatter('%(asctime)s %(message)s')  # 打印格式

# fh = logging.FileHandler('test.log')  # 可以向文件发送日志
# fh.setFormatter(fm)
# logger.addHandler(fh)

ch = logging.StreamHandler()  # 可以向屏幕发送日志
ch.setFormatter(fm)
logger.addHandler(ch)

logger.setLevel('INFO')  # 设置级别

# logger.info('info')
# logger.debug('debug')
# logger.warning('warning')
# logger.error('error')
# logger.critical('critical')
