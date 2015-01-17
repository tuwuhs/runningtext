# runningtext
#
# (c) 2015 Tuwuh Sarwoprasojo
# All rights reserved.

import logging
import threading
import time
import Queue
import re

import textwriter

logger = logging.getLogger(__name__) 

class CommandServer(threading.Thread):
	def __init__(self, modem_object):
		self._modem = modem_object
		self._command_queue = Queue.Queue() 
		self._text_writer = textwriter.TextWriter('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 15, 
												'/home/pi/rpi-rgb-led-matrix/runtext16.ppm')
		threading.Thread.__init__(self)
		self.daemon = True
		self._current_text = ''
		self._current_color = ''
		self._pin_code = '1234'
	
	def run(self):
		while True:
			sms = self._command_queue.get()
			logger.info('== Processing SMS ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}'.format(sms.number, sms.time, sms.text))
			# Parse the text
			try:
				command_type, pin_code, data = self.parse_command(sms.text)
			except TypeError:
				logger.info('Command cannot be parsed')
				continue
			
			logger.info('Command type: {0}, PIN: {1}, data: {2}'.format(command_type, pin_code, data))
			
			if command_type == 'tx':
				if pin_code != self._pin_code:
					sms.reply('Incorrect PIN')
					continue
				data_array = data.split('#', 1)
				color_command = data_array[0].lower()
				color = (255, 0, 0)
				if color_command == 'r':
					color = (255, 0, 0)
					data = data_array[1]
				elif color_command == 'g':
					color = (0, 255, 0)
					data = data_array[1]
				elif color_command == 'b':
					color = (0, 0, 255)
					data = data_array[1]
				elif color_command == 'y':
					color = (255, 255, 0)
					data = data_array[1]
				elif color_command == 'w':
					color = (255, 255, 255)
					data = data_array[1]
				else:
					pass
				
				self._current_text = data.lstrip()
				self._text_writer.write_text(self._current_text, color, -1)
				sms.reply(self._current_color + '#' + self._current_text)
				continue
			elif command_type == 'cm':
				data_array = data.split('#')
				command = data_array[0].lower()
				if command == 'chgpassword':
					if pin_code != self._pin_code:
						sms.reply('Incorrect PIN')
						continue
					new_pin_code = data_array[1]
					if len(new_pin_code) != 4 or not new_pin_code.isdigit():
						sms.reply('Invalid new PIN. Use 4 digits only.')
						continue
				elif command == 'chkpulsa':
					if pin_code != self._pin_code:
						sms.reply('Incorrect PIN')
						continue
				elif command == 'readbacktxt':
					if pin_code != self._pin_code:
						sms.reply('Incorrect PIN')
						continue
					sms.reply(self._current_color + '#' + self._current_text)
					continue
				else:
					sms.reply('Unknown command')
					continue
	
	def parse_command(self, text):
		# Example format: cm*1234#chgpassword#9125
		#                 tx*1234#Hello world! #1 in the world*)
		t = text.split('*', 1)
		command_type = t[0].lower()
		if len(command_type) != 2:
			return None
		
		t = t[1].split('#', 1)
		pin_code = t[0]
		if len(pin_code) != 4:
			return None
		
		data = t[1]
		return (command_type, pin_code, data)
	
	def queue_sms(self, sms):
		self._command_queue.put(sms)
	