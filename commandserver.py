# runningtext
#
# (c) 2015 Tuwuh Sarwoprasojo
# All rights reserved.

import logging
import threading
import time
import Queue

logger = logging.getLogger(__name__) 

class CommandServer(threading.Thread):
	def __init__(self, modem_object):
		self._modem = modem_object
		self._command_queue = Queue.Queue() 
		threading.Thread.__init__(self)
		self.daemon = True
	
	def run(self):
		while True:
			sms = self._command_queue.get()
			logger.info('== Processing SMS ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}'.format(sms.number, sms.time, sms.text))
			if sms.text == 'yeah':
				sms.reply('Hello!')
			
	def queue_sms(self, sms):
		self._command_queue.put(sms)
