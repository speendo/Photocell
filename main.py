#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'marcel'

import photocell

# define methods to run when light state changes
def light_on_method():
	print("Light On!")


def light_off_method():
	print("Light Off!")

check_light = photocell.CheckLight(light_on_method, light_off_method)
check_light.start()
