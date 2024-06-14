import logging

# 创建全局的日志记录器
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

# 创建文件处理程序
file_handler = logging.FileHandler('log.log')
file_handler.setLevel(logging.DEBUG)

# 创建日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s  - %(message)s')
file_handler.setFormatter(formatter)

# 添加处理程序到日志记录器
logger.addHandler(file_handler)