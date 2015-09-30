__author__ = 'marcel'

import threading
import os
import select
import time
import atexit

class CheckLight(threading.Thread):
	def __init__(self, light_on_method, light_off_method, pin=24, waiting_time=0.5):
		threading.Thread.__init__(self)
	
		self.pin_number = pin

		# Making the pin available
		# First of all, make sure, that the pin is unexported, once the script is terminated
		atexit.register(self.unexport_pin)

		# Now export the pin (if not already exported)
		if not os.path.isdir("/sys/class/gpio/gpio{pin_number}".format(pin_number=self.pin_number)):
			with open("/sys/class/gpio/export", "w") as export_pin_file:
				export_pin_file.write(str(self.pin_number))
		
		# Define pin as interrupt (with both edges)
		# /sys/class/gpio/<pin number>/edge should be writeable
		# However, it might be necessary to wait a bit until it is writeable
		# Save the current time
		start_time = time.time()
		# If the questionable file is not writeable, wait ...
		while not os.access("/sys/class/gpio/gpio{pin_number}/edge".format(pin_number=self.pin_number), os.W_OK):
			# ... but not longer than waitingTime
			if waiting_time < time.time() - start_time:
				raise ValueError("Waited for {waiting_time} seconds for \"/sys/class/gpio/gpio{pin_number}/edge\" to be writeable. "
					"Either waiting_time is defined too short or there's something wrong with the GPIO-setup. "
					.format(waiting_time = waiting_time, pin_number=self.pin_number))

		# /sys/class/gpio/<pin number>/edge is here now. Set it to "both"
		with open("/sys/class/gpio/gpio{pin_number}/edge".format(pin_number=self.pin_number), "w") as edge_pin_file:
			edge_pin_file.write("both")

		self.pin_fd = open("/sys/class/gpio/gpio{pin_number}/value".format(pin_number=self.pin_number))
		
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

	# unexport the pin
	def unexport_pin(self):
		if os.path.isdir("/sys/class/gpio/gpio{pin_number}".format(pin_number=self.pin_number)):
			with open("/sys/class/gpio/unexport", "w") as unexport_pin_file:
				unexport_pin_file.write(str(self.pin_number))
