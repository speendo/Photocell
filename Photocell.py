__author__ = 'marcel'

 import threading
import os
import select
import time

class CheckLight(threading.Thread):
	def __init__(self, light_on_method, light_off_method, pin=24):
		threading.Thread.__init__(self)
	
		self.pin_number = pin

		# Making the pin available
		# Export pin (if not already exported)
		if not os.path.isdir("/sys/class/gpio/gpio%i" % self.pin_number):
			with open("/sys/class/gpio/export", "w") as export_pin_file:
				export_pin_file.write(str(self.pin_number))
		
		# Wait for the pin to be exported (isn't there a better solution?)
		time.sleep(0.1)

		# Define pin as interrupt (with both edges)
		with open("/sys/class/gpio/gpio%i/edge" % self.pin_number, "w") as edge_pin_file:
			edge_pin_file.write("both")

		self.pin_fd = open("/sys/class/gpio/gpio%i/value" % self.pin_number)
		
		self.epoll = select.epoll()

		self.light_on_method = light_on_method
		self.light_off_method = light_off_method
	
		self.light_status = False # light is started off

	def run(self):
		with self.pin_fd:
			self.epoll.register(self.pin_fd, select.EPOLLIN | select.EPOLLET)

			while True:
				events = self.epoll.poll()
				if len(events) > 0:
					current_light_status = not self.pin_fd.read(1) == "1" # 0 == ON, 1 == OFF
					self.pin_fd.seek(0)
					
					if current_light_status != self.light_status:
						self.light_status = current_light_status
						
					if self.light_status:
						self.light_on_method()
					else:
						self.light_off_method()
