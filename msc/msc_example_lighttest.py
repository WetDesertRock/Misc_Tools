import pygame
import time, ConfigParser
import pygame.midi as midi

from msc import * 

print pygame.__version__

midi.init()
out = midi.Output(midi.get_default_output_id())

t = time.time() + 2
state = 0

max = 80

while True:
	if t <= time.time():
		if state == max:
			state = 0
		elif state == 0:
			state = max
		t += 2
		print t
	
	print state		
	for i in xrange(4):
		out.write_sys_ex(0, list(Submaster(-1, i+1, state+20)))
	
	time.sleep(.015)