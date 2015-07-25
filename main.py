__author__ = 'marcel'

import Photocell

# define methods to run when light state changes
def light_on_method():
	print("Light On!")


def light_off_method():
	print("Light Off!")

check_light = Photocell.CheckLight(light_on_method, light_off_method)
check_light.run()
