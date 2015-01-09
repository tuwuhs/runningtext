# runningtext
#
# (c) 2015 Tuwuh Sarwoprasojo
# All rights reserved.

import ConfigParser

import gsmmodem
import simplesms

class GsmModem(gsmmodem.GsmModem):
	def sendUssdText(self, text):
		u = self.sendUssd(simplesms.pdu.encode(text))
		return simplesms.pdu.decode(u.message)
