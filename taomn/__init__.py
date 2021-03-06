import logging

__version__ = '0.5.1'

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger = logging.getLogger('taomn')
logger.addHandler(handler)
logger.setLevel('CRITICAL')
