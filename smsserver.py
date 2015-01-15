
import logging

import modem
import commandserver
from gsmmodem.exceptions import TimeoutException

logger = logging.getLogger(__name__)

class SmsServer(object):
	def __init__(self, modem_port):
		self._is_connected = False
		self._modem = modem.GsmModem(modem_port, smsReceivedCallbackFunc=self.handle_sms)
		self._command_server = commandserver.CommandServer(self._modem)
		self._command_server.start()
		pass
	
	def connect(self):
		logger.info('Connecting GsmModem at port {0}...'.format(self._modem.port))
		self._modem.connect()		
		logger.info('Connected GsmModem at port {0}'.format(self._modem.port))
		logger.info('Modem mfg: {0} Model: {1}'.format(self._modem.manufacturer, self._modem.model))
		logger.info('Waiting for network...')
		while True:
			try:
				self._modem.waitForNetworkCoverage(5)
			except TimeoutException:
				logger.info('No network')
				continue
			else:
				break
		logger.info('Network found: {0}'.format(self._modem.networkName))
		logger.info('Signal strength: {0}'.format(self._modem.signalStrength))
		
		self._modem.smsTextMode = True
		stored_sms = self._modem.listStoredSms(delete=True)
		logger.info('Deleted {0} stored messages'.format(len(stored_sms)))
	
	def disconnect(self):
		logger.info('Closing GsmModem at port {0}...'.format(self._modem.port))
		self._modem.close()
		logger.info('Closed GsmModem at port {0}'.format(self._modem.port))
	
	def handle_sms(self, sms):
		logger.info('== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}'.format(sms.number, sms.time, sms.text))
		self._command_server.queue_sms(sms)
# 		logger.info('Replying to SMS...')
# 		sms.reply('SMS received: "{0}{1}"'.format(sms.text[:20], '...' if len(sms.text) > 20 else ''))
# 		logger.info('SMS sent')
		
	