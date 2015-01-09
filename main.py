# runningtext
#
# (c) 2015 Tuwuh Sarwoprasojo
# All rights reserved.

import ConfigParser
import errno
import logging
import logging.handlers
import os

import modem
from gsmmodem.exceptions import TimeoutException

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
	
	logger = logging.getLogger(__name__) 
	logger.setLevel(logging.INFO)
	logger.addHandler(handler)
	
	logger.info('Logger initialized')

def handle_sms(sms):
	logger = logging.getLogger(__name__)
	logger.info('== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}'.format(sms.number, sms.time, sms.text))
	logger.info('Replying to SMS...')
	sms.reply('SMS received: "{0}{1}"'.format(sms.text[:20], '...' if len(sms.text) > 20 else ''))
	logger.info('SMS sent')

def main():
	init_logger()
	logger = logging.getLogger(__name__)

	config = ConfigParser.SafeConfigParser()
	config.read('app.cfg')
	modem_port = config.get('modem', 'port')
	
	m = modem.GsmModem(modem_port, smsReceivedCallbackFunc=handle_sms)
	m.connect()
	logger.info('Connected GsmModem at port {0}'.format(modem_port))
	logger.info('Modem mfg: {0} Model: {1}'.format(m.manufacturer, m.model))

	logger.info('Waiting for network...')
	while True:
		try:
			m.waitForNetworkCoverage(5)
		except TimeoutException:
			logger.info('No network'.format(modem_port))
			continue
		else:
			break
	logger.info('Network found: {0}'.format(m.networkName))
	logger.info('Signal strength: {0}'.format(m.signalStrength))
	
	m.smsTextMode = True
	stored_sms = m.listStoredSms(delete=True)
	logger.info('Deleted {0} stored messages'.format(len(stored_sms)))

	print('Listening...')
	try:	
		while True:
			pass
	except KeyboardInterrupt:
		pass
	finally:
		print('Closing...')
		logger.info('Closing GsmModem...')
		m.close()
		logger.info('Closed GsmModem')
	
if __name__ == '__main__':
	main()
