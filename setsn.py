# runningtext
#
# (c) 2015 Tuwuh Sarwoprasojo
# All rights reserved.

import ConfigParser

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

sn = getserial()

config = ConfigParser.SafeConfigParser()
config.read('app.cfg')
if not config.has_section('system'):
	config.add_section('system')

config.set('system', 'sn', sn)

with open('app.cfg', 'wb') as configfile:
	config.write(configfile)
