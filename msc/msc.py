# The MIT License (MIT)
# 
# Copyright (c) 2013 WetDesertRock
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# In addition to the following license, I would apperciate if you contact me if
#   you use the library, and how you are using it. If any assistance is required,
#   I can help. Note, this isn't going to work on all lightboards.

#F0 7F 01 02 01 01 31 00 31 F7
#F0 7F [device_ID] 02 01 [command] [command_number] F7
import struct

def constrain(val, minv, maxv):
	if val > maxv:
		return maxv
	elif val < minv:
		return minv
	else:
		return val

class MSCcmds():
	GOCUE = 1
	PSCUE = 2
	RSCUE = 3
	SETSM = 6
	FIREM = 7

class MSCCommand():
	FormatStr = '\xf0\x7f{deviceid}\x02\x01{cmd}{cmdnum}\xf7'
	def __init__(self, did, cmd):
		if did == -1:
			did = 127
		self.deviceid = did
		self.command = cmd
	
	def format(self, listb = False):
		cmdnums = self.__formatcmdnums__()
		finalstr = self.FormatStr.format(deviceid = chr(self.deviceid), cmd = chr(self.command), cmdnum = cmdnums)
		if listb:
			return [ord(i) for i in finalstr] 
		else:
			return finalstr
	
	def __str__(self):
		return self.format()
	
	def __iter__(self):
		return iter(self.format(listb=True))

class FireMacro(MSCCommand):
	def __init__(self, did, macro):
		MSCCommand.__init__(self, did, MSCcmds.FIREM)
		self.macro = constrain(macro, 1, 127)
	
	def __formatcmdnums__(self):
		return chr(self.macro)
	
class Submaster(MSCCommand):
	def __init__(self, did, subm, level):
		MSCCommand.__init__(self, did, MSCcmds.SETSM)
		
		self.subm = constrain(subm, 1, 127)
		self.level = constrain(level, 0, 100)
	
	def __formatcmdnums__(self):
		return chr(self.subm) + chr(0) + chr(self.level) + chr(0)
		

class GMFaders(MSCCommand):
	def __init__(self, did, action, level):
		MSCCommand.__init__(self, did, MSCcmds.SETSM)
		
		if action == "GM":
			self.action = "\x7E\x03"
		elif action == "MPFup":
			self.action = "\x00\x01"
		elif action == "MPFdown":
			self.action = "\x01\x01"
		
		self.level = constrain(level, 0, 100)
		
	def __formatcmdnums__(self):
		cmdnums = self.action + chr(self.level) + chr(0)

def MasterPlaybackUp(did, level):
	return GMFaders(did, "MPFup", level)

def MasterPlaybackDown(did, level):
	return GMFaders(did, "MPFdown", level)

def GrandMaster(did, level):
	return GMFaders(did, "GM", level)


class Cue(MSCCommand):
	def __init__(self, did, cuelist, cuenumber, action):
		#Cue(1, 1, 10, "go")
		if action == "pause":
			cmd = MSCcmds.PSCUE
		elif action == "go":
			cmd = MSCcmds.GOCUE
		elif action == "resume":
			cmd = MSCcmds.RSCUE
			
		MSCCommand.__init__(self, did, cmd)
		self.cuelist = cuelist
		self.cuenumber = cuenumber
	
	def __formatcmdnums__(self):
		return "%s\x00%s" % ( str(self.cuenumber), str(self.cuelist) )

def hexstr(listi):
	retstr = ''
	for i in listi:
		retstr += ' %X'%i
	return retstr.strip()

if __name__ == '__main__':
	import pygame.midi as midi
	
	midi.init()
	out = midi.Output(midi.get_default_output_id())
	
	import time
	f = open("./config.cfg", 'r')
	o = open("./output.txt", 'a')
	stri = f.read()
	lines = stri.split('\n')
	print lines
	for i in lines:
		i = i.strip()
		if i == '':
			continue
		if i[0] == '#':
			continue
		stri = i.split(' ')
		time.sleep(float(stri[0]))
		subm = Submaster(int(stri[1]), int(stri[2]), int(stri[3]))
		o.write(hexstr(list(subm)))
		o.write("\n")
		print hexstr(list(subm))
		out.write_sys_ex(0, list(subm))
	
	o.close()
	f.close()
	
	out.close()
	
	midi.quit()