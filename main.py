# runningtext
#
# (c) 2015 Tuwuh Sarwoprasojo
# All rights reserved.

import ConfigParser
import errno
import logging
import logging.handlers
import os
import time

import smsserver

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

	handler = MyRotatingFileHandler(LOG_FILENAME, maxBytes=1000000, backupCount=10)
	handler.setFormatter(formatter)
	
	logger = logging.getLogger() 
	logger.setLevel(logging.INFO)
	logger.addHandler(handler)
	
	logger.info('Logger initialized')

def getserial():
	# Extract serial from cpuinfo file
	cpuserial = "0000000000000000"
	try:
		f = open('/proc/cpuinfo','r')
		for line in f:
			s = line.split(':')
			if len(s) != 2:
				continue
			field = s[0].strip()
			value = s[1].strip()
			if field.lower() != 'serial':
				continue
			cpuserial = value
			break
		f.close()
	except:
		cpuserial = "ERROR"
	return cpuserial

def main():
	init_logger()

	config = ConfigParser.SafeConfigParser()
	config.read('app.cfg')
	
	try:
		sn = config.get('system', 'sn')
		if sn != getserial():
			print('SN mismatch')
			return
	except ConfigParser.NoOptionError:
		print('SN not found')
		return
	
	modem_port = config.get('modem', 'port')
	
	sms_server = smsserver.SmsServer(modem_port)
	sms_server.connect()

	print('Listening...')
	try:	
		while True:
			pass
	except KeyboardInterrupt:
		pass
	finally:
		print('Closing...')
		sms_server.disconnect()
	
if __name__ == '__main__':
	main()
