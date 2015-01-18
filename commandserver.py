# runningtext
#
# (c) 2015 Tuwuh Sarwoprasojo
# All rights reserved.

import ConfigParser
import logging
import threading
import time
import Queue
import re

import gsmmodem.exceptions
import textwriter

logger = logging.getLogger(__name__) 

class CommandServer(threading.Thread):
	_color_dict = {'r': (255, 0, 0), 'g': (0, 255, 0), 'b': (0, 0, 255), 'y': (255, 255, 0), 'w': (255, 255, 255)}
	
	def __init__(self, modem_object):
		self._modem = modem_object
		self._command_queue = Queue.Queue() 
		self._text_writer = textwriter.TextWriter('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 15, 
												'/home/pi/rpi-rgb-led-matrix/runtext16.ppm')
		threading.Thread.__init__(self)
		self.daemon = True
		defaults = {'text': 'ictronics', 'color':'w', 'pin':'1234', 'chkpulsa':'*888#'}
		self._config = ConfigParser.SafeConfigParser(defaults)
		self._config.read('app.cfg')
		if not self._config.has_section('ledmatrix'):
			self._config.add_section('ledmatrix')
		if not self._config.has_section('system'):
			self._config.add_section('system')
		with open('app.cfg', 'wb') as configfile:
			self._config.write(configfile)
		self._current_text = self._config.get('ledmatrix', 'text')
		self._current_color = self._config.get('ledmatrix', 'color')
		self._pin_code = self._config.get('system', 'pin')
		self._chkpulsa_ussd = self._config.get('system', 'chkpulsa')
		
		if self._current_color in CommandServer._color_dict:
			color = CommandServer._color_dict[self._current_color]
		else:
			color = (255, 0, 0)
		self._text_writer.write_text(self._current_text, color, -1)
		
	def _write_config(self, section, key, value):
		if not self._config.has_section(section):
			self._config.add_section(section)
		self._config.set(section, key, value)
		with open('app.cfg', 'wb') as configfile:
			self._config.write(configfile)
	
	def _verify_pin(self, pin_code):
		return (pin_code == self._pin_code)
	
	def _process_command(self, text):
		# Parse the text
		try:
			command_type, pin_code, data = self._parse_command(text)
		except TypeError:
			logger.info('Command cannot be parsed')
			return
		
		logger.info('Command type: {0}, PIN: {1}, data: {2}'.format(command_type, pin_code, data))
		
		if command_type == 'tx':
			if not self._verify_pin(pin_code):
				return 'Incorrect PIN'
			
			# Parse color
			data_array = data.split('#', 1)
			color_command = 'r'
			color = (255, 0, 0)
			color_command = data_array[0].lower()
			if color_command in CommandServer._color_dict:
				color = CommandServer._color_dict[color_command]
				data = data_array[1]
			
			self._current_color = color_command
			self._current_text = data.lstrip()
			self._text_writer.write_text(self._current_text, color, -1)
			self._write_config('ledmatrix', 'text', self._current_text)
			self._write_config('ledmatrix', 'color', self._current_color)
			return (self._current_color + '#' + self._current_text)
		elif command_type == 'cm':
			data_array = data.split('#', 1)
			command = data_array[0].lower()
			if command == 'chgpassword':
				if not self._verify_pin(pin_code):
					return 'Incorrect PIN'
				new_pin_code = data_array[1]
				if len(new_pin_code) != 4 or not new_pin_code.isdigit():
					return 'Invalid new PIN. Use 4 digits only.'
				self._pin_code = new_pin_code
				self._write_config('system', 'pin', self._pin_code)
				return 'PIN code changed to ' + self._pin_code
			elif command == 'chkpulsa':
				if not self._verify_pin(pin_code):
					return 'Incorrect PIN'
				time.sleep(10) # Put sleep here, otherwise the modem returns with timeout
				try:
					print self._chkpulsa_ussd
					u = self._modem.sendUssd(self._chkpulsa_ussd, 30)
					if u == None:
						return 'USSD Error'
					else:
						return u.message
				except gsmmodem.exceptions.TimeoutException:
					return 'USSD Timeout'
			elif command == 'readbacktxt':
				if not self._verify_pin(pin_code):
					return 'Incorrect PIN'
				return (self._current_color + '#' + self._current_text)
			elif command == 'setchkpulsa':
				if not self._verify_pin(pin_code):
					return 'Incorrect PIN'
				if re.match('^[0-9*#]*$', data_array[1].lstrip()):
					self._chkpulsa_ussd = data_array[1]
					self._write_config('system', 'chkpulsa', self._chkpulsa_ussd)
					return 'chkpulsa USSD changed to ' + self._chkpulsa_ussd
				else:
					return 'Invalid USSD.'
			else:
				return 'Unknown command'
		elif command_type == 'rz':
			if data == '358124':
				self._pin_code = '1234'
				self._write_config('system', 'pin', self._pin_code)
				return 'PIN code reset to ' + self._pin_code

	def run(self):
		while True:
			sms = self._command_queue.get()
			logger.info('== Processing SMS ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}'.format(sms.number, sms.time, sms.text))
			
			reply = self._process_command(sms.text)
			if reply != None:
				sms.reply(reply)
			
	def _parse_command(self, text):
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
	