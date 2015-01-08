# runningtext
#
# (c) 2015 Tuwuh Sarwoprasojo
# All rights reserved.

import errno
import logging
import logging.handlers
import os

LOG_FILENAME = './log/runningtext.log'

def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

class MyRotatingFileHandler(logging.handlers.RotatingFileHandler):
	def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
		mkdir_p(os.path.dirname(filename))
		logging.handlers.RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

def init_logger():
	formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')

	handler = MyRotatingFileHandler(LOG_FILENAME, maxBytes=1024, backupCount=10)
	handler.setFormatter(formatter)
	
	logger = logging.getLogger(__name__) 
	logger.setLevel(logging.INFO)
	logger.addHandler(handler)
	
	logger.info('Logger initialized')

def main():
	init_logger()
	
if __name__ == '__main__':
	main()
